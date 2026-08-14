from utility.message_templates import MessageTemplates
from utils.envSetup import environment
import urllib.parse
import requests
from utils.constants import APP_ENV
from django.conf import settings

class SMSService:

    def __init__(self):
        self.apikey = environment.SMS_API_KEY
        self.baseurl = 'https://instantalerts.co/api/web/send/?apikey='+self.apikey
        self.sender = 'RADFIN'

    def sendLoginOtp(self, mobile: str, otp: str):
        # self.otp_msg = f'Dear {name}, your login OTP for your Radian account is {otp}. The OTP will expire in {(environment.OTP_TIMEOUT / 60)} minutes.'
        #
        # url= self.baseurl+'&sender='+self.sender+'&to='+mobile+'&message='+self.otp_msg+'&format=json'
        # response = requests.get(url)
        #
        # # Check for HTTP codes other than 200
        # if response.status_code != 200:
        #     print('Status:', response, 'Problem with the request.')
        # else:
        #     print("Sent login SMS")
        return self.__process_sms(mobile, otp)


    def sendGoldCollectionOtp(self, mobile: str, otp: str, customerName: str, loanOffcierName: str):
        # self.otp_msg = f'Dear {customerName}, please share the OTP {otp} with the loan officer {loanOffcierName} to initiate the loan application process. Please make sure the loan officer is at your doorstep.'
        #
        # url= self.baseurl+'&sender='+self.sender+'&to='+mobile+'&message='+self.otp_msg+'&format=json'
        # response = requests.get(url)
        #
        # # Check for HTTP codes other than 200
        # if response.status_code != 200:
        #     print('Status:', response, 'Problem with the request.')
        # else:
        #     print("Sent gold collection SMS")
        # return ""
        return self.__process_sms(mobile, otp)

    def sendGoldDepositOtp(self, mobile: str, otp: str):
        return self.__process_sms(mobile, otp)

    def sendForgotPasswordOtp(self, mobile: str, otp: str):
        return self.__process_sms(
            mobile, 
            otp, 
            template_id="1007177824524275693", 
            text="{#var#} is your one time secret password. Do not share it with anyone. - Team Manipal Fintech"
        )


    def verify_mobile_number(self, mobile, otp):
        #self.otp_msg=f'Dear customer, your OTP to verify your mobile number to the Radian app is {otp}. The OTP expires in {(environment.OTP_TIMEOUT / 60)} minutes.'
        return self.__process_sms(mobile, otp)

    def sendLeadGenerationOtp(self, mobile: str, otp: str):
        return self.__process_sms(
            mobile, 
            otp, 
            template_id=settings.SMS_LEAD_GENERATION_TEMPLATE_ID, 
            text=settings.SMS_LEAD_GENERATION_OTP_TEXT
        )

    def sendPanVerificationOtp(self, mobile: str, otp: str, lead_type=None):
        is_balance_transfer = str(lead_type or "").strip().upper() in {
            "BT",
            "BALANCE_TRANSFER",
            "BALANCE TRANSFER",
        }
        template_id = getattr(settings, "SMS_PAN_VERIFICATION_TEMPLATE_ID", "1007788001501641886")
        text = getattr(
            settings,
            "SMS_PAN_VERIFICATION_OTP_TEXT",
            "Dear customer, To complete onboarding, we need your consent to process personal data including KYC & Credit Bureau checks and to contact you. Code to share your consent is {#var#}. - Team Manipal Fintech",
        )
        if is_balance_transfer:
            template_id = getattr(settings, "SMS_BT_PAN_VERIFICATION_TEMPLATE_ID", "1007613213003792024")
            text = getattr(
                settings,
                "SMS_BT_PAN_VERIFICATION_OTP_TEXT",
                "Dear Customer, OTP {#var#} confirms your consent to process your personal data for onboarding including KYC verification, credit bureau checks, Account Aggregator Services and to contact you. You also consent to recording of your interaction with our sales officer for service and assessment purposes. - Team Manipal Fintech (LSP of Simplepay Finance Pvt Ltd)",
            )
        return self.__process_sms(
            mobile,
            otp,
            template_id=template_id,
            text=text,
        )


    def sendLeadAutoClosedNotification(self, mobile: str, customer_name: str, lead_code: str):
        template_text = getattr(
            settings,
            "SMS_LEAD_AUTO_CLOSED_TEXT",
            "Lead {#var#} ({#var#}) has been auto-closed due to inactivity. Manipal Fintech Private Limited",
        )
        text = template_text.replace("{#var#}", str(customer_name), 1).replace("{#var#}", str(lead_code), 1)
        template_id = getattr(settings, "SMS_LEAD_AUTO_CLOSED_TEMPLATE_ID", None)
        return self.__process_sms_no_otp(mobile, text, template_id)

    def __process_sms_no_otp(self, mobile, text, template_id=None):
        if mobile == environment.TEST_LM_PHONE or mobile == environment.TEST_CUSTOMER_PHONE:
            return "Test success"
        num = str(mobile)
        if num.startswith("+91"):
            num = num[1:]
        if not num.startswith("91"):
            num = f"91{num}"
        
        dlt_template_id = template_id or settings.SMS_TEMPLATE_ID

        payload = {
            "Account": {
                "APIkey": settings.SMS_API_KEY,
                "SenderId": settings.SMS_SENDER_ID,
                "Channel": "2",
                "DCS": "0",
                "SchedTime": None,
                "GroupId": None,
                "EntityId": settings.SMS_ENTITY_ID,
            },
            "Messages": [
                {
                    "Text": text,
                    "DLTTemplateId": dlt_template_id,
                    "Number": num,
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            "https://www.smsgatewayhub.com/api/MT/SendSMS",
            json=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return "SMS sent successfully"
        return "Failed to send SMS"

    def __process_sms(self, mobile, otp, template_id=None, text=None):
        if mobile == environment.TEST_LM_PHONE or mobile == environment.TEST_CUSTOMER_PHONE:
            return otp
        num = str(mobile)
        if num.startswith("+91"):
            num = num[1:]
        if not num.startswith("91"):
            num = f"91{num}"
        
        sms_text = text or settings.SMS_OTP_TEXT
        dlt_template_id = template_id or settings.SMS_TEMPLATE_ID

        payload = {
            "Account": {
                "APIkey": settings.SMS_API_KEY,
                "SenderId": settings.SMS_SENDER_ID,
                "Channel": "2",
                "DCS": "0",
                "SchedTime": None,
                "GroupId": None,
                "EntityId": settings.SMS_ENTITY_ID,
            },
            "Messages": [
                {
                    "Text": sms_text.replace("{#var#}", str(otp)),
                    "DLTTemplateId": dlt_template_id,
                    "Number": num,
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            "https://www.smsgatewayhub.com/api/MT/SendSMS",
            json=payload,
            headers=headers,
            timeout=10
        )
        print("OTP message:,", response.text)
        if response.status_code == 200:
            return "OTP sent successfully"
        return "Failed to send OTP"

    def __send_sms(self, sms_text, mobile):
        # url = f"https://103.229.250.200/smpp/sendsms?username=radianhttp&from=RADFNS&to={str(mobile).replace('+91', '')}&udh=&text=" + sms_text
        url = f"https://http.myvfirst.com/smpp/sendsms?username=radianhttp&from=RADFNS&to={str(mobile).replace('+91', '')}&udh=&text=" + sms_text
        payload = ""
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaS5teXZhbHVlZmlyc3QuY29tL3BzbXMiLCJzdWIiOiJyYWRpYW5odHRwIiwiZXhwIjoyMDA1ODE5NTYyfQ.v66VcopAyWI-CqQe0wcOjP2Ghp4Tbo4YlyfDjadU7qg'
        }
        print(sms_text)
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    def send_status_update(self, template,mobile, application_no,customer_name):
        template_msg=urllib.parse.quote(MessageTemplates().message_template(template, application_no, customer_name))
        response=self.__send_sms(sms_text=template_msg, mobile=mobile)
        print(response, response.text)
        if response.text.replace(".", "").lower() == "sent":
            return "Update sms sent successfully"
        return "Failed to send sms"
