"""
config/settings/development.py
================================
Development environment settings.
Extends base.py with dev-specific overrides.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Show full SQL queries in console during development
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}

# Django Debug Toolbar (only active when installed)
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# Relaxed CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend — print to console during dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
