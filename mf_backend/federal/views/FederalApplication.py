from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse
from federal.models import FederalBankApplication
from federal.serializers import FederalBankApplicationModelSerializer


class FederalApplication(APIView):

    def get(self, request):
        try:
            app_id = request.GET.get("app_id","")
            fed_app = FederalBankApplication.objects.get(application__application_id=app_id)
            return HttpResponse.Success({
                "federal_application": FederalBankApplicationModelSerializer(fed_app).data,
            })
        except FederalBankApplication.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            print(e)
            return HttpResponse.InternalServerError(str(e))


    def patch(self, request):
        try:
            app_id = request.GET.get("app_id","")
            fed_app = FederalBankApplication.objects.get(application__application_id=app_id)
            ser = FederalBankApplicationModelSerializer(fed_app, data=request.data, partial=True)
            if ser.is_valid():
                ser.save()
                return HttpResponse.Success({
                    "federal_application": ser.data
                })
            return HttpResponse.BadRequest(ser.errors)
        except FederalBankApplication.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            print(e)
            return HttpResponse.InternalServerError(str(e))
        
    