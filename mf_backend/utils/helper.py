# from uuid import uuid4
# a = uuid4()
# print(a)
# print(a.hex)
import math
import random

import pytz
import requests
from bs4 import BeautifulSoup
from lxml import html
from asset.models import GoldPriceData
import datetime
from django.db.models import Sum, Avg
from django.core.mail import send_mail
from django.conf import settings
from utils.envSetup import environment


# from datetime import datetime

# e = datetime.now()
# ep = e.timestamp()
# print(e)
# print(hex(int(str(ep).replace('.',''))))

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
        digits.append("-")

    digits.reverse()

    return "".join(digits)




def get_gold_price(lender, karat: int) -> float:
    obj = (
        GoldPriceData.objects.values("gold_price")
        .filter(karat=karat, lender=lender)
        .order_by("-created_at")
        .first()
    )
    return float(obj["gold_price"]) if obj else 0.0


def get_radian_gold_price_by_karat(karat: int) -> float:
    obj = (
        GoldPriceData.objects.values("gold_price")
        .filter(karat=karat, lender__lender_code=environment.RADIAN_LENDER_CODE)
        .order_by("-created_at")
        .first()
    )
    return float(obj["gold_price"]) if obj else 0.0



def get_radian_gold_price_obj(karat=None):
    q = {}
    if karat:
        q['karat'] = karat
    else:
        q['lender__lender_code'] = environment.RADIAN_LENDER_CODE
        
    return GoldPriceData.objects.filter(**q)



def generate_numbers(n):
    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(n):
        index = math.floor(random.random() * 10)

        random_str += str(digits[index])

    return random_str


# def get_gold_price():
#     # Making a GET request
#     page = requests.get("https://ibjarates.com/")

#     soup = BeautifulSoup(page.content, "html.parser")
#     # This will create a list of buyers:
#     soup = soup.table.tbody
#     # soup=soup.find('td')
#     price = int(soup.text.split()[11]) / 10
#     lending_price=price*0.75
#     GoldPriceData.objects.create(gold_price=price, karat=22, lending_price=lending_price, created_at=datetime.datetime.now()).save()
#     return price


def price_of_gold_22_karates():
    # gold_price = GoldPriceData.objects.filter(karat=22, lender=environment.RADIAN_LENDER_CODE).latest('created_at').gold_price
    return float(get_radian_gold_price_by_karat(karat=22))

# def get_lending_rate():
#     start_date = datetime.date.today() - datetime.timedelta(days=30)
#     end_date = datetime.datetime.now()
#     queryset = GoldPriceData.objects.filter(
#         created_at__gte=start_date, created_at__lte=end_date
#     ).aggregate(lending_rate=Avg('lending_price',default=0))
#     lending_rate= round(queryset.get('lending_rate',0), 2)
#     return float(lending_rate)

# def gold_karat_converter(
#     customer_gold_karate, total_num_of_gold_in_grams, ltv_percentage
# ):
#     # gold_price=GoldPriceData.objects.all().first().gold_price
#     gold_price = price_of_gold_22_karates()
#     # print(gold_price)
#     # price_of_22_karate = gold_price
#     # price_of_22_karate = float(price_of_22_karate["gold_price__avg"])
#     # price of 22 karates
#     price_of_gold = (gold_price / 22) * customer_gold_karate
#     eligible_amount = float(price_of_gold) * total_num_of_gold_in_grams
#     price = int(eligible_amount)
#     return price * (ltv_percentage / 100)


# def gold_asset_price(customer_gold_karate, total_num_of_gold_in_grams):
#     # price_of_22_karate=get_gold_price()/10 #price of 22 karates
#     price_of_22_karate = price_of_gold_22_karates()  # price of 22 karates
#     # price_of_22_karate = float(price_of_22_karate["gold_price__avg"])
#     price_of_gold = (price_of_22_karate / 22) * customer_gold_karate
#     eligible_amount = float(price_of_gold) * float(total_num_of_gold_in_grams)

