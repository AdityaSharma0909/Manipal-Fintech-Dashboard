from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cibil_score.service.cibil_score_check import CibilScoreCheck


class CibilCreditPull(APIView):

    permission_classes = [AllowAny]
    def get(self, request):
        self.application_no=request.GET.get('application_no')
        if self.application_no is None:
            return Response(data={'status':'success', 'data':{'msg':'application_no is required'}}, status=200)
        score = CibilScoreCheck().check_consumer_report(self.application_no)
        return score