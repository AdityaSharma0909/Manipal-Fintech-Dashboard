from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from loan.models import Loan
from loan.services.calculate_accrued_interest import CalculateAccruedInterest
from loan.services.calculate_penalty import CalculatePenalty
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj
from utils.constants import LOAN_STATUS


class CalculateLoanData(ApiFramework):
    def process(self):
        Loan.objects.filter(status=LOAN_STATUS.NEW.value).update(status=LOAN_STATUS.GOOD_STANDING.value)
        CalculateAccruedInterest()
        CalculatePenalty()
        loans=list(Loan.objects.values().all())
        return custom_response_obj(message=loans, code=200)


class CalculateLoanView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return CalculateLoanData().main()