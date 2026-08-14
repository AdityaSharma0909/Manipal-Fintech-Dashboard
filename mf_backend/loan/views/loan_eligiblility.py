from rest_framework.views import APIView

from loan.services.loan_services import LoanHelper
from utility.api_framework import ApiFramework


class LoanEligibility(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data

    def process(self):
        return LoanHelper().check_loan_amount_pan_eligibility(amount_request=self.__data.get('amount_request'),
                                                              amount_requested_by=self.__data.get('application_id'))

class LoanEligibilityView(APIView):

    def post(self, request):
        return LoanEligibility(data=request.data).main()