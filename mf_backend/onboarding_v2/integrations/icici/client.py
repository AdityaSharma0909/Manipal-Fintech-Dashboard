import base64
import json
import logging
import uuid
import requests
from typing import Dict, Any

from onboarding_v2.integrations.bank_trace import mask_sensitive_values, update_bank_lead_trace

from .settings import ICICIConfig
from .crypto import ICICIEncryptionService

logger = logging.getLogger(__name__)

class ICICIClient:
    def __init__(self, config: ICICIConfig):
        self.config = config

    def decrypt_payload(self, encrypted_data: str, encrypted_key: str) -> str:
        """
        Public decryption method using instance config.
        """
        if not self.config.pfx_path:
            raise ValueError("ICICI_PFX_PATH not configured")
        
        return ICICIEncryptionService.decrypt_payload(
            encrypted_data_b64=encrypted_data,
            encrypted_key_b64=encrypted_key,
            pfx_path=self.config.pfx_path,
            pfx_password=self.config.pfx_password
        )

    def _get_token(self) -> str:
        credentials = f"{self.config.client_id}:{self.config.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {"grant_type": "client_credentials"}
        
        logger.info("Fetching ICICI access token from %s", self.config.token_url)
        resp = requests.post(self.config.token_url, data=payload, headers=headers, timeout=self.config.timeout_seconds)
        resp.raise_for_status()
        
        data = resp.json()
        logger.info("ICICI Token Response: %s", data)
        token = data.get("access_token")
        if not token:
            raise ValueError("No access_token in ICICI response")
        return token

    def push_lead(self, payload: Dict[str, Any], bank_trace=None) -> Dict[str, Any]:
        token = self._get_token()
        
        payload_json = json.dumps(payload, separators=(",", ":"))
        logger.info("ICICI Plaintext Payload: %s", payload_json)
        
        encrypted_key, encrypted_data = ICICIEncryptionService.encrypt_payload(
            payload_json, self.config.public_key_path
        )
        
        api_payload = {
            "requestId": str(uuid.uuid4()),
            "service": "LeadCreation",
            "encryptedKey": encrypted_key,
            "oaepHashingAlgorithm": "NONE",
            "iv": "",
            "encryptedData": encrypted_data,
            "clientInfo": self.config.client_id,
            "oauthToken": token
        }
        
        headers = {
            "apikey": self.config.api_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = self.config.push_lead_url
        update_bank_lead_trace(
            bank_trace,
            bank_api_url=url,
            request_headers=headers,
            request_payload={
                "body": mask_sensitive_values(api_payload),
                "plain_request": mask_sensitive_values(payload),
            },
        )
        logger.info("Pushing lead to ICICI at %s with timeout %s", url, self.config.timeout_seconds)
        try:
            resp = requests.post(url, json=api_payload, headers=headers, timeout=self.config.timeout_seconds)
        except requests.exceptions.Timeout as exc:
            logger.error("ICICI request timeout| url=%s timeout=%s", url, self.config.timeout_seconds)
            update_bank_lead_trace(
                bank_trace,
                response_payload={"exception": str(exc)},
            )
            raise exc
        
        logger.info("ICICI Push Lead Response status: %s", resp.status_code)
        logger.info("ICICI Push Lead Response body: %s", resp.text)
        
        # Log response for debugging but be careful with PII if any
        logger.info("ICICI Response status: %s", resp.status_code)
        
        if resp.status_code >= 400:
            decrypted_error = self._handle_error_response(resp)
            update_bank_lead_trace(
                bank_trace,
                response_status_code=resp.status_code,
                response_payload={
                    "raw_body": resp.text,
                    "decrypted_body": decrypted_error,
                },
            )
            resp.raise_for_status()

        # Handle successful response decryption
        response_payload = {"raw_body": resp.text, "json_body": None, "decrypted_body": None}
        try:
            data = resp.json()
            response_payload["json_body"] = data
            enc_data = data.get("encryptedData")
            enc_key = data.get("encryptedKey")
            
            if enc_data and enc_key and self.config.pfx_path:
                logger.info("Attempting to decrypt ICICI success response using %s", self.config.pfx_path)
                decrypted = self.decrypt_payload(enc_data, enc_key)
                logger.info("Decrypted ICICI Success Response: %s", decrypted)
                decrypted_data = json.loads(decrypted)
                response_payload["decrypted_body"] = decrypted_data
                update_bank_lead_trace(
                    bank_trace,
                    response_status_code=resp.status_code,
                    response_payload=response_payload,
                )
                return decrypted_data
        except Exception as exc:
            logger.error("Failed to decrypt/parse ICICI success response: %s", str(exc))
        
        fallback_data = resp.json()
        response_payload["json_body"] = fallback_data
        update_bank_lead_trace(
            bank_trace,
            response_status_code=resp.status_code,
            response_payload=response_payload,
        )
        return fallback_data

    def _handle_error_response(self, resp: requests.Response) -> Any:
        """
        Attempts to decrypt and log the ICICI error response.
        """
        try:
            data = resp.json()
            encrypted_data = data.get("encryptedData")
            encrypted_key = data.get("encryptedKey")
            
            if encrypted_data and encrypted_key and self.config.pfx_path:
                logger.info("Attempting to decrypt ICICI error response using %s", self.config.pfx_path)
                decrypted = ICICIEncryptionService.decrypt_payload(
                    encrypted_data_b64=encrypted_data,
                    encrypted_key_b64=encrypted_key,
                    pfx_path=self.config.pfx_path,
                    pfx_password=self.config.pfx_password
                )
                logger.error("Decrypted ICICI Error Response: %s", decrypted)
                try:
                    return json.loads(decrypted)
                except json.JSONDecodeError:
                    return decrypted
            else:
                logger.error("ICICI Error Response (not decryptable): %s", resp.text)
                return resp.text
        except Exception as exc:
            logger.error("Failed to process ICICI error response: %s", str(exc))
            logger.error("Raw ICICI Error Body: %s", resp.text)
            return {"raw_body": resp.text, "decrypt_error": str(exc)}
