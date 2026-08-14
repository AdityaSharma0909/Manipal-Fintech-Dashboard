import base64
import json
import logging
import uuid
from typing import Dict, Any

from django.conf import settings

from apps.integrations.icici.base_client import ICICIBaseClient
from apps.utilities.icici_encryption import ICICIEncryptionService
from apps.common.exceptions.integration_exceptions import (
    ICICIIntegrationException,
    ICICIAuthException
)

logger = logging.getLogger(__name__)


class ICICILeadClient(ICICIBaseClient):
    """
    ICICI CRM Lead Integration Client
    """

    def get_bearer_token(self, app_settings) -> str:

        try:

            credentials = (
                f"{app_settings.client_id}:"
                f"{app_settings.client_secret}"
            )

            encoded_credentials = base64.b64encode(
                credentials.encode("utf-8")
            ).decode("utf-8")

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                "grant_type": "client_credentials"
            }

            logger.info("Generating ICICI access token")

            response = self._http.post(
                app_settings.token_url,
                data=payload,
                headers=headers
            )

            logger.info(
                f"ICICI Token API Response Status: "
                f"{response.status_code}"
            )

            logger.debug(
                f"ICICI Token API Response: {response.text}"
            )

            if response.status_code != 200:

                logger.error(
                    f"Token API Failed | "
                    f"Status={response.status_code} | "
                    f"Response={response.text}"
                )

                raise ICICIAuthException(
                    "Failed to generate ICICI token."
                )

            response_data = response.json()

            access_token = response_data.get("access_token")

            if not access_token:

                logger.error(
                    "Access token missing in ICICI response"
                )

                raise ICICIAuthException(
                    "Access token missing."
                )

            logger.info(
                "ICICI access token generated successfully"
            )

            return access_token

        except Exception as ex:

            logger.exception(
                "ICICI token generation failed"
            )

            raise ICICIAuthException(
                "ICICI authentication failed."
            ) from ex

    def push_lead(
        self,
        plain_payload: Dict[str, Any],
        app_settings
    ) -> Dict[str, Any]:

        try:

            # =====================================================
            # STEP 1: GET TOKEN
            # =====================================================

            token = self.get_bearer_token(app_settings)

            # =====================================================
            # STEP 2: ENCRYPT PAYLOAD
            # =====================================================

            payload_json = json.dumps(
                plain_payload,
                separators=(",", ":")
            )

            logger.info(
                f"ICICI Plain Payload: {payload_json}"
            )

            encrypted_key, encrypted_data = (
                ICICIEncryptionService.encrypt_payload(
                    payload_json,
                    settings.ICICI_PUBLIC_KEY_PATH
                )
            )

            logger.info("ICICI Payload Encrypted Successfully")

            # =====================================================
            # PRINT ENCRYPTED VALUES
            # =====================================================

            print("\n" + "=" * 100)
            print("ICICI ENCRYPTED REQUEST")
            print("=" * 100)

            print("\nACCESS TOKEN:\n")
            print(token)

            print("\nENCRYPTED KEY:\n")
            print(encrypted_key)

            print("\nENCRYPTED DATA:\n")
            print(encrypted_data)

            print("\n" + "=" * 100)

            # =====================================================
            # STEP 3: BUILD API PAYLOAD
            # =====================================================

            api_payload = {
                "requestId": str(uuid.uuid4()),
                "service": "LeadCreation",
                "encryptedKey": encrypted_key,

                # TRY BOTH VALUES IF 401 COMES
                # "NONE"
                # "SHA512"
                "oaepHashingAlgorithm": "NONE",

                "iv": "",
                "encryptedData": encrypted_data,

                # IMPORTANT
                "clientInfo": app_settings.client_id,

                # IMPORTANT
                "oauthToken": token
            }

            # =====================================================
            # STEP 4: HEADERS
            # =====================================================

            headers = {
                "apikey": app_settings.client_id,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            logger.info(
                "ICICI Lead Push Request Initiated"
            )

            logger.debug(
                f"ICICI Request Headers: "
                f"{json.dumps(headers, indent=2)}"
            )

            logger.debug(
                f"ICICI Request Payload: "
                f"{json.dumps(api_payload)[:2000]}"
            )

            # =====================================================
            # PRINT CURL FOR POSTMAN TESTING
            # =====================================================

            curl_command = f"""
curl --location '{app_settings.customer_url}' \\
--header 'apikey: {app_settings.client_id}' \\
--header 'Authorization: Bearer {token}' \\
--header 'Content-Type: application/json' \\
--header 'Accept: application/json' \\
--data '{json.dumps(api_payload)}'
"""

            print("\n" + "=" * 100)
            print("ICICI CURL REQUEST")
            print("=" * 100)
            print(curl_command)
            print("=" * 100 + "\n")

            # =====================================================
            # STEP 5: API CALL
            # =====================================================

            response = self._http.post(
                app_settings.customer_url,
                json=api_payload,
                headers=headers,
                timeout=60
            )

            logger.info(
                f"ICICI Response Status: "
                f"{response.status_code}"
            )

            logger.info(
                f"ICICI Response Body: "
                f"{response.text}"
            )

            return self._handle_response(
                response=response,
                sent_encrypted_key=encrypted_key,
                sent_encrypted_data=encrypted_data
            )

        except Exception as ex:

            logger.exception(
                f"ICICI CRM Push failed: {str(ex)}"
            )

            raise ICICIIntegrationException(
                "Failed to push lead to ICICI CRM."
            ) from ex

    def _handle_response(
        self,
        response,
        sent_encrypted_key,
        sent_encrypted_data
    ) -> Dict[str, Any]:

        result = {
            "status_code": str(response.status_code),
            "status_text": getattr(response, "reason_phrase", ""),
            "success": response.status_code == 200,
            "encrypted_request": sent_encrypted_data,
            "encrypted_response": response.text,
            "plain_response": "",
            "lead_number": "",
            "message": ""
        }

        try:

            # =====================================================
            # NON-200 RESPONSE
            # =====================================================

            if response.status_code != 200:

                result["message"] = response.text

                logger.error(
                    f"ICICI API Error | "
                    f"status={response.status_code} | "
                    f"response={response.text}"
                )

                return result

            # =====================================================
            # PARSE RESPONSE
            # =====================================================

            response_json = response.json()

            encrypted_data = response_json.get(
                "encryptedData"
            )

            encrypted_key = response_json.get(
                "encryptedKey"
            )

            if not encrypted_data or not encrypted_key:

                result["message"] = (
                    "Encrypted response fields missing."
                )

                logger.error(
                    "encryptedData or encryptedKey missing"
                )

                return result

            # =====================================================
            # DECRYPT RESPONSE
            # =====================================================

            plain_response = (
                ICICIEncryptionService.decrypt_payload(
                    encrypted_data,
                    encrypted_key,
                    settings.ICICI_PFX_PATH,
                    settings.ICICI_PFX_PASSWORD
                )
            )

            result["plain_response"] = plain_response

            logger.info(
                f"ICICI Decrypted Response: "
                f"{plain_response}"
            )

            response_data = json.loads(
                plain_response
            )

            response_message = response_data.get(
                "Response",
                ""
            )

            result["message"] = response_message

            # =====================================================
            # EXTRACT LEAD NUMBER
            # =====================================================

            if (
                response_message and
                "duplicate" not in response_message.lower()
            ):

                parts = response_message.split(" ")

                if parts:

                    result["lead_number"] = (
                        parts[-1]
                        .replace("!!", "")
                        .strip()
                    )

            return result

        except Exception as ex:

            logger.exception(
                f"Error while processing ICICI response: "
                f"{str(ex)}"
            )

            result["message"] = (
                "Error decrypting ICICI response."
            )

            return result