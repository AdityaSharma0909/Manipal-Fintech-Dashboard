from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class SaasWebhookUser(AnonymousUser):
    role = None

    @property
    def is_authenticated(self):
        return True

class SaasWebhookAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        provided_token = request.headers.get("X-Saas-Token")
        
        # Also check Authorization header for 'Bearer <token>'
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            provided_token = auth_header.split(" ")[1]

        expected_token = getattr(settings, "SAAS_WEBHOOK_SECRET", None)

        if not provided_token:
            return None

        if expected_token and provided_token == expected_token:
            return (SaasWebhookUser(), None)
        
        # If it doesn't match, return None to allow other authenticators (like OAuth2) to try.
        # We only raise an exception if it was specifically the X-Saas-Token header and it was wrong.
        if request.headers.get("X-Saas-Token"):
            raise exceptions.AuthenticationFailed("Invalid SaaS Webhook Token")
            
        return None
