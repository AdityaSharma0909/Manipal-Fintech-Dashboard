import datetime
import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from application.models import Application, LoanDocument
from application.services.application_pdf_service import ApplicationPdfGeneration
from core.service.jofin_application_data import JoffinApplicationData
from utility.common_utils import custom_response_obj
from utility.frs.frs_helper import FrsHelper
from utils.constants import APPLICATION_STATUS, ROLES
from utils.envSetup import environment


class EsignApplicationUtil:


    def process_esign(self, application_id, user):
        application=self.__get_application_instance(application_id)
        if application is None:
            return custom_response_obj(message=f"Application with id {application} does not exist", code=404, error_code=400, error_msg=f"Application with id {application} does not exist")


        if application.Originatedby.role==ROLES.THIRD_PARTY_VENDOR.value:
            pdf, data=JoffinApplicationData().get_data(application_id)
            signature_config="LAST_PAGE_BOTTOM"
        else:
            pdf=ApplicationPdfGeneration().generate(application)
            signature_config = "FIRST_PAGE_BOTTOM"


        lm_email=application.Originatedby.email
        customer_email=application.account.email


        if customer_email and customer_email.strip() != "":
            signatory_email = customer_email

        elif not customer_email and lm_email and lm_email.strip() != "":
            signatory_email = lm_email

        elif not lm_email or (lm_email and lm_email.strip() == ""):
            signatory_email = application.Originatedby.lm_branch_map.all().first().branch.email

        else:
            signatory_email = environment.DEFAULT_CPC_ADMIN_EMAIL

        # if len(lm_email)==0:
        #     return custom_response_obj(message='Loan Officer email is mandatory for e sign, Please update Valid email id',
        #                                error_msg='Loan Officer email is mandatory for e sign, Please update Valid email id',
        #                                error_code=401,
        #                                code=401)
        # if len(signatory_email)==0:
        #     signatory_email=lm_email
        sender_email=None
        if lm_email and lm_email.strip() != "":
            sender_email = lm_email

        elif not lm_email or (lm_email and lm_email.strip() == ""):
            sender_email = application.Originatedby.lm_branch_map.all().first().branch.email

        else:
            signatory_email = environment.DEFAULT_CPC_ADMIN_EMAIL
        
        print("signatory_email: "+signatory_email)
        print("sender_email: "+sender_email)
        payload=self.__create_payload(application, signatory_email, sender_email,signature_config=signature_config)

        pdf_file_name= "{app_no}-{fn}_{ln}.pdf".format(
            app_no=application.application_number,
            fn=application.account.user.first_name,
            ln=application.account.user.last_name,
        )
        files = {'document': (pdf_file_name, pdf, 'application/pdf')}

        resp=FrsHelper().process_esign_documents(payload, files)

        try:
            loan_doc = LoanDocument.objects.get(application=application,document_type='SIGNED_LOAN_DOCUMENT')
            # If exists, update the existing document
            loan_doc.esign_id = resp.get('data').get('id')
            loan_doc.esign_signature_link = resp.get('data').get('esign_url')[0]['signer_url']
            loan_doc.save()
        except ObjectDoesNotExist:
            # If not exists, create a new document
            if resp.get('status_code') == 200:
                loan_doc = LoanDocument(
                    document_type='SIGNED_LOAN_DOCUMENT',
                    uploaded_by=user,
                    application=application,
                    esign_id=resp.get('data').get('id'),
                    esign_signature_link=resp.get('data').get('esign_url')[0]['signer_url']
                )
                loan_doc.save()

        # if resp.get('status_code')==200:
        #     # TODO e-sign:  
        #     # Create loan_doc:
        #     loan_doc = LoanDocument(document_type='SIGNED_LOAN_DOCUMENT',
        #                                 uploaded_by=user,
        #                                 application=application)
        #     print(loan_doc.uploaded_by)
        #     loan_doc.esign_id=resp.get('data').get('id')
        #     loan_doc.esign_signature_link=resp.get('data').get('esign_url')[0]['signer_url']
        #     loan_doc.save() This one
            # loan_doc = LoanDocument(application=application, document_type='SIGNED_LOAN_DOCUMENT', uploaded_by=req.user)
            # loan_doc.esign_id=resp.get('data').get('id')
            # loan_doc.esign_signature_link=resp.get('data').get('esign_url')[0]['signer_url']

            
            # application.esign_application_id=resp.get('data').get('id')
            # application.esign_signature_link=resp.get('data').get('esign_url')[0]['signer_url']
            # #application.status=APPLICATION_STATUS.E_SIGN_REQUEST_SENT.value
            # application.save()
        return resp

    def __get_application_instance(self, application_id):
        try:
            application=Application.objects.get(application_id=application_id)

            return application
        except ObjectDoesNotExist:
            return None

    def __create_payload(self, application, signatory_email, sender_email, signature_config="FIRST_PAGE_BOTTOM"):
        sender=self.__get_json_dump({"name": application.Originatedby.first_name+' '+application.Originatedby.last_name,"email": sender_email})
        signatory=self.__get_json_dump({"signatories": [{"name": application.account.user.first_name+' '+str(application.account.user.last_name),
                                                         "email": signatory_email}]})
        signature_config=self.__get_json_dump({"signature_stamp": signature_config})
        remainder_config=self.__get_json_dump({"reminder": "EVERY_DAY"})
        expiry_date= (datetime.datetime.now() + datetime.timedelta(days=90)).date()
        day="0"+str(expiry_date.day) if len(str(expiry_date.day))==1 else str(expiry_date.day)
        month="0"+str(expiry_date.month) if len(str(expiry_date.month))==1 else str(expiry_date.month)
        document_config=self.__get_json_dump({"expiry_date": f"{day}-{month}-{expiry_date.year}","send_signed_copy": "BOTH"})

        return {
                'sender': sender,
                'signatory':signatory,
                'signature_config':signature_config,
                'reminder_config': remainder_config,
                'document_config': document_config,
                'esign_url': 'True',
                'send_email': 'True'
            }

    def __get_json_dump(self, data):
        return json.dumps(data)

    # TODO e-sign:
    # def save_document(self, link, application, loan_doc=None):
    def save_document(self, link, loan_doc):
        response = requests.get(link)
        if response.status_code == 200:
            file_content = response.content
            # file_name = "{app_no}-{fn}_{ln}.pdf".format(
            #     app_no=application.application_number,
            #     fn=application.account.user.first_name,
            #     ln=application.account.user.last_name,
            # )  # Extract file name from URL
            # TODO e-sign: DONE!
            # if loan_doc:
            #     file_name = app_id + loan_doc_type
            #     loan_doc.file_name = file_name
            #     loan_doc.file.save(file_name, ContentFile(file_content))
            # else:
            #     # add all below code in else:
            
            file_name = "{esign_id}-{type}.pdf".format(
                esign_id = loan_doc.esign_id,
                type = loan_doc.document_type,
            )
            loan_doc.file_name = file_name
            loan_doc.file.save(file_name, ContentFile(file_content))
            loan_doc.save()
            
            # else:
            #     try:
            #         LoanDocument.objects.get(document_type='SIGNED_LOAN_DOCUMENT',
            #                                 application=application)
            #     except ObjectDoesNotExist:
            #         document = LoanDocument(document_type='SIGNED_LOAN_DOCUMENT',
            #                                 file_name=file_name,
            #                                 application=application)
            #         document.file.save(file_name, ContentFile(file_content))
            #         document.save()
            #     except:
            #         pass