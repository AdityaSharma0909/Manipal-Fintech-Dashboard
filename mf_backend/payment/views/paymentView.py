from payment.models import Repayment
from payment.serializers import RepaymentStatusSerializer
from loan.models import Loan
from application.models import Application
from account.models import Account
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from rest_framework.views import APIView
from branch.models import BranchUserMapping
import traceback

class PaymentView(APIView):
    def get(self,request):
        try:
            user = request.user
            payments_data=[]
            if request.user.role in [ROLES.CPC.value, ROLES.BUSINESS_HEAD.value]:
                payments=Repayment.objects.all()
            
            elif user.role==ROLES.BRANCH_MANAGER.value:
                branch_user_mapping = BranchUserMapping.objects.get(user=request.user)
                branch = branch_user_mapping.branch
                payments=Repayment.objects.filter(loan__branch=branch)
               
            elif user.role == ROLES.CUSTOMER.value:
                loan_id = request.GET.get('loan_id')
                if loan_id:
                    try:
                        payments = Repayment.objects.filter(loan__loan_id=loan_id)
                    except Loan.DoesNotExist:
                        return HttpResponse.BadRequest({"error":"Loan Not Found"})  
                else:
                    payments = Repayment.objects.filter(loan__application__account__user=request.user)
            else:
                return HttpResponse.BadRequest({"error": "Invalid user role"})
            serializer = RepaymentStatusSerializer(payments, many=True)
            return HttpResponse.Success({"Payments": serializer.data}) 

        except Repayment.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))