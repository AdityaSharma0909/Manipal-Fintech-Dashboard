import datetime
import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from disbursements.service.export_disbusrement_data import ExportDisbursementService


class ExportDisbursementView(APIView):


    def get(self, request):
        try:
            user = request.user
            if user.role != ROLES.CPC.value:
                return HttpResponse.Forbidden("Not Allowed")
            output = ExportDisbursementService().exportDisbursement(request)
            if output is None:
                return HttpResponse.BadRequest({"message":"No disbursement IDs provided"})
            df_output = pd.DataFrame(output, columns=['Debit Ac No' , 'Beneficiary Ac No' , 'Beneficiary Name' , 
                                                      'Amount' , 'Payment Mode (N-NEFT,R-RTGS)' , 'IFSC' , 'Lender' ,
                                                      'Request For' , 'Remark']) 
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df_output.to_excel(xlwriter, 'Disbursement Report' , index = False)
            # xlwriter.save()   
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = f'attachment; filename=Disbursement_Data_{current_date}.xlsx'
            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))