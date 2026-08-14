from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from credit_status.models import CreditStatus
from credit_status.serializers import CreditStatusSerializer , CreditStatusGETSerializer
import traceback
from django.core.exceptions import ObjectDoesNotExist
from account.models import Account
from utils.constants import ACCOUNT_STATUS



class CreditStatusView(APIView):
    def post(self,request):
        try:
            data = request.data
            user = request.user
            account_id = request.GET.get("account_id", "")
            account = Account.objects.get(account_id=account_id)

            if CreditStatus.objects.filter(account=account).exists():
                return HttpResponse.BadRequest({"error": "Credit details already exist for this account"})
            data["created_by"] = str(user.user_id)
            data["account"] = account.account_id
            serializer=CreditStatusSerializer(data = data)

            if serializer.is_valid():
                serializer.save()
                account.status = ACCOUNT_STATUS.CREDIT_STATUS_ADDED.value
                account.save()
                return HttpResponse.Success({"credit_status" : serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def get(self, request):
        try:
            account_id = request.GET.get("account_id", "")
            if not account_id:
                return HttpResponse.BadRequest("Account id is required!")
            
            credit_status = CreditStatus.objects.get(account=account_id)
            serializer = CreditStatusGETSerializer(credit_status)
            return HttpResponse.Success({"credit_status": serializer.data})
            # else:
            #     credit_statuses = CreditStatus.objects.all()
            #     serializer = CreditStatusSerializer(credit_statuses, many=True)
            #     return HttpResponse.Success({"credit_status": serializer.data})
        
        except CreditStatus.DoesNotExist:
            return HttpResponse.BadRequest("CreditStatus not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def patch(self, request):
        try:
            data = request.data
            account_id = request.GET.get("account_id", "")
            account = Account.objects.get(account_id=account_id)
            credit_status = CreditStatus.objects.get(account=account)

            serializer = CreditStatusSerializer(credit_status, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"credit_status": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except CreditStatus.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def delete(self, request):
        try:
            credit_status = CreditStatus.objects.get(
                credit_status_id = request.GET.get('credit_status_id',"")
            )
            credit_status.delete()
            return HttpResponse.Success({"msg": 'Deleted document successfully'})
        except ObjectDoesNotExist:
            return HttpResponse.BadRequest("CreditStatus not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))