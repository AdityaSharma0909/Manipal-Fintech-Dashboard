from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple
from uuid import UUID

from onboarding_v2.models import BankBranch, LeadV2, PincodeMaster

from .settings import AxisEnvConfig


def _split_name(full_name: str) -> Tuple[str, str, str]:
    parts = [p for p in (full_name or "").strip().split() if p]
    if not parts:
        return ("", ".", "")
    if len(parts) == 1:
        return (parts[0], ".", ".")
    if len(parts) == 2:
        return (parts[0], ".", parts[1])
    return (parts[0], " ".join(parts[1:-1]) or ".", parts[-1])


def _meta(lead: LeadV2) -> Dict[str, Any]:
    m = getattr(lead, "metadata", None)
    return m if isinstance(m, dict) else {}


def _resolve_branch_sol_id(lead: LeadV2, meta: Dict[str, Any]) -> str:
    # Lead creation may provide the exact SOL ID selected by the caller. Prefer
    # it over all lookup-based resolution.
    explicit_sol_id = meta.get("sol_id") or meta.get("solId") or meta.get("branch_sol_id")
    if explicit_sol_id and str(explicit_sol_id).strip():
        return str(explicit_sol_id).strip()

    branch_id = meta.get("bank_branch_id") or meta.get("branch_id") or meta.get("branchId")

    bank_name = getattr(lead, "bank", None) or meta.get("bank") or meta.get("bank_name") or meta.get("bankName")
    branch_name = (
        getattr(lead, "bank_branch", None)
        or meta.get("bank_branch")
        or meta.get("branch_name")
        or meta.get("branchName")
    )
    qs = BankBranch.objects.exclude(sol_id__isnull=True).exclude(sol_id="")

    if branch_id:
        try:
            branch_uuid = UUID(str(branch_id))
        except (TypeError, ValueError):
            branch_uuid = None
        if branch_uuid:
            branch = qs.filter(id=branch_uuid).first()
            if branch and branch.sol_id:
                return branch.sol_id.strip()

    if not branch_name:
        return ""

    # Match the same records exposed by pincode-branch-lookup: the lead's pincode
    # identifies a district, and the selected bank narrows the available branches.
    # This prevents a same-named branch belonging to another bank/district from
    # supplying the SOL ID.
    matches = qs.filter(branch_name__iexact=str(branch_name).strip())
    if bank_name:
        matches = matches.filter(bank_name__iexact=str(bank_name).strip())

    pincode = getattr(lead, "pincode", None) or meta.get("pinCode") or meta.get("pincode")
    if pincode:
        district = (
            PincodeMaster.objects.filter(pincode=str(pincode).strip())
            .values_list("district", flat=True)
            .first()
        )
        if district:
            matches = matches.filter(district__iexact=str(district).strip())

    branch = matches.first()
    return branch.sol_id.strip() if branch and branch.sol_id else ""


@dataclass(frozen=True)
class AxisLeadMappingResult:
    axis_data: Dict[str, Any]


