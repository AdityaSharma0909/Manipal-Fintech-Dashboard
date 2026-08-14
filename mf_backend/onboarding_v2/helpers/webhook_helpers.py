from __future__ import annotations

import json
from typing import Tuple

from onboarding_v2.constants import ApplicationStatus
from onboarding_v2.models import WebhookEvent


def resolve_webhook_source(payload: dict) -> str:
    meta_obj = payload.get("meta")
    source = ""
    if isinstance(meta_obj, dict):
        source = meta_obj.get("source") or ""
    elif isinstance(meta_obj, str) and meta_obj:
        try:
            parsed = json.loads(meta_obj)
            if isinstance(parsed, dict):
                source = parsed.get("source") or ""
        except Exception:
            source = meta_obj
    return payload.get("source") or source


def resolve_webhook_purpose(source: str, status_val: str | None, payload: dict = None) -> str:
    purpose = WebhookEvent.Purpose.UNKNOWN
    source_lower = str(source).lower()
    status_lower = str(status_val or "").lower()
    # Normalize: replace both space and hyphen with underscore
    status_norm = status_lower.replace(" ", "_").replace("-", "_")
    
    # Check status first as it's more specific for lifecycle stage
    if status_norm in [
        "approved",
        "loan_created",
        "declined",
        "agreement_signed",
        "disbursement_ready",
        "disbursed",
        "matured",
        "dropped",
        "disbursement_cancelled",
        "drop_requested",
        "allocation_pending",
        "commercial_processing",
        "deviation_requested",
        "esign_initiated",
        "esign_completed",
        "e_sign_initiated",
        "e_sign_completed",
        "rejected_by_underwriting",
        "approved_by_accounts_for_processing",
        "bt_fund_disbursed",
        "correction_raised_by_underwriting",
        "rectified",
        "rh",
        "d",
    ]:
        purpose = WebhookEvent.Purpose.LOAN_CREATION
    elif status_norm in ["ready_for_loan", "eligible", "not_eligible", "rejected", "correction", "in_progress"]:
        purpose = WebhookEvent.Purpose.PRESCREEN
    elif source_lower == "saas_tech_prescreening":
        purpose = WebhookEvent.Purpose.PRESCREEN
    elif source_lower == "saas_tech_loan_creation":
         purpose = WebhookEvent.Purpose.LOAN_CREATION
    
    if payload and payload.get("transaction_reference_number"):
        purpose = WebhookEvent.Purpose.FUND_REFUND
         
    return purpose


def resolve_prescreen_status(status_val: str | None, remarks: str | None = None) -> Tuple[str | None, bool]:
    status_raw = str(status_val or "")
    status_upper = status_raw.upper()
    status_norm = status_upper.replace(" ", "_")
    status_clean = status_upper.replace("-", " ").replace("_", " ")
    remarks_upper = str(remarks or "").upper()

    eligible_states = {"ELIGIBLE", "READY_FOR_LOAN"}
    if status_upper in eligible_states or status_norm in eligible_states:
        return ApplicationStatus.READY_FOR_LOAN, True
    
    if status_upper in ["NOT ELIGIBLE", "NOT_ELIGIBLE"] or status_norm in ["NOT_ELIGIBLE"]:
        return ApplicationStatus.NOT_ELIGIBLE, False
    
    if status_upper == "CORRECTION" or status_clean == "CORRECTION RAISED BY UNDERWRITING":
        return ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING, False
    
    if status_upper == "REJECTED" or status_clean == "REJECTED BY UNDERWRITING":
        return ApplicationStatus.REJECTED_BY_UNDERWRITING, False
    
    if status_clean == "APPROVED BY ACCOUNTS FOR PROCESSING":
        return ApplicationStatus.APPROVED_BY_ACCOUNTS, False
    
    if status_clean == "BT FUND DISBURSED":
        return ApplicationStatus.BT_FUND_DISBURSED, False
    
    if status_upper == "IN_PROGRESS":
        return ApplicationStatus.IN_PROGRESS, False
    
    if status_clean in ["ESIGN INITIATED", "E SIGN INITIATED", "E-SIGN INITIATED"]:
        return ApplicationStatus.ESIGN_INITIATED, False
        
    if status_clean in ["ESIGN COMPLETED", "E SIGN COMPLETED", "E-SIGN COMPLETED"]:
        return ApplicationStatus.ESIGN_COMPLETED, False

    if status_upper == "RH":
        return ApplicationStatus.APPROVED_BY_RH, False

    return None, False


def resolve_loan_creation_status(status_val: str | None, remarks: str | None = None) -> str | None:
    status_norm_upper = (status_val or "").replace("_", " ").upper()
    status_clean = status_norm_upper.replace("-", " ")
    remarks_upper = str(remarks or "").upper()

    loan_status_map = {
        "APPROVED": ApplicationStatus.APPROVED,
        "AGREEMENT SIGNED": ApplicationStatus.AGREEMENT_SIGNED,
        "DISBURSEMENT READY": ApplicationStatus.DISBURSEMENT_READY,
        "DISBURSED": ApplicationStatus.DISBURSED,
        "MATURED": ApplicationStatus.MATURED,
        "DROPPED": ApplicationStatus.DROPPED,
        "DISBURSEMENT CANCELLED": ApplicationStatus.DISBURSEMENT_CANCELLED,
        "DROP REQUESTED": ApplicationStatus.DROP_REQUESTED,
        "ALLOCATION PENDING": ApplicationStatus.ALLOCATION_PENDING,
        "COMMERCIAL PROCESSING": ApplicationStatus.COMMERCIAL_PROCESSING,
        "DEVIATION REQUESTED": ApplicationStatus.DEVIATION_REQUESTED,
        "REJECTED": ApplicationStatus.REJECTED_BY_UNDERWRITING,
        "REJECTED BY UNDERWRITING": ApplicationStatus.REJECTED_BY_UNDERWRITING,
        "REJECTED_BY_UNDERWRITING": ApplicationStatus.REJECTED_BY_UNDERWRITING,
        "APPROVED BY ACCOUNTS FOR PROCESSING": ApplicationStatus.APPROVED_BY_ACCOUNTS,
        "BT FUND DISBURSED": ApplicationStatus.BT_FUND_DISBURSED,
        "CORRECTION RAISED BY UNDERWRITING": ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING,
        "CORRECTION_RAISED_BY_UNDERWRITING": ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING,
        "ESIGN INITIATED": ApplicationStatus.ESIGN_INITIATED,
        "ESIGN_INITIATED": ApplicationStatus.ESIGN_INITIATED,
        "E-SIGN INITIATED": ApplicationStatus.ESIGN_INITIATED,
        "ESIGN COMPLETED": ApplicationStatus.ESIGN_COMPLETED,
        "ESIGN_COMPLETED": ApplicationStatus.ESIGN_COMPLETED,
        "E-SIGN COMPLETED": ApplicationStatus.ESIGN_COMPLETED,
        "RH": ApplicationStatus.APPROVED_BY_RH,
    }
    
    status_match = loan_status_map.get(status_norm_upper)
    if status_match:
        return status_match
    
    status_clean_match = loan_status_map.get(status_clean)
    if status_clean_match:
        return status_clean_match

    # if "REJECTED BY UNDERWRITING" in remarks_upper:
    #     return ApplicationStatus.REJECTED_BY_UNDERWRITING
    
    # if "CORRECTION RAISED BY UNDERWRITING" in remarks_upper:
    #     return ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING
    
    # if "E-SIGN INITIATED" in remarks_upper:
    #     return ApplicationStatus.ESIGN_INITIATED
    
    # if "E-SIGN COMPLETED" in remarks_upper:
    #     return ApplicationStatus.ESIGN_COMPLETED
    
    return None
