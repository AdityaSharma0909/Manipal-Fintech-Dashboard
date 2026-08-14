import requests
from utils.envSetup import environment
from utility import common_utils
import datetime
import xmltodict
from federal.models import FederalBankApplication

class PanService():
    
    def verifyPanNumber(fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_PAN_PATH
            print("url: ",url, "\n")
            # fba = FederalBankApplication.objects.get(application=borrower_application)
            payload,referenceId = PanService.createRequestPayload(fba)
            print('#################################',referenceId)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending PAN Validation Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("Pan Validation Response: ", response.text, "\n")
            response_dict = xmltodict.parse(response.text,process_namespaces=False)
            fba.pan_validation_meta_response = response_dict
            fba.save()
            if(response.status_code == 200 ):
                pan_response = response_dict.get("soapenv:Envelope").get("soapenv:Body").get("NS1:PANResponse")
                pan_details = pan_response.get("PANDetails")
                lastUpdateDate = datetime.datetime.strptime(pan_details.get("LastUpdateDate"), '%d/%m/%Y').date()

                # fba.update(pan_request_id=referenceId,
                #            pan_response_code=pan_response.get("ResponseCode"),
                #            pan=pan_details.get("PAN"),
                #            pan_status=pan_details.get("PANStatus"),
                #            last_name=pan_details.get("LastName"),
                #            first_name=pan_details.get("FirstName"),
                #            pan_title=pan_details.get("PANTitle"),
                #            last_update_date=lastUpdateDate,
                #            name_on_card=pan_details.get("NameOnCard"),
                #            aadhar_seeded_Status=pan_details.get("AadhaarSeededStatus"),)
                

                fba.pan_request_id=referenceId
                fba.pan_response_code=pan_response.get("ResponseCode")
                fba.pan=pan_details.get("PAN")
                fba.pan_status=pan_details.get("PANStatus")
                fba.last_name=pan_details.get("LastName")
                fba.first_name=pan_details.get("FirstName")
                fba.pan_title=pan_details.get("PANTitle")
                fba.last_update_date=lastUpdateDate
                fba.name_on_card=pan_details.get("NameOnCard")
                fba.aadhar_seeded_Status=pan_details.get("AadhaarSeededStatus")
                fba.save()

                if(pan_response.get("ResponseCode") == "1"):
                    return {"is_eligible":True,"status":"success","pan_details":pan_response.get("PANDetails")}
                else:
                    return {"is_eligible":False,"status":"Error","message":pan_response.get("ResponseDesc")}         
            else:
                return {"is_eligible":False,"status":"Error","message":"Invalid Response from server, try again!"}
            
        except Exception as e:
            print(e)
            return {"is_eligible":False,"status":"Error","message":str(e)}
            
    
    def createRequestPayload(fba: FederalBankApplication):
        pan_no = fba.application.account.pan_no
        reference_id = common_utils.getFederalReferenceID(fba.application.application_number,"PAN")

        xml_body="<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:in=\"in.co.federalbank\">" +\
                    "<soapenv:Header/>"+\
                        "<soapenv:Body>"+\
                            "<in:PANRequest>"+\
                                "<ChannelID>"+environment.FEDERAL_UAT_CHANNEL_ID+"</ChannelID>"+\
                                "<AccessId>"+environment.FEDERAL_UAT_USERNAME+"</AccessId>"+\
                                "<AccessCode>"+environment.FEDERAL_UAT_PAN_PASSWORD+"</AccessCode>"+\
                                "<RequestID>"+reference_id+"</RequestID>"+\
                                "<PAN1>"+pan_no+"</PAN1>"+\
                                "<PAN2></PAN2>"+\
                                "<PAN3></PAN3>"+\
                                "<PAN4></PAN4>"+\
                                "<PAN5></PAN5>"+\
                            "</in:PANRequest>"+\
                        "</soapenv:Body>"+\
                    "</soapenv:Envelope>"
        return xml_body,reference_id
    
        