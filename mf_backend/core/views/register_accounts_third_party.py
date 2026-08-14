from rest_framework.response import Response
from rest_framework.views import APIView

from core.service.register_third_party_user import ThirdPartyRegistrationLogin
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework
from utils.constants import ROLES


class RegisterThirdPartyAccounts(ApiFramework):
    def __init__(self, data, created_by):
        super().__init__()
        self.__data = data
        self.__created_by=created_by

    def process(self):
        response = ThirdPartyRegistrationLogin().register_third_party_user(data=self.__data, created_by=self.__created_by)
        return response


class RegisterThirdPartyAccountsView(APIView):
    permission_classes = [ThirdPartyPermission]
    def post(self, request):
        data = request.data.copy()
        return RegisterThirdPartyAccounts(data=data, created_by=request.user).main()

