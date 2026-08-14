import logging
import json
from datetime import datetime
from django.conf import settings
from rest_framework import status
from crm_integration.exceptions import BajajFinServoApiException
from crm_integration.api_clients.base_client import BaseHttpClient

logger = logging.getLogger(__name__)


class BajajFinServoApiClient(BaseHttpClient):
    """API client calling the external Bajaj Finserv CRM APIs with encrypted requests."""
    
    async def create_lead(self, encrypted_payload: str, access_token: str, source_header: str | None = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = f"{timestamp}"
        directory_name = settings.FILE_STORAGE.get('LEAD_LOG_PATH', 'CreateLeadRequestLogs')
        
        base_url = settings.BAJAJ_CONFIG.get('BASE_API_URL')
        endpoint = settings.BAJAJ_CONFIG.get('SAVE_LEAD_ENDPOINT')
        
        if not endpoint:
            raise ValueError("BajajFinServo SaveLead endpoint is not configured.")
            
        api_url = f"{base_url}{endpoint}"
        
        # Build request body: {"text": encrypted_payload}
        payload = {"text": encrypted_payload}
        
        headers = {
            "Ocp-Apim-Subscription-Key": settings.BAJAJ_CONFIG.get('OCP_APIM_SUBSCRIPTION_KEY'),
            "source": source_header or settings.BAJAJ_CONFIG.get('HEADER_SOURCE'),
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Outbound request execution
            response = await self._send_request(
                method="POST",
                url=api_url,
                headers=headers,
                json_data=payload,
                file_prefix=file_prefix,
                directory_name=directory_name
            )
            
            response_body = response.text
            
            
            # Check for non-success status code
            if response.status_code != 200:
                await self._handle_error_response(response, response_body, file_prefix, directory_name)
                
            # Validate JSON format
            try:
                result_json = response.json()
            except json.JSONDecodeError as ex:
                err_msg = "Invalid JSON response received from BajajFinServo API."
                self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
                raise BajajFinServoApiException(err_msg, response.status_code, response_body)
                
            # Validate format contains key 'text'
            if 'text' not in result_json:
                err_msg = "Invalid response format: missing 'text' field."
                self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
                raise BajajFinServoApiException(err_msg, response.status_code, response_body)
                
            if not isinstance(result_json['text'], str):
                err_msg = "Invalid response format: 'text' must be a string."
                self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
                raise BajajFinServoApiException(err_msg, response.status_code, response_body)
                
            return result_json['text']
            
        except BajajFinServoApiException:
            raise
        except Exception as ex:
            logger.exception("Unexpected error in BajajFinServoApiClient create_lead")
            err_msg = f"Something went wrong in API call: {str(ex)}"
            self._log_to_file(f"EXCEPTION: {err_msg}\nStack Trace: {getattr(ex, '__traceback__', '')}", file_prefix, directory_name)
            raise BajajFinServoApiException(err_msg, status.HTTP_500_INTERNAL_SERVER_ERROR, None)

    async def _handle_error_response(self, response, response_body, file_prefix, directory_name):
        error_messages = {
            "403": "Access to the Bajaj Finserv Create Lead API is denied. Please verify authentication credentials or permissions.",
            "403_html": "Access to the Bajaj Finserv Create Lead API is denied. Response body contains HTML (likely an error page) instead of Create Lead Response.",
            "404": "Resource not found. Please check the URL.",
            "404_html": "404 Not Found: Response body contains HTML (likely an error page) instead of Create Lead Response.",
            "429": "Rate limit exceeded. Please retry after some time.",
            "500": "Internal server error. Please try again later.",
            "503": "Service unavailable. Please try again later.",
            "504": "The Bajaj Finserv Create Lead API did not respond within the expected time.",
            "default": "An unexpected error occurred."
        }
        
        status_code = response.status_code
        err_msg = error_messages.get(str(status_code), error_messages['default'])
        
        # Check for HTML responses on certain codes
        if status_code == 404:
            if not response_body or "<html>" in response_body.lower():
                err_msg = error_messages['404_html']
        elif status_code == 403:
            if not response_body or "<html>" in response_body.lower():
                err_msg = error_messages['403_html']
                
        self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
        raise BajajFinServoApiException(err_msg, status_code, response_body)
