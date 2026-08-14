from django.db.models import Q
from rest_framework.views import APIView
from account.models import Account
from application.models import Application
from application.serializers import LoanTakeOverApplicationSerializer
from lender.models import Lender
from lender.serializers import LenderSerializer
from loan.models import LoanTakeOver
from loan.serializers.loan_take_over_serializer import LoanTakeOverSerializer, LoanTakeOverDetails
from loan.services.loan_services import LoanHelper
from loan.services.loan_take_over import LoanTakeOverHelper
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj
from utils.constants import APPLICATION_STATUS, ApplicationType
from utils.envSetup import environment
from utils.sms import SMSService


class LoanTakeOverUtil(ApiFramework):

    def __init__(self, data, method, user,id=None, **kwargs):
        super().__init__()
        self.__data = data
        self.__method = method
        self.__id = id
        self.__kwargs = kwargs
        self.__response = {}
        self.__orginated_by=user.user_id
        self.__branch=user.lm_branch_map.all().first().branch_id
        self.__service = LoanTakeOverHelper(LoanTakeOverApplicationSerializer)

    def format_request(self):
        if self.__method=='POST':
            self.__app_payload=self.__service.create_app_payload(data=self.__data, id=self.__id)
            # print(self.__app_payload)
            self.__take_over_payload = self.__service.create_take_over_payload(self.__data)
        elif self.__method=='PATCH':
            self.__take_over_payload=self.__service.create_take_over_payload(self.__data)

    def run_logic(self):
        eligible_loan_amount_without_pan = int(environment.LOAN_PAN_CHECK_ELIGIBILITY)
        if self.__method != "GET" and self.__id is None:
            self.__response=custom_response_obj(message='account id is required', code=400)
        else:
            if self.__method == 'GET':
                self.__response = LoanTakeOverHelper(LoanTakeOverDetails).get_data_by_id(self.__id)
            elif self.__method == 'POST':
                self.__app_payload['account_id']=self.__id
                self.__app_payload['Originatedby']=self.__orginated_by
                self.__app_payload['branch']=self.__branch

                app_exist=self.__service.get_all_data(Q(account__account_id=self.__id,
                                                        application_type=ApplicationType.TAKEOVER.value,
                                                        status__in=[
                                                            APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value,
                                                            APPLICATION_STATUS.TAKE_OVER.value,
                                                            APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value,
                                                            APPLICATION_STATUS.TAKE_OVER_APPROVED.value,

                                                            ]))
                requested_loan_amount=self.__take_over_payload.get('requested_amount_from_radian')


                account=Account.objects.get(account_id=self.__id)
                loan_eligibility = LoanHelper().check_loan_amount_pan_eligibility(
                    amount_request=requested_loan_amount,
                    amount_requested_by=account)

                # if len(app_exist.get('data',[]))>0:
                #     self.__response=custom_response_obj(message={'msg':f'Take over application with this account already exist,cannot create new application until previous application is disbursed'},
                #                                         code=200,
                #                                         error_code=200)
                if loan_eligibility.get('status_code')==403:
                    self.__response=custom_response_obj(message={'msg':f'required_pan_card',
                                           }, code=200, error_msg={'msg':f'required_pan_card',
                                           }, error_code=200)
                else:
                    application = self.__service.add_obj(self.__app_payload, validate_add=True, validate_model=Account,value=self.__id)
                    if application.get('status_code')==200:
                        self.__take_over_payload['application']=application.get('data').get('application_id')
                        take_over_data=LoanTakeOverHelper(LoanTakeOverSerializer).add_obj(self.__take_over_payload)
                        application.get('data')['show_inspection_screen']=requested_loan_amount>=int(environment.REQUEST_LOAN_AMOUNT_CHECK)
                        if take_over_data.get('status_code')==200:
                            lender=application.get('data').get('existing_loan_data',{}).get('lender', None)
                            application.get('data')['existing_loan_data'] = take_over_data.get('data')
                            if lender:
                                application.get('data')['existing_loan_data']['lender'] = LenderSerializer(Lender.objects.get(lender_id=application.get('data')['existing_loan_data']['lender'])).data
                            else:
                                application.get('data')['existing_loan_data']['lender'] = None
                            self.__response = application
                            application=Application.objects.get(application_id=application.get('data').get('application_id'))
                            SMSService().send_status_update(template='application_submitted',
                                                            mobile=str(application.Originatedby.phone),
                                                            application_no=application.application_number,
                                                            customer_name=application.account.user.get_full_name()
                                                            )
                        else:
                            self.__service.delete_obj(application.get('data').get('application_id'))
                            self.__response=custom_response_obj(message='Failed to create take over loan object', code=400,
                                                                error_msg=take_over_data.get('data'), error_code=400)

            elif self.__method == 'PATCH':
                requested_loan_amount = self.__take_over_payload.get('requested_amount_from_radian')
                loan_take_over_service=LoanTakeOverHelper(LoanTakeOverSerializer)
                account = LoanTakeOver.objects.get(take_over_id=self.__id).application.account
                loan_eligibility = LoanHelper().check_loan_amount_pan_eligibility(
                    amount_request=requested_loan_amount,
                    amount_requested_by=account)
                if loan_eligibility.get('status_code') == 403:
                    self.__response = custom_response_obj(message={
                        'msg': f'required_pan_card',
                    }, code=200, error_msg={
                        'msg': f'required_pan_card',
                    }, error_code=200)
                else:
                    self.__response = loan_take_over_service.update_obj(data=self.__take_over_payload,
                                                                        update_key_value=self.__id)
                    self.__response.get('data')['show_inspection_screen']=requested_loan_amount>=int(environment.REQUEST_LOAN_AMOUNT_CHECK)


                    if self.__response.get('status_code')==200:
                        lender=self.__take_over_payload.get('lender', None)
                        if lender:
                            takeover_data=LoanTakeOver.objects.get(take_over_id=self.__id)
                            if takeover_data.application.lender.lender_id!=lender:
                                takeover_data.application.lender=takeover_data.lender
                                takeover_data.application.save()

    def process(self):
        return self.__response


class LoanTakeOverView(APIView):

    def get(self, request):
        take_over_id=request.query_params.get('take_over_id')
        return LoanTakeOverUtil(data=None, method='GET', user=None, id=take_over_id).main()

    def post(self, request):
        data = request.data
        id = request.GET.get('account_id', None)

        return LoanTakeOverUtil(data=data, method='POST', id=id, user=request.user).main()

    def patch(self, request):
        data = request.data
        id=request.query_params.get('take_over_id')
        return LoanTakeOverUtil(data=data, method='PATCH', id=id, user=request.user).main()
