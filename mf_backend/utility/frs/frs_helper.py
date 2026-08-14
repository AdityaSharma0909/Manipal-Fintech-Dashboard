from utility.common_utils import custom_response_obj
from utility.frs.frs_utilities import Frs


class FrsHelper:

    def __init__(self):
        self.__frs_instance=Frs()


    def process_bank_verification(self, account_number, ifsc, account_holder):
        verify_bank = self.__frs_instance.verify_bank(account_number=account_number, ifsc=ifsc,account_holder=account_holder)
        print(verify_bank)
        print(verify_bank.get('data',{}).get('bank_details',{}).get('beneficiary_name','').lower(),account_holder.lower())
        error = verify_bank.get('error', None)
        is_verified = False
        bank_status=verify_bank.get('data', {}).get('bank_status', 'FAILED')
        if error is None and bank_status == 'SUCCESS' :
            match_score=verify_bank.get('data',{}).get('match_score',{})
            if match_score is None:
                match_score=0
            else:
                match_score=int(match_score.get('name_1_match_score', '0'))
            is_verified = verify_bank.get('data',{}).get('match_status','FAILED') == 'SUCCESS' and match_score>=60
        return is_verified,error


    def process_pan_verification(self, pan_number):
        verify_pan=self.__frs_instance.verify_pan(pan_number)
        error=verify_pan.get('error', None)
        error_code=None
        if error is None:
            verify_pan=verify_pan['data']
            is_valid=verify_pan.get('pan_status','')=='VALID'
            error_code=400 if not is_valid else None
        return self.__send_response(verify_pan, error=error, error_code=error_code)

    def __send_response(self,message, error, error_code=None):
        if error:
            return custom_response_obj(message=message, code=400, error_msg=error,error_code=400)
        return custom_response_obj(message=message, code=200)


    def process_aadhar(self, data):
        verify_aadhar=self.__frs_instance.verify_aadhar(data)
        error = verify_aadhar.get('error', None)
        if error is None:
            verify_aadhar=verify_aadhar['data']
        return self.__send_response(verify_aadhar, error=error)


    def process_passport(self, data):
        verify_passport=self.__frs_instance.verify_passport(data)
        error = verify_passport.get('error', None)
        if error is None:
            verify_passport = verify_passport['data']
        return self.__send_response(verify_passport, error=error)


    def process_esign_documents(self, data, files):
        esign_request = self.__frs_instance.send_esign_request(data, files)
        error = esign_request.get('error', None)
        print('error', error)
        if error is None:

            esign_request = esign_request['data']
        return self.__send_response(esign_request, error=error)

    def verify_esign_status(self, data):
        esign_status=self.__frs_instance.verify_esign_status(data)
        error = esign_status.get('error', None)
        if error is None:
            esign_status = esign_status['data']
        return self.__send_response(esign_status, error=error)