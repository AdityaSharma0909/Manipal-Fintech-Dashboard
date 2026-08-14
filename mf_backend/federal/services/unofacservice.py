import requests
from utils.envSetup import environment
from utility import common_utils
import json
import xmltodict
from federal.models import FederalBankApplication

class UNOFACService():
    
    def verifyUnOfac(fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_NAMECHECK_PATH
            print("url: ",url)
            # fba = FederalBankApplication.objects.get(application=borrower_application)
            payload,request_id = UNOFACService.createRequestPayload(fba)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending UNOFAC Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("UnoFac Response: ", response.text, "\n")
            response_dict = xmltodict.parse(response.text,process_namespaces=False)
            fba.unofac_meta_response = response_dict
            fba.save()
            if(response.status_code == 200 ):
                unofac_response = response_dict.get("ns3:Envelope").get("ns3:Body").get("ns2:Unchk")
                if(unofac_response.get("ns2:status") == "S"):
                    # fba.update(unchck_request_id=request_id,
                    #            unchck_status=unofac_response.get("ns2:status"),
                    #            unchk_msg=unofac_response.get("ns2:msg"),
                    #            unchk_first_name=unofac_response.get("ns2:FIRST_NAME"),
                    #            unchk_last_name=unofac_response.get("ns2:LAST_NAME"),
                    #            unchk_ind_address_note=unofac_response.get("ns2:IND_ADDRESS_NOTE"))
                    
                    fba.unchck_request_id=request_id
                    fba.unchck_status=unofac_response.get("ns2:status")
                    fba.unchk_msg=unofac_response.get("ns2:msg")
                    fba.unchk_first_name=unofac_response.get("ns2:FIRST_NAME")
                    fba.unchk_last_name=unofac_response.get("ns2:LAST_NAME")
                    fba.unchk_ind_address_note=unofac_response.get("ns2:IND_ADDRESS_NOTE")
                    fba.save()
                    
                    return {"is_eligible":True,"status":"success"}
                else:
                    return {"is_eligible":False,"status":"Error","message":unofac_response.get("ns2:msg")}         
            else:
                return {"is_eligible":False,"status":"Error","message":"Invalid Response from server, try again!"}
            
        except Exception as e:
            print(e)
            return {"is_eligible":False,"status":"Error","message":e}
            
    
    def createRequestPayload(fba):
        request_id=common_utils.getFederalReferenceID(fba.application.application_number,"UNOFAC")
        xml_body="<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">"+\
                    "<soapenv:Header/>"+\
                        "<soapenv:Body>"+\
                            "<firstname>"+fba.application.account.user.first_name+"</firstname>"+\
                            "<middlename></middlename>"+\
                            "<token_number>"+request_id+"</token_number>"+\
                            "<customernong>1</customernong>"+\
                            "<lastname>"+fba.application.account.user.last_name+"</lastname>"+\
                            "<custcorpname>?</custcorpname>"+\
                            "<panno>"+fba.application.account.pan_no+"</panno>"+\
                            "<msisdn>"+str(fba.application.account.user.phone).replace("+","")+"</msisdn>"+\
                            "<dob>"+str(fba.application.account.year_of_birth.strftime("%d-%b-%Y"))+"</dob>"+\
                        "</soapenv:Body>"+\
                    "</soapenv:Envelope>"
        return xml_body,request_id
    
        