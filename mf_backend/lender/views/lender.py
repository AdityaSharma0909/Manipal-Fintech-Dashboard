from rest_framework.views import APIView
from ..models import Lender
from ..serializers import LenderSerializer
from utils.responseHandler import HttpResponse
import traceback

class LenderView(APIView):
    #get all lenders 
    def get(self,request):
        try:
            data=Lender.objects.all()
            ser=LenderSerializer(data,many=True)
            return HttpResponse.Success({"lender":ser.data})
        except Lender.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))