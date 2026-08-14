from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse
from federal.services import utilitysevrice
from federal.serializers import SolidMappingModelSerializer
from ..models import FederalBankApplication
from django.core.files.base import ContentFile

from ..services.customercreation import CustomerCreation
import base64
import traceback


class FederalCustomerCreation(APIView):

    def post(self, request):
        try:
            app_id = request.data.get("app_id","")
            sign_id = request.data.get("sign_id")
            sol_id = request.data.get("sol_id")
            
            if(sign_id is None):
                return HttpResponse.BadRequest("Error","Sign Id is mandatory")
            if(sol_id is None):
                return HttpResponse.BadRequest("Error","Sol Id is mandatory")
            borrower_application = Application.objects.get(application_id=app_id)
            fba = FederalBankApplication.objects.get(application=app_id)

            signImg = ContentFile(base64.b64decode(sign_id), name=app_id+'.png')

            fba.sign_id = signImg
            fba.solId = sol_id
            fba.save()

            customer_response = CustomerCreation.createCustomer(borrower_application,fba)
           
            return HttpResponse.Success(customer_response)
            #return HttpResponse.Success("success")
        except Application.DoesNotExist as e:
            print(e)
            traceback.print_exc()
            return HttpResponse.BadRequest("Error","Application Does Not Exist")
        except FederalBankApplication.DoesNotExist as e:
            print(e)
            traceback.print_exc()
            return HttpResponse.BadRequest("Error", str(e))
        
    def get(self, request):
        try:
            reference_id = request.GET.get("reference_id","")
            print("reference_id: ",reference_id)
            customer_response = CustomerCreation.customerEnquiry(reference_id)
           
            return HttpResponse.Success(customer_response)
            #return HttpResponse.Success("success")
        except Application.DoesNotExist as e:
            print(e)
            return HttpResponse.BadRequest("Error","Application Does Not Exist")
        
class SolidMapping(APIView):

    def get(self, request):
        try:
            q=request.GET.get("q","")
            if q == None or q == " ":
                return HttpResponse.BadRequest()
            else:
                solid_mapping = utilitysevrice.getBranchList(q)
                ser = SolidMappingModelSerializer(solid_mapping,many=True)
                return HttpResponse.Success({"federal_branches":ser.data})
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))