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


# ── Column order for the BT-Disbursal Report ────────────────────────────
COLUMN_ORDER = [
    "Debit Bank",
    "FLID",
    "Customer-Contact No",
    "Customer Name",
    "Beneficiary Name",
    "BT Sanction Amount",
    "BT Disbursal Amount",
    "Platform Fees+ PF-Non Bajaj",
    "Platform Fees+ PF-In Case of Bajaj Finserv",
    "Waiver %",
    "Posting Date (Disburse)",
    "Customer-Account No",
    "IFSC Code",
    "Payment Mode",
    "Disburse Timing",
    "ZH Name",
    "RH Name",
    "SBO Name",
    "State",
    "Type of BT",
    "Time of BT",
    "Exiting Bank",
    "New Bank",
    "VAN Number",
]


def build_bt_disbursal_report_workbook(qs):
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

        # ── Extract from DOCUMENTS stage snapshot ──────────────
        docs_payload = snapshots.get("DOCUMENTS", [])
        account_number = ""
        ifsc_code = ""
        if isinstance(docs_payload, list):
            for d in docs_payload:
                if isinstance(d, dict) and d.get("document_type") == "OTHER" and d.get("subtype") == "CHEQUE_PRIMARY":
                    metadata = d.get("metadata", {})
                    if isinstance(metadata, dict):
                        account_number = metadata.get("account_number", "") or ""
                        ifsc_code = metadata.get("IFSC_code", "") or ""
                    break

        # ── Extract from LOAN stage snapshot ───────────────────
        loan_payload = snapshots.get("LOAN", {})
        type_of_bt = loan_payload.get("bt_category", "") or ""

        # ── Extract from PLEDGE_CARD stage snapshot ────────────
        pledge_payload = snapshots.get("PLEDGE_CARD", {})
        from_bank = ""
        if isinstance(pledge_payload, dict):
            pledge_cards = pledge_payload.get("pledge_cards", [])
            if isinstance(pledge_cards, list):
                lenders = []
                for card in pledge_cards:
                    if isinstance(card, dict):
                        lender_val = card.get("lender")
                        if lender_val:
                            lenders.append(str(lender_val))
                from_bank = ", ".join(lenders)

        # ── State from PincodeMaster ───────────────────────────
        lead_pincode = getattr(lead, "pincode", None) or ""
        state_name = pincode_state_map.get(lead_pincode, "")

        # ── SO (Created By) details from lead.created_by ───────
        so_user = getattr(lead, "created_by", None)
        so_name = ""
        if so_user:
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

        # ── ZH details (manager of RH if available) ────────────
        zh_name = ""
        if rh_user and hasattr(rh_user, 'manager') and rh_user.manager:
            zh_user = rh_user.manager
            zh_name = f"{zh_user.first_name or ''} {zh_user.last_name or ''}".strip()

        row = {
            "Debit Bank": "",  # Sastech
            "FLID": app.application_id or "",  # 2nd field is Application ID as per instruction
            "Customer-Contact No": getattr(lead, "contact_number", "") or "",
            "Customer Name": getattr(lead, "customer_name", "") or "",
            "Beneficiary Name": "",  # Sastech
            "BT Sanction Amount": "",  # Sastech
            "BT Disbursal Amount": "",  # Sastech
            "Platform Fees+ PF-Non Bajaj": "",  # Sastech
            "Platform Fees+ PF-In Case of Bajaj Finserv": "",  # Sastech
            "Waiver %": "",  # Sastech
            "Posting Date (Disburse)": "",  # Sastech
            "Customer-Account No": account_number,
            "IFSC Code": ifsc_code,
            "Payment Mode": "",
            "Disburse Timing": "",
            "ZH Name": zh_name,
            "RH Name": rh_name,
            "SBO Name": so_name,
            "State": state_name,
            "Type of BT": type_of_bt,
            "Time of BT": "",  # Sastech
            "Exiting Bank": from_bank,
            "New Bank": app.lending_partner or "",
            "VAN Number": app.van_number or "",
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
    df.to_excel(writer, sheet_name="BT Disbursal Report", index=False)
    writer.close()
    excel_buffer.seek(0)
    return excel_buffer, len(rows)


class ExportBTDisbursalReportView(APIView):
    """
    Export BT-Disbursal Report as an Excel (.xlsx) file.
    Fields labeled 'Sastech' in specifications are left empty.
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

            excel_buffer, _ = build_bt_disbursal_report_workbook(qs)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = (
                "attachment; filename=BT_Disbursal_Report.xlsx"
            )
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export BT Disbursal Report failed")
            return HttpResponse.InternalServerError(str(e))
