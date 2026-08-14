from __future__ import annotations
from pathlib import Path
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .exceptions import AxisConfigurationError

# .../onboarding_v2/integrations/axis/
_INTEGRATION_DIR = Path(__file__).resolve().parent


def _resolve_axis_file_path(raw: Optional[str]) -> Optional[str]:
    """
    Resolve cert/key PEM paths from env.

    - Absolute paths: used as-is.
    - ``certs/...``: relative to this package (good for Docker).
    - Other relative paths: relative to Django ``BASE_DIR`` (project root).
    """
    if raw is None:
        return None
    p = str(raw).strip()
    if not p:
        return None
    if os.path.isabs(p):
        return p
    norm = p.replace("\\", "/")
    if norm.startswith("certs/") or norm.startswith("Axis_Certificates/"):
        return str((_INTEGRATION_DIR / norm).resolve())
    from django.conf import settings as django_settings

    return str((Path(django_settings.BASE_DIR) / p).resolve())


def _getenv(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name, default)
    if val is None:
        return None
    val = str(val).strip()
    return val if val != "" else None


def _getenv_bool(name: str, default: bool = False) -> bool:
    raw = _getenv(name, None)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


def _getenv_int(name: str, default: int) -> int:
    raw = _getenv(name, None)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class AxisEnvConfig:
    env: str  # "UAT" or "PROD"
    base_url: str

    ibm_client_id: str
    ibm_client_secret: str

    channel_id: str
    service_id: str
    service_version: str

    username: str
    password: str

    mtls_cert_file: Optional[str] = None
    mtls_key_file: Optional[str] = None
    mtls_pkcs12_file: Optional[str] = None
    mtls_pkcs12_password: Optional[str] = None
    verify_ssl: bool = True

    # JOSE keys
    axis_encrypt_public_key_pem_file: str = ""
    partner_sign_private_key_pem_file: str = ""

    # Used to decrypt/verify responses if Axis encrypts/signs
    partner_decrypt_private_key_pem_file: Optional[str] = None
    axis_verify_public_key_pem_file: Optional[str] = None

    timeout_seconds: int = 60

    # Endpoint paths
    login_path: str = "/login"
    create_lead_path: str = "/create-lead"
    get_lead_path: str = "/get-partner-lead-details"

    # Axis create-lead constants (configurable, defaults match repo samples)
    default_customer_type: int = 1
    default_salutation_id: int = 1
    default_layout: int = 1002
    default_created_by_source: int = 54
    default_lead_source: int = 154
    default_lead_owner_id: int = 1
    default_product: int = 365
    default_sub_product: int = 374
    default_lead_priority: int = 100001
    default_status_code: int = 146
    default_branch: str = "0"
    default_sub_source: str = "Sahi_Bandhu"


