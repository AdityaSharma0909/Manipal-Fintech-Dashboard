from account.service.accountService import AccountService


class ThirdPartyApi:

    def get_account_verified(self, account_id):
        return AccountService().verify_kyc_for_third_party(account_id)


    def create_application(self, data):
        pass