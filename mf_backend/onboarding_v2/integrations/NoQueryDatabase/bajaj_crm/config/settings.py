import os
import re
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-default-secret-key-change-in-prod'),
    ALLOWED_HOSTS=(list, ['*']),
)

# Read .env file from the parent directory of BASE_DIR (workspace root)
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

# Fix: BAJAJ_SHARED_SECRET_IV may contain '#' which django-environ treats as a comment
# delimiter, truncating the value. Re-read it directly from the .env file.
_env_path = os.path.join(BASE_DIR.parent, '.env')
if os.path.exists(_env_path):
    with open(_env_path, encoding='utf-8') as _f:
        for _line in _f:
            _m = re.match(r'\ABAJAJ_SHARED_SECRET_IV=(.*)', _line)
            if _m:
                _raw_iv = _m.group(1).strip()
                # Remove surrounding double quotes if present
                if len(_raw_iv) >= 2 and _raw_iv[0] == '"' and _raw_iv[-1] == '"':
                    _raw_iv = _raw_iv[1:-1]
                # Remove surrounding single quotes if present
                elif len(_raw_iv) >= 2 and _raw_iv[0] == "'" and _raw_iv[-1] == "'":
                    _raw_iv = _raw_iv[1:-1]
                os.environ['BAJAJ_SHARED_SECRET_IV'] = _raw_iv
                break

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    
    # Local apps
    'crm_integration',
]

MIDDLEWARE = [
    'crm_integration.middleware.ErrorHandlingMiddleware',  # Global exception handling first
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Middlewares
    # 'crm_integration.middleware.CorrelationIdMiddleware',
    'crm_integration.middleware.RequestResponseLoggingMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL'),
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production security hardening — active only when DEBUG=False to avoid breaking local dev.
# Set SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS, etc. via environment for production.
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)  # Set to 31536000 (1yr) in prod
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
    SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# REST Framework Configuration
# NOTE: GoldLoanTokenAuthentication intentionally excluded from migration scope.
# Local development runs without GoldLoan-specific authentication.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'crm_integration.exceptions.custom_exception_handler',
}

# Spectacular Swagger Config
SPECTACULAR_SETTINGS = {
    'TITLE': 'Bajaj FinServ CRM Integration API',
    'DESCRIPTION': 'Migrated Django/DRF implementation of Bajaj CRM Lead integration.',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Match .NET Program.cs AddSecurityDefinition("Bearer") + AddSecurityRequirement
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': "Enter 'Bearer' [space] and then your valid JWT token."
            }
        }
    }
}

# Gateway / Token Provider Configuration
GATEWAY_CONFIG = {
    'MICROSOFT_TOKEN_URL': env('GATEWAY_MICROSOFT_TOKEN_URL', default='https://login.microsoftonline.com/bajajfinance.in/oauth2/token'),
    'MICROSOFT_CLIENT_ID': env('GATEWAY_MICROSOFT_CLIENT_ID', default=''),
    'MICROSOFT_CLIENT_SECRET': env('GATEWAY_MICROSOFT_CLIENT_SECRET', default=''),
    'MICROSOFT_RESOURCE': env('GATEWAY_MICROSOFT_RESOURCE', default='https://management.azure.com/'),
    'MICROSOFT_SCOPE': env('GATEWAY_MICROSOFT_SCOPE', default='api://default/.default'),
}

# Bajaj CRM Configurations
BAJAJ_CONFIG = {
    'BASE_API_URL': env('BAJAJ_BASE_API_URL'),
    'SAVE_LEAD_ENDPOINT': env('BAJAJ_SAVE_LEAD_ENDPOINT'),
    'OCP_APIM_SUBSCRIPTION_KEY': env('BAJAJ_OCP_APIM_SUBSCRIPTION_KEY'),
    'HEADER_SOURCE': env('BAJAJ_HEADER_SOURCE'),
    'SHARED_SECRET_KEY': env('BAJAJ_SHARED_SECRET_KEY'),
    'SHARED_SECRET_IV': env('BAJAJ_SHARED_SECRET_IV'),
    'LEAD_TYPE': env('BAJAJ_LEAD_TYPE'),
    'LEAD_SOURCE': env('BAJAJ_LEAD_SOURCE'),
    'LEAD_ORIGIN': env('BAJAJ_LEAD_ORIGIN'),
    'LEAD_CHANNEL': env('BAJAJ_LEAD_CHANNEL'),
    'SRC': env('BAJAJ_SRC'),
    'INTERNAL_SOURCE': env('BAJAJ_INTERNAL_SOURCE'),
    'FOLLOW_UP': env.bool('BAJAJ_FOLLOW_UP', default=False),
    'PRODUCT': env('BAJAJ_PRODUCT'),
    'JOURNEY_NAME': env('BAJAJ_JOURNEY_NAME'),
    'REFERRAL_ID': env('BAJAJ_REFERRAL_ID'),
    'REFERRAL_PARTNER': env('BAJAJ_REFERRAL_PARTNER'),
    'LEAD_DATE_FORMAT': env('BAJAJ_LEAD_DATE_FORMAT', default='%Y-%m-%d %H:%M:%S'),
    'SUB_CODE': env('BAJAJ_SUB_CODE'),
    'DSC_CODE': env('BAJAJ_DSC_CODE'),
}

