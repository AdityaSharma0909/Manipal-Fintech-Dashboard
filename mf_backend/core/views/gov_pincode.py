import traceback
from abc import abstractmethod

from rest_framework import status
import logging
from utility.common_utils import normalize_serializer_error
from utility.error_handler import HttpErrors
from utility.response_handler import HttpResponse
from rest_framework.views import APIView
import requests
import json


from utils.envSetup import environment
from core.service.third_party_api import ThirdPartyApi
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj




logger = logging.getLogger('radian')

class GetGovPincode(APIView):
    def get(self, request, *args, **kwargs):
        try:
            pincode = request.GET.get('pincode', None)
            if not pincode:
                # return custom_response_obj(message={'msg':'pincode is required'},
                #                    code=400,
                #                    error_msg={'msg':'pincode is required'},
                #                    error_code=400)
                response = HttpResponse().response(code=400, data={'msg':'pincode is required'},error_code=400,
                                                   error_msg={'msg':'pincode is required'}, )
                return response

            url = "https://api.data.gov.in/resource/6176ee09-3d56-4a3b-8115-21841576b2f6"
            url = url + "?api-key=" + str(environment.PINCODE_GOV_API_KEY)
            url = url + "&format=json"
            url = url + "&filters%5Bpincode%5D=" + pincode

            

            response = requests.request("GET", url, headers={})
            resp = response.json()

            msg = resp.get("message")
            if isinstance(msg, str) and "error" in msg:
                msg_json = json.loads(msg)
                return HttpResponse().response(
                    code=400,
                    data=None,
                    error_code=msg_json.get("status", 400),
                    error_msg="Please enter proper pincode.",
                )

            records = resp.get("records") or []
            if len(records) == 0:
                return HttpResponse().response(
                    code=400,
                    data=None,
                    error_code=400,
                    error_msg="Pincode not found!",
                )

            final_resp = [
                {
                    "statename": records[0].get("statename"),
                    "districtname": records[0].get("districtname"),
                    "country": "India",
                }
            ]

            return HttpResponse().response(data={'records':final_resp,}, code=200, )
        except Exception as e:
            traceback.print_exc()
            logger.exception('Exception ' + str(e))
            response = HttpErrors.InternalServerError(str(e))
            return response
