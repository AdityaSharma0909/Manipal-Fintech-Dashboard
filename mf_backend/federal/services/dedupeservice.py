import requests
from application.models import Application
from federal.models import FederalBankApplication
from utils.envSetup import environment
import json
import time
from utility import common_utils

class DedupeService():
    
    def fetchDedupe(self,fba):
        
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_DEDUPE_PATH
            print("url: ",url)
            
            # fba = FederalBankApplication.objects.get(application=borrower_application)
            payload = json.dumps(self.__dict__)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            'Content-Type': 'application/json',
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending DeDupe Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("DeDupe Response: ", response.text, "\n")
            response_dict = response.json()
            fba.dedupe_meta_response = response_dict
            fba.save()
            if(response.status_code == 200 ):
                # response_dict = json.loads(response.text)
                #{'ddupe_flag': 'Y', 'kyc_flag': 'Y', 'kyc_profile_flag': 'Y', 'partial_kyc_flag': 'N', 'dob_flag': 'N', 'mobile_flag': 'Y', 'customer_id': None, 'customer_name': None, 'nri_flag': 'N', 'minor_flag': 'N', 'reserve_field1': None, 'reserve_field2': '1', 'reserve_field3': 'IND', 'reserve_field4': None, 'reserve_field5': 'N', 'reserve_field6': 'N', 'reserve_field7': None, 'reserve_field8': None, 'reserve_field9': '0', 'reserve_field10': None, 'reference_id': 'RAD4896DD1699360211113'}
                # fba.update(ddupe_request_id=response_dict.get("reference_id",""),
                #            ddupe_flag=response_dict.get("ddupe_flag",""),
                #            kyc_flag=response_dict.get("kyc_flag",""),
                #            kyc_profile_flag=response_dict.get("kyc_profile_flag",""),
                #            partial_kyc_flag=response_dict.get("partial_kyc_flag",""),
                #            dob_flag=response_dict.get("dob_flag",""),
                #            mobile_flag=response_dict.get("mobile_flag",""),
                #            customer_id=response_dict.get("customer_id",""),
                #            customer_name=response_dict.get("customer_name",""),
                #            nri_flag=response_dict.get("nri_flag",""),
                #            minor_flag=response_dict.get("minor_flag",""),
                #            reserve_field1=response_dict.get("reserve_field1",""),
                #            reserve_field2=response_dict.get("reserve_field2",""),
                #            reserve_field3=response_dict.get("reserve_field3",""),
                #            reserve_field4=response_dict.get("reserve_field4",""),
                #            reserve_field5=response_dict.get("reserve_field5",""),
                #            reserve_field6=response_dict.get("reserve_field6",""),
                #            reserve_field7=response_dict.get("reserve_field7",""),
                #            reserve_field8=response_dict.get("reserve_field8",""),
                #            reserve_field9=response_dict.get("reserve_field8",""),
                #            reserve_field10=response_dict.get("reserve_field8",""),
                #            ddupe_reference_id=response_dict.get("reference_id",""))
                
                fba.ddupe_request_id=response_dict.get("reference_id","")
                fba.ddupe_flag=response_dict.get("ddupe_flag","")
                fba.kyc_flag=response_dict.get("kyc_flag","")
                fba.kyc_profile_flag=response_dict.get("kyc_profile_flag","")
                fba.partial_kyc_flag=response_dict.get("partial_kyc_flag","")
                fba.dob_flag=response_dict.get("dob_flag","")
                fba.mobile_flag=response_dict.get("mobile_flag","")
                fba.customer_id=response_dict.get("customer_id","")
                fba.customer_name=response_dict.get("customer_name","")
                fba.nri_flag=response_dict.get("nri_flag","")
                fba.minor_flag=response_dict.get("minor_flag","")
                fba.reserve_field1=response_dict.get("reserve_field1","")
                fba.reserve_field2=response_dict.get("reserve_field2","")
                fba.reserve_field3=response_dict.get("reserve_field3","")
                fba.reserve_field4=response_dict.get("reserve_field4","")
                fba.reserve_field5=response_dict.get("reserve_field5","")
                fba.reserve_field6=response_dict.get("reserve_field6","")
                fba.reserve_field7=response_dict.get("reserve_field7","")
                fba.reserve_field8=response_dict.get("reserve_field8","")
                fba.reserve_field9=response_dict.get("reserve_field8","")
                fba.reserve_field10=response_dict.get("reserve_field8","")
                fba.ddupe_reference_id=response_dict.get("reference_id","")
                fba.save()
                

                if(response_dict.get("Error",None) == None):
                    dedupe_flag = response_dict.get("ddupe_flag")
                    if(dedupe_flag == "N"):
                        return {"is_eligible":True,"is_existing_customer":False,"status":"success"}
                    elif (dedupe_flag=="Y" and response_dict.get("kyc_profile_flag") == "Y" and 
                          response_dict.get("kyc_flag") == "Y" and not response_dict.get("reserve_field7") == "N"):
                        return {"is_eligible":True,"is_existing_customer":True,"status":"success"}
                    elif(dedupe_flag=="Y" and response_dict.get("reserve_field7") == "N"):
                        return {"is_eligible":False,"is_existing_customer":True,"status":"success"}
                    else:
                        return {"is_eligible":False,"is_existing_customer":False,"status":"success"}
                else:
                    return {"is_eligible":False,"is_existing_customer":False,"status":"Error","message":response_dict.get("Error")}
            else:
                return {"is_eligible":False,"is_existing_customer":False,"status":"Error","message":"Invalid Response from server, try again!"}
        except Exception as e:
            print(e)
            return {"is_eligible":False,"is_existing_customer":False,"status":"Error","message":str(e)}
            
    
    def __init__(self,fba: FederalBankApplication):
        service_code = "DD"
        self.reference_id=common_utils.getFederalReferenceID(fba.application.application_number,service_code)
        self.pan_number=fba.application.account.pan_no
        self.mobile_num=str(fba.application.account.user.phone).replace("+","")
        self.dob=str(fba.application.account.year_of_birth.strftime("%d-%b-%Y"))
        self.aadhaar_number=""
        self.passport_number=""
        self.driving_license=""
        self.voter_id=""
        self.res_field1=fba.aadhar_rrn
        self.res_field2=""
        self.res_field3=""
        self.res_field4=""
        self.res_field5=""
        self.res_field6=""
        self.res_field7=""
        self.res_field8=""
        self.res_field9=""
        self.res_field10=""
        self.user_id=environment.FEDERAL_UAT_USER_ID
        
   
    
        