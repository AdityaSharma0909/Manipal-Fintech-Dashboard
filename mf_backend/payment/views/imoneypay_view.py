from payment.models import BharatSwasthyaRepayment
from utility.response_handler import HttpResponse
from utils.constants import APPLICATION_STATUS
from utility.error_handler import HttpErrors
from application.models import Application
from rest_framework.views import APIView
from utils.envSetup import environment
import traceback
import requests
import logging
import hashlib


logger = logging.getLogger("radian")


class IMoneyPayGenerateQR(APIView):

    def post(self, request, *args, **kwargs):

        try:
            data = request.data

            application_id = data.get("application_id")
            amount = data.get("amount", "100")

            application = Application.objects.get(application_id=application_id)
            phone_number = str(application.account.user.phone)
            # name = f"{application.account.user.first_name} {application.account.user.last_name}"

            existing_repayments = BharatSwasthyaRepayment.objects.filter(application=application)

            if existing_repayments:
                existing_repayments.delete()

            repayment = BharatSwasthyaRepayment.objects.create(
                initiated_by=request.user,
                created_by=request.user,
                application=application,
                amount=amount
            )

            payload = {
                "CUST_EMAIL": environment.DEFAULT_CPC_ADMIN_EMAIL,
                "ORDER_ID": repayment.order_id,
                "PAY_ID": environment.PAY_ID,
                "UPI_TRANSACTION_MODE": "QR",
                #"CUST_NAME":name,
                "CUST_PHONE": phone_number,
                "CURRENCY_CODE": "356",
                "PAYMENT_TYPE": "UP",
                "TXNTYPE": "SALE",
                "MOP_TYPE": "UP",
                "AMOUNT": amount
            }

            sorted_payload = sorted([f"{key}={value}" for key, value in payload.items()])
            print("SORTED PAYLOAD:",sorted_payload)
            print("SECRET KEY:",environment.IMONEY_SECRET_KEY)
            hash_string = "~".join(sorted_payload) + environment.IMONEY_SECRET_KEY
            print("HASH STRING",hash_string)
            payload["HASH"] = hashlib.sha256(hash_string.encode()).hexdigest().upper()

            url = "https://prod.imoneypay.in/pgws/transact"
            #url = "https://uat.royalshop.me/pgws/transact"
            print("Reached to the url part")
            
            response = requests.post(url, json=payload)
            print("Response from URL>>>>>>>>:", response.text)
            qr_data = response.json()
            print("Parsed QR Data>>>>>>>:", qr_data)
            if qr_data.get("RESPONSE_CODE") == "000":
                qr_code = qr_data.get("UPI_PAY_QR")

                repayment.status = "QR_GENERATED"
                repayment.save()

                application.status = APPLICATION_STATUS.IMONEY_QR_GENERATED.value
                application.save()

                return HttpResponse().response(code=200, data={"qr_code": qr_code, "order_id": repayment.order_id})

            else:
                response_message = qr_data.get("RESPONSE_MESSAGE")
                logger.error(f"QR Generation failed: {qr_data}")

                repayment.status = "QR_FAILED"
                repayment.save()
                return HttpErrors.BadRequest(response_message)

        except Exception as e:
            logger.exception(f"Exception occurred in IMoneyPayGenerateQR: {str(e)}")
            traceback.print_exc()

            return HttpErrors.InternalServerError(str(e))


class IMoneyPayStatusView(APIView):

     def post(self, request, *args, **kwargs):

        try:
            data = request.data
            order_id = data.get("order_id")

            error_msg = "order_id is required!"

            if not order_id:
                response = HttpResponse().response(code=400, data={"msg": error_msg}, error_code=400, error_msg={"msg": error_msg})
                return response

            payment = BharatSwasthyaRepayment.objects.get(order_id=order_id)
            return HttpResponse().response(code=200, data={"order_id": order_id, "status": payment.status})

        except Exception as e:
            logger.exception(f"Exception occurred in IMoneyPayStatusView: {str(e)}")
            traceback.print_exc()

            return HttpErrors.InternalServerError(str(e))
