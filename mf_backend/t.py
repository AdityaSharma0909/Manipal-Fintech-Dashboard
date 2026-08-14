# # import numpy_financial as npf
# # from decimal import Decimal


# # emi_amount=npf.pmt(
# #     Decimal(11.88) / 12,
# #     3,
# #     Decimal(123.34),
# # )

# # print(emi_amount)


# # from time import time

# # a = time()
# # a = str(a).replace('.','')
# # print(int(a))

# import requests
# import jks, textwrap, base64

# # keystore = jks.KeyStore.load('/home/kp/workspace/radian/radian-los-backend/radianfinserv_uat.jks', 'radian')

# # print(keystore.private_keys)
# # print(keystore.certs)
# # print(keystore.secret_keys)



# # def print_pem(der_bytes, type):
# #     print("-----BEGIN %s-----" % type)
# #     print("\r\n".join(textwrap.wrap(base64.b64encode(der_bytes).decode('ascii'), 64)))
# #     print("-----END %s-----" % type)

# # for alias, pk in keystore.private_keys.items():
# #     print("Private key: %s" % pk.alias)
# #     if pk.algorithm_oid == jks.util.RSA_ENCRYPTION_OID:
# #         print_pem(pk.pkey, "RSA PRIVATE KEY")
# #     else:
# #         print_pem(pk.pkey_pkcs8, "PRIVATE KEY")

# #     for c in pk.cert_chain:
# #         print_pem(c[1], "CERTIFICATE")
# #     print()

# url = "https://uatgateway.federalbank.co.in/fedbnk/uat/pan/validation"

# payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:in=\"in.co.federalbank\">\n<soapenv:Header/>\n<soapenv:Body>\n<in:PANRequest>\n<ChannelID>CHNLTEST</ChannelID>\n<AccessId>TestUser</AccessId>\n<AccessCode>Fed#uat</AccessCode>\n<RequestID>TST7830001</RequestID>\n<PAN1>DEJPP3574N</PAN1>\n<PAN2>MOYHI5479N</PAN2>\n<PAN3>AAACC2093E</PAN3>\n<PAN4>BIOPC7152A</PAN4>\n<PAN5></PAN5>\n</in:PANRequest>\n</soapenv:Body>\n</soapenv:Envelope>"
# headers = {
#   'x-ibm-client-id': 'c3337c76-9b2e-46f7-8afa-7f98e8a692ad',
#   'x-ibm-client-secret': 'oT5aU2wJ8gN2uD8aP8yR3uO5tL5yV7kF5dW4oE7hF7uW2oO1nV',
#   'Content-Type': 'application/xml',
# #   'Authorization': 'Bearer nhAdNz80nXRKgW3lf39pvoj7GPV6sJ'
# }


# # certFile = "/home/kp/workspace/radian/radian-los-backend/radianfinserv_uat.jks"
# certFile = "radianfinserv_uat.pem"

# response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)

# print(response.text)

# # keytool -export -alias radian -file radianfinserv.der -keystore radianfinserv_uat.jks

# # openssl x509 -inform der -in radianfinserv.der -out radianfinserv.pem


# # openssl x509 -in radianfinserv.pem -text

# import base64

# message = base64.b64encode( '20221086'.encode('utf-8') )

# print(message)
