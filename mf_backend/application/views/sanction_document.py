from rest_framework.views import APIView
from django.http import HttpResponse as dhttp

from application.models import Application
from utils.responseHandler import HttpResponse
from application.services.sanction_service import SanctionPdfGeneration,SanctionEsignUtil
from utility.api_framework import ApiFramework

import traceback

class SanctionDocument(APIView):
    def get(self,request):
        try:
            application_id = request.GET.get("application_id","")
            application = Application.objects.get(application_id=application_id)

            pdf=SanctionPdfGeneration().generate(application)
            pdf_file_name= "{app_no}-{fn}_{ln}.pdf".format(
                    app_no=application.application_number,
                    fn=application.account.user.first_name,
                    ln=application.account.user.last_name,
                )
                
            response = dhttp(pdf, content_type='application/pdf')
                
            response['Content-Disposition'] = f'attachment; filename="{pdf_file_name}"'
            response["Access-Control-Expose-Headers"] = 'Content-Disposition'
            
            return response

        except Exception as e:
           traceback.print_exc()
           return HttpResponse.InternalServerError(str(e))
        

class SanctionEsign(ApiFramework):

    def __init__(self, data , user):
        super().__init__()
        self.__application_id=data.get('application_id')
        #added here 
        self.__user = user

    def process(self):
        return SanctionEsignUtil().process_esign(self.__application_id , self.__user)


class SanctionEsignView(APIView):

    def post(self, request):
        return SanctionEsign(data=request.data , user=request.user).main()