from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.service.register_third_party_user import ThirdPartyRegistrationLogin
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework
from utils.constants import ROLES


class LoginThirdParty(ApiFramework):
    def __init__(self, data):
        super().__init__()
        self.__data = data

    def process(self):
        response = ThirdPartyRegistrationLogin().authenticate_users(data=self.__data,
                                                                    key_secret=self.__data.get('key_secret').replace("Basic ",""))
        return response


class LoginThirdPartyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        key_secret = request.META.get('HTTP_AUTHORIZATION')
        data['key_secret']=key_secret
        return LoginThirdParty(data=data).main()

