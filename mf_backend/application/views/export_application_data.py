import traceback
import pandas as pd
from io import BytesIO as IO  # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from application.services.export_application_data import ExportApplicationService


class ExportApplicationView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        try:

            user = request.user
            if user.role == ROLES.LOAN_OFFICER.value:
                return HttpResponse.Forbidden("Not Allowed")

            output = ExportApplicationService().get_application_data(
                query_options=request.query_params
            )

            # df_output = pd.DataFrame(output)
            df_output = pd.DataFrame(
                output,
                columns=[
                    "Name",
                    "Customer ID",
                    "Loan Number",
                    "Email",
                    "Gender",
                    "DOB",
                    "Contact Number",
                    "Address",
                    "Occupation",
                    "Net Annual Income",
                    "Aadhar No",
                    "PAN",
                    "Mother's Name",
                    "Father's Name",
                    "Spouse's Name",
                    "Education",
                    "Religion",
                    "Nationality",
                    "Caste",
                    "Bank Name",
                    "Account Number",
                    "IFSC code",
                    "Account Holder Name",
                    "Branch Code",
                    "Branch Name",
                    "Branch State",
                    "Status",
                    "Application number",
                    "Purpose of loan",
                    "Loan amount",
                    "Contra loan amount",
                    "Product name",
                    "Lender name",
                    "White goods",
                    "Total goods price",
                    "Total Gross Weight",
                    "Total Wastage",
                    "Total Net weight",
                    "Application type",
                    "Insurance Product Name",
                    "Insurance Coverage",
                    "Insurance Premium",
                    "Takeover Lender Name",
                    "Takeover Loan Amount",
                    "Takeover Requested Amount",
                    "Takeover Total Release Amount",
                    "Takeover Loan Start Date",
                    "Takeover Maturity Date",
                    "Takeover Loan Reference Number",
                    "Takeover Gold Weight Pledged",
                    "EMI Start Date",
                    "Loan Maturity Date",
                    "Originated by name",
                    "Appraised by name",
                    "Nominee Name",
                    "Nominee Age",
                    "Nominee Relation",
                    "Nominee Contact",
                    "Tenure",
                    "Intrest rate",
                    "Processing fee",
                    "Processing fee percent",
                    "Amortization type",
                    "Penalty",
                    "GST",
                    "Stamp duty",
                    "Ltv",
                    "Gold rate(per gram)",
                    "Disbursal Amount",
                    "Disbursed date",
                    "Created At",
                ],
            )

            columns_to_fill_with_zero = [
                "Loan amount",
                "Tenure",
                "Contra loan amount",
                "Total goods price",
                "Gold rate(per gram)",
                "Ltv",
                "Stamp duty",
                "Intrest rate",
                "Processing fee",
                "Penalty",
                "Disbursal Amount",
                "GST",
            ]
            df_output[columns_to_fill_with_zero] = (
                df_output[columns_to_fill_with_zero].fillna(0).astype(int)
            )
            df_output[columns_to_fill_with_zero] = (
                df_output[columns_to_fill_with_zero].replace("", 0).astype(int)
            )

            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine="openpyxl")
            df_output.to_excel(xlwriter, "Applications Report", index=False)
            # xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(
                excel_file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            response["Content-Disposition"] = (
                "attachment; filename=Application_Data.xlsx"
            )

            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
