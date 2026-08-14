from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding as symmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from payment.models import Repayment
from payment.serializers import RepaymentModelSerializer

from utils.constants import REPAYMENT_PAYMENT_STATUS, REPAYMENT_PAYMENT_MODE

# from base64 import b64encode

import hashlib
import secrets
import binascii

import jwt
import json

import datetime
import requests
import base64
import os

from utils.envSetup import environment
from django.conf import settings

# Callback URL: https://dev-api.radianfinserv.com/payment/upi/callback/


class CipherpayHelper:
    def __init__(self):
        self.header_public_key = os.path.join(
            settings.BASE_DIR, "keys", "cipherpay", environment.PAYMENT_ENV, "header_public_key.pem"
        )
        self.body_public_key = os.path.join(
            settings.BASE_DIR, "keys", "cipherpay", environment.PAYMENT_ENV, "body_public_key.pem"
        )
        self.private_key_path = os.path.join(
            settings.BASE_DIR, "keys", "cipherpay", environment.PAYMENT_ENV, "cipherpay_private_key.pem"
        )
        self.radian_vpa = environment.RADIAN_VPA
        self.partner_code = environment.CIPHERPAY_PARTNER_CODE
        self.partner_id = environment.CIPHERPAY_PARTNER_ID
        self.secret = b"CipherPay API Payout"
        self.jwt_key = environment.CIPHERPAY_JWT_KEY
        self.headerToken = environment.CIPHERPAY_HEADER_TOKEN

        self.auth_header = self.generate_header_auth(
            self.partner_code, self.headerToken, self.header_public_key
        )
        print("auth_header: ", self.auth_header)

        self.salt = self.generate_salt()
        print("Salt: ", self.salt)

        self.aes_key = self.generate_aes_key(self.salt, self.secret)
        print("aes_key: ", self.aes_key,)

        # encrypted_salt will be used as Key in header
        self.key_header = self.encrypt_salt(self.salt, self.body_public_key)
        print("key_header: ", self.key_header,)

    def generate_header_auth(self, partner_code, headerToken, header_public_key):
        header_auth_raw_paylod = {
            "partnerId": partner_code,  # CP00392
            "headerToken": headerToken,
        }
        message = json.dumps(header_auth_raw_paylod).encode("utf-8")
        # message = partner_id.encode("utf-8")
        # with open(self.header_public_key, "rb") as key_file:
        with open(header_public_key, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())

        ciphertext = public_key.encrypt(
            message,
            padding.PKCS1v15(),
            # padding.OAEP(
            #     mgf=padding.MGF1(algorithm=hashes.SHA256()),
            #     algorithm=hashes.SHA256(),
            #     label=None,
            # ),
        )
        # print("ciphertext")
        # print(ciphertext)

        base64_bytes = base64.b64encode(ciphertext)
        base64_string = base64_bytes.decode()
        return base64_string

    def encrypt_body(self, data, iv, key):
        encrypted = json.dumps(data).encode("utf-8")
        # cipher = AES.new(base64.b64decode(key), AES.MODE_CBC,  iv.encode('utf-8'))
        # cipher = AES.new(base64.b64decode(key), AES.MODE_CBC,  iv)
        cipher = AES.new(base64.b64decode(key), AES.MODE_CBC, iv)
        padded_data = pad(encrypted, AES.block_size)
        decrypted = cipher.encrypt(padded_data)
        return base64.b64encode(decrypted).decode("utf-8")

    def decrypt_body(self, encrypted_data, iv, key):
        # Decode the Base64-encoded data
        encrypted_data = base64.b64decode(encrypted_data)
        
        # Create an AES cipher object with the provided key and IV
        cipher = AES.new(base64.b64decode(key), AES.MODE_CBC, iv)
        
        # Decrypt the data and remove padding
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        
        # Convert the decrypted data to a string
        decrypted_body = decrypted_data.decode("utf-8")
    
        return decrypted_body

    """

    def encrypt_body(self, data, iv, aes_key):
        # data = b64encode(data).decode('utf-8')
        data = json.dumps(data).encode("utf-8")

        # aes_key = base64.b64decode(aes_key+ b'=' * (-len(aes_key) % 4)).decode()
        print()
        print("aes_key")
        print(aes_key)
        print(iv)
        print()

        # Step 3: Encrypt the body using the AES key
        cipher = Cipher(
            # algorithms.AES(aes_key), modes.CFB(b"\0" * 16), backend=default_backend()
            # algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend()
            algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        padder = symmetric_padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        raw_ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        print("ciphertext: ", raw_ciphertext, "\n")
       
        ciphertext = raw_ciphertext#.decode("latin-1").encode('utf-8')

        print("ciphertext: ", ciphertext, "\n")

        # Step 4: Convert the encrypted data to Base64
        base64_encrypted_body = base64.b64encode(ciphertext).decode()

        return base64_encrypted_body
    """
    """
    def encrypt_body(self, data, iv, aes_key):
        # data = b64encode(data).decode('utf-8')
        data = json.dumps(data).encode("utf-8")

        # aes_key = base64.b64decode(aes_key+ b'=' * (-len(aes_key) % 4)).decode()
        print()
        print("aes_key")
        print(aes_key)
        print(iv)
        print()
        # aes_key = base64.b64decode(aes_key)
        # aes_key = base64.b64encode(aes_key)
        # Step 1: Create a 16 Character Hexadecimal Salt
        # salt = self.generate_salt()r

        # Step 2: Generate an AES key using the salt and a secret
        # key_material = salt.encode('utf-8') + global_secret_key.encode('utf-8')
        # key_material = salt + aes_key
        # key = hashlib.pbkdf2_hmac('sha256', key_material, salt, 100000, 32)
        
        # Step 3: Encrypt the body using the AES key
        cipher = Cipher(
            # algorithms.AES(aes_key), modes.CFB(b"\0" * 16), backend=default_backend()
            # algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend()
            algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        padder = symmetric_padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        raw_ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        print("ciphertext: ", raw_ciphertext, "\n")
       
        ciphertext = raw_ciphertext#.decode("latin-1").encode('utf-8')

        print("ciphertext: ", ciphertext, "\n")

        # iv_padding = iv + ciphertext

        # Step 4: Convert the encrypted data to Base64
        base64_encrypted_body = base64.b64encode(ciphertext).decode()
        # base64_encrypted_body = base64.b64encode(iv_padding).decode()


        # # key = rsa.load_pem_public_key(self.header_public_key, backend=default_backend())
        # # encrypted_salt = key.encrypt(salt.encode('utf-8'), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))s
        # encrypted_salt = key.encrypt(salt, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        # base64_encrypted_salt = b64encode(encrypted_salt).decode('utf-8')

        return base64_encrypted_body
    """

    # Step 5: Encrypt the salt using RSA public key
    def encrypt_salt(self, salt, body_public_key):
        with open(body_public_key, "rb") as key_file:
            key = serialization.load_pem_public_key(key_file.read())

        encrypted_salt = key.encrypt(
            salt,
            padding.PKCS1v15(),
            # padding.OAEP(
            #     mgf=padding.MGF1(algorithm=hashes.SHA256()),
            #     algorithm=hashes.SHA256(),
            #     label=None,
            # ),
        )
        base64_encrypted_salt = base64.b64encode(encrypted_salt).decode("utf-8")
        return base64_encrypted_salt

    def generate_salt(self):
        # salt = os.urandom(16)
        salt = str.encode(secrets.token_hex(8))
        return salt

    def generate_aes_key(self, salt, passphrase):
        salt = binascii.unhexlify(salt)
        # passphrase = b'CipherPay API Payout'
        iteration_count = 10000
        key_size = 128
        hash_algorithm = hashlib.sha1
        dk = hashlib.pbkdf2_hmac(
            hash_algorithm().name, passphrase, salt, iteration_count, key_size
        )
        aes_key = dk[: key_size // 8]
        aes_key_base64 = base64.b64encode(aes_key).decode()
        aes_iv = binascii.hexlify(salt).decode()
        return aes_key_base64  # , aes_iv
        # return aes_key_base64, aes_iv

    def generate_req_ref_id(self, time_now: datetime.datetime, loan_number: str):
        req_ref_id = str(
            int(time_now.timestamp() * 1000)
        )  # *1000 = convert to millisec | int() to remove .0123

        # sytax of reference_id = <LOAN_ID>_<timestamp>
        # return '1270001SLHM883202_'+req_ref_id
        return loan_number + "_" + req_ref_id

    def generate_jwt(
        self, time_now: datetime.datetime, jwt_key, req_id
    ):  # , partner_id):
        # with open(self.private_key_path, "r") as key_file:
        # with open(self.private_key_path, "r") as key_file:
        #     private_key = key_file.read()

        timestamp = time_now.strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "timestamp": timestamp,
            "partnerId": self.partner_id,
            "reqId": req_id,  # (send a unique integer for each request)
        }

        jwt_token = jwt.encode(payload=payload, key=jwt_key, algorithm="HS256")
        print("\n\nJWT Token:", jwt_token, "\n\n")
        return jwt_token

    def decrypt_rsa(self, encrypted_data, key):
        with open(self.private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # Enter the password if your private key is encrypted
                backend=default_backend(),
            )

        decrypted_salt = private_key.decrypt(
            key,
            padding.PKCS1v15(),
        )

        aes_key = self.generate_aes_key(decrypted_salt, self.secret)

        # cipher = AES.new(base64.b64decode(aes_key), AES.MODE_CBC, base64.b64decode(decrypted_salt))
        cipher = AES.new(base64.b64decode(aes_key), AES.MODE_CBC, decrypted_salt)
        # decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
        decrypted_data = cipher.decrypt(encrypted_data)
        unpadded_data = unpad(decrypted_data, AES.block_size)
        decrypted_json = unpadded_data.decode("utf-8")
        decrypted_data_dict = json.loads(decrypted_json)

        return decrypted_data_dict

    def cipherpay_dynamic_qr(self, data, loan_number, loan_id, user, qr_type):
        url = environment.CIPHERPAY_BASE_URL + "payin/dynamic-qr"
        # url = "https://uatapi.cipherpay.co.in/api/v3/payin/dynamic-qr"

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        remarks = f"{timestamp}_{loan_number}"
        # remarks = timestamp + " | "+ loan_number + " | DynamicQR"
        ref_id = self.generate_req_ref_id(time_now=now, loan_number=loan_number)
        token = self.generate_jwt(now, self.jwt_key, ref_id)
        print("\n\nToken:", token, "\n\n")

        payload = {
            "receiver_vpa": self.radian_vpa,
            "amount": data["amount"],
            "remarks": remarks,
            "refid": ref_id,
            "expiry": "5",
            "type": qr_type,
        }
        # payload = json.dumps(payload)
        print("\nPayload:\n\n", payload)
        encPayload = self.encrypt_body(payload, self.salt, self.aes_key)
        payload = {"requestData": encPayload}
        
        success, resp = self.call_cipherpay_api(url=url, payload=payload, token=token)
        if success:
            encrypted_text = json.loads(resp.text)["returnData"]
         
            decrypted_data = self.decrypt_body(
                iv=self.salt, encrypted_data=encrypted_text, key=self.aes_key
            )
    
            decrypted_data = json.loads(decrypted_data)
            print("\nDecrypted Data:\n\n", decrypted_data)
            final_resp = {}
            if "qr" in decrypted_data:
                final_resp["qr"] = decrypted_data["qr"].replace(
                    "\\/", "/"
                )  # Replace "\/"" with /
            decrypted_data    
            if "intent" in decrypted_data:
                final_resp["intent"] = decrypted_data["intent"]
            print("QR CODE:", final_resp["qr"])
            metaData = decrypted_data["data"]
            db_data = {
                "loan": loan_id,
                "initiated_by": user.user_id,
                "created_by": user.user_id,
                "modified_by": user.user_id,
                "amount": metaData["amount"],
                # "reference_id": metaData["refid"],
                # "remarks": metaData["remarks"],
                "reference_id": ref_id,
                "remarks": remarks,
                "utr_no": metaData["utr"],
                "txn_id": metaData["txnid"],
                # "sender_vpa": metaData["sender_vpa"],
                # "sender_name": "sender_name",
                "receiver_vpa": metaData["receiverVpa"],
                "receiver_name": metaData["receiverName"],
                "receiver_account_number": metaData["receiverAccountNumber"],
                "upi_ref_id": metaData["upiRefid"],
                "payment_mode": REPAYMENT_PAYMENT_MODE.DYNAMICQR.value,
                "payment_status": Repayment().get_payment_status(metaData["status"]),
            }

            _, res = self.save_in_db(
                data=db_data, loan_id=loan_id, user=user, ref_id=ref_id
            )
            final_resp.update(res)
        else:
            final_resp = resp

        return success, final_resp

    def cipherpay_initiate_collect(self, data, loan_number, loan_id, user):
        url = environment.CIPHERPAY_BASE_URL + "payin/initiate-collect"
        # url = "https://uatapi.cipherpay.co.in/api/v3/payin/initiate-collect"

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        remarks = f"{timestamp}_{loan_number}"
        # remarks = timestamp + " | "+ loan_number + " | InitiateCollect"
        ref_id = self.generate_req_ref_id(time_now=now, loan_number=loan_number)
        token = self.generate_jwt(now, self.jwt_key, ref_id)

        payload = {
            "sender_vpa": data["sender_vpa"],
            "sender_name": data["sender_name"],
            "sender_mobile": data["sender_mobile"],
            "receiver_vpa": self.radian_vpa,
            "amount": data["amount"],
            "remarks": remarks,
            "refid": ref_id,
            "expiry": "5",
        }
        print("Payload:", payload)

        encPayload = self.encrypt_body(payload, self.salt, self.aes_key)
        payload = {"requestData": encPayload}

        responsePayload = {}
        success, resp = self.call_cipherpay_api(url=url, payload=payload, token=token)
        if success:
            encrypted_text = json.loads(resp.text)["returnData"]
            decrypted_data = self.decrypt_body(
                iv=self.salt, encrypted_data=encrypted_text, key=self.aes_key
            )
            # decrypted_data = """{"statuscode":200,"status":true,"responsecode":1,"data":{"refid":"1270001SLHM245882_1708081186008","sender_name":"Radian Dev Server","sender_vpa":"cpy.radian@fin","receiver_name":"Radian Finserv","receiver_vpa":"cpy.radian@fin","txnid":"538669","upiRefId":null,"amount":"100.00","remarks":"2024-02-16 16:29:46_1270001SLHM245882","status":2,"utr":null,"msg":"Transaction initiated successfully"}}"""
            decrypted_data = json.loads(decrypted_data)
            print("Decrypted Data:", decrypted_data)

            # responsePayload = final_resp["data"]
            # responsePayload["transactionType"] = (
            #     REPAYMENT_PAYMENT_MODE.VPA_REQUEST.value
            # )

            metaData = decrypted_data["data"]
            # {
            #     "refid":"1270001SLHM120392_1710307383539",
            #     "sender_name":"Radian Dev Server",
            #     "sender_vpa":"cpy.radian@fin",
            #     "receiver_name":"Radian Finserv",
            #     "receiver_vpa":"cpy.cipher@fin",
            #     "txnid":"228761",
            #     "upiRefId":"None",
            #     "amount":"2500.00",
            #     "remarks":"2024-03-13 10:53:03_1270001SLHM120392",
            #     "status":2,
            #     "utr":"None",
            #     "msg":"Transaction initiated successfully"
            # }
            db_data = {
                "loan": loan_id,
                "initiated_by": user.user_id,
                "created_by": user.user_id,
                "modified_by": user.user_id,
                "amount": metaData["amount"],
                "reference_id": metaData["refid"],
                "remarks": metaData["remarks"],
                "utr_no": metaData["utr"],
                "txn_id": metaData["txnid"],
                "sender_vpa": metaData["sender_vpa"],
                "sender_name": "sender_name",
                "receiver_vpa": metaData["receiver_vpa"],
                "receiver_name": metaData["receiver_name"],
                # "receiver_account_number": metaData["receiverAccountNumber"],
                # "upi_ref_id": metaData["upiRefid"],
                "payment_mode": REPAYMENT_PAYMENT_MODE.VPA_REQUEST.value,
                "payment_status": Repayment().get_payment_status(metaData["status"]),
            }

            _, res = self.save_in_db(data=db_data, loan_id=loan_id, user=user, ref_id=ref_id)
            responsePayload = res
        else:
            responsePayload = resp

        return success, responsePayload
    


    def cipherpay_fetch_status(self, reference_id):
        url = environment.CIPHERPAY_BASE_URL + "payin/status-enquiry"
        # url = "https://uatapi.cipherpay.co.in/api/v3/payin/status-enquiry"

        now = datetime.datetime.now()
        token = self.generate_jwt(now, self.jwt_key, reference_id)

        payload = {
            "refid": reference_id,
        }
        # payload = json.dumps(payload)
        print("Payload:", payload)
        encPayload = self.encrypt_body(payload, self.salt, self.aes_key)
        payload = {"requestData": encPayload}

        success, resp = self.call_cipherpay_api(url=url, payload=payload, token=token)
        if success:
            encrypted_text = json.loads(resp.text)["returnData"]
            decrypted_data = self.decrypt_body(
                iv=self.salt, encrypted_data=encrypted_text, key=self.aes_key
            )
            decrypted_data = json.loads(decrypted_data)
            print("Decrypted Data:", decrypted_data)
            # final_resp = {}
            # db_data = {
            #     "loan": loan_id,
            #     "initiated_by": user.user_id,
            #     "created_by": user.user_id,
            #     "modified_by": user.user_id,
            #     "amount": metaData["amount"],
            #     # "reference_id": metaData["refid"],
            #     # "remarks": metaData["remarks"],
            #     "reference_id": ref_id,
            #     "remarks": remarks,
            #     "utr_no": metaData["utr"],
            #     "txn_id": metaData["txnid"],
            #     # "sender_vpa": metaData["sender_vpa"],
            #     # "sender_name": "sender_name",
            #     "receiver_vpa": metaData["receiverVpa"],
            #     "receiver_name": metaData["receiverName"],
            #     "receiver_account_number": metaData["receiverAccountNumber"],
            #     "upi_ref_id": metaData["upiRefid"],
            #     "payment_mode": REPAYMENT_PAYMENT_MODE.DYNAMICQR.value,
            #     "payment_status": Repayment().get_payment_status(metaData["status"]),
            # }

            # _, res = self.save_in_db(
            #     data=db_data, loan_id=loan_id, user=user, ref_id=ref_id
            # )
            # final_resp.update(res)

            final_resp = decrypted_data["data"]
        else:
            final_resp = resp

        return success, final_resp
    


    def modify_data_to_save(self, data):
        return_data = {}

        # if "user" in data:
        #     return_data["initiated_by"] = data["user"]
        #     return_data["created_by"] = data["user"]

        if "transactionType" in data:
            return_data["payment_mode"] = data["transactionType"]
            # if data["transactionType"] == "DynamicQR": return_data["payment_mode"] = REPAYMENT_PAYMENT_MODE.DYNAMICQR.value
            # elif data["transactionType"] == "InitiateCollect": return_data["payment_mode"] = REPAYMENT_PAYMENT_MODE.VPA_REQUEST.value
            # elif data["transactionType"] == "Cash": return_data["payment_mode"] = REPAYMENT_PAYMENT_MODE.CASH.value
            # else:
            #     print("===== ERROR IN 'transactionType' =====")
            #     print(data["transactionType"])

        if "status" in data:
            if str(data["status"]) == "0":
                return_data["payment_status"] = (
                    REPAYMENT_PAYMENT_STATUS.TRANSACTION_FAILED_0.value
                )
            elif str(data["status"]) == "1":
                return_data["payment_status"] = (
                    REPAYMENT_PAYMENT_STATUS.TRANSACTION_SUCCESSFUL_1.value
                )
            elif str(data["status"]) == "2":
                return_data["payment_status"] = (
                    REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_2.value
                )
            elif str(data["status"]) == "3":
                return_data["payment_status"] = (
                    REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_3.value
                )
            elif str(data["status"]) == "4":
                return_data["payment_status"] = (
                    REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_4.value
                )
            else:
                print("===== ERROR IN 'status' =====")
                print(data["status"])

        replace_matrix = {
            "loan": "loan_id",
            "initiated_by": "user",
            "created_by": "user",
            "modified_by": "user",
            "amount": "amount",
            "reference_id": "refid",
            "remarks": "remarks",
            "utr_no": "utr",
            "txn_id": "txnid",
            "sender_vpa": "sender_vpa",
            "sender_name": "sender_name",
            "receiver_vpa": "receiver_vpa",
            "receiver_name": "receiver_name",
            "receiver_account_number": "receiverAccountNumber",
        }

        for each_key, each_item in replace_matrix.items():
            if each_item in data:
                return_data[each_key] = data[each_item]

        return return_data

    def save_in_db(self, data: dict, loan_id, user=None, ref_id=None):

        formatted_data = data

        formatted_data.update(
            {
                "loan_id": loan_id,
                "user": user.user_id,
                "refid": ref_id,
            }
        )
        if user:
            formatted_data["user"] = user.user_id

        # print("formatted_data: ", formatted_data)

        # new_data = self.modify_data_to_save(formatted_data)

        # print("\n\nnew_data: ", new_data)

        repayment_ser = RepaymentModelSerializer(data=formatted_data)
        if repayment_ser.is_valid():
            repayment_ser.save()
            print("data sucessfully saved in DB")
        else:
            print("Errors")
            print(repayment_ser.errors)
            return False, repayment_ser.errors

        return True, repayment_ser.data

    def call_cipherpay_api(self, url, payload, token, method="POST"):

        headers = {
            "Token": token,
            "Content-Type": "application/json",
            "User-Agent": "APIAGENT/7.29.2",
            "Key": self.key_header,
            "Auth": self.auth_header,
        }
        # payload = json.dumps(payload)
        # encPayload = self.encrypt_body(payload, self.salt, self.aes_key)
        # payload = {"requestData": payload}
        # print("encPayload: ", payload, "\n")

        # encrypted_payload = self.encrypt_body(payload)
        # response = requests.request(method, url, headers=headers, data=encrypted_payload)

        response = requests.request(method, url, headers=headers, json=payload)

        if response.status_code == 404:
            message = "Resource not found"
            return False, message
        elif response.status_code != 201 and response.status_code != 200:
            return False, response.text
        elif "error" in response.text:
            print("# ===== Error Detected ===== #")
            print(response)
            print(response.text)

            return False, json.loads(response.text)["error"]

        return True, response


