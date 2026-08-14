from rest_framework.views import APIView

from lead.models import Lead
from loan.models import TakeOverResidenceAddress
from loan.serializers.loan_take_over_serializer import LoanTakeOverDetails, TakeOverResidenceDetailsSerializer
from utils.envSetup import environment
from utils.sms import SMSService
# from utility.common_utils import calc_total_loan_taken
from ..models import Application
from users.models import User
from document.models import Document
from ..serializers import ApplicationOverviewSerializer , ApplicationDocSerializer
from asset.models import Asset
from account.models import Account
from account.serializers import AccountOverviewSerializer
from utils.responseHandler import HttpResponse
from utils.constants import APPLICATION_STATUS, ApplicationType , ROLES , LENDING_TYPE , APPLICANT_TYPE

from users.service.fcmService import FCMService
from ..services.application_services import ApplicationHelper
from loan.serializer import GPRSDocOverviewSerializer , GPRSDocSerializer
from credit_status.serializers import CreditStatusSerializer
from reference_pd.serializer import Reference_PDSerializer
from payment.serializers import BharatSwasthyaRepaymentModelSerializer
class ApplicationOverviewView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            application=Application.objects.get(application_id=request.GET.get('application_id', ""))
            if application.Originatedby.role in [ROLES.LOAN_OFFICER.value, ROLES.BRANCH_MANAGER.value] or application.application_loan_type == LENDING_TYPE.GOLD_LOAN:
                existing_loan = application.loan_take_over_app.all()
                
                existing_loan_data={}
                if len(existing_loan) > 0:
                    existing_loan_data = LoanTakeOverDetails(existing_loan.first()).data
                
                    existing_loan_data['show_inspection_screen_loan_amount']=int(existing_loan_data.get('requested_amount_from_radian'))>=int(environment.REQUEST_LOAN_AMOUNT_CHECK)
                   
                lead_data = Lead.objects.values().filter(account__account_id=application.account.account_id).first()
                bt_residence=TakeOverResidenceAddress.objects.filter(account__account_id=application.account.account_id).first()
                
                if bt_residence:
                    bt_residence=TakeOverResidenceDetailsSerializer(bt_residence).data

                else:
                    bt_residence={}
                show_inspection_field = False
               
                if application.application_type == ApplicationType.TAKEOVER.value and int(existing_loan_data.get('requested_amount_from_radian')) >= int(
                        environment.REQUEST_LOAN_AMOUNT_CHECK):
                    show_inspection_field = True
                # loan_amount=application.loan_amount
                # if loan_amount:
                #     if application.application_type == ApplicationType.TAKEOVER.value and  loan_amount>= int(
                #             environment.REQUEST_LOAN_AMOUNT_CHECK):
                #         show_inspection_field = True
                # if application.Originatedby.role == ROLES.LOAN_OFFICER.value or application.application_loan_type == LENDING_TYPE.GOLD_LOAN:
               
                if application.status!=APPLICATION_STATUS.APPLICATION_INITIATED.value:
                    ser=ApplicationOverviewSerializer(application).data
                    res = {"overview": ser}
                    res['overview']['lead'] = lead_data
                    # res['overview']['total_loan_taken'] = total_loan_taken
                    res['overview']['existing_loan_data']=existing_loan_data
                    # res['overview']['balance_amount_to_be_paid_to_the_customer']=balance_loan_amount
                    # res['overview']['total_net_payable']=net_payable
                    
                    disbursed_amount = res.get('overview', {}).get('disbursment_txn', [])
                    res['overview']['bt_residence_data']=bt_residence
                    res['overview']['show_inspection_screen'] = show_inspection_field
                    print("show_inspection_field: "+str(show_inspection_field))
                    res['overview']['show_inspection_screen_loan_amount']=show_inspection_field
                    res['overview']['total_disbursed_amount'] = float(0 if len(disbursed_amount) == 0 else sum(
                        [float(x['disbursement_amount']) for x in disbursed_amount]))
                    #bharat swasth payment details
                    bs_payment_details=application.bs_repayments.all().first()
                    res['overview']['bs_payment_details']=BharatSwasthyaRepaymentModelSerializer(bs_payment_details).data

                    return HttpResponse.Success(res)
                
                if not  Asset.objects.filter(application=application).exists():
                    application.eligible_amount=0
                    application.status=APPLICATION_STATUS.APPLICATION_INITIATED.value
                    application.save()


                ser = ApplicationOverviewSerializer(application).data
                res = {"overview": ser}
                res['overview']['lead'] = lead_data
                
                # res['overview']['total_loan_taken'] = total_loan_taken
                res['overview']['existing_loan_data'] = existing_loan_data
                disbursed_amount=res.get('overview',{}).get('disbursment_txn',[])
                res['overview']['show_inspection_screen'] = show_inspection_field
                print("show_inspection_field: "+str(show_inspection_field))
                
                res['overview']['bt_residence_data'] = bt_residence
                res['overview']['total_disbursed_amount']=float(0 if len(disbursed_amount)==0 else sum([float(x['disbursement_amount']) for x in disbursed_amount]))
                
            # res['overview']['balance_amount_to_be_paid_to_the_customer'] = balance_loan_amount
            # res['overview']['total_net_payable'] = net_payable
                return HttpResponse.Success(res)
            
            elif application.Originatedby.role == ROLES.RELATIONSHIP_MANAGER.value or application.application_loan_type == LENDING_TYPE.MSME_UNSECURED:
                rm_gprs = application.account.account_gprs_photos.filter(application_id__isnull=True)
                co_gprs =  application.application_gprs_photos.all()
                credit_status=application.account.creditstatus_account.all().first()
                reference_pd=application.account.refenrence_pd_account.all()
                app_doc=application.application_document.all()
                co_applicant=Account.objects.filter(
                    applicant=application.account.user,
                    applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
                )
                
                ser = ApplicationOverviewSerializer(application).data
                
                res = {"overview": ser}
              
                # res['overview']['lead'] = lead_data
                # res['overview']['existing_loan_data'] = existing_loan_data
                disbursed_amount = res.get('overview', {}).get('disbursment_txn', [])
                
                res['overview']['total_disbursed_amount'] = float(0 if len(disbursed_amount) == 0 else sum([float(x['disbursement_amount']) for x in disbursed_amount]))
                res['overview']['co_applicant'] = AccountOverviewSerializer(co_applicant, many=True).data
                res['overview']['credit_status'] = CreditStatusSerializer(credit_status).data
                res['overview']['reference_pd'] = Reference_PDSerializer(reference_pd , many=True).data
                gprs_images_serialized = GPRSDocSerializer(rm_gprs, many=True).data
                co_images_serialized = GPRSDocSerializer(co_gprs, many=True).data
                res['overview']['geo_tagged'] = gprs_images_serialized + co_images_serialized
                res['overview']['application_doc'] = ApplicationDocSerializer(app_doc, many=True).data
                return HttpResponse.Success(res)
            
            return HttpResponse.BadRequest({"error": "Invalid application type or role"})
        except Exception as e:
            return HttpResponse.InternalServerError({ "data": None, "error": str(e)})
            
    def post(self, request, *args, **kwargs):
        user=request.user
        application = Application.objects.get(application_id=request.GET.get('application_id', ""))
        if user.role == ROLES.RELATIONSHIP_MANAGER.value:
            application.status=APPLICATION_STATUS.APPLICATION_SENT_TO_CO.value
        else:
            application.status=APPLICATION_STATUS.APPLICATION_INITIATED.value
        msg_sent=SMSService().send_status_update(template='application_submitted',
                                        mobile=str(application.Originatedby.phone),
                                        application_no=application.application_number,
                                        customer_name=application.account.user.get_full_name()
                                        )
        print(msg_sent)
        application.save()
        # FCMService(user).generateNotification(
        #                             title="Application Created", message="Application Created Sucessfully "
        #                         )
        
        return HttpResponse.Success({})