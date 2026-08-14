import logging
from typing import Any, Dict
from onboarding_v2.models import LeadV2
from .client import ICICIClient
from .mapping import build_icici_lead_payload
from .settings import load_icici_config

logger = logging.getLogger(__name__)

def sendToIcici(lead: LeadV2, *, bank_trace=None) -> Dict[str, Any]:
    """
    Public entrypoint for ICICI integration.
    """
    if not isinstance(lead, LeadV2):
        raise ValueError("sendToIcici expects a LeadV2 instance")

    config = load_icici_config()
    client = ICICIClient(config)
    payload = build_icici_lead_payload(lead, config)

    logger.info("ICICI sendToIcici start| lead_id=%s", str(lead.id))
    logger.debug("ICICI sendToIcici payload| %s", payload)
    try:
        resp = client.push_lead(payload, bank_trace=bank_trace)
        logger.info("ICICI sendToIcici done| lead_id=%s", str(lead.id))
        return resp
    except Exception as e:
        logger.exception("ICICI integration failed for lead_id=%s", str(lead.id))
        raise
