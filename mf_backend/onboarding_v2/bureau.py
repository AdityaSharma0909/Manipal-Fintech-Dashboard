import time
import uuid
import logging
import requests
from django.conf import settings

from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import ApplicationDocument
from onboarding_v2.loggers import log_saas_request
from onboarding_v2.models import SaasRequestLog
from onboarding_v2.saas import _split_name, _get_snapshot_payload, _safe_json

logger = logging.getLogger(__name__)


class BureauError(Exception):
    pass


def normalize_bureau_score(value):
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return int(str(value).strip()) if isinstance(value, str) else int(value)
    except (TypeError, ValueError):
        logger.warning("Ignoring non-numeric bureau score | value=%r", value)
        return None


def build_bureau_payload(application):
    """
    Build Signzy Experian bureau payload from saved snapshots and lead.
    Raises BureauError if required fields are missing.
    """
    lead = application.lead
    pan_snap = _get_snapshot_payload(application, ApplicationStage.PAN) or {}
    basic = _get_snapshot_payload(application, ApplicationStage.BASIC) or {}
    personal = _get_snapshot_payload(application, ApplicationStage.PERSONAL) or {}
    address = _get_snapshot_payload(application, ApplicationStage.ADDRESS) or {}

    missing = []
    # PAN number
    pan_doc = ApplicationDocument.objects.filter(
        application=application, document_type="PAN"
    ).first()
    pan_number = (pan_doc.metadata or {}).get("pan_number") if pan_doc else pan_snap.get("pan_number")
    if not pan_number:
        missing.append("pan_number")

    # Name
    full_name = personal.get("full_name") or basic.get("full_name_as_pan") or lead.customer_name
    first_name, _, last_name = _split_name(full_name)
    if not first_name:
        missing.append("first_name")
    if not last_name:
        missing.append("last_name")

    # DOB
    dob = personal.get("dob") or basic.get("dob")
    if not dob:
        missing.append("dob")

    # Phone
    phone = basic.get("phone_number") or lead.contact_number
    if not phone:
        missing.append("phone_number")

    # Pincode
    permanent = address.get("permanent") or {}
    pincode = permanent.get("pincode") or lead.pincode
    if not pincode:
        missing.append("pincode")

    if missing:
        raise BureauError("Missing required fields: " + ", ".join(missing))

    consent_ts = int(time.time())
    consent_ip = str(getattr(settings, "SIGNZY_CONSENT_IP", "") or "0.0.0.0")
    consent_msg_id = getattr(settings, "SIGNZY_CONSENT_MESSAGE_ID", None)
    if not consent_msg_id:
        # Signzy validates this against whitelisted/registered consent templates.
        raise BureauError("SIGNZY_CONSENT_MESSAGE_ID not configured; cannot trigger bureau check")
    consent_msg_id = str(consent_msg_id)

    phone_num = int(phone) if str(phone).isdigit() else phone

    payload = {
        "phoneNumber": phone_num,
        "pan": pan_number,
        "firstName": first_name,
        "lastName": last_name,
        "dateOfBirth": str(dob),
        "pincode": int(pincode) if str(pincode).isdigit() else pincode,
        "consent": {
            "consentFlag": True,
            "consentTimestamp": consent_ts,
            "consentIpAddress": consent_ip,
            "consentMessageId": consent_msg_id,
        },
    }
    return payload


def run_bureau_check(application):
    """
    Call Signzy Experian bureau API and return dict with decision/score/raw.
    """
    api_url = getattr(settings, "SIGNZY_EXP_API_URL", None) or "https://api-preproduction.signzy.app/api/v3/bureau/experian-bureau-report"
    auth_token = getattr(settings, "SIGNZY_EXP_AUTH_TOKEN", None)
    if not auth_token:
        raise BureauError("SIGNZY_EXP_AUTH_TOKEN not configured")

    payload = build_bureau_payload(application)
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token,
    }
    log_saas_request(
        application=application,
        request_type=SaasRequestLog.RequestType.BUREAU_CHECK,
        payload=payload,
        increment_attempt=True,
    )
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=30)
        logger.info("Bureau response %s %s", resp.status_code, resp.text[:500])
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.BUREAU_CHECK,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
    except Exception as exc:
        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.BUREAU_CHECK,
            error=str(exc),
        )
        raise BureauError(f"Bureau API error: {exc}")

    data = resp.json() if resp.text else {}
    score = None
    raw_score = None
    try:
        raw_score = data.get("data", {}).get("jsonExperianReport", {}).get("SCORE", {})
        score = normalize_bureau_score(raw_score.get("FCIREXScore"))
    except Exception:
        pass

    decision = "DECLINED" if score is not None and score < 500 else "APPROVED"
    return {"decision": decision, "score": score, "raw": data}
