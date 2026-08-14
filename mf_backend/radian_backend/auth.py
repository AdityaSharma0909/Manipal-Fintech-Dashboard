from rest_framework.authentication import BaseAuthentication
from users.models import User

class AutoLoginAuthentication(BaseAuthentication):
    """
    Custom authentication backend that automatically authenticates all requests
    as the system superuser / admin user if no other authentication method succeeds.
    This ensures that endpoints requiring user attributes (e.g. role, user_id)
    do not crash with AnonymousUser errors and remain open to everyone.
    """
    def authenticate(self, request):
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if user:
            return (user, None)
        return None
