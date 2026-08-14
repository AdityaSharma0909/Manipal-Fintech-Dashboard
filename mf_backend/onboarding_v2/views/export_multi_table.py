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
    BankBranch,
    PincodeMaster,
)
from onboarding_v2.constants import LeadType
from onboarding_v2.helpers.lead_application_helpers import filter_applications
from utils.responseHandler import HttpResponse

logger = logging.getLogger(__name__)


MULTI_TABLE_REPORT_COLUMNS = [
    "Application ID", "Lead Code", "Loan Account Number",
    "Customer Name", "Branch Name", "Bank Loan Amount",
    "Loan Amount", "User Type", "Regional Manager Name",
    "Lead Generation Date", "Account Open Date", "Dist Name",
    "State Name", "Loan Status", "Client ID",
    "Loan Account Number (Punching)", "Bank Name", "Sol Id",
    "SBO ID", "SBO Name", "CRMID", "Disbursed Amount", "Sanction Amount",
    "Branch ID", "New Bank Name", "New Bank Branch Name", "New Bank Branch's SOL ID",
]


def build_multi_table_export_workbook(qs):
    """
    Build the GL Punching multi-table report workbook for the provided applications queryset.
    """
    qs = qs.select_related("lead", "punched_by", "assigned_rh").prefetch_related(
        "punched_loans",
        "stage_snapshots",
    )

    # -----------------------------------------------------------
    # Pre-fetch lookup tables to avoid N+1 queries
    # -----------------------------------------------------------

    # Collect all pincodes from leads for district/state lookup
    lead_pincodes = set(
        qs.values_list("lead__pincode", flat=True).distinct()
    )
    lead_pincodes.discard(None)
    lead_pincodes.discard("")

    pincode_map = {}
    if lead_pincodes:
        for pm in PincodeMaster.objects.filter(pincode__in=lead_pincodes):
            pincode_map[pm.pincode] = {
                "district": pm.district or "",
                "state": pm.statename or "",
            }

    # Collect all unique bank names from applications and loan punches for Bank Branch lookup
    bank_branch_map = {}

    loan_punches_qs = LoanPunchV2.objects.filter(application_id__in=qs.values_list("id", flat=True))

    all_bank_names = set(qs.values_list("lending_partner", flat=True).distinct())
    all_bank_names.update(loan_punches_qs.values_list("bank_name", flat=True).distinct())
    all_bank_names.update(loan_punches_qs.values_list("new_bank_name", flat=True).distinct())

    all_bank_names.discard(None)
    all_bank_names.discard("")

    if all_bank_names:
        for bb in BankBranch.objects.filter(bank_name__in=all_bank_names):
            b_name = (bb.bank_name or "").strip().upper()
            br_name = (bb.branch_name or "").strip().upper()

            if b_name not in bank_branch_map:
                bank_branch_map[b_name] = {}

            # Keep first match for the generic bank name fallback
            if "" not in bank_branch_map[b_name]:
                bank_branch_map[b_name][""] = bb

            if br_name and br_name not in bank_branch_map[b_name]:
                bank_branch_map[b_name][br_name] = bb

    # -----------------------------------------------------------
    # Build rows
    # -----------------------------------------------------------
    rows = []
    report_items = []
    for app in qs:
        punched_loans = list(app.punched_loans.all())
        if punched_loans:
            report_items.extend((app, loan_punch) for loan_punch in punched_loans)
        else:
            # Keep applications without a punched loan in the report as before.
            report_items.append((app, None))

    for app, loan_punch in report_items:
        lead = app.lead

        # Pincode-based district/state
        lead_pincode = getattr(lead, "pincode", None) or ""
        pincode_info = pincode_map.get(lead_pincode, {})

        # SO user who punched the application
        so_user = app.punched_by

        # Regional Head (assigned_rh)
        rh_user = app.assigned_rh

        # We will calculate SOL ID below after determining branch_name

        # -------------------------------------------------------
        # Branch Name - based on loan type
        #   BT            -> BANK stage  -> branch_name
        #   FRESH         -> LOAN stage  -> bank_branch
        #   CO_LENDING    -> LOAN stage  -> partner_branch_name
        # -------------------------------------------------------
        branch_name = ""
        loan_type = app.loan_type or ""
        snapshots = {
            s.stage: s.payload
            for s in app.stage_snapshots.all()
            if isinstance(s.payload, dict)
        }

        if loan_type == LeadType.BALANCE_TRANSFER:
            bank_payload = snapshots.get("BANK", {})
            branch_name = bank_payload.get("branch_name", "") or ""
        elif loan_type == LeadType.FRESH:
            loan_payload = snapshots.get("LOAN", {})
            branch_name = loan_payload.get("bank_branch", "") or ""
        elif loan_type == LeadType.CO_LENDING:
            branch_name = app.partner_branch_name or ""

        # Retrieve Bank Branch details based on bank and branch name
        sol_id = ""
        branch_id = ""
        lookup_bank_name = (loan_punch.bank_name if loan_punch else app.lending_partner) or ""
        b_name_key = lookup_bank_name.strip().upper()
        br_name_key = branch_name.strip().upper()

        if b_name_key in bank_branch_map:
            bb = bank_branch_map[b_name_key].get(br_name_key) or bank_branch_map[b_name_key].get("")
            if bb:
                sol_id = bb.sol_id or ""
                branch_id = bb.branch_code or ""

        # Details for New Bank
        new_bank_name = ""
        new_bank_branch_name = ""
        new_bank_branch_sol_id = ""

        if loan_punch:
            new_bank_name = loan_punch.new_bank_name or ""
            new_bank_branch_name = loan_punch.new_bank_branch or ""

            nb_name_key = new_bank_name.strip().upper()
            nbr_name_key = new_bank_branch_name.strip().upper()

            if nb_name_key in bank_branch_map:
                nbb = bank_branch_map[nb_name_key].get(nbr_name_key) or bank_branch_map[nb_name_key].get("")
                if nbb:
                    new_bank_branch_sol_id = nbb.sol_id or ""

        row = {
            # Col A - Application ID (ApplicationV2)
            "Application ID": app.application_id or "",

            # Col B - Lead Code (LeadV2)
            "Lead Code": getattr(lead, "lead_code", "") or "",

            # Col C - Loan Account Number (Blank for now)
            "Loan Account Number": "",

            # Col D - Customer Name (LeadV2)
            "Customer Name": getattr(lead, "customer_name", "") or "",

            # Col E - Branch Name (from stage snapshots based on loan type)
            "Branch Name": branch_name,

            # Col F - Bank Loan Amount (Blank for now)
            "Bank Loan Amount": "",

            # Col G - Loan Amount (LeadV2.amount)
            "Loan Amount": str(getattr(lead, "amount", "") or ""),

            # Col H - User Type / Source (LeadV2.source)
            "User Type": getattr(lead, "source", "") or "",

            # Col I - Regional Manager Name (assigned_rh -> User)
            "Regional Manager Name": (
                f"{rh_user.first_name or ''} {rh_user.last_name or ''}".strip()
                if rh_user
                else ""
            ),

            # Col J - Lead Generation Date (LeadV2.created_at)
            "Lead Generation Date": (
                str(lead.created_at.date()) if getattr(lead, "created_at", None) else ""
            ),

            # Col K - Account Open Date (LoanPunchV2.loan_opening_date)
            "Account Open Date": (
                str(loan_punch.loan_opening_date)
                if loan_punch and loan_punch.loan_opening_date
                else ""
            ),

            # Col L - Dist Name (PincodeMaster via LeadV2.pincode)
            "Dist Name": pincode_info.get("district", ""),

            # Col M - State Name (PincodeMaster via LeadV2.pincode)
            "State Name": pincode_info.get("state", ""),

            # Col N - Loan Status (Blank for now)
            "Loan Status": "",

            # Col O - Client ID (LeadV2.customer_id)
            "Client ID": getattr(lead, "customer_id", "") or "",

            # Col P - Loan Account Number from Loan Punching (Field5)
            "Loan Account Number (Punching)": (
                loan_punch.loan_account_number or ""
                if loan_punch
                else ""
            ),

            # Col Q - Bank Name / Lending Partner (ApplicationV2)
            "Bank Name": app.lending_partner or "",

            # Col R - Sol Id (BankBranch.sol_id)
            "Sol Id": sol_id,

            # Col S - SBO ID / SO Employee ID (User.employee_id)
            "SBO ID": (
                so_user.employee_id or ""
                if so_user
                else ""
            ),

            # Col T - SBO Name / SO Name (User)
            "SBO Name": (
                f"{so_user.first_name or ''} {so_user.last_name or ''}".strip()
                if so_user
                else ""
            ),

            # Col U - CRMID (LoanPunchV2.crm_id)
            "CRMID": (
                loan_punch.crm_id or ""
                if loan_punch
                else ""
            ),
            "Disbursed Amount": (
                str(loan_punch.disbursed_amount)
                if loan_punch and loan_punch.disbursed_amount is not None
                else ""
            ),
            "Sanction Amount": (
                str(loan_punch.sanctioned_amount)
                if loan_punch and loan_punch.sanctioned_amount is not None
                else ""
            ),

            "Branch ID": branch_id,
            "New Bank Name": new_bank_name,
            "New Bank Branch Name": new_bank_branch_name,
            "New Bank Branch's SOL ID": new_bank_branch_sol_id,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # If the dataframe is empty, ensure all columns are present
    if df.empty:
        df = pd.DataFrame(columns=MULTI_TABLE_REPORT_COLUMNS)

    # Write to Excel
    excel_buffer = BytesIO()
    writer = pd.ExcelWriter(excel_buffer, engine="openpyxl")
    df.to_excel(writer, sheet_name="GL Punching Report", index=False)
    writer.close()
    excel_buffer.seek(0)

    return excel_buffer, len(rows)


class ExportMultiTableView(APIView):
    """
    Export V2 application data from multiple tables as an Excel (.xlsx) file.

    Columns pulled from: ApplicationV2, LeadV2, LoanPunchV2, BankBranch,
    PincodeMaster, and User tables.

    Supports the same query filters as the ApplicationListView plus optional
    ``start_date`` and ``end_date`` params (YYYY-MM-DD) to filter by
    ``ApplicationV2.created_at``.
    """

    def get(self, request):
        try:
            qs = (
                filter_applications(request.user, request.query_params)
                .select_related("lead", "punched_by", "assigned_rh")
                .prefetch_related("punched_loans", "stage_snapshots")
            )

            # Optional date range filter
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)

            excel_buffer, _ = build_multi_table_export_workbook(qs)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = (
                "attachment; filename=GL_Punching_Report.xlsx"
            )
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export multi-table applications failed")
            return HttpResponse.InternalServerError(str(e))
