from rest_framework.views import APIView

from core.service.customer_dashboard import CustomerData
from utility.api_framework import ApiFramework


class CustomerDashboardView(APIView, ApiFramework):
    __account_id=None
    serializer=None
    __response=None
    def process(self):
        self.__response=CustomerData().get_dashboard_data(account_id=self.__account_id)
        return self.__response
    def get(self, request):
        self.__account_id=request.GET.get('account_id')
        return self.main()


class CustomerApplicationDetailsView(APIView, ApiFramework):
    __application_id = None
    serializer = None
    __response = None

    def process(self):
        self.__response = CustomerData().get_customer_app_details(self.__application_id)
        return self.__response

    def get(self, request):
        self.__application_id = request.GET.get('application_id')
        return self.main()