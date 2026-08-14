from __future__ import annotations
import logging
import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

from onboarding_v2.integrations.bank_trace import mask_sensitive_values, update_bank_lead_trace

from .crypto import AxisJoseKeys, encrypt_and_sign, load_jose_keys, verify_and_decrypt
from .exceptions import AxisRequestError
from .p12_utils import load_pkcs12_cert_and_key
from .settings import AxisEnvConfig
logger = logging.getLogger(__name__)


def _json_or_text(value: Optional[str]) -> Any:
    if not value:
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def _extract_axis_error_message(value: Any) -> Optional[str]:
    if isinstance(value, str):
        parsed = _json_or_text(value)
        if parsed is not value:
            return _extract_axis_error_message(parsed)
        return value.strip() or None

    if not isinstance(value, dict):
        return None

    data = value.get("Data")
    if isinstance(data, dict):
        for key in ("message", "Message", "errorMessage", "error_description"):
            message = data.get(key)
            if message:
                return str(message).strip()

    for key in ("message", "Message", "error", "error_description"):
        message = value.get(key)
        if message:
            return str(message).strip()

    return None


@dataclass
class AxisToken:
    token: str
    expires_on: Optional[datetime] = None

    def is_expired(self) -> bool:
        if not self.expires_on:
            return False
        return datetime.utcnow() >= self.expires_on


class AxisClient:
    """
    Minimal Axis CRMNext client for:
    - POST /login
    - POST /create-lead
    using Axis encryption scheme (JWE then JWS) and mTLS + required headers.
    """

    def __init__(self, config: AxisEnvConfig):
        self.config = config
        self._session = requests.Session()
        self._token: Optional[AxisToken] = None
        self._pkcs12_tmp_dir: Optional[str] = None

        (
            mtls_cert_path,
            mtls_key_path,
            partner_sign_path,
            partner_decrypt_path,
            pkcs12_tmp_dir,
        ) = _resolve_tls_and_partner_key_paths(config)
        self._mtls_cert_path = mtls_cert_path
        self._mtls_key_path = mtls_key_path
        self._pkcs12_tmp_dir = pkcs12_tmp_dir

        self._keys: AxisJoseKeys = load_jose_keys(
            axis_encrypt_public_key_pem_file=config.axis_encrypt_public_key_pem_file,
            partner_sign_private_key_pem_file=partner_sign_path,
            partner_decrypt_private_key_pem_file=partner_decrypt_path,
            axis_verify_public_key_pem_file=config.axis_verify_public_key_pem_file,
        )

    def __del__(self) -> None:
        if self._pkcs12_tmp_dir and os.path.isdir(self._pkcs12_tmp_dir):
            for name in ("client.crt", "client.key"):
                try:
                    os.remove(os.path.join(self._pkcs12_tmp_dir, name))
                except OSError:
                    pass
            try:
                os.rmdir(self._pkcs12_tmp_dir)
            except OSError:
                pass

    def _headers(self, *, request_uuid: str) -> Dict[str, str]:
        epoch_millis = str(int(time.time() * 1000))
        return {
            "Content-Type": "text/plain",
            "X-IBM-Client-Id": self.config.ibm_client_id,
            "X-IBM-Client-Secret": self.config.ibm_client_secret,
            "x-fapi-channel-id": self.config.channel_id,
            "x-fapi-epoch-millis": epoch_millis,
            "x-fapi-uuid": request_uuid,
            "x-fapi-serviceId": self.config.service_id,
            "x-fapi-serviceVersion": self.config.service_version,
        }

    def _post_encrypted(self, *, path: str, request_uuid: str, payload_obj: Dict[str, Any], bank_trace=None) -> Dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        plaintext = json.dumps(payload_obj, separators=(",", ":"), ensure_ascii=False)
        logger.info(f"Axis request plaintext: {plaintext}")
        logger.info(f"Axis request keys: {self._keys}")

        body = encrypt_and_sign(keys=self._keys, payload_json=plaintext)

        cert = None
        if self._mtls_cert_path and self._mtls_key_path:
            cert = (self._mtls_cert_path, self._mtls_key_path)
        elif self._mtls_cert_path:
            cert = self._mtls_cert_path
        headers = self._headers(request_uuid=request_uuid)
        update_bank_lead_trace(
            bank_trace,
            bank_api_url=url,
            request_headers=headers,
            request_payload={
                "body": body,
                "plain_request": mask_sensitive_values(payload_obj),
                "path": path,
            },
        )

        try:
            logger.info(f"Axis request payload: {body} || {url}|| {cert} || {headers}")
        
            resp = self._session.post(
                url,
                headers=headers,
                data=body,
                timeout=self.config.timeout_seconds,
                cert=cert,
                verify=self.config.verify_ssl,
            )
        except requests.exceptions.SSLError as exc:
            detail = str(exc)
            hint = ""
            if "KEY_VALUES_MISMATCH" in detail or "key values mismatch" in detail.lower():
                hint = (
                    " The mTLS client certificate and key are not a matching pair "
                    "(use the private key that belongs to the same CSR/keypair as the signed client cert)."
                )
            raise AxisRequestError(f"Axis TLS/mTLS failed for {path}: {detail}.{hint}") from exc
        except requests.RequestException as exc:
            update_bank_lead_trace(
                bank_trace,
                response_payload={"exception": str(exc)},
            )
            raise AxisRequestError(f"Axis request failed for {path}") from exc

        if resp.status_code >= 400:
            logger.error(f"Axis request failed for {path}: {resp.status_code} {resp.text} ||{resp}")
            error_decrypted = None
            error_payload = None
            try:
                error_decrypted = verify_and_decrypt(keys=self._keys, token=(resp.text or "").strip())
                error_payload = _json_or_text(error_decrypted)
                logger.info(f"Axis error response decrypted: {error_decrypted}")
            except Exception:
                logger.exception("Axis error response decrypt failed")
            partner_message = _extract_axis_error_message(error_payload or error_decrypted)
            update_bank_lead_trace(
                bank_trace,
                response_status_code=resp.status_code,
                response_payload={
                    "raw_body": resp.text,
                    "decrypted_body": error_payload or error_decrypted,
                },
            )
            raise AxisRequestError(
                f"Axis request failed for {path}",
                status_code=resp.status_code,
                response_text=resp.text,
                decrypted_response=error_payload or error_decrypted,
                partner_message=partner_message,
            )
        logger.info(f"Axis response keys: {self._keys}")
        # Axis response is expected to be encrypted+signed compact string.
        decrypted = verify_and_decrypt(keys=self._keys, token=(resp.text or "").strip())
        logger.info(f"Axis response decrypted: {decrypted}")
        try:
            data = json.loads(decrypted)
            update_bank_lead_trace(
                bank_trace,
                response_status_code=resp.status_code,
                response_payload={
                    "raw_body": resp.text,
                    "decrypted_body": data,
                },
            )
            return data
        except json.JSONDecodeError as exc:
            update_bank_lead_trace(
                bank_trace,
                response_status_code=resp.status_code,
                response_payload={
                    "raw_body": resp.text,
                    "decrypted_body": decrypted,
                },
            )
            raise AxisRequestError("Axis response was not valid JSON after decrypt") from exc

    def login(self, *, request_uuid: Optional[str] = None) -> AxisToken:
        if self._token and not self._token.is_expired():
            return self._token

        request_uuid = request_uuid or uuid.uuid4().hex
        payload = {"Data": {"userName": self.config.username, "password": self.config.password}, "Risks": {}}
        logger.info(f"Axis login payload: {payload}")

        data = self._post_encrypted(path="/login", request_uuid=request_uuid, payload_obj=payload)
        logger.info(f"Axis login response: {data}")

        token = (data or {}).get("Data", {}).get("token")
        if not token:
            raise AxisRequestError("Axis login did not return token", response_text=str(data))

        # expiresOn parsing is optional; keep token until process restart if not parseable
        expires_on = None
        raw_exp = (data or {}).get("Data", {}).get("expiresOn")
        if isinstance(raw_exp, str) and raw_exp:
            # often ISO-ish, but may include timezone; keep best-effort without strict parsing
            try:
                # Example: 2022-05-25T14:16:28.4947222+05:30
                dt = datetime.fromisoformat(raw_exp.replace("Z", "+00:00"))
                if dt.tzinfo is not None:
                    dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                expires_on = dt
            except Exception:
                expires_on = None

        self._token = AxisToken(token=token, expires_on=expires_on)
        return self._token

    def create_lead(self, *, lead_data: Dict[str, Any], request_uuid: Optional[str] = None, bank_trace=None) -> Dict[str, Any]:
        request_uuid = request_uuid or uuid.uuid4().hex
        token = self.login(request_uuid=request_uuid).token

        payload = {"Data": {"token": token, **lead_data}, "Risks": {}}
        logger.info(f"Axis create-lead payload: {payload}")
        return self._post_encrypted(
            path="/create-lead",
            request_uuid=request_uuid,
            payload_obj=payload,
            bank_trace=bank_trace,
        )


