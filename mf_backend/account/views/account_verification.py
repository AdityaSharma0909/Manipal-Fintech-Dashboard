from rest_framework.views import APIView
from account.service.accountService import AccountService
from utility.api_framework import ApiFramework


class AccountVerification(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data = data

    def process(self):
        return AccountService().account_kyc_verification(account_id=self.__data.get('account_id'), data=self.__data)


class AccountVerificationView(APIView):

    def patch(self, request):
        data = request.data
        data['account_id'] = request.GET.get('account_id')
        return AccountVerification(data=data).main()
