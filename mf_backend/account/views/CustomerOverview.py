from rest_framework.views import APIView

from lead.models import Lead
from ..models import Account ,BankAccount
from users.models import User
from document.models import Document
from loan.serializer import GPRSDocSerializer
from ..serializers import AccountOverviewSerializer, NomineeDetailsSerializer
from utils.responseHandler import HttpResponse
from utils.constants import ACCOUNT_STATUS , ROLES
from users.service.fcmService import FCMService
from application.serializers import ApplicationOverviewSerializer 
from application.models import Application
from credit_status.serializers import CreditStatusSerializer
from reference_pd.serializer import Reference_PDSerializer

class CustomerOverviewView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        account=Account.objects.get(account_id=request.GET.get('account_id', ""))
        account_creator_role = account.created_by.role
        res = {"detail": "Role not authorized"}
        # if account.status!=ACCOUNT_STATUS.BANK_DETAILS_ADDED.value:
        #     return HttpResponse.BadRequest("You need to add bank details to your account")
        
        # overview = OverviewDataObject(,bankaccount,documents)
        nominee_details = account.nomieedetails_account.all()
        gprs = account.account_gprs_photos.all()
        credit_status=account.creditstatus_account.all().first()
        reference_pd=account.refenrence_pd_account.all()
        lead_data = Lead.objects.values().filter(account__account_id=account.account_id).first()
        if account_creator_role in [ROLES.LOAN_OFFICER.value , ROLES.BRANCH_MANAGER.value] :
            ser = AccountOverviewSerializer(account)
            res = {"overview": ser.data}
            res['overview']['lead'] = lead_data
            res['overview']['nominee'] = NomineeDetailsSerializer(nominee_details, many=True).data
        elif account_creator_role == ROLES.RELATIONSHIP_MANAGER.value:
            ser = AccountOverviewSerializer(account)
            res = {"overview": ser.data}
            res['overview']['lead'] = lead_data
            res['overview']['credit_status'] = CreditStatusSerializer(credit_status).data
            res['overview']['reference_pd'] = Reference_PDSerializer(reference_pd , many=True).data
            res['overview']['geo_tagged'] = GPRSDocSerializer(gprs , many=True).data
        return HttpResponse.Success(res)
    
    def post(self,request):
        user = request.user
        account=Account.objects.get(account_id=request.GET.get('account_id', ""))
        account.status =ACCOUNT_STATUS.ACCOUNT_CONFIRMED.value
        account.save()
    
        # FCMService(user).generateNotification(
        #             title="Customer Account", message="Customer Account Created Sucessfully "
        #         )
        return HttpResponse.Success({})

class AllAplications(APIView):
    def get(self,request, *args, **kwargs):
       
        account=Account.objects.get(account_id=request.GET.get('account_id', ""))
        # if account.status!=ACCOUNT_STATUS.BANK_DETAILS_ADDED.value:
        #     return HttpResponse.BadRequest("You need to add bank details to your account")
        
        # overview = OverviewDataObject(,bankaccount,documents)
        applications=Application.objects.filter(account=account)
        ser=ApplicationOverviewSerializer(applications,many=True)
        
        return HttpResponse.Success({"overview": ser.data})
    
    