# Lead Type-specific Configurations
# These mappings are selected based on the incoming request Type field,
# and should contain a full set of values for the external Bajaj lead API.
BAJAJ_LEAD_TYPE_CONFIGS = {
    'balance transfer': {
        'HEADER_SOURCE': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_HEADER_SOURCE', default=env('BAJAJ_HEADER_SOURCE')),
        'LEAD_SOURCE': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_LEAD_SOURCE', default=env('BAJAJ_LEAD_SOURCE')),
        'LEAD_ORIGIN': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_LEAD_ORIGIN', default=env('BAJAJ_LEAD_ORIGIN')),
        'LEAD_CHANNEL': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_LEAD_CHANNEL', default=env('BAJAJ_LEAD_CHANNEL')),
        'SRC': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_SRC', default=env('BAJAJ_SRC')),
        'PRODUCT': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_PRODUCT', default=env('BAJAJ_PRODUCT')),
        'REFERRAL_PARTNER': env('BAJAJ_LEAD_TYPE_BALANCE_TRANSFER_REFERRAL_PARTNER', default=env('BAJAJ_REFERRAL_PARTNER')),
    },
    'fresh lead': {
        'HEADER_SOURCE': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_HEADER_SOURCE', default=env('BAJAJ_HEADER_SOURCE')),
        'LEAD_SOURCE': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_LEAD_SOURCE', default=env('BAJAJ_LEAD_SOURCE')),
        'LEAD_ORIGIN': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_LEAD_ORIGIN', default=env('BAJAJ_LEAD_ORIGIN')),
        'LEAD_CHANNEL': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_LEAD_CHANNEL', default=env('BAJAJ_LEAD_CHANNEL')),
        'SRC': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_SRC', default=env('BAJAJ_SRC')),
        'PRODUCT': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_PRODUCT', default=env('BAJAJ_PRODUCT')),
        'REFERRAL_PARTNER': env('BAJAJ_LEAD_TYPE_FRESH_LEAD_REFERRAL_PARTNER', default=env('BAJAJ_REFERRAL_PARTNER')),
    },
}

# Validation Limits
BAJAJ_VALIDATION = {
    'FULL_NAME_MIN_LENGTH': env.int('VAL_FULL_NAME_MIN_LENGTH', default=1),
    'FULL_NAME_MAX_LENGTH': env.int('VAL_FULL_NAME_MAX_LENGTH', default=80),
    'LOAN_AMOUNT_MIN': env.float('VAL_LOAN_AMOUNT_MIN', default=10000),
    'LOAN_AMOUNT_MAX': env.float('VAL_LOAN_AMOUNT_MAX', default=5000000),
}

# GoldLoan API settings intentionally excluded from migration scope.
# GOLDLOAN_API block removed alongside GoldLoanTokenAuthentication.

# Security Decryption Keys
KEYS = {
    'KEY_PATH': env('KEYS_KEY_PATH', default=''),
    'DECRYPT_KEY': env('KEYS_DECRYPT_KEY', default=''),
}

# Role Access
ROLE_SETTINGS = {
    'AUTHORIZED_ROLES': [role.strip() for role in env('AUTHORIZED_ROLES', default='SBO,Lead Generator').split(',')]
}

# File storage config
FILE_STORAGE = {
    'BASE_PATH': env('FILE_STORAGE_BASE_PATH', default=str(BASE_DIR / 'logs' / 'Audits')),
    'TOKEN_LOG_PATH': env('FILE_STORAGE_TOKEN_LOG_PATH', default='TokenRequestLogs'),
    'LEAD_LOG_PATH': env('FILE_STORAGE_LEAD_LOG_PATH', default='CreateLeadRequestLogs'),
}

# Logging configuration (Django & Standard Logger)
LOG_PATH_ROOT = env('LOG_PATH_ROOT', default=str(BASE_DIR / 'logs'))

# Fix 3: Ensure log directory exists before the logging handlers try to open files.
# Without this, TimedRotatingFileHandler raises FileNotFoundError on first startup.
os.makedirs(LOG_PATH_ROOT, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'crm_integration.middleware.JSONFormatter',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s (CorrID: %(correlation_id)s): %(message)s'
        },
    },
    'filters': {
        'correlation_id': {
            '()': 'crm_integration.middleware.CorrelationIdFilter',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['correlation_id'],
            'formatter': 'standard',
        },
        'file_error': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH_ROOT, env('LOG_PATH_ERROR', default='Error.json')),
            'when': 'D',
            'interval': 1,
            'backupCount': 30,
            'filters': ['correlation_id'],
            'formatter': 'json',
            'level': 'ERROR',
        },
        'file_info': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH_ROOT, env('LOG_PATH_INFO', default='Information.json')),
            'when': 'D',
            'interval': 1,
            'backupCount': 30,
            'filters': ['correlation_id'],
            'formatter': 'json',
            'level': 'INFO',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
