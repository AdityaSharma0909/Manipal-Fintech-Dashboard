import fcntl
import hashlib
import logging
import os
import subprocess
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

import paramiko

from utils.envSetup import environment
from onboarding_v2.storage import get_minio_client, _resolve_bucket_name
from django.core.mail import send_mail



logger = logging.getLogger(__name__)


class DatabaseTransfer:
    """Create production dumps and securely copy the newest dump to development."""

    def __init__(self):
        self.app_env = (environment.APP_ENV or "").strip().upper()
        self.backup_dir = Path(environment.DATABASE_BACKUP_DIR or "/app/db_backups")
        self.prefix = environment.DATABASE_BACKUP_PREFIX or "manipal_db_dump_production"

    def backup_production_database(self):
        self._require_environment("dev")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        with self._lock("production-backup"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = self.backup_dir / f"{self.prefix}_{timestamp}.sql"
            partial_path = final_path.with_suffix(".sql.partial")

            command = [
                "pg_dump",
                "--host", environment.DJANGO_POSTGRES_HOST,
                "--port", str(environment.DJANGO_POSTGRES_PORT or 5432),
                "--username", environment.DJANGO_POSTGRES_USER,
                "--dbname", environment.DJANGO_POSTGRES_DATABASE,
                "--no-password",
                "--no-owner",
                "--no-acl",
                "--file", str(partial_path),
            ]
            process_env = os.environ.copy()
            process_env["PGPASSWORD"] = environment.DJANGO_POSTGRES_PASSWORD

            try:
                subprocess.run(
                    command,
                    env=process_env,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self._require_nonempty_file(partial_path)
                partial_path.replace(final_path)
                checksum = self._sha256(final_path)
                checksum_path = final_path.with_suffix(".sql.sha256")
                checksum_path.write_text(
                    f"{checksum}  {final_path.name}\n",
                    encoding="ascii",
                )
                self._delete_older_files(final_path, checksum_path)
            except subprocess.CalledProcessError as exc:
                partial_path.unlink(missing_ok=True)
                detail = (exc.stderr or "").strip() or "no error output returned"
                logger.error("pg_dump failed: %s", detail)
                raise RuntimeError(f"pg_dump failed: {detail}") from exc
            except Exception:
                partial_path.unlink(missing_ok=True)
                logger.exception("Production database backup failed")
                raise

            logger.info("Production database backup created: %s", final_path.name)
            return {
                "file": str(final_path),
                "sha256": checksum,
                "size_bytes": final_path.stat().st_size,
            }

    def download_latest_production_backup(self):
        self._require_environment("DEV")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        with self._lock("development-download"):
            with self._ssh_client() as client:
                with client.open_sftp() as sftp:
                    remote_dir = environment.PRODUCTION_BACKUP_REMOTE_DIR
                    if not remote_dir:
                        raise ValueError("PRODUCTION_BACKUP_REMOTE_DIR is required")

                    latest = self._latest_remote_dump(sftp, remote_dir)
                    remote_path = str(PurePosixPath(remote_dir) / latest.filename)
                    remote_checksum_path = f"{remote_path}.sha256"
                    final_path = self.backup_dir / latest.filename
                    partial_path = final_path.with_suffix(".sql.partial")

                    try:
                        expected_checksum = self._read_remote_checksum(
                            sftp,
                            remote_checksum_path,
                            latest.filename,
                        )
                        sftp.get(remote_path, str(partial_path))
                        self._require_nonempty_file(partial_path)
                        if partial_path.stat().st_size != latest.st_size:
                            raise RuntimeError(
                                "Downloaded backup size does not match the remote file"
                            )
                        checksum = self._sha256(partial_path)
                        if checksum != expected_checksum:
                            raise RuntimeError(
                                "Downloaded backup checksum does not match production"
                            )
                        partial_path.replace(final_path)
                        checksum_path = final_path.with_suffix(".sql.sha256")
                        checksum_path.write_text(
                            f"{checksum}  {final_path.name}\n",
                            encoding="ascii",
                        )
                        self._delete_older_files(final_path, checksum_path)
                    except Exception:
                        partial_path.unlink(missing_ok=True)
                        logger.exception("Production backup download failed")
                        raise

            logger.info("Production backup downloaded: %s", final_path.name)
            
            download_url = self._upload_and_email_backup(final_path)

            return {
                "file": str(final_path),
                "sha256": checksum,
                "size_bytes": final_path.stat().st_size,
                "download_url": download_url,
            }

    def _upload_and_email_backup(self, final_path):
        try:
            # 1. Upload to storage
            client = get_minio_client()
            bucket = _resolve_bucket_name()
            object_name = f"db_backups/{final_path.name}"
            
            logger.info("Uploading %s to %s/%s...", final_path.name, bucket, object_name)
            client.fput_object(bucket, object_name, str(final_path))
            logger.info("Upload completed successfully.")
            
            # 2. Generate presigned GET URL with 7 days expiry
            expires = timedelta(days=7)
            get_url = client.presigned_get_object(
                bucket,
                object_name,
                expires=expires
            )
            logger.info("Generated download URL: %s", get_url)
            
            # 3. Send email to configured recipient
            recipient = environment.DATABASE_BACKUP_EMAIL or "tamoghna.m@getafixtechnologies.com"
            subject = "Production Database Backup Download Link"
            body = f"""Hi,

The latest production database backup has been downloaded, verified, and uploaded to the secure E2E Object Store.

Details:
- File Name: {final_path.name}
- Size: {final_path.stat().st_size / (1024*1024):.2f} MB
- Download Link (expires in 7 days):
{get_url}

Please download it at your convenience.

Best regards,
Radian System
"""
            logger.info("Sending backup download link email to %s...", recipient)
            send_mail(
                subject=subject,
                message=body,
                from_email=environment.DEFAULT_FROM_EMAIL or "service@getafixtechnologies.com",
                recipient_list=[recipient],
                fail_silently=False
            )
            logger.info("Email sent successfully to %s.", recipient)
            return get_url
        except Exception:
            logger.exception("Uploading or emailing production backup failed")
            raise


    def _ssh_client(self):
        host = environment.PRODUCTION_SSH_HOST
        username = environment.PRODUCTION_SSH_USER
        known_hosts = environment.PRODUCTION_SSH_KNOWN_HOSTS_PATH
        if not host or not username or not known_hosts:
            raise ValueError(
                "PRODUCTION_SSH_HOST, PRODUCTION_SSH_USER and "
                "PRODUCTION_SSH_KNOWN_HOSTS_PATH are required"
            )
        if not Path(known_hosts).is_file():
            raise ValueError("PRODUCTION_SSH_KNOWN_HOSTS_PATH does not exist")

        client = paramiko.SSHClient()
        client.load_host_keys(known_hosts)
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.connect(
            hostname=host,
            port=int(environment.PRODUCTION_SSH_PORT or 22),
            username=username,
            password=environment.PRODUCTION_SSH_PASSWORD or None,
            key_filename=environment.PRODUCTION_SSH_PRIVATE_KEY_PATH or None,
            look_for_keys=False,
            allow_agent=False,
            timeout=30,
            banner_timeout=30,
            auth_timeout=30,
        )
        return client

    def _latest_remote_dump(self, sftp, remote_dir):
        candidates = [
            entry
            for entry in sftp.listdir_attr(remote_dir)
            if entry.filename.startswith(f"{self.prefix}_")
            and entry.filename.endswith(".sql")
            and entry.st_size > 0
        ]
        if not candidates:
            raise FileNotFoundError(
                f"No completed {self.prefix}_*.sql backup found in {remote_dir}"
            )
        return max(candidates, key=lambda entry: (entry.st_mtime, entry.filename))

    @staticmethod
    def _read_remote_checksum(sftp, checksum_path, expected_filename):
        try:
            with sftp.open(checksum_path, "r") as checksum_file:
                line = checksum_file.readline().strip()
        except IOError as exc:
            raise RuntimeError(
                "The newest production backup has no checksum file"
            ) from exc

        parts = line.split()
        if len(parts) != 2 or parts[1] != expected_filename:
            raise RuntimeError("Production backup checksum file is invalid")
        checksum = parts[0].lower()
        if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
            raise RuntimeError("Production backup checksum is invalid")
        return checksum

    def _delete_older_files(self, current_dump, current_checksum):
        for path in self.backup_dir.glob(f"{self.prefix}_*.sql"):
            if path != current_dump:
                path.unlink()
                path.with_suffix(".sql.sha256").unlink(missing_ok=True)

        # Remove orphan checksum files left by interrupted/manual operations.
        for path in self.backup_dir.glob(f"{self.prefix}_*.sql.sha256"):
            if path != current_checksum and not path.with_suffix("").exists():
                path.unlink()

    def _require_environment(self, expected):
        if self.app_env != expected:
            raise RuntimeError(
                f"This job can run only in {expected}; current APP_ENV is "
                f"{self.app_env or 'unset'}"
            )

    @staticmethod
    def _require_nonempty_file(path):
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError("Backup file is missing or empty")

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with path.open("rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @contextmanager
    def _lock(self, name):
        lock_path = self.backup_dir / f".{name}.lock"
        with lock_path.open("w") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError(f"{name} job is already running") from exc
            yield
