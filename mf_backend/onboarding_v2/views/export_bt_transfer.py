import logging
import traceback

import pandas as pd
from io import BytesIO
from django.http import HttpResponse as DjangoHttpResponse
from rest_framework.views import APIView

from onboarding_v2.models import (
    ApplicationV2,
    ApplicationStageSnapshot,
    LoanPunchV2,
    PincodeMaster,
)
from onboarding_v2.constants import LeadType
from onboarding_v2.helpers.lead_application_helpers import filter_applications
from utils.responseHandler import HttpResponse

logger = logging.getLogger(__name__)


# ── Column order for the BT-Transfer Report ────────────────────────────
COLUMN_ORDER = [
    "Application ID",
    "Lead ID",
    "Create Date",
    "Full Name",
    "Mobile Number",
    "Account Number",
    "IFSC Code",
    "State Name",
    "Balance Transfer Amount",
    "Fore Closure Amount",
    "Created By",
    "Agent",
    "RM",
    "PM",
    "BTReturn Amount",
    "From Bank",
    "Status",
    "Loan Amount",
    "Lead Account Open Date",
    "Loan Account Number",
    "Loan Status",
]


class ExportBTTransferReportView(APIView):
    """
    Export BT-Transfer Report as an Excel (.xlsx) file.

    This report is **only** applicable for applications where
    lead_type = BALANCE_TRANSFER.

    Data is pulled from multiple tables:
      - ApplicationV2
      - LeadV2 (via application.lead)
      - ApplicationStageSnapshot (DOCUMENTS, PLEDGE_CARD, LOAN stages)
      - LoanPunchV2
      - PincodeMaster (state lookup via lead pincode)
      - User (SO / RH details)

    Supports the same query filters as the ApplicationListView plus optional
    ``start_date`` and ``end_date`` params (YYYY-MM-DD) to filter by
    ``ApplicationV2.created_at``.
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
                    if isinstance(s.payload, dict)
                }

                # Latest loan punch for this application
                loan_punch = None
                punched_loans = list(app.punched_loans.all())
                if punched_loans:
                    loan_punch = max(punched_loans, key=lambda lp: lp.created_at)

                # ── Extract from DOCUMENTS stage snapshot ──────────────
                # Documents >> Payload >> Cheque primary >> Account Number / IFSC
                docs_payload = snapshots.get("DOCUMENTS", {})
                cheque_primary = docs_payload.get("cheque_primary", {}) or {}
                if not isinstance(cheque_primary, dict):
                    cheque_primary = {}
                account_number = cheque_primary.get("account_number", "") or ""
                ifsc_code = cheque_primary.get("ifsc", "") or ""

                # ── Extract from LOAN stage snapshot ───────────────────
                # Loan stage >> Payload >> Requested Amount
                loan_payload = snapshots.get("LOAN", {})
                bt_amount = loan_payload.get("requested_amount", "") or ""

                # ── Extract from PLEDGE_CARD stage snapshot ────────────
                # Pledge card >> lender  (could be list → comma-separated)
                pledge_payload = snapshots.get("PLEDGE_CARD", {})
                lender_raw = pledge_payload.get("lender", "") or ""
                if isinstance(lender_raw, list):
                    from_bank = ", ".join(str(l) for l in lender_raw if l)
                else:
                    from_bank = str(lender_raw)

                # ── State from PincodeMaster ───────────────────────────
                lead_pincode = getattr(lead, "pincode", None) or ""
                state_name = pincode_state_map.get(lead_pincode, "")

                # ── SO (Created By) details from lead.created_by ───────
                so_user = getattr(lead, "created_by", None)
                so_employee_id = ""
                so_name = ""
                if so_user:
                    so_employee_id = getattr(so_user, "employee_id", "") or ""
                    so_name = (
                        f"{so_user.first_name or ''} {so_user.last_name or ''}".strip()
                    )

                # ── RH (assigned_rh) details ───────────────────────────
                rh_user = app.assigned_rh
                rh_name = ""
                if rh_user:
                    rh_name = (
                        f"{rh_user.first_name or ''} {rh_user.last_name or ''}".strip()
                    )

                row = {
                    "Application ID": app.application_id or "",
                    "Lead ID": getattr(lead, "lead_code", "") or "",
                    "Create Date": (
                        str(app.created_at.date()) if app.created_at else ""
                    ),
                    "Full Name": getattr(lead, "customer_name", "") or "",
                    "Mobile Number": getattr(lead, "contact_number", "") or "",
                    "Account Number": account_number,
                    "IFSC Code": ifsc_code,
                    "State Name": state_name,
                    "Balance Transfer Amount": str(bt_amount) if bt_amount else "",
                    "Fore Closure Amount": "",          # NA – no data source
                    "Created By": so_employee_id,
                    "Agent": so_name,
                    "RM": rh_name,
                    "PM": app.lending_partner or "",
                    "BTReturn Amount": "",              # ??? – pending clarification
                    "From Bank": from_bank,
                    "Status": app.status or "",
                    "Loan Amount": (
                        str(loan_punch.sanctioned_amount)
                        if loan_punch and loan_punch.sanctioned_amount is not None
                        else ""
                    ),
                    "Lead Account Open Date": (
                        str(loan_punch.loan_opening_date)
                        if loan_punch and loan_punch.loan_opening_date
                        else ""
                    ),
                    "Loan Account Number": (
                        loan_punch.loan_account_number or ""
                        if loan_punch
                        else ""
                    ),
                    "Loan Status": "",                  # NA – no data source
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
            df.to_excel(writer, sheet_name="BT Transfer Report", index=False)
            writer.close()
            excel_buffer.seek(0)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = (
                "attachment; filename=BT_Transfer_Report.xlsx"
            )
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export BT Transfer Report failed")
            return HttpResponse.InternalServerError(str(e))
