from rest_framework.views import APIView
from tele_verification.serializers import tele_verificationSerializer
from ..models import TeleVerification
from utils.responseHandler import HttpResponse
from account.models import Account
from application.models import Application
from utils.constants import APPLICATION_STATUS

class TeleVerificationView(APIView):  
    def post(self, request):
        try:
            data = request.data
            user = request.user
            application_id = request.GET.get("application_id", "")
            
            if not application_id:
                return HttpResponse.BadRequest("Application not found")
            application =  Application.objects.get(application_id = application_id)
            data["created_by"] = str(user.user_id)
            data["pd_done_by"] = application.Originatedby
            data["tele_pd_done_by"] = TeleVerification.created_by 
            data["application"] = application.application_id
            serializer = tele_verificationSerializer(data= data)
            if serializer.is_valid():
                serializer.save()
                application.status = APPLICATION_STATUS.TELE_VERIFICATION_DONE.value
                application.save() 
                return HttpResponse.Success({"tele_verification": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
            
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
    def patch(self, request):
        try:
            data = request.data
            tele_verification_id = request.GET.get("tele_verification_id", "")  
            if not tele_verification_id:
                return HttpResponse.BadRequest("tele verification not found")    
            tele_verification_user = TeleVerification.objects.get(tele_verification_id=tele_verification_id)
            serializer = tele_verificationSerializer(tele_verification_user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"tele_verification":serializer.data})

            return HttpResponse.BadRequest( serializer.errors)                      
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
    
    def get(self,request):
        try:
            application_id = request.GET.get("application_id", "")
            if not application_id:
                return HttpResponse.BadRequest("Application id is required!")
            tele_verification_user = TeleVerification.objects.get(application=application_id)
            serializer = tele_verificationSerializer(tele_verification_user)
            return HttpResponse.Success({"tele_verification":serializer.data})
            # else:
            #     tele_verification_user=  TeleVerification.objects.all()
            #     serializer = tele_verificationSerializer(tele_verification_user,many=True)
            #     return HttpResponse.Success({"tele verification":serializer.data})
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
    def delete(self,request):
        try:
            tele_verification_id = request.GET.get("tele_verification_id", "")
            tele_verification_user = TeleVerification.objects.get(tele_verification_id=tele_verification_id)
            tele_verification_user.delete()
            return HttpResponse.Success("Deleted Successfully")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        


