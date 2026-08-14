import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from loan.services.export_loan_data import ExportLoanServices


class ExportLoanView(APIView):

    def get(self, request):
        try:

            user = request.user
            if user.role != ROLES.CPC.value:
                return HttpResponse.Forbidden("Not Allowed")
            
            output = ExportLoanServices().get_loans_data(query_options=request.query_params)

            #df_output = pd.DataFrame(output)
            df_output = pd.DataFrame(output, columns=['Loan number','Status','Name','Email','Gender','DOB',
                                                      'Contact Number','Occupation','Net Annual Income','Aadhar No',
                                                      'PAN',"Mother's Name","Father's Name","Spouse's Name",
                                                      'Education','Religion','Nationality','Disability','Bank Name',
                                                      'Account Number','IFSC code','Account Holder Name','Branch Code','Branch Name',
                                                      'Amortization type','Product name','Tenure','Intrest rate',
                                                      'Processing fee','Processing fee percent','Penalty',
                                                      'Stamp duty','Ltv','Lender name','Loan amount','Loan type',
                                                      'Days past dues','Purpose of loan','Total goods price',
                                                      'Total weight','Net weight','Originated by name',
                                                      'Appraised by name','GST','Gold rate(per gram)',
                                                      'Disbursed date','Interest accrued till date','Principal paid',
                                                      'Interest paid','Principal remaining','Interest remaining'])

            columns_to_fill_with_zero = ['Loan amount', 'Total weight', 'Net weight', 'Tenure' , 'Total goods price' , 'Gold rate(per gram)' , 'Ltv' , 'Stamp duty' , 'Intrest rate' , 'Processing fee' , 'Penalty' , 'Processing fee percent' , 'Days past dues' , 'GST' , 'Interest accrued till date','Principal paid','Interest paid','Principal remaining','Interest remaining' ]
            df_output[columns_to_fill_with_zero] = df_output[columns_to_fill_with_zero].fillna(0).astype(int)
            df_output[columns_to_fill_with_zero] = df_output[columns_to_fill_with_zero].replace('', 0).astype(int)



            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df_output.to_excel(xlwriter, 'Loan Report', index=False)
            # xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = 'attachment; filename=Loan_Data.xlsx'

            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))