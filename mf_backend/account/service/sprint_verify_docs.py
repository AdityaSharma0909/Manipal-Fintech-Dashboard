import datetime
import random

from utility.common_utils import custom_response_obj
from utility.connection_utils import ConnectionUtil
from utility.jwt_token import CreateJWTToken
from utils.envSetup import environment
from  datetime import timedelta


class SprintVerifyDocs:

    def __init__(self):
        self.__connection=ConnectionUtil()
        self.__url='https://api.verifya2z.com/api/v1'
    def __generate_access_token(self):
        payload={
            "timestamp": (datetime.datetime.now() + timedelta(minutes=10)).timestamp(),
            "partnerId": "CORP00001186", #PROVIDED BY SPRINTVERIFY
            "reqid": self.__generate_req_id() #must be unique for every request
        }
        access_token=CreateJWTToken().create_token(payload)
        return access_token

    def __generate_req_id(self):
        return random.randint(000000,999999)

    def __create_header(self):
        token=self.__generate_access_token()
        return {
            'Token':token,
            'authorisedkey':'TnpneU9UVTNPRGs1T1RFeU9ETkRUMUpRTURBd01ERXhPRFk9'
        }


    def bank_verification(self, data):
        data['extended_data']=1
        bank_verification=self.__connection.process_request('POST',
                                                            url=self.__url+'/verification/penny_drop_v2',
                                                            headers=self.__create_header(),
                                                            data=data)

        return self.__process_response(bank_verification)


    def mask_aadhar(self, file, back):
        data={
            'type':'MASK-AADHAR',
        }
        if back:
            data['back']=back
        files = {'file': (file.name, file, file.content_type)}

        response=self.__connection.process_request(method='POST',url=self.__url+'/verification/ocr_doc',
                                                   headers=self.__create_header(),
                                                   data=data,files=files)
        return self.__process_response(response)


    def __process_response(self, data):
        status=data.get('statuscode', 400)
        if status == 200:
            return custom_response_obj(message=data.get('data'), code=200)
        return custom_response_obj(message={'msg': data.get('message')}, code=200)

    def pan_verification(self, payload):
        pan_verification=self.__connection.process_request('POST',
                                                           url=self.__url+'/verification/pandetails_verify',
                                                           headers=self.__create_header(),
                                                           data=payload)
        return self.__process_response(pan_verification)

    def process_verification(self, verification_type, payload):
        if verification_type=='pan':
            return self.pan_verification(payload=payload)
        elif verification_type=='bank':
            return self.bank_verification(payload)
        elif verification_type=='aadhar_mask':
            return self.mask_aadhar(payload.get('file'), back=payload.get('back', None))
        elif verification_type=='aadhaar':
            return self.aadhar_verification_with_otp(payload)
        elif verification_type=='aadhaar_otp':
            return self.validate_aadhar_otp(payload)

    def aadhar_verification_with_otp(self, payload):
        aadhar_verification = self.__connection.process_request('POST',
                                                             url=self.__url + '/verification/aadhaar_sendotp',
                                                             headers=self.__create_header(),
                                                             data=payload)
        return self.__process_response(aadhar_verification)


    def validate_aadhar_otp(self, payload):
        aadhar_verification = self.__connection.process_request('POST',
                                                                url=self.__url + '/verification/aadhaar_verifyotp',
                                                                headers=self.__create_header(),
                                                                data=payload)
        print("aadhar_verification responses------",self.__process_response(aadhar_verification))
        return self.__process_response(aadhar_verification)


if __name__=='__main__':
    payload = {
        "timestamp": (datetime.datetime.now() + timedelta(minutes=10)).timestamp(),
        "partnerId": "CORP00001186",  # PROVIDED BY SPRINTVERIFY
        "reqid": random.randint(000000,999999)  # must be unique for every request
    }
    access_token = CreateJWTToken().create_token(payload)
    print(access_token)