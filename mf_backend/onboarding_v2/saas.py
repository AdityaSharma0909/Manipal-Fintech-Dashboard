from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from django.conf import settings
from django.utils import timezone

from onboarding_v2.constants import (
    ApplicationStage,
    DocumentType,
    Occupation,
    IncomeSource,
    LoanPurpose,
    Category,
    Religion,
    MaritalStatus,
    LeadType,
)
from onboarding_v2.loggers import log_saas_request
from onboarding_v2.models import ApplicationDocument, ApplicationV2, JewelleryItem, Packet, SaasRequestLog, RoiConfiguration
from onboarding_v2.serializers import LeadV2Serializer
from onboarding_v2.serializers.state import ApplicationStateSerializer
from onboarding_v2.storage import generate_presigned_get

import json
from decimal import Decimal

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 120
SAAS_AGREEMENT_ID = "2605"
SAAS_DEFAULT_BUREAU_NAME = "experian"
ALLOWED_PURITY_VALUES = {18, 19, 20, 21, 22, 23, 24}
SAAS_STATE_MAP = {
    "JAMMU AND KASHMIR": "jammu_kashmir",
    "JAMMU & KASHMIR": "jammu_kashmir",
    "HIMACHAL PRADESH": "himachal_pradesh",
    "PUNJAB": "punjab",
    "CHANDIGARH": "chandigarh",
    "UTTARANCHAL": "uttaranchal",
    "UTTARAKHAND": "uttaranchal",
    "HARYANA": "haryana",
    "DELHI": "delhi",
    "RAJASTHAN": "rajasthan",
    "UTTAR PRADESH": "uttar_pradesh",
    "BIHAR": "bihar",
    "SIKKIM": "sikkim",
    "ARUNACHAL PRADESH": "arunachal_pradesh",
    "NAGALAND": "nagaland",
    "MANIPUR": "manipur",
    "MIZORAM": "mizoram",
    "TRIPURA": "tripura",
    "MEGHALAYA": "meghalaya",
    "ASSAM": "assam",
    "WEST BENGAL": "west_bengal",
    "JHARKHAND": "jharkhand",
    "ODISHA": "orissa",
    "ORISSA": "orissa",
    "CHHATTISGARH": "chhattisgarh",
    "MADHYA PRADESH": "madhya_pradesh",
    "GUJARAT": "gujarat",
    "DAMAN AND DIU": "daman_diu",
    "DAMAN & DIU": "daman_diu",
    "DADRA AND NAGAR HAVELI": "dadra_nagar_haveli",
    "THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "dadra_nagar_haveli",
    "MAHARASHTRA": "maharashtra",
    "ANDHRA PRADESH": "andhra_pradesh",
    "KARNATAKA": "karnataka",
    "GOA": "goa",
    "LAKSHADWEEP": "lakshadweep",
    "KERALA": "kerala",
    "TAMIL NADU": "tamil_nadu",
    "PUDUCHERRY": "pondicherry",
    "PONDICHERRY": "pondicherry",
    "ANDAMAN AND NICOBAR ISLANDS": "andaman_nicobar_islands",
    "ANDAMAN & NICOBAR ISLANDS": "andaman_nicobar_islands",
    "TELANGANA": "telangana",
    "LADAKH": "jammu_kashmir",
    "NAN": "",
}
STATE_CODE_MAP = {
    "AN": "andaman_nicobar_islands",
    "AP": "andhra_pradesh",
    "AR": "arunachal_pradesh",
    "AS": "assam",
    "BR": "bihar",
    "CG": "chhattisgarh",
    "CH": "chandigarh",
    "DD": "daman_diu",
    "DL": "delhi",
    "DN": "dadra_nagar_haveli",
    "GA": "goa",
    "GJ": "gujarat",
    "HR": "haryana",
    "HP": "himachal_pradesh",
    "JH": "jharkhand",
    "JK": "jammu_kashmir",
    "KA": "karnataka",
    "KL": "kerala",
    "LA": "jammu_kashmir",
    "LD": "lakshadweep",
    "MH": "maharashtra",
    "ML": "meghalaya",
    "MN": "manipur",
    "MP": "madhya_pradesh",
    "MZ": "mizoram",
    "NL": "nagaland",
    "OR": "orissa",
    "PB": "punjab",
    "PY": "pondicherry",
    "RJ": "rajasthan",
    "SK": "sikkim",
    "TN": "tamil_nadu",
    "TR": "tripura",
    "TS": "telangana",
    "UK": "uttaranchal",
    "UP": "uttar_pradesh",
    "WB": "west_bengal",
}
GEO_LOCATION_MAP = {
    "andaman_nicobar_islands": "south",
    "andhra_pradesh": "south",
    "arunachal_pradesh": "east",
    "assam": "east",
    "bihar": "north",
    "chandigarh": "north",
    "dadra_nagar_haveli": "west",
    "daman_diu": "west",
    "delhi": "north",
    "goa": "west",
    "gujarat": "west",
    "haryana": "north",
    "himachal_pradesh": "north",
    "jammu_kashmir": "north",
    "jharkhand": "north",
    "karnataka": "south",
    "kerala": "south",
    "lakshadweep": "south",
    "maharashtra": "west",
    "manipur": "east",
    "meghalaya": "east",
    "mizoram": "east",
    "nagaland": "east",
    "orissa": "east",
    "pondicherry": "south",
    "punjab": "north",
    "rajasthan": "west",
    "sikkim": "east",
    "tamil_nadu": "south",
    "telangana": "south",
    "tripura": "east",
    "uttar_pradesh": "north",
    "uttaranchal": "north",
    "west_bengal": "east",
}

def _to_number(value: Any, default: Union[float, int] = 0) -> Union[float, int]:
    """
    Convert string/Decimal-like numeric values to float/int where possible.
    Returns default if value is falsy/empty.
    """
    if value in (None, ""):
        return default
    try:
        # Preserve int if it's an integer value
        fval = float(value)
        if fval.is_integer():
            return int(fval)
        return fval
    except Exception:
        return default


def _coerce_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _calculate_age(dob_value: Any) -> Optional[int]:
    dob = _coerce_date(dob_value)
    if not dob:
        return None
    today = timezone.now().date()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years if years >= 0 else None


def _safe_json(resp: requests.Response) -> Union[Dict[str, Any], str]:
    try:
        return resp.json()
    except Exception:
        return resp.text


def _presign_get(url: str, doc_id: Optional[int] = None) -> str:
    try:
        presigned = generate_presigned_get(file_url=url).get("get_url")
        return presigned or url
    except Exception:
        if doc_id is not None:
            logger.warning("presign get failed for doc %s: %s", doc_id, url)
        return url


def _doc_url(doc: ApplicationDocument) -> Optional[str]:
    if doc.file:
        return doc.file.url
    return doc.file_url


def _first_document_url(
    documents: List[ApplicationDocument],
    doc_type: str,
    *,
    subtype_contains: Optional[str] = None,
) -> Optional[str]:
    doc = _first_document(documents, doc_type, subtype_contains=subtype_contains)
    if not doc:
        return None
    url = _doc_url(doc)
    if not url:
        return None
    return _presign_get(url, doc.id)


def _doc_metadata(doc: Optional[ApplicationDocument]) -> Dict[str, Any]:
    return (doc.metadata or {}) if doc else {}


def _map_state_for_saas(state: Optional[str]) -> str:
    if not state:
        return ""
    raw = str(state).strip().upper()
    if raw in SAAS_STATE_MAP:
        return SAAS_STATE_MAP[raw]
    return raw.lower().replace(" ", "_")


def _map_geo_location(state: Optional[str]) -> str:
    if not state:
        return ""
    raw = str(state).strip().upper()
    if raw in STATE_CODE_MAP:
        slug = STATE_CODE_MAP[raw]
    elif raw in SAAS_STATE_MAP:
        slug = SAAS_STATE_MAP[raw]
    else:
        slug = raw.lower().replace(" ", "_")
    return GEO_LOCATION_MAP.get(slug, "")


