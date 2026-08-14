from rest_framework.views import APIView

from loan.models import Loan
from loan.services.calculate_accrued_interest import CalculateAccruedInterest
from loan.services.calculate_penalty import CalculatePenalty
from loan.services.demand_generation import DemandGeneration
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class ManualInterestAccrual(ApiFramework):
    def process(self):

        CalculateAccruedInterest()
        # CalculatePenalty()
        # DemandGeneration()

        return custom_response_obj(message=list(Loan.objects.values().all()),code=200)



class ManualInterestAccrualView(APIView):

    def get(self, request):
        return ManualInterestAccrual().main()