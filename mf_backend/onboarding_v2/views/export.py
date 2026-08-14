import logging
import traceback

import pandas as pd
from io import BytesIO
from django.http import HttpResponse as DjangoHttpResponse
from rest_framework.views import APIView

from onboarding_v2.models import ApplicationV2, ApplicationStageSnapshot
from onboarding_v2.helpers.lead_application_helpers import filter_applications
from utils.responseHandler import HttpResponse

logger = logging.getLogger(__name__)


class ExportApplicationV2View(APIView):
    """
    Export V2 application data as an Excel (.xlsx) file.
    Supports the same query filters as the ApplicationListView.
    """

    def get(self, request):
        try:
            qs = (
                filter_applications(request.user, request.query_params)
                .select_related("lead")
                .prefetch_related("stage_snapshots", "bank_details")
            )

            rows = []
            for app in qs:
                lead = app.lead

                # Gather stage snapshot payloads
                snapshots = {s.stage: s.payload for s in app.stage_snapshots.all() if isinstance(s.payload, dict)}
                pan = snapshots.get("PAN", {})
                basic = snapshots.get("BASIC", {})
                address_payload = snapshots.get("ADDRESS", {})
                loan = snapshots.get("LOAN", {})
                selfie = snapshots.get("SELFIE", {})

                # Address
                permanent = address_payload.get("permanent", {}) if isinstance(address_payload.get("permanent"), dict) else {}
                current = address_payload.get("current", {}) if isinstance(address_payload.get("current"), dict) else {}

                # Bank details
                bank = app.bank_details.first()

                row = {
                    "Application ID": app.application_id,
                    "Name": getattr(lead, "customer_name", ""),
                    "Customer ID": getattr(lead, "customer_id", ""),
                    "Lead Code": getattr(lead, "lead_code", ""),
                    "Email": getattr(lead, "email_address", ""),
                    "Phone No": getattr(lead, "contact_number", ""),
                    "Gender": getattr(lead, "gender", "") or basic.get("gender", ""),
                    "DOB": str(getattr(lead, "dob", "") or "") or basic.get("dob", ""),
                    "DOB From PAN": pan.get("dob_as_per_pan", "") or pan.get("dob", ""),
                    "PAN Number": pan.get("pan_number", "") or getattr(lead, "pan_number", ""),
                    "Name On PAN": pan.get("name_on_pan", ""),
                    "Alternate No": basic.get("alternate_number", "") or basic.get("alternate_no", ""),
                    "Father Name": basic.get("father_name", "") or basic.get("fathers_name", ""),
                    "Mother Name": basic.get("mother_name", "") or basic.get("mothers_name", ""),
                    "Marital Status": basic.get("marital_status", ""),
                    "Profession": basic.get("profession", "") or getattr(app, "applicant_profession", ""),
                    "Occupation": basic.get("occupation", "") or getattr(app, "occupation", ""),
                    "Income Source": basic.get("income_source", "") or getattr(app, "income_source", ""),
                    "Annual Income": basic.get("annual_income", "") or basic.get("annual_income_family", ""),
                    "Net Income Per Month": basic.get("net_income_per_month", "") or basic.get("monthly_income", ""),
                    "Net Worth": basic.get("net_worth", ""),
                    "Religion": basic.get("religion", ""),
                    "Category": basic.get("category", "") or getattr(app, "caste", ""),
                    "Place Of Birth": basic.get("place_of_birth", ""),
                    "Permanent Address": permanent.get("address_line1", ""),
                    "Permanent Pincode": permanent.get("pincode", ""),
                    "Permanent State": permanent.get("state", ""),
                    "Permanent District": permanent.get("district", ""),
                    "Current Address": current.get("address_line1", ""),
                    "Current Pincode": current.get("pincode", ""),
                    "Current State": current.get("state", ""),
                    "Current District": current.get("district", ""),
                    "Bank Name": getattr(bank, "bank_name", "") if bank else "",
                    "Account Number": getattr(bank, "account_number", "") if bank else "",
                    "IFSC Code": getattr(bank, "ifsc_code", "") if bank else "",
                    "Branch Name": getattr(bank, "branch_name", "") if bank else "",
                    "Lending Partner": app.lending_partner or "",
                    "Loan Type": app.loan_type or "",
                    "Requested Amount": str(getattr(lead, "amount", "") or ""),
                    "Loan Amount": loan.get("loan_amount", "") or loan.get("requested_amount", ""),
                    "Tenure": loan.get("tenure", ""),
                    "Interest Rate": loan.get("interest_rate", "") or loan.get("roi", ""),
                    "Processing Fee": str(app.processing_fee or ""),
                    "Status": app.status or "",
                    "Stage": app.stage or "",
                    "Bureau Score": app.bureau_score or "",
                    "Bureau Decision": app.bureau_decision or "",
                    "VAN Number": app.van_number or "",
                    "Lead Added On": str(getattr(lead, "created_at", "")),
                    "Application Created At": str(app.created_at),
                    "Last Modified At": str(app.modified_at),
                }
                rows.append(row)

            df = pd.DataFrame(rows)

            # Write to Excel
            excel_buffer = BytesIO()
            writer = pd.ExcelWriter(excel_buffer, engine="openpyxl")
            df.to_excel(writer, sheet_name="V2 Applications Report", index=False)
            writer.close()
            excel_buffer.seek(0)

            response = DjangoHttpResponse(
                excel_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = "attachment; filename=V2_Application_Data.xlsx"
            return response

        except Exception as e:
            traceback.print_exc()
            logger.exception("Export V2 applications failed")
            return HttpResponse.InternalServerError(str(e))
