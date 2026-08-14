import json

import base64
import os
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class AES128:
    @staticmethod
    def encrypt(word, password, private_key):
        try:
            salt_bytes = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashlib.sha1(),
                iterations=50,
                salt=salt_bytes,
                length=16,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            iv_bytes = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv_bytes), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_text_bytes = encryptor.update(word.encode('utf-8')) + encryptor.finalize()

            # Create a digital signature
            private_key = serialization.load_pem_private_key(private_key.encode(), password=None, backend=default_backend())
            signature = private_key.sign(
                encrypted_text_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            buffer = salt_bytes + iv_bytes + encrypted_text_bytes + signature
            return base64.urlsafe_b64encode(buffer).decode('utf-8')
        except Exception as e:
            return "ER001" + str(e)

    @staticmethod
    def decrypt(encrypted_text, password, public_key):
        try:
            encrypted_text_bytes = base64.urlsafe_b64decode(encrypted_text)
            salt_bytes = encrypted_text_bytes[:16]
            iv_bytes = encrypted_text_bytes[16:32]
            signature = encrypted_text_bytes[-256:]  # Assuming the signature length is 256 bytes
            ciphertext_bytes = encrypted_text_bytes[32:-256]

            # Verify the digital signature
            public_key = serialization.load_pem_public_key(public_key.encode(), backend=default_backend())
            public_key.verify(
                signature,
                ciphertext_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            kdf = PBKDF2HMAC(
                algorithm=hashlib.sha1(),
                iterations=50,
                salt=salt_bytes,
                length=16,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv_bytes), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_text_bytes = decryptor.update(ciphertext_bytes) + decryptor.finalize()

            return decrypted_text_bytes.decode('utf-8')
        except Exception as e:
            return "ER001" + str(e)



if __name__ == "__main__":
    password='alwebuser'
    encrypted_text = json.dumps({
            "body": {"loginRequest": {"requestBody": {
                "userName": "alwebuser",
                "password": "alwebuser"
            }}
            }})
    encrypt_password="""MIIEKTCCAxGgAwIBAgIUJ3mBbkc/gaDa7NAUg61EocxPxmowDQYJKoZIhvcNAQEL
BQAwgaMxCzAJBgNVBAYTAklOMRQwEgYDVQQIDAtNYWhhcmFzaHRyYTEPMA0GA1UE
BwwGTXVtYmFpMRIwEAYDVQQKDAlBeGlzIEJhbmsxETAPBgNVBAsMCEFQSSBUZWFt
MR0wGwYDVQQDDBRVQVQgUm9vdCBDZXJ0aWZpY2F0ZTEnMCUGCSqGSIb3DQEJARYY
YXBpLmNvbm5lY3RAYXhpc2JhbmsuY29tMB4XDTIyMDgxODE2MTM1MFoXDTMyMDgx
NTE2MTM1MFowgaMxCzAJBgNVBAYTAklOMRQwEgYDVQQIDAtNYWhhcmFzaHRyYTEP
MA0GA1UEBwwGTXVtYmFpMRIwEAYDVQQKDAlBeGlzIEJhbmsxETAPBgNVBAsMCEFQ
SSBUZWFtMR0wGwYDVQQDDBRVQVQgUm9vdCBDZXJ0aWZpY2F0ZTEnMCUGCSqGSIb3
DQEJARYYYXBpLmNvbm5lY3RAYXhpc2JhbmsuY29tMIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAv+wyqLkgGBaL/geLmj2nzMLwOsAW4uHISyucC9QP9KZk
CtfZPXjUVrclIEGwcQ3p2ECyHyvWHj0SVui0Xrqnj6I3QKYf8bOK5ljb9gOS/u6a
taTCBez/uoMbTEIad0Mq8Oa4c5hP9x20ZLiW5VyN2MbHMG+WuNSEWsjz6nOWNhr0
rwnZ1N+3BjqpG4KanGx4pYtVHdCyBfppxG2TOVstYXuub9Qfl4QjqTJA2qHaOeA0
MRMpghMhZfep7C/zQA1H/XggDaqUYcMtcgv3kGd1LiaajFpD6KfxNQKzSypgyimi
WAr3YOMOfEkTWJBMu6OEEK8YcKKA0cmPxtVCXAhXNQIDAQABo1MwUTAdBgNVHQ4E
FgQUYtWzyHOuNIF/AQw/YHw0dblSAAIwHwYDVR0jBBgwFoAUYtWzyHOuNIF/AQw/
YHw0dblSAAIwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAcKlT
ocyOIf2GVNtRBmVoKLKxQwhRZnLOvjzM0e8VYSIPblo0/8gYci5+WBcL0puz3lqP
En6XVjdLb5XXbPILaFQmIGCwF50kEAZfzhRk8pq+LPA4wDhPRrOmxq62GVgh5xJy
Zp2AUc2Z6Q1Jj/jn9LBN7thkvAuBO5Pa1z6/qs4Eb0uIkU/qstwhI9X06Kz+j80T
0zrlYX4VkqZII3NOVsHbQkaUUA5S16HTpzVN1xilum/vgq1R/R1mSn+KeHYATI99
uKE9SyQvxYresgEC88MonExhihuQ3Eid/DsFIDZOAHQPpkxvTN4ZeYG2y+/lQDQC
DIt8cG/WxJc9F0l1Fg==""".replace(" ","")

    decrypt_password="""MIIDzzCCArcCAQEwDQYJKoZIhvcNAQELBQAwgasxCzAJBgNVBAYTAklOMRQwEgYD
VQQIDAtNYWhhcmFzaHRyYTEPMA0GA1UEBwwGTXVtYmFpMRIwEAYDVQQKDAlBeGlz
IEJhbmsxETAPBgNVBAsMCEFQSSBUZWFtMSUwIwYDVQQDDBxVQVQgSW50ZXJtZWRp
YXRlIENlcnRpZmljYXRlMScwJQYJKoZIhvcNAQkBFhhhcGkuY29ubmVjdEBheGlz
YmFuay5jb20wHhcNMjQwMTMxMDkzNzMwWhcNMjUwMTMwMDkzNzMwWjCBrjELMAkG
A1UEBhMCSU4xEjAQBgNVBAgMCUthcm5hdGFrYTESMBAGA1UEBwwJQmFuZ2Fsb3Jl
MScwJQYDVQQKDB5SYWRpYW4gRmluc2VydiBQcml2YXRlIExpbWl0ZWQxDTALBgNV
BAsMBE5CRkMxEzARBgNVBAMMCkRFVl9TRVJWRVIxKjAoBgkqhkiG9w0BCQEWG2Rl
dmVsb3BlckByYWRpYW5maW5zZXJ2LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBALM9GjcC2r/aJfJ2VHnO5mwqsjRNxeRUkX3J+n6n/dAKVIrVj2uR
4DyGAmhdV/7bYVWseV6xgLkpgiZ9IbKfqYcLsUghiXJOWQimt7jvAarAYMS/C1oW
YkOHmZKpdORs8eKvC65EUtG5xp+yJ5wPYVJo8MUJ4SH5SSxPzoLHUqzlgUy1gl9c
K1zJ96Xx80qdUqhjzyCqjWAOnOd8yLV4hRwao4AeRMPnS6tljrg7X8nbqoubY7PE
7EQB3Vob1BcCufHzLPgl6beej/4dlAN/3t6gMxw6jcJRUI/I8H/51V4KJ/rkpAoC
WMsEBnQFwWwtxCBWL4Nb6c6iaOtsrG6vaycCAwEAATANBgkqhkiG9w0BAQsFAAOC
AQEAD+PG2Q20I5dWSsN0Kw2rvuIJZ/uWkCrfxoWk2AJhtnzof/rmc8TFLLIGH+I0
i4l+s7s8BXt/l8rqo+vtuwd7a+oQMgtzVh9Vc9rsWZDsljnr8N6b0WHTI4XSEEmO
krFP0DkvLxhlV5/a1eVzfuxvQIZxuO5FF/zFuzkfOU18tGKlRcrlf6GiUBpNfNm4
W/C16VPF0zOREPoSvnPwfgKurVLLtAsSWUS2TVQr58Z1PeyQ/M9HJy8hxuy6Tzy8
rcxsXD73Xje7Cq9Dj3AteA3IuQ8dPYLXeLUYZRYDRaxyPVAWqLSTDMEhgJvTDeGf
yktFxVxKSqXG6CT5ELiOetA4Vw==""".replace(" ","")
    encrypted_text = AES128.encrypt(encrypted_text, password, private_key=encrypt_password)
    print("Encrypted Text:", encrypted_text)
    print("Decrypted Text:", AES128.decrypt(encrypted_text, password, public_key=decrypt_password))
