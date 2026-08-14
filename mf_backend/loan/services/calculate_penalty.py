import datetime
import traceback

from django.db.models import Q, F, Value, ExpressionWrapper, DecimalField

from loan.models import Loan, LoanEMIRecord
from utility.common_utils import divide_into_batches, total_days_in_a_month, get_days_difference
from utility.send_email_in_background import EmailReport
from utils.constants import LOAN_STATUS, PERIOD
from utils.envSetup import environment

"""
    This API takes care of Accrued Interest rate
    flow:- 1. Pick all loans whose status is active good/bad standing and whose accrued date is null or less than today, and accrual is not on hold
           2. divide the queried loans into batch
           3. update interest accrual on each loan batch wise
"""


# TODO send loan id number in exception, create mechanism to track over how many days a particular loan obj has failed to update interest accrued

class CalculatePenalty:

    def __init__(self):
        self.__batch_size=int(environment.PROCESS_LOAN_BATCH)
        self.__todays_date=datetime.datetime.today().date()
        self.__process()

    def __process(self):
        try:
            total_loans_to_update=self.__get_total_eligible_loans()
            print('penalty',total_loans_to_update)
            self.__update_in_batches(total_loans_to_update)
        except Exception as e:

            traceback.print_exc()
            EmailReport().process(subject=f'Error in accrued interest task on {self.__todays_date}',message=str(e),)
    def __get_total_eligible_loans(self):
        loans=Loan.objects.filter(Q(status=LOAN_STATUS.GOOD_STANDING.value)|Q(status=LOAN_STATUS.BAD_STANDING.value),
                                    due_date__lt=datetime.datetime.today().date())\
            .count()
        return loans

    def __update_in_batches(self, total_records):
        # Calculate the number of batches
        num_batches = (total_records // int(self.__batch_size)) + 1

        # Perform bulk update in batches
        for batch_number in range(num_batches):
            records_to_save=[]
            start_index = batch_number * self.__batch_size
            end_index = start_index + self.__batch_size
            record_ids = Loan.objects.filter(Q(status=LOAN_STATUS.GOOD_STANDING.value)|Q(status=LOAN_STATUS.BAD_STANDING.value),
                                             due_date__lt=datetime.datetime.today().date())[start_index:end_index]
            # Calculate the interest per day using ExpressionWrapper

            for i in record_ids:
                loan_obj=i
                get_days_past=get_days_difference(loan_obj.due_date.date())
                interest=self.__interest_part(loan_obj.principal_remaining, loan_obj.intrest_rate,loan_obj.application.product.period)
                penalty=round(float((loan_obj.application.product.penalty/100)) * float(interest),2)
                if int(penalty)==0:
                    penalty=int(penalty+0.5)
                loan_obj.penalty=penalty
                loan_obj.days_past_dues=loan_obj.days_past_dues+get_days_past
                records_to_save.append(loan_obj)

            # Save the modified records
            for record in records_to_save:
                record.save()


    def __penalty_per_day(self, principal_remaining, interest_rate, period, penalty_percentage):
        if period == PERIOD.WEEKLY.value:
            period = 52
        elif period == PERIOD.MONTHLY.value:
            period = 12
        elif period == PERIOD.QUATERLY.value:
            period = 4
        interest=(float(principal_remaining) * float(interest_rate)) / (period * 100)
        return interest * penalty_percentage

    def __interest_part(self, principal_remaining, interest_rate, period):
        if period == PERIOD.WEEKLY.value:
            period = 52
        elif period == PERIOD.MONTHLY.value:
            period = 12
        elif period == PERIOD.QUATERLY.value:
            period = 4
        interest=(float(principal_remaining) * float(interest_rate)) / (period * 100)
        return round(interest,2)

