from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse

from federal.models import FederalBankApplication
from ..services.goldaccountservice import GLOpenService,GLCustomerValidationService, GLAccountService

import random

        
class GLOpenView(APIView):

    def post(self, request):
        try:
            app_id = request.data.get("app_id","")
            fba = FederalBankApplication.objects.get(application__application_id=app_id)
            service_response = GLOpenService.createGLAccount(fba)    
            # print("service_response:: ")
            # print(service_response)
            if service_response:
                fba.agent_otp = random.randrange(100000,999999)
                fba.save()
                resp = GLCustomerValidationService(fba).validateCustomer()
                if resp['status'] != 'error':
                    resp = GLAccountService().sendAccountDetails(fba)
                    return HttpResponse.Success(resp)
                else:
                    return HttpResponse.BadRequest(resp['message'])


            #TODO: If service_response is sucess:
                # 0. Generate Loan Agent Auth OTP and return in GlAccountOpen API response
                # 1. Call validateCustomer
                # 2. Call Account Details API (Send the generated OTP to federal)
                # 3. Pledge Card Submission      
            # return HttpResponse.BadRequest(service_response)
        except FederalBankApplication.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest(str(e))
        except ValueError as e:
            print(e)
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            print(e)
            return HttpResponse.InternalServerError(str(e))
        

        
# class GLValidateView(APIView):
#     def post(self,request):
#         try:
#             app_id = request.data.get("app_id","")
#             print("AppId: ",app_id)
#             borrower_application = Application.objects.get(application_id=app_id)
#             fba = FederalBankApplication.objects.get(application=app_id)
#             print("borrower_application: ",borrower_application)
#             service = GLCustomerValidationService(borrower_application,fba)
#             service_response = service.validateCustomer()             
#             return HttpResponse.Success(service_response)
#         except Application.DoesNotExist as e:
#             print(e)
#             return HttpResponse.BadRequest("Error","Application Does Not Exist")
        
    