from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from onboarding_v2.models import BankLeadTrace

logger = logging.getLogger(__name__)


def json_safe(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, default=str))
    except Exception:
        return {"raw": str(value)}


def mask_headers(headers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    sensitive_names = ("authorization", "cookie", "token", "secret", "key", "apikey")
    masked = {}
    for name, value in (headers or {}).items():
        if any(sensitive in str(name).lower() for sensitive in sensitive_names):
            masked[name] = "***masked***"
        else:
            masked[name] = str(value)
    return masked


def mask_sensitive_values(value: Any) -> Any:
    sensitive_names = ("authorization", "cookie", "token", "secret", "key", "password", "apikey")
    if isinstance(value, dict):
        masked = {}
        for key, item in value.items():
            if any(sensitive in str(key).lower() for sensitive in sensitive_names):
                masked[key] = "***masked***"
            else:
                masked[key] = mask_sensitive_values(item)
        return masked
    if isinstance(value, list):
        return [mask_sensitive_values(item) for item in value]
    return value


def update_bank_lead_trace(trace: Optional[BankLeadTrace], **fields) -> None:
    if not trace:
        return
    try:
        update_fields = []
        for field, value in fields.items():
            if field == "request_headers":
                value = mask_headers(value)
            elif field in {"request_payload", "response_payload", "metadata"}:
                value = json_safe(value)
            setattr(trace, field, value)
            update_fields.append(field)
        if update_fields:
            update_fields.append("modified_at")
            trace.save(update_fields=update_fields)
    except Exception:
        logger.exception("Failed to update BankLeadTrace")
