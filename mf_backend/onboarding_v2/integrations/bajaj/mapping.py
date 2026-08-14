
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime

from onboarding_v2.models import LeadV2
from .settings import BajajCrmTypeConfig, BajajEnvConfig

logger = logging.getLogger(__name__)


def _split_name(full_name: str) -> tuple[str, str]:
    parts = [p for p in (full_name or "").strip().split() if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


@dataclass(frozen=True)
class BajajLeadMappingResult:
    bajaj_data: Dict[str, Any]
    header_source: str


def _crm_type_from_lead(lead: LeadV2) -> str:
    crm_type = str(getattr(lead, "crm_type", "") or "").strip().upper()
    if crm_type:
        return crm_type
    meta = getattr(lead, "metadata", {}) or {}
    if not isinstance(meta, dict):
        return ""
    return str(meta.get("crm_type") or "").strip().upper()


def build_bajaj_create_lead_data(*, lead: LeadV2, config: BajajEnvConfig) -> BajajLeadMappingResult:
    """Build the plain Bajaj lead create request payload from LeadV2."""
    meta = getattr(lead, "metadata", {}) or {}
    crm_type_config: BajajCrmTypeConfig = config.config_for_crm_type(_crm_type_from_lead(lead))
    customer_name = getattr(lead, "customer_name", "") or meta.get("customer_name", "")
    first_name, last_name = _split_name(customer_name)

    # Format lead generation datetime as YYYY-MM-DD HH:MM:SS
    lead_gen_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get loan amount from lead.amount
    loan_amount = str(getattr(lead, "amount", "") or meta.get("amount", ""))

    payload = {
        "lead_generation_datetime": lead_gen_datetime,
        "mobile": str(getattr(lead, "contact_number", "") or ""),
        "lead_required_amount": loan_amount,
        "total_gold_weight": "",
        "interest_repayment_frequency": "",
        "tenure": "",
        "interest_repayment": "",
        "rate_of_interest": "",
        "disposition_time": "",
        "first_name": first_name,
        "last_name": last_name,
        "tokenno": "",
        "product": crm_type_config.product,
        "lead_type": config.lead_type,
        "emp_id": "",
        "disposition_type": "",
        "lead_source": crm_type_config.lead_source,
        "lead_origin": crm_type_config.lead_origin,
        "employement_type": "",
        "employement_subtype": "",
        "journey_name": config.journey_name,
        "competitor_name": "",
        "competitor_loan_amount": "",
        "final_loan_amount": "",
        "lead_remark": "",
        "lead_channel": crm_type_config.lead_channel,
        "lead_status": "",
        "emp_role": "",
        "emp_adid": "",
        "emp_name": "",
        "alt_mobile": "",
        "branch_id": "",
        "followup": str(config.follow_up).lower(),
        "eventCode": "",
        "src": crm_type_config.src,
        "internal_src": config.internal_src,
        "pincode": str(getattr(lead, "pincode", "") or meta.get("pincode", "") or ""),
        "dsc_code": config.dsc_code,
        "sub_code": config.sub_code,
        "subsub_code": "",
        "referral_id": config.referral_id,
        "referral_business": "",
        "referral_partner": crm_type_config.referral_partner,
        "lead_details_3in1": {
            "lead_id": None,
            "interest_repayment_frequency": "",
            "interest_repayment": "",
            "date_of_birth": "",
            "pan": "",
            "branch_name": "",
            "branck_address": "",
            "gold_loan_officer_name": "",
            "gold_loan_officer_mobile": "",
            "preferred_payment_mode": "",
            "cash_disbursement_required": "",
            "bank_transfer_required": "",
            "cash_and_bank_transfer_required": "",
            "loan_required_in_cash": "",
            "loan_required_in_bank": "",
            "bank_account_no": "",
            "ifsc": "",
            "bank_name": "",
            "bank_branch_name": "",
            "kyc_completion_status": "",
            "kyc_method_used": "",
            "kyc_name": "",
            "kyc_address": "",
            "kyc_dob": "",
            "kyc_city": "",
            "kyc_state": "",
            "kyc_pincode": "",
            "kyc_photo": "",
            "total_loan_amount_bt": "",
            "rate_of_interest_bt": "",
            "gold_weight_bt": "",
            "name_of_loan_provider_bt": "",
            "gdr_upload_status_bt": "",
            "gdr_image_bt": "",
            "loan_amount_with_bfl_bt": "",
            "monthly_interest_with_bfl_bt": "",
            "potential_annual_interest_savings_bt": "",
            "extra_amount_for_same_gold_weight_bt": "",
            "eligibility_for_reward_for_completing_journey_bt": "",
            "eligibility_for_reward_for_completing_journey_additional_info": "",
            "share_jewellery_details_completion": "",
            "ornament_details": "",
            "customer_is_rsl_rpl_reject": "",
            "lead_req_date_time": "",
            "dynamicinfo": "",
            "gl_loan_existing": "",
            "docDtl": "",
            "docName": "",
            "docType": "",
            "docCode": "",
            "account_type": "",
        },
    }

    return BajajLeadMappingResult(
        bajaj_data=payload,
        header_source=crm_type_config.header_source,
    )
