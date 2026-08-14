import datetime
import os
import uuid

import requests
from requests.adapters import HTTPAdapter
from rest_framework.views import APIView

from axis_test import axis_bank_call
from radian_backend import settings
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class TestAxisBankView(APIView, ApiFramework):
    serializer=None
    __endpoint=None
    __data=None
    __response=None
    def run_logic(self):
        try:
            print(self.__data.get('token').replace(" ",""))
            response=axis_bank_call(jwe_token_data=self.__data.get('token').replace(" ",""), endpoint=self.__endpoint)
            print("response",response.text)
            self.__response=custom_response_obj(message={'response':response.text,}, code=200)
        except Exception as e:
            self.__response = custom_response_obj(
                message={'data': e.__str__(), 'json': {}, 'code': 500}, code=200)

    def process(self):
        return self.__response

    def post(self, request, endpoint):
        self.__endpoint=endpoint
        self.__data=request.data
        return self.main()

