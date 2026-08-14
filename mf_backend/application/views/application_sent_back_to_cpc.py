from rest_framework.views import APIView

from application.services.application_services import ApplicationHelper
from utility.api_framework import ApiFramework


class ApplicationRevertedToCPC(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data
    def process(self):
        return ApplicationHelper().update_kick_back_status(self.__data)

class ApplicationRevertToCPCView(APIView):

    def post(self, request):
        data=request.data
        return ApplicationRevertedToCPC(data=data).main()