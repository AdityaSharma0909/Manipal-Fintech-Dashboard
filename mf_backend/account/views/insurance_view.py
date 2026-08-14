from rest_framework.views import APIView

from account.service.insurance_service import InsuranceService
from utility.api_framework import ApiFramework
from account.models import InsuranceProduct
from account.serializers import InsuranceSerializer
from utils.responseHandler import HttpResponse


class InsuranceUtil(ApiFramework):

    def __init__(self, data,method,application_id=None):
        super().__init__()
        self.data = data
        self.method = method
        self.application_id = application_id
        self.service = InsuranceService()
        self.response = {}

    def run_logic(self):
        if self.method == 'POST':
            self.response = self.service.create_obj(self.data)
        elif self.method == 'GET':
            # self.response = self.service.get_all_insurance()
            self.response = self.service.get_all_insurance(application_id=self.application_id)
    def process(self):
        return self.response


class InsuranceView(APIView):

    def post(self, request):
        data=request.data
        return InsuranceUtil(data=data, method='POST').main()

    def get(self, request):
        application_id = request.GET.get('application_id', None)
        # return InsuranceUtil(data=None, method='GET').main()
        return InsuranceUtil(data=None, method='GET', application_id=application_id).main()
    


class InsuranceAllView(APIView):

    def get(self , request):
        ins = InsuranceProduct.objects.all()
        ser = InsuranceSerializer(ins , many=True)
        return HttpResponse.Success({"insurance_product": ser.data})