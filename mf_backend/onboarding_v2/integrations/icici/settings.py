import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from django.conf import settings

# .../onboarding_v2/integrations/icici/
_INTEGRATION_DIR = Path(__file__).resolve().parent

def _resolve_icici_file_path(raw: Optional[str]) -> Optional[str]:
    """
    Resolve cert/key paths from env.
    - Absolute paths: used as-is.
    - ``certs/...``: relative to this package.
    - Other relative paths: relative to Django ``BASE_DIR``.
    """
    if raw is None:
        return None
    p = str(raw).strip()
    if not p:
        return None
    if os.path.isabs(p):
        return p
    
    norm = p.replace("\\", "/")
    if norm.startswith("certs/"):
        return str((_INTEGRATION_DIR / norm).resolve())
    
    return str((Path(settings.BASE_DIR) / p).resolve())

@dataclass(frozen=True)
class ICICIConfig:
    env: str
    push_lead_url: str
    token_url: str
    client_id: str
    client_secret: str
    api_key: str
    public_key_path: str
    partner_id: str
    lead_source: str
    product: str
    lead_channel: str
    sub_agent_code: str
    timeout_seconds: int = 60
    pfx_path: Optional[str] = None
    pfx_password: Optional[str] = None

def load_icici_config() -> ICICIConfig:
    env = os.getenv("ICICI_ENV", "UAT").upper()
    
    # New UAT defaults provided by user
    default_token_url = "https://apibankingonesandbox.icici.bank.in/clientcredentials/GenerateAccessToken"
    default_push_url = "https://apibankingonesandbox.icici.bank.in/api/v1/LeadCreationDCRM/LeadCreation"
    
    # Robust path handling for public key
    pub_key_path = _resolve_icici_file_path(
        os.getenv(f"ICICI_{env}_PUBLIC_KEY_PATH") or f"certs/ICICI_{env}_public.cer"
    )

    # PFX for decryption
    pfx_path = _resolve_icici_file_path(os.getenv("ICICI_PFX_PATH"))
    pfx_password = os.getenv("ICICI_PFX_PASSWORD")
    
    return ICICIConfig(
        env=env,
        push_lead_url=os.getenv(f"ICICI_{env}_PUSH_LEAD_URL", default_push_url),
        token_url=os.getenv(f"ICICI_{env}_TOKEN_URL", default_token_url),
        client_id=os.getenv(f"ICICI_{env}_CLIENT_ID", "kBVanlA5SRbaf4XHAbIvbGDAFMxPqaOG"),
        client_secret=os.getenv(f"ICICI_{env}_CLIENT_SECRET", "IGOlsF8m7NkPXQF3"),
        api_key=os.getenv(f"ICICI_{env}_API_KEY", "kBVanlA5SRbaf4XHAbIvbGDAFMxPqaOG"),
        public_key_path=pub_key_path,
        partner_id=os.getenv(f"ICICI_{env}_PARTNER_ID", "PI07515"),
        lead_source=os.getenv(f"ICICI_{env}_LEAD_SOURCE", "LSM0018"),
        product=os.getenv(f"ICICI_{env}_PRODUCT", "CRM728"),
        lead_channel=os.getenv(f"ICICI_{env}_LEAD_CHANNEL", "Digital"),
        sub_agent_code=os.getenv(f"ICICI_{env}_SUB_AGENT_CODE", ""),
        timeout_seconds=int(os.getenv(f"ICICI_{env}_TIMEOUT_SECONDS", "60")),
        pfx_path=pfx_path,
        pfx_password=pfx_password
    )
