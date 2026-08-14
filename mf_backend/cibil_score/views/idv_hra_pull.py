from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cibil_score.service.idv_efficiency import IdvEfficiency


class IdvHraPull(APIView):

    permission_classes = [AllowAny]
    def get(self, request):
        application_no=request.GET.get('application_no')
        if application_no is None:
            return Response(data={'status':'success', 'data':{'msg':'application_no is required'}}, status=200)
        score = IdvEfficiency().call_idv_efficiency(application_no=application_no)
        return Response(score)