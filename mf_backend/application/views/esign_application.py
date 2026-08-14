from django.shortcuts import render
from rest_framework.views import APIView

from application.services.esign_application import EsignApplicationUtil
from utility.api_framework import ApiFramework


class EsignApplication(ApiFramework):

    def __init__(self, data , user):
        super().__init__()
        self.__application_id=data.get('application_id')
        #added here 
        self.__user = user

    def process(self):
        return EsignApplicationUtil().process_esign(self.__application_id , self.__user)


class EsignApplicationView(APIView):

    def post(self, request):
        return EsignApplication(data=request.data , user=request.user).main()



# def temp(request):
#     data=EsignApplicationUtil().process_esign('91627f41-a5ab-4962-9056-167bc7056575')
#     return render(request, "application/index.html", data)
