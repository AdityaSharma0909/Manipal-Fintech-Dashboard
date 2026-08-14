from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from account.service.sprint_verify_docs import SprintVerifyDocs
from utility.api_framework import ApiFramework


class SprintVerifyDocsView(APIView, ApiFramework):

    __data=None
    __method=None
    __response=None
    __verification_type=None
    serializer=None
    def run_logic(self):
        service=SprintVerifyDocs()
        if self.__method=='POST':
            self.__response=service.process_verification(verification_type=self.__verification_type, payload=self.__data)

    def process(self):
        return self.__response

    @extend_schema(operation_id="account_verify_sprint_create")
    def post(self, request, verification_type):
        self.__data=request.data
        self.__method='POST'
        self.__verification_type=verification_type
        return self.main()
