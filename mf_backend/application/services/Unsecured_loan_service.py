from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from dateutil.relativedelta import relativedelta

from ..serializers import ApplicationOverviewSerializer
from application.service import ApplicationService
from ..models import Application,LoanDocument
from utils.responseHandler import HttpResponse
from utils.envSetup import environment
from utility.common_utils import custom_response_obj
from utility.frs.frs_helper import FrsHelper

import pdfkit
import datetime
import json
import requests

class UnsecuredLoanPdfGeneration:
    
    def generate(self, application):
        try:
            applicationData = ApplicationOverviewSerializer(application)
            htmlData = applicationData.data

            # Extract and set user information
            htmlData["name"] = htmlData['account']['user']['first_name'] + " " + htmlData['account']['user']['last_name']
            htmlData["gender"] = htmlData['account']['gender'].lower()
            print(htmlData["gender"])

            # Determine salutation based on gender and marital status
            if htmlData['account']['gender'].lower() == 'male':
                htmlData["salutation"] = 'male'
            elif htmlData['account']['gender'].lower() == 'female' and htmlData['account']['maritial_status'].lower() == 'married':
                htmlData["salutation"] = 'female'
            elif htmlData['account']['gender'].lower() == 'female' and htmlData['account']['maritial_status'].lower() == 'single':
                htmlData["salutation"] = 'unmarried'
            else:
                htmlData["salutation"] = 'other'
            print(htmlData["salutation"])

            dob = datetime.datetime.strptime(htmlData['account']['year_of_birth'].split("T")[0], "%Y-%m-%d")
            htmlData["dob"] = ApplicationService().format_date(
                htmlData['account']['year_of_birth'].split("T")[0]
            )
            print( htmlData["dob"])
            today = datetime.date.today()
            years = today.year - dob.year
            months = today.month - dob.month
            months = abs(months)

            htmlData["age_yrs"] = years
            print( htmlData["age_yrs"])
            htmlData["age_month"] = months
            print( htmlData["age_month"])
            htmlData["marital_status"]= htmlData['account']['maritial_status'].lower()
            print(htmlData["marital_status"])
            htmlData["husband_name"]= htmlData['account']['spouse_name']
            print(htmlData["husband_name"])
            # htmlData["children_no"]= htmlData['account']['maritial_status']
            # htmlData["dependents_no"]= htmlData['account']['maritial_status']
            htmlData["father_name"]= htmlData['account']['father_name']
            print(htmlData["father_name"])
            htmlData["mother_maiden_name"]= htmlData['account']['mother_name']
            print(htmlData["mother_maiden_name"])
            htmlData["nationality"]= htmlData['account']['nationality']
            print(htmlData["nationality"])
            #htmlData["residential_status"]= htmlData['account']['maritial_status']
            #htmlData["country"]= htmlData['account']['maritial_status']
            htmlData["religion"]= htmlData['account']['religion']
            print(htmlData["religion"])
            # htmlData["category"]= htmlData['account']['maritial_status']
            # htmlData["minority_details"]= htmlData['account']['maritial_status']
            # htmlData["place_of_birth"]= htmlData['account']['maritial_status']

            htmlData["id_type"]= 'Aadhar'
            htmlData["id_no"]= htmlData['account']['aadhar_no']
            print(htmlData["id_no"])
            # htmlData["id_valid_upto"]= htmlData['account']['maritial_status']
            # htmlData["driving_license_no"]= htmlData['account']['maritial_status']
            # htmlData["driving_license_valid_upto"]= htmlData['account']['maritial_status']
            # htmlData["passport_no"]= htmlData['account']['maritial_status']
            # htmlData["passport_valid_upto"]= htmlData['account']['maritial_status']
            htmlData["pan_no"]= htmlData['account']['pan_no']
            print(htmlData["pan_no"])
            htmlData["aadhar_no"]= htmlData['account']['aadhar_no']
            print(htmlData["aadhar_no"])
            htmlData["educational_qualification"]= htmlData['account']['education']
            print(htmlData["educational_qualification"])
            # htmlData["social_media"]= htmlData['account']['maritial_status']

            # htmlData["id_address"]= htmlData['account']['maritial_status']
            # htmlData["present_years"]= htmlData['account']['maritial_status']
            # htmlData["present_months"]= htmlData['account']['maritial_status']

            # Extract address data
            address = {}
            for i in htmlData["account"]["address"]:
                i = dict(i)
                i["address_type"] = i["address_type"].split("_")[0]
                address[i["address_type"]] = i

            htmlData["address"] = address

            # Extracting permanent address
            htmlData[
                "p_address"
            ] = f"{address['PERMANENT']['building_name']} {address['PERMANENT']['street_name']} {address['PERMANENT']['city']} {address['PERMANENT']['state']} {address['PERMANENT']['pincode']} {address['PERMANENT']['country']}"

            # Extracting correspondence address
            htmlData[
                "c_address"
            ] = f"{address['CORRESPONDENCE']['building_name']} {address['CORRESPONDENCE']['street_name']} {address['CORRESPONDENCE']['city']} {address['CORRESPONDENCE']['state']} {address['CORRESPONDENCE']['pincode']} {address['CORRESPONDENCE']['country']}"

            # Extracting residential ownership details
            htmlData[
                "p_residential_ownership"
            ] = f"{address['PERMANENT']['residential_ownership']}"

            htmlData[
                "c_residential_ownership"
            ] = f"{address['CORRESPONDENCE']['residential_ownership']}"

            # Updating htmlData with permanent address fields
            if address['CORRESPONDENCE']['residential_ownership'] == "INDIVIDUAL_OWNERSHIP":
                htmlData["type_of_residence"] = 'owned'
            else:
                htmlData["type_of_residence"] = 'rented'
            print(htmlData["type_of_residence"])
            # htmlData["type_of_residence"] = address['PERMANENT'].get('residential_ownership', '')
            htmlData["present_flat_no_name"] = address['CORRESPONDENCE']['building_name']
            print(htmlData["present_flat_no_name"])
            htmlData["present_street_no_name"] = address['CORRESPONDENCE']['street_name']
            print(htmlData["present_street_no_name"])
            # htmlData["present_area_name"] = address['PERMANENT']['area_name']
            # print(htmlData["present_flat_no_name"])
            # htmlData["present_landmark"] = address['PERMANENT'].get('landmark', '')
            htmlData["present_city"] = address['CORRESPONDENCE']['city']
            print(htmlData["present_city"])
            # htmlData["present_district"] = address['PERMANENT'].get('district', '')
            htmlData["present_pin_code"] = address['CORRESPONDENCE']['pincode']
            print(htmlData["present_pin_code"])
            htmlData["present_state"] = address['CORRESPONDENCE']['state']
            print(htmlData["present_state"])
            htmlData["present_country"] = address['CORRESPONDENCE']['country']
            print(htmlData["present_country"])

            # htmlData["present_landline"]= htmlData['account']['maritial_status']
            htmlData["present_mobile"]= htmlData['account']['user']['phone']
            print(htmlData["present_mobile"])
            # htmlData["present_mobile2"]= htmlData['account']['maritial_status']
            htmlData["present_email"]= htmlData['account']['email']
            print(htmlData["present_email"])

            # htmlData["present_same_permanent"]= htmlData['account']['maritial_status']

            # htmlData["permanent_flat_no_name"]= htmlData['account']['maritial_status']
            # htmlData["permanent_street_no_name"]= htmlData['account']['maritial_status']
            # htmlData["permanent_area_name"]= htmlData['account']['maritial_status']
            # htmlData["permanent_landmark"]= htmlData['account']['maritial_status']
            # htmlData["permanent_city"]= htmlData['account']['maritial_status']
            # htmlData["permanent_district"]= htmlData['account']['maritial_status']
            # htmlData["permanent_pin_code"]= htmlData['account']['maritial_status']
            # htmlData["permanent_state"]= htmlData['account']['maritial_status']
            # htmlData["permanent_country"]= htmlData['account']['maritial_status']
            # htmlData["permanent_landline"]= htmlData['account']['maritial_status']
            # htmlData["permanent_mobile"]= htmlData['account']['maritial_status']
            # htmlData["permanent_mobile2"]= htmlData['account']['maritial_status']
            # htmlData["permanent_email"]= htmlData['account']['maritial_status']

            # htmlData["office_name"]= htmlData['account']['maritial_status']
            htmlData["office_dept"]= address['PERMANENT']['building_name']
            print(htmlData["office_dept"])
            htmlData["office_street_no_name"]= address['PERMANENT']['street_name']
            print(htmlData["office_street_no_name"])
            # htmlData["office_area_name"]= htmlData['account']['maritial_status']
            # htmlData["office_landmark"]= htmlData['account']['maritial_status']
            htmlData["office_city"]= address['PERMANENT']['city']
            print(htmlData["office_city"])
            # htmlData["office_district"]= htmlData['account']['maritial_status']
            htmlData["office_pin_code"]= address['PERMANENT']['pincode']
            print(htmlData["office_pin_code"])
            htmlData["office_state"]= address['PERMANENT']['state']
            print(htmlData["office_state"])
            htmlData["office_country"]= address['PERMANENT']['country']  
            print(htmlData["office_country"])      
            # htmlData["office_landline"]= htmlData['account']['maritial_status']
            # htmlData["office_mobile"]= htmlData['account']['maritial_status']
            # htmlData["office_mobile2"]= htmlData['account']['maritial_status']
            # htmlData["office_email"]= htmlData['account']['maritial_status']
            
            # htmlData["repayment_mode"]= htmlData['account']['maritial_status']
            # htmlData["bank_relationship"]= htmlData['account']['maritial_status']
            # htmlData["applicant_signature"]= htmlData['account']['maritial_status']
            # htmlData["occupation"]= htmlData['account']['maritial_status']
            # htmlData["employer_name"]= htmlData['account']['maritial_status']
            # htmlData["employment_status"]= htmlData['account']['maritial_status']
            # htmlData["employer_address"]= htmlData['account']['maritial_status']
            # htmlData["employer_mobile"]= htmlData['account']['maritial_status']
            # htmlData["present_job_yrs"]= htmlData['account']['maritial_status']
            # htmlData["present_job_mon"]= htmlData['account']['maritial_status']
            # htmlData["past_job_yrs"]= htmlData['account']['maritial_status']
            # htmlData["past_job_mon"]= htmlData['account']['maritial_status']
            # htmlData["past_employer_address"]= htmlData['account']['maritial_status']
            # htmlData["past_employer_mobile"]= htmlData['account']['maritial_status']
            # htmlData["organization_type"]= htmlData['account']['maritial_status']
            # htmlData["department"]= htmlData['account']['maritial_status']
            # htmlData["designation"]= htmlData['account']['maritial_status']
            # htmlData["employee_no"]= htmlData['account']['maritial_status']
            # htmlData["remaining_yrs"]= htmlData['account']['maritial_status']
            # htmlData["remaining_months"]= htmlData['account']['maritial_status']
            # htmlData["retirement_date"]= htmlData['account']['maritial_status']
            # htmlData["website"]= htmlData['account']['maritial_status']
            # htmlData["total_land"]= htmlData['account']['maritial_status']
            # htmlData["presently_irrigated_land"]= htmlData['account']['maritial_status']
            # htmlData["seasonally_irrigated_land"]= htmlData['account']['maritial_status']
            # htmlData["rain_fed_land"]= htmlData['account']['maritial_status']
            # htmlData["allied_activities"]= htmlData['account']['maritial_status']
            # htmlData["other_specify"]= htmlData['account']['maritial_status']
            # htmlData["nature_of_business"]= htmlData['account']['maritial_status']
            # htmlData["nob_other"]= htmlData['account']['maritial_status']
            # htmlData["business_name"]= htmlData['account']['maritial_status']
            # htmlData["industry"]= htmlData['account']['maritial_status']
            # htmlData["business_address"]= htmlData['account']['maritial_status']
            # htmlData["trade_licence_no"]= htmlData['account']['maritial_status']
            # htmlData["trade_licence_expiry_date"]= htmlData['account']['maritial_status']
            # htmlData["share_holding"]= htmlData['account']['maritial_status']
            # htmlData["business_reg_no"]= htmlData['account']['maritial_status']
            # htmlData["gross_salary"]= htmlData['account']['maritial_status']
            # htmlData["net_salary"]= htmlData['account']['maritial_status']
            # htmlData["frequency_salary"]= htmlData['account']['maritial_status']
            # htmlData["mop_salary"]= htmlData['account']['maritial_status']
            # htmlData["gross_business"]= htmlData['account']['maritial_status']
            # htmlData["net_business"]= htmlData['account']['maritial_status']
            # htmlData["frequency_business"]= htmlData['account']['maritial_status']
            # htmlData["mop_business"]= htmlData['account']['maritial_status']
            # htmlData["gross_rent"]= htmlData['account']['maritial_status']
            # htmlData["net_rent"]= htmlData['account']['maritial_status']
            # htmlData["frequency_rent"]= htmlData['account']['maritial_status']
            # htmlData["mop_rent"]= htmlData['account']['maritial_status']
            # htmlData["gross_agriculture"]= htmlData['account']['maritial_status']
            # htmlData["net_agriculture"]= htmlData['account']['maritial_status']
            # htmlData["frequency_agriculture"]= htmlData['account']['maritial_status']
            # htmlData["mop_agriculture"]= htmlData['account']['maritial_status']
            # htmlData["gross_other"]= htmlData['account']['maritial_status']
            # htmlData["net_other"]= htmlData['account']['maritial_status']
            # htmlData["frequency_other"]= htmlData['account']['maritial_status']
            # htmlData["mop_other"]= htmlData['account']['maritial_status']
            # htmlData["tax_gross_deduction"]= htmlData['account']['maritial_status']
            # htmlData["tax_net_deduction"]= htmlData['account']['maritial_status']
            # htmlData["tax_frequency_deduction"]= htmlData['account']['maritial_status']
            # htmlData["tax_remark_deduction"]= htmlData['account']['maritial_status']
            # htmlData["other_gross_deduction"]= htmlData['account']['maritial_status']
            # htmlData["other_net_deduction"]= htmlData['account']['maritial_status']
            # htmlData["other_frequency_deduction"]= htmlData['account']['maritial_status']
            # htmlData["other_remark_deduction"]= htmlData['account']['maritial_status']
            # htmlData["salary_income"]= htmlData['account']['maritial_status']
            # htmlData["date"]= datetime.now().strftime("%Y-%m-%d")
            
            # htmlData["applicant_passport"]= htmlData['account']['maritial_status']

            template = get_template("unsecured_application.html")
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


            pdf = pdfkit.from_string(html, False, options=options, configuration=pdfkit.configuration())

           
            return pdf
        
        except Application.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")
        except Exception as e:
            return HttpResponse.InternalServerError(f"Error generating PDF: {e}")
        

class UnsecuredLoanEsignUtil:


    def process_esign(self, application_id, user):
        application=self.__get_application_instance(application_id)
        if application is None:
            return custom_response_obj(message=f"Application with id {application} does not exist", code=404, error_code=400, error_msg=f"Application with id {application} does not exist")


        pdf=UnsecuredLoanPdfGeneration().generate(application)
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
            loan_doc = LoanDocument.objects.get(application=application,document_type='SIGNED_UNSECURED_LOAN_DOCUMENT')
            # If exists, update the existing document
            loan_doc.esign_id = resp.get('data').get('id')
            loan_doc.esign_signature_link = resp.get('data').get('esign_url')[0]['signer_url']
            loan_doc.save()
        except ObjectDoesNotExist:
            # If not exists, create a new document
            if resp.get('status_code') == 200:
                loan_doc = LoanDocument(
                    document_type='SIGNED_UNSECURED_LOAN_DOCUMENT',
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





