from rest_framework.views import APIView
from rest_framework.response import Response
from loan.models import DemandGeneration
from loan.serializers.bill_generation_serializier import BillGenerationSerializer
from utils.responseHandler import HttpResponse

class LoanBillAPIView(APIView):
    def get(self, request):
        try:
            loan_id = request.GET.get('loan_id')

            if not loan_id:
                return HttpResponse.BadRequest('loan_id is required')

            loans = DemandGeneration.objects.filter(loan_id=loan_id)
            serializer = BillGenerationSerializer(loans, many=True)
            return HttpResponse.Success(serializer.data)


        
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
