import datetime
import json
import os
import uuid

from dateutil import parser as parser
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework.response import Response

from application.models import Application , LoanDocument
from cibil_score.constant import state_code_dict
from cibil_score.serializers.cibil_serializer import ConsumerInputSubject
from cibil_score.service.convert_to_pdf import convert_cibil_json_to_pdf
from cibil_score.models import CibilScore
from radian_backend.settings import BASE_DIR
from utility.common_utils import custom_response_obj
from utils.constants import GENDER, RESENDITIAL_OWNERSHIP, ADDRESS_TYPE, APPLICATION_STATUS
from utils.envSetup import environment


class CibilScoreCheck:

    def __get_headers(self):

        if environment.APP_ENV=='PROD':
            apikey='l7d8827d553d9d4e85887b6b0d962c3813'
        else:
            apikey='l7f7523ad4a92649d0953f8c63140dedbf'
        return {
                    "member-ref-id": 'NB3861',
                    "cust-ref-id": uuid.uuid4().__str__()[0:9].replace("-",""),
                    "apikey": apikey
                }

    def check_consumer_report(self, application_no):
        data, application = self.__get_application_data(application_no)
        current_date = datetime.datetime.now().date()
        print('data', data)
        # Format the date as DDMMYYYY
        formatted_date = current_date.strftime("%d%m%Y")
        dob = parser.parse(data.get('dob')).date().strftime("%d%m%Y")
        print(formatted_date, dob)
        if data.get('gender')==GENDER.MALE.value: gender=1
        elif data.get('gender')==GENDER.FEMALE.value: gender=2
        else: gender= 3

        check_consumer_report_data= ConsumerInputSubject(data, formatted_date, dob, str(gender))
        result = check_consumer_report_data.to_dict()

        headers=self.__get_headers()
        if environment.APP_ENV=='PROD':
            url='https://api.transunioncibil.com/acquire/credit-assessment/v1/consumer-cir-cv'
            certFile = os.path.join(BASE_DIR, "keys/cibil/prod_public_cert.pem")
            keyFile = os.path.join(BASE_DIR, "keys/cibil/prod_private_key.pem")
        else:
            url='https://apiuat.cibilhawk.com/acquire/credit-assessment/v1/consumer-cir-cv'
            certFile = os.path.join(BASE_DIR, "keys/cibil/cert.pem")
            keyFile = os.path.join(BASE_DIR, "keys/cibil/key.pem")
        print(result)
        response = requests.post(url, headers=headers, json=result, cert=(certFile, keyFile))
        print(response.text)
        success=response.json().get("controlData", {}).get('success', False)
        # if response.status_code==200:
        if success:
            response= response.json()
            print(response)
            json_data = json.dumps(response)
            json_bytes = json_data.encode('utf-8')
            # application.cibil_report_json.save(application_no + '_cibil' + '.json', Con       tentFile(json_bytes), save=True)
            # application.save()
            try:
                document = LoanDocument.objects.get(application=application, document_type='CIBIL_JSON_REPORT')
                document.file.delete()
                document.file.save(application_no + '_cibil.json', ContentFile(json_bytes))
                document.save()
            except ObjectDoesNotExist:
                document = LoanDocument(document_type='CIBIL_JSON_REPORT', file_name=application_no + '_cibil.json', application=application)
        
                document.file.save(application_no + '_cibil.json', ContentFile(json_bytes))
                document.save()
            application.status=APPLICATION_STATUS.CIBIL_REPORT_GENERATED.value
            application.save()
            return convert_cibil_json_to_pdf(response,
                                             file_name=application_no+'.pdf',application=application)

        
        
        
        # with open("./sample_cibil_report.txt", "r") as u:
        #     json_str = u.read()
        # response=json.loads(json_str)
        # json_data=json.dumps(response)
        # json_bytes = json_data.encode('utf-8')


        #return convert_cibil_json_to_pdf(response,file_name=application_no + '.pdf',application=application)
        # Parse the JSON string
        # json_data = json.loads(json_str)
        #     response={
        #         'credit_score_data':{
        #             'scores':cibil_score_data['scores']
        #         },
        #         'disputes':response['consumerDisputeRemarks']
        #     }
        #     return custom_response_obj(message=response, code=200)
        data=custom_response_obj(message={'msg':f'error while pulling cibil report : {response.text}'},code=400)
        return Response(data, status=400)




    def __get_application_data(self, application_no):
        try:
            data={}
            address_details=[]
            application= Application.objects.get(application_number=application_no)
            account_data=application.account
            address=account_data.user_addresse.all()
            bank_account=account_data.bankaccount_account.all().first()

            if bank_account is None:
                raise ValueError("Bank account is required for Credit check")
            state_code=0
            for add in address:

                residence_type_code= "01" if add.residential_ownership in [RESENDITIAL_OWNERSHIP.INDIVIDUAL_OWNERSHIP.value,RESENDITIAL_OWNERSHIP.SELF_OWNED.value, RESENDITIAL_OWNERSHIP.NATIVE_OWNED.value] else "02"
                address_category= "01" if add.address_type ==  ADDRESS_TYPE.PERMANENT_ADDRESS.value else "02"

                add_line_1=str(add.building_name)+' '+str(add.street_name)+' '+str(add.city)+' '+str(add.pincode)
                addr=self.__format_address_to_lines(add_line_1)
                state_code = state_code_dict.get(add.state.title(), 0)

                temp_address_data={
                    'building_name': add.building_name,
                    'state_code': state_code,
                    'pin_code': add.pincode,
                    'residence_type':residence_type_code,
                    'address_category':address_category
                }
                for i, line in enumerate(addr):
                    print(f"Line {i + 1}: {line} {len(line)}")
                    temp_address_data['line_'+str(i+1)]=line

                address_details.append(temp_address_data)
            data['application_no']= str(application.application_number)
            data['address']=address_details
            data['loan_amount']=application.requested_loan_amount
            data['first_name']=account_data.user.first_name
            data['last_name']=account_data.user.last_name
            data['email']=account_data.email
            data['phone']= account_data.user.phone_to_str()
            data['bank_account']=bank_account.account_number
            data['pan_no']=account_data.pan_no
            data['state_code']=str(state_code)
            data['dob']=str(account_data.year_of_birth.date())
            data['gender']=account_data.gender


            return data, application

        except ObjectDoesNotExist:
            raise ValueError("Application Id not found")


    def __format_address_to_lines(self,address_line, max_length=40):
        words = address_line.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines[:4]
    
    # def __save_cibil_json_report(self, application, application_no, response):
    #     json_data = json.dumps(response)
    #     json_bytes = json_data.encode('utf-8')
    #     try:
    #         document = LoanDocument.objects.get(application=application, document_type='CIBIL_JSON_REPORT')
    #         document.file.delete()
    #         document.file.save(application_no + '_cibil.json', ContentFile(json_bytes))
    #         document.save()
    #     except ObjectDoesNotExist:
    #         document = LoanDocument(document_type='CIBIL_JSON_REPORT', file_name=application_no + '_cibil.json', application=application)
    #         document.file.save(application_no + '_cibil.json', ContentFile(json_bytes))
    #         document.save()

    # def __save_cibil_score(self, application, response):
    #     json_data = response
    #     print("json_data" , json_data)
    #     # Extract the score value
    #     score_value = None
    #     for score in json_data.get('scores', []):
    #         score_value = score['score']
    #         break  

    #     # Take only the last 3 digits of the score value
    #     if score_value is not None:
    #         score_value = str(score_value)[-3:]

    #     # Check if the last 3 characters of the score value are numeric
    #     if score_value and score_value.isdigit():
    #         score_value = int(score_value)
    #     else:
    #         # Handle the case where score_value is not numeric
    #         print(f"Invalid score value: {score_value}")
    #         return False  # or handle this case as needed

    #     # Check if the credit score already exists
    #     try:
    #         cibil_score = CibilScore.objects.get(application=application)
    #         cibil_score.cb_score = score_value
    #         cibil_score.save()
    #     except CibilScore.DoesNotExist:
    #         cibil_score = CibilScore(application=application, cb_score=score_value)
    #         cibil_score.save()

    #     return True
