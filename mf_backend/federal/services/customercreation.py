import requests
from utils.envSetup import environment
from utility import common_utils
from ..services import utilitysevrice
import traceback
import xmltodict
import base64

from users.models import Address
from utils.constants import ADDRESS_TYPE

class CustomerCreation():
    
    def createCustomer(borrower_application,fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_CUSTOMER_CREATION_PATH
            print("url: ",url)
            
            payload = CustomerCreation.createRequestPayload(borrower_application,fba)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending CIF Customer Creation Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("CIF Customer Creation Response: ", response.text, "\n")
            if(response.status_code == 200 ):
                response_dict = xmltodict.parse(response.text,process_namespaces=False)
                return response_dict
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"is_eligible":False,"status":"Error","message":str(e)}
            
    
    def createRequestPayload(borrower_application,fba):
        pan_no = borrower_application.account.pan_no
        reference_id = common_utils.getFederalReferenceID(borrower_application.application_number,"CIF")
        gender = "M" if borrower_application.account.gender == "MALE" else "F"
        marital_status = "SING" if borrower_application.account.maritial_status else "MARD"
        # fba = fba[0]
        account = fba.account

        encoded_sign_id = base64.b64encode(fba.sign_id.read()).decode()

        current_address = Address()
        current_state_code = ""
        current_city_code = ""
        current_address_pincode = ""
        permenant_address = Address()
        permenant_city_code = ""
        permenant_state_code = ""
        permenant_address_pincode=""
        addresses = Address.objects.filter(account=account)
        for address in addresses:
            if address.address_type == ADDRESS_TYPE.CORRESPONDENCE_ADDRESS.value:
                current_address=address
                current_state_code = utilitysevrice.getStateCode(address.state)
                current_city_code = utilitysevrice.getCityCode(address.city)
                current_address_pincode = current_address.pincode if current_address.pincode != None else " "
            elif address.address_type == ADDRESS_TYPE.PERMANENT_ADDRESS.value:
                permenant_address = address
                permenant_city_code = utilitysevrice.getCityCode(address.city)
                permenant_state_code = utilitysevrice.getStateCode(address.state)
                permenant_address_pincode = permenant_address.pincode if permenant_address.pincode != None else " "
                
        xml_body="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+\
                    "<Cif_Creation>"+\
                        "<SenderCredentials>"+\
                            "<UserAccessId>"+environment.FEDERAL_UAT_USER_ID+"</UserAccessId>"+\
                            "<UserAccessCode>"+environment.FEDERL_UAT_USER_ACCESS_CODE+"</UserAccessCode>"+\
                            "<SenderCode>"+environment.FEDERAL_UAT_CHANNEL_ID+"</SenderCode>"+\
                        "</SenderCredentials>"+\
                        "<Cif_Request>"+\
                            "<RequestId>"+reference_id+"</RequestId>"+\
                            "<SolId>1001</SolId>"+\
                            "<BRERefNum> </BRERefNum>"+\
                            "<Personal_Details>"+\
                                "<Title>Mr</Title>"+\
                                "<FirstName>"+str(borrower_application.account.user.first_name)+"</FirstName>"+\
                                "<MiddleName></MiddleName>"+\
                                "<LastName>"+str(borrower_application.account.user.last_name)+"</LastName>"+\
                                "<FatherName>"+str(borrower_application.account.father_name)+"</FatherName>"+\
                                "<MotherName>"+str(borrower_application.account.mother_name)+"</MotherName>"+\
                                "<DateOfBirth>"+str(borrower_application.account.year_of_birth.strftime("%Y-%m-%d"))+"</DateOfBirth>"+\
                                "<Gender>"+str(gender)+"</Gender>"+\
                                "<MaritalStatus>"+str(marital_status)+"</MaritalStatus>"+\
                                "<Uid_No>"+str(fba.aadhar_rrn)+"</Uid_No>"+\
                            "</Personal_Details>"+\
                            "<Contact_Details>"+\
                                "<Mobile>"+str(borrower_application.account.user.phone).replace("+","")+"</Mobile>"+\
                                "<Email>"+str(borrower_application.account.email)+"</Email>"+\
                                "<Communication_Address>"+\
                                    "<House></House>"+\
                                    "<Place>"+str(current_address.street_name)+"</Place>"+\
                                    "<City_Cd>"+str(current_city_code)+"</City_Cd>"+\
                                    "<State_Cd>"+str(current_state_code)+"</State_Cd>"+\
                                    "<Country_Cd>IN</Country_Cd>"+\
                                    "<PinCode>"+str(current_address_pincode)+"</PinCode>"+\
                                    "<LandLine></LandLine>"+\
                                    "</Communication_Address>"+\
                                    "<CA_Sameas_PA>N</CA_Sameas_PA>"+\
                                "<Permanent_Address>"+\
                                    "<House></House>"+\
                                    "<Place>"+str(permenant_address.street_name)+"</Place>"+\
                                    "<City_Cd>"+str(permenant_city_code)+"</City_Cd>"+\
                                    "<State_Cd>"+str(permenant_state_code)+"</State_Cd>"+\
                                    "<Country_Cd>IN</Country_Cd>"+\
                                    "<PinCode>"+str(permenant_address_pincode)+"</PinCode>"+\
                                    "<LandLine></LandLine>"+\
                                "</Permanent_Address>"+\
                            "</Contact_Details>"+\
                            "<Additional_Details>"+\
                                "<AnnualIncome>1200</AnnualIncome>"+\
                                "<PanNo>"+str(pan_no)+"</PanNo>"+\
                                "<Religion>"+str(borrower_application.account.religion)+"</Religion>"+\
                                "<Community>HI</Community>"+\
                                "<Qualification>PRF</Qualification>"+\
                                "<Occupation>MERCH</Occupation>"+\
                                "<Form60>N</Form60>"+\
                                "<TaxSlab>TDSI</TaxSlab>"+\
                                "<Employement>Other</Employement>"+\
                                "<EmployerName>EIDIKO</EmployerName>"+\
                                "<Designation>CEO</Designation>"+\
                                "<WorkPlace>HYDERABAD</WorkPlace>"+\
                                "<EmployerType>PVT</EmployerType>"+\
                                "<SpouseNme>Radha</SpouseNme>"+\
                                "<SpouseOcupation>Housewife</SpouseOcupation>"+\
                                "<SpouseDesig>CEO</SpouseDesig>"+\
                                "<NoOfChild>0</NoOfChild>"+\
                                "<NoOfDependents>7</NoOfDependents>"+\
                                "<Networth>2500000</Networth>"+\
                            "</Additional_Details>"+\
                            "<Identification_Details>"+\
                                "<ProofOfIdentity>"+\
                                    "<Type>AADHA</Type>"+\
                                    "<Id_Number>"+fba.aadhar_rrn+"</Id_Number>"+\
                                "</ProofOfIdentity>"+\
                                "<ProofOfAddress>"+\
                                    "<Type>AADHA</Type>"+\
                                    "<Id_Number>"+fba.aadhar_rrn+"</Id_Number>"+\
                                "</ProofOfAddress>"+\
                            "</Identification_Details>"+\
                            "<Sign_Id>"+encoded_sign_id+"</Sign_Id>"+\
                        "</Cif_Request>"+\
                    "</Cif_Creation>"
        return xml_body
    
    
    def customerEnquiry(reference_id):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_CUSTOMER_ENQUIRY_PATH
            print("url: ",url)
            
            payload = "<CifEnqReq>"+\
                        "<SenderDetails>"+\
                            "<UserAccessId>"+environment.FEDERAL_UAT_USER_ID+"</UserAccessId>"+\
                            "<UserAccessCode>"+environment.FEDERL_UAT_USER_ACCESS_CODE+"</UserAccessCode>"+\
                            "<SenderCode>"+environment.FEDERAL_UAT_CHANNEL_ID+"</SenderCode>"+\
                        "</SenderDetails>"+\
                        "<RequestId>"+"01"+reference_id+"</RequestId>"+\
                        "<CifRequestId>"+reference_id+"</CifRequestId>"+\
                        "</CifEnqReq>"
            print(payload)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Request: ",payload)
            print("headers: ",headers)
            print("Sending CIF Creation Request...")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print(response.text)
            if(response.status_code == 200 ):
                response_dict = xmltodict.parse(response.text,process_namespaces=False)
                return response_dict
            
        except Exception as e:
            print(e)
            return {"is_eligible":False,"status":"Error","message":e}
    