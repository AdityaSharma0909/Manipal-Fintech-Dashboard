import json

from utils.constants import PERIOD
import calendar
import datetime
import time
from dateutil.relativedelta import relativedelta



def custom_response_obj(message,code, error_msg=None, error_code=None):
    resp_status='success' if code==200 or code==201 or code==204 else 'error'
    return {'status': resp_status, 'data': message, 'status_code': code, 'error_msg': error_msg,
            'error_code':error_code}

def serializer_instance(serializer_instance,read_only=False,**kwargs):

    if read_only:
        data=kwargs.get('data')
        many=kwargs.get('many', False)
        serializer = serializer_instance(data, many=many)
        return custom_response_obj(message=serializer.data, code=200)
    else:
        serializer = serializer_instance(**kwargs)
        if serializer.is_valid():
            serializer.save()
            return custom_response_obj(message=serializer.data, code=200)
        print(serializer.errors)
        is_many=kwargs.get('many',False)
        if not is_many:
            error= normalize_serializer_error(serializer.errors.items())
        else:
            error=serializer.errors
        return custom_response_obj(message=error, code=400)

def normalize_serializer_error(data):
    return {k: ','.join([str(j) for j in v]) for k, v in data}


def get_period_in_numbers(period):
    if period == PERIOD.WEEKLY.value:
        period = 52
    elif period == PERIOD.MONTHLY.value:
        period = 12
    elif period == PERIOD.QUATERLY.value:
        period = 4
    return period


def divide_into_batches(lst, batch_size):
    num_batches = len(lst) // batch_size
    batches = {}

    for i in range(num_batches):
        start = i * batch_size
        end = start + batch_size
        batch = lst[start:end]
        batches[i + 1] = batch

    if len(lst) % batch_size != 0:
        remaining = lst[num_batches * batch_size:]
        batches[num_batches + 1] = remaining

    return batches

def total_days_in_a_month():
    # Get the current month and year
    current_month = calendar.month_name[datetime.datetime.now().month]
    current_year = datetime.datetime.now().year

    # Get the total number of days in the current month
    total_days = calendar.monthrange(current_year, datetime.datetime.now().month)[1]
    return total_days


def divide_into_batches(lst, batch_size):
    num_batches = len(lst) // batch_size
    batches = {}

    for i in range(num_batches):
        start = i * batch_size
        end = start + batch_size
        batch = lst[start:end]
        batches[i + 1] = batch

    if len(lst) % batch_size != 0:
        remaining = lst[num_batches * batch_size:]
        batches[num_batches + 1] = remaining

    return batches

def total_days_in_a_month():
    # Get the current month and year
    current_month = calendar.month_name[datetime.datetime.now().month]
    current_year = datetime.datetime.now().year

    # Get the total number of days in the current month
    total_days = calendar.monthrange(current_year, datetime.datetime.now().month)[1]
    return total_days

# def get_next_generation_date(due_date):
#     # Calculate the interest per day using ExpressionWrapper
#     one_month_later = due_date.replace(month=due_date.month + 1)
#     # Subtract one day
#     result_date = one_month_later - datetime.timedelta(days=1)
#     return result_date
def get_next_generation_date(due_date):
    # Add one month to the due date
    next_due_generation_date = due_date + relativedelta(months=1)
    # Subtract one day
    result_date = next_due_generation_date - datetime.timedelta(days=1)
    return result_date

def get_days_difference(due_date):
    todays=datetime.datetime.today().date()
    delta = todays - due_date
    # Extract the number of days from the difference
    days_difference = delta.days
    return days_difference

def calculate_apr(loan_amount, interest_rate, loan_term, fees):
    # Calculate the monthly interest rate
    monthly_interest_rate = interest_rate / 12 / 100

    # Calculate the total number of payments
    total_payments = loan_term * 12

    # Calculate the monthly payment
    monthly_payment = loan_amount * (monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments))

    # Calculate the total cost of the loan
    total_cost = monthly_payment * total_payments + fees

    # Calculate the APR
    apr = (total_cost / loan_amount) * 100

    return apr

def getFederalReferenceID(application_number,service_code):
        return "RAD"+application_number[11:15]+service_code+str(round(time.time() * 1000))
# def calc_total_loan_taken(goods_price, gl_loan, pl_loan):
#     goods_price=goods_price if goods_price!=None else 0
#     gl_loan=gl_loan if gl_loan !=None else 0
#     pl_loan=pl_loan if pl_loan !=None else 0

#     return (gl_loan+pl_loan)-goods_price


