import string
digs = string.digits + string.ascii_letters


def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x = x // base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

# t = 10000000
# a = int2base(t*800, 36).upper()

# print(a)


# from time import time

# b = str(time()).replace('.','')
# b = int2base(int(b), 36).upper()
# print(b)
# print(type(b))





from lead.models import NewLead 
from account.models import NewAccount
from application.models import NewApplication

# --- Lead ID Logic ---
LOAN_PREFIX = {
    "GOLD_LOAN": "GL",
    "HOME_LOAN": "HL",
    "PERSONAL_LOAN": "PL",
    "BUSINESS_LOAN": "BL",
    "LAP": "LAP",
    "HEALTH_INSURANCE": "HI",
    "MOTOR_INSURANCE": "MI",
    "CREDIT_CARDS": "CC",
}

def generate_lead_id(loan_type):
    prefix = LOAN_PREFIX.get(loan_type, "XX")

    last_lead = NewLead.objects.filter(lead_id__startswith=prefix).order_by("-created_at").first()
    if last_lead:
        last_num = int(last_lead.lead_id.replace(prefix, ""))
        return f"{prefix}{last_num + 1:04d}"
    return f"{prefix}0001"


# --- Customer ID Logic ---
def increment_alpha(code):
    a, b, c = code
    if c != "Z":
        return a + b + chr(ord(c) + 1)
    if b != "Z":
        return a + chr(ord(b) + 1) + "A"
    return chr(ord(a) + 1) + "AA"


def generate_customer_id():
    last_acc = NewAccount.objects.order_by("-created_at").first()
    if not last_acc:
        return "AAA0001"

    prefix = last_acc.customer_id[:3]
    number = int(last_acc.customer_id[3:])

    if number < 9999:
        return f"{prefix}{number + 1:04d}"
    
    new_prefix = increment_alpha(prefix)
    return f"{new_prefix}0001"


# --- Application Number Logic ---
def generate_application_number(loan_type):
    prefix = LOAN_PREFIX.get(loan_type, "XX")
    code_prefix = f"MPA{prefix}"

    last_app = NewApplication.objects.filter(application_number__startswith=code_prefix).order_by("-created_at").first()

    if last_app:
        last_num = int(last_app.application_number.replace(code_prefix, ""))
        return f"{code_prefix}{last_num + 1}"
    return f"{code_prefix}10001"
