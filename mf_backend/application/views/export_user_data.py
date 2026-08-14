# import traceback
# import pandas as pd
# from io import BytesIO as IO # for modern python
# from django.http import HttpResponse as dhttp
# from rest_framework.views import APIView
# from utils.constants import ROLES
# from utils.responseHandler import HttpResponse
# from application.services.export_user_data import ExportUserApplicationService


# class ExportUserApplicationView(APIView):

#     def get(self, request):
#         try:

#             user = request.user
#             if user.role != ROLES.CPC.value:
#                 return HttpResponse.Forbidden("Not Allowed")
            
#             output = ExportUserApplicationService().export_user_application(request)

#             #df_output = pd.DataFrame(output)
#             df_output = pd.DataFrame(output, columns=['Name','Email','Gender','DOB','Contact Number',
#                                                       'Occupation','Net Annual Income','Aadhar No','PAN',
#                                                       "Mother's Name","Father's Name","Spouse's Name",'Education',
#                                                       'Religion','Nationality','Disability','Bank Name',
#                                                       'Account Number','IFSC code','Account Holder Name','Account Created At'])
            
        
#             excel_file = IO()
#             xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
#             df_output.to_excel(xlwriter, 'Radian Applications')
#             # xlwriter.save()
#             xlwriter.close()
#             excel_file.seek(0)
#             response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#             response['Access-Control-Expose-Headers'] = 'Content-Disposition'
#             response['Content-Disposition'] = 'attachment; filename=Radian_User_Application_Data.xlsx'

#             return response

#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse.InternalServerError(str(e))