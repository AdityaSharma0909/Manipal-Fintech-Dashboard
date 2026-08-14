from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from onboarding_v2.models import LeadV2

from .client import AxisClient
from .exceptions import AxisIntegrationError
from .mapping import build_axis_create_lead_data
from .settings import load_axis_config


logger = logging.getLogger(__name__)


def sendToAxis(lead: LeadV2, *, request_uuid: Optional[str] = None, bank_trace=None) -> Dict[str, Any]:
    """
    Public entrypoint for Axis integration.

    Core team usage:
        from onboarding_v2.integrations.axis import sendToAxis
        sendToAxis(lead_obj)

    Notes:
    - This function does NOT decide whether the lead should go to Axis.
      The calling layer should check (e.g. lead.lead_type == 'BANK_LEAD').
    - Uses env-based settings; supports UAT/PROD via AXIS_ENV and AXIS_<ENV>_* vars.
    """
    if not isinstance(lead, LeadV2):
        raise AxisIntegrationError("sendToAxis expects a LeadV2 instance")

    cfg = load_axis_config()
    client = AxisClient(cfg)
    mapped = build_axis_create_lead_data(lead=lead, config=cfg)

    req_uuid = request_uuid or uuid.uuid5(uuid.NAMESPACE_URL, f"axis:create-lead:{lead.id}").hex
    logger.info("Axis sendToAxis start| lead_id=%s env=%s uuid=%s", str(lead.id), cfg.env, req_uuid)

    resp = client.create_lead(lead_data=mapped.axis_data, request_uuid=req_uuid, bank_trace=bank_trace)
    logger.info("Axis sendToAxis done| lead_id=%s env=%s uuid=%s", str(lead.id), cfg.env, req_uuid)
    return resp

