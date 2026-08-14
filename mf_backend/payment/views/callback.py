from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from utils.envSetup import environment
from utility.response_handler import HttpResponse
from utility.error_handler import HttpErrors
from payment.utils.cipherkey_utils import CipherpayHelper
from loan.models import Loan
from payment.models import Repayment

import traceback
import logging
import base64

from payment.models import BharatSwasthyaRepayment
from utils.constants import APPLICATION_STATUS
import hashlib

logger = logging.getLogger("radian")


class IMoneyPayCallback(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        try:
            data = request.data
            received_hash = data.pop("HASH")

            if not received_hash:
                return HttpErrors.BadRequest("HASH is missing!")

            sorted_data = sorted([f"{key}={value}" for key, value in data.items()])
            hash_string = "~".join(sorted_data) + environment.IMONEY_SECRET_KEY
            generated_hash = hashlib.sha256(hash_string.encode()).hexdigest().upper()

            if generated_hash != received_hash:
                return HttpErrors.BadRequest("Invalid hash!")

            order_id = data.get("ORDER_ID")
            status = data.get("STATUS")

            if not order_id:
                return HttpErrors.BadRequest("ORDER_ID is missing!")

            repayment = BharatSwasthyaRepayment.objects.get(order_id=order_id)

            repayment.pg_txn_message = data.get("PG_TXN_MESSAGE")
            repayment.pg_ref_num = data.get("PG_REF_NUM")
            repayment.txn_id = data.get("TXN_ID")
            repayment.amount = data.get("AMOUNT")
            repayment.rrn = data.get("RRN")
            repayment.status = status

            repayment.save()

            if status.lower() in ['captured', 'approved', 'success']:
                repayment.application.status = APPLICATION_STATUS.IMONEY_PAYMENT_SUCCESSFUL.value

            else:
                repayment.application.status = APPLICATION_STATUS.IMONEY_PAYMENT_FAILED.value

            repayment.application.save()

            return HttpResponse().response(code=200, data={"message": "Payment updated successfully!"})

        except Exception as e:
            logger.exception(f"Exception occurred in IMoneyPayCallback: {str(e)}")
            traceback.print_exc()

            return HttpErrors.InternalServerError(str(e))


class CipherpayUPICallback(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        rawRequestData = request.data.get("requestData", None)
        rawKeyHeader = request.META.get("HTTP_KEY", None)
        print("POST upi/callback/ - CipherPay callback\n\n")
        # print("Headers: ", request.META, "\n\n")
        # regex = re.compile('^HTTP_')
        # headers = dict((regex.sub('', header), value) for (header, value)
        #     in request.META.items() if header.startswith('HTTP_'))
        # print("HTTP Headers: ", headers, "\n\n")

        print("Raw RequestData: ", rawRequestData, "\n\n")
        print("Raw Key Header: ", rawKeyHeader, "\n\n")

        try:
            requestData = base64.b64decode(rawRequestData)
            keyHeader = base64.b64decode(rawKeyHeader)
            cipherpay_utils = CipherpayHelper()
            decrypted_data = cipherpay_utils.decrypt_rsa(
                encrypted_data=requestData, key=keyHeader
            )

            print("decrypted_data: ", decrypted_data)
            repaymentObj = Repayment.objects.get(reference_id=decrypted_data["param"]["refid"])
            repaymentObj.payment_status = repaymentObj.get_payment_status(decrypted_data["param"]["status"])
            repaymentObj.utr_no = decrypted_data["param"]["utr"]
            repaymentObj.save()

            return HttpResponse().response(code=204, data={})

        except Loan.DoesNotExist as e:
            logger.error("Error " + str(e))
            response = HttpErrors.BadRequest(str(e))
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception("Exception " + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response


"""
# Callback logs:
        
POST upi/callback/ - CipherPay callback


RequestData:  bu3GXBXJnta3bdIT+hU7REcHYME/aVVOQeQElCZV4P6IcF8xr/BCnmJNNtfQ4jaqKGh0exWlsEttJ8M8UwcNImsOr7SHjclzsyoAejudxDPZcFV0JnSsShH999+te+nHFeJHSOi5+IK4LAnYc1TF6QSfA8KRdEZukiKwVEZwPMzHIWecCPWgZFa7G8O4RvVsfypOTfLWpTR06EZFs4mGeJrH8pvptIBltQVFznnheJqH2/jUMT+5Az9fDJXoDmkMn9EonFGuD4rpWmqPwJT5tXmUB6pecgj16E5KoBpv4fjyi2QgzXVzEniXCgeXGWAnqbaFIK3bvt3j3j3fVwhq6McBzBxsmK3W5IYUuRfZsAwpam6iaPY941Sg+KQHJn4nQYpw6ieDaCUQqLzf1Vu2vcrDsasbZEJadZaWsJmOxM098xJvkNY+PO0pR03nuKM5o98HTlV0JPWEd3AwfCt+Pkhs19nfTEUWCwwx+e+OTsvFVjC5HWvdD1jxnmLJFYxUfqYz5BujFspHf37I9SRkZ9SJGJ4/vp6WUd7w6Cq7HL4tcdxGNmRTBQiivnO10MCKcXK4xSPE4ZiTK8Xpno8cna7DrgIDvEXWBvAIxGQM5Rbmez9Xk4GGuLM9tu6arDOrKhz0Y+oXgp8ZnNXNWRCkjxsd0LObvsl5RMgXuZQB+5kDJIF6TgwCH5oSnz8CHHmbRoWOJ/mAHWuW8IqnGCWdCm3HTszPypjWi4ky0JsTRiKPWE5ifVpM47g867JsZ4wf/uNvesAIRL8Ir8VuIbrX/hPksyBCI3RNFh9MYUpY35qAmslS7t3uPhNh7pXZLGPSa/urvc79Xzv3P2bCg8LkYocn4vqmEd0vqyFR/6L3jqHyj/hdWScpHDQfDYhE/AqHayu5YXfiNYGKGhbgasLwLqxqiH5zzkUkXOfm4uyEWeGbKt5z1RN/8bwUiubntK/lKQNumNQvFnckWXWnku9THKZiHTYk4RALLQKk3cA6jHOy4qPRaA8MZIoNaIdqyi9U/6JRH3l8dkNna5lhv/xBD4zTwk8JK+aksXcsfMSeasTz6gtOuNjTDKbAZ58+rvYi0imbPq+NOV2kimFKbxVFyQ== 


Headers:  {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7f9817aaf160>, 'wsgi.version': (1, 0), 'wsgi.multithread': True, 'wsgi.multiprocess': True, 'wsgi.run_once': False, 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>, 'wsgi.input_terminated': True, 'SERVER_SOFTWARE': 'gunicorn/20.1.0', 'wsgi.input': <gunicorn.http.body.Body object at 0x7f9817aaf040>, 'gunicorn.socket': <gevent._socket3.socket at 0x7f981b6c7c40 object, fd=8, family=2, type=1, proto=6>, 'REQUEST_METHOD': 'POST', 'QUERY_STRING': '', 'RAW_URI': '/payment/upi/callback/', 'SERVER_PROTOCOL': 'HTTP/1.0', 'HTTP_HOST': 'localhost:8000', 'HTTP_CONNECTION': 'close', 'CONTENT_LENGTH': '1130', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'deflate, gzip, br', 'CONTENT_TYPE': 'application/json', 'HTTP_KEY': 'pa6Dhqpo+xvEnDqBF9TUnxRpMijg2FAXUM3bt4cpcl9dna/+983NK0rchnYKMsjy/SAYDc4MM7dbrG9W/vx39VBfgXpbjZf2NiLsx8RNKotMj2MTfXjVl/jNNZDatb6Q4LvmBxqlFKJ268XRKNw/Hrf8GGqrdYeWpU0Zj3090oRb2tHzQs/J9FLdpIiJd2Q0foDE2jhKMJGcqhP+kL03zv0yJaPYS5cNzGuMGf/Mk7Qbn5paJSfN4DWP6DI5QgPkQ/1eMsActo45UDLPhEFcHw2fkymoe/nWLPpVD/KAESxGagc2zXz6nOMq+WFeL4CEIEa+LV9dc1sq0D6W4ykzeQ==', 'wsgi.url_scheme': 'http', 'REMOTE_ADDR': '172.19.0.1', 'REMOTE_PORT': '62764', 'SERVER_NAME': '0.0.0.0', 'SERVER_PORT': '8000', 'PATH_INFO': '/payment/upi/callback/', 'SCRIPT_NAME': ''} 


HTTP Headers:  {'HOST': 'localhost:8000', 'CONNECTION': 'close', 'ACCEPT': '*/*', 'ACCEPT_ENCODING': 'deflate, gzip, br', 'KEY': 'pa6Dhqpo+xvEnDqBF9TUnxRpMijg2FAXUM3bt4cpcl9dna/+983NK0rchnYKMsjy/SAYDc4MM7dbrG9W/vx39VBfgXpbjZf2NiLsx8RNKotMj2MTfXjVl/jNNZDatb6Q4LvmBxqlFKJ268XRKNw/Hrf8GGqrdYeWpU0Zj3090oRb2tHzQs/J9FLdpIiJd2Q0foDE2jhKMJGcqhP+kL03zv0yJaPYS5cNzGuMGf/Mk7Qbn5paJSfN4DWP6DI5QgPkQ/1eMsActo45UDLPhEFcHw2fkymoe/nWLPpVD/KAESxGagc2zXz6nOMq+WFeL4CEIEa+LV9dc1sq0D6W4ykzeQ=='} 


auth_header:  rhYdeark/viAhfADpz8e0ahsQ40bqrHiy23/4YBK6MId0rVmP1/lFPcwH6BXX2nFPvfO1fsL/Lcr59LQaYpqRIL53l1z9VEWof0iwnmkkzHGTZULQGQUeANnw4cIRubKF5iD29aijJqdjUqbajuWRjsF1lCWR1t4muwGAkH6CIpmwtvPB0a2FfkomGGZFvklhv8evX+MsYQ3yV9cJSn51owR4X5VTvwFc4PvsjeES4hJEEWCa7mMdMu4rckgl+ZevCVjnRiQLR35dcTLnq3alMRBI1n17NXicE547CtVLaB9ZdRx57Fh5/VZx/N2XsYoDyOTvto/zpcov4pWMcVZgQ== 

Salt:  b'f2d9488258dfce75' 

aes_key:  v0Tzh0obbZ/jnS4hLvPMnA== 

key_header:  f7bJS92gzQTXIB6ddG7Pv3vImpYwwMi0DkZlmQ6tucKUU+N7mbxppwAzQDL/g2F6U7i4n+J/MoiTUeMpKzLV3KSusSYEoizZDcjCOCzurfHZy9FF7ICkHwYLJpp/oGI6Dwni7h55vfYjKes7nlp+bXNDaqN3OPt7ivnEc402ct9rvg1kla02A2tps3AHf/en2rWWdkZKBZO3XDjOyIponqdM/7s7KlmlKAivQM98GU0fqnEzTyzd05pH70Xrv5k07k2XI/D9XdU67VL4SgaNC4iopudlh5ALqB3M57Ma4OjtnlxRpCaKkxtlymBsQA8QOmi5ds6rz2X2brgNGoulTw== 

Traceback (most recent call last):
  File "/app/payment/views/callback.py", line 37, in post
    decrypted_data = cipherpay_utils.decrypt_rsa(encrypted_data=requestData)
  File "/app/payment/utils/cipherkey_utils.py", line 294, in decrypt_rsa
    decrypted_data = private_key.decrypt(
TypeError: argument 'ciphertext': 'str' object cannot be converted to 'PyBytes'
Internal Server Error: /payment/upi/callback/




POST upi/callback/ - CipherPay callback


RequestData:  jcbr78g0lQ4RZ2PyyHmmgndcOSTTaiX51DtcLr+jKe+tDHV8NzXDyOzQjAbtyJ82hZruFg3/V0qpjKe0ULl9hFChuJSlImS8XpJBjan+gUJ1PNfOtNlhu9hEddqScQs3JFlrD1RVmvudcq6GtX8RPo4yHePTdHzBvHhGN7PU+rLwJgJ4poFbdS3Kwu7K9gvQwuEm5GbiCGwUJQKqGtiKos3T6z1pXpxeXU+Rb6DoAwhblfZXlS3uAH9UI/tw+e5oN9xHmSH+sXyVb8hcZguOlsXExOsy6gXh9eQ4yIhJFw7T3nMG5h6/HU8JMN2v8/Z8QxDdLRl701or9l8jaKlXafszTOTynxNZYCW3dSc1LSnTpusJleEFbU/1F57vGZCfftETFlQxDVHF+HhB4AMIWu5j0nHQyypjMKjA/0UhjqBUzaVZlcUFja+w67BVUCCCtCmhW2B5yreddY/zWQru6IuMs/NkBkfvDLlFTXT0hDBTpt3o9qlycbuVR0IcQTSxCGmuJ4EhP59YzoCBAyOVYVZxh+RTLo/wC5TdQZ1hixnXADDBysjzNsmYRQ/aNavGCwIFjRfudm4M/LWRzz1a50vik/JX26DUVVK5WaVms4rJNkoYaCH5LysMXyvouVasMhFZQFl8VqB7yjZBpbkTcjHHP1c1jDbP6AvybwYzSPnqI+oI9ftLVlq5e6u3J9dGqaCKpiU5p0UPzBM6wyjOcPMJDNEKPz2tMqkB5H0g3Phg99E9K/WHK2n0i8yiPk93s6AxMOHTMmmGgvPOlAAFDDQQLuzYpxvhkNdbJaWEqWr/vkqXUBa7cQ4s/Hzq4MYq09K3KMr/4q8gU9C102K4E6fXreHtifnd0EhALa0lqEooEBP8of7b0fONH+oWh6JQCFwR5OWMgA485KH36g6IgVu+Ev3FXgIJ3TEYYSuk4yQgEOX405p9HF4LdYbtlC5WQ4xcoSgRN7HAYz7nhLz+DNEJW9ai1iQe0KWGJ/RqLsYRAeO/MRfGVluE2d2lO1p0g1krKoslXlAJIjLspodB17YvdFKs2hbTTizjkA1nMoSf7ce33M3xTPKtOHEc3WpImr6xDP6LUzOTS+tZ4I3x8Q== 


Headers:  {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7f9817a439d0>, 'wsgi.version': (1, 0), 'wsgi.multithread': True, 'wsgi.multiprocess': True, 'wsgi.run_once': False, 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>, 'wsgi.input_terminated': True, 'SERVER_SOFTWARE': 'gunicorn/20.1.0', 'wsgi.input': <gunicorn.http.body.Body object at 0x7f9817aaf910>, 'gunicorn.socket': <gevent._socket3.socket at 0x7f9817a2a9a0 object, fd=8, family=2, type=1, proto=6>, 'REQUEST_METHOD': 'POST', 'QUERY_STRING': '', 'RAW_URI': '/payment/upi/callback/', 'SERVER_PROTOCOL': 'HTTP/1.0', 'HTTP_HOST': 'localhost:8000', 'HTTP_CONNECTION': 'close', 'CONTENT_LENGTH': '1130', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'deflate, gzip, br', 'CONTENT_TYPE': 'application/json', 'HTTP_KEY': 'vraLXzhHvgni+vEdeZJtoAlkI6miWvC2i78/tsaZrP12evp0UGT5dTv3Ej1i664gurgXpS51BR985oeDMsSWyWxL2rUJl3mhzZG4GkLdSlhskl5MYQb0sPUKPnvu/YXUKysoK2OyNHTM9AZtMZ92N4HAamvPkh/A0aosVcO92HwVy3IQHapMZH342XlBr96uW8qRQkEDTXiCxbDKI6FeryIqQf4CDfiwzfL9zE+aC/CaOm+lppqq/sYO09KqbC0KcdtW/gI/ns0NcwmHVa6qM0QnE9REW1hACJgDsxPdC4wpNHX93dg8uXKFhz9P1hDXMjJ2m+UYwKn1QANKeN+oDQ==', 'wsgi.url_scheme': 'http', 'REMOTE_ADDR': '172.19.0.1', 'REMOTE_PORT': '64710', 'SERVER_NAME': '0.0.0.0', 'SERVER_PORT': '8000', 'PATH_INFO': '/payment/upi/callback/', 'SCRIPT_NAME': ''} 


HTTP Headers:  {'HOST': 'localhost:8000', 'CONNECTION': 'close', 'ACCEPT': '*/*', 'ACCEPT_ENCODING': 'deflate, gzip, br', 'KEY': 'vraLXzhHvgni+vEdeZJtoAlkI6miWvC2i78/tsaZrP12evp0UGT5dTv3Ej1i664gurgXpS51BR985oeDMsSWyWxL2rUJl3mhzZG4GkLdSlhskl5MYQb0sPUKPnvu/YXUKysoK2OyNHTM9AZtMZ92N4HAamvPkh/A0aosVcO92HwVy3IQHapMZH342XlBr96uW8qRQkEDTXiCxbDKI6FeryIqQf4CDfiwzfL9zE+aC/CaOm+lppqq/sYO09KqbC0KcdtW/gI/ns0NcwmHVa6qM0QnE9REW1hACJgDsxPdC4wpNHX93dg8uXKFhz9P1hDXMjJ2m+UYwKn1QANKeN+oDQ=='} 


auth_header:  KoTJahe5pbUt831sXDbKSyPzQEhVYLbyvli1NfEXi68Uen68NK18s2+TOMQDt92fmuh60oElmTIaX5fvyeRgvPE6G25oy5oPpFONQ2wnd5zNd5qAjGDoVEJVUEC4F3r8WjhpE3zD/SHlJJ8wrQt11FXjnrvNKeYz4JoWQSOfQiMVdOFJHcnfkdj6C1i+KT3hGPMr4wzr5odbZ2N2fqkpd79v9awPdecRhIOnG5NuewQCuid5QqscAgSt9Ot9+oS8onJlzgjSbrio6F1bkZmwkAZM6jAhLg7n9POsLU4v6wSGbQMETFYDwGdVfaBx1zCxDTUNj5IMKdY/fALOeKlcNQ== 

Salt:  b'd6069def11226c76' 

aes_key:  F+OsX4JW0N70joA+OBTLrA== 

key_header:  pJc0h3XrnEoc73ywj+88ExJ3TDOTQ0U++vpY9nqg6vLFutHlolvSCSXw1Ug+/t4BbRUE6ibX3ck+OM8e/oFofbpFichvrCRl4F+AeUsDOAbF+mCi7zkH/MK1tFC4sgU30ZdPgL352eODDQ19NTYvWK5VybcmuRNgLW5xncLmg/hZC6qwhYvwzmHjagwWdF8dx0m0waFe37M5YfHeXniRcenyoKNqjqyxzLAPvQugPYK83k96y7hpjAOrWdIkZjAv+PKXXoJqt2g/9ZNtS6wBGNuQFfGXRL8G5ny82q1theOa4EC0oJwrXyYzTRiYKPxF1ZfUJYiMHY3don9O2t6I8Q== 

Traceback (most recent call last):
  File "/app/payment/views/callback.py", line 37, in post
    decrypted_data = cipherpay_utils.decrypt_rsa(encrypted_data=requestData)
  File "/app/payment/utils/cipherkey_utils.py", line 294, in decrypt_rsa
    decrypted_data = private_key.decrypt(
TypeError: argument 'ciphertext': 'str' object cannot be converted to 'PyBytes'
Internal Server Error: /payment/upi/callback/
Not Found: /
Not Found: /boaform/admin/formLogin
Not Found: /boaform/admin/formLogin
POST upi/callback/ - CipherPay callback


RequestData:  i1ABjU3yoJ6b+ltNBtlZ/rrOyo19ZQHPAgil1npdigP1IE8IKhkk1vPVZT0AeSveG5iG8W0FEhnXkbF9+hnsr4eVdisRKCYA2aZnmycgSG6vTOzbjrfzcKOkr54YZV2EXRXYrijjlUNCkI6WhpR8tb2hCLqDH/pZA74dC6a+MSREJbsmOoeaO7jHTnJirtxYQBS1fwwU1oVAhM+oraFx0vo4XkIX116VHXg11yWVuoaQ5rgIHrL+xPcL8lZl8KHj/cnFmB1R3t5ssLKroPIbLkf4jOogqwYV5e1ICJTvaWVXfIymlpJ+cp7+oMIKd65KbDwlq/L+8qgkcL7NyX29Y+WNfZpa9gem0zXR/Rbh7YLkH92Yz6M4ixpr6pXgDZj8aqA06FFsk4MONiy2xDmt0qmEwRvSu9BwMN5D4B+MGnaTVHLp/LXg5MphcrDgn6ITu/OInkVbvWly2SmcFfY/8eJE0C5hExVmR3GrDy84qy8AvLM2UhGxpv5CBTlyA8KCG1kMG1QiYczQCRqIA8ChZ4DtNEZzMLfNxzS7SUEBVOIqGC24ekFt/YgukwGuRUc+y0odJi3q4q0AxOSNRkgJ09bhnZotd7oZeR732W0TRuRF71pYlaVoZPaQNzQ+OUjItLtpUaUCjsaRPb74/mUWOWQUrYYDlGfxrYlGzqPIbCRkaYbS/g9X/CmwkOd8CNupw1VTj/3y3JHOHl0VNIo9GYnlxeog4Nz+Vgw2zWhmMuwMnku889L366xGIvWMt7m+CFlaESjHX9vAgCcY9CBQU1DznSrj0l3043m7/iDisY1RANfYYlrucpM1F6/N6JMry1b8lVB5S3ceSEAMqqzzWTa+qmpd29YuPvEq68JLeqj7xlNjitq5DivZM3NCdBGyMg/V/M/TBAb/3yhfA+isG2i15A3KU9xFVUJjJv5G5ViYoNXplsjuICjgLVbuFfW8CdCIVyIvbzkKxNhb6TkGRoDvAyOukhcL+ibdHJEAq75kRwDtB6o4MUP9mkSDSDNib2vbOPtmInfDspEsEitGnITSVjeHV3djRAY6YKRT96dpOYc2wMHksR5fWcJipo0VXFepVuaNC4FAOH4bXFmqtQ== 


Headers:  {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7f982b90caf0>, 'wsgi.version': (1, 0), 'wsgi.multithread': True, 'wsgi.multiprocess': True, 'wsgi.run_once': False, 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>, 'wsgi.input_terminated': True, 'SERVER_SOFTWARE': 'gunicorn/20.1.0', 'wsgi.input': <gunicorn.http.body.Body object at 0x7f9817aaf070>, 'gunicorn.socket': <gevent._socket3.socket at 0x7f981795a6a0 object, fd=8, family=2, type=1, proto=6>, 'REQUEST_METHOD': 'POST', 'QUERY_STRING': '', 'RAW_URI': '/payment/upi/callback/', 'SERVER_PROTOCOL': 'HTTP/1.0', 'HTTP_HOST': 'localhost:8000', 'HTTP_CONNECTION': 'close', 'CONTENT_LENGTH': '1130', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'deflate, gzip, br', 'CONTENT_TYPE': 'application/json', 'HTTP_KEY': 'St91EO6FT5DQM3R1t164lelX8xM7etD60nnumRkkhN/VBnb1A+wzgWSjbBHpaqdYDfSQ/CXXGQPP6gYykp0LigZesbNisIqCsSr2hDISIIsuSsTgmarj/eWg/5z5w6KMF5nPvS9ou5XBxpp80P2bQhRM0rrab6aWOe5hgaNHxc5zbvmisN4X0QEJ//MsKZTpWijUiJleEVdDFimPSuSBQrV2NqQDVY0pwJbWLNi4tBX+PeP4G7bCVLUKkL2JcMND/57lWszD+RvwO6hvERDr6ALeYu8J1OYM1mZ6+RE/3LhpSVMnpBF1VWmf4AszPgoXrVPoe9ugmVbo6B+S7sVmRg==', 'wsgi.url_scheme': 'http', 'REMOTE_ADDR': '172.19.0.1', 'REMOTE_PORT': '54920', 'SERVER_NAME': '0.0.0.0', 'SERVER_PORT': '8000', 'PATH_INFO': '/payment/upi/callback/', 'SCRIPT_NAME': ''} 


HTTP Headers:  {'HOST': 'localhost:8000', 'CONNECTION': 'close', 'ACCEPT': '*/*', 'ACCEPT_ENCODING': 'deflate, gzip, br', 'KEY': 'St91EO6FT5DQM3R1t164lelX8xM7etD60nnumRkkhN/VBnb1A+wzgWSjbBHpaqdYDfSQ/CXXGQPP6gYykp0LigZesbNisIqCsSr2hDISIIsuSsTgmarj/eWg/5z5w6KMF5nPvS9ou5XBxpp80P2bQhRM0rrab6aWOe5hgaNHxc5zbvmisN4X0QEJ//MsKZTpWijUiJleEVdDFimPSuSBQrV2NqQDVY0pwJbWLNi4tBX+PeP4G7bCVLUKkL2JcMND/57lWszD+RvwO6hvERDr6ALeYu8J1OYM1mZ6+RE/3LhpSVMnpBF1VWmf4AszPgoXrVPoe9ugmVbo6B+S7sVmRg=='} 


auth_header:  Qq8VIx7zJtA7tv16sYEI2MZpjP9HW+8Fj331nbmZUcBr3aCWb+W0u1O4ME8swLv/mb8aYRINqRdVJaXLcGC5oeJzStOQynHSb8rh3s0JmChy8rmCvsVv7/fkES/BAZVCYb8aER6Spc9FQjslVkWDqMPQZuC8yIT8PpgM+2AG4PYCGZo3DEkyP1LYDm7tNFZA++E8tQZTyJSe7sAu7vHJIibvco1R1RSKvkKlHPH9ufFuoGrEY7hxAsRTKWWP6IaZ/dkSNX0Hzqpeo09DfxLkGWRXCcd42kQwtdNcWRuj6pGn6kUYAKfgcUWv9++AQxTpJsmXQ+u/VF46G19+huskzA== 

Salt:  b'5690c8abe58ea5fe' 

aes_key:  CWbhhDDculDgQwLadZztUg== 

key_header:  bt1iXBPMDTZqd6r7i94+OOG4uTCnDqueBW+ewZjDBu8OOJQXPP7bF/qzFftmA2b9ed+nZfppWacMfHm0xhS1WlSQFRzmxY+beVmlSEcg6SGqyJRSWOzsExWdFAYSyBzc6YZPjOcpRnEnxVxyVtR+O7QIStFrW6uzOb9VnhxbQ7AOoHu9zTF0/UhLc+xjN8tZumuvM21YlXMlhdJBVsTiNStyf3biaoClVcRo9sFhvbQEFh5EAVJVa2I5zGelY2eR7wssTKgZjTZdxasQXY5uhYv8wW7MzIRT/+tZlvMJ9vHEpHnJQWfUQbdmTBJmIVJQ/jHlttAEPuoVQIqRTa6i6w== 

Traceback (most recent call last):
  File "/app/payment/views/callback.py", line 37, in post
    decrypted_data = cipherpay_utils.decrypt_rsa(encrypted_data=requestData)
  File "/app/payment/utils/cipherkey_utils.py", line 294, in decrypt_rsa
    decrypted_data = private_key.decrypt(
TypeError: argument 'ciphertext': 'str' object cannot be converted to 'PyBytes'
Internal Server Error: /payment/upi/callback/

"""
