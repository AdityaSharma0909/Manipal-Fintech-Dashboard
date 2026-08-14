import requests

from utils.envSetup import environment
import base64


class Frs:

    def __init__(self):
        self.__username = environment.FRS_USERNAME
        self.__password = environment.FRS_PASSWORD
        self.__base_url="https://api.atlaskyc.com/v2/prod/"
    def __process_headers(self):
        encoded_credentials = self.__encode_base64(self.__username+':' + self.__password)
        return {'Authorization': f'Basic {encoded_credentials}'}

    def __process_request(self, method, url, content_type=None, **kwargs):
        headers = self.__process_headers()
        if method=='GET':
            response = requests.request('GET', url, headers=headers, **kwargs)
        else:
            response = requests.request(method, url, headers=headers, **kwargs)
        return response.json()

    def __encode_base64(self, string_to_encode):
        return base64.b64encode(string_to_encode.encode("ascii")).decode("ascii")
    def verify_pan(self, pan_number):
        url=self.__base_url+'verify/pan'
        return self.__process_request(method='POST', url=url,params={'pan_number':pan_number})

    def verify_bank(self, account_number, ifsc, account_holder):
        url = self.__base_url + 'verify/bank_advanced'
        return self.__process_request(method='POST', url=url, params={'acc_number':account_number,'ifsc':ifsc,
                                                                      "name_n_match":account_holder,
                                                                      'name_1_match':account_holder,'fuzzy_match':"1"})


    def verify_status(self, verification_type, verification_id):
        url = self.__base_url + 'verify/status'
        return self.__process_request(method='GET', url=url,params={'type': verification_type, 'id': verification_id})


    def verify_aadhar(self, data):
        url=self.__base_url+'digilocker/aadhaar_xml'
        return self.__process_request(method='POST', url=url, data=data)


    def verify_passport(self, data):
        url = self.__base_url + 'verify/passport'

        return self.__process_request(method='POST', url=url,params=data)


    def send_esign_request(self, data, files):
        url=self.__base_url+'esign/request'
        return self.__process_request(method='POST', url=url ,data=data, files=files)


    def verify_esign_status(self, data):
        url=self.__base_url+'esign/status'
        return self.__process_request(method='POST', url=url, params=data)

    def mask_aadhar(self, data, files):
        url=self.__base_url+'aadhaar/mask'
        return self.__process_request(method='POST', url=url, data=data,files=files)