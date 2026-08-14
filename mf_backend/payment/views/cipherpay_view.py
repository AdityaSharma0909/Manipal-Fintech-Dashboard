from rest_framework.views import APIView
import json
import traceback
import logging

from utils.envSetup import environment

# from utils.responseHandler import HttpResponse
from utility.response_handler import HttpResponse
from utility.error_handler import HttpErrors
from payment.utils.cipherkey_utils import CipherpayHelper

from loan.models import Loan

logger = logging.getLogger("radian")

# from payment.utils.cipherkey_utils import CipherpayHelper
# from users.models import User
# from utils.envSetup import environment

# user = User.objects.get(pk='09d91051-1f54-4b4f-b484-8d61195673ea')
# # environment.RADIAN_VPA = 'cpy.radian@fin'
# data = {
#     "sender_vpa": '7977440556@kotak',
#     "amount": '123abc',
#     "sender_name": 'Radian Dev Server',
#     "sender_mobile": '9999999999',
# }
# cipherpay_utils = CipherpayHelper()
# success, resp = cipherpay_utils.cipherpay_dynamic_qr(data=data, loan_number='1270001SLHM020411', loan_id='ff877913-395c-4e35-b62c-d3dc79564ff8', user=user)
# print(success)
# print(resp)


class CipherpayGenerateIntentURL(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        try:

            amount = data.get("amount", None)
            if not amount:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "amount is required"},
                    error_code=400,
                    error_msg={"msg": "amount is required"},
                )
                return response

            loan_id = data.get("loan_id", None)
            if not loan_id:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "loan_id is required"},
                    error_code=400,
                    error_msg={"msg": "loan_id is required"},
                )
                return response

            loan = Loan.objects.get(loan_id=loan_id)

            data = {
                "amount": amount,
            }
            cipherpay_utils = CipherpayHelper()
            success, resp = cipherpay_utils.cipherpay_dynamic_qr(
                data=data,
                loan_number=loan.loan_number,
                loan_id=loan.loan_id,
                user=user,
                qr_type="INTENT",
            )
            if not success:
                response = HttpErrors.BadRequest(resp)
                return response

            intent = resp.get("intent", None)
            del resp["intent"]
            return HttpResponse().response(code=200, data={"payments": resp, "intent": intent})

        except Loan.DoesNotExist as e:
            logger.error("Error " + str(e))
            response = HttpErrors.BadRequest(str(e))
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception("Exception " + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response


class CipherpayGenerateQR(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        try:

            amount = data.get("amount", None)
            if not amount:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "amount is required"},
                    error_code=400,
                    error_msg={"msg": "amount is required"},
                )
                return response

            loan_id = data.get("loan_id", None)
            if not loan_id:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "loan_id is required"},
                    error_code=400,
                    error_msg={"msg": "loan_id is required"},
                )
                return response

            loan = Loan.objects.get(loan_id=loan_id)

            data = {
                "amount": amount,
            }
            cipherpay_utils = CipherpayHelper()
            success, resp = cipherpay_utils.cipherpay_dynamic_qr(
                data=data,
                loan_number=loan.loan_number,
                loan_id=loan.loan_id,
                user=user,
                qr_type="QR",
            )
            if not success:
                response = HttpErrors.BadRequest(resp)
                return response

            # Extracting QR code from the response
            qr_code = resp.get("qr", None)

            # Removing QR code from the payments response
            del resp["qr"]

            return HttpResponse().response(
                code=200, data={"payments": resp, "qr": qr_code}
            )

        except Loan.DoesNotExist as e:
            logger.error("Error " + str(e))
            response = HttpErrors.BadRequest(str(e))
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception("Exception " + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response


# ========================================= #


class CipherpayInitiateCollect(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        try:

            sender_vpa = data.get("sender_vpa", None)
            if not sender_vpa:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "sender_vpa is required"},
                    error_code=400,
                    error_msg={"msg": "sender_vpa is required"},
                )
                return response

            sender_name = data.get("sender_name", None)
            if not sender_name:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "sender_name is required"},
                    error_code=400,
                    error_msg={"msg": "sender_name is required"},
                )
                return response

            sender_mobile = data.get("sender_mobile", None)
            if not sender_mobile:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "sender_mobile is required"},
                    error_code=400,
                    error_msg={"msg": "sender_mobile is required"},
                )
                return response

            amount = data.get("amount", None)
            if not amount:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "amount is required"},
                    error_code=400,
                    error_msg={"msg": "amount is required"},
                )
                return response

            loan_id = data.get("loan_id", None)
            if not loan_id:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "loan_id is required"},
                    error_code=400,
                    error_msg={"msg": "loan_id is required"},
                )
                return response

            loan = Loan.objects.get(loan_id=loan_id)

            data = {
                "sender_vpa": sender_vpa,
                "amount": amount,
                "sender_name": sender_name,
                "sender_mobile": sender_mobile,
            }
            cipherpay_utils = CipherpayHelper()
            success, resp = cipherpay_utils.cipherpay_initiate_collect(
                data=data, loan_number=loan.loan_number, loan_id=loan.loan_id, user=user
            )
            if not success:
                response = HttpErrors.BadRequest(str(resp))
                return response

            return HttpResponse().response(code=200, data={"payments": resp})

        except Loan.DoesNotExist as e:
            logger.error("Exception " + str(e))
            response = HttpErrors.BadRequest(str(e))
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception("Exception " + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response


class CipherpayStatusView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        try:

            reference_id = data.get("reference_id", None)
            if not reference_id:
                response = HttpResponse().response(
                    code=400,
                    data={"msg": "reference_id is required"},
                    error_code=400,
                    error_msg={"msg": "reference_id is required"},
                )
                return response

            data = {
                "reference_id": reference_id,
            }
            cipherpay_utils = CipherpayHelper()
            success, resp = cipherpay_utils.cipherpay_fetch_status(
                reference_id=reference_id
            )
            if not success:
                response = HttpErrors.BadRequest(resp)
                return response

            return HttpResponse().response(code=200, data={"payments": resp})

        except Loan.DoesNotExist as e:
            logger.error("Error " + str(e))
            response = HttpErrors.BadRequest(str(e))
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception("Exception " + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response
