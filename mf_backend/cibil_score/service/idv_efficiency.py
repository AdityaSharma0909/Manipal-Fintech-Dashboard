import json
import os
import uuid

import requests
from dateutil import parser as parser
from django.core.exceptions import ObjectDoesNotExist

from application.models import Application
from cibil_score.serializers.idv_serializers import IDVerificationData
from radian_backend.settings import BASE_DIR
from utility.common_utils import custom_response_obj
from utils.constants import GENDER
from utils.envSetup import environment


class IdvEfficiency:

    def __get_headers(self):
        if environment.APP_ENV=='PROD':
            apikey='l7d8827d553d9d4e85887b6b0d962c3813'
            client_token='c56a72a395164d51afce922959cf96de'
        else:
            apikey='l7f7523ad4a92649d0953f8c63140dedbf'
            client_token='bb39611a-e5a6-4986-824f-421722b99649'
        return {
        "Clientid": "NB3861",
        "client-token": client_token,
        "apikey": apikey,
        "cust-ref-id":uuid.uuid4().__str__()[0:9].replace("-",""),
        "member-ref-id": 'NB3861',

    }


    def call_idv_efficiency(self, application_no):
        data= self.__get_application_data(application_no)

        print('data', data)
        # Format the date as DDMMYYYY


        print(json.dumps(data, indent=4))
        headers = self.__get_headers()
        if environment.APP_ENV=='PROD':
            url='https://api.transunioncibil.com/fraud-id-management/verification/v1/IDV-efficiency'
        else:
            url='https://apiuat.cibilhawk.com/fraud-id-management/verification/v1/IDV-efficiency'
        certFile = os.path.join(BASE_DIR, "keys/cibil/cert.pem")
        keyFile = os.path.join(BASE_DIR, "keys/cibil/key.pem")
        print("data", data)
        response = requests.post(url, headers=headers, json=data, cert=(certFile, keyFile))

        print(response.text, response.status_code)
        if response.status_code == 200:
            response = response.json()
            return custom_response_obj(message=response, code=200)
        return custom_response_obj(message={'msg': f'error while pulling cibil report : {response.text}'}, code=200)



    def __get_application_data(self, application_no):
        try:

            application= Application.objects.get(application_number=application_no)
            account_data=application.account

            gender=account_data.gender
            if gender == GENDER.MALE.value:
                gender = 1
            elif gender == GENDER.FEMALE.value:
                gender = 2
            else:
                gender = 3
            dob = parser.parse(str(account_data.year_of_birth.date())).date().strftime("%d%m%Y")
            data=IDVerificationData(
                name={
                'firstName':account_data.user.first_name,
                'lastName':account_data.user.last_name
                },
                dob={'value':dob}, gender={'value':str(gender)},
                mobilePhone=[{'number':account_data.user.phone_to_str()}],
                gstStateCode={'value':"29"},
                pan={'value':str(account_data.pan_no)},
            )
            return data.to_dict()

        except ObjectDoesNotExist:
            raise ValueError("Application Id not found")

