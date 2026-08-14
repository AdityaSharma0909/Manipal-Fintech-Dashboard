
import hashlib
import hmac
import time
import jwt
from django.conf import settings

medibuddy_secret_key = getattr(settings, "MEDI_BUDDY_SECRET_KEY").encode("utf-8")
medibuddy_url = getattr(settings, "MEDI_BUDDY_URL", None) or 'https://bifrost-prod.medibuddy.in/sdk/affinity/user-upsell-sso-url'
medibuddy_corporate_id = getattr(settings, "MEDI_BUDDY_CORPORATE_ID", None) or ""
MEDI_BUDDY_SHARED_SECRET = getattr(settings, "MEDI_BUDDY_SHARED_SECRET", None) or ""

AUTH_TOKEN = hmac.new(
    medibuddy_secret_key,
    medibuddy_url.encode(),
    hashlib.sha256,
).hexdigest()

def generate_partner_token(reversed_mobile, employee_id):
    current_time = int(time.time())
    payload = {
        "mobileNumber": reversed_mobile,
        "employeeId": employee_id,
        "entityId": medibuddy_corporate_id,
        "iat": current_time,
        "exp": current_time + 60000
    }
    token = jwt.encode(payload, MEDI_BUDDY_SHARED_SECRET, algorithm="HS256")
    return token


