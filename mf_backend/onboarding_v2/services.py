import uuid
from typing import Optional, Tuple

from django.db import transaction

from onboarding_v2.constants import ApplicationStage, LeadStatus
from onboarding_v2.models import IdSequence

try:
    from utility.frs.frs_helper import FrsHelper
except Exception:  # pragma: no cover - optional dependency at import time
    FrsHelper = None


def _next_sequence(name: str) -> int:
    """
    Atomically increment and return the next integer for a named sequence.
    """
    with transaction.atomic():
        seq, _ = IdSequence.objects.select_for_update().get_or_create(name=name, defaults={"last_value": 0})
        seq.last_value += 1
        seq.save(update_fields=["last_value", "modified_at"])
        return seq.last_value


def _alpha_prefix(index: int) -> str:
    """
    Convert a zero-based integer to a 3-letter uppercase prefix.
    0 -> AAA, 1 -> AAB, ..., 25 -> AAZ, 26 -> ABA, ...
    """
    letters = []
    n = index
    for _ in range(3):
        n, rem = divmod(n, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


def generate_customer_id() -> str:
    """
    Generate customer ID: 3 letters + 4 digits. Prefix rolls every 10,000 numbers.
    """
    next_val = _next_sequence("customer")
    prefix_index = (next_val - 1) // 10000
    suffix = (next_val - 1) % 10000 + 1
    prefix = _alpha_prefix(prefix_index)
    return f"{prefix}{suffix:04d}"


LEAD_PREFIX_MAP = {
    "gold": ("GL", "MPAGL"),
    "home": ("HL", "MPAHL"),
    "personal": ("PL", "MPAPL"),
    "business": ("BL", "MPABL"),
    "property": ("LAP", "MPALAP"),
    "health": ("HI", "MPAHI"),
    "motor": ("MI", "MPAMI"),
    "working capital": ("WC", "MPAWC"),
    "overdraft": ("OD", "MPAOD"),
    "credit card": ("CC", "MPACC"),
}


def _resolve_prefixes(
    product_category: Optional[str],
    product_subcategory: Optional[str] = None,
    loan_type: Optional[str] = None,
) -> Tuple[str, str]:
    text = " ".join(filter(None, [product_category, product_subcategory, loan_type])).lower().replace("_", " ")
    for key, (lead_prefix, app_prefix) in LEAD_PREFIX_MAP.items():
        if key in text:
            return lead_prefix, app_prefix
    # Default to gold loan style prefixes
    return "GL", "MPAGL"


def generate_lead_code(product_category: Optional[str], product_subcategory: Optional[str] = None, loan_type: Optional[str] = None) -> str:
    lead_prefix, _ = _resolve_prefixes(product_category, product_subcategory, loan_type)
    seq = _next_sequence(f"lead_{lead_prefix}")
    return f"{lead_prefix}{seq:04d}"


def generate_application_id(product_category: Optional[str], product_subcategory: Optional[str] = None, loan_type: Optional[str] = None) -> str:
    _, app_prefix = _resolve_prefixes(product_category, product_subcategory, loan_type)
    seq = _next_sequence(f"app_{app_prefix}")
    return f"{app_prefix}{seq:04d}"


STAGE_COMPLETION_MAP = {
    ApplicationStage.PAN: 10,
    ApplicationStage.SELFIE: 20,
    ApplicationStage.LENDING_PARTNER_BANK: 15,
    ApplicationStage.LOAN_RANGE_SELECTION: 25,
    ApplicationStage.PRODUCT_SELECTION: 50,
    ApplicationStage.BASIC: 75,
    ApplicationStage.ADDRESS: 100,
}

POST_SCREEN_COMPLETION_MAP = {
    ApplicationStage.SELF_DECLARATION: 5,
    ApplicationStage.DOCUMENTS: 10,
    ApplicationStage.PERSONAL: 25,
    ApplicationStage.ADDRESS_SECONDARY: 35,
    ApplicationStage.GOLD: 60,
    ApplicationStage.LOAN: 75,
    ApplicationStage.BANK: 90,
    ApplicationStage.CUSTOMER_VISIT: 95,
    ApplicationStage.ADDITIONAL: 100,
    ApplicationStage.CHARGES: 100,
    ApplicationStage.WAIVER: 100,
    ApplicationStage.AMOUNT_TRANSFERRED: 100,
    ApplicationStage.GOLD_RECEIVED: 100,
    ApplicationStage.GOLD_SUBMITTED: 100,
    ApplicationStage.CHOOSE_CUSTOMER: 100,
    ApplicationStage.FUND_REFUND: 100,
}


def resolve_pre_screen_completion(stage: str) -> int:
    return STAGE_COMPLETION_MAP.get(stage, 0)


def resolve_post_screen_completion(stage: str) -> int:
    return POST_SCREEN_COMPLETION_MAP.get(stage, 0)


def verify_pan_number(pan_number: str):
    """
    Leverage existing FRS pan verification helper.
    Returns (is_valid, response_dict).
    """
    if not FrsHelper:
        return False, {"status": "error", "message": "FRS helper unavailable"}
    helper = FrsHelper()
    resp = helper.process_pan_verification(pan_number)
    status = resp.get("status")
    pan_status = resp.get("data", {}).get("idStatus") or resp.get("data", {}).get("pan_status")
    is_valid = status == "success" and str(pan_status).upper() == "VALID"
    return is_valid, resp


def sync_lead_status(application, status: Optional[str] = None) -> None:
    """
    Update lead status to APPLICATION_CREATED when an application exists.
    """
    lead = getattr(application, "lead", None)
    if not lead:
        return
    
    # Once an application exists, the lead status should be APPLICATION_CREATED
    if lead.status != LeadStatus.APPLICATION_CREATED:
        lead.status = LeadStatus.APPLICATION_CREATED
        lead.save(update_fields=["status", "modified_at"])
