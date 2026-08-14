import datetime
import math
from dateutil.relativedelta import relativedelta
from utils.constants import (
    CODE_OF_STATES, NO_OF_LOCATION, TYPE_OF_LOCATION, PERIOD
)
from utils.helper import generate_numbers


class AmortScheduleObject:
    def __init__(self, principal, interest, principal_remaining, emi, date):
        self.principal = principal
        self.interest = interest
        self.principal_remaining = principal_remaining
        self.emi = emi
        self.date = str(date)


class ContraAmortScheduleObject:
    def __init__(self, primary_loan_principal, primary_loan_interest, primary_loan_principal_remaining,
                 contra_loan_principal, contra_loan_interest,
                 contra_loan_principal_remaining, total_principal, total_interest, total_principal_remaining, emi,
                 date):
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
        self.date = str(date)


class PaymentSchedule:
    def generate_application_number(self):
        location = (
            TYPE_OF_LOCATION.BRANCHES.value +
            CODE_OF_STATES.MAHARASTRA.value +
            NO_OF_LOCATION.REGISTERED_OFFICE_GURGAON.value
        )

        current_date = str(datetime.date.today())
        year = current_date[2:4]
        month = current_date[5:7]
        number = generate_numbers(4)

        return location + month + year + number

    def format_date(self, date_str):
        date_parts = date_str.split("-")
        formatted_date = date_parts[2] + "-" + date_parts[1] + "-" + date_parts[0]
        return formatted_date

    def payment_dates(self, frequency, disbursed_date, tenure, period):
        dates = []
        start = datetime.datetime(disbursed_date.year, disbursed_date.month, disbursed_date.day)
        no_of_emis = int((tenure / 12) * period)

        period_mapping = {
            PERIOD.WEEKLY.value: 7,
            PERIOD.MONTHLY.value: 1,
            PERIOD.QUATERLY.value: 3,
        }

        delta = relativedelta(months=period_mapping.get(frequency, 1))

        for i in range(no_of_emis):
            dates.append(start + i * delta)

        return dates

    def interest_only_schedule(self,app,no_of_emis,principal,interest_rate,period,disbursed_date):
        schedule = {}
        principal_remaining = principal
        dates = self.payment_dates(app.product.period, disbursed_date, app.tenure, period)
        sequence=0
        while sequence < no_of_emis:
            interest_part = math.ceil((principal * interest_rate) / (period * 100))
            principal_part = 0
            # date=dates[sequence-1].strftime("%d-%m-%Y")
            date = dates[sequence]

            principal_remaining = principal_remaining - principal_part
            if principal_remaining < 0:
                principal_part = principal_part - principal_remaining
                principal_remaining = 0
            # last emi logic
            if sequence == no_of_emis - 1:
                principal_part = principal_remaining
                principal_remaining = 0
            emi = principal_part + interest_part
            amzObj = AmortScheduleObject(principal=principal_part, interest=interest_part,
                                         principal_remaining=principal_remaining, emi=emi, date=date)
            schedule[sequence] = amzObj.__dict__
            sequence += 1
        print('contra loan amount', app.contra_loan_amount, app.product.contra_product)
        if app.contra_loan_amount != None:
            contra_product = app.product.contra_product
            if contra_product != None:
                contraSchedule = {}
                contra_schedule = self.generateInterestOnlySchedule(no_of_emis, app.contra_loan_amount,
                                                                    contra_product.interest_rate, period, dates)

                for sequence, schd in schedule.items():
                    contraScheduleObj = ContraAmortScheduleObject(
                        primary_loan_principal=schd['principal'],
                        primary_loan_interest=schd['interest'],
                        primary_loan_principal_remaining=schd['principal_remaining'],
                        contra_loan_principal=contra_schedule[sequence]['principal'],
                        contra_loan_interest=contra_schedule[sequence]['interest'],
                        contra_loan_principal_remaining=contra_schedule[sequence]['principal_remaining'],
                        total_principal=schd['principal'] + contra_schedule[sequence]['principal'],
                        total_interest=schd['interest'] + contra_schedule[sequence]['interest'],
                        total_principal_remaining=schd['principal_remaining'] + contra_schedule[sequence][
                            'principal_remaining'],
                        emi=schd['emi'] + contra_schedule[sequence]['emi'],
                        date=schd['date']
                    )
                    contraSchedule[sequence] = contraScheduleObj.__dict__
                return contraSchedule
        return schedule

    def generate_application_amort_schedule(self, app, principal, interest_rate,period, product):
        disbursed_date = app.disbursed_date or app.modified_at

        period_mapping = {
            PERIOD.WEEKLY.value: 52,
            PERIOD.MONTHLY.value: 12,
            PERIOD.QUATERLY.value: 4,
        }
        period = period_mapping.get(period, period)

        tenure = product.tenure
        no_of_emis = int((tenure / 12) * period)
        schedule = {}
        sequence = 0

        interest_rate_per_cycle = ((interest_rate / 100) / period)
        emi = math.ceil((principal * interest_rate_per_cycle) /
                        (1 - pow((1 + interest_rate_per_cycle), -no_of_emis)))

        dates = self.payment_dates(product.period, disbursed_date, tenure, period)
        principal_remaining = principal

        for sequence, date in enumerate(dates, start=1):
            interest_part = math.ceil((principal_remaining * interest_rate) / (period * 100))
            principal_part = math.ceil(emi - interest_part)

            if sequence == no_of_emis:
                principal_part += principal_remaining
                principal_remaining = 0
            else:
                principal_remaining -= principal_part

            amortization_schedule = AmortScheduleObject(
                    principal=principal_part,
                    interest=interest_part,
                    principal_remaining=principal_remaining,
                    emi=emi,
                    date=date,
                )
            schedule[sequence] = amortization_schedule.__dict__

        return schedule

    def generateInterestOnlySchedule(self, no_of_emis, principal, interest_rate, period, dates):
        schedule = {}
        principal_remaining = principal
        sequence = 0

        while sequence < no_of_emis:
            emi = 0

            interest_part = math.ceil((principal * interest_rate) / (period * 100))
            principal_part = 0
            date = dates[sequence - 1].strftime("%d-%m-%Y")

            principal_remaining = principal_remaining - principal_part
            if principal_remaining < 0:
                principal_part = principal_part - principal_remaining
                principal_remaining = 0
            # last emi logic
            if sequence == no_of_emis - 1:
                principal_part = principal_remaining
                principal_remaining = 0
            emi = principal_part + interest_part
            amzObj = AmortScheduleObject(principal=principal_part, interest=interest_part,
                                         principal_remaining=principal_remaining, emi=emi, date=date)
            schedule[sequence] = amzObj.__dict__
            sequence += 1
        return schedule