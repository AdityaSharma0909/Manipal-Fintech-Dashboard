from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse
from utils.constants import APPLICATION_STATUS
from federal.models import FederalBankApplication

import datetime

        
class ConsentView(APIView):

    def post(self, request):
        try:
            app_id = request.data.get("app_id","")
            consent_status = request.data.get("is_consent_given","")
            borrower_application = Application.objects.get(application_id=app_id)
            fbas = FederalBankApplication.objects.filter(application=borrower_application)
            if len(fbas)>0:
                fba = fbas[0]
                fba.ekyc_consent_given=consent_status
                fba.ekyc_consent_given_at=datetime.datetime.now()
                fba.save()
            else:
                fba = FederalBankApplication(application=borrower_application,account=borrower_application.account,ekyc_consent_given=consent_status,ekyc_consent_given_at=datetime.datetime.now())
                fba.save()
            borrower_application.status = APPLICATION_STATUS.FEDERAL_CONSENT_SUBMITTED.value
            borrower_application.save()
            return HttpResponse.Success({"federal_application_id":fba.federal_application_id})
        except Application.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest("Error","Application Does Not Exist")
        except Exception as e:
            print(e)
            return HttpResponse.InternalServerError(str(e))
        
class AadharVerificationView(APIView):
    def post(self,request):
        try:
            app_id = request.data.get("app_id","")
            aadhar_rrn = request.data.get("TransactionId")
            status = request.data.get("Status")
            if aadhar_rrn == None:
                return HttpResponse.BadRequest("Aadhar RRN cannot be empty")
            if(not status== "Y"):
                return HttpResponse.BadRequest("eKYC verification failed")
            # borrower_application = Application.objects.get(application_id=app_id)
            fba = FederalBankApplication.objects.get(application__application_id=app_id)

            fba.aadhar_rrn = aadhar_rrn
            fba.ekyc_status = "1"
            fba.ekyc_request_id = aadhar_rrn
            fba.ekyc_meta_response = request.data
            fba.application.status = APPLICATION_STATUS.FEDERAL_EKYC_SUBMITTED.value
            fba.save()
            return HttpResponse.Success({"federal_application_id":fba.federal_application_id})
        except FederalBankApplication.DoesNotExist:
            return HttpResponse.BadRequest("FBA with app_id does not exist")
        except Exception as e:
            return HttpResponse.BadRequest(str(e))
            
        
    