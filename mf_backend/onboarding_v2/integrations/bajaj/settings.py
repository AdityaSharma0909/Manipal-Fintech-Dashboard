
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Dict, Optional

from .exceptions import BajajConfigurationError


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
class BajajCrmTypeConfig:
    header_source: str
    lead_source: str
    lead_origin: str
    lead_channel: str
    src: str
    product: str
    referral_partner: str


@dataclass(frozen=True)
class BajajEnvConfig:
    base_api_url: str
    save_lead_endpoint: str
    ocp_apim_subscription_key: str
    header_source: str
    shared_secret_key: str
    shared_secret_iv: str
    microsoft_token_url: str
    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_resource: str
    microsoft_scope: str
    bypass_encryption: bool = False
    timeout_seconds: int = 60

    # Default values from user example
    lead_type: str = "Partner"
    lead_source: str = "CSC"
    lead_origin: str = "CSC"
    lead_channel: str = "CSC"
    src: str = "CSC"
    internal_src: str = "999979"
    follow_up: bool = False
    product: str = "MFPL BT"
    journey_name: str = "Assisted"
    sub_code: str = "DLE11011231"
    dsc_code: str = "DLE110011"
    referral_partner: str = "CSC"
    referral_id: str = "999979"
    crm_type_configs: Optional[Dict[str, BajajCrmTypeConfig]] = None

    def config_for_crm_type(self, crm_type: Optional[str]) -> BajajCrmTypeConfig:
        normalized = (crm_type or "").strip().upper()
        if self.crm_type_configs and normalized in self.crm_type_configs:
            return self.crm_type_configs[normalized]
        return BajajCrmTypeConfig(
            header_source=self.header_source,
            lead_source=self.lead_source,
            lead_origin=self.lead_origin,
            lead_channel=self.lead_channel,
            src=self.src,
            product=self.product,
            referral_partner=self.referral_partner,
        )


def _load_crm_type_config(prefix: str, base: BajajCrmTypeConfig) -> BajajCrmTypeConfig:
    return BajajCrmTypeConfig(
        header_source=_getenv(f"{prefix}_HEADER_SOURCE", base.header_source),
        lead_source=_getenv(f"{prefix}_LEAD_SOURCE", base.lead_source),
        lead_origin=_getenv(f"{prefix}_LEAD_ORIGIN", base.lead_origin),
        lead_channel=_getenv(f"{prefix}_LEAD_CHANNEL", base.lead_channel),
        src=_getenv(f"{prefix}_SRC", base.src),
        product=_getenv(f"{prefix}_PRODUCT", base.product),
        referral_partner=_getenv(f"{prefix}_REFERRAL_PARTNER", base.referral_partner),
    )


