import datetime
import os
import uuid
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent

def axis_bank_call(jwe_token_data, endpoint):
    certFile = os.path.join(BASE_DIR, "onboarding_v2/integrations/axis/certs/sahibandhu-client.crt")
    keyFile = os.path.join(BASE_DIR, "onboarding_v2/integrations/axis/certs/sahibandhu-private.key")

    url = f"https://sakshamuat.axisbank.co.in/gateway/api/v2/CRMNext/{endpoint}"
    print(f"Testing URL: {url}")
    
    # Try with resolve to the IP we found earlier if DNS fails, 
    # but for now let's just update the URL as requested.
    response = requests.post(
        url,
        data=jwe_token_data,
        headers={
            "Content-Type": "text/plain",
            "X-IBM-Client-Id": "72ce6df971a8b255d622b48f0b704df2",
            "X-IBM-Client-Secret": "3f39dded1b52f089f3282493a007f0e3",
            "x-fapi-channel-id": "SAHIBANDHU",
            "x-fapi-epoch-millis": str(int(datetime.datetime.now().timestamp() * 1000)),
            "x-fapi-uuid": uuid.uuid4().__str__(),
            "x-fapi-serviceId": "OpenAPI",
            "x-fapi-serviceVersion": "1.0",
        },
        cert=(certFile, keyFile),
        verify=False,
    )

    return response


if __name__ == "__main__":
    # Test the login endpoint
    print("Testing Axis Login...")
    try:
        # Dummy payload for login test
        dummy_payload = "dummy_encrypted_data"
        resp = axis_bank_call(dummy_payload, "login")
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")
    except Exception as e:
        print(f"Error occurred: {e}")
