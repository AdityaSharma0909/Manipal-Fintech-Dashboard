import datetime
from utils.constants import CODE_OF_STATES, NO_OF_LOCATION, TYPE_OF_LOCATION, AMORTIZATIONTYPE
import utils.helper as helper
import math
from .models import Application
from dateutil.relativedelta import relativedelta
from utils.constants import PERIOD
from .services.payment_schedule import PaymentSchedule
from dateutil import parser as parser

class ApplicationService:
    def generate_application_number(self):

        location=TYPE_OF_LOCATION.BRANCHES.value+CODE_OF_STATES.MAHARASTRA.value+NO_OF_LOCATION.REGISTERED_OFFICE_GURGAON.value
        
        

        current_date = str(datetime.date.today())
        year=current_date[2:4]
        month=current_date[5:7]
        number=helper.generate_numbers(4)
    

        return location+month+year+number
    
    def format_date(self,s):
        str1=s.split("-")
        s=str1[2]+"-"+str1[1]+"-"+str1[0]
        return s


    def payment_dates(self, frequency,disbursed_date,tenure,period):
        dates = []

        start = datetime.datetime(disbursed_date.year, disbursed_date.month, disbursed_date.day)
        no_of_emis=int((tenure/12)*period)
        if frequency == PERIOD.WEEKLY.value:
            delta = datetime.timedelta(days=7)
        elif frequency == PERIOD.MONTHLY.value:
            delta = relativedelta(months=1)
        elif frequency == PERIOD.QUATERLY.value:
            delta = relativedelta(months=3)
        else:
            raise ValueError("Invalid frequency ")
        for i in range(1,no_of_emis+1):
            dates.append(start + i * delta)

        return dates

    def __get_quaterly_sequence(self, period):
        weekly = 52
        temp = weekly / period
        new_temp = temp
        count = 0
        sequence = {int(new_temp - 1): count}
        for i in range(period - 1):
            new_temp += temp
            count += 1
            sequence[int(new_temp - 1)] = count
        return sequence

    def generate_application_amort_schedule(self,app_id):
        app = Application.objects.get(application_id=app_id)
        disbursedDate = app.disbursed_date if app.disbursed_date else app.modefied_at
        principal = app.loan_amount
        interest_rate = app.product.interest_rate
        main_product=app.product
        contra_product=app.product.contra_product
        period=app.product.period
        gold_schedule={}
        tenure = app.product.tenure
        amortization_type = app.product.amortization_type

        period=self.get_period(period)
        if contra_product:
            disbursal_date=parser.parse(str(disbursedDate))
            # if period==4:
            #     disbursedDate= disbursal_date + relativedelta(months=3)
            no_of_emis = int((tenure / 12) * period)
            dates = self.payment_dates(app.product.period, disbursedDate, tenure=tenure, period=period)
            if amortization_type==AMORTIZATIONTYPE.INTEREST_ONLY.value:
                gold_schedule = self.generateInterestOnlySchedule(no_of_emis, app.loan_amount,
                                                                  interest_rate,
                                                                  period,
                                                                  dates)
            elif amortization_type==AMORTIZATIONTYPE.BULLET.value:
                gold_schedule=self.__bullet_payment(schedule={}, principal=principal, interest_rate=interest_rate,period=period,
                                                    no_of_emis=no_of_emis, app=app, tenure=tenure)

            else:
                gold_schedule=self.__amort_for_main_product(schedule={},interest_rate=interest_rate, period=period, principal=principal,
                                                            no_of_emis=no_of_emis, app=app, disbursedDate=disbursedDate,
                                                            sequence=0)


        no_of_emis=int((tenure/12)*period)
        schedule = {}
        sequence = 0

        if 'Amortization Schedule' == amortization_type or (contra_product and contra_product.amortization_type=='Amortization Schedule'):
            if contra_product:
                schedule=self.__amort_for_contra_product(app, disbursedDate, tenure, sequence, gold_schedule, schedule, amortization_type)
                return schedule
            else:
                schedule=self.__amort_for_main_product(schedule, interest_rate, period, principal, no_of_emis, app,disbursedDate,
                                                       sequence)
                return schedule
        elif 'Interest Only' ==  amortization_type:
            principal_remaining = principal
            dates=self.payment_dates(app.product.period,disbursedDate,app.tenure,period)
            # print("payment_dates: ____________________________")
            # print(dates)
            # print(f"Lenght: {str(len(dates))}")
            # print(f"sequence: {sequence}")
            # print(f"no_of_emis: {no_of_emis}")
            # print("payment_dates: ____________________________")
            while sequence < no_of_emis:
                interest_part = math.ceil((principal*interest_rate)/(period*100))
                principal_part = 0
                # date=dates[sequence-1].strftime("%d-%m-%Y")
                date = dates[sequence].date()

                principal_remaining = principal_remaining - principal_part
                if principal_remaining < 0:
                    principal_part=principal_part-principal_remaining
                    principal_remaining = 0
                #last emi logic
                if sequence == no_of_emis-1 :
                    principal_part = principal_remaining
                    principal_remaining = 0
                emi = principal_part + interest_part
                amzObj = AmortScheduleObjectDbSave(principal = principal_part,interest=interest_part,principal_remaining=principal_remaining,emi=emi,date=date)
                schedule[sequence] = amzObj.__dict__
                sequence +=1
            # print('contra loan amount',app.contra_loan_amount, app.product.contra_product)
            if app.contra_loan_amount != None:
                contra_product = app.product.contra_product
                if contra_product != None:
                    contraSchedule = {}
                    contra_schedule = self.generateInterestOnlySchedule(no_of_emis,app.contra_loan_amount,contra_product.interest_rate,period,dates)

                    for sequence,schd in schedule.items():
                        contraScheduleObj =  ContraAmortScheduleObject(
                                                                    primary_loan_principal = schd['principal'],
                                                                    primary_loan_interest = schd['interest'],
                                                                    primary_loan_principal_remaining = schd['principal_remaining'],
                                                                    contra_loan_principal = contra_schedule[sequence]['principal'],
                                                                    contra_loan_interest = contra_schedule[sequence]['interest'],
                                                                    contra_loan_principal_remaining = contra_schedule[sequence]['principal_remaining'],
                                                                    total_principal = schd['principal'] + contra_schedule[sequence]['principal'],
                                                                    total_interest = schd['interest'] + contra_schedule[sequence]['interest'],
                                                                    total_principal_remaining = schd['principal_remaining'] + contra_schedule[sequence]['principal_remaining'],
                                                                    emi = schd['emi'] + contra_schedule[sequence]['emi'],
                                                                    date=schd['date']
                                                                    )
                        contraSchedule[sequence] = contraScheduleObj.__dict__
                    return contraSchedule
            return schedule
        elif 'Bullet' ==  amortization_type:
            schedule=self.__bullet_payment(schedule, principal, interest_rate, period,no_of_emis, app, tenure)
            return schedule

    def __amort_for_contra_product(self,app,disbursedDate, tenure, sequence, gold_schedule, schedule, main_product_amort_type):
        principal = app.contra_loan_amount
        interest_rate = app.product.contra_product.interest_rate
        # print(interest_rate, period)
        period=self.get_period(app.product.contra_product.period)
        no_of_emis=int((app.product.contra_product.tenure/12)*period)
        interestRatePercycle = ((interest_rate / 100) / period)
        total=0
        total_with_interest=0   # print(interestRatePercycle)
        emi = math.ceil((principal * interestRatePercycle) / (1 - pow((1 + interestRatePercycle), -no_of_emis)))
        # TODO: now setting start date as modifed_at make it when loan is confirmed.
        dates = self.payment_dates(app.product.contra_product.period, disbursedDate, tenure, period)
        principal_remaining = principal
        # print(principal_remaining, principal)
        quarterly_sequence = self.__get_quaterly_sequence(period)


        while principal_remaining > 0 and (sequence < no_of_emis):

            interest_part = math.ceil((principal_remaining * interest_rate) / (period * 100))
            principal_part = math.ceil(emi - interest_part)
            # date=dates[sequence-1].strftime("%d-%m-%Y")
            date = dates[sequence].date()

            principal_remaining = principal_remaining - principal_part
            if principal_remaining < 0:
                #principal_part = principal_part - principal_remaining
                principal_part=principal-total
                principal_remaining = 0
            total+=principal_part
            total_with_interest+=interest_part
            amzObj = AmortScheduleObjectDbSave(principal=principal_part, interest=interest_part,
                                         principal_remaining=principal_remaining, emi=principal_part+interest_part, date=date)
            temp = amzObj.__dict__

            index_sequence = quarterly_sequence.get(sequence) if app.product.contra_product.period==PERIOD.WEEKLY.value else sequence


            if main_product_amort_type==AMORTIZATIONTYPE.BULLET.value:

                if sequence==(no_of_emis-1) :
                    data=gold_schedule.get(1)
                    temp=self.__add_to_emi_in_contra_product(temp, data)
                else:
                    data=AmortScheduleObjectDbSave(principal=0, interest=0,principal_remaining=gold_schedule.get(1).get('principal'),emi=0,date=None).__dict__
                    temp=self.__add_to_emi_in_contra_product(temp, data)
            else: #main_product_amort_type==AMORTIZATIONTYPE.AMORTIZATION_SCHEDULE.value:
                data = gold_schedule.get(index_sequence)

                temp=self.__add_to_emi_in_contra_product(temp, data)

            schedule[sequence] = temp
            sequence += 1
        return schedule

    def calculate_number_of_emis(self, tenure, period):
        return int((tenure / 12) * period)
    def calculate_emi(self, principal, interest_rate, period,no_of_emis,amortization_type):
        if amortization_type==AMORTIZATIONTYPE.AMORTIZATION_SCHEDULE.value:
            interest_rate_per_cycle = ((interest_rate / 100) / period)
            return math.ceil((principal * interest_rate_per_cycle) / (1 - pow((1 + interest_rate_per_cycle), -no_of_emis)))
        elif amortization_type==AMORTIZATIONTYPE.INTEREST_ONLY.value:
            return math.ceil((principal*interest_rate)/(period*100))
        else:
            interest_part = math.ceil((principal * interest_rate) / (period * 100))
            total_interest = interest_part * no_of_emis
            principal_part = principal
            return total_interest + principal_part

    def __add_to_emi_in_contra_product(self, contra_loan, data):

        return ContraAmortScheduleObject(primary_loan_principal=data.get('principal'),
                                         primary_loan_interest=data.get('interest'),
                                         primary_loan_principal_remaining=data.get('principal_remaining'),
                                         contra_loan_principal=contra_loan.get('principal'),
                                         contra_loan_interest=contra_loan.get('interest'),
                                         contra_loan_principal_remaining=contra_loan.get('principal_remaining'),
                                         total_principal=contra_loan['principal'] + data.get('principal'),
                                         total_interest=contra_loan['emi'] + data.get('emi'),
                                         total_principal_remaining=contra_loan.get('principal_remaining')+data.get('principal_remaining'),
                                         emi=contra_loan['emi'] + data.get('emi'),
                                         date=contra_loan.get('date')).__dict__
    def __amort_for_main_product(self, schedule, interest_rate, period, principal, no_of_emis, app,disbursedDate,
                                 sequence):
        # print(interest_rate,period)
        interestRatePercycle = ((interest_rate / 100) / period)
        # print(interestRatePercycle)
        emi = math.ceil((principal * interestRatePercycle) / (1 - pow((1 + interestRatePercycle), -no_of_emis)))
        # TODO: now setting start date as modifed_at make it when loan is confirmed.
        dates = self.payment_dates(app.product.period, disbursedDate, app.tenure, period)
        principal_remaining = principal
        # print(principal_remaining, principal)
        total=0
        total_with_interest=0
        while principal_remaining > 0 and (sequence < no_of_emis):

            interest_part = math.ceil((principal_remaining * interest_rate) / (period * 100))
            principal_part = math.ceil(emi - interest_part)
            #date=dates[sequence-1].strftime("%d-%m-%Y")
            date = (dates[sequence]).date()
            principal_remaining = principal_remaining - principal_part

            if principal_remaining < 0:
                #principal_part=principal_part-principal_remaining
                principal_part = principal-total
                principal_remaining = 0

            total += principal_part
            total_with_interest += interest_part


            amzObj = AmortScheduleObjectDbSave(principal=principal_part, interest=interest_part,
                                         principal_remaining=principal_remaining, emi=principal_part+interest_part, date=date)
            schedule[sequence] = amzObj.__dict__
            sequence += 1
        return schedule

    def get_period(self, period):
        if period == PERIOD.WEEKLY.value:
            period = 52
        elif period == PERIOD.MONTHLY.value:
            period = 12
        elif period == PERIOD.QUATERLY.value:
            period = 4
        return period
    def __bullet_payment(self, schedule,principal, interest_rate, period, no_of_emis, app, tenure):
        sequence = 1
        interest_part = math.ceil((principal * interest_rate) / (period * 100))
        total_interest = interest_part * no_of_emis
        principal_part = principal
        loan_start_Date = app.disbursed_date if app.disbursed_date != None else app.created_at
        loan_close_date = (loan_start_Date + relativedelta(months=tenure)).date()
        

        emi = total_interest + principal_part
        amzObj = AmortScheduleObjectDbSave(principal=principal_part, interest=total_interest, principal_remaining=0, emi=emi,
                                     date=loan_close_date)
        schedule[sequence] = amzObj.__dict__
        return schedule
    def generateInterestOnlySchedule(self,no_of_emis,principal,interest_rate,period,dates):
        schedule = {}
        principal_remaining = principal
        sequence = 0
        print(dates)
        while sequence < no_of_emis:
            emi = 0
            print(sequence-1, no_of_emis)
            interest_part = math.ceil((principal*interest_rate)/(period*100))
            principal_part = 0
            date=dates[sequence-1].strftime("%d-%m-%Y")

            principal_remaining = principal_remaining - principal_part
            if principal_remaining < 0:
                principal_part=principal_part-principal_remaining
                principal_remaining = 0
            #last emi logic
            if sequence == no_of_emis-1 :
                principal_part = principal_remaining
                principal_remaining = 0
            emi = principal_part + interest_part
            amzObj = AmortScheduleObjectDbSave(principal = principal_part,interest=interest_part,principal_remaining=principal_remaining,emi=emi,date=date)
            schedule[sequence] = amzObj.__dict__
            sequence +=1
        return schedule
        