def _resolve_tls_and_partner_key_paths(
    config: AxisEnvConfig,
) -> Tuple[Optional[str], Optional[str], str, Optional[str], Optional[str]]:
    """
    Returns (mtls_cert_path, mtls_key_path, partner_sign_pem_path, partner_decrypt_pem_path, pkcs12_tmp_dir).
    When PKCS12 is configured, it is the source of truth for mTLS and (by default) partner keys.
    """
    mtls_cert = config.mtls_cert_file
    mtls_key = config.mtls_key_file
    partner_sign = config.partner_sign_private_key_pem_file
    partner_decrypt = config.partner_decrypt_private_key_pem_file

    if not config.mtls_pkcs12_file:
        return mtls_cert, mtls_key, partner_sign, partner_decrypt, None
    logger.info(f"Loading PKCS12 file: {config.mtls_pkcs12_file}")
    cert_pem, key_pem = load_pkcs12_cert_and_key(
        config.mtls_pkcs12_file,
        config.mtls_pkcs12_password,
    )
    tmp_dir = tempfile.mkdtemp(prefix="axis_pkcs12_")
    cert_path = os.path.join(tmp_dir, "client.crt")
    key_path = os.path.join(tmp_dir, "client.key")
    Path(cert_path).write_bytes(cert_pem)
    Path(key_path).write_bytes(key_pem)

    if not partner_sign or not os.path.isfile(partner_sign):
        partner_sign = key_path
    if not partner_decrypt or not os.path.isfile(partner_decrypt):
        partner_decrypt = key_path

    return cert_path, key_path, partner_sign, partner_decrypt, tmp_dir
