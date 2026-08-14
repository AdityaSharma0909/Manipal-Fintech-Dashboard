import datetime
import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from application.services.export_insurance_MU_service import ExportMUInsuranceService

class ExportMUInsuranceView(APIView):

    def get(self, request):
        try:
            user = request.user
            if user.role != ROLES.CPC.value:
                return HttpResponse.Forbidden("Not Allowed")
            output = ExportMUInsuranceService().exportMUInsurance(request)
            # if not output:
            #     return HttpResponse.BadRequest({"message":"No Data found"})
            df_output = pd.DataFrame(output, columns=['SL No','Master Code','Agent Code','Bank','Branch','Source','CAFOS Code','FSC/FSM Code','SP Code',
                                                      'Member ID/Loan Account Number','First Name','Last Name','DOB','Gender','Address','City',
                                                      'State','Country','Pin Code','Loan Amount','Loan Tenure','Sum Assured','Loan Disbursement date/ Date of Joining Scheme',
                                                      'Type of Cover (Single Life / Joint Life)','Policy term','Premium Amount (Actual)','ADB SA',
                                                      'Accelerated TI Benefit','Type of cover (Level / Reducing)','Nominee First Name','Nominee Surname',
                                                      'Nominee Gender','Nominee DOB','Nominee Relationship with LA','Medical questions YES/NO','Member Consent to Split Payment',
                                                      'UTRN No','Fund Transfer Date','Appointee Name','Appointee Surname','Appointee Gender','Appointee DOB',
                                                      'Appointee Relationship with Nominee','Member Consent to Cover Continuation','Mobile Numbers']) 
            for col in df_output.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']):
                df_output[col] = df_output[col].dt.tz_localize(None)
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df_output.to_excel(xlwriter, 'MSME Unsecured Insurance Report' , index = False)
            # xlwriter.save()   
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = f'attachment; filename=MSME_Unsecured_Insurance_Report_{current_date}.xlsx'
            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))