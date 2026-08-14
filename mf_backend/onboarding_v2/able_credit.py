"""AbleCredit video-PD integration helpers."""
from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Minimum loan amount (in rupees) that requires a video-PD via AbleCredit.
ABLE_CREDIT_MIN_AMOUNT = 1_000_000  # 10 Lac


class AbleCreditError(Exception):
    pass


def _get_config():
    host = getattr(settings, "ABLE_CREDIT_HOST", "https://col-api-qa.ablecredit.com").rstrip("/")
    tenant_id = getattr(settings, "ABLE_CREDIT_TENANT_ID", None)
    api_key = getattr(settings, "ABLE_CREDIT_API_KEY", None)
    sdk_key = getattr(settings, "ABLE_CREDIT_SDK_KEY", None)
    if not all([host, tenant_id, api_key, sdk_key]):
        raise AbleCreditError("AbleCredit credentials are not fully configured")
    return host, tenant_id, api_key, sdk_key


def requires_video_pd(application) -> bool:
    """Return True when the application's loan amount is >= 10 Lac."""
    try:
        amount = int(application.lead.amount or 0)
    except (TypeError, ValueError):
        amount = 0
    return amount >= ABLE_CREDIT_MIN_AMOUNT


def create_session(application) -> dict:
    """
    Call AbleCredit to create a session for the given application.

    Returns a dict with at least:
        {
            "session_token": "<token>",
            "sdk_key": "<sdk_key>",
            "tenant_id": "<tenant_id>",
        }
    Raises AbleCreditError on failure.
    """
    host, tenant_id, api_key, sdk_key = _get_config()
    url = f"{host}/v1/session"

    lead = application.lead
    customer = getattr(lead, "customer", None) or getattr(application, "customer", None)

    payload = {
        "tenantId": tenant_id,
        "clientLoanId": str(application.application_id),
        "applicantName": str(lead.customer_name or ""),
        "mobileNumber": str(lead.contact_number or ""),
        "loanAmount": int(lead.amount or 0),
    }
    if customer:
        payload["panNumber"] = getattr(customer, "pan_number", None) or ""

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    logger.info(
        "AbleCredit create_session | application=%s | url=%s",
        application.application_id,
        url,
    )

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        logger.info(
            "AbleCredit response | status=%s | body=%s",
            resp.status_code,
            resp.text[:500],
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise AbleCreditError(
            f"AbleCredit API error {exc.response.status_code}: {exc.response.text[:200]}"
        ) from exc
    except requests.RequestException as exc:
        raise AbleCreditError(f"AbleCredit request failed: {exc}") from exc

    data = resp.json()
    session_token = data.get("sessionToken") or data.get("session_token") or data.get("token")
    if not session_token:
        raise AbleCreditError(f"AbleCredit returned no session token: {data}")

    return {
        "session_token": session_token,
        "sdk_key": sdk_key,
        "tenant_id": tenant_id,
        "raw": data,
    }