def load_bajaj_config() -> BajajEnvConfig:
    # Required settings
    base_api_url = _getenv("BAJAJ_BASE_API_URL")
    save_lead_endpoint = _getenv("BAJAJ_SAVE_LEAD_ENDPOINT")
    ocp_apim_subscription_key = _getenv("BAJAJ_OCP_APIM_SUBSCRIPTION_KEY")
    header_source = _getenv("BAJAJ_HEADER_SOURCE")
    shared_secret_key = _getenv("BAJAJ_SHARED_SECRET_KEY")
    shared_secret_iv = _getenv("BAJAJ_SHARED_SECRET_IV")

    microsoft_token_url = _getenv("GATEWAY_MICROSOFT_TOKEN_URL")
    microsoft_client_id = _getenv("GATEWAY_MICROSOFT_CLIENT_ID")
    microsoft_client_secret = _getenv("GATEWAY_MICROSOFT_CLIENT_SECRET")
    microsoft_resource = _getenv("GATEWAY_MICROSOFT_RESOURCE")
    microsoft_scope = _getenv("GATEWAY_MICROSOFT_SCOPE", "api://default/.default")

    if not base_api_url:
        raise BajajConfigurationError("Missing BAJAJ_BASE_API_URL")
    if not save_lead_endpoint:
        raise BajajConfigurationError("Missing BAJAJ_SAVE_LEAD_ENDPOINT")
    if not ocp_apim_subscription_key:
        raise BajajConfigurationError("Missing BAJAJ_OCP_APIM_SUBSCRIPTION_KEY")
    if not header_source:
        raise BajajConfigurationError("Missing BAJAJ_HEADER_SOURCE")
    if not shared_secret_key:
        raise BajajConfigurationError("Missing BAJAJ_SHARED_SECRET_KEY")
    if not shared_secret_iv:
        raise BajajConfigurationError("Missing BAJAJ_SHARED_SECRET_IV")
    if not microsoft_token_url:
        raise BajajConfigurationError("Missing GATEWAY_MICROSOFT_TOKEN_URL")
    if not microsoft_client_id:
        raise BajajConfigurationError("Missing GATEWAY_MICROSOFT_CLIENT_ID")
    if not microsoft_client_secret:
        raise BajajConfigurationError("Missing GATEWAY_MICROSOFT_CLIENT_SECRET")
    if not microsoft_resource:
        raise BajajConfigurationError("Missing GATEWAY_MICROSOFT_RESOURCE")

    lead_source = _getenv("BAJAJ_LEAD_SOURCE", "CSC")
    lead_origin = _getenv("BAJAJ_LEAD_ORIGIN", "CSC")
    lead_channel = _getenv("BAJAJ_LEAD_CHANNEL", "CSC")
    src = _getenv("BAJAJ_SRC", "CSC")
    product = _getenv("BAJAJ_PRODUCT", "MFPL BT")
    referral_partner = _getenv("BAJAJ_REFERRAL_PARTNER", "CSC")
    base_crm_type_config = BajajCrmTypeConfig(
        header_source=header_source,
        lead_source=lead_source,
        lead_origin=lead_origin,
        lead_channel=lead_channel,
        src=src,
        product=product,
        referral_partner=referral_partner,
    )
    crm_type_configs = {
        "BALANCE_TRANSFER": _load_crm_type_config(
            "BAJAJ_LEAD_TYPE_BALANCE_TRANSFER",
            base_crm_type_config,
        ),
        "FRESH": _load_crm_type_config(
            "BAJAJ_LEAD_TYPE_FRESH_LEAD",
            base_crm_type_config,
        ),
    }

    return BajajEnvConfig(
        base_api_url=base_api_url,
        save_lead_endpoint=save_lead_endpoint,
        ocp_apim_subscription_key=ocp_apim_subscription_key,
        header_source=header_source,
        shared_secret_key=shared_secret_key,
        shared_secret_iv=shared_secret_iv,
        microsoft_token_url=microsoft_token_url,
        microsoft_client_id=microsoft_client_id,
        microsoft_client_secret=microsoft_client_secret,
        microsoft_resource=microsoft_resource,
        microsoft_scope=microsoft_scope,
        bypass_encryption=_getenv_bool("BAJAJ_BYPASS_ENCRYPTION", False),
        timeout_seconds=_getenv_int("BAJAJ_TIMEOUT_SECONDS", 60),
        lead_type=_getenv("BAJAJ_LEAD_TYPE", "Partner"),
        lead_source=lead_source,
        lead_origin=lead_origin,
        lead_channel=lead_channel,
        src=src,
        internal_src=_getenv("BAJAJ_INTERNAL_SRC", _getenv("BAJAJ_INTERNAL_SOURCE", "999979")),
        follow_up=_getenv_bool("BAJAJ_FOLLOW_UP", False),
        product=product,
        journey_name=_getenv("BAJAJ_JOURNEY_NAME", "Assisted"),
        sub_code=_getenv("BAJAJ_SUB_CODE", "DLE11011231"),
        dsc_code=_getenv("BAJAJ_DSC_CODE", "DLE110011"),
        referral_partner=referral_partner,
        referral_id=_getenv("BAJAJ_REFERRAL_ID", "999979"),
        crm_type_configs=crm_type_configs,
    )
