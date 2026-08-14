from rest_framework.views import APIView
from loan.models import Loan
from loan.services.calculate_penalty import CalculatePenalty
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class ManualPenalty(ApiFramework):
    def process(self):
        CalculatePenalty()
        return custom_response_obj(message=list(Loan.objects.values().all()),code=200)



class ManualPenaltyView(APIView):

    def get(self, request):
        return ManualPenalty().main()