def load_axis_config() -> AxisEnvConfig:
    env = (_getenv("AXIS_ENV", "UAT") or "UAT").upper()
    if env not in ("UAT", "PROD"):
        raise AxisConfigurationError("AXIS_ENV must be UAT or PROD")

    prefix = f"AXIS_{env}_"

    # Defaults use axis.bank.in (current Axis host). Override with AXIS_<ENV>_BASE_URL if needed.
    base_url = _getenv(prefix + "BASE_URL") or (
        "https://sakshamuat.axis.bank.in/gateway/api/v2/CRMNext"
        if env == "UAT"
        else "https://saksham.axis.bank.in/gateway/api/v2/CRMNext"
    )

    def req(name: str) -> str:
        v = _getenv(prefix + name) or _getenv("AXIS_" + name)
        if not v:
            raise AxisConfigurationError(f"Missing required Axis setting: {prefix}{name}")
        return v

    mtls_pkcs12 = _resolve_axis_file_path(
        _getenv(prefix + "MTLS_PKCS12_FILE") or _getenv("AXIS_MTLS_PKCS12_FILE")
    )
    mtls_pkcs12_password = _getenv(prefix + "MTLS_PKCS12_PASSWORD") or _getenv("AXIS_MTLS_PKCS12_PASSWORD")
    mtls_cert = _resolve_axis_file_path(_getenv(prefix + "MTLS_CERT_FILE") or _getenv("AXIS_MTLS_CERT_FILE"))
    mtls_key = _resolve_axis_file_path(_getenv(prefix + "MTLS_KEY_FILE") or _getenv("AXIS_MTLS_KEY_FILE"))
    pem_encrypt = _resolve_axis_file_path(req("AXIS_ENCRYPT_PUBLIC_KEY_PEM_FILE"))
    pem_sign = _resolve_axis_file_path(
        _getenv(prefix + "PARTNER_SIGN_PRIVATE_KEY_PEM_FILE")
        or _getenv("AXIS_PARTNER_SIGN_PRIVATE_KEY_PEM_FILE")
    )
    pem_decrypt = _resolve_axis_file_path(
        _getenv(prefix + "PARTNER_DECRYPT_PRIVATE_KEY_PEM_FILE")
        or _getenv("AXIS_PARTNER_DECRYPT_PRIVATE_KEY_PEM_FILE")
    )
    if mtls_pkcs12 and not pem_sign:
        pem_sign = ""  # filled from PKCS12 in AxisClient
    elif not pem_sign:
        pem_sign = _resolve_axis_file_path(req("PARTNER_SIGN_PRIVATE_KEY_PEM_FILE"))
    if mtls_pkcs12 and not pem_decrypt:
        pem_decrypt = None
    elif not pem_decrypt:
        pem_decrypt = pem_sign
    pem_verify = _resolve_axis_file_path(
        _getenv(prefix + "AXIS_VERIFY_PUBLIC_KEY_PEM_FILE")
        or _getenv("AXIS_AXIS_VERIFY_PUBLIC_KEY_PEM_FILE")
    )

    return AxisEnvConfig(
        env=env,
        base_url=base_url.rstrip("/"),
        ibm_client_id=req("IBM_CLIENT_ID"),
        ibm_client_secret=req("IBM_CLIENT_SECRET"),
        channel_id=req("CHANNEL_ID"),
        service_id=req("SERVICE_ID"),
        service_version=req("SERVICE_VERSION"),
        username=req("USERNAME"),
        password=req("PASSWORD"),
        mtls_cert_file=mtls_cert,
        mtls_key_file=mtls_key,
        mtls_pkcs12_file=mtls_pkcs12,
        mtls_pkcs12_password=mtls_pkcs12_password,
        verify_ssl=_getenv_bool(prefix + "VERIFY_SSL", True),
        axis_encrypt_public_key_pem_file=pem_encrypt,
        partner_sign_private_key_pem_file=pem_sign,
        partner_decrypt_private_key_pem_file=pem_decrypt,
        axis_verify_public_key_pem_file=pem_verify,
        timeout_seconds=_getenv_int(prefix + "TIMEOUT_SECONDS", 60),
        login_path=_getenv(prefix + "LOGIN_PATH") or _getenv("AXIS_LOGIN_PATH") or "/login",
        create_lead_path=_getenv(prefix + "CREATE_LEAD_PATH")
        or _getenv("AXIS_CREATE_LEAD_PATH")
        or "/create-lead",
        get_lead_path=_getenv(prefix + "GET_LEAD_PATH")
        or _getenv("AXIS_GET_LEAD_PATH")
        or "/get-partner-lead-details",
        default_customer_type=_getenv_int(prefix + "DEFAULT_CUSTOMER_TYPE", 1),
        default_salutation_id=_getenv_int(prefix + "DEFAULT_SALUTATION_ID", 1),
        default_layout=_getenv_int(prefix + "DEFAULT_LAYOUT", 1002),
        default_created_by_source=_getenv_int(prefix + "DEFAULT_CREATED_BY_SOURCE", 54),
        default_lead_source=_getenv_int(prefix + "DEFAULT_LEAD_SOURCE", 154),
        default_lead_owner_id=_getenv_int(prefix + "DEFAULT_LEAD_OWNER_ID", 1),
        default_product=_getenv_int(prefix + "DEFAULT_PRODUCT", 365),
        default_sub_product=_getenv_int(prefix + "DEFAULT_SUB_PRODUCT", 374),
        default_lead_priority=_getenv_int(prefix + "DEFAULT_LEAD_PRIORITY", 100001),
        default_status_code=_getenv_int(prefix + "DEFAULT_STATUS_CODE", 146),
        default_branch=_getenv(prefix + "DEFAULT_BRANCH", "0") or "0",
        default_sub_source=_getenv(prefix + "DEFAULT_SUB_SOURCE", "Sahi_Bandhu") or "Sahi_Bandhu",
    )
