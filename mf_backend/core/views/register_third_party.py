from rest_framework.response import Response
from rest_framework.views import APIView

from core.service.register_third_party_user import ThirdPartyRegistrationLogin
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework
from utils.constants import ROLES


class RegisterThirdParty(ApiFramework):
    def __init__(self, data):
        super().__init__()
        self.__data=data

    def process(self):
        response=ThirdPartyRegistrationLogin().create_third_party_vendor(self.__data)
        return response


class RegisterThirdPartyView(APIView):
    permission_classes = [ThirdPartyPermission]
    def post(self, request):
        if request.user.role not in (ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value, ROLES.CPC.value):
            return Response(data={'msg':"only super admin, vertical admin or CPC is allowed"}, status=403)
        data=request.data.copy()
        return RegisterThirdParty(data=data).main()