def build_axis_create_lead_data(*, lead: LeadV2, config: AxisEnvConfig) -> AxisLeadMappingResult:
    """
    Build the inner Axis `Data` object for /create-lead (token is injected by client).
    Most fields are sourced from lead.metadata because LeadV2 itself is minimal.
    """
    meta = _meta(lead)

    first, middle, last = _split_name(getattr(lead, "customer_name", "") or meta.get("customer_name", ""))

    # Best-effort field extraction. Core team can enrich metadata upstream.
    email = getattr(lead, "email_address", None) or meta.get("email") or meta.get("email_address") or ""
    dob = meta.get("dateOfBirth") or meta.get("dob") or meta.get("date_of_birth") or ""
    pan = meta.get("panNumber") or meta.get("pan") or meta.get("pan_number") or ""

    address1 = meta.get("address1") or meta.get("address_line1") or meta.get("address_line") or ""
    address2 = meta.get("address2") or meta.get("address_line2") or ""
    address3 = meta.get("address3") or meta.get("address_line3") or ""

    pincode = getattr(lead, "pincode", None) or meta.get("pinCode") or meta.get("pincode") or ""
    city = meta.get("city") or ""
    state = meta.get("state") or ""

    alt_mobile = meta.get("alternateMobile") or meta.get("alternate_mobile") or ""
    phone = meta.get("phone") or ""

    loan_amount_lakhs = meta.get("loanAmountInLakhs") or meta.get("loan_amount_in_lakhs") or ""
    branch_sol_id = _resolve_branch_sol_id(lead, meta)

    # Axis expects strings/ints depending on field; keep as-is but ensure not None.
    axis_data: Dict[str, Any] = {
        "customerType": int(meta.get("customerType") or config.default_customer_type),
        "customerId": str(meta.get("customerId") or meta.get("customer_id") or ""),
        "comments": str(meta.get("comments") or ""),
        "alternateMobile": str(alt_mobile),
        "otherSource": str(meta.get("otherSource") or ""),
        "address1": str(address1),
        "address2": str(address2),
        "address3": str(address3),
        "pinCode": str(pincode),
        "city": str(city),
        "state": str(state),
        "dateOfBirth": str(dob),
        "panNumber": str(pan),
        "email": str(email),
        "salutationId": int(meta.get("salutationId") or config.default_salutation_id),
        "firstName": str(first),
        "middleName": str(middle),
        "lastName": str(last),
        "layout": int(meta.get("layout") or config.default_layout),
        "createdBySource": int(meta.get("createdBySource") or config.default_created_by_source),
        "leadSource": int(meta.get("leadSource") or config.default_lead_source),
        "subSource": str(meta.get("subSource") or config.default_sub_source),
        "leadOwnerId": int(meta.get("leadOwnerId") or config.default_lead_owner_id),
        "mobilePhone": str(getattr(lead, "contact_number", None) or meta.get("mobilePhone") or ""),
        "phone": str(phone),
        "product": int(meta.get("product") or config.default_product),
        "subProduct": int(meta.get("subProduct") or config.default_sub_product),
        "leadPriority": int(meta.get("leadPriority") or config.default_lead_priority),
        "statusCode": int(meta.get("statusCode") or config.default_status_code),
        "branch": str(branch_sol_id or meta.get("branch") or config.default_branch),
        "followUpDate1": str(meta.get("followUpDate1") or ""),
        "followUpReason": str(meta.get("followUpReason") or ""),
        "preferredDateAndTime": str(meta.get("preferredDateAndTime") or ""),
        "initialRejectedReason": meta.get("initialRejectedReason") or "",
        "deferredDate": str(meta.get("deferredDate") or ""),
        "deferredReason": str(meta.get("deferredReason") or ""),
        "userWorkedOnLead": str(meta.get("userWorkedOnLead") or ""),
        "leadConvertor": meta.get("leadConvertor") or "",
        "countryOfStudy": str(meta.get("countryOfStudy") or ""),
        "instituteName": str(meta.get("instituteName") or ""),
        "courseType": str(meta.get("courseType") or ""),
        "qualifyingTest": str(meta.get("qualifyingTest") or ""),
        "testScore": meta.get("testScore") or "",
        "loanAmountInLakhs": str(loan_amount_lakhs),
        "industry": meta.get("industry") or "",
        "designation": meta.get("designation") or "",
        "contactPerson": meta.get("contactPerson") or "",
        "estimatedAnnualRevenue": meta.get("estimatedAnnualRevenue") or "",
        "leadValue": meta.get("leadValue") or "",
        "customerLocalityCheck": meta.get("customerLocalityCheck") or "",
        "customerOwns4Wheeler": meta.get("customerOwns4Wheeler") or "",
        "customerOwns2Wheeler": meta.get("customerOwns2Wheeler") or "",
        "customerMonthlyIncome": meta.get("customerMonthlyIncome") or "",
        "customerWorkingLevel": meta.get("customerWorkingLevel") or "",
        "customerDesignation": meta.get("customerDesignation") or "",
        "customerSegment": meta.get("customerSegment") or "",
        "monthAnnualIncome": meta.get("monthAnnualIncome") or "",
        "jobExperience": meta.get("jobExperience") or "",
        "age": meta.get("age") or "",
        "retirementAge": meta.get("retirementAge") or "",
        "loanTenureInYears": meta.get("loanTenureInYears") or "",
        "isCarVariantFinal": meta.get("isCarVariantFinal") or "",
    }

    # Axis samples use empty string rather than nulls.
    for k, v in list(axis_data.items()):
        if v is None:
            axis_data[k] = ""

    return AxisLeadMappingResult(axis_data=axis_data)
