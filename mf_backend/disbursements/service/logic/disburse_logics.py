import datetime
import traceback

from django.core.exceptions import ObjectDoesNotExist

from account.service.insurance_service import InsuranceService
from application.models import Application
from disbursements.serializers import DisbursementSerializer
from disbursements.service.logic.disburse_crud import DisburseCrud
from loan.services.loan_services import LoanHelper
from loan.services.logic.gl_pl_logic import LoanGLPL
from utility.common_utils import custom_response_obj
from utils.constants import APPLICATION_STATUS, ApplicationType
from users.service.fcmService import FCMService
from utils.envSetup import environment
from utils.sms import SMSService


class DisburseLoan:
    loan_helper = LoanHelper()

    def __init__(self):
        self.__loan_ids = []

    def process(self, data, user):
        application = self.__get_application(application_number=data.get('application_number'))
        if application:
            if application.status == APPLICATION_STATUS.LOAN_DISBURSED.value:
                return custom_response_obj(message=None, code=401,
                                           error_msg="Application is already disbursed",
                                           error_code=401)

            print("status=======>",application.status)
            if application.status == APPLICATION_STATUS.TAKE_OVER_APPROVED.value:

                loan_eligibility = LoanHelper().check_loan_amount_pan_eligibility(
                    amount_request=data.get('disbursement_amount'),
                    amount_requested_by=application.account)

                if loan_eligibility.get('status_code')==403:
                    return custom_response_obj(
                        message={'msg':f'required_pan_card'},
                        code=200,
                        error_msg=f'required_pan_card',
                        error_code=200)
                return self.__create_disburse_only(data, application, user)
            else:
                response = self.__create_disburse_and_loan(data, application, user)
                return response
        else:
            return custom_response_obj(message=None, code=404,
                                       error_code=404,
                                       error_msg=f'Application with number {data.get("application_number")} not found')

    def __create_disburse_only(self, data, application, user):
        disburse_data = self.__create_disburse_payload(disbursal_data=data,
                                                       loan_id=None,
                                                       application=application,
                                                       create_by=user.user_id)

        FCMService([application.Originatedby]).generateNotification(
            title="Radian Finserv",
            message=f"Amount of ₹ {data['disbursement_amount']} is been disbursed to {application.account.user.first_name} {application.account.user.last_name}."
        )
        response=self.__create_disburse_obj(disbursal_data=disburse_data)
        if response.get('status_code')==200:
            self.__update_application(application, APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value,
                                      data.get('disbursal_date'))
        return response

    def __create_disburse_and_loan(self, data, application, user):
        loan_disburse_date = data.get('disbursal_date')
        # print('payload', data)
        # print('loan disburse date=======>',loan_disburse_date)
        already_disbursed=application.net_disbursed_amount
        if already_disbursed>0:
            application.net_disbursed_amount= application.net_disbursed_amount - data.get('disbursement_amount') if application.net_disbursed_amount >  data.get('disbursement_amount') else  data.get('disbursement_amount')-application.net_disbursed_amount
        else:
            application.net_disbursed_amount=data.get('disbursement_amount')
        application.save()
        loan_data = self.__create_loan(application, loan_disburse_date, user)

        if loan_data.get('status_code') == 400:
            return custom_response_obj(message=None, code=400,
                                       error_msg=loan_data.get('data'),
                                       error_code=400)
        loan_id = loan_data.get('data').get('loan_id')
        self.__loan_ids.append(loan_id)
        disburse_data = self.__create_disburse_payload(disbursal_data=data,
                                                       loan_id=loan_id,
                                                       application=application,
                                                       create_by=user.user_id)
        response = self.__create_disburse_obj(disbursal_data=disburse_data)
        if response.get('status_code') == 400:
            self.__roll_back_loan_obj()
            return response
        self.__update_application(application, APPLICATION_STATUS.LOAN_DISBURSED.value,loan_disburse_date)
        return response

    def __create_disburse_payload(self, disbursal_data, loan_id, application, create_by):
        disbursal_data["loan"] = loan_id
        disbursal_data["application"] = str(application.application_id)
        disbursal_data["created_by"] = create_by

        return disbursal_data

    def __create_disburse_obj(self, disbursal_data):

        disburse_crud = DisburseCrud(DisbursementSerializer).add_obj(data=disbursal_data)
        if disburse_crud.get('status_code') == 400:
            return custom_response_obj(message=None, code=400,
                                       error_msg=disburse_crud.get('data'),
                                       error_code=400)
        return disburse_crud

    def __update_application(self, application, status, disbursal_date):
        application.disbursed_date =disbursal_date
        application.status = status
        application.save()
        SMSService().send_status_update(template='application_disbursed',
                                        mobile=str(application.Originatedby.phone),
                                        application_no=application.application_number,
                                        customer_name=application.account.user.get_full_name()
                                        )

        if status==APPLICATION_STATUS.LOAN_DISBURSED.value or (application.application_type==ApplicationType.TAKEOVER.value and status==APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value):
            InsuranceService().mark_insurance_paid(account=application.account,
                                                   application=application, status=status)


    def __create_loan(self, application, loan_disbursal_date, user):

        check_if_contra, msg = LoanGLPL().process(application)

        if check_if_contra:
            gl_pl_loan = self.loan_helper.create_loan_obj(application, loan_disbursal_date, user, contra_loan=True)
            if gl_pl_loan.get('status_code') == 200:
                self.__loan_ids.append(gl_pl_loan.get('data').get('loan_id'))

        return self.loan_helper.create_loan_obj(application, loan_disbursal_date, user)

    def __get_application(self, application_number):
        try:
            application = Application.objects.get(application_number=application_number)
            return application
        except ObjectDoesNotExist:
            return None
        except Exception:
            traceback.print_exc()
            return None

    def __roll_back_loan_obj(self):
        self.loan_helper.roll_back_loan(self.__loan_ids)
