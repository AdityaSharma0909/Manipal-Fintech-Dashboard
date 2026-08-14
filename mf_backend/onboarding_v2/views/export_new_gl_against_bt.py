import logging
import traceback

import pandas as pd
from io import BytesIO
from django.http import HttpResponse as DjangoHttpResponse
from rest_framework.views import APIView

from onboarding_v2.models import (
    ApplicationV2,
    PincodeMaster,
)
from onboarding_v2.constants import LeadType
from onboarding_v2.helpers.lead_application_helpers import filter_applications
from utils.responseHandler import HttpResponse

logger = logging.getLogger(__name__)


# ── Column order for the New GL against BT Report ────────────────────────────
COLUMN_ORDER = [
    "Month",
    "FLID",
    "Customer Name",
    "New Loan A/C",
    "New Loan Amount",
    "New Loan Open Date",
    "State",
    "RH",
    "ZH",
    "SBO",
    "Exiting Bank",
    "New Bank",
]


def build_new_gl_against_bt_report_workbook(qs):
    # ── Pre-fetch pincode → state lookup ───────────────────────
    lead_pincodes = set(
        qs.values_list("lead__pincode", flat=True).distinct()
    )
    lead_pincodes.discard(None)
    lead_pincodes.discard("")

    pincode_state_map = {}
    if lead_pincodes:
        for pm in PincodeMaster.objects.filter(pincode__in=lead_pincodes):
            pincode_state_map[pm.pincode] = pm.statename or ""

    # ── Build rows ─────────────────────────────────────────────
    rows = []
    for app in qs:
        lead = app.lead

        # Stage snapshots keyed by stage name
        snapshots = {
            s.stage: s.payload
            for s in app.stage_snapshots.all()
            if isinstance(s.payload, (dict, list))
        }

        # Latest loan punch for this application
        loan_punch = None
        punched_loans = list(app.punched_loans.all())
        if punched_loans:
            loan_punch = max(punched_loans, key=lambda lp: lp.created_at)

        exiting_bank = ""
        new_bank = ""
        if loan_punch:
            exiting_bank = loan_punch.bank_name or ""
            new_bank = loan_punch.new_bank_name or ""

        # ── State from PincodeMaster ───────────────────────────
        lead_pincode = getattr(lead, "pincode", None) or ""
        state_name = pincode_state_map.get(lead_pincode, "")

        # ── SO (SBO Name) details from lead.created_by ───────
        so_user = getattr(lead, "created_by", None)
        so_name = ""
        if so_user:
            so_name = f"{so_user.first_name or ''} {so_user.last_name or ''}".strip()

        # ── RH (assigned_rh) details ───────────────────────────
        rh_user = app.assigned_rh
        rh_name = ""
        zh_name = ""
        if rh_user:
            rh_name = f"{rh_user.first_name or ''} {rh_user.last_name or ''}".strip()
            zh_user = getattr(rh_user, "manager", None) or getattr(rh_user, "reporting_manager", None)
            if zh_user:
                zh_name = f"{zh_user.first_name or ''} {zh_user.last_name or ''}".strip()

        # ── Loan details ───────────────────────────
        punching_month = ""
        loan_account_number = ""
        loan_amount = ""
        loan_open_date = ""

        if loan_punch:
            if loan_punch.created_at:
                punching_month = loan_punch.created_at.strftime("%B")  # Full month name (e.g. July)
            loan_account_number = loan_punch.loan_account_number or ""
            loan_amount = str(loan_punch.sanctioned_amount) if loan_punch.sanctioned_amount is not None else ""
            loan_open_date = str(loan_punch.loan_opening_date) if loan_punch.loan_opening_date else ""

        row = {
            "Month": punching_month,
            "FLID": app.application_id or "",
            "Customer Name": getattr(lead, "customer_name", "") or "",
            "New Loan A/C": loan_account_number,
            "New Loan Amount": loan_amount,
            "New Loan Open Date": loan_open_date,
            "State": state_name,
            "RH": rh_name,
            "ZH": zh_name,
            "SBO": so_name,
            "Exiting Bank": exiting_bank,
            "New Bank": new_bank,
        }
        rows.append(row)

    # ── Build DataFrame with fixed column order ────────────────
    if rows:
        df = pd.DataFrame(rows, columns=COLUMN_ORDER)
    else:
        df = pd.DataFrame(columns=COLUMN_ORDER)

    # ── Write to Excel ─────────────────────────────────────────
    excel_buffer = BytesIO()
    writer = pd.ExcelWriter(excel_buffer, engine="openpyxl")
    df.to_excel(writer, sheet_name="New GL against BT", index=False)
    writer.close()
    excel_buffer.seek(0)
    return excel_buffer, len(rows)


class ExportNewGLAgainstBTReportView(APIView):
    """
    Export New GL against BT Report as an Excel (.xlsx) file.
    """

    def get(self, request):
        try:
            # ── Base queryset: only BALANCE_TRANSFER applications ──────
            qs = (
                filter_applications(request.user, request.query_params)
                .filter(loan_type=LeadType.BALANCE_TRANSFER)
                .select_related(
                    "lead",
                    "lead__created_by",
                    "punched_by",
                    "assigned_rh",
                )
                .prefetch_related("punched_loans", "stage_snapshots")
            )

            # Optional date range filter
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)

            excel_buffer, _ = build_new_gl_against_bt_report_workbook(qs)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = (
                "attachment; filename=New_GL_against_BT_Report.xlsx"
            )
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export New GL against BT Report failed")
            return HttpResponse.InternalServerError(str(e))
