
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import traceback
import logging

from utils.envSetup import environment
from utils.responseHandler import HttpResponse
from payment.utils.cipherkey_utils import CipherpayHelper

logger = logging.getLogger('radian')


class CipherpayUPICollect(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        user = request.user
        # data = request.data
        # header = request.header
        try:
            encrypted_param = request.GET.get()
            encrypted_data = request.data.get("param_enc")
            encrypted_header = request.header.get()



            response = HttpResponse.Success("")
            return response
        except Exception as e:
            traceback.print_exc()
            logger.exception('Exception ' + str(e))
            response = HttpResponse.Success("")
            return response