# cipherpay_utils = CipherpayHelper()
# global_auth = cipherpay_utils.generate_header_auth()
# global_secret_key = cipherpay_utils.generate_secret_key()
# global_key = cipherpay_utils.rsa_encrypt_salt()
# encrypted_body, global_key = cipherpay_utils.encrypt_body({"Test": "Passes"})


# Testing
# cipherpay_utils = CipherpayHelper()
# auth_header = cipherpay_utils.generate_header_auth()
# global_key = cipherpay_utils.generate_body_key()

# encrypted_body = cipherpay_utils.encrypt_body({"Test": "Passes"})
# print("encrypted_body")
# print(encrypted_body)
# salt = cipherpay_utils.generate_salt()
# printableSalt = salt.decode('latin-1')
# print("Printable salt: ", printableSalt, "\n")


# raw_aes_key = cipherpay_utils.generate_aes_key(salt)
# aes_key = raw_aes_key#.decode("latin-1")
# print("AES: ", aes_key)


# global_key = cipherpay_utils.rsa_encrypt_salt(salt)
# print("global_key")
# print(global_key, "\n")
# global_key = cipherpay_utils.generate_key()


web_hook_request = """ILxehoscp+GyNVUr0h6lsSIkwv5K5j4Dxei1TqUL1xP+Pig60/
oxW7Eld352+9K3zBCydMG6xX7vir7Qw9Oefgk3PMHZU42Z3vIYXCc5I+OskI4iFLl6qiat
/h4/OFNgXebW4uQiIj8n/i9C8xMW9RcZqiQBUhCnSa8uEKAt1pXZ/
irkD3v5x9mjZnp3aL80CPyxXzy286XHK2NJ7JkJx8g0VkWQPSbTbws+21AO3DyM1gVjN
3yNUkXAeWB/ka64AXp/
dNEM5xA0KPGdRqTHKd75iCQOuMad6sJXpJMdfyu1w3JcPsF/DsScW9RvwT/
IsXqUZK5IRcyCUc6+tKlfSPCvNuT1/I5Q7oyhu2L0sGt/4w4QbFVPStHFx0K6D07AWVW/
e0/GkId/
JtVjVg28VOWXK8VCq8LOHQXT6dmAzmIwbVBYnSyIcn2wAOghi7dPbzWglHL+1EY4
bGi26KAqSAzx/
rLfdsHg1EWcgOYRV5K6yvBnYm0xd4R11R0I1owI7RqmC1y6VZoXTMTSlko5+u8SiNb/ejoF+3n01+BElL18fnPdThPX/rtF2T8hFbg1y5cFoRP/
619WbRtAwFEMqe2zN33Wi9jqIDqEXptWVbW7pKFDswMUyNJRYqXUfgiQikfUnSxrp6
HXGAmySaZy2Q=="""


web_hook_request = "ILxehoscp+GyNVUr0h6lsSIkwv5K5j4Dxei1TqUL1xP+Pig60/oxW7Eld352+9K3zBCydMG6xX7vir7Qw9Oefgk3PMHZU42Z3vIYXCc5I+OskI4iFLl6qiat/h4/OFNgXebW4uQiIj8n/i9C8xMW9RcZqiQBUhCnSa8uEKAt1pXZ/irkD3v5x9mjZnp3aL80CPyxXzy286XHK2NJ7JkJx8g0VkWQPSbTbws+21AO3DyM1gVjN3yNUkXAeWB/ka64AXp/dNEM5xA0KPGdRqTHKd75iCQOuMad6sJXpJMdfyu1w3JcPsF/DsScW9RvwT/IsXqUZK5IRcyCUc6+tKlfSPCvNuT1/I5Q7oyhu2L0sGt/4w4QbFVPStHFx0K6D07AWVW/e0/GkId/JtVjVg28VOWXK8VCq8LOHQXT6dmAzmIwbVBYnSyIcn2wAOghi7dPbzWglHL+1EY4bGi26KAqSAzx/rLfdsHg1EWcgOYRV5K6yvBnYm0xd4R11R0I1owI7RqmC1y6VZoXTMTSlko5+u8SiNb/ejoF+3n01+BElL18fnPdThPX/rtF2T8hFbg1y5cFoRP/619WbRtAwFEMqe2zN33Wi9jqIDqEXptWVbW7pKFDswMUyNJRYqXUfgiQikfUnSxrp6HXGAmySaZy2Q=="
webhook_param_enc = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyZWZpZCI6IjIwMzgxNDkiLCJhY2tubyI6MTIxOTUsIm5hbWUiOiJDSEFORFJBU0hFS0hBUiIsIm1vYmlsZSI6Ijk1OTEwODIwMTQiLCJhbW91bnQiOiIxOTAwLjAwIiwiY2hhcmdlIjoiMS41NSIsInJlbWFya3MiOm51bGwsInN0YXR1cyI6MSwidXRyIjoiMjM0OTExMzg1NDk5In0.qM1sIz6NIiNAwwzFevYrbyLwmZ3l3yAcOiBq7FcPZE4"
webhook_headers = "Qv5KhCVtuKioCwGEQzCIXlNSHTw80YUWI34J+p849couneAd86MJUNK6v6ST8Hfv8RQMR9viTGCdTezCNNck/jjpguxcKG0lDQfeeHAMjJr/TOao/UT4FTnHcogxBFyh2wteZYX6iUI09JjZme2wbwSqBJyP0WzwocPnP5ApjJSlGpLh2k2lROzFe/FAie6wPd2X9oM7w76FQGtvfsX43m1xZeVFVFz2AIPa46GtEyBZP0MRW10cbaC/+wjXMUoQ+6UR7z4/PEiJgM/aoNXkTNmlH0HrTvkOc6sPI9sGfBtBv1RZJQGqjP5pLAELgXkCav0+DmVLHwlXe+3Bof+PBg=="


# decrypt_webhook_message = cipherpay_utils.decrypt_rsa(web_hook_request)
# decrypt_webhook_message = cipherpay_utils.decrypt_rsa(web_hook_request.encode("utf-8"))
# decrypt_webhook_message = cipherpay_utils.decrypt_rsa(base64.b64encode(web_hook_request.encode("utf-8")))
# print("decrypt_rsa")
# print(decrypt_webhook_message)
