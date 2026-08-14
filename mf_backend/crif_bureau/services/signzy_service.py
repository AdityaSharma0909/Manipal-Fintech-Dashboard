import logging

import requests
from django.conf import settings
from requests import RequestException, Timeout

logger = logging.getLogger(__name__)

SIGNZY_BASE_HEADERS = {
    "Authorization": getattr(settings, "SIGNZY_EXP_AUTH_TOKEN", ""),
    "Content-Type": "application/json",
}


def phone_to_pan(mobile_number: str, first_name: str, last_name: str):
    url = "https://api-preproduction.signzy.app/api/v3/phonekyc/phonetoPan"
    payload = {
        "phoneNumber": mobile_number,
        "firstName": first_name,
        "lastName": last_name,
    }
    try:
        response = requests.post(url, headers=SIGNZY_BASE_HEADERS, json=payload, timeout=10)
        return response
    except (Timeout, RequestException) as exc:
        logger.exception("Error while calling Signzy phone_to_pan API")
        raise exc

def send_crif_request(request_payload: dict):
    url = "https://api-preproduction.signzy.app/api/v3/test-encrypt-data"
    headers = SIGNZY_BASE_HEADERS.copy()

    try:
        response = requests.post(url=url, headers=headers, json=request_payload, timeout=20)
        response.raise_for_status()
        return response
    except (Timeout, RequestException) as exc:
        logger.exception("Error while calling Signzy send_crif_request API")
        raise exc


def create_bureau_consent(request_data: str):
    url = "https://api-preproduction.signzy.app/api/v3/create-bureau-consent"
    headers = SIGNZY_BASE_HEADERS.copy()
    payload = {
        "requestData": request_data
    }
    try:
        response = requests.post(url=url, headers=headers, json=payload, timeout=20)
        if not (200 <= response.status_code < 300):
            logger.error("Signzy create_bureau_consent returned %s: %s", response.status_code, response.text)
        response.raise_for_status()


        return response
    except (Timeout, RequestException) as exc:
        logger.exception("Error while calling Signzy create_bureau_consent API")
        raise exc


def decrypt_data(request_data: str):
    url = "https://api-preproduction.signzy.app/api/v3/test-decrypt-data"
    headers = SIGNZY_BASE_HEADERS.copy()
    payload = {"requestData": request_data}

    try:
        response = requests.post(url=url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()     
        return response
    except (Timeout, RequestException) as exc:
        logger.exception("Error while calling Signzy decrypt_data API")
        raise exc

def crif_report_request(request_payload: dict):
    url = "https://api-preproduction.signzy.app/api/v3/bureau/crif"
    headers = SIGNZY_BASE_HEADERS.copy()

    try:
        print(f"Sending request to Signzy CRIF API: {request_payload}")
        response = requests.post(url=url, headers=headers, json=request_payload, timeout=20)
        return response
    except (Timeout, RequestException) as exc:
        logger.exception("Error while calling Signzy send_crif_request API")
        raise
    