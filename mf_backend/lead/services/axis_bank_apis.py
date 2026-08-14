import json

import requests

from axis_test import axis_bank_call
from utility.common_utils import custom_response_obj


class AxisBankCalls:

    def __login(self):
        login_data=json.dumps({"Data": {"userName": "alwebuser", "password": "acid_qa"}, "Risks": {}}).replace(" ","")
        encrypt_payload=self.__encrypt(payload=login_data)
        print("encrypt:payload")
        resp_data=self.__send_data_to_axis_bank(data=encrypt_payload, endpoint='login')
        print(resp_data)
        if resp_data:
            decrypted_data=self.__decrypt(resp_data)
            resp_data=json.loads(decrypted_data)
        return resp_data
    def __encrypt(self, payload):
        return self.__call_sprint_boot_service(action="encrypt", payload=payload)

    def __decrypt(self, payload):
        return self.__call_sprint_boot_service(action="decrypt", payload=payload)

    def create_lead(self, payload):
        resp_data=self.__login()
        print("login resp:", resp_data)
        if resp_data:
            token=resp_data.get('Data',{}).get('token')
            print("token login", token)
            payload=self.__process_payload_for_lead_data(data=payload, token=token)
            print("lead payload", payload)
            encrypt_payload = self.__encrypt(payload)
            print("encrypted payload=========>", encrypt_payload)
            resp_data=self.__send_data_to_axis_bank(data=encrypt_payload, endpoint='create-lead')
            print("lead response-",resp_data)
            if resp_data:
                decrypted_data = self.__decrypt(resp_data)
                resp_data= custom_response_obj(message=json.loads(decrypted_data), code=200)
                return resp_data
        else:
            return custom_response_obj(message={"msg":"Failed to encrypt/decrypt data"}, code=200)
        return resp_data


    """
        here data should be the encrypted token and endpoint should be the endpoint expected at axis bank servers
        two of the endpoints we are currently using are
        1.login
        2.create-lead
    """
    def __send_data_to_axis_bank(self, data, endpoint):
        try:
            response=axis_bank_call(jwe_token_data=data.replace(" ",""), endpoint=endpoint)
            return response.text
        except Exception as e:
            return None

    """
        since we are running our axis bank encryption and decryption api in another docker container on same machine 
        we are placing the app name of  docker as local host
    """
    def __call_sprint_boot_service(self,action, payload):
        #url = f"http://127.0.0.1:8080/{action}"
        url = f"http://axisBankApp:8002/{action}"
        headers = {
            'Content-Type': 'text/plain',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text

    def __process_payload_for_lead_data(self, data, token):
        lead_initial_data={
                            "Data": {
                                "token": token,
                                "lastName": data.get('last_name'),
                                "leadOwnerId": 1,
                                "subSource": "Radian",
                                "deferredDate": "2023-05-05 18:10:00.000",
                                "city": data.get('city',''),
                                "branch": "1596",
                                "customerType": 1,
                                "createdBySource": 54,
                                "otherSource": 1,
                                "state": data.get('state',''),
                                "email": data.get('email',''),
                                "product": "365",
                                "address3": data.get('address3',""),
                                "address2": data.get('address2',""),
                                "address1": data.get('address1',""),
                                "leadSource": 147,
                                "dateOfBirth": data.get('dob'),
                                "panNumber": data.get("pan_number"),
                                "layout": 1002,
                                "subProduct": 374,
                                "followUpDate1": "2023-05-05 18:10:00.000",
                                "mobilePhone": data.get('mobile_number'),
                                "pinCode": "",
                                "salutationId": 1,
                                "first Name": data.get('first_name'),
                                "leadPriority": 100001,
                                "statusCode": 146,
                                "loanAmountInLakhs":data.get("loan_amount_in_lakhs")
                            },
                            "Risks": {}
                        }
        return json.dumps(lead_initial_data).replace(" ","")

"""
Sample payload for login:-
{"Data": {"userName": "alwebuser", "password": "acid_qa"}, "Risks": {}}
Sample payload for lead creation:-
{
    "Data": {
        "token": "qjg8clqv8mjs5njd6l2s676fk5h22mu7uswaz7zq8mzahy83h372kk7q6sfuynds9xmyqjz5m7vfmhjnmurenzlmfpvp5e9qfuglvdueyq97e84nu7vcf8zgaj6dzk5bt6thngeb7gyae7m73fuldet4bttm9z6d5w8dsss5qctm2wcfv7kfkmubcvlekxxaax2jxlmpemcnjkcl78etpszfl4ufpxlf7u486fgf3v7erav23e56t95e299nsy7hhpq8vxvy8vzs54j5u9pt3jmthap887fe8tqjkwy3v4h3c8w9mareglckfcssub64fs4qfybrjp3d6zxh7kzkdv7nlderhd8vllx8z4qedqx82g3ssrm2pngx3kwbhhc5l268vp5ggdxsjfhhpu8ky6njjzty2ucdrtgcbs2u3sztmlfglfybsbcd276rltjblpkwmnld6hz8pa62z29g4gcht8n7wk858jx44k9ezpcaex932x4bfn3gw3ves4dqarsxes7w6pysskf73387kcgawyfsr5ujxaexuurml89rwhdd7mh4my69phpqet84nwm6gwx42surjd83jaygrkmtat4afl5pfrtckq2",
        "lastName": "KUMAR",
        "leadOwnerId": 1,
        "subSource": "3781",
        "deferredDate": "2023-05-05 18:10:00.000",
        "city": "Chennai",
        "branch": "1596",
        "customerType": 1,
        "createdBySource": 54,
        "otherSource": 1,
        "state": "Tamil Nadu",
        "email": ".",
        "product": "365",
        "address3": "uttam nagar",
        "address2": "no 9 vikas enclave",
        "address1": "B91 gali",
        "leadSource": 153,
        "dateOfBirth": "1993-02-02",
        "panNumber": "NOPAN1234X",
        "layout": 1002,
        "subProduct": 374,
        "followUpDate1": "2023-05-05 18:10:00.000",
        "mobilePhone": "7899475301",
        "pinCode": "600004",
        "salutationId": 1,
        "first Name": "AMIT",
        "leadPriority": 100001,
        "statusCode": 146
    },
    "Risks": {}
}
"""

