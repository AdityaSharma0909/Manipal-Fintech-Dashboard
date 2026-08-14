"""
Test settings overriding the default DB to use SQLite in-memory.
"""
from .settings import *  # noqa

# Use in-memory SQLite for tests to avoid Postgres dependency
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable migrations for speed by using the syncdb fallback
# Comment this out if you need real migrations in tests.
MIGRATION_MODULES = {
    app.split(".")[-1]: None
    for app in INSTALLED_APPS
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Ensure oauth2 models are defined for apps that reference these settings
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken"
OAUTH2_PROVIDER_GRANT_MODEL = "oauth2_provider.Grant"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "oauth2_provider.RefreshToken"

# Relax DRF auth/permissions for tests
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = []
