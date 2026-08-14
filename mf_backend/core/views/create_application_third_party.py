from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView
from application.services.application_services import ApplicationHelper
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework


class CreateApplicationView(APIView, ApiFramework):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [ThirdPartyPermission]

    serializer=None
    __response=None
    __data=None
    __method=None
    def run_logic(self):
        application_helper=ApplicationHelper()
        if self.__method=="POST":
            self.__response=application_helper.create_application(data=self.__data)
        else:
            self.__response=application_helper.get_third_part_application(third_party_user=self.__data)

    def process(self):
        return self.__response

    def post(self, request):
        self.__data=request.data
        self.__data['Originatedby']=request.user.user_id
        self.__method="POST"
        return self.main()

    def get(self, request):
        self.__data=request.user.user_id
        return self.main()