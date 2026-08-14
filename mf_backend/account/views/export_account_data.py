import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from account.service.export_account_data import ExportAccountService

class ExportAccountView(APIView):
    
    def get(self, request):
        try:
            
            user = request.user
            if user.role == ROLES.LOAN_OFFICER.value:
                return HttpResponse.Forbidden("Not Allowed")
            
            output = ExportAccountService().get_account_data(query_options=request.query_params)

            #df_output = pd.DataFrame(output)
            df_output = pd.DataFrame(output, columns=['Name','Customer ID','Email','Gender','DOB',
                                                      'Occupation','Sub Occupation','Profile Pic','Net Annual Income','Aadhar No','PAN',
                                                      "Mother's Name","Father's Name","Spouse's Name",'Education',
                                                      'Religion','Disablity','Nationality','Caste','Maritial_Status','Status','Bank Name',
                                                      'Account Number','IFSC code','Account Holder Name','Branch Code','Branch Name','Branch State',
                                                      'Nominee Name','Nominee Age','Nominee Relation','Nominee Contact','Insurance Product Name','Company Name','Validity','Coverage','Price','Account Created At'])
            
            
            columns_to_fill_with_zero = ['Net Annual Income']
            df_output[columns_to_fill_with_zero] = df_output[columns_to_fill_with_zero].fillna(0).astype(int)
            df_output[columns_to_fill_with_zero] = df_output[columns_to_fill_with_zero].replace('', 0).astype(int)

            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df_output.to_excel(xlwriter, 'Accounts Report' , index=False)
            # xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = 'attachment; filename=Account_Data.xlsx'

            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))