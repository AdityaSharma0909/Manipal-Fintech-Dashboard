import requests
from utils.envSetup import environment
from utility import common_utils
import traceback
import xmltodict
import pytz
from django.utils import timezone
from federal.models import FederalBankApplication

class NameDobService():
    
    def verifyNameDob(fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_NAME_DOB_PATH
            print("url: ",url, "\n")
            # fba = FederalBankApplication.objects.get(application=borrower_application)
            payload = NameDobService.createRequestPayload(fba.application,fba)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending NameDob Validation Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("NameDob Response: ", response.text, "\n")
            if(response.status_code == 200 ):
                response_dict = xmltodict.parse(response.text,process_namespaces=False)
                fio_response = response_dict.get("ns3:Envelope").get("ns3:Body").get("ns2:fioekycbiooutput")
                fba.name_dob_request_id = fba.aadhar_rrn
                fba.name_dob_status = fio_response.get("ns2:status")
                fba.name_dob_desc = fio_response.get("ns2:description")
                fba.name_dob_meta_response = response_dict
                fba.save()
                # fba.update(name_dob_request_id=fba[0].aadhar_rrn,
                #            name_dob_status=fio_response.get("ns1:status"),
                #            name_dob_desc=fio_response.get("ns1:description"))
                if(fio_response.get("ns2:status") == "Y"):
                    return {"is_eligible":True,"status":"success"}
                else:
                    return {"is_eligible":False,"status":"Error"}         
            else:
                return {"is_eligible":False,"status":"Error","message":"Invalid Response from server, try again!"}
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"is_eligible":False,"status":"Error","message":str(e)}
            
    
    def createRequestPayload(borrower_application,fba):
        borrower_name = borrower_application.account.user.first_name +" "+ borrower_application.account.user.last_name
        dob = borrower_application.account.year_of_birth
        local_dob = timezone.localtime(dob, pytz.timezone('Asia/Kolkata'))
        fdt = local_dob.strftime("%d-%m-%Y")

        xml_body="<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\""+\
                    " xmlns:fio=\"http://www.fiorano.com/services/fioekycbioinputService\">"+\
                    "<soapenv:Header/>"+\
                        "<soapenv:Body>"+\
                            "<fio:fioekycbioinput>"+\
                                "<fio:requestid>"+fba.aadhar_rrn+"</fio:requestid>"+\
                                "<fio:customer_name>"+borrower_name+"</fio:customer_name>"+\
                                "<fio:customer_dob>"+fdt+"</fio:customer_dob>"+\
                                "<fio:reserve1></fio:reserve1>"+\
                                "<fio:reserve2></fio:reserve2>"+\
                                "<fio:reserve3></fio:reserve3>"+\
                                "<fio:reserve4></fio:reserve4>"+\
                                "<fio:reserve5></fio:reserve5>"+\
                                "<fio:reserve6></fio:reserve6>"+\
                                "<fio:reserve7></fio:reserve7>"+\
                                "<fio:reserve8></fio:reserve8>"+\
                                "<fio:reserve9></fio:reserve9>"+\
                                "<fio:reserve10></fio:reserve10>"+\
                            "</fio:fioekycbioinput>"+\
                        "</soapenv:Body>"+\
                    "</soapenv:Envelope>"
        return xml_body
    
        