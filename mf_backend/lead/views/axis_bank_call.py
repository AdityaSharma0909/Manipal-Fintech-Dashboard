from rest_framework.views import APIView

from lead.serializers import AxisBankSerializer
from lead.services.axis_bank_apis import AxisBankCalls
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class AxisBankApiView(APIView, ApiFramework):

    serializer=None
    def run_logic(self):
        ser=AxisBankSerializer(data=self.__data)
        if ser.is_valid():
            self.__response=AxisBankCalls().create_lead(self.__data)
        else:
            self.__response=custom_response_obj(message=ser.errors, code=400)
    def process(self):
        return self.__response

    def post(self, request):
        self.__data=request.data
        return self.main()