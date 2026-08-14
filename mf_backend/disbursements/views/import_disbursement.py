import pandas as pd
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from disbursements.models import Disbursement

class ExcelImportView(APIView):
    def post(self, request):
        try:
            excel_file = request.data['file']
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.lower()

            result = []
            for index, row in df.iterrows():

                remark = row['remark']
                disbursement_id = remark.split('_')[-1]

                disbursement = Disbursement.objects.get(disbursement_id__iexact=disbursement_id)

                disbursement_data = {
                    "disbursement_id": disbursement.disbursement_id,
                    "beneficiary_ac_no": row['beneficiary ac no'],
                    "beneficiary_name": row['beneficiary name'],
                    "ifsc": row['ifsc'],
                    "amount": row['amount'],
                    "lender": row['lender'],
                    "application_number": disbursement.application.application_number,
                    "request_for": row['request for'],
                    "utr_no": row['utr no'],
                    "modified_at": row['last update']
                }
                result.append(disbursement_data)

            return HttpResponse.Success(result)
        except Disbursement.DoesNotExist:
            return HttpResponse.BadRequest("Disbursement not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
