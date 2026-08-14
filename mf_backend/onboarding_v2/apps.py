from django.apps import AppConfig


class OnboardingV2Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "onboarding_v2"
    verbose_name = "Onboarding V2"

    def ready(self):
        import onboarding_v2.signals  # noqa
        
        # Force urllib3 to use IPv4 only to avoid "Network is unreachable" errors on IPv6 addresses
        try:
            import socket
            import urllib3.util.connection as connection
            connection.allowed_gai_family = lambda: socket.AF_INET
        except ImportError:
            pass