def _parse_purity(value: Any) -> int:
    """
    Extract numeric carat value (allowed: 18, 19, 20, 21, 22, 24).
    Defaults to 22 if not recognized.
    """
    if value in (None, ""):
        return 22
    s = str(value).upper()
    digits = "".join(ch for ch in s if ch.isdigit())
    try:
        num = int(digits)
        return num if num in ALLOWED_PURITY_VALUES else 22
    except Exception:
        return 22


def _get_adjusted_purity(actual_purity: int) -> int:
    """
    Map actual fineness (carat) to adjusted fineness based on rules:
    18K, 19K -> 18K
    20K, 21K, 22K -> 22K
    23K, 24K -> 24K
    """
    if actual_purity in (18, 19):
        return 18
    elif actual_purity in (20, 21, 22):
        return 22
    elif actual_purity in (23, 24):
        return 24
    return actual_purity


def _get_roi_bank_value(lending_partner: Optional[str]) -> str:
    """
    Standardize the bank name to match RoiConfigurationBank choices (e.g. AXIS_BANK).
    """
    if not lending_partner:
        return "AXIS_BANK"
    lp = lending_partner.upper().replace(" ", "_").replace("-", "_")
    if "AXIS" in lp:
        return "AXIS_BANK"
    return lp


def _map_customer_category(
    value: Optional[str],
    income_source: Optional[str],
    primary_borrower_type: Optional[str],
    profession: Optional[str] = None,
) -> str:
    """
    SAAS expects lower-case enum values.
    Valid: salaried, self_employed_professional, self_employed, others.
    Derive from profession/income_source/category/primary_borrower_type.
    """
    candidates = [profession, income_source, value, primary_borrower_type]
    for v in candidates:
        if not v:
            continue
        low = str(v).lower()
        if "prof" in low:
            return "self_employed_professional"
        if low.startswith("sal"):
            return "salaried"
        if "bus" in low or "self" in low:
            return "self_employed"
    return "others"


def _map_sub_category(value: Optional[str]) -> str:
    low = (value or "").lower().strip()
    if low in {"fresh", "f"}:
        return "fresh"
    if low in {"bt", "balance_transfer", "balance transfer"}:
        return "bt"
    if low in {"topup", "top_up", "top up"}:
        return "top_up"
    return ""


def _map_gender(value: Optional[str]) -> str:
    low = (value or "").lower()
    if low in {"male", "m"}:
        return "m"
    if low in {"female", "f"}:
        return "f"
    if low in {"other", "others", "o"}:
        return "o"
    return "o"


def _choice_label(value: Optional[str], choices_cls) -> str:
    if not value:
        return ""
    try:
        return choices_cls(value).label
    except Exception:
        return str(value)


JEWELLERY_CODE_MAP = {
    "NOSE_RING": ("NR", "Nose Ring"),
    "RING": ("RN", "Ring"),
    "WAIST_CHAIN": ("WC", "Waist Chain"),
    "ANKLET": ("AK", "Anklet"),
    "BALLY_CHAIN": ("BC", "Bally Chain"),
    "BANGLES": ("BN", "Bangles"),
    "BANGLE": ("BN", "Bangles"),
    "BRACELET": ("BR", "Bracelet"),
    "CHAIN": ("CH", "Chain"),
    "CHAIN_WITH_LOCKET": ("CL", "Chain With Locket"),
    "EAR_RING": ("ER", "Earings"),
    "FOREHEAD_ORNAMENT": ("FO", "Forehead Ornament"),
    "MANG_TIKKA": ("FO", "Forehead Ornament"),
    "FINGER_RING": ("FR", "Finger Ring"),
    "GEMSTONE": ("GS", "Gemstone"),
    "HAIR_ORNAMENT": ("HO", "Hair Ornaments"),
    "LONG_CHAIN": ("LC", "Long Chain"),
    "MENS_KADA": ("MK", "Mens Kada"),
    "NECKLACE": ("NL", "Necklace"),
    "PENDANT": ("PE", "Pendant"),
}

JEWELLERY_CODE_ID_MAP: Dict[str, int] = {
    "NR": 1030,
    "RN": 1031,
    "WC": 1032,
    "AK": 1015,
    "BC": 1016,
    "BN": 1017,
    "BR": 1018,
    "CH": 1019,
    "CL": 1020,
    "ER": 1021,
    "FO": 1022,
    "FR": 1023,
    "GS": 1024,
    "HO": 1025,
    "LC": 1026,
    "MK": 1027,
    "NL": 1028,
    "PE": 1029,
}


def _resolve_jewellery_meta(raw_type: Optional[str]) -> Tuple[str, str, Optional[int]]:
    if not raw_type:
        return "UN", "", None
    key = str(raw_type).strip().upper().replace(" ", "_")
    code, name = JEWELLERY_CODE_MAP.get(key, (key[:2] or "UN", raw_type))
    saas_id = JEWELLERY_CODE_ID_MAP.get(code)
    return code, name, saas_id

# Backward compatibility
def _resolve_jewellery_code_and_name(raw_type: Optional[str]) -> Tuple[str, str]:
    code, name, _ = _resolve_jewellery_meta(raw_type)
    return code, name


def _format_jewellery_url(url: str, code: str, side: str, index: int) -> str:
    """
    Reformat the URL to use SAAS-required filename convention (e.g., BN_FRONT_1.jpg).
    We only rewrite the last path segment to include code/side/index; base path is preserved.
    """
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        path_parts = parsed.path.rsplit("/", 1)
        ext = ""
        if "." in path_parts[-1]:
            ext = "." + path_parts[-1].split(".")[-1]
        new_name = f"{code}_{side}_{index}{ext or '.jpg'}"
        new_path = "/".join([path_parts[0], new_name]) if len(path_parts) == 2 else new_name
        return urlunparse(parsed._replace(path=new_path))
    except Exception:
        return url


def _format_jewellery_upload_name(original_name: str, code: str, side: str, index: int) -> str:
    ext = ""
    if original_name and "." in original_name:
        ext = "." + original_name.split(".")[-1]
    suffix = f"_{index}" if index > 1 else ""
    return f"{code}_{side}{suffix}{ext or '.jpg'}"


def _append_jewellery_url(
    urls: List[str],
    code_side_counts: Dict[Tuple[str, str], int],
    code: str,
    side: str,
    url: Optional[str],
) -> None:
    if not url:
        return
    code_side_counts[(code, side)] = code_side_counts.get((code, side), 0) + 1
    idx = code_side_counts[(code, side)]
    urls.append(_format_jewellery_url(url, code, side, idx))


def _build_appraiser_eval(
    packet: Packet,
    item: JewelleryItem,
    label: str,
    saas_jewellery_id: Optional[int],
    fallback_packet: Optional[Packet] = None,
) -> Dict[str, Any]:
    appraiser_id = getattr(packet, "appraiser_id", "") or ""
    appraiser_name = getattr(packet, "appraiser_name", "") or ""
    if fallback_packet and (not appraiser_id or not appraiser_name):
        appraiser_id = appraiser_id or getattr(fallback_packet, "appraiser_id", "") or ""
        appraiser_name = appraiser_name or getattr(fallback_packet, "appraiser_name", "") or ""
    return {
        "appraiserId": appraiser_id,
        "appraiserName": appraiser_name,
        "jewelleryId": saas_jewellery_id if saas_jewellery_id is not None else str(item.id),
        "jewelleryName": label or item.type_of_jewellery or "",
        "typeOfJewellery": label or item.type_of_jewellery or "",
        "jewelleryCount": _to_number(item.number_of_articles) or 0,
        "actualPurityGrade": _parse_purity(item.purity),
        "actualGoldRateConsidered": _to_number(item.actual_gold_rate),
        "adjustedGoldRateConsidered": _to_number(item.actual_gold_rate),
        "grossWeightOfJewellery": _to_number(item.gross_weight),
        "impurityWeightForDeduction": _to_number(item.impurity_deducted),
        "grossValueOfJewellery": _to_number(item.gross_value),
        "netWeightOfJewellery": _to_number(item.net_weight),
        "netValueOfJewellery": _to_number(item.net_value),
        "netAdjustedWeightOfJewellery": _to_number(item.net_adjusted_weight),
        "netAdjustedValueOfJewellery": _to_number(item.net_adjusted_value),
        "stoneWeight": _to_number(item.stone_weight),
    }


