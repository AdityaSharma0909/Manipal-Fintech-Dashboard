# import http.client
# import json
# import ssl
 
# # Defining certificate related stuff and host of endpoint
# certificate_file = 'radianfinserv.pem'
# certificate_secret= 'radian'
# host = 'uatgateway.federalbank.co.in'
 
# # Defining parts of the HTTP request
# request_url='/fedbnk/uat/pan/validation'
# request_headers = {
#     'Content-Type': 'application/xml'
# }
# payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:in=\"in.co.federalbank\">\n<soapenv:Header/>\n<soapenv:Body>\n<in:PANRequest>\n<ChannelID>CHNLTEST</ChannelID>\n<AccessId>TestUser</AccessId>\n<AccessCode>Fed#uat</AccessCode>\n<RequestID>TST7830001</RequestID>\n<PAN1>AAAPA0039K</PAN1>\n<PAN2>MOYHI5479N</PAN2>\n<PAN3>AAACC2093E</PAN3>\n<PAN4>BIOPC7152A</PAN4>\n<PAN5></PAN5>\n</in:PANRequest>\n</soapenv:Body>\n</soapenv:Envelope>"

# # request_body_dict={
# #     'Temperature': 38,
# #     'Humidity': 80
# # }
 
# # Define the client certificate settings for https connection
# context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
# context.load_cert_chain(certfile=certificate_file,)
 
# # Create a connection to submit HTTP requests
# connection = http.client.HTTPSConnection(host, port=443, context=context)
 
# # Use connection to submit a HTTP POST request
# connection.request(method="POST", url=request_url, headers=request_headers, body=payload)
 
# # Print the HTTP response from the IOT service endpoint
# response = connection.getresponse()
# print(response.status, response.reason)
# data = response.read()
# print(data)