"""
config/settings/base.py
=======================
Base Django settings shared across all environments.
Environment-specific settings (development.py / production.py) import from here.

Load order: base.py → {environment}.py
"""

import os
from pathlib import Path
import environ

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root
APPS_DIR = BASE_DIR / "apps"

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom middleware (order matters)
    "apps.middleware.correlation_id.CorrelationIdMiddleware",
    "apps.middleware.request_logging.RequestLoggingMiddleware",
    "apps.middleware.exception_handler.ExceptionHandlerMiddleware",
]

ROOT_URLCONF = "config.urls"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.authentication.backends.DelegatedJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.common.exceptions.base_exception.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ---------------------------------------------------------------------------
# DRF Spectacular (Swagger/OpenAPI)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "ICICI CRM API",
    "DESCRIPTION": "Enterprise CRM integration service for ICICI Bank.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# Simple JWT
# ---------------------------------------------------------------------------
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": env("JWT_ALGORITHM", default="HS256"),
    "SIGNING_KEY": env("JWT_SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / Media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = BASE_DIR / env("LOG_DIR", default="logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] [{name}] [{process:d}] [{thread:d}] {message}",
            "style": "{",
        },
        "json": {
            "()": "apps.utilities.logger.JsonFormatter",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": env.int("LOG_MAX_BYTES", default=10_485_760),
            "backupCount": env.int("LOG_BACKUP_COUNT", default=5),
            "formatter": "json",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": env.int("LOG_MAX_BYTES", default=10_485_760),
            "backupCount": env.int("LOG_BACKUP_COUNT", default=5),
            "level": "ERROR",
            "formatter": "json",
        },
        "file_requests": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "requests.log",
            "maxBytes": env.int("LOG_MAX_BYTES", default=10_485_760),
            "backupCount": env.int("LOG_BACKUP_COUNT", default=5),
            "formatter": "json",
        },
        "file_integration": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "integration.log",
            "maxBytes": env.int("LOG_MAX_BYTES", default=10_485_760),
            "backupCount": env.int("LOG_BACKUP_COUNT", default=5),
            "formatter": "json",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file_app", "file_error"],
            "level": env("LOG_LEVEL", default="DEBUG"),
            "propagate": False,
        },
        "apps.middleware.request_logging": {
            "handlers": ["file_requests"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.integrations": {
            "handlers": ["console", "file_integration", "file_error"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# ---------------------------------------------------------------------------
# ICICI CRM Integration
# ---------------------------------------------------------------------------
# Note: Most URLs and credentials are dynamically fetched from the 
# icici_app_settings database table. These settings provide defaults.
ICICI_CRM = {
    "BASE_URL": env("ICICI_CRM_BASE_URL", default=""),
    "API_KEY": env("ICICI_CRM_API_KEY", default=""),
    "API_SECRET": env("ICICI_CRM_API_SECRET", default=""),
    "TIMEOUT": env.int("ICICI_CRM_TIMEOUT_SECONDS", default=30),
    "MAX_RETRIES": env.int("ICICI_CRM_MAX_RETRIES", default=3),
    "RETRY_BACKOFF_FACTOR": env.float("ICICI_CRM_RETRY_BACKOFF_FACTOR", default=0.5),
}

# ---------------------------------------------------------------------------
# App Metadata
# ---------------------------------------------------------------------------
APP_NAME = env("APP_NAME", default="ICICI CRM Backend")
APP_VERSION = env("APP_VERSION", default="1.0.0")
ENCRYPTION_KEY = env("ENCRYPTION_KEY")

# ---------------------------------------------------------------------------
# ICICI Integration Certificates
# ---------------------------------------------------------------------------
ICICI_PUBLIC_KEY_PATH = env("ICICI_PUBLIC_KEY_PATH", default=BASE_DIR / "certs" / "ICICI_UAT_public.cer")
ICICI_PFX_PATH = env("ICICI_PFX_PATH", default=BASE_DIR / "certs" / "banksekure_2020.pfx")
ICICI_PFX_PASSWORD = env("ICICI_PFX_PASSWORD", default="password")

# -----------------------------------------------------------------------------
# Gold Loan API (Auth Delegation)
# -----------------------------------------------------------------------------
GOLD_LOAN_API = {
    "BASE_URL": env("GOLD_LOAN_API_BASE_URL", default=""),
    "AUTHORIZE_ENDPOINT": env("GOLD_LOAN_API_AUTH_ENDPOINT", default="api/Auth/Authorize"),
    "KEY": env("GOLD_LOAN_API_KEY", default=""),
}
