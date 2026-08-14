import logging
from datetime import datetime
from django.conf import settings
from rest_framework import status
from crm_integration.exceptions import TokenApiException
from crm_integration.api_clients.base_client import BaseHttpClient

logger = logging.getLogger(__name__)


class BaseTokenProvider(BaseHttpClient):
    """Abstract base for Token Providers."""

    async def get_token(self) -> str:
        raise NotImplementedError("Subclasses must implement get_token")


class MicrosoftTokenProvider(BaseTokenProvider):
    """Fetches access token from Azure AD OAuth endpoint."""

    def _get_config(self):
        return settings.GATEWAY_CONFIG

    async def get_token(self) -> str:
        cfg = self._get_config()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_prefix = f"{timestamp}"
        directory_name = settings.FILE_STORAGE.get('TOKEN_LOG_PATH', 'TokenRequestLogs')

        token_url = cfg.get('MICROSOFT_TOKEN_URL', 'https://login.microsoftonline.com/bajajfinance.in/oauth2/token')
        resource = cfg.get('MICROSOFT_RESOURCE', 'https://management.azure.com/')
        client_id = cfg.get('MICROSOFT_CLIENT_ID', '')
        client_secret = cfg.get('MICROSOFT_CLIENT_SECRET', '')

        if not client_id:
            raise TokenApiException(
                "GATEWAY_MICROSOFT_CLIENT_ID is not configured.",
                status.HTTP_500_INTERNAL_SERVER_ERROR, None
            )
        if not client_secret:
            raise TokenApiException(
                "GATEWAY_MICROSOFT_CLIENT_SECRET is not configured.",
                status.HTTP_500_INTERNAL_SERVER_ERROR, None
            )

        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'resource': resource
        }

        try:
            response = await self._send_request(
                method="POST",
                url=token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                file_prefix=file_prefix,
                directory_name=directory_name
            )

            await self._handle_token_status_code(response, file_prefix, directory_name)

            result = response.json()
            access_token = result.get('access_token')
            if not access_token:
                err_msg = "Microsoft access_token is missing in response."
                self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
                raise TokenApiException(err_msg, response.status_code, response.text)

            return access_token
        except TokenApiException:
            raise
        except Exception as ex:
            err_msg = f"Microsoft token generation failed: {str(ex)}"
            self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
            raise TokenApiException(err_msg, status.HTTP_500_INTERNAL_SERVER_ERROR, None)

    async def _handle_token_status_code(self, response, file_prefix, directory_name):
        if response.status_code == 200:
            return

        error_messages = {
            "404": "Token URL not found (404). Please verify the token endpoint.",
            "404_html": "404 Not Found: Response body contains HTML (likely an error page) instead of token.",
            "429": "Rate limit exceeded (429) while generating token. Retry after: {0}.",
            "500": "Server error (500) during token generation. The server encountered an internal error.",
            "503": "Service unavailable (503) during token generation. The server is temporarily unable to handle the request.",
            "default": "An unexpected error occurred during token generation."
        }

        status_code = response.status_code
        content = response.text
        err_msg = content

        if status_code == status.HTTP_404_NOT_FOUND:
            err_msg = error_messages["404_html"] if "<html>" in content.lower() else error_messages["404"]
        elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After", "No retry-after header found.")
            err_msg = error_messages["429"].format(retry_after)
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            err_msg = error_messages["500"]
        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            err_msg = error_messages["503"]
        else:
            err_msg = error_messages["default"]

        self._log_to_file(f"EXCEPTION: {err_msg}", file_prefix, directory_name)
        raise TokenApiException(err_msg, status_code, content)