class AmortScheduleObject:
    def __init__(self,principal,interest,principal_remaining,emi,date):
        self.principal = principal
        self.interest = interest
        self.principal_remaining = principal_remaining
        self.emi = emi
        self.date=date

class AmortScheduleObjectDbSave:
    def __init__(self,principal,interest,principal_remaining,emi,date):
        self.principal = principal
        self.interest = interest
        self.principal_remaining = principal_remaining
        self.emi = emi
        self.date=str(date)
class ContraAmortScheduleObject:
    def __init__(self,primary_loan_principal,primary_loan_interest,primary_loan_principal_remaining,contra_loan_principal,contra_loan_interest,
                 contra_loan_principal_remaining,total_principal,total_interest,total_principal_remaining,emi,date):
        self.primary_loan_principal = primary_loan_principal
        self.primary_loan_interest = primary_loan_interest
        self.primary_loan_principal_remaining = primary_loan_principal_remaining
        self.contra_loan_principal = contra_loan_principal
        self.contra_loan_interest = contra_loan_interest
        self.contra_loan_principal_remaining = contra_loan_principal_remaining
        self.total_principal = total_principal
        self.total_interest = total_interest
        self.total_principal_remaining = total_principal_remaining
        self.emi = emi
        self.date=str(date)
        

    
    