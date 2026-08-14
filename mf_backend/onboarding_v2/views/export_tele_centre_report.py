import logging
import traceback
import datetime
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse as DjangoHttpResponse
from rest_framework.views import APIView

from onboarding_v2.models import (
    ApplicationV2,
    ApplicationStageSnapshot,
    LoanPunchV2,
    PincodeMaster,
    BankBranch,
)
from onboarding_v2.constants import (
    LeadType,
    LendingPartner,
    LeadSource,
    Gender,
    Profession,
    Qualification,
    LoanPurpose,
)
from onboarding_v2.helpers.lead_application_helpers import filter_applications
from utils.responseHandler import HttpResponse

logger = logging.getLogger(__name__)

# ── Header ordering for Tele Centre Report ──────────────────────────────
COLUMN_ORDER = [
    "Application ID",
    "Customer ID",
    "Loan Type",
    "Bank Name",
    "Loan Amount",
    "Loan Account Number",
    "ROI",
    "Customer Name",
    "Customer Mobile Number",
    "Customer Profession",
    "Customer Qualification",
    "Loan Purpose",
    "Lead source",
    "SO Name",
    "Loan Date",
    "District",
    "State",
    "Zone",
    "Pin Code",
    "Customer Gender",
    "Branch Name",
    "Bank Sol ID",
    "Customer DOB",
    "Customer Father Name",
    "SBO ID",
    "Lead Punching Date",
]


def _choice_label(value, choices_cls):
    if not value:
        return ""
    try:
        return choices_cls(value).label
    except Exception:
        try:
            return getattr(choices_cls, str(value)).label
        except Exception:
            return str(value)


def load_zone_map():
    """
    Loads state-to-zone mappings from sheet 2 of 'Tele centre report.xlsx'.
    Falls back to a static list if the spreadsheet is not found or fails to read.
    """
    state_to_zone = {}

    static_map = {
        "andaman and nicobar island": "South",
        "andaman and nicobar islands": "South",
        "andhra pradesh": "South",
        "arunachal pradesh": "East",
        "assam": "East",
        "bihar": "North",
        "chandigarh": "North",
        "chhattisgarh": "North",
        "dadra and nagar haveli": "West",
        "daman and diu": "West",
        "delhi": "North",
        "goa": "West",
        "gujarat": "West",
        "haryana": "North",
        "himachal pradesh": "North",
        "jammu and kashmir": "North",
        "jharkhand": "North",
        "karnataka": "South",
        "kerala": "South",
        "lakshadweep": "South",
        "madhya pradesh": "North",
        "maharashtra": "West",
        "manipur": "East",
        "meghalaya": "East",
        "mizoram": "East",
        "odisha": "East",
        "puducherry": "South",
        "punjab": "North",
        "rajasthan": "West",
        "sikkim": "East",
        "tamil nadu": "South",
        "telangana": "South",
        "tripura": "East",
        "uttar pradesh": "North",
        "uttarakhand": "North",
        "west bengal": "East",
        "nagaland": "East",
    }

    try:
        import os
        file_path = os.path.join(settings.BASE_DIR, "Tele centre report.xlsx")
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name="zone details")
            for _, row in df.iterrows():
                state_name = str(row.get("State_Name", "")).strip().lower()
                zone = str(row.get("ZoneName", "")).strip()
                if state_name and zone:
                    state_to_zone[state_name] = zone
    except Exception as e:
        logger.warning("Could not parse zone details sheet: %s", str(e))

    # Merge static map to guarantee coverage
    for k, v in static_map.items():
        if k not in state_to_zone:
            state_to_zone[k] = v

    return state_to_zone


