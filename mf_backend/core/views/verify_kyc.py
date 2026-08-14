from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.views import APIView

from core.service.third_party_api import ThirdPartyApi
from middlewares.auth import ThirdPartyPermission
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class VerifyKycView(APIView, ApiFramework):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [ThirdPartyPermission]
    account_id=None
    serializer=None
    def process(self):
        if self.account_id:
            return ThirdPartyApi().get_account_verified(account_id=self.account_id)
        return custom_response_obj(message={'msg':'account_id is required'},
                                   code=400,
                                   error_msg={'msg':'account_id is required'},
                                   error_code=400)
    def get(self, request):
        self.account_id=request.query_params.get('account_id')
        return self.main()