def _build_jewellery_detail(
    item: JewelleryItem,
    label: str,
    saas_jewellery_id: Optional[int],
    appraiser_evals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    actual_purity = _parse_purity(item.purity)
    adjusted_purity = _get_adjusted_purity(actual_purity)
    return {
        "typeOfJewelleryOrnament": label or item.type_of_jewellery or "",
        "unitsNumberOfOrnamentType": _to_number(item.number_of_articles) or 0,
        "grossWeightOfJewellery": _to_number(item.gross_weight),
        "percentage": _to_number(item.percent_of_gold),
        "netAdjustedWeightOfJewellery": _to_number(item.net_adjusted_weight),
        "stoneWeight": _to_number(item.stone_weight),
        "netWeightOfJewellery": _to_number(item.net_weight),
        "jewelleryId": saas_jewellery_id if saas_jewellery_id is not None else str(item.id),
        "jewelleryName": label or item.type_of_jewellery or "",
        "actualGoldRateConsidered": _to_number(item.actual_gold_rate),
        "grossValueOfJewellery": _to_number(item.gross_value),
        "impurityWeightForDeduction": _to_number(item.impurity_deducted),
        "netAdjustedValueOfJewellery": _to_number(item.net_adjusted_value),
        "netValueOfMetal": _to_number(item.net_value),
        "actualPurityGrade": actual_purity,
        "adjustedPurityGrade": adjusted_purity,
        "adjustedGoldRateConsidered": _to_number(item.actual_gold_rate),
        "appraiserEvaluations": appraiser_evals,
    }


def _resolve_jewellery_image_url(
    item: JewelleryItem,
    url_value: Optional[str],
    url_key: str,
) -> Optional[str]:
    if url_value:
        return _presign_get(url_value)
    url_from_meta = (item.metadata or {}).get(url_key)
    if url_from_meta:
        return _presign_get(url_from_meta)
    return None


def _get_primary_packet(
    application: ApplicationV2,
    jewellery_items: List[JewelleryItem],
) -> Optional[Packet]:
    if jewellery_items:
        return jewellery_items[0].packet
    return Packet.objects.filter(application=application).first()


def _build_gold_details(
    packet: Optional[Packet],
    multi_appraisal: bool,
    source_id: str,
    source_name: str,
) -> Dict[str, Any]:
    if not packet:
        return {"multiAppraisal": multi_appraisal}
    return {
        "referenceNumber": packet.packet_id or "",
        "packetId": packet.packet_id or "",
        "appraiserId": packet.appraiser_id or "",
        "appraiserName": packet.appraiser_name or "",
        "grossWeightOfJewellery": _to_number(packet.gross_weight),
        "grossValueOfJewellery": _to_number(packet.gross_value),
        "netAdjustedWeightOfJewellery": _to_number(packet.net_adjusted_weight),
        "netAdjustedValueOfJewellery": _to_number(packet.net_adjusted_value),
        "sourceId": source_id,
        "sourceName": source_name,
        "multiAppraisal": multi_appraisal,
    }


def _resolve_poa_type(address_secondary: Dict[str, Any], address_primary: Optional[Dict[str, Any]] = None) -> str:
    explicit_poa_type = address_secondary.get("poa_type") or (address_primary or {}).get("poa_type")
    if explicit_poa_type:
        return explicit_poa_type

    poa = address_secondary.get("poa") or []
    if not poa:
        return DocumentType.AADHAAR
    first = poa[0] or {}
    return first.get("document_type") or ""


def _build_disbursement_accounts(
    bank_details: Dict[str, Any],
    personal: Dict[str, Any],
    principal_amount: Any,
) -> List[Dict[str, Any]]:
    return [
        {
            "bankName": bank_details.get("bank_name") or "",
            "accountName": bank_details.get("customer_name_as_per_bank")
            or personal.get("full_name")
            or "",
            "amount": principal_amount or 0,
            "ifscCode": bank_details.get("ifsc_code") or "",
            "bankBranchName": bank_details.get("branch_name") or "",
            "accountNo": bank_details.get("account_number") or "",
        }
    ]


def _map_bureau_fields(
    application: ApplicationV2,
    loan_details: Dict[str, Any],
) -> Tuple[str, Any, Any, str]:
    bureau_name = SAAS_DEFAULT_BUREAU_NAME
    bureau_pull_date = application.bureau_pull_date or ""
    bureau_report_link = application.bureau_report_link or ""
    bureau_reference_number = application.bureau_reference_number or loan_details.get("reference_number") or ""
    return (
        bureau_name,
        bureau_pull_date,
        bureau_report_link,
        bureau_reference_number,
    )


def _resolve_addresses(
    address_payload: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
    permanent = address_payload.get("permanent") or {}
    current_same = address_payload.get("current_same_as_permanent")
    current = permanent if current_same else address_payload.get("current") or {}
    return permanent, current, bool(current_same)


def _build_address_entries(
    permanent: Dict[str, Any],
    current: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        {
            "addressValue": permanent.get("address_line1", ""),
            "addressType": "PERMANENT",
            "addressState": _map_state_for_saas(permanent.get("state")),
            "addressPincode": permanent.get("pincode", ""),
            "addressCity": permanent.get("city", ""),
        },
        {
            "addressValue": current.get("address_line1", ""),
            "addressType": "COMMUNICATION",
            "addressState": _map_state_for_saas(current.get("state")),
            "addressPincode": current.get("pincode", ""),
            "addressCity": current.get("city", ""),
        },
    ]


class SaasClient:
    """
    Thin wrapper around SAAS Tech APIs (pre-screen, create-loan, doc upload).
    """

    def __init__(self):
        self.base_url = getattr(settings, "SAAS_URL", None)
        self.create_loan_url = getattr(settings, "SAAS_CREATE_LOAN_URL", None)
        self.upload_doc_url = getattr(settings, "SAAS_UPLOAD_DOC_URL", None)
        # Default creds
        self.access_key = getattr(settings, "SAAS_ACCESS_KEY", None)
        self.secret_key = getattr(settings, "SAAS_SECRET_KEY", None)
        self.client_code = getattr(settings, "SAAS_CLIENT_CODE", None)
        # Endpoint-specific overrides
        self.pre_access_key = getattr(settings, "SAAS_ACCESS_KEY_PRE_SCREEN", None)
        self.pre_secret_key = getattr(settings, "SAAS_SECRET_KEY_PRE_SCREEN", None)
        self.pre_client_code = getattr(settings, "SAAS_CLIENT_CODE_PRE_SCREEN", None)
        self.create_access_key = getattr(settings, "SAAS_ACCESS_KEY_CREATE_LOAN", None)
        self.create_secret_key = getattr(settings, "SAAS_SECRET_KEY_CREATE_LOAN", None)
        self.create_client_code = getattr(settings, "SAAS_CLIENT_CODE_CREATE_LOAN", None)
        self.fund_refund_url = getattr(settings, "SAAS_FUND_REFUND_URL", None)
        self.onboard_url = getattr(settings, "SAAS_SAVE_ONBOARD_URL", None)
        self.update_onboard_url = getattr(settings, "SAAS_UPDATE_ONBOARD_URL", None)
        self.onboard_access_key = getattr(settings, "SAAS_ACCESS_KEY_ONBOARD", None)
        self.onboard_secret_key = getattr(settings, "SAAS_SECRET_KEY_ONBOARD", None)
        self.onboard_client_code = getattr(settings, "SAAS_CLIENT_CODE_ONBOARD", None)
        self.notification_url = getattr(settings, "SAAS_NOTIFICATION_URL", None)
        self.session = requests.Session()

    def _headers(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        client_code: Optional[str] = None,
    ) -> Dict[str, str]:
        return {
            "accessKey": access_key or self.access_key or "",
            "secretKey": secret_key or self.secret_key or "",
            "clientCode": client_code or self.client_code or "",
            "Content-Type": "application/json",
        }

    def submit_pre_screen(self, payload: Dict[str, Any], application: Optional[ApplicationV2] = None) -> Dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("SAAS_URL is not configured")
        if not application and payload:
            app_id = payload.get("applicationId") or payload.get("clientLoanId") or payload.get("clientApplicationId")
            if app_id:
                application = ApplicationV2.objects.filter(application_id=app_id).first()
        base = self.base_url.rstrip("/")
        # If the env already includes the endpoint, don't append it again.
        if base.endswith("kyc/api/lead/addLeadDetail"):
            url = base
        else:
            url = base + "/kyc/api/lead/addLeadDetail"
        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.CREATE_LEAD,
            payload=payload,
            increment_attempt=True,
        )
        logger.info("SAAS pre-screen request | url=%s payload=%s", url, payload)
        resp = self.session.post(
            url,
            json=payload,
            headers=self._headers(
                access_key=self.pre_access_key,
                secret_key=self.pre_secret_key,
                client_code=self.pre_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        logger.info("SAAS pre-screen response %s %s", resp.status_code, resp.text)
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.CREATE_LEAD,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
        return resp.json() if resp.text else {}

    def create_loan(self, payload: Dict[str, Any], application: Optional[ApplicationV2] = None) -> Dict[str, Any]:
        if not self.create_loan_url:
            raise RuntimeError("SAAS_CREATE_LOAN_URL is not configured")
        if not application and payload:
            app_id = payload.get("applicationId") or payload.get("clientLoanId") or payload.get("clientApplicationId")
            if app_id:
                application = ApplicationV2.objects.filter(application_id=app_id).first()
        logger.info("SAAS create-loan request | url=%s payload=%s", self.create_loan_url, payload)
        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
            payload=payload,
            increment_attempt=True,
        )
        resp = self.session.post(
            self.create_loan_url,
            json=payload,
            headers=self._headers(
                access_key=self.create_access_key,
                secret_key=self.create_secret_key,
                client_code=self.create_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        logger.info("SAAS create-loan response %s %s", resp.status_code, resp.text)
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.CREATE_LOAN,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
        return resp.json() if resp.text else {}

    def notify_rh_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.notification_url:
            raise RuntimeError("SAAS_NOTIFICATION_URL is not configured")
        logger.info("SAAS notification request | url=%s payload=%s", self.notification_url, payload)
        resp = self.session.post(
            self.notification_url,
            json=payload,
            headers=self._headers(
                access_key=self.onboard_access_key,
                secret_key=self.onboard_secret_key,
                client_code=self.onboard_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        logger.info("SAAS notification response %s %s", resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def save_onboard_details(self, payload: Dict[str, Any], application: Optional[ApplicationV2] = None) -> Dict[str, Any]:
        if not self.onboard_url:
            raise RuntimeError("SAAS_SAVE_ONBOARD_URL is not configured")
        if not application and payload:
            app_id = payload.get("applicationId") or payload.get("clientLoanId") or payload.get("clientApplicationId")
            if app_id:
                application = ApplicationV2.objects.filter(application_id=app_id).first()
        
        logger.info("SAAS save-onboard request | url=%s", self.onboard_url)
        
        # Using CREATE_LOAN request type for logging as it's the closest existing type
        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
            payload=payload,
            increment_attempt=True,
        )
        # print("payload-->>>",payload)
        
        resp = self.session.post(
            self.onboard_url,
            json=payload,
            headers=self._headers(
                access_key=self.onboard_access_key,
                secret_key=self.onboard_secret_key,
                client_code=self.onboard_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        print("resp.text-->>>",resp.text)
        logger.info("SAAS save-onboard response %s %s", resp.status_code, resp.text)
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.CREATE_LOAN,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
        return resp.json() if resp.text else {}

    def submit_fund_refund(self, payload: Dict[str, Any], application: Optional[ApplicationV2] = None) -> Dict[str, Any]:
        if not self.fund_refund_url:
            raise RuntimeError("SAAS_FUND_REFUND_URL is not configured")
        
        logger.info("SAAS fund-refund request | url=%s", self.fund_refund_url)
        
        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.FUND_REFUND,
            payload=payload,
            increment_attempt=True,
        )
        
        resp = self.session.post(
            self.fund_refund_url,
            json=payload,
            headers=self._headers(
                access_key=self.onboard_access_key,
                secret_key=self.onboard_secret_key,
                client_code=self.onboard_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        logger.info("SAAS fund-refund response %s %s", resp.status_code, resp.text)
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.FUND_REFUND,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
        return resp.json() if resp.text else {}

    def update_onboard_details(self, payload: Dict[str, Any], application: Optional[ApplicationV2] = None) -> Dict[str, Any]:
        if not self.update_onboard_url:
            # Fallback or derive from onboard_url if not explicitly set
            if self.onboard_url:
                self.update_onboard_url = self.onboard_url.replace("saveOnboardDetails", "updateOnboardDetails")
            else:
                raise RuntimeError("SAAS_UPDATE_ONBOARD_URL is not configured")
        if not application and payload:
            app_id = payload.get("applicationId") or payload.get("clientLoanId") or payload.get("clientApplicationId")
            if app_id:
                application = ApplicationV2.objects.filter(application_id=app_id).first()

        logger.info("SAAS update-onboard request | url=%s", self.update_onboard_url)

        log_saas_request(
            application=application,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
            payload=payload,
            increment_attempt=True,
        )

        resp = self.session.put(
            self.update_onboard_url,
            json=payload,
            headers=self._headers(
                access_key=self.onboard_access_key,
                secret_key=self.onboard_secret_key,
                client_code=self.onboard_client_code,
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        logger.info("SAAS update-onboard response %s %s", resp.status_code, resp.text)
        try:
            resp.raise_for_status()
        finally:
            log_saas_request(
                application=application,
                request_type=SaasRequestLog.RequestType.CREATE_LOAN,
                response_status=resp.status_code,
                response_body=_safe_json(resp),
            )
        return resp.json() if resp.text else {}

    def upload_document(self, payload: dict) -> dict:
        """
        SAAS no longer requires direct uploads; just return payload (file locations).
        Kept for backward compatibility/logging.
        """
        logger.info("SAAS upload-doc skipped (sending locations only)")
        return {"status": "skipped", "payload": payload}


def generate_saas_request_id(prefix: str = "SAAS") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def _split_name(name: str) -> Tuple[str, str, str]:
    if not name:
        return "", "", ""
    parts = [part for part in name.split() if part]
    if not parts:
        return "", "", ""
    title_token = parts[0].rstrip(".").lower()
    if title_token in {
        "mr",
        "mrs",
        "ms",
        "miss",
        "dr",
        "prof",
        "shri",
        "sri",
        "smt",
        "kumari",
    }:
        parts = parts[1:]
    if not parts:
        return "", "", ""
    if len(parts) == 1:
        return parts[0], "", ""
    if len(parts) == 2:
        return parts[0], "", parts[1]
    return parts[0], " ".join(parts[1:-1]), parts[-1]


def _add_months(value, months: int):
    if not value or not months:
        return value
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    # Clamp day to last day of target month.
    import calendar

    last_day = calendar.monthrange(year, month)[1]
    day = min(value.day, last_day)
    return value.replace(year=year, month=month, day=day)


def _split_name_with_title(name: str) -> Tuple[str, str, str, str]:
    if not name:
        return "", "", "", ""
    parts = [part for part in name.split() if part]
    if not parts:
        return "", "", "", ""
    title_token = parts[0].rstrip(".")
    if title_token.lower() in {
        "mr",
        "mrs",
        "ms",
        "miss",
        "dr",
        "prof",
        "shri",
        "sri",
        "smt",
        "kumari",
    }:
        parts = parts[1:]
    else:
        title_token = ""
    first, middle, last = _split_name(" ".join(parts))
    return title_token, first, middle, last


def _get_documents(application: ApplicationV2) -> List[ApplicationDocument]:
    return list(ApplicationDocument.objects.filter(application=application))


def _first_document(
    documents: List[ApplicationDocument],
    doc_type: str,
    *,
    subtype_contains: Optional[str] = None,
) -> Optional[ApplicationDocument]:
    for doc in documents:
        if doc.document_type != doc_type:
            continue
        if subtype_contains and subtype_contains not in (doc.subtype or "").lower():
            continue
        return doc
    return None


def _get_snapshot_payload(application: ApplicationV2, stage: str) -> Optional[Dict[str, Any]]:
    snap = (
        application.stage_snapshots.filter(stage=stage, is_complete=True)
        .order_by("-modified_at")
        .first()
    )
    return snap.payload if snap else None


def _resolve_aadhar_number(
    documents: List[ApplicationDocument],
    fallback: Optional[str] = None,
) -> str:
    aadhar_doc = _first_document(
        documents,
        DocumentType.AADHAAR,
        subtype_contains="front",
    ) or _first_document(documents, DocumentType.AADHAAR)
    metadata = _doc_metadata(aadhar_doc)
    return (
        metadata.get("aadhar_number")
        or metadata.get("aadhaar_number")
        or fallback
        or ""
    )


def _resolve_pre_screen_client_loan_id(application: ApplicationV2) -> str:
    lending_partner_bank = _get_snapshot_payload(application, ApplicationStage.LENDING_PARTNER_BANK) or {}
    return (
        lending_partner_bank.get("client_loan_id")
        or getattr(application, "client_loan_id", None)
        or "GLN00007"
    )


def validate_pre_screen_requirements(application: ApplicationV2) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], str]:
    """
    Ensure pre-screen snapshots exist and key fields are present.

    Co-lending/fresh journeys use BASIC. Self Lending uses PERSONAL directly.
    """
    pan = _get_snapshot_payload(application, ApplicationStage.PAN)
    if not pan and application.loan_type == LeadType.CO_LENDING:
        lead = application.lead
        pan = {
            "pan_number": lead.pan_number,
            "name_on_pan": lead.customer_name,
            "dob_as_per_pan": lead.dob,
        }

    is_self_lending = application.loan_type == LeadType.SELF_LENDING
    applicant = _get_snapshot_payload(
        application,
        (
            ApplicationStage.PERSONAL
            if is_self_lending
            else ApplicationStage.BASIC
        ),
    )
    address = _get_snapshot_payload(application, ApplicationStage.ADDRESS)

    missing = []
    if not pan:
        missing.append("stage PAN not completed")
    if not applicant:
        missing.append(
            "stage PERSONAL not completed"
            if is_self_lending
            else "stage BASIC not completed"
        )
    if not address:
        missing.append("stage ADDRESS not completed")
    if missing:
        raise ValueError(", ".join(missing))

    # Resolve PAN number/name/dob
    documents = _get_documents(application)
    pan_doc = _first_document(documents, DocumentType.PAN)
    pan_number = _doc_metadata(pan_doc).get("pan_number") or pan.get("pan_number")
    name_on_pan = pan.get("name_on_pan")
    dob_as_per_pan = pan.get("dob_as_per_pan")
    if not pan_number:
        missing.append("PAN number")
    if not name_on_pan:
        missing.append("Name on PAN")
    if not dob_as_per_pan:
        missing.append("DOB as per PAN")

    if is_self_lending:
        if not _resolve_aadhar_number(documents):
            missing.append("AADHAAR_FRONT:aadhar_number")

    if is_self_lending:
        required_fields = [
            "full_name",
            "dob",
            "dob_as_per_pan",
            "mobile_number",
            "gender",
        ]
        field_prefix = "PERSONAL"
    else:
        required_fields = [
            "full_name_as_pan",
            "dob",
            "dob_as_per_pan",
            "phone_number",
            "gender",
        ]
        # Aadhaar is optional for Fresh and Balance Transfer.
        if application.loan_type not in {
            LeadType.FRESH,
            LeadType.BALANCE_TRANSFER,
        }:
            required_fields.append("aadhar_number")
        field_prefix = "BASIC"

    for field in required_fields:
        if not applicant.get(field):
            missing.append(f"{field_prefix}:{field}")

    # ADDRESS required fields (permanent)
    permanent, current, _current_same = _resolve_addresses(address)
    for field in ["address_line1", "pincode", "state", "city"]:
        if not permanent.get(field):
            missing.append(f"ADDRESS:permanent:{field}")
    for field in ["address_line1", "pincode", "state", "city"]:
        if not current.get(field):
            missing.append(f"ADDRESS:current:{field}")

    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))

    return pan, applicant, address, pan_number


def build_create_loan_payload(application: ApplicationV2) -> Dict[str, Any]:
    """
    Build payload for SAAS createLoan from persisted data.
    This is a best-effort mapping using saved stage snapshots and related models.
    """
    stages = validate_post_screen_requirements(application)
    lead = application.lead
    basic = stages["basic"]
    personal = stages["personal"]
    loan_details = stages["loan"]
    bank_details = stages["bank"]
    address_primary = stages["address"]
    address_secondary = _get_snapshot_payload(application, ApplicationStage.ADDRESS_SECONDARY) or {}

    jewellery_items = list(
        JewelleryItem.objects.filter(packet__application=application).select_related("packet")
    )
    first_packet = _get_primary_packet(application, jewellery_items)
    no_of_assets = len(jewellery_items)

    gold_details = None

    documents = _get_documents(application)
    pan_doc = _first_document(documents, DocumentType.PAN)
    pan_meta = _doc_metadata(pan_doc)
    pan_number = pan_meta.get("pan_number")
    pan_name = pan_meta.get("name_on_pan")
    aadhar_doc = _first_document(documents, DocumentType.AADHAAR, subtype_contains="front")
    if not aadhar_doc:
        aadhar_doc = _first_document(documents, DocumentType.AADHAAR)
    aadhar_number = _doc_metadata(aadhar_doc).get("aadhar_number") or basic.get("aadhar_number")
    passport_doc = _first_document(documents, DocumentType.PASSPORT)
    passport_meta = _doc_metadata(passport_doc)
    driving_doc = _first_document(documents, DocumentType.DRIVING_LICENSE)
    driving_meta = _doc_metadata(driving_doc)
    voter_doc = _first_document(documents, DocumentType.VOTER_ID)
    voter_meta = _doc_metadata(voter_doc)

    permanent, current, current_same = _resolve_addresses(address_primary)

    (
        derived_title,
        first_name,
        middle_name,
        last_name,
    ) = _split_name_with_title(
        personal.get("full_name") or basic.get("full_name_as_pan") or lead.customer_name
    )
    age_value = _calculate_age(
        personal.get("dob_as_per_pan")
        or basic.get("dob_as_per_pan")
        or personal.get("dob")
        or basic.get("dob")
    )

    # Defaults from provided enums
    emi_type = loan_details.get("type_of_emi") or "FIXED"
    interest_type = loan_details.get("interest_type") or "FIXED"
    repayment_frequency = loan_details.get("repayment_frequency") or "BULLET"
    repayment_frequency_norm = (repayment_frequency or "").lower() or "bullet"
    category = loan_details.get("category") or "SECURED"
    disbursement_type = loan_details.get("disbursement_type") or "SINGLE"

    eligible_amount = loan_details.get("eligible_amount")
    requested_amount = loan_details.get("requested_amount")
    principal_amount = eligible_amount or requested_amount or ""
    product_id = application.partner_product_code or getattr(settings, "SAAS_PRODUCT_ID", "") or ""
    agreement_id = SAAS_AGREEMENT_ID
    spread_id = application.spread_id or loan_details.get("spread_id") or ""
    interest_start_date = application.interest_start_date or loan_details.get("interest_start_date")
    if not interest_start_date:
        interest_start_date = timezone.localdate()
    loan_maturity_date = application.loan_maturity_date or loan_details.get("loan_maturity_date")
    if not loan_maturity_date:
        tenure_months = loan_details.get("tenure_months") or loan_details.get("tenure_years") or 0
        loan_maturity_date = _add_months(
            interest_start_date, int(tenure_months) if tenure_months else 0
        )
    first_repayment_date = application.first_repayment_date or loan_details.get("first_repayment_date")
    if not first_repayment_date and repayment_frequency_norm == "bullet":
        first_repayment_date = loan_maturity_date
    consent_timestamp = application.consent_timestamp
    consent_ip = application.consent_ip
    (
        bureau_name,
        bureau_pull_date,
        bureau_report_link,
        bureau_reference_number,
    ) = _map_bureau_fields(application, loan_details)
    # SAAS expects a fixed LTR value.
    ltr = 75
    processing_fee = application.processing_fee or loan_details.get("processing_fee") or ""
    stamp_duty = application.stamp_duty or loan_details.get("stamp_duty") or ""
    insurance_charges = application.insurance_charges or loan_details.get("insurance_charges") or ""
    documentation_charges = application.documentation_charges or loan_details.get("documentation_charges") or ""
    other_charges = application.other_charges or loan_details.get("other_charges") or ""
    total_charges = application.total_charges or loan_details.get("total_charges") or ""
    primary_borrower_type = "INDIVIDUAL"
    income_source_raw = application.income_source or personal.get("income_source") or ""
    income_source = _choice_label(income_source_raw, IncomeSource)
    occupation_raw = application.occupation or personal.get("occupation") or ""
    occupation = _choice_label(occupation_raw, Occupation)
    annual_income = personal.get("annual_income") or ""
    net_monthly_income = personal.get("net_monthly_income") or ""
    net_worth = personal.get("net_worth")
    nationality = "Indian"
    nri_status = application.nri_status or personal.get("nri_status") or ""
    caste_raw = application.caste or personal.get("category") or ""
    caste = _choice_label(caste_raw, Category)
    compliance = application.compliance or ""
    requested_numeric = _to_number(requested_amount)
    multi_appraisal = bool(requested_numeric and requested_numeric > 500000)
    partner_branch_code = application.partner_branch_code or ""
    partner_branch_name = application.partner_branch_name or ""
    created_by_user = getattr(application.lead, "created_by", None)
    fatca_official_id = getattr(created_by_user, "employee_id", None)
    fatca_official_name = ""
    if created_by_user:
        fatca_official_name = f"{created_by_user.first_name} {created_by_user.last_name}".strip()
    source_id = application.source_id or str(fatca_official_id or "")
    source_name = fatca_official_name or ""
    fatca_official_branch = "Gurgaon"
    fatca_official_designation = "SO"
    fatca_date = (application.created_at or timezone.now()).date().isoformat()
    fatca_place = permanent.get("district") or ""
    lead_id_for_saas = getattr(lead, "lead_code", "") or ""
    gold_details = _build_gold_details(
        first_packet,
        multi_appraisal,
        source_id,
        source_name,
    )

    (
        father_title,
        father_first,
        father_middle,
        father_last,
    ) = _split_name_with_title(personal.get("father_full_name") or "")
    (
        mother_title,
        mother_first,
        mother_middle,
        mother_last,
    ) = _split_name_with_title(personal.get("mother_full_name") or "")

    identity_payload = {
        "panNumber": pan_number,
        "firstName": first_name,
        "middleName": middle_name,
        "lastName": last_name,
        "nameAsPerPan": pan_name or basic.get("full_name_as_pan") or "",
        "dateOfBirth": str(personal.get("dob") or basic.get("dob") or ""),
        "dateOfBirthAsPerPan": str(personal.get("dob_as_per_pan") or basic.get("dob_as_per_pan") or ""),
        "aadharNumber": aadhar_number or "",
        "mobileNumber": personal.get("mobile_number") or basic.get("phone_number") or lead.contact_number,
        "poaType": _resolve_poa_type(address_secondary, address_primary),
        "primaryBorrowerType": primary_borrower_type,
        "customerCategory": _map_customer_category(
            personal.get("category"),
            income_source_raw,
            primary_borrower_type,
            personal.get("profession"),
        ),
        "passPortNumber": passport_meta.get("passport_number") or "",
        "passPortExpiryDate": passport_meta.get("passport_expiry_date") or "",
        "passPortFileNumber": passport_meta.get("passport_file_number") or "",
        "passportissuedate": passport_meta.get("passport_issue_date") or "",
        "passportplaceofissue": passport_meta.get("passport_place_of_issue") or "",
        "title": personal.get("title") or derived_title,
        "email": personal.get("email") or basic.get("email") or "",
        "placeOfBirth": personal.get("place_of_birth") or "",
        "gender": _map_gender(personal.get("gender")),
        "maritalStatus": _choice_label(personal.get("marital_status"), MaritalStatus),
        "religion": _choice_label(personal.get("religion"), Religion),
        "occupation": occupation,
        "nationality": nationality,
        "nriStatus": "N",
        "caste": caste,
        "fatherNameTitle": father_title,
        "fatherName": " ".join(part for part in [father_first, father_middle, father_last] if part),
        "motherTitle": mother_title,
        "motherName": " ".join(part for part in [mother_first, mother_middle, mother_last] if part),
    }

    address_payload = {
        "mailingAddress": "PERMANENT" if current_same else "CURRENT",
        "permanentPincode": permanent.get("pincode") or "",
        "permanentState": _map_state_for_saas(permanent.get("state")),
        "permanentCity": permanent.get("city") or "",
        "permanentAddress": permanent.get("address_line1") or "",
        "currentPincode": current.get("pincode") or "",
        "currentState": _map_state_for_saas(current.get("state")),
        "currentCity": current.get("city") or "",
        "currentAddress": current.get("address_line1") or "",
        "addressType": "current",
    }

    bureau_payload = {
        "nameOfBureau": bureau_name,
        "bureauScore": application.bureau_score or "",
        "cibilScore": -1,
        "bureauReportLink": bureau_report_link,
        "bureauPullDate": str(bureau_pull_date or ""),
        "referenceNumber": bureau_reference_number,
    }

    # Fetch originatorRoiForBlendedYield from RoiConfiguration
    originator_roi = None
    try:
        bank_param = _get_roi_bank_value(application.lending_partner)
        
        lead_type_val = application.loan_type
        if lead_type_val == LeadType.BANK_LEAD:
            lead_type_param = "CO_LENDING"
        else:
            lead_type_param = lead_type_val

        loan_range_payload = _get_snapshot_payload(application, ApplicationStage.LOAN_RANGE_SELECTION) or {}
        is_above = loan_range_payload.get("above_range")
        if is_above is None:
            is_above = loan_range_payload.get("avobe_range")
        loan_amount = _to_number(loan_range_payload.get("loan_amount"))
        if is_above is True:
            loan_range_param = "MORE_THAN_2_5_LAKHS"
        elif is_above is False:
            loan_range_param = "LESS_THAN_2_5_LAKHS"
        elif loan_amount is not None and loan_amount > 250000:
            loan_range_param = "MORE_THAN_2_5_LAKHS"
        else:
            loan_range_param = "LESS_THAN_2_5_LAKHS"

        product_selection_payload = _get_snapshot_payload(application, ApplicationStage.PRODUCT_SELECTION) or {}
        product_type_param = product_selection_payload.get("product_type") or "GENERAL_PURPOSE"

        repayment_schedule_param = (loan_details.get("repayment_frequency") or "BULLET").upper()

        tenure_val = _to_number(loan_details.get("tenure_months") or loan_details.get("tenure_years"), None)
        tenure_param = f"{int(tenure_val)}_MONTHS" if tenure_val is not None else None
        logger.info("----------->>>>bank_param=%s, lead_type_param=%s, loan_range_param=%s, product_type_param=%s, repayment_schedule_param=%s, tenure_param=%s", bank_param, lead_type_param, loan_range_param, product_type_param, repayment_schedule_param, tenure_param)
        roi_config = RoiConfiguration.objects.filter(
            bank__iexact=bank_param,
            lead_type__iexact=lead_type_param,
            loan_range__iexact=loan_range_param,
            product_type__iexact=product_type_param,
            repayment_schedule__iexact=repayment_schedule_param,
            tenure__iexact=tenure_param,
        ).first()
        if roi_config and roi_config.manipal_roi is not None:
            originator_roi = _to_number(roi_config.manipal_roi)
    except Exception as e:
        logger.error(f"Error fetching RoiConfiguration for application {application.application_id}: {e}", exc_info=True)

    loan_payload = {
        "principalAmount": _to_number(principal_amount),
        "tenure": loan_details.get("tenure_months") or loan_details.get("tenure_years") or "",
        "typeOfEmi": emi_type,
        "interestRate": _to_number(loan_details.get("interest_rate")),
        "originatorRoiForBlendedYield": originator_roi,
        "interestStartDate": str(interest_start_date or ""),
        "interestType": interest_type,
        "repaymentFrequency": repayment_frequency_norm,
        "disbursementType": disbursement_type,
        "category": category,
        # "subCategory": _map_sub_category(loan_details.get("loan_subcategory")),
        "subCategory": "fresh",
        "purpose": _choice_label(loan_details.get("purpose"), LoanPurpose),
        "loanMaturityDate": str(loan_maturity_date or ""),
        "firstRepaymentDate": str(first_repayment_date or ""),
        "lastDisbDate": str(loan_details.get("last_disb_date") or ""),
        "numberOfRepayments": loan_details.get("number_of_repayments") or 1,
        "ltr": ltr,
        "processingFee": _to_number(processing_fee),
        "stampDuty": _to_number(stamp_duty),
        "insuranceCharges": _to_number(insurance_charges),
        "documentationCharges": _to_number(documentation_charges),
        "otherCharges": _to_number(other_charges),
        "totalCharges": _to_number(total_charges),
        "annualIncome": _to_number(annual_income),
        "netMonthlyIncome": _to_number(net_monthly_income),
        "foir": _to_number(loan_details.get("foir") or personal.get("foir")),
        "tenureFrequency": (
            loan_details.get("tenure_frequency") or repayment_frequency or ""
        ).lower()
        or "bullet",
    }

    compliance_payload = {
        "consentTimestamp": consent_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        if consent_timestamp
        else "",
        "consentipaddress": consent_ip or "",
        "compliance": compliance,
        "sourceId": source_id,
        "geoLocation": _map_geo_location(permanent.get("state") or current.get("state")),
        "complianceSecurityFlag": "Y",
        "complianceDelinquency": "Y",
        "sourcingDetail": {
            "complianceVendorLegal": "Y",
            "complianceLenderPolicy": "Y",
            "complianceOriginatorSourcing": "Y",
            "complianceEligibleVendors": "Y",
            "complianceSegmentFlag": "Y",
        },
    }

    kyc_identity_payload = {
        "nameAsPerDrivingLicense": driving_meta.get("name") or "",
        "drivingLicenseNumber": driving_meta.get("dl_number") or "",
        "drivingLicenseExpiryDate": driving_meta.get("expiry_date") or "",
        "drivingLicenseIssueDate": driving_meta.get("issue_date") or "",
        "voterIdNumber": voter_meta.get("document_number") or voter_meta.get("voter_id_number") or "",
        "nameAsPerVoterId": voter_meta.get("name") or "",
    }

    fatca_payload = {
        "fatcaVerificationOfficialId": str(fatca_official_id or ""),
        "fatcaVerificationOfficialBranch": fatca_official_branch,
        "fatcaVerificationOfficialDesignation": fatca_official_designation,
        "fatcaVerificationOfficialName": fatca_official_name or "",
        "fatcaVerificationDate": fatca_date,
        "fatcaPlace": fatca_place,
        "fatcaDeclarationDate": fatca_date,
    }

    payload = {
        "leadId": lead_id_for_saas,
        "age": age_value if age_value is not None else "",
        "productId": product_id,
        "clientLoanId": application.application_id,
        "applicationId": application.application_id,
        "clientApplicationId": application.application_id,
        "clientCustomerId": lead.customer_id,
        "agreementId": agreement_id,
        "noOfAssets": no_of_assets,
        "spreadId": spread_id,
        "politicallyExposed": personal.get("politically_exposed") or "N",
        "partnerBranchCode": partner_branch_code,
        "partnerBranchName": partner_branch_name,
        "partnerProductCode": "MANIPAL",
        "partnerSchemeCode": "MTPGL",
        "incomeSource": income_source,
        "applicantProfession": occupation,
        "netWorth": _to_number(net_worth),
        "loanCycle": loan_details.get("loan_cycle") or 1,
        "goldDetails": gold_details,
        "jewelleryDetails": [],
        "disbursementAccounts": _build_disbursement_accounts(
            bank_details, personal, principal_amount
        ),
        **identity_payload,
        **address_payload,
        **bureau_payload,
        **loan_payload,
        **compliance_payload,
        **kyc_identity_payload,
        **fatca_payload,
    }

    # Attach document URLs (presigned GET) grouped per SAAS field expectations.
    doc_field_map = {
        DocumentType.PAN: "pannumberUrl",
        DocumentType.AADHAAR: "aadharNumberLink",
        DocumentType.VOTER_ID: "votingIdLink",
        DocumentType.DRIVING_LICENSE: "drivingLicenceNumberUrl",
        DocumentType.PASSPORT: "passportNumberUrl",
        DocumentType.SELFIE: "selfieUrl",
        DocumentType.OTHER: "otherKycUrl",  # fallback for OTHER without specific subtype
        DocumentType.FRESH_LOAN: "otherKycUrl",
    }

    # Additional mapping for OTHER doc subtypes (case-insensitive contains)
    other_subtype_map = {
        "bureau": "bureauReportUrl",
        "form60": "form60Url",
        "application_form": "applicationFormUrl",
        "bank_statement": "bankStatementUrl",
        "rent_agreement": "rentagreementlink",
        "utility_bill": "utilitybillslink",
        "other_kyc": "otherKycUrl",
        "pan_front": "pannumberUrl",
        "pan_back": "pannumberUrl",
        "pan_card": "pannumberUrl",
        "additional": "otherKycUrl",
    }

    def _resolve_doc_field(doc: ApplicationDocument) -> Optional[str]:
        target = doc_field_map.get(doc.document_type)
        if doc.document_type not in {DocumentType.OTHER, DocumentType.FRESH_LOAN}:
            return target
        subtype = (doc.subtype or "").lower()
        for key, field_name in other_subtype_map.items():
            if key in subtype:
                return field_name
        return target

    doc_url_items: Dict[str, List[Tuple[int, int, str]]] = {}
    doc_idx = 0
    for doc in documents:
        target_field = _resolve_doc_field(doc)
        if not target_field:
            continue
        url = _doc_url(doc)
        if not url:
            continue
        url = _presign_get(url, doc.id)
        subtype = (doc.subtype or "").lower()
        priority = 1
        if doc.document_type in {
            DocumentType.PAN,
            DocumentType.AADHAAR,
            DocumentType.VOTER_ID,
            DocumentType.DRIVING_LICENSE,
            DocumentType.PASSPORT,
        }:
            if "front" in subtype:
                priority = 0
            elif "back" in subtype:
                priority = 2
        doc_url_items.setdefault(target_field, []).append((priority, doc_idx, url))
        doc_idx += 1

    # Only set fields that have values
    for field_name, items in doc_url_items.items():
        urls = [item[2] for item in sorted(items, key=lambda entry: (entry[0], entry[1]))]
        if urls:
            payload[field_name] = urls

    # If we have a bureau report doc, set bureauReportUrl as well (single string expected)
    bureau_url = _first_document_url(documents, DocumentType.OTHER, subtype_contains="bureau")
    if bureau_url:
        payload["bureauReportUrl"] = bureau_url

    # Jewellery images: flatten front/back per item with code-based naming expectations.
    jewellery_urls: List[str] = []
    jewellery_details: List[Dict[str, Any]] = []
    code_side_counts: Dict[Tuple[str, str], int] = {}
    for item in jewellery_items:
        packet = item.packet
        code, label, saas_jewellery_id = _resolve_jewellery_meta(item.type_of_jewellery)

        for side, url_value, url_key in (
            ("FRONT", item.front_image_url, "front_image_url"),
            ("BACK", item.back_image_url, "back_image_url"),
            ("WEIGHING", item.weighing_machine_image_url, "weighing_machine_image_url"),
            ("CERTIFICATE", item.appraiser_certificate_image_url, "appraiser_certificate_image_url"),
        ):
            url = _resolve_jewellery_image_url(item, url_value, url_key)
            _append_jewellery_url(jewellery_urls, code_side_counts, code, side, url)

        appraiser_eval = _build_appraiser_eval(
            packet,
            item,
            label,
            saas_jewellery_id,
            fallback_packet=first_packet,
        )
        appraiser_evals = [appraiser_eval]
        bank_appraiser_id = loan_details.get("bank_appraiser_id")
        bank_appraiser_name = loan_details.get("bank_appraiser_name")
        if multi_appraisal and bank_appraiser_id and bank_appraiser_name:
            bank_eval = dict(appraiser_eval)
            bank_eval["appraiserId"] = bank_appraiser_id
            bank_eval["appraiserName"] = bank_appraiser_name
            appraiser_evals.append(bank_eval)
        jewellery_details.append(
            _build_jewellery_detail(item, label, saas_jewellery_id, appraiser_evals)
        )

    if jewellery_urls:
        payload["jewelleryUrl"] = jewellery_urls
    if jewellery_details:
        payload["jewelleryDetails"] = jewellery_details

    return payload


def build_rh_approval_notification_payload(application: ApplicationV2) -> Dict[str, Any]:
    """
    Build RH approval notification payload for SAAS, including the approved selfie.
    """
    documents = _get_documents(application)
    payload = {
        "applicationId": application.application_id,
        "status": "RH",
        "remarks": application.rh_remarks or "",
    }
    selfie_url = _first_document_url(documents, DocumentType.SELFIE)
    if selfie_url:
        payload["selfieUrl"] = selfie_url
    return payload


def build_fund_refund_payload(application: ApplicationV2, refund_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build payload for SAAS fund-return/submit.
    Uses presigned URLs for images to ensure SAAS can access them.
    """
    cheque_image_urls = refund_entry.get("cheque_image_urls")
    if cheque_image_urls is None:
        cheque_image_url = refund_entry.get("cheque_image_url")
        if isinstance(cheque_image_url, list):
            cheque_image_urls = cheque_image_url
        elif cheque_image_url:
            cheque_image_urls = [cheque_image_url]
        else:
            cheque_image_urls = []

    return {
        "loanId": application.application_id,
        "amount": _to_number(refund_entry.get("amount")),
        "paymentMode": refund_entry.get("payment_mode") or "",
        "fundTransferredBy": refund_entry.get("fund_transferred_by") or "",
        "transactionReferenceNumber": refund_entry.get("transaction_reference_number") or "",
        "transactionId": refund_entry.get("id") or "",
        "bankName": refund_entry.get("bank_name") or "",
        "relationship": refund_entry.get("relationship") or "",
        "chequeImageUrls": [_presign_get(url) for url in cheque_image_urls if url],
        "transactionProofUrl": _presign_get(refund_entry.get("transaction_proof_url")) if refund_entry.get("transaction_proof_url") else "",
        "relationshipProofUrl": _presign_get(refund_entry.get("relationship_proof_url")) if refund_entry.get("relationship_proof_url") else "",
    }


def build_bt_onboard_payload(application: ApplicationV2) -> Dict[str, Any]:
    """
    Build payload for SAAS saveOnboardDetails for Balance Transfer loans.
    """
    app_data = ApplicationStateSerializer(application).data
    lead_data = LeadV2Serializer(application.lead).data

    # Merge lead into application as requested
    app_data["lead"] = lead_data

    # Ensure payload is JSON serializable (convert Decimals to strings/floats)
    # We do this by dumping and loading back via a custom encoder if needed,
    # or more simply, using DRF's behavior which we already have in .data.
    # However, since snapshots can have raw Decimals, we'll do a safe pass:
    return json.loads(json.dumps({
        "status": "success",
        "data": {
            "application": app_data
        }
    }, default=str))


def map_documents_for_saas(application: ApplicationV2) -> List[Dict[str, Any]]:
    """
    Map our ApplicationDocuments to SAAS doc upload payloads.
    """
    doc_id_map = getattr(settings, "SAAS_DOCUMENT_ID_MAP", {}) or {}
    uploads = []
    for doc in _get_documents(application):
        doc_id = doc_id_map.get(doc.document_type)
        if not doc_id:
            continue
        url = _doc_url(doc)
        if not url:
            continue
        uploads.append(
            {
                "clientApplicationId": application.application_id,
                "documentId": doc_id,
                "url": _presign_get(url, doc_id),
            }
        )
    return uploads


def validate_post_screen_requirements(application: ApplicationV2) -> Dict[str, Dict[str, Any]]:
    """
    Ensure key post-screen stages are present before finalize/create-loan.
    Returns a dict of stage payloads.
    Raises ValueError on missing.
    """
    required_stage = {
        "basic": _get_snapshot_payload(application, ApplicationStage.BASIC),
        "personal": _get_snapshot_payload(application, ApplicationStage.PERSONAL),
        "address": _get_snapshot_payload(application, ApplicationStage.ADDRESS),
        "loan": _get_snapshot_payload(application, ApplicationStage.LOAN),
        "bank": _get_snapshot_payload(application, ApplicationStage.BANK),
    }
    # For Fresh loans, Gold stage is not required as per UI design.
    if application.loan_type != LeadType.FRESH:
        required_stage["gold"] = _get_snapshot_payload(application, ApplicationStage.GOLD)

    missing = [name for name, payload in required_stage.items() if not payload]
    if missing:
        raise ValueError("Missing required stages: " + ", ".join(missing))
    return required_stage


def build_pre_screen_payload(application: ApplicationV2) -> Dict[str, Any]:
    """
    Build payload for SAAS pre-screen (addLeadDetail) from persisted data.
    Raises ValueError if required data is missing.
    """
    lead = application.lead
    pan, applicant, address, pan_number = validate_pre_screen_requirements(application)
    is_self_lending = application.loan_type == LeadType.SELF_LENDING

    if is_self_lending:
        full_name = applicant.get("full_name")
        gender = applicant.get("gender")
        dob_as_per_pan = applicant.get("dob_as_per_pan")
        dob = applicant.get("dob")
        phone_number = applicant.get("mobile_number")
        alternate_number = applicant.get("alternate_mobile_number")
    else:
        full_name = applicant.get("full_name_as_pan")
        gender = applicant.get("gender")
        dob_as_per_pan = applicant.get("dob_as_per_pan")
        dob = applicant.get("dob")
        phone_number = applicant.get("phone_number")
        alternate_number = applicant.get("alternate_number")

    first_name, middle_name, last_name = _split_name(
        pan.get("name_on_pan") or lead.customer_name or full_name
    )

    # Aadhaar belongs to the DOCUMENTS stage in Self Lending.
    documents = _get_documents(application)
    aadhar_number = _resolve_aadhar_number(
        documents,
        fallback=applicant.get("aadhar_number"),
    )
    lead_code = getattr(lead, "lead_code", "") or ""

    # Addresses
    permanent, current, _current_same = _resolve_addresses(address)

    payload = {
        "customerId": lead.customer_id,
        "leadId": lead_code,
        "clientLoanId": _resolve_pre_screen_client_loan_id(application),
        "applicationId": application.application_id,
        "pan": pan_number or "",
        "agreementId": SAAS_AGREEMENT_ID,
        "modelName": getattr(settings, "SAAS_MODEL_NAME", "CLM1"),
        "customerType": "individual",
        "businessName": "",
        "firstName": first_name,
        "middleName": middle_name,
        "lastName": last_name,
        "gender": (gender or "").lower(),
        "nameAsPerPan": pan.get("name_on_pan") or full_name,
        "dateOfBirthAsPerPan": str(
            pan.get("dob_as_per_pan") or dob_as_per_pan or ""
        ),
        "dateOfBirth": str(dob or dob_as_per_pan or ""),
        "phoneNumber": phone_number or lead.contact_number,
        "mobileNumber": alternate_number or lead.contact_number,
        "email": applicant.get("email") or "",
        "dedupeType": "single",
        "aadharNumber": aadhar_number or "",
        "dedupeIds": [
            {"idValue": pan_number or "", "idType": "PAN"},
            {"idValue": aadhar_number or "", "idType": "AADHAR"},
            {"idValue": "", "idType": "Form_60"},
        ],
        "address": _build_address_entries(permanent, current),
    }

    return payload
