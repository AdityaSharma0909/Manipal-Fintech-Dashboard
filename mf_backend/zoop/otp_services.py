import requests
from django.conf import settings

def send_sms_otp(mobile_number, otp):
    """
    Send OTP SMS using SMSGatewayHub.
    Replaces {#var#} in the template with  the actual OTP.
    """

    

    # Add country code if missing
    if not mobile_number.startswith("91"):
        mobile_number = f"91{mobile_number}"

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
                "Text": settings.SMS_OTP_TEXT.replace("{#var#}", str(otp)),
                "DLTTemplateId": settings.SMS_TEMPLATE_ID,
                "Number": mobile_number,
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            "https://www.smsgatewayhub.com/api/mt/SendSMS", 
            json=payload, 
            headers=headers,
            timeout=10
        )
        response_data = response.json()
        return response_data
    except Exception as e:
        raise





