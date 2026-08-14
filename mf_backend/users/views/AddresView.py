from rest_framework.views import APIView    

from account.models import Account
from users.models import User
from rest_framework.response import Response
from ..models import Address
from utils.responseHandler import HttpResponse
import logging
from ..serializers import AddressesSerializer ,AddressesDisplaySerializer
import traceback
from utils.constants import ACCOUNT_STATUS , APPLICANT_TYPE
class AddressesView(APIView):
        
        
        
    # TODO: structure the code here
    
        def post(self, request):
            try:
                data=request.data
                account = Account.objects.get(account_id=request.GET.get("account_id", ""))
                if not Account.objects.filter(account_id=str(account.account_id)).exists():
                    return HttpResponse.BadRequest("Lead does not exist")
                
                for i in range(len(data)):
                    data[i]["account"] =str(account) 
                # data[0]["account"] =str(account) 
                # data[1]["account"] =str(account) 


                
                serializer=AddressesSerializer(data=data,many=True)
                if serializer.is_valid():

                    serializer.save()
                    if account.applicant_type==APPLICANT_TYPE.CO_APPLICANT.value:
                        applicant=Account.objects.get(user=account.applicant)
                        applicant.status=ACCOUNT_STATUS.CO_APPLICANT_ADDRESS_ADDED.value
                        applicant.save()
                        account.status=ACCOUNT_STATUS.ADDRESS_ADDED.value
                    else:
                        account.status=ACCOUNT_STATUS.ADDRESS_ADDED.value
                    account.save()

                    return HttpResponse.Success({"addresses": serializer.data})
                return HttpResponse.BadRequest({"errors": serializer.errors})
            except Address.DoesNotExist:
                return HttpResponse.Unauthorized('Invalid credentials given')
                
            except Exception as e:
                traceback.print_exc()
                return HttpResponse.InternalServerError(str(e))   
        
        # def patch(self, request):
        #     try:
        #         data=request.data
        #         dataDict = {}
        #         for x in data:
        #             dataDict[x.get("address_id")] = x
        #         addresses = Address.objects.filter(account=request.GET.get('account_id',''))
        #         updatedAddresses = []
        #         for address in addresses:
        #             serializer=AddressesSerializer(address, data=dataDict[str(address.address_id)], partial=True)
        #             print(serializer)
        #             if serializer.is_valid():
        #                 updatedAddress = serializer.save()
        #                 updatedAddresses.append(updatedAddress)
        #             #return HttpResponse.BadRequest(serializer.errors)
        #             respData = AddressesSerializer(updatedAddresses,many=True)
        #         return HttpResponse.Success({'address': respData.data } )

        #     except Address.DoesNotExist as e:
        #         return HttpResponse.BadRequest(e)
        #     except Exception as e:
        #         traceback.print_exc()
        #         return HttpResponse.InternalServerError(str(e))

        def patch(self, request):
            try:
                data = request.data
                address = Address.objects.get(address_id=request.GET.get("address_id", ""))
                serializer = AddressesSerializer(address, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return HttpResponse.Success({"address": serializer.data})
                return HttpResponse.BadRequest(serializer.errors)
            except Address.DoesNotExist as e:
                return HttpResponse.BadRequest(e)
            except Exception as e:
                traceback.print_exc()
                return HttpResponse.InternalServerError(str(e))
    
        def get(self, request):
            try:
                address= Address.objects.filter(account=request.GET.get('account_id',''))
                serializer=AddressesDisplaySerializer(address,many=True)     
                return HttpResponse.Success({'address':serializer.data})
            except Address.DoesNotExist as e:
                return HttpResponse.BadRequest(str(e))
            except Exception as e:
                traceback.print_exc()
                return HttpResponse.InternalServerError(str(e))
    
        
        
            
# class BothAddressesView(APIView):
#     def post(self,request):
#         try :
#             data=request.data
            
#             serializer=BothAddressSerializer(data)
#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse.InternalServerError(str(e))