from __future__ import annotations

from decimal import Decimal, InvalidOperation

from onboarding_v2.constants import ApplicationStage, ApplicationStatus, LeadType, TransactionStatus
from onboarding_v2.models import ApplicationStageSnapshot


def _to_decimal(value) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    if isinstance(value, str):
        value = value.replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _status_key(value) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _get_loan_payload(application, current_payload: dict) -> dict:
    loan_payload = current_payload.get("loan") if isinstance(current_payload, dict) else {}
    if isinstance(loan_payload, dict) and loan_payload:
        return loan_payload

    try:
        snapshot = application.stage_snapshots.get(stage=ApplicationStage.LOAN)
    except (ApplicationStageSnapshot.DoesNotExist, AttributeError):
        return {}

    return snapshot.payload if isinstance(snapshot.payload, dict) else {}


def get_fund_refund_sanctioned_amount(application, current_payload: dict | None = None) -> Decimal:
    current_payload = current_payload if isinstance(current_payload, dict) else {}
    sanctioned_amount = _to_decimal(getattr(application.lead, "amount", None))

    if application.loan_type == LeadType.BALANCE_TRANSFER:
        loan_payload = _get_loan_payload(application, current_payload)
        bt_amount = loan_payload.get("requested_amount") or loan_payload.get("required_bt_amount")
        if bt_amount not in (None, ""):
            sanctioned_amount = _to_decimal(bt_amount)

    return sanctioned_amount


def calculate_fund_refund_amounts(application) -> dict:
    current_payload = application.stage_payload if isinstance(application.stage_payload, dict) else {}
    refunds = current_payload.get("fund_refund", [])
    if not isinstance(refunds, list):
        refunds = []
    
    # If no refunds in stage_payload, check the stage snapshot
    if not refunds:
        try:
            from onboarding_v2.constants import ApplicationStage
            snapshot = application.stage_snapshots.get(stage=ApplicationStage.FUND_REFUND)
            if isinstance(snapshot.payload, list):
                refunds = snapshot.payload
        except Exception:
            pass

    sanctioned_amount = get_fund_refund_sanctioned_amount(application, current_payload)
    deposited_amount = Decimal("0")
    not_verified_amount = Decimal("0")

    for refund in refunds:
        if not isinstance(refund, dict):
            continue

        amount = _to_decimal(refund.get("amount"))
        status = _status_key(refund.get("status"))

        if status == TransactionStatus.VERIFIED:
            deposited_amount += amount
        elif status in {TransactionStatus.UNVERIFIED, "NOT_VERIFIED"}:
            not_verified_amount += amount

    return {
        "sanctioned_amount": sanctioned_amount,
        "deposited_amount": deposited_amount,
        "not_verified_amount": not_verified_amount,
        # "pending_amount": sanctioned_amount - (deposited_amount + not_verified_amount),
        "pending_amount": sanctioned_amount - deposited_amount,
        
    }


BT_RETURN_COMPLETED_STATUS_MAP = {
    ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER: ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER_BT_RETURN_COMPLETED,
    ApplicationStatus.GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER: ApplicationStatus.GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER_BT_RETURN_COMPLETED,
    ApplicationStatus.GOLD_NOT_SUBMITTED_TO_PARTNER_BANK: ApplicationStatus.GOLD_NOT_SUBMITTED_TO_PARTNER_BANK_BT_RETURN_COMPLETED,
    ApplicationStatus.LOAN_TRANSFERRED: ApplicationStatus.LOAN_TRANSFERRED_BT_RETURN_COMPLETED,
    ApplicationStatus.LOAN_STATUS_UPDATED: ApplicationStatus.LOAN_STATUS_UPDATED_BT_RETURN_COMPLETED,
}


def update_bt_return_completed_status(application, previous_status: str | None) -> bool:
    """
    Mark the BT return branch completed when submitted refund amount covers the sanctioned amount.
    """
    completed_status = BT_RETURN_COMPLETED_STATUS_MAP.get(previous_status)
    if not completed_status:
        return False

    current_payload = application.stage_payload if isinstance(application.stage_payload, dict) else {}
    refunds = current_payload.get("fund_refund", [])
    if not isinstance(refunds, list):
        refunds = []

    verified_amount = Decimal("0")
    for refund in refunds:
        if not isinstance(refund, dict):
            continue
        status = _status_key(refund.get("status"))
        if status == TransactionStatus.VERIFIED:
            verified_amount += _to_decimal(refund.get("amount"))

    sanctioned_amount = get_fund_refund_sanctioned_amount(application, current_payload)
    if sanctioned_amount <= 0 or verified_amount != sanctioned_amount:
        return False

    application.status = completed_status
    application.save(update_fields=["status", "modified_at"])
    return True