#     return eligible_amount


def get_disbursement_amount(loan_amount, processing_fee, stamp_duty):
    processing_fee = loan_amount * processing_fee / 100
    gst = processing_fee * 0.18
    stamp_duty = loan_amount * stamp_duty / 100
    return loan_amount - processing_fee - gst - stamp_duty


# def get_gst(loan_amount, processing_fee):
#     processing_fee = loan_amount * processing_fee / 100
#     gst = processing_fee * 0.18
#     return gst

from django.core.mail import EmailMessage
from django.conf import settings
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def sendForgotPasswordEmail(email, otp, name):
    """
    Send OTP for forgot password to user.
    """
    print(f"📧 Attempting to send forgot password email to: {email}")

    subject = "Password Reset OTP - Manipal Fintech"
    body = (
        f"{otp} is your one time secret password. Do not share it with anyone. - Team Manipal Fintech"
    )

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        if settings.EMAIL_USE_TLS:
            server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Forgot password email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send forgot password email: {str(e)}")
        logger.error(f"Error sending forgot password email: {str(e)}")
        return False


def sendEmailUser(email, username, password, name):
    """
    Send welcome email to new user.
    Compatible with Python 3.12+
    """
    print(f"📧 Attempting to send email to: {email}")

    subject = "Welcome to Manipal Fintech"
    body = (
        f"Welcome {name}\n\n"
        "Your account with Manipal Fintech is created.\n\n"
        "Login Credentials:\n"
        f"Username: {username}\n"
        f"Password: {password}\n\n"
        "Please change your password after first login."
    )

    try:
        # Use Python's smtplib directly to avoid Django's SMTP backend issue
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP connection
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        
        # Start TLS (Python 3.12 compatible - no keyfile/certfile params)
        if settings.EMAIL_USE_TLS:
            server.starttls()
        
        # Login
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"❌ Email sending failed for {email}: {e}")
        logger.error(f"Failed to send registration email to {email}", exc_info=True)
        return False



import random
import string


def generate_password():
    # define the characters to use in the password
    chars = string.ascii_letters + string.digits

    # generate a random password of length 8
    password = "".join(random.choice(chars) for _ in range(8))

    return password


# def rate_per_gram(customer_gold_karate):
#     # price_of_22_karate=get_gold_price()/10 #price of 22 karates

#     price_of_22_karate = price_of_gold_22_karates()
#     price_of_gold = (price_of_22_karate / 22) * customer_gold_karate
#     return price_of_gold


# def customer_gold_weight_converter_to_22_karate_weight(
#     karat_of_customer_gold, weight_of_customer_gold
# ):
#     price_of_22_karate = price_of_gold_22_karates()
#     # price_of_karate_22 = float(price_of_22_karate["gold_price__avg"])
#     price_of_customer_karate = rate_per_gram(karat_of_customer_gold)

#     weight = (price_of_customer_karate / price_of_22_karate) * float(
#         weight_of_customer_gold
#     )
#     return weight


import logging

logger = logging.getLogger(__name__)


def reverse_geocode_lat_lng(latitude, longitude, default_location=None) -> str:
    """
    Convert Latitude and Longitude to a human-readable address using Google Geocoding API.
    Returns the formatted address string or default_location if failed/empty.
    """
    if not latitude or not longitude:
        return default_location

    api_key = getattr(settings, "GOOGLE_API_KEY", None)
    if not api_key:
        logger.warning("GOOGLE_API_KEY is not configured for reverse geocoding.")
        return default_location

    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": api_key,
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "OK" and res_json.get("results"):
                formatted_address = res_json["results"][0].get("formatted_address")
                if formatted_address:
                    return formatted_address
            else:
                logger.warning("Google Geocoding API status: %s", res_json.get("status"))
        else:
            logger.warning("Google Geocoding API returned HTTP status %s", response.status_code)
    except Exception as e:
        logger.warning("Error fetching location from Google Geocoding API: %s", str(e))

    return default_location