def build_tele_centre_report_workbook(loan_punches_qs):
    """
    Builds the Tele Centre report Excel workbook based on the provided LoanPunchV2 queryset.
    """
    # Evaluate queryset to list to handle sliced querysets safely
    loan_punches_list = list(loan_punches_qs)

    # ── Pre-fetch lookup details to optimize performance ─────────────────
    app_ids = [lp.application_id for lp in loan_punches_list if lp.application_id]
    applications = ApplicationV2.objects.filter(id__in=app_ids).select_related(
        "lead", "lead__created_by"
    ).prefetch_related("stage_snapshots")

    app_map = {app.id: app for app in applications}

    # Collect lead pincodes for Pincode Master lookup
    lead_pincodes = set()
    for app in app_map.values():
        if app.lead and app.lead.pincode:
            lead_pincodes.add(app.lead.pincode)
    lead_pincodes.discard(None)
    lead_pincodes.discard("")

    pincode_map = {}
    if lead_pincodes:
        for pm in PincodeMaster.objects.filter(pincode__in=lead_pincodes):
            pincode_map[pm.pincode] = {
                "district": pm.district or "",
                "state": pm.statename or "",
            }

    # Collect bank and branch names for BankBranch mapping
    bank_branch_map = {}
    all_bank_names = set()
    for lp in loan_punches_list:
        if lp.bank_name:
            all_bank_names.add(lp.bank_name)
        if lp.new_bank_name:
            all_bank_names.add(lp.new_bank_name)
    for app in app_map.values():
        if app.lending_partner:
            all_bank_names.add(app.lending_partner)
    all_bank_names.discard(None)
    all_bank_names.discard("")

    if all_bank_names:
        for bb in BankBranch.objects.filter(bank_name__in=all_bank_names):
            b_name = (bb.bank_name or "").strip().upper()
            br_name = (bb.branch_name or "").strip().upper()

            if b_name not in bank_branch_map:
                bank_branch_map[b_name] = {}

            if "" not in bank_branch_map[b_name]:
                bank_branch_map[b_name][""] = bb

            if br_name and br_name not in bank_branch_map[b_name]:
                bank_branch_map[b_name][br_name] = bb

    # Load zone map
    state_to_zone = load_zone_map()

    # ── Compile Row Data ─────────────────────────────────────────────────
    rows = []
    for lp in loan_punches_list:
        app = app_map.get(lp.application_id)
        if not app:
            continue

        lead = app.lead
        so_user = getattr(lead, "created_by", None) if lead else None

        # Resolve stage snapshots
        snapshots = {s.stage: s.payload for s in app.stage_snapshots.all() if isinstance(s.payload, dict)}
        basic = snapshots.get("BASIC", {})
        address_payload = snapshots.get("ADDRESS", {})
        loan_payload = snapshots.get("LOAN", {})

        permanent = address_payload.get("permanent", {}) if isinstance(address_payload.get("permanent"), dict) else {}

        # ── Address resolution (District, State, Pincode) ───────────────────
        pincode = lead.pincode if (lead and lead.pincode) else ""
        district = ""
        state = ""

        if pincode and pincode in pincode_map:
            district = pincode_map[pincode].get("district", "")
            state = pincode_map[pincode].get("state", "")

        # ── Zone resolution ──────────────────────────────────────────────────
        zone = ""
        if state:
            zone = state_to_zone.get(str(state).strip().lower(), "")

        # ── Branch and SOL ID resolution ─────────────────────────────────────
        branch_name = loan_payload.get("bank_branch", "") or app.partner_branch_name or ""
        bank_name = lp.bank_name or app.lending_partner or ""
        sol_id = ""

        b_name_key = bank_name.strip().upper()
        br_name_key = branch_name.strip().upper()

        if b_name_key in bank_branch_map:
            bb = bank_branch_map[b_name_key].get(br_name_key) or bank_branch_map[b_name_key].get("")
            if bb:
                sol_id = bb.sol_id or ""

        # ── Date formatting ──────────────────────────────────────────────────
        loan_date_str = ""
        if lp.loan_opening_date:
            loan_date_str = str(lp.loan_opening_date)

        dob_str = ""
        dob_val = basic.get("dob") or (lead and lead.dob) or ""
        if dob_val:
            dob_str = str(dob_val)

        punch_date_str = ""
        if lp.created_at:
            punch_date_str = timezone.localtime(lp.created_at).strftime("%Y-%m-%d %H:%M:%S")

        # ── SBO & SO Names ───────────────────────────────────────────────────
        so_name = ""
        sbo_id = ""
        if so_user:
            so_name = f"{so_user.first_name or ''} {so_user.last_name or ''}".strip()
            sbo_id = so_user.employee_id or ""

        row = {
            "Application ID": app.application_id,
            "Customer ID": getattr(lead, "customer_id", "") if lead else "",
            "Loan Type": _choice_label(getattr(lead, "lead_type", "") if lead else app.loan_type, LeadType),
            "Bank Name": _choice_label(bank_name, LendingPartner),
            "Loan Amount": lp.disbursed_amount or lp.sanctioned_amount or 0,
            "Loan Account Number": lp.loan_account_number or "",
            "ROI": lp.rate_of_interest or 0,
            "Customer Name": getattr(lead, "customer_name", "") if lead else "",
            "Customer Mobile Number": getattr(lead, "contact_number", "") if lead else "",
            "Customer Profession": _choice_label(basic.get("profession") or app.applicant_profession, Profession),
            "Customer Qualification": _choice_label(basic.get("qualification"), Qualification),
            "Loan Purpose": _choice_label(loan_payload.get("purpose"), LoanPurpose),
            "Lead source": _choice_label(getattr(lead, "source", "") if lead else "", LeadSource),
            "SO Name": so_name,
            "Loan Date": loan_date_str,
            "District": district,
            "State": state,
            "Zone": zone,
            "Pin Code": pincode,
            "Customer Gender": _choice_label((lead and lead.gender) or basic.get("gender") or "", Gender),
            "Branch Name": branch_name,
            "Bank Sol ID": sol_id,
            "Customer DOB": dob_str,
            "Customer Father Name": basic.get("father_full_name") or basic.get("father_name") or basic.get("fathers_name") or "",
            "SBO ID": sbo_id,
            "Lead Punching Date": punch_date_str,
        }
        rows.append(row)

    # Build DataFrame
    if rows:
        df = pd.DataFrame(rows, columns=COLUMN_ORDER)
    else:
        df = pd.DataFrame(columns=COLUMN_ORDER)

    # Write to Excel
    excel_buffer = BytesIO()
    writer = pd.ExcelWriter(excel_buffer, engine="openpyxl")
    df.to_excel(writer, sheet_name="Customer Details For Tele", index=False)
    writer.close()
    excel_buffer.seek(0)
    return excel_buffer, len(rows)


