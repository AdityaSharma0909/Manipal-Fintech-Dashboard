from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, FloatField, Q

from application.models import Application
from application.serializers import ApplicationModelSerializer, CreatApplicationSerializer, \
    ApplicationOverviewSerializer
from application.services.logic.application_approve_logic import ApplicationApproveLogic
from asset.models import Asset
from disbursements.models import Disbursement
from disbursements.service.constants import DisbursalConstants
from instance import custom_response_obj
from loan.models import TakeOverResidenceAddress
from loan.serializers.loan_take_over_serializer import LoanTakeOverDetails, TakeOverResidenceDetailsSerializer
from product.models import Product

from utility.crud_helper import CrudHelper
from utility.response_handler import ResponseSchema
from utils.constants import ROLES, APPROVED, APPLICATION_STATUS, ApplicationType
from users.service.fcmService import FCMService
from utils.envSetup import environment
from django.core.mail import send_mail


class ApplicationHelper:
    application_instance = CrudHelper(ApplicationModelSerializer)
    create_third_party_application=CrudHelper(CreatApplicationSerializer)
    def delete(self, application_id):
        return self.application_instance.delete_obj(application_id)
    # def approve_application(self, approved_by, response, comment, application_id, rejection_status):
    #     if approved_by.role==ROLES.CPC.value:
    #         application = self.__get_application_obj(application_id)

    #         if application:
    #             eligible_loan_amount_without_pan = int(environment.LOAN_PAN_CHECK_ELIGIBILITY)
    #             amount_request = application.loan_amount
    #             if amount_request is not None and amount_request > eligible_loan_amount_without_pan and (
    #                     application.account.pan_no is None or not application.account.pan_verified):
    #                 return ResponseSchema(data=f'required_pan_card', status_code=403,
    #                                       error_msg=f'required_pan_card', error_code=403).get_response()
    #             response_data=ApplicationApproveLogic().approve_application(approved_by, application, response, comment, rejection_status)
    #             FCMService([application.Originatedby]).generateNotification(
    #                     title="Radian Finserv", message=f"Application {application.application_number}({application.account.user.get_full_name()}) {response} by CPC."
    #                 )
    #             return ResponseSchema(data=response_data, status_code=200).get_response()
    #         else:
    #             return ResponseSchema(data=None, status_code=404, error_msg='Application not found', error_code=404).get_response()
    #     else:
    #         return ResponseSchema(data=None, status_code=401, error_msg='Only CPC is allowed', error_code=401).get_response()

    def approve_application(self, approved_by, response, comment, application_id, rejection_status, loan_amount=None, deviated_amount=None):
        # Retrieve the application object using the provided application_id
        application = self.__get_application_obj(application_id)
        print(1)
        # Check if the application exists, return a 404 response if not found
        if not application:
            return ResponseSchema(data=None, status_code=404, error_msg='Application not found', error_code=404).get_response()

        # Check if the approver's role is CPC
        if approved_by.role == ROLES.CPC.value:
            eligible_loan_amount_without_pan = int(environment.LOAN_PAN_CHECK_ELIGIBILITY)
            amount_request = application.loan_amount
            # Check if loan amount exceeds the eligible amount without PAN and if PAN details are missing or not verified
            if amount_request is not None and amount_request > eligible_loan_amount_without_pan and (
                    application.account.pan_no is None or not application.account.pan_verified):
                return ResponseSchema(data='required_pan_card', status_code=403,
                                    error_msg='required_pan_card', error_code=403).get_response()
            # Process the approval logic and get the response data
            response_data = ApplicationApproveLogic().approve_application(approved_by, application, response, comment, rejection_status)
            # Generate a notification for the originator
            FCMService([application.Originatedby]).generateNotification(
                title="Radian Finserv", message=f"Application {application.application_number} ({application.account.user.get_full_name()}) {response} by CPC."
            )
            # Return a successful response with the response data
            return ResponseSchema(data=response_data, status_code=200).get_response()

        # Check if the approver's role is Credit Manager
        elif approved_by.role == ROLES.CREDIT_MANAGER.value:
            # Check if the response is 'DEVIATE' and deviated_amount is not provided, return a 400 response
            if response == 'DEVIATE' and deviated_amount is None:
                return ResponseSchema(data=None, status_code=400, error_msg="deviated_amount is required", error_code=400).get_response()
            # Process the approval logic and get the response data
            response_data = ApplicationApproveLogic().approve_application(approved_by, application, response, comment, rejection_status, loan_amount, deviated_amount)
            if response_data.get("status") == "error":
                return ResponseSchema(data=None, status_code=400 , error_msg=response_data.get("message"),error_code=400).get_response()
    
            # Generate a notification for the originator
            FCMService([application.Originatedby]).generateNotification(
                title="Radian Finserv", message=f"Application {application.application_number} ({application.account.user.get_full_name()}) {response} by Credit Manager."
            )
            if response == 'DEVIATE':
                ApplicationHelper.send_deviation_approval_email(application)
            # Return a successful response with the response data
            return ResponseSchema(data=None, status_code=200).get_response()

        # Check if the approver's role is Business Head
        elif approved_by.role == ROLES.BUSINESS_HEAD.value:
            # Check if loan_amount or deviated_amount are not provided, return a 400 response
            if loan_amount is None or deviated_amount is None:
                return ResponseSchema(data=None, status_code=400, error_msg="'loan_amount' and 'deviated_amount' are required", error_code=400).get_response()
            # Process the approval logic and get the response data
            response_data = ApplicationApproveLogic().approve_application(approved_by, application, response, comment, rejection_status, loan_amount, deviated_amount)
            if response_data.get("status") == "error":
                return ResponseSchema(data=None, status_code=400 , error_msg=response_data.get("message") ,error_code=400).get_response()
            # Generate a notification for the originator
            FCMService([application.Originatedby]).generateNotification(
                title="Radian Finserv", message=f"Application {application.application_number} ({application.account.user.get_full_name()}) {response} by Business Head."
            )
            # Return a successful response with the response data
            return ResponseSchema(data=response_data, status_code=200).get_response()

        else:
            # Return a 401 response if the approver's role is unauthorized
            return ResponseSchema(data=None, status_code=401, error_msg='Unauthorized role', error_code=401).get_response()

    def __previous_disbursal_data(self, application_id):
        try:
            previously_disbursed = Disbursement.objects.get(application__application_id=application_id,
                                                            disbursement_status=DisbursalConstants.TAKEOVER.value)
            return previously_disbursed
        except Exception:
            return None

    def previous_disbursal_total(self, application_id):
        disbursement=list(Disbursement.objects.values('application__application_id',).filter(
                                                application__application_id=application_id,
                                                disbursement_status=DisbursalConstants.TAKEOVER.value)
                          .annotate(total_loan_taken=Sum('disbursement_amount',default=0,
                                                         output_field=FloatField())))
        return disbursement

    def application_disbursals(self, application_id):
        disbursals=list(Disbursement.objects.values().filter(
                                                application__application_id=application_id))
        return disbursals

    def get_takeover_disbursal_amount(self, application_id):

        previously_disbursed=self.__previous_disbursal_data(application_id=application_id)
        return previously_disbursed.disbursement_amount if previously_disbursed is not None else 0

    def get_takeover_previous_disbursal_date(self, application_id):
        previously_disbursed = self.__previous_disbursal_data(application_id=application_id)
        return previously_disbursed.disbursal_date if previously_disbursed is not None else None
    def __get_application_obj(self, application_id):
        try:
            application = Application.objects.get(application_id=application_id)
            return application
        except ObjectDoesNotExist():
            return None

    def update_kick_back_status(self, data):
        status=APPLICATION_STATUS.ROLL_BACK.value
        self.application_instance.update_obj(data={'status':status}, update_key_value=data.get('application_id'))
        return custom_response_obj(message='Application rolled back successfully', code=200)


    def update_takeover_docs(self, data):
        pass


    def get_pending_application(self, loan_manager, pagination, request):
        pending_status=[APPLICATION_STATUS.NEW_APPLICATION.value,
                        APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value,
                        APPLICATION_STATUS.BT_RESIDENCE_ADDED.value,
                        APPLICATION_STATUS.BT_NOMINEE_ADDED.value,
                        APPLICATION_STATUS.ASSET_ADDED.value,
                        APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value,
                        APPLICATION_STATUS.WHITE_GOODS_ADDED.value,
                        APPLICATION_STATUS.ROLL_BACK_BY_CPC.value,
                        APPLICATION_STATUS.GENERATE_LOAN_DOCUMENT.value,
                        APPLICATION_STATUS.LOAN_DISBURSED.value,
                        APPLICATION_STATUS.GOLD_COLLECTED.value,
                        ]
        pagination=pagination()
        applications=Application.objects.filter(Originatedby__user_id=loan_manager, status__in=pending_status)\
            .order_by('-modefied_at')
        paginated_data=pagination.paginate_queryset(applications, request=request)
        serializer=ApplicationModelSerializer(paginated_data, many=True)
        resp_data=pagination.get_paginated_response(serializer.data).data
        resp_data['status_code']=200
        resp_data['data']={}
        resp_data['data']['applications']=resp_data.pop('results', {})
        #resp_data['application']=resp_data.pop('results')
        return resp_data


    def create_application(self, data):
        product=data.get('product')
        data['status']=APPLICATION_STATUS.APPLICATION_INITIATED.value
        data['source']='JOFFIN'
        if product:
            product = Product.objects.get(product_id=product)
            data['tenure'] = product.tenure
            data['intrest_rate'] = product.interest_rate
            data['processing_fee_percent'] = product.processing_fee
            data['penalty_percent'] = product.penalty
            data['repayment_frequency'] = product.period
            data['lender'] = product.lender.lender_id
            data['amortization_type'] = product.amortization_type
        return self.create_third_party_application.add_obj(data=data)

    def get_third_part_application(self, third_party_user):
        return self.create_third_party_application.get_all_data(Q(Originatedby__user_id=third_party_user))


    def get_app_overview(self, application_id):
        application = Application.objects.get(application_id=application_id)

        existing_loan = application.loan_take_over_app.all()
        existing_loan_data = {}
        if len(existing_loan) > 0:
            existing_loan_data = LoanTakeOverDetails(existing_loan.first()).data
            existing_loan_data['show_inspection_screen_loan_amount'] = int(
                existing_loan_data.get('requested_amount_from_radian')) >= int(environment.REQUEST_LOAN_AMOUNT_CHECK)
        bt_residence = TakeOverResidenceAddress.objects.filter(
            account__account_id=application.account.account_id).first()
        if bt_residence:
            bt_residence = TakeOverResidenceDetailsSerializer(bt_residence).data

        else:
            bt_residence = {}
        show_inspection_field = False
        if application.application_type == ApplicationType.TAKEOVER.value and existing_loan_data.get('requested_amount_from_radian') >= int(
                environment.REQUEST_LOAN_AMOUNT_CHECK):
            show_inspection_field = True

        # loan_amount = application.loan_amount
        # if loan_amount:
        #     if application.application_type == ApplicationType.TAKEOVER.value and loan_amount >= int(
        #             environment.REQUEST_LOAN_AMOUNT_CHECK):
        #         show_inspection_field = True
        if application.status != APPLICATION_STATUS.APPLICATION_INITIATED.value:
            ser = ApplicationOverviewSerializer(application).data
            res = {"overview": ser}
            # res['overview']['total_loan_taken'] = total_loan_taken
            res['overview']['existing_loan_data'] = existing_loan_data
            # res['overview']['balance_amount_to_be_paid_to_the_customer']=balance_loan_amount
            # res['overview']['total_net_payable']=net_payable
            disbursed_amount = res.get('overview', {}).get('disbursment_txn', [])
            res['overview']['bt_residence_data'] = bt_residence
            res['overview']['show_inspection_screen'] = show_inspection_field
            res['overview']['show_inspection_screen_loan_amount'] = show_inspection_field
            res['overview']['total_disbursed_amount'] = float(0 if len(disbursed_amount) == 0 else sum(
                [float(x['disbursement_amount']) for x in disbursed_amount]))

            return res, application
        if not Asset.objects.filter(application=application).exists():
            application.eligible_amount = 0
            application.status = APPLICATION_STATUS.APPLICATION_INITIATED.value
            application.save()

        ser = ApplicationOverviewSerializer(application).data
        res = {"overview": ser}
         # res['overview']['total_loan_taken'] = total_loan_taken
        res['overview']['existing_loan_data'] = existing_loan_data
        disbursed_amount = res.get('overview', {}).get('disbursment_txn', [])
        res['overview']['show_inspection_screen'] = show_inspection_field
        res['overview']['bt_residence_data'] = bt_residence
        res['overview']['total_disbursed_amount'] = float(
            0 if len(disbursed_amount) == 0 else sum([float(x['disbursement_amount']) for x in disbursed_amount]))
        # res['overview']['balance_amount_to_be_paid_to_the_customer'] = balance_loan_amount
        # res['overview']['total_net_payable'] = net_payable
        return res, application
    


    def send_deviation_approval_email(application):
        bh_email = environment.DEFAULT_BH_EMAIL
        subject = f"Application {application.application_number} requires deviation approval"
        email_body =f"""
            Dear BH,

            Application {application.application_number} ({application.account.user.get_full_name()}) requires deviation approval.
            Please review the application at https://dev-app.radianfinserv.com/#/application/{application.application_id}.

            Best regards,
            Radian Finserv
        """

        from_email = environment.DEFAULT_FROM_EMAIL
   
        recipient_list = [bh_email,"kartik.patel@getafixtechnologies.com"]
        
        try:
            send_mail(subject, email_body, from_email, recipient_list,fail_silently=False)
            print(f"Email sent to {recipient_list} successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

