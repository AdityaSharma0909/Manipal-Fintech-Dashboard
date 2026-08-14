"""
# To run this
sudo docker exec -it radian_app  bash
python3 manage.py shell
exec(open('payment/tests/qr_code_decode_test.py').read())
"""


import json
from payment.utils.cipherkey_utils import CipherpayHelper

with open('./payment/tests/qr_encoded_resp.json', 'r') as f:
    data = json.load(f)

# print(data)
    
cipherpay_utils = CipherpayHelper()
iv=b'03657d42f5423c2e'
aes_key = cipherpay_utils.generate_aes_key(salt=iv, passphrase=cipherpay_utils.secret)
decrypted_data = cipherpay_utils.decrypt_body(iv=iv,encrypted_data=data["returnData"], key = aes_key)

with open('./payment/tests/qr_decode_output.json', 'w') as f:
    f.write(decrypted_data)
    # data = json.load(f)

print(decrypted_data)
    

"""
>>> exec(open('payment/tests/qr_code_raw_test.py').read())
auth_header:  VcODgkry7DVDaCBvoj0VNhYgEHIWkSFw4XXy/TGLs4/4USNpCqHVkAltn8ua2BJNvMSHWzh/Scjo+q/53puf5aarD2V7s64UtHZp2bDHJ3N8zWjgoaACPJd8JBd8bWg+kS17j1R80ued2cv4mp7zvr1KMfWasUv6ZFbV8dDT4Qyy0JdWxBrrAGeCeTNOub4fZ7ELnaQ3LqjzosH83nX2WgJgvPRA//UTlpo11Rx2iskHEzJ8tJKDdhExznUZtSQODg1yZSENO4Qy6nhpYD/t3xOLVKVx/bwCTFOrsXd1eoOyHHTeXzV8/MsoTqepssnbISKgrTlUkMKR+8mTuPz29A== 

Salt:  b'ccb644a790713d86' 

aes_key:  KdmdiR5tlbLwghTj8AdWEQ== 

key_header:  o0B60vhB2ANml6qcxvbvRRVpwQX02VknTOsUYa0IVctGCWAI8if1jg0tdXkGQcaTSM6Xq7XA0ETYR5tFZhsRE4zrFXiVpCp3yaPsq89UKJV8DaFvUzywGYKzmW9Han1c/jlG60nAtpZChn0dyZRUhinlwvQCd2dlLUUy4DxVM39uJ3Gh+Z+uvZTZJRkP/iLdZxZHPFSl0cE2U2UemneCvX3O3d7OHPSK1rhqCEsJfYf1eZA4PGMDbNIyh63BAtHKHwjhufMz15BWS2NgwnJfLuwAtb8PohrIaD4TICUVNt5mdC+2nvpvO1YkRf+VmQg47CKfRbi9IM+e8NnM2XFnTQ== 

jwt payload {'timestamp': '2024-02-05 13:20:30', 'partnerId': '20221086', 'reqId': '1270001SLHM883202_1707119430035'}
jwt_token::  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOiIyMDI0LTAyLTA1IDEzOjIwOjMwIiwicGFydG5lcklkIjoiMjAyMjEwODYiLCJyZXFJZCI6IjEyNzAwMDFTTEhNODgzMjAyXzE3MDcxMTk0MzAwMzUifQ.51dILKphHXWl8zOI0DS4Ylqs0KLTzQkFE7LK-THtddw 

auth_header::  VcODgkry7DVDaCBvoj0VNhYgEHIWkSFw4XXy/TGLs4/4USNpCqHVkAltn8ua2BJNvMSHWzh/Scjo+q/53puf5aarD2V7s64UtHZp2bDHJ3N8zWjgoaACPJd8JBd8bWg+kS17j1R80ued2cv4mp7zvr1KMfWasUv6ZFbV8dDT4Qyy0JdWxBrrAGeCeTNOub4fZ7ELnaQ3LqjzosH83nX2WgJgvPRA//UTlpo11Rx2iskHEzJ8tJKDdhExznUZtSQODg1yZSENO4Qy6nhpYD/t3xOLVKVx/bwCTFOrsXd1eoOyHHTeXzV8/MsoTqepssnbISKgrTlUkMKR+8mTuPz29A== 

key_header::  o0B60vhB2ANml6qcxvbvRRVpwQX02VknTOsUYa0IVctGCWAI8if1jg0tdXkGQcaTSM6Xq7XA0ETYR5tFZhsRE4zrFXiVpCp3yaPsq89UKJV8DaFvUzywGYKzmW9Han1c/jlG60nAtpZChn0dyZRUhinlwvQCd2dlLUUy4DxVM39uJ3Gh+Z+uvZTZJRkP/iLdZxZHPFSl0cE2U2UemneCvX3O3d7OHPSK1rhqCEsJfYf1eZA4PGMDbNIyh63BAtHKHwjhufMz15BWS2NgwnJfLuwAtb8PohrIaD4TICUVNt5mdC+2nvpvO1YkRf+VmQg47CKfRbi9IM+e8NnM2XFnTQ== 

{'Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aW1lc3RhbXAiOiIyMDI0LTAyLTA1IDEzOjIwOjMwIiwicGFydG5lcklkIjoiMjAyMjEwODYiLCJyZXFJZCI6IjEyNzAwMDFTTEhNODgzMjAyXzE3MDcxMTk0MzAwMzUifQ.51dILKphHXWl8zOI0DS4Ylqs0KLTzQkFE7LK-THtddw', 'Content-Type': 'application/json', 'User-Agent': 'APIAGENT/7.29.2', 'Key': 'o0B60vhB2ANml6qcxvbvRRVpwQX02VknTOsUYa0IVctGCWAI8if1jg0tdXkGQcaTSM6Xq7XA0ETYR5tFZhsRE4zrFXiVpCp3yaPsq89UKJV8DaFvUzywGYKzmW9Han1c/jlG60nAtpZChn0dyZRUhinlwvQCd2dlLUUy4DxVM39uJ3Gh+Z+uvZTZJRkP/iLdZxZHPFSl0cE2U2UemneCvX3O3d7OHPSK1rhqCEsJfYf1eZA4PGMDbNIyh63BAtHKHwjhufMz15BWS2NgwnJfLuwAtb8PohrIaD4TICUVNt5mdC+2nvpvO1YkRf+VmQg47CKfRbi9IM+e8NnM2XFnTQ==', 'Auth': 'VcODgkry7DVDaCBvoj0VNhYgEHIWkSFw4XXy/TGLs4/4USNpCqHVkAltn8ua2BJNvMSHWzh/Scjo+q/53puf5aarD2V7s64UtHZp2bDHJ3N8zWjgoaACPJd8JBd8bWg+kS17j1R80ued2cv4mp7zvr1KMfWasUv6ZFbV8dDT4Qyy0JdWxBrrAGeCeTNOub4fZ7ELnaQ3LqjzosH83nX2WgJgvPRA//UTlpo11Rx2iskHEzJ8tJKDdhExznUZtSQODg1yZSENO4Qy6nhpYD/t3xOLVKVx/bwCTFOrsXd1eoOyHHTeXzV8/MsoTqepssnbISKgrTlUkMKR+8mTuPz29A=='}

key
KdmdiR5tlbLwghTj8AdWEQ==

encPayload:  AVlQPgmJ7xDC4BhwpZTWTjmqlJcRYiyc6KTXHx7ffaxTCgH5w9jxSUVHZtcmhZCES5GC8ShgwJ70hUpxXGEjMGU/2+Hgf7jquFSoQQVwwJVbOhC1i7zmXk9HLkhsoQsLHAreIJ/Yz07glfwTam02z9QnCPU0Waw7ry9J3XQ5QJuDdQr97rcyqZrAmCvgHgdWCuRrHnNXzGLg9kqHVP7D5w== 



"""