from os import path
from pathlib import Path
import environ as __environ
import os

# Monkeypatch smtplib for Python 3.12+ compatibility with Django 4.0.4
import smtplib
_orig_starttls = getattr(smtplib.SMTP, 'starttls', None)
if _orig_starttls:
    def _patched_starttls(self, *args, **kwargs):
        kwargs.pop('keyfile', None)
        kwargs.pop('certfile', None)
        return _orig_starttls(self, *args, **kwargs)
    smtplib.SMTP.starttls = _patched_starttls

_orig_smtp_ssl_init = getattr(smtplib.SMTP_SSL, '__init__', None)
if _orig_smtp_ssl_init:
    def _patched_smtp_ssl_init(self, *args, **kwargs):
        kwargs.pop('keyfile', None)
        kwargs.pop('certfile', None)
        return _orig_smtp_ssl_init(self, *args, **kwargs)
    smtplib.SMTP_SSL.__init__ = _patched_smtp_ssl_init

BASE_DIR = Path(__file__).resolve().parent.parent
env = __environ.Env()
# print(path.join(BASE_DIR, ".env"))
__environ.Env.read_env(env_file=path.join(BASE_DIR, ".env"))


class __Environment:
    def __init__(self) -> None:
        self.APP_ENV: str = None
        self.PAYMENT_ENV:str = None

        self.RADIAN_LENDER_CODE: str = None

        self.BASE_URL: str = None
        self.DJANGO_POSTGRES_HOST: str = None
        self.DJANGO_POSTGRES_PORT: int = None
        self.DJANGO_POSTGRES_USER: str = None
        self.DJANGO_POSTGRES_PASSWORD: str = None
        self.DJANGO_POSTGRES_DATABASE: str = None
        self.EMAIL_USE_TLS: bool = None
        self.EMAIL_USE_SSL: bool = None
        self.EMAIL_HOST: str = None
        self.EMAIL_PORT: int = None
        self.EMAIL_HOST_USER: str = None
        self.EMAIL_HOST_PASSWORD: str = None
        self.DEFAULT_FROM_EMAIL: str = None
        self.DEFAULT_TO_EMAIL: str = None

        self.DEFAULT_BH_EMAIL: str = None
        self.TIMESTAMP_EXPORT_EMAIL: str = None
        self.BANCA_LEADS_EXPORT_EMAIL: str = None
        self.BANCA_LEADS_EXPORT_CC: str = None
        self.MULTI_TABLE_EXPORT_EMAIL: str = None
        self.MULTI_TABLE_EXPORT_CC: str = None
        self.BANK_CRM_REPORT_EMAIL: str = None
        self.BANK_CRM_REPORT_CC: str = None

        self.BT_DISBURSAL_EXPORT_EMAIL: str = None
        self.BT_DISBURSAL_EXPORT_CC: str = None
        self.NEW_GL_AGAINST_BT_EXPORT_EMAIL: str = None
        self.NEW_GL_AGAINST_BT_EXPORT_CC: str = None

        self.DJANGO_SUPERUSER_USERNAME: str = None
        self.DJANGO_SUPERUSER_PASSWORD: str = None
        self.DJANGO_SUPERUSER_PHONE: str = None

        self.CURRENT_GTS_RATE: str = None

        self.FCM_API_KEY: str = None
        self.GOOGLE_API_KEY: str = None

        self.BROKER_URL: str = None
        self.CELERY_RESULT_BACKEND: str = None

        # Production database dump / development download jobs
        self.DATABASE_BACKUP_DIR: str = None
        self.DATABASE_BACKUP_PREFIX: str = None
        self.PRODUCTION_SSH_HOST: str = None
        self.PRODUCTION_SSH_PORT: int = None
        self.PRODUCTION_SSH_USER: str = None
        self.PRODUCTION_SSH_PASSWORD: str = None
        self.PRODUCTION_SSH_PRIVATE_KEY_PATH: str = None
        self.PRODUCTION_SSH_KNOWN_HOSTS_PATH: str = None
        self.PRODUCTION_BACKUP_REMOTE_DIR: str = None
        self.DATABASE_BACKUP_EMAIL: str = None

        self.OTP_TIMEOUT: str = None
        self.MASTER_OTP: str = None
        self.MASTER_PASSWORD: str = None

        self.SMS_API_KEY: str = None
        self.PROCESS_LOAN_BATCH: int = 0
        self.PRE_BUILD_DAYS: int = 0
        self.FRS_USERNAME: str = None
        self.FRS_PASSWORD: str = None
        self.LOAN_PAN_CHECK_ELIGIBILITY: str = None
        self.STORAGE_ACCESS_KEY: str = None
        self.STORAGE_SECRET_KEY: str = None
        self.STORAGE_ENDPOINT: str = None
        self.DEV_STORAGE_BUCKET_NAME: str = None
        self.PROD_STORAGE_BUCKET_NAME: str = None
        self.STORAGE_USE_SSL: str = None
        self.DEFAULT_CPC_ADMIN_EMAIL: str = None

        self.TEST_LM_USERNAME: str = None
        self.TEST_LM_PHONE: str = None
        self.TEST_CUSTOMER_PHONE: str = None

        self.ELASTICSEARCH_HOST:str=None
        self.ELASTICSEARCH_PORT:str=None
        self.ELASTICSEARCH_USERNAME:str=None
        self.ELASTICSEARCH_PASSWORD:str=None
        
        self.FEDERAL_ENV:str=None
        self.FEDERAL_CERT_FILE_PATH:str=None
        self.FEDERAL_UAT_BASE_URL:str=None
        self.FEDERAL_PAN_PATH:str=None
        self.FEDERAL_DEDUPE_PATH:str=None
        self.FEDERAL_NAMECHECK_PATH:str=None
        self.FEDERAL_UAT_CLIENT_ID:str=None
        self.FEDERAL_UAT_CLIENT_SECRET:str=None
        self.FEDERAL_UAT_USER_ID:str=None
        self.FEDERAL_UAT_CHANNEL_ID:str=None
        self.FEDERAL_UAT_USERNAME:str=None
        self.FEDERAL_UAT_PAN_PASSWORD:str=None
        self.FEDERL_UAT_USER_ACCESS_CODE:str=None
        self.FEDERAL_CUSTOMER_CREATION_PATH:str=None
        self.FEDERAL_CUSTOMER_ENQUIRY_PATH:str=None
        self.FEDERAL_NAME_DOB_PATH:str=None
        self.FEDERAL_GL_OPEN_PATH:str=None
        self.FEDERAL_GL_ACCOUNT_INSERT:str=None
        self.FEDERAL_GL_CUSTOMER_VALIDATION:str=None
        self.REQUEST_LOAN_AMOUNT_CHECK:str=None
        self.FEDERAL_GL_PLEDGE_CARD: str = None
        self.PINCODE_GOV_API_KEY: str = None
        self.CIPHERPAY_BASE_URL: str = None
        self.CIPHERPAY_PARTNER_CODE: str = None
        self.CIPHERPAY_PARTNER_ID: str = None
        self.CIPHERPAY_HEADER_TOKEN: str = None
        self.CIPHERPAY_JWT_KEY: str = None
        self.RADIAN_VPA: str = None
        self.SPRINT_SECRET:str=None
        self.SPRINT_URL:str=None
        self.KYC_VENDOR:str=None
        
        self.SCORE_ME_BASE_URL:str=None
        self.SCORE_ME_CLIENT_ID:str=None
        self.SCORE_ME_CLIENT_SECRET:str=None
        self.IMONEY_SECRET_KEY:str=None
        self.PAY_ID:str=None

        self.WORKAPPS_API_KEY:str=None
        self.WORKAPPS_API_SECRET:str=None
        self.SAAS_URL: str = None
        self.SAAS_ACCESS_KEY: str = None
        self.SAAS_SECRET_KEY: str = None
        self.SAAS_CLIENT_CODE: str = None
        self.SAAS_MODEL_NAME: str = None
        self.SAAS_AGREEMENT_ID: str = None
        self.SAAS_CREATE_LOAN_URL: str = None
        self.SAAS_UPLOAD_DOC_URL: str = None
        self.SAAS_PRODUCT_ID: str = None
        self.SAAS_WEBHOOK_SECRET: str = None
        # SAAS per-endpoint overrides
        self.SAAS_ACCESS_KEY_PRE_SCREEN: str = None
        self.SAAS_SECRET_KEY_PRE_SCREEN: str = None
        self.SAAS_CLIENT_CODE_PRE_SCREEN: str = None
        self.SAAS_ACCESS_KEY_CREATE_LOAN: str = None
        self.SAAS_SECRET_KEY_CREATE_LOAN: str = None
        self.SAAS_CLIENT_CODE_CREATE_LOAN: str = None
        self.SAAS_SAVE_ONBOARD_URL: str = None
        self.SAAS_UPDATE_ONBOARD_URL: str = None
        self.SAAS_NOTIFICATION_URL: str = None
        self.SAAS_FUND_REFUND_URL: str = None
        self.SAAS_ACCESS_KEY_ONBOARD: str = None
        self.SAAS_SECRET_KEY_ONBOARD: str = None
        self.SAAS_CLIENT_CODE_ONBOARD: str = None
        # Used only for health/validation; must be base host (no endpoint appended)
        # Example: SAAS_URL=https://uat-manipal-api.finncub.com
        # Object storage (MinIO/E2E)
        self.STORAGE_ENDPOINT: str = None
        self.STORAGE_ACCESS_KEY: str = None
        self.STORAGE_SECRET_KEY: str = None
        self.STORAGE_BUCKET_NAME: str = None
        self.STORAGE_USE_SSL: str = None
        self.STORAGE_PRESIGNED_GET_EXPIRY_HOURS: str = None
        # Bureau (Signzy Experian)
        self.SIGNZY_EXP_API_URL: str = None
        self.SIGNZY_EXP_AUTH_TOKEN: str = None
        self.SIGNZY_CONSENT_IP: str = None
        self.SIGNZY_CONSENT_MESSAGE_ID: str = None
        # Slack notifications (SAAS lifecycle)
        self.SAAS_SLACK_WEBHOOK_URL: str = None

        # CRIF Bureau Configuration
        self.CRIF_CALLBACK_URL: str = None
        self.CRIF_REDIRECT_URL: str = None
        self.CRIF_WEBHOOK_SECRET: str = None
        self.CRIF_BUREAU_ELIGIBLE_SCORE: str = None

        # Leegality Configuration
        self.LEEGALITY_BASE_URL: str = None
        self.LEEGALITY_AUTH_TOKEN: str = None
        self.LEEGALITY_SALT_KEY: str = None
        
        self.SENTRY_DSN: str = None
        self.SENTRY_ENVIRONMENT: str = None
        self.SENTRY_RELEASE: str = None
        self.SENTRY_TRACES_SAMPLE_RATE: str = None
        self.SENTRY_PROFILES_SAMPLE_RATE: str = None
        self.SENTRY_SEND_DEFAULT_PII: str = None
        self.SENTRY_ENABLE_LOGS: str = None
        # AbleCredit (video PD)
        self.ABLE_CREDIT_HOST: str = None
        self.ABLE_CREDIT_TENANT_ID: str = None
        self.ABLE_CREDIT_API_KEY: str = None
        self.ABLE_CREDIT_SDK_KEY: str = None
        # Cover fox insurance
        self.COVER_FOX_USERNAME: str = None
        self.COVER_FOX_PASSWORD : str = None
        self.COVER_FOX_REQUEST_TOKEN_URL : str = None
        self.COVER_FOX_LOGIN_URL : str = None

        # Medibuddy insurance
        self.MEDI_BUDDY_SECRET_KEY: str = None
        self.MEDI_BUDDY_URL: str = None
        self.MEDI_BUDDY_CORPORATE_ID: str = None
        self.MEDI_BUDDY_SHARED_SECRET:str =None


    def run(self):
        for k in self.__dict__.keys():
            # Use default=None so newly added optional keys don't break settings when unset.
            setattr(self, k, env(k, default=None))


environment = __Environment()
environment.run()
print("Environment variables loaded.")
# TODO: test this env setup inside docker container
