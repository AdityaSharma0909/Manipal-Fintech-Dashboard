from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from utils.responseHandler import HttpResponse
from ..serializers import ReferedLeadSerializer
from .. models import Lead
from utils.constants import LEAD_SOURCE
import traceback

class OpenReferedLeadView(APIView):
    permission_classes = [AllowAny] 
    def post(self,request):
        try:
            data = request.data
            data["source"] = LEAD_SOURCE.CUSTOMER_APP_REFERENCE.value
            serializer=ReferedLeadSerializer(data = data)

            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead" : serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        

class ReferedLeadView(APIView):
    def post(self,request):
        try:
            data = request.data
            user = request.user
            data["refered_by"] = str(user.user_id)
            data["source"] = LEAD_SOURCE.CUSTOMER_APP_REFERENCE.value
            serializer=ReferedLeadSerializer(data = data)

            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead" : serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