class ExportTeleCentreReportView(APIView):
    """
    Exposes GET /onboarding_v2/applications/export/tele-centre-report/
    Exports tele centre report matching columns based on query params start_date & end_date.
    Defaults to yesterday's date range.
    """

    def get(self, request):
        try:
            # 1. Base queryset filtering based on roles
            app_qs = filter_applications(request.user, request.query_params)

            # 2. Extract date range (YYYY-MM-DD)
            start_date_str = request.query_params.get("start_date")
            end_date_str = request.query_params.get("end_date")

            if start_date_str and end_date_str:
                try:
                    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                except ValueError:
                    return HttpResponse.BadRequest("Invalid date format. Use YYYY-MM-DD")
            else:
                # Default to yesterday
                yesterday = timezone.localtime(timezone.now()).date() - datetime.timedelta(days=1)
                start_date = yesterday
                end_date = yesterday

            # Combine with local day start and end time
            start_dt = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
            end_dt = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))

            # Query LoanPunchV2 records punched within range that belong to accessible applications
            loan_punches = (
                LoanPunchV2.objects.filter(
                    application__in=app_qs,
                    created_at__range=(start_dt, end_dt)
                )
                .order_by("-created_at")
            )

            excel_buffer, total_count = build_tele_centre_report_workbook(loan_punches)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = f"attachment; filename=Customer_Details_For_Tele_{start_date}_to_{end_date}.xlsx"
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export Tele Centre report failed")
            return HttpResponse.InternalServerError(str(e))
