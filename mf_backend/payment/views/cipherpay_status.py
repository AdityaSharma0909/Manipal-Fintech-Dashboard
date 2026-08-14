from payment.models import Repayment
from payment.serializers import RepaymentStatusSerializer
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
import traceback

class cipherpayStatus(APIView):
    def get(self,request):
        try:
            repayment_id = request.GET.get("repayment_id", "")
            if not repayment_id:
                return HttpResponse.BadRequest("Repayment ID is required")
            
            payment = Repayment.objects.get(repayment_id=repayment_id)
            serializer = RepaymentStatusSerializer(payment)

            return HttpResponse.Success(data={"payments":serializer.data})
        except Repayment.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))