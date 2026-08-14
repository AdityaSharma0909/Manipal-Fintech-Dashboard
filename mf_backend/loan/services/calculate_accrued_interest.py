import datetime
import traceback

from django.db.models import Q, F, Value, ExpressionWrapper, DecimalField

from loan.models import Loan
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

class CalculateAccruedInterest:

    def __init__(self):
        self.__batch_size=int(environment.PROCESS_LOAN_BATCH)
        self.__todays_date=datetime.datetime.today().date()
        self.__process()

    def __process(self):
        try:
            total_loans_to_update=self.__get_total_eligible_loans()
            self.__update_in_batches(total_loans_to_update)
        except Exception as e:

            traceback.print_exc()
            #EmailReport().process(subject=f'Error in accrued interest task on {self.__todays_date}',message=str(e),)
    def __get_total_eligible_loans(self):
        loans=Loan.objects.filter(Q(status=LOAN_STATUS.GOOD_STANDING.value)|Q(status=LOAN_STATUS.BAD_STANDING.value),
                                Q(interest_last_accrued_on__lt=self.__todays_date)|Q(interest_last_accrued_on__isnull=True),accrual_on_hold=False, )\
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
                                Q(interest_last_accrued_on__isnull=True)|Q(interest_last_accrued_on__lt=self.__todays_date),accrual_on_hold=False)[start_index:end_index]
            # Calculate the interest per day using ExpressionWrapper
            try:
                for i in record_ids:
                    last_accured_on=i.interest_last_accrued_on if i.interest_last_accrued_on is not None else i.disbursed_date.date()
                    days_diff=get_days_difference(last_accured_on)
                    interest_per_day = self.__interest_per_day(i.principal_remaining, i.intrest_rate)
                    i.interest_accrued_till_date += round(float(interest_per_day*days_diff),2)
                    i.interest_last_accrued_on = datetime.datetime.now().date()
                    records_to_save.append(i)

                # Save the modified records
                for record in records_to_save:
                    record.save()
            except Exception as e:

                traceback.print_exc()
                #EmailReport().process(subject=f'Error in accrued interest task on {self.__todays_date}',
                #                      message=str(e), )
                pass



    def __interest_per_day(self, principal_remaining, interest_rate):
        interest=(float(principal_remaining) * float(interest_rate)) / (365 * 100)
        return round(interest,2)


