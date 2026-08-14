from rest_framework.views import APIView

from cibil_score.models import CibilScore
from application.models import Application
from cibil_score.serializer import CibilScoreSerializer
from utils.responseHandler import HttpResponse
import traceback

class CibilScoreView(APIView):
    def post(self, request):
        try:
            data = request.data
            user = request.user
            application_id = request.GET.get("application_id", "")
            application = Application.objects.get(application_id=application_id)

            data["created_by"] = str(user.user_id)
            data["application"] = application.application_id

            existing_cibil_score = CibilScore.objects.filter(application=application).first()

            if existing_cibil_score:
                # Update existing credit score
                serializer = CibilScoreSerializer(existing_cibil_score, data=data)
            else:
                # Create new credit score
                serializer = CibilScoreSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({'cibil_score': serializer.data})
            else:
                return HttpResponse.BadRequest(serializer.errors) 

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def get(self, request):
        try:
            application_id = request.GET.get("application_id", "")
            if not application_id:
                return HttpResponse.BadRequest("Application id is required!")
            
            cibil_score = CibilScore.objects.get(application=application_id)
            serializer = CibilScoreSerializer(cibil_score)
            return HttpResponse.Success({'cibil_score': serializer.data})
        
        except CibilScore.DoesNotExist:
            return HttpResponse.BadRequest("Cibil Score not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))