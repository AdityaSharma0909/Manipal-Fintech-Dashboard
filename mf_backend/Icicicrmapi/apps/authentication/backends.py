import logging
import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from apps.utilities.auth_encryption import AuthEncryptionService

logger = logging.getLogger(__name__)
User = get_user_model()


class DelegatedJWTAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class that delegates token validation to an external Gold Loan API.
    
    Workflow:
    1. Extracts Bearer token from request.
    2. Calls Gold Loan API /Authorize endpoint with the token.
    3. If successful, receives encrypted username/roles.
    4. Decrypts username using TripleDES.
    5. Retrieves/Creates local user instance.
    """

    AUTH_HEADER_PREFIX = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.AUTH_HEADER_PREFIX:
            raise exceptions.AuthenticationFailed("Invalid header format.")

        token = parts[1]
        return self._authenticate_via_gold_loan_api(token)

    def _authenticate_via_gold_loan_api(self, token: str):
        config = settings.GOLD_LOAN_API
        if not config["BASE_URL"]:
            # Fallback to standard check if delegation is not configured
            logger.warning("Gold Loan API Base URL not configured. Auth delegation skipped.")
            return None

        auth_url = f"{config['BASE_URL'].rstrip('/')}/{config['AUTHORIZE_ENDPOINT'].lstrip('/')}"
        
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    auth_url,
                    headers={"Authorization": f"Bearer {token}"}
                )

            if response.status_code != 200:
                logger.warning(f"Gold Loan API rejected token. Status: {response.status_code}")
                raise exceptions.AuthenticationFailed("User not authorized by external provider.")

            # Parity with JObject.Parse(content)["EncryptedUserName"]
            data = response.json()
            enc_username = data.get("EncryptedUserName")
            enc_roles = data.get("EncryptedRoles")
            
            if not enc_username:
                raise exceptions.AuthenticationFailed("External provider did not return user info.")

            # Decrypt using TripleDES (DecryptionService.DecryptAuth)
            username = AuthEncryptionService.decrypt_auth_token(enc_username, config["KEY"])
            
            if not username:
                logger.error("Failed to decrypt username from Gold Loan API response.")
                raise exceptions.AuthenticationFailed("Auth decryption failure.")

            # In Django, we need a User object. We'll get or create based on username.
            # This ensures parity with context.HttpContext.Items["UserId"] = decryptedUserName
            user, created = User.objects.get_or_create(username=username, defaults={"is_active": True})
            
            # Store decrypted roles in the user object for permission checks (optional but useful)
            if enc_roles:
                roles = AuthEncryptionService.decrypt_auth_token(enc_roles, config["KEY"])
                user._decrypted_roles = roles # Temporary attribute
            
            return user, {"token": token, "username": username}

        except httpx.RequestError as exc:
            logger.error(f"Network error contacting Gold Loan API: {exc}")
            raise exceptions.AuthenticationFailed("Identity provider unavailable.")
        except Exception as exc:
            logger.error(f"Delegated authentication failure: {str(exc)}")
            raise exceptions.AuthenticationFailed(f"Authentication failed: {exc}")

    def authenticate_header(self, request):
        return f'{self.AUTH_HEADER_PREFIX} realm="api"'
