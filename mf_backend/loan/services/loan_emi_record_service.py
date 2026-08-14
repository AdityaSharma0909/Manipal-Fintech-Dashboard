import json
import traceback
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from application.service import ApplicationService
from loan.models import LoanEMISchedule, Loan
from loan.serializers.loan_emi_schedule_record import LoanEmiScheduleSerializer, LoanEmiRecordSerializer
from utility.common_utils import get_next_generation_date
from utility.crud_helper import CrudHelper
from dateutil import parser as parser

class LoanEmiService:

    loan_emi_schedule=CrudHelper(serializer=LoanEmiScheduleSerializer)
    loan_emi_record=CrudHelper(serializer=LoanEmiRecordSerializer)
    def __get_schedule(self, app_id):
        schedule = ApplicationService().generate_application_amort_schedule(app_id)
        return schedule

    def create_loan_schedule(self, app_id):
        schedule_data=self.__get_schedule(app_id=app_id)
        loan_header_data = {
            'application': app_id,
            'principal': 0,
            'emi_amount': 0,
            'data': schedule_data
        }
        for k,v in schedule_data.items():
            loan_header_data['principal']= v.get('primary_loan_principal_remaining',v.get('principal',0))
            loan_header_data['emi_amount']= v.get('emi')
            break
        loan_emi_schedule = self.loan_emi_schedule.add_obj(loan_header_data)
        if loan_emi_schedule.get('status_code') == 200:
            loan_emi_schedule_id = loan_emi_schedule.get('data').get('loan_emi_header_id')
            records=self.create_loan_record(loan_header=loan_emi_schedule_id, schedule_data=schedule_data)
            if records.get('status_code')!=200:
                self.__roll_back(loan_emi_schedule_id)
                return records
        return loan_emi_schedule

    def __roll_back(self, header_id):
        LoanEMISchedule.objects.get(loan_emi_header_id=header_id).delete()

    def update_loan(self, app_id, loan_id):
        try:
            schedule=LoanEMISchedule.objects.filter(application__application_id=str(app_id))
            if len(schedule) > 0:
                schedule_data=schedule.first()
                schedule_data.loan=loan_id
                first_element=sorted(list(schedule.first().data.keys()))
                next_due_date = parser.parse(schedule.first().data[first_element[0]]['date'])
                next_due_generation_date = get_next_generation_date(next_due_date)
                loan_id.due_date = next_due_date.date().strftime("%Y-%m-%d")
                loan_id.next_due_date= next_due_date.date().strftime("%Y-%m-%d")
                loan_id.next_due_generation_date= next_due_generation_date.date().strftime("%Y-%m-%d")
                loan_id.save(update_fields=['due_date', 'next_due_date', 'next_due_generation_date'])
                schedule_data.save(update_fields=['loan'])
            return schedule.values()
        except ObjectDoesNotExist:
            traceback.print_exc()
        except Exception:
            traceback.print_exc()
    def create_loan_record(self, loan_header, schedule_data):
        records = []
        for key, value in schedule_data.items():
            record_data = {}
            record_data['emi_amount']=value.get('emi')
            record_data['principal']=value.get('total_principal')
            record_data['interest']=value.get('total_interest')
            record_data['amount']=value.get('emi')
            record_data['loan_emi_header'] = loan_header
            record_data['sequence_no'] = key
            #record_data['bill_generation_date']=(parser.parse(value['date']).date()-timedelta(days=2)).today()
            record_data['bill_generation_date']=(parser.parse(value['date']).date()-timedelta(days=2))
            record_data['due_date'] = parser.parse(value['date']).date().strftime("%Y-%m-%d")
            record_data.update(**value)
            records.append(record_data)
        loan_emi_records = self.loan_emi_record.add_obj(records, many=True)
        return loan_emi_records

    def create_or_get_schedule(self, app_id):
        emi_schedule=self.loan_emi_schedule.get_all_data(query=Q(application__application_id=app_id))
        if emi_schedule.get('status_code')==200 and len(emi_schedule.get('data'))>0:
            emi_data=emi_schedule.get('data')[0]
            return emi_data.get('data')
        else:
            data=self.create_loan_schedule(app_id)
            if data.get('status_code',200)!=200:
                return data
            return data.get('data').get('data')


