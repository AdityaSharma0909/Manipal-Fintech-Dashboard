"""
    This class handles demand/bill generation

    Flow:
        1. Pick the loan / loans emi who next due generation date is today
        2. generate bill and update next due generation date and next due date, apply if any penalty is applicable
        3. add it to bill generated table
"""

import datetime
from django.db.models import Q
from loan.models import Loan, LoanEMISchedule
from loan.serializers.bill_generation_serializier import BillGenerationSerializer
from utility.common_utils import get_next_generation_date
from utility.crud_helper import CrudHelper
from utils.constants import LOAN_STATUS, LOAN_TYPE
from utils.envSetup import environment


class DemandGeneration:

    def __init__(self):
        self.__todays_date = datetime.datetime.now().date()
        self.__pre_bill_days = int(environment.PRE_BUILD_DAYS)
        self.__batch_size = int(environment.PROCESS_LOAN_BATCH)
        self.__process()

    def __process(self):
        eligible_loans_count = self.__get_total_eligible_loans()
        print(eligible_loans_count)
        self.__update_in_batches(total_records=eligible_loans_count)

    def __update_in_batches(self, total_records):
        # Calculate the number of batches
        num_batches = (total_records // int(self.__batch_size)) + 1
        crud_helper = CrudHelper(BillGenerationSerializer)
        # Perform bulk update in batches
        pre_build_days = int(environment.PRE_BUILD_DAYS)
        due_date = self.__todays_date + datetime.timedelta(days=pre_build_days)
        for batch_number in range(num_batches):
            records_to_save = []
            loan_bill_data = []
            start_index = batch_number * self.__batch_size
            end_index = start_index + self.__batch_size
            record_ids = LoanEMISchedule.objects.filter(
                Q(loan__status=LOAN_STATUS.GOOD_STANDING.value)
                | Q(loan__status=LOAN_STATUS.BAD_STANDING.value),
                Q(loan__next_due_generation_date=self.__todays_date)
                | Q(loan__next_due_generation_date__isnull=True),
                loan__loan_type=LOAN_TYPE.GOLD_LOAN.value,
            )[start_index:end_index]
            print(record_ids)
            for i in record_ids:
                schedule = i.loan_emi_schedule.filter(due_date=due_date).first()
                print(schedule, i.loan_emi_schedule.all(), due_date)
                if schedule:
                    loan_bill_data.append(
                        self.__create_bill_generation_obj(
                            loan_data=i, schedule_data=schedule
                        )
                    )
                else:
                    print("problem with record", i.loan)
            # Save the modified records
            for record in records_to_save:
                record.save()

            crud_helper.add_obj(validate_add=False, data=loan_bill_data, many=True)

    def __get_total_eligible_loans(self):
        loans = Loan.objects.filter(
            Q(status=LOAN_STATUS.GOOD_STANDING.value)
            | Q(status=LOAN_STATUS.BAD_STANDING.value),
            Q(next_due_generation_date=self.__todays_date)
            | Q(next_due_generation_date__isnull=True),
        ).count()
        return loans

    def __create_bill_generation_obj(self, loan_data, schedule_data):
        data = {}
        data["loan"] = loan_data.loan_id
        data["emi_record"] = schedule_data.loan_emi_record_id
        data["total_amount"] = schedule_data.emi_amount
        data["total_principal"] = schedule_data.principal
        data["total_interest"] = schedule_data.interest
        data["total_penalty"] = 0
        data["total_amount_paid"] = 0 
        data["principal_paid"] = 0  
        data["interest_paid"] = 0
        data["penalty_paid"] = 0
        data["principal_remaining"] = schedule_data.principal # 0
        data["interest_remaining"] = schedule_data.interest #0
        data["penalty_remaining"] = 0 
        data["bill_paid"] = 0
        return data
