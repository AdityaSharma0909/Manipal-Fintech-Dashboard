import subprocess
import os
from utility.e2e_utility import MinioUtility
from utils.envSetup import environment
class BackDatabase:
    def backup(self):
        DATABASE_NAME = environment.DJANGO_POSTGRES_DATABASE
        DATABASE_USER = environment.DJANGO_POSTGRES_USER
        DATABASE_PASSWORD = environment.DJANGO_POSTGRES_PASSWORD
        DATABASE_HOST=environment.DJANGO_POSTGRES_HOST
        # Backup directory and file name

        BACKUP_DIR = 'db_backup/'
        BACKUP_FILE = f'database_backup.sql'
        file_path =os.path.join(BACKUP_DIR, BACKUP_FILE)
        # Build the pg_dump command
        print(f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}')
        pg_dump_cmd = [
            'pg_dump',
            '--dbname', f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}',
            '--file', file_path,
        ]

        try:
            # Execute the pg_dump command
            subprocess.run(pg_dump_cmd, check=True)
            file_name = os.path.basename(file_path)
            MinioUtility().upload_file_to_minio_by_path(file_path=file_path, object_name='db_backup', file_name=file_name)
            print(f"Database backup completed successfully. Backup file: {os.path.join(BACKUP_DIR, BACKUP_FILE)}")

        except subprocess.CalledProcessError as e:
            print(f"Database backup failed with error: {e}")