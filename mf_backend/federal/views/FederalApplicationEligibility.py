from rest_framework.views import APIView
from application.models import Application
from federal.models import FederalBankApplication
from utils.responseHandler import HttpResponse
from utils.constants import APPLICATION_STATUS

from ..services.dedupeservice import DedupeService
from ..services.panservice import PanService
from ..services.unofacservice import UNOFACService
from ..services.namedobservice import NameDobService


class EligibilityView(APIView):

    def get(self, request):
        try:
            app_id = request.GET.get("app_id","")
            fba = FederalBankApplication.objects.get(application__application_id=app_id)

            fba.application.status = APPLICATION_STATUS.FEDERAL_ELIGIBILITY_CHECKED.value
            
            # borrower_application = Application.objects.get(application_id=app_id)
            #CALLING DEDUPE SERVICE
            is_existing_customer = False
            resp = {}
            name_Dob_response = NameDobService.verifyNameDob(fba)
            if name_Dob_response.get("is_eligible"):
                service =  DedupeService(fba)
                dedupe_response = service.fetchDedupe(fba)
                is_existing_customer = dedupe_response.get("is_existing_customer")
                is_eligible = dedupe_response.get("is_eligible")

                if(not is_eligible):
                    resp = {
                            "is_eligible":False,
                            "is_existing_customer":is_existing_customer,
                            "status":"success",
                            "message":dedupe_response.get("message")
                        }
                elif(is_eligible):
                    #CALLING PAN SERVICE
                    pan_response = PanService.verifyPanNumber(fba)
                    if(not pan_response.get("is_eligible")):
                        resp = {
                                "is_eligible":False,
                                "is_existing_customer":is_existing_customer,
                                "status":"success",
                                "message":pan_response.get("message"),
                            }
                    else:
                        #CALLING UN OFAC SERVICE
                        unofac_response = UNOFACService.verifyUnOfac(fba)
                        if(not unofac_response.get("is_eligible")):
                            resp = {
                                "is_eligible":False,
                                "is_existing_customer":is_existing_customer,
                                "status":"success",
                                "message":unofac_response.get("message"),
                            }
                        else:
                            resp = {
                                "is_eligible":True,
                                "is_existing_customer":is_existing_customer,
                                "status":"success",
                            }
            else:
                resp = {
                        "is_eligible":False,
                        "is_existing_customer":is_existing_customer,
                        "status":"success",
                        "message":name_Dob_response.get("message"),
                    }
            
            fba.is_existing_customer = resp['is_existing_customer']
            fba.is_eligible = resp['is_eligible']
            fba.save()
            
            # return HttpResponse.Success(resp)
            # TODO: need to remove below code and uncommenting above line 
            return HttpResponse.Success({
                                "is_eligible":True,
                                "is_existing_customer": False,
                                "status":"success",
                            })
            #return HttpResponse.Success("success")
        except Application.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest("Error","Application Does Not Exist")
        except Exception as e:
            print(e)
            return HttpResponse.InternalServerError(str(e))
        
    