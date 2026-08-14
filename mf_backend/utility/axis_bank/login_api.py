import json
import os

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

#from cryptography.hazmat.primitives.serialization import load_pem_x509_certificate


# Your X.509 certificate
certificate_pem = """
-----BEGIN CERTIFICATE-----
MIIERzCCAy+gAwIBAgIIRkJL3X2j2skwDQYJKoZIhvcNAQELBQAwcTELMAkGA1UE
BhMCSU4xCzAJBgNVBAgMAk1IMQ8wDQYDVQQHDAZNdW5iYWkxDTALBgNVBAoMBEF4
aXMxEjAQBgNVBAsMCUF4aXMgQmFuazEhMB8GA1UEAwwYcmd3Lmp3ZWp3cy51YXQu
YXhpc2IuY29tMB4XDTIzMDEwMzA1MzM0MloXDTI4MDEwMjA1MzM0MlowcTELMAkG
A1UEBhMCSU4xCzAJBgNVBAgMAk1IMQ8wDQYDVQQHDAZNdW5iYWkxDTALBgNVBAoM
BEF4aXMxEjAQBgNVBAsMCUF4aXMgQmFuazEhMB8GA1UEAwwYcmd3Lmp3ZWp3cy51
YXQuYXhpc2IuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsnQp
Zr0a8kkIriT+rwwpAJ89IidiLfnII4/wW8gqgTXiijDkBCKuL1Unbw5Tu4c/KRPF
c7exhelePG+jPZtSTo5Kqy2IlosP4MOi4LFLNV4l8102nipumJ0KUAjnkGsalY2o
mIuae2uq6PI4gHhezCS0Q742qIbKI52tPw9ZTxeF8csPLn1dZPooJeK/3gWA3JS1
YTvqx1xANAKyy6eaXsrIBPZar/pypwNmfpbLk+smVxLem5gyG2Jmi56SOhQFXAVW
1NBbgeIEPsYlbghIFrzBXwzS8Hwcl2YMDl0UJsSzquAOcFhuDh6ZKqki6tgFN+KC
czeBCPDKsBVZtGdJVQIDAQABo4HiMIHfMAwGA1UdEwQFMAMBAf8wHQYDVR0OBBYE
FFAH79oC8dZ3Csggp0RdAL0QsLQJMIGiBgNVHSMEgZowgZeAFFAH79oC8dZ3Csgg
p0RdAL0QsLQJoXWkczBxMQswCQYDVQQGEwJJTjELMAkGA1UECAwCTUgxDzANBgNV
BAcMBk11bmJhaTENMAsGA1UECgwEQXhpczESMBAGA1UECwwJQXhpcyBCYW5rMSEw
HwYDVQQDDBhyZ3cuandlandzLnVhdC5heGlzYi5jb22CCEZCS919o9rJMAsGA1Ud
DwQEAwICvDANBgkqhkiG9w0BAQsFAAOCAQEALxNfMn7gVCJQgNxJ2iwXnw41ZM8B
Zf/iwIKrMkeFZcnqnxSwTpGxKAaRy3ExkyGBVmJQuGIEIjCGJfqp2SUNcr1UsFuy
5kljiePR2TtjTZa4WwQ7RYFP9tk6u+0r7aVLk/jzfDx+ZHYjNjvy6TpFkMJB0fAS
wboRHxlv0TDpO66E0cEpJpfrkI7MEZSf6DTam+qn4OFUiqspG2ooclf9l9hIg4Qe
RJegWhPJvcqSpAnasLyhHLpTfgZFetVDNwwCYqu4XEb2fyySOy/WgGcz7fOU4mO1
HxQ84TURjWhCbEmiAVHGY3y5Mc1tKgEupSvUGSSO2SlL9EXngunkv4cLTw==
-----END CERTIFICATE-----
"""

# Assuming you have the private key in PEM format
private_key_pem ="""
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,C513F1C9D2E67352E709BDA751F184C6

9CvCPfF5B3+V+jNcQA3627smkUh5kopdh3YjfpkWLYsQq7CnEZgQZPqb1Koy55+M
arOD5L0ydnGb6UpV/HvQMiuI/3oFMsq0HNUn5pdhcaokcYNCAMStIuoahTG+EH5p
SDa/3dqMJY5TagiXvKgIYtDJC4e6Hawzu2zold6HKO+8vi4782sSci+b62LlE2Lw
fvcgVvj41qN0l+GB7ymS0mE1BKGdeMPCdkFNuD+vSJ7QqHy3nqMFnTN21RfoGUrQ
lyhLVegEuMjE5O26kqTjaYTszNX0zRM1BRkRX3iGO0E+sADXcIZq053iIPTaCh0y
sgG3+hp3RyQ6S1/bFNc7aQZ+9aoxC/8hPbFXLFZGpRBlTCNT0L5BPHA11y8AKbiW
WoYlfkiXqe/YtKmEZQ/H0po3R6D3IFPK7Mz/ZknHvMuvQOQPjAfEAgVUuSxsF+tp
anZ31klhGvYBDYkb7l1uKp1gsdJ2yhq3XK44uk8QMFpSbTW0j5ZNt0Ayfcqicm1/
1W1kYAokVklEarUXGnzNFHq8n2wgLklN3mE7daVdqjxrIP/kQggiqNkWeka5eNwI
Jy07b5uL0pPyN2Ai3lIDcvDPCEjQMYVmvwVx+rAx6fD/BtliwRqiSUgzEGQaI/Sp
Ns7w4XP23pWMhRESUEY2kxsvbu/rYwACw5FdG7yXebpK7TvfXsdOmikW+/5QEhaN
hDzsXTwn1ly25XBtaAJzm3BDYCOPikyx7l3Qx4IUqX2i8AsSbGGmoajfFpmvxZdA
JiF7p70yTTZeopONk9B35slZh/YrpBkJ8cmDKCyiFflDrqflnDwK8IdmCZHb+Zg/
aJX4LLSX4WDGf8FJoJIIGQC8/zG3kIO1WAWJw0R3vSD1V4syG8Q5oEel5IJffZvb
8ztUYUouzYGR1vMQrw5dztIXdd/AEWEfhjV2NHa/2JNAHx8yfg+nlDXKE3zz+PwC
73TNJijYMJMbZ48NcxZFSv/cOsrzat45epdR8DCTU23KKc7721nYdAz4vw+uI0hV
ZSQy4B2HCU4VjlcD0yDi0dsErU/kaIS69hXDfk0t0JNM5RRnsb+ZPA8YNygQLIVZ
3T1KEVljK3YYdDJ5cre1FNkabwDrOhsA5RV4qDdLOZAVu7qX+utDp6ciphNEDqZ8
N+/bmu86d+g9ePNhyTRLEglptkTVA/CHD0uGy2UxiDoQFZ+SZUbNJmGjwQkSFFTv
0Wpkzw2vSwIr+6AXqHKqbvsrIeTpaPQDeI0WMNYypYQY2bfiQ2SpZ1oJRyVVWDRP
Qfb9zSxjuZkf9akjLXE6kjJK+8MwMUJNnJ18tJirEOS2PbPj9Yztl7CjFaS0Xf0f
XqvqFw9+ctAqgsz0aoEkF0CBTN75cNP8E6t5GkD4sV1bHZSfooYf0j9Dl+ljelF7
bIB5eSwN1ZlQVLqCWqSSYWK8GI0REj+YswZeo35PzjvxOZuSA9TdeWpP4a4nDUL8
1RUUTjFyP0lVWjXVmDhoIvghTyCSUDMAerbMGbC/7kykT0ZKjrFLeOefeXvsWlMG
74TfBNm2I5mny3SQVtKVhkhMod22RVOdSSrEBB0FHwSvHz9ZZlXBDgfgQsPM04Cc
-----END RSA PRIVATE KEY-----

"""

def create_jwe_token(content_key, plaintext_data, signature):
    # Create a random IV (Initialization Vector) for content encryption (96 bits)
    iv = os.urandom(12)

    # Serialize the JWE header
    jwe_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM"
    }
    serialized_header = json.dumps(jwe_header).encode()

    # Encrypt the content using A256GCM
    aesgcm = AESGCM(content_key)
    ciphertext = aesgcm.encrypt(iv, plaintext_data, serialized_header)

    # Create the JWE token by concatenating components
    jwe_token = serialized_header + b"." + iv + b"." + ciphertext + b"." + signature

    return jwe_token

if __name__=='__main__':
    # Your API endpoint
    api_url = "https://api.example.com/resource"

    # Generate a random content key for content encryption (256 bits)
    content_key = os.urandom(32)
    # Load the X.509 certificate
    certificate = load_pem_x509_certificate(certificate_pem.encode(), default_backend())

    # Extract the public key
    public_key = certificate.public_key()

    # Serialize the public key to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    print(public_key_pem)
    # Load public key for encryption
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )

    # Encrypt content key with RSA-OAEP-256
    encrypted_content_key = public_key.encrypt(
        content_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Your request data
    request_data = {
        "key": str(encrypted_content_key),
        "data": "Your plain text data here"
    }

    # Serialize the request data as JSON
    request_json = json.dumps(request_data)

    # Your private key for signing
    private_key = load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )

    # Sign the request data using RS256
    signature = private_key.sign(
        request_json.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Create the JWE token with A256GCM content encryption and RS256 signing
    jwe_token = create_jwe_token(
        content_key,
        request_json.encode(),
        signature
    )

    # Send the encrypted token as the request body
    #response = requests.post(api_url, data=jwe_token)

    # Handle the response as needed
    print(jwe_token)
