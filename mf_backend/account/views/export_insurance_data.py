import datetime
import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from account.service.export_insurance_data import ExportInsuranceService


class ExportInsuranceView(APIView):


    def get(self, request):
        try:
            user = request.user
            if user.role != ROLES.CPC.value:
                return HttpResponse.Forbidden("Not Allowed")
            output = ExportInsuranceService().exportInsurance(request)
            # if not output:
            #     return HttpResponse.BadRequest({"message":"No Data found"})
            df_output = pd.DataFrame(output, columns=['Master Policy No','Loan A/c No','Name of Proposer',
                                                      'Branch Name','Branch Code','Disbursement Date','Policy Start Date',
                                                      'Policy End Date','Number of Applicant','Loan Tenure (In Years)','Loan Amount',
                                                      'Policy Tenure (In Years)','Name of Insured','Date of Birth (DD/MM/YYYY)','Age',
                                                      'Gender','Address of the Insured','City', 'District','State','Pincode','Mobile No.',
                                                      'Email','Sum Insured','Nominee Name','Age of Nominee','Nominee Relationship With Insured',
                                                      'SM Name','Premium Amount','GST','Total','UTR No.','UTR Amount','UTR Date', 'Product']) 
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df_output.to_excel(xlwriter, 'Insurance Report' , index = False)
            # xlwriter.save()   
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = f'attachment; filename=Insurance_Report_{current_date}.xlsx'
            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))