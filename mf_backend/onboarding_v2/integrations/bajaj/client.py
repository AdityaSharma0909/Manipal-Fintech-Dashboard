
from __future__ import annotations
import logging
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from onboarding_v2.integrations.bank_trace import update_bank_lead_trace

from .crypto import AESCryptoUtility
from .exceptions import BajajRequestError, BajajTokenError
from .settings import BajajEnvConfig

logger = logging.getLogger(__name__)


@dataclass
class BajajToken:
    token: str
    expires_on: Optional[datetime] = None

    def is_expired(self) -> bool:
        if not self.expires_on:
            return False
        return datetime.utcnow() >= self.expires_on


class BajajClient:
    def __init__(self, config: BajajEnvConfig):
        self.config = config
        self._session = requests.Session()
        self._token: Optional[BajajToken] = None

    def _get_microsoft_token(self) -> BajajToken:
        """Get Microsoft OAuth token for Bajaj API."""
        token_url = self.config.microsoft_token_url
        payload = {
            "client_id": self.config.microsoft_client_id,
            "client_secret": self.config.microsoft_client_secret,
            "grant_type": "client_credentials",
            "resource": self.config.microsoft_resource,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            logger.info("Fetching Microsoft access token")
            response = self._session.post(
                token_url,
                data=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            if response.status_code != 200:
                logger.error(f"Microsoft token API failed with status {response.status_code}: {response.text}")
                raise BajajTokenError(
                    f"Microsoft token API failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

            result = response.json()
            access_token = result.get("access_token")
            if not access_token:
                raise BajajTokenError("Microsoft access_token is missing in response")

            expires_in = result.get("expires_in", 3600)
            expires_on = datetime.utcnow() + timedelta(seconds=int(expires_in))
            logger.info("Successfully obtained Microsoft access token")
            return BajajToken(token=access_token, expires_on=expires_on)

        except BajajTokenError:
            raise
        except Exception as ex:
            logger.exception("Microsoft token generation failed")
            raise BajajTokenError(f"Microsoft token generation failed: {str(ex)}")

    def _ensure_token(self):
        if self._token and not self._token.is_expired():
            return self._token
        self._token = self._get_microsoft_token()
        return self._token

    def create_lead(
        self,
        lead_data: Dict[str, Any],
        source_header: Optional[str] = None,
        bank_trace=None,
    ) -> Dict[str, Any]:
        """Create a lead in Bajaj CRM."""
        request_uuid = uuid.uuid4().hex
        logger.info(f"Bajaj create_lead start, request_uuid={request_uuid}")

        # Step 1: Prepare plain request
        plain_request_json = json.dumps(lead_data, separators=(",", ":"), ensure_ascii=False)
        logger.info(f"Bajaj plain request: {plain_request_json}")

        # Step 2: Encrypt request if bypass is not enabled
        encrypted_request = plain_request_json
        if not self.config.bypass_encryption:
            try:
                logger.info("Encrypting Bajaj request")
                encrypted_request = AESCryptoUtility.encrypt(
                    plain_request_json,
                    self.config.shared_secret_key,
                    self.config.shared_secret_iv,
                )
            except Exception as ex:
                logger.exception("Bajaj request encryption failed")
                raise BajajRequestError(f"Bajaj request encryption failed: {str(ex)}")

        # Step 3: Get token
        token = self._ensure_token()

        # Step 4: Call Bajaj API
        api_url = f"{self.config.base_api_url}{self.config.save_lead_endpoint}"
        payload = {"text": encrypted_request}
        headers = {
            "Ocp-Apim-Subscription-Key": self.config.ocp_apim_subscription_key,
            "source": source_header or self.config.header_source,
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        }
        update_bank_lead_trace(
            bank_trace,
            bank_api_url=api_url,
            request_headers=headers,
            request_payload={
                "body": payload,
                "plain_request": lead_data,
                "encryption_bypassed": self.config.bypass_encryption,
            },
        )

        try:
            logger.info(f"Sending Bajaj API request to {api_url}")
            response = self._session.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout_seconds,
            )
            response_payload = {
                "raw_body": response.text,
                "json_body": None,
                "encrypted_text": None,
                "decrypted_body": None,
            }
            if response.status_code != 200:
                logger.error(
                    f"Bajaj API failed with status {response.status_code}: {response.text}"
                )
                try:
                    response_payload["json_body"] = response.json()
                    response_payload["encrypted_text"] = response_payload["json_body"].get("text")
                except Exception:
                    pass
                update_bank_lead_trace(
                    bank_trace,
                    response_status_code=response.status_code,
                    response_payload=response_payload,
                )
                raise BajajRequestError(
                    f"Bajaj API failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

            result_json = response.json()
            response_payload["json_body"] = result_json
            if "text" not in result_json:
                update_bank_lead_trace(
                    bank_trace,
                    response_status_code=response.status_code,
                    response_payload=response_payload,
                )
                raise BajajRequestError(
                    "Invalid response format: missing 'text' field",
                    status_code=response.status_code,
                    response_text=response.text,
                )
            encrypted_response_text = result_json["text"]
            response_payload["encrypted_text"] = encrypted_response_text

            # Step 5: Decrypt response
            plain_response = encrypted_response_text
            if not self.config.bypass_encryption:
                try:
                    logger.info("Decrypting Bajaj response")
                    plain_response = AESCryptoUtility.decrypt(
                        encrypted_response_text,
                        self.config.shared_secret_key,
                        self.config.shared_secret_iv,
                    )
                except Exception as ex:
                    logger.exception("Bajaj response decryption failed")
                    update_bank_lead_trace(
                        bank_trace,
                        response_status_code=response.status_code,
                        response_payload=response_payload,
                    )
                    raise BajajRequestError(f"Bajaj response decryption failed: {str(ex)}")

            # Parse plain response
            try:
                response_object = json.loads(plain_response)
                if isinstance(response_object, str):
                    response_object = json.loads(response_object)
            except json.JSONDecodeError:
                response_object = {"raw": plain_response}
            response_payload["decrypted_body"] = response_object
            update_bank_lead_trace(
                bank_trace,
                response_status_code=response.status_code,
                response_payload=response_payload,
            )

            logger.info(f"Bajaj create_lead complete, response: {json.dumps(response_object)}")
            return response_object

        except BajajRequestError:
            raise
        except Exception as ex:
            logger.exception("Unexpected error in Bajaj create_lead")
            update_bank_lead_trace(
                bank_trace,
                response_payload={"exception": str(ex)},
            )
            raise BajajRequestError(f"Unexpected error in Bajaj create_lead: {str(ex)}")
