import traceback

from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from utils.constants import ROLES, LOAN_STATUS
from loan.models import Loan
from loan.serializer import OtherLenderAppraisalSerializer
from utils.envSetup import environment



class OtherLenderAppraisalView(APIView):
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            loanId = data.get('loan', None)
            if not loanId:
                return HttpResponse.BadRequest("loan_id is required")
            
            # if user.role !=  ROLES.ASSISTANT_BRANCH_MANAGER or user.role !=  ROLES.BRANCH_MANAGER:
            #     return HttpResponse.Forbidden("Not allowed")

            branch=request.user.lm_branch_map.all().first().branch
            # loan = Loan.objects.get(loan_id=loanId)
            loan = Loan.objects.get(loan_id=loanId, branch=branch)


            # if loan.lender.lender_code == environment.RADIAN_LENDER_CODE:
            #     return HttpResponse.Forbidden("Not allowed for own book")

            # if (user.role !=  ROLES.ASSISTANT_BRANCH_MANAGER.value and user.role !=  ROLES.BRANCH_MANAGER.value):
            #     return HttpResponse.Forbidden("Access Denied")

            # if (loan.status != LOAN_STATUS.NEW.value and loan.status != LOAN_STATUS.GOOD_STANDING.value):
            #     return HttpResponse.Forbidden("Not allowed")

            
            if loan.lender.lender_code != environment.RADIAN_LENDER_CODE and \
                (user.role ==  ROLES.ASSISTANT_BRANCH_MANAGER.value or user.role ==  ROLES.BRANCH_MANAGER.value) and \
                loan.status == LOAN_STATUS.GOOD_STANDING.value:
                
                data['created_by'] = user.user_id
                ser = OtherLenderAppraisalSerializer(data=data)
                if ser.is_valid():
                    ser.save()
                    loan.status = LOAN_STATUS.SUBMITTED_TO_LENDER.value
                    loan.save()
                    return HttpResponse.Success({"other_lender_appraisal": ser.data})
                return HttpResponse.BadRequest(ser.errors)
            else:
                return HttpResponse.Forbidden("Not allowed")
        
        except Loan.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        