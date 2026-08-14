
from __future__ import annotations

import logging
from typing import Any, Dict

from onboarding_v2.models import LeadV2

from .client import BajajClient
from .exceptions import BajajIntegrationError
from .mapping import build_bajaj_create_lead_data
from .settings import load_bajaj_config

logger = logging.getLogger(__name__)


def sendToBajaj(lead: LeadV2, *, bank_trace=None) -> Dict[str, Any]:
    """
    Public entry point for Bajaj integration.
    Sends lead to Bajaj CRM and returns the response dict.
    """
    if not isinstance(lead, LeadV2):
        raise BajajIntegrationError("sendToBajaj expects a LeadV2 instance")

    config = load_bajaj_config()
    client = BajajClient(config)
    mapped = build_bajaj_create_lead_data(lead=lead, config=config)
    logger.info(f"Starting sendToBajaj for lead id {lead.id}")
    response = client.create_lead(
        mapped.bajaj_data,
        source_header=mapped.header_source,
        bank_trace=bank_trace,
    )
    return response


def extract_bajaj_lead_id(response: Dict[str, Any]) -> str:
    """Extract Bajaj lead id from API response."""
    if not isinstance(response, dict):
        return ""

    data = response.get("data", {})
    if not isinstance(data, dict):
        return ""

    return str(data.get("lead_id") or "")
