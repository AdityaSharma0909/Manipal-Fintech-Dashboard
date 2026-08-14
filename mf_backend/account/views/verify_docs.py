from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from account.service.verify_docs import VerifyDocs
from utility.api_framework import ApiFramework


class Verify(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data = data

    def process(self):
        resp = VerifyDocs(data=self.__data).verify()
        return resp


class VerifyDocView(APIView):

    @extend_schema(operation_id="account_verify_document_create")
    def post(self, request):
        data = request.data
        return Verify(data).main()
