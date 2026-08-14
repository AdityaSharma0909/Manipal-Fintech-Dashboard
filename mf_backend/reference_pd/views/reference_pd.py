from rest_framework.views import APIView
from reference_pd.serializer import Reference_PDSerializer
from utils.responseHandler import HttpResponse
from ..models import Reference_PD
from account.models import Account
from utils.constants import ACCOUNT_STATUS


class ReferencePDView(APIView):
    def post(self,request):
        try:
            data = request.data
            user = request.user
            account_id = request.GET.get("account_id", "")
            account = Account.objects.get(account_id=account_id)
            
            response_data = []
            errors = []
            
            for entry in data:
                entry["created_by"] = str(user.user_id)
                entry["account"] = account.account_id
                serializer = Reference_PDSerializer(data=entry)
                if serializer.is_valid():
                    serializer.save()
                    account.status = ACCOUNT_STATUS.REFERENCE_PD_ADDED.value
                    account.save()
                    response_data.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            
            if errors:
                return HttpResponse.BadRequest({"errors": errors})
            
            return HttpResponse.Success({"reference_pd": response_data})
        
        except Account.DoesNotExist:
            return HttpResponse.BadRequest({"error": "Account not found"})
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
    def patch(self,request):
        try:
            data_list = request.data  
            response_data = []
            errors = []

            for item in data_list:
                pd_details_id = item.get('pd_details_id', "")
                if not pd_details_id:
                    errors.append({"error": "pd_details_id is required"})
                    continue

                try:
                    user_reference = Reference_PD.objects.get(pd_details_id=pd_details_id)
                    serializer = Reference_PDSerializer(user_reference, data=item, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        response_data.append(serializer.data)
                    else:
                        errors.append({"pd_details_id": pd_details_id, "errors": serializer.errors})
                except Reference_PD.DoesNotExist:
                    errors.append({"pd_details_id": pd_details_id, "error": "Reference_PD not found"})
                except Exception as e:
                    errors.append({"pd_details_id": pd_details_id, "error": str(e)})

            if errors:
                return HttpResponse.BadRequest({"errors": errors})
            
            return HttpResponse.Success({"reference_pd": response_data})
        
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
    
    def get(self,request):
        try:
            account_id = request.GET.get("account_id", "")
            if not account_id:
                return HttpResponse.BadRequest("Account id is required!")
            reference_user=Reference_PD.objects.filter(account=account_id)
            serializer=Reference_PDSerializer(reference_user,many=True)
            return HttpResponse.Success({"reference_pd":serializer.data})
            # else:
            #     reference_user= Reference_PD.objects.all()
            #     serializer=Reference_PDSerializer(reference_user,many=True)
            #     return HttpResponse.Success({"reference_pd":serializer.data})
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
    def delete(self,request):
        try:
            pd_details_id = request.GET.get('pd_details_id')
            reference_user = Reference_PD.objects.get(pd_details_id=pd_details_id)
            reference_user.delete()
            return HttpResponse.Success("Deleted Successfully")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        


