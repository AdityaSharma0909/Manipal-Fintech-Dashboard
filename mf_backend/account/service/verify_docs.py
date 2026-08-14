from account.service.accountService import AccountService
from account.service.sprint_verify_docs import SprintVerifyDocs
from application.models import Application
from application.services.esign_application import EsignApplicationUtil
from utility.frs.frs_helper import FrsHelper
from account.models import Account, NomineeDetails
from utility.common_utils import custom_response_obj
from utils.constants import FRS_DOC_VERIFY, APPLICATION_STATUS, KYC_VENDORS
from utils.envSetup import environment


class VerifyDocs:

    def __init__(self, data):
        self.__doc_type=data.get('doc_type')
        self.__account_id=data.get('account_id', )
        self.__nominee_id=data.get('nominee_id')
        self.__verification_id=data.get('verification_id', )
        self.__frs_helper=FrsHelper()
        self.__data=data
        self.__aadhar_verification_type=data.get('verify_aadhar_type', 'account')
        self.__kyc_vendor=environment.KYC_VENDOR
        self.__sprint_verify=SprintVerifyDocs()

    def verify(self):

        if self.__doc_type not in [FRS_DOC_VERIFY.MOBILE_NUMBER.value, FRS_DOC_VERIFY.ESIGN_DOC.value, FRS_DOC_VERIFY.ESIGN_STATUS.value]:
            if not self.__account_id:
                return custom_response_obj(message="account_id is required",
                                           code=400,
                                           error_code=400,
                                           error_msg='account id is required')
            else:
                try:
                    if self.__aadhar_verification_type!='nominee':
                        self.__account = Account.objects.get(account_id=self.__account_id)
                    else:
                        self.__account=None
                except Account.DoesNotExist as ae:
                    return custom_response_obj(message=str(ae), code=400)
        
        if self.__doc_type=='PAN':
            return self.__pan_verification()
        elif self.__doc_type=='AADHAR':
            return self.__aadhar_verification()
        elif self.__doc_type=='PASSPORT':
            return self.__passport_verification()
        elif self.__doc_type=='MOBILE_NUMBER':
            return AccountService().verify_mobile_number_otp(self.__verification_id)
        elif self.__doc_type=='ESIGN_DOC':
            return self.__process_esign_request()
        elif self.__doc_type=='ESIGN_STATUS':
            return self.__process_esign_status()

    def __pan_verification(self):

        try:
            existingAcc = Account.objects.filter(pan_no=self.__verification_id)
            if len(existingAcc) > 0 and existingAcc.first().pan_no==self.__verification_id:
                return custom_response_obj(message={'msg':'Account already exist with given PAN'}, error_msg={'msg':'Account already exist with given PAN'}, code=200, error_code=200)
        except Exception as err:
            return custom_response_obj(message=str(err), error_msg=str(err), code=400, error_code=400)

        if self.__kyc_vendor==KYC_VENDORS.RNFI.value:
            response=self.__sprint_verify.pan_verification(payload={"id_number":self.__verification_id})
            valid=response.get('data',{}).get('idStatus','INVALID')
        else:
            response = self.__frs_helper.process_pan_verification(self.__verification_id)

            valid=response.get('data',{}).get('pan_status','INVALID')
        status = response.get('status')
        if status=='success' and valid=='VALID':
             self.__account.pan_no = response['data']['idNumber']
             self.__account.pan_verified = True
             self.__account.pan_meta_field=response['data']
             self.__account.save()
             response['data']['pan_status']=response.get('data',{}).get('idStatus','INVALID')
        else:
            response=custom_response_obj(message={'msg':'Invalid_pan_card'}, code=200)
        return response

    def __aadhar_verification(self):
        # TODO: remove below "self.__data.get('otp', None) is None" check
        if self.__kyc_vendor==KYC_VENDORS.FRS.value or self.__data.get('otp', None) is None:
            self.__data['access_token']=self.__data.pop('verification_id')
            response = self.__frs_helper.process_aadhar(self.__data)
        else:
            response=self.__sprint_verify.validate_aadhar_otp({'otp':self.__data.get('otp'),
                                                               'client_id':self.__data.get('verification_id')})
        if response['status'] == 'success':
            print(self.__aadhar_verification_type)
            if self.__aadhar_verification_type!='nominee' and self.__account:
                # TODO: remove below "self.__data.get('otp', None) is None" check
                if self.__kyc_vendor == KYC_VENDORS.FRS.value or self.__data.get('otp', None) is None:
                    self.__account.aadhar_no = response['data']['aadhaar_uid']
                else:
                    print("data", response['data'])
                    response['data']['aadhaar_number']='x' * 8 + response['data']['aadhaar_number'][-4:]
                    self.__account.aadhar_no = response['data']['aadhaar_number']
                self.__account.aadhar_verified = True
                self.__account.aadhar_meta_field = response['data']
                self.__account.save()
        return response

    def __passport_verification(self):
        return self.__frs_helper.process_passport(self.__data.get('data'))


    def __process_esign_request(self):
        payload = {'sender': self.__data.get('sender'),
                   'signatory': self.__data.get('signatory'),
                   'signature_config':self.__data.get('signature_config'),
                   'reminder_config': self.__data.get('reminder_config'),
                   'document_config': self.__data.get('document_config'),
                   'esign_url':'True',
                   'send_email':'False'
                   }
        uploaded_file = self.__data.get('document')
        files = {'document': (uploaded_file.name, uploaded_file, uploaded_file.content_type)}

        return self.__frs_helper.process_esign_documents(payload, files)

    def __process_esign_status(self):
        application=Application.objects.get(application_id=self.__data.get('verification_id'))
        resp=self.__frs_helper.verify_esign_status(data={'id':application.esign_application_id})
        if resp.get('status_code')==200 and resp.get('data').get("document_status")=="COMPLETED":
            link=resp.get('data').get('download_link')
            EsignApplicationUtil().save_document(link, application)
            application.status=APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
            application.save()

        return resp


