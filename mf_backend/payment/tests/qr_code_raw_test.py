"""
# To run this
sudo docker exec -it radian_app  bash
python3 manage.py shell
exec(open('payment/tests/qr_code_raw_test.py').read())
"""


import requests
import json
import datetime
import time
from payment.utils.cipherkey_utils import CipherpayHelper

utils = CipherpayHelper()
now = datetime.datetime.now()
req_id = utils.generate_req_ref_id(time_now=now, loan_number="DUMMY_LOAN_ID")
jwt_token = utils.generate_jwt(now, utils.jwt_key, req_id=req_id)

print("jwt_token:: ", jwt_token, "\n")
print("auth_header:: ", utils.auth_header, "\n")
print("key_header:: ", utils.key_header, "\n")



"""

url = "https://uatapi.cipherpay.co.in/api/v3/payin/dynamic-qr"

payload = json.dumps({
  "receiver_vpa": "cpy.radian@fin",
  "amount": "100",
  "remarks": "UPI Collect",
  "refid": "1234567",
  "expiry": "5",
  "type": "QR"
})
"""

url = "https://uatapi.cipherpay.co.in/api/v3/payin/initiate-collect"
payload = json.dumps(
    {
        "sender_vpa": "cpy.radian@fin",
        "sender_name": "Money sender",
        "sender_mobile": "9999999999",
        # "receiver_vpa": "cp.corp@fin",
        "receiver_vpa": "cpy.radian@fin",
        "amount": "100",
        "remarks": "UPI Collect",
        "refid": f"{time.time()}",
        "expiry": "5",
    }
)

print("payload: ", payload)


headers = {
    "Token": jwt_token,
    "Content-Type": "application/json",
    "User-Agent": "APIAGENT/7.29.2",
    "Key": utils.key_header,
    # 'Key': encrypt_with_body_public_key(salt),
    "Auth": utils.auth_header,
    # 'Auth':  encrypt_with_header_public_key(
    #     '{"partnerId":"CP00392","headerToken":"fKm2O9A8JB-pAEZpSwjcS-rhhXi-lepCAH7xHBwP0dT"}'
    # )
    # 'Authorization': 'Bearer fasYOkO7l5XixxTkQMJYwFHO1YYZAT'
}


print(headers)
encPayload = utils.encrypt_body(payload, utils.salt, utils.aes_key)
print("encPayload: ", encPayload, "\n")

# print("decrypt")
# decoded = utils.decrypt_aes_cbc(iv = utils.salt,encrypted_data=encPayload, aes_key=utils.aes_key)
# print(decoded)


# response = requests.request("POST", url, headers=headers, data=payload)
response = requests.request(
    "POST", url, headers=headers, json={"requestData": encPayload}
)

print(response.text)
# decrypted_data = utils.decrypt_body(iv=utils.salt,encrypted_data=response["returnData"], key = utils.aes_key)
decrypted_data = utils.decrypt_body(iv=utils.salt,encrypted_data=response.text["returnData"], key = utils.aes_key)
print(response.status_code)
# print(response.json())
print(response.text)
