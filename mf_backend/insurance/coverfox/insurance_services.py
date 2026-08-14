import json

import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from insurance.coverfox.utils.auth import AUTH_TOKEN, generate_partner_token, medibuddy_corporate_id


def get_sso_url(request_payload):

    cover_fox_username = getattr(settings, "COVER_FOX_USERNAME", None) or ""
    cover_fox_password = getattr(settings, "COVER_FOX_PASSWORD", None) or ""
    cover_fox_request_token_url = getattr(settings, "COVER_FOX_REQUEST_TOKEN_URL", None) or "https://manipalfintech.coverfox-uat.uat.coverstack.net/b2c/sso/request-token/"
    cover_fox_login_url = getattr(settings, "COVER_FOX_LOGIN_URL", None) or "https://manipalfintech.coverfox-uat.uat.coverstack.net/b2c/login/"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'landing_page_url={cover_fox_request_token_url}'
    }
    response = requests.request("POST", cover_fox_request_token_url, headers=headers, data=request_payload,
                                auth=HTTPBasicAuth(cover_fox_username, cover_fox_password),verify=False,
                                timeout=10)
    response.raise_for_status()
    token = response.json()["access_token"]
    if not token:
        return None
    return f"{cover_fox_login_url}?token={token}"


def get_medibuddy_sso_url(mobile_number, employee_id):
    medibuddy_request_url = "https://bifrost-prod.medibuddy.in/sdk/affinity/user-upsell-sso-url"
    headers = {
        'x-api-token': AUTH_TOKEN,
        'corporateid': medibuddy_corporate_id,
        "Content-Type": "application/json",
    }
    token = generate_partner_token(
        reversed_mobile=mobile_number,
        employee_id=employee_id)

    request_payload= json.dumps({
        "token": token,
        "createUserIfNotExists": True
    })

    response = requests.request("POST", medibuddy_request_url, headers=headers, data=request_payload,timeout=30,verify=False)
    response.raise_for_status()
    data=response.json().get("data",{})
    sso_url=data.get("ssoUrl",{})
    if not sso_url:
        return None
    return f"{sso_url}&redirect=/affinity"

