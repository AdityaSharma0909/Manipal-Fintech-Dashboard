from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from application.services.application_services import ApplicationHelper
from utility.api_framework import ApiFramework


class PendingApplicationView(APIView, PageNumberPagination, ApiFramework ):

    response={}
    method=""
    serializer=None
    service=ApplicationHelper()
    logged_in_user=None
    request=None
    def run_logic(self):
        if self.method=="GET":
            self.response=self.service.get_pending_application(loan_manager=self.logged_in_user,
                                                               pagination=PageNumberPagination,
                                                               request=self.request)

    def process(self):
        return self.response

    def get(self, request):
        self.logged_in_user=request.user.user_id
        self.request=request
        self.method="GET"
        return self.main()