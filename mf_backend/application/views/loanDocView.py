# from rest_framework.views import APIView
# from utils.responseHandler import HttpResponse
# from application.models import LoanDocument
# from document.serializers import LoanDocumentSerializer
from django.db.models import Q
from rest_framework.views import APIView
from application.models import LoanDocument

from document.serializers import LoanDocumentSerializer , GetLoanDocumentSerializer
from utility.api_framework import ApiFramework
from utility.crud_helper import CrudHelper
from utils.constants import ApplicationType
from utils.responseHandler import HttpResponse


class TakeOverDoc(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data

    def process(self):
        data=CrudHelper(LoanDocumentSerializer)\
            .get_all_data(query=Q(application__application_type=ApplicationType.TAKEOVER.value,application__application_id=self.__data.get('application_id')))

        return data

class TakeOverDocView(APIView):

    def get(self, request):
        application=request.query_params.get('application_id')
        return TakeOverDoc(data={'application_id':application}).main()
    
class UnsecuredLoanDocView(APIView):
    
    def get(self,request):
        application=request.data.get("application", None)
        document_type=request.data.get("document_type", None)

        loan_doc= LoanDocument.objects.filter(application=application , document_type=document_type)
        ser = GetLoanDocumentSerializer(loan_doc , many=True)
        return HttpResponse.Success({"loan_doc":ser.data})

