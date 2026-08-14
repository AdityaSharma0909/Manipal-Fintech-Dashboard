import datetime
import json
import uuid

from django.core.exceptions import ObjectDoesNotExist
from dateutil import parser as parser
from application.serializers import AddLoanAPISerializer
from loan.models import Loan, LoanEMIRecord
from loan.serializer import LoanSerializer
from loan.serializers.bill_generation_serializier import BillGenerationSerializer
from loan.serializers.loan_emi_schedule_record import LoanEmiScheduleSerializer, LoanEmiRecordSerializer
from loan.service import LoanService
from loan.services.loan_emi_record_service import LoanEmiService
from utility.common_utils import get_period_in_numbers, serializer_instance, get_days_difference,custom_response_obj
from utility.crud_helper import CrudHelper
from utils.constants import LOAN_STATUS
from utils.envSetup import environment
from datetime import timedelta as timedelta

class LoanHelper:
    loan_bill_generation = CrudHelper(serializer=BillGenerationSerializer)
    def get_all_loans_by_user(self):
        pass

    def get_loan_by_id(self):
        pass


    def add_take_over_data(self):
        pass

    
    def get_loan_data(self, loan_id, loan=None):
                
            try:
                loan = Loan.objects.get(loan_id=loan_id)
            except Loan.DoesNotExist:
                return {}  # Return an empty dictionary if loan is not found

            # Serialize the loan object using LoanSerializer
            serializer = LoanSerializer(loan)
            loan_data = serializer.data

            return loan_data

    def check_loan_amount_pan_eligibility(self, amount_request, amount_requested_by):
        try:
            eligible_loan_amount_without_pan=int(environment.LOAN_PAN_CHECK_ELIGIBILITY)
            if amount_request is not None and amount_request>eligible_loan_amount_without_pan and (amount_requested_by.pan_no is None or not amount_requested_by.pan_verified):
                return custom_response_obj(message=f'required_pan_card',
                                           code=403,
                                           error_msg=f'required_pan_card',
                                           error_code=403)
            else:
                return custom_response_obj(message=f'Eligible for loan amount above {eligible_loan_amount_without_pan}',
                                           code=200)
        except ObjectDoesNotExist:
            return custom_response_obj(message='Application not found', error_msg='Application not found',
                                       error_code=404, code=404)



    def update_last_payment_transaction(sellf, loan_id, payment_date):
        try:
            loan=Loan.objects.get(loan_id=loan_id)
            loan.last_payment_date=payment_date
            loan.save()
        except ObjectDoesNotExist:
            return None

    def roll_back_loan(self, loan_ids):
        try:
            Loan.objects.filter(loan_id__in=loan_ids).delete()
        except ObjectDoesNotExist():
            pass

    def create_loan_emi_header(self, emi_schedule_data, record_data):
        CrudHelper(serializer=LoanEmiScheduleSerializer).add_obj(emi_schedule_data)
        CrudHelper(serializer=LoanEmiRecordSerializer).add_obj(record_data, many=True)


    def get_loan_payment_data(self, application):
        """
            This method is used to create loan emi schedule
        """

        emi_data=LoanEmiService().create_or_get_schedule(application.application_id)
        due_dates=self.get_next_due_date(emi_data)

        return due_dates, emi_data

    def create_loan_obj(self, application, loan_disbursal_date, user, contra_loan=False):
        app_data=serializer_instance(AddLoanAPISerializer, read_only=True, data=application).get('data')
        disbursal_date=parser.parse(loan_disbursal_date)
        loan_basic_data, emi_data = self.get_loan_payment_data(application)
        loan_dict={}
        loan_dict.update(**app_data)
        loan_dict["loan_amount"] = application.loan_amount
        loan_dict['disbursal_amount'] = float(application.loan_amount)
        loan_dict['disbursed_amount'] = application.disbursal_amount
        loan_dict['total_goods_price'] = application.total_goods_price
        loan_dict["current_amount"] = application.loan_amount
        loan_dict["principal_remaining"] = application.loan_amount
        loan_dict["interest_remaining"] = ((application.loan_amount * (application.product.interest_rate / 100))/12)*application.product.tenure
        loan_dict['period'] = get_period_in_numbers(application.product.period)
        loan_dict["loan_type"] = application.product.product_type
        loan_dict["loan_number"] = LoanService().generate_loan_number()
        loan_dict["application"] = str(application.application_id)
        loan_dict["intrest_rate"] = application.intrest_rate
        loan_dict["term"] = application.tenure
        loan_dict["days_past_dues"] = 0
        loan_dict['penalty'] = 0
        loan_dict['lender'] = application.lender.lender_id
        loan_dict['processing_fee'] = application.loan_amount * application.product.processing_fee
        loan_dict['disbursed_date'] = disbursal_date
        loan_dict["status"] = LOAN_STATUS.GOOD_STANDING.value
        loan_dict["branch"] = str(application.Originatedby.lm_branch_map.all().first().branch.branch_id)
        loan_dict['next_due_date']=loan_basic_data.get('next_due_date')
        loan_dict['next_due_generation_date']=loan_basic_data.get('next_due_generation_date')
        loan_dict['current_emi']=loan_basic_data.get('current_installment')
        loan_dict['net_disbursed_amount']=application.net_disbursed_amount
        accrual_amount, accrual_date = self.__get_emi_accrued_till_date(disbursal_date, application.loan_amount,
                                                                        application.intrest_rate)

        loan_dict["interest_accrued_till_date"] = accrual_amount
        loan_dict['interest_last_accrued_on'] = accrual_date
        if contra_loan:
            loan_dict['loan_amount']=application.contra_loan_amount
            loan_dict['disbursal_amount']=application.contra_loan_net_payable_balance
            loan_dict['disbursed_amount']=application.contra_loan_net_payable_balance
            loan_dict['stamp_duty']=application.contra_loan_stamp_duty_amount
            loan_dict['intrest_rate']=application.product.contra_product.interest_rate
            loan_dict['net_disbursed_amount']=application.contra_loan_net_payable_balance
            loan_dict['gst']=application.contra_loan_gst_amount
            loan_dict["current_amount"] = application.contra_loan_amount
            loan_dict['processing_fee']=application.contra_loan_processing_fee_amount
            loan_dict["principal_remaining"] = application.contra_loan_amount
            loan_dict["loan_type"] = application.product.contra_product.product_type
            loan_dict["interest_remaining"] = ((application.contra_loan_amount * (application.product.contra_product.interest_rate / 100))/12)*application.product.contra_product.tenure
            accrual_amount, accrual_date = self.__get_emi_accrued_till_date(disbursal_date,
                                                                            application.contra_loan_amount,
                                                                            application.product.contra_product.interest_rate,
                                                                            )
            loan_dict["interest_accrued_till_date"] = accrual_amount
            loan_dict['interest_last_accrued_on'] = accrual_date

        loan_result=serializer_instance(LoanSerializer, data=loan_dict)
        """
            #check if disbursal date is of previous date, then create bills to backdate
        """

        print("DATES DATA+++>",disbursal_date, disbursal_date.date()<datetime.datetime.now().date())
        if disbursal_date.date()<datetime.datetime.now().date():
            self.__create_bills_in_back_date(loan=loan_result.get('data').get('loan_id'))
        return loan_result


    def __get_emi_accrued_till_date(self, disbursal_date, principal_remaining, interest_rate):

        days_diff = get_days_difference(disbursal_date.date())
        if days_diff==0:
            return 0,None
        else:
            interest_per_day=self.__interest_per_day(principal_remaining, interest_rate)
            return round(float(interest_per_day*days_diff),2), datetime.datetime.now().date()

    def __interest_per_day(self, principal_remaining, interest_rate):
        interest=round((float(principal_remaining) * float(interest_rate)/ (365 * 100)),2)
        return interest


    def get_next_due_date(self, loan_schedule):
        current_date = datetime.datetime.now().date()
        current_due_date=None
        next_due_date=None
        emi=None
        pre_bill_generation_days = int(environment.PRE_BUILD_DAYS)
        current_installment=0
        next_due_generation_date=None
        for index, installment in loan_schedule.items():
            print("installment[date]:::")
            print(installment["date"])
            installment_date = datetime.datetime.strptime(installment["date"], "%Y-%m-%d").date()
            
            if current_date >= installment_date:
                current_due_date = installment_date
            else:
                next_due_date = installment_date
                emi=installment['emi']
                current_installment=int(index)+1
                next_due_generation_date=parser.parse(str(next_due_date)) - timedelta(days=pre_bill_generation_days)
                break  # Stop loop once the next due date is found
        return {
            'due_date': current_due_date.strftime("%Y-%m-%d") if current_due_date else None,
            'next_due_date': next_due_date.strftime("%Y-%m-%d") if next_due_date else None,
            'emi': emi,
            'current_installment': current_installment,
            'next_due_generation_date': next_due_generation_date.strftime("%Y-%m-%d") if next_due_generation_date else None
        }

        # return {'due_date':current_due_date.__str__(),
        #         'next_due_date':next_due_date.__str__(),
        #         'emi':emi,
        #         'current_installment':current_installment,
        #         'next_due_generation_date':next_due_generation_date.__str__()
        #         }
        
                


    """
        Creates old bills while back date
    """


    def __create_bills_in_back_date(self, loan):
        loan_emi_records=LoanEMIRecord.objects.filter(loan_emi_header__loan=loan).order_by('due_date')
        bill_records=[]
        records_added=[]
        for record in loan_emi_records:
            print("date",record.bill_generation_date, datetime.datetime.today().date())
            if record.bill_generation_date < datetime.datetime.today().date():
                if str(record.loan_emi_record_id) not in records_added:
                    records_added.append(record.loan_emi_record_id)
                    bill_records.append({'loan': record.loan_emi_header.loan.loan_id,
                                         'emi_record': record.loan_emi_record_id,
                                         'total_penalty': record.loan_emi_header.loan.penalty,
                                         'principal_remaining': record.principal,
                                         'interest_remaining': record.interest,
                                         'penalty_remaining': record.loan_emi_header.loan.penalty,
                                         'total':record.loan_emi_header.emi_amount,
                                         'total_paid':0
                                         })
                else:
                    print("bills",str(record.loan_emi_record_id))
            else:
                break
        print("records",bill_records)
        self.loan_bill_generation.add_obj(data=bill_records, many=True)


