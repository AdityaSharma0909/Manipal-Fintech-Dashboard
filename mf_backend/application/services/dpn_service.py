from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from decimal import Decimal
from datetime import datetime

from ..serializers import ApplicationOverviewSerializer
from ..models import Application,LoanDocument
from utils.responseHandler import HttpResponse
from utils.envSetup import environment
from utility.common_utils import custom_response_obj
from utility.frs.frs_helper import FrsHelper

import pdfkit
import datetime
import json
import requests
import num2words

class DpnPdfGeneration:

    def convert_number_to_words(self, number):
 
        rupees_words = num2words.num2words(int(number), lang='en_IN').replace(',', '')
        return f"{rupees_words}"

    def generate(self, application):

        try:
            applicationData = ApplicationOverviewSerializer(application)
            htmlData = applicationData.data
         
            # Extract the required fields for DPN
            
            htmlData["amount"] = htmlData['loan_amount']
            htmlData["Lender"] = f"{htmlData['account']['user']['first_name']} {htmlData['account']['user']['last_name']}",
            htmlData["amount_in_words"] = self.convert_number_to_words(htmlData['loan_amount']),
            htmlData["interest"] = htmlData['intrest_rate'],
            #htmlData["borrower_signature"] ='https://tse3.mm.bing.net/th?id=OIP.2OqeilssfIebKYb46WO7kQHaEm&pid=Api&P=0&h=180',  # Replace with self.get_document_url() if needed
            htmlData["place"] = htmlData['branch']['branch_name'],
            #htmlData["date"] = htmlData['created_at'],
            #htmlData["revenue_stamp"] = 'https://tse3.mm.bing.net/th?id=OIP.2OqeilssfIebKYb46WO7kQHaEm&pid=Api&P=0&h=180'  # Replace with self.get_document_url() if needed

            # Render the template
            template = get_template("dpn.html")
            html = template.render(htmlData)
        

            # Generate the PDF
            options = {
                "page-size": "A4",
                "margin-top": "5mm",
                "margin-right": "5mm",
                "margin-bottom": "5mm",
                "margin-left": "5mm",
                "enable-local-file-access": "",
                "encoding": "UTF-8",
            }

           
            pdf = pdfkit.from_string(html, False,options=options, configuration=pdfkit.configuration())
            return pdf

        except Application.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")
        except Exception as e:
            return HttpResponse.InternalServerError(f"Error generating PDF: {e}")

    
        
class DpnEsignUtil:


    def process_esign(self, application_id, user):
        application=self.__get_application_instance(application_id)
        if application is None:
            return custom_response_obj(message=f"Application with id {application} does not exist", code=404, error_code=400, error_msg=f"Application with id {application} does not exist")


        pdf=DpnPdfGeneration().generate(application)
        signature_config = "FIRST_PAGE_BOTTOM"


        rm_email=application.Originatedby.email
        customer_email=application.account.email


        if customer_email and customer_email.strip() != "":
            signatory_email = customer_email

        elif not customer_email and rm_email and rm_email.strip() != "":
            signatory_email = rm_email

        elif not rm_email or (rm_email and rm_email.strip() == ""):
            signatory_email = application.Originatedby.lm_branch_map.all().first().branch.email

        else:
            signatory_email = environment.DEFAULT_CPC_ADMIN_EMAIL

        sender_email=None
        if rm_email and rm_email.strip() != "":
            sender_email = rm_email

        elif not rm_email or (rm_email and rm_email.strip() == ""):
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
            loan_doc = LoanDocument.objects.get(application=application , document_type="SIGNED_DPN_DOCUMENT")
            # If exists, update the existing document
            loan_doc.esign_id = resp.get('data').get('id')
            loan_doc.esign_signature_link = resp.get('data').get('esign_url')[0]['signer_url']
            loan_doc.save()

        except ObjectDoesNotExist:
            # If not exists, create a new document
            if resp.get('status_code') == 200:
                loan_doc = LoanDocument(
                    document_type='SIGNED_DPN_DOCUMENT',
                    uploaded_by=user,
                    application=application,
                    esign_id=resp.get('data').get('id'),
                    esign_signature_link=resp.get('data').get('esign_url')[0]['signer_url']
                )
                loan_doc.save()

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

    def save_document(self, link, loan_doc):
        response = requests.get(link)
        if response.status_code == 200:
            file_content = response.content
            
            file_name = "{esign_id}-{type}.pdf".format(
                esign_id = loan_doc.esign_id,
                type = loan_doc.document_type,
            )
            loan_doc.file_name = file_name
            loan_doc.file.save(file_name, ContentFile(file_content))
            loan_doc.save()
