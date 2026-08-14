import requests
from utils.envSetup import environment
from utility import common_utils
from federal.models import FederalBankApplication
from application.models import Application
from utils.constants import AMORTIZATIONTYPE
from collections import Counter
import xmltodict
import datetime
import json
import traceback
from time import time
import base64
import re


def getFederalAssetType(radianAsset):
    radianAsset = radianAsset.lower()

    if radianAsset == 'bangles':
        federalAsset = 'BANGLE'

    elif radianAsset == 'finger_ring':
        federalAsset = 'RING'

    elif radianAsset == 'chain' or radianAsset == 'chain_with_locket' or radianAsset == 'black_beads_chain':
        federalAsset = 'CHAIN'

    elif radianAsset == 'earings' or radianAsset == 'jhumka':
        federalAsset = 'EAR RING'

    elif radianAsset == 'anklet':
        federalAsset = 'ANKLET'

    elif radianAsset == 'necklace':
        federalAsset = 'NECKLACE'

    elif radianAsset == 'bracelet':
        federalAsset = 'BRACELET'

    elif radianAsset == 'belly_chain':
        federalAsset = 'HIP CHAIN'

    elif radianAsset == 'hair_ornaments':
        federalAsset = 'OTHER'

    elif radianAsset == 'pendant':
        federalAsset = 'OTHER'

    elif radianAsset == 'gemstone_jeweler':
        federalAsset = 'OTHER'

    elif radianAsset == 'mens_kada':
        federalAsset = 'OTHER'

    elif radianAsset == 'Matti' or radianAsset == 'matti' or radianAsset == 'studs(with_stone)' or radianAsset == 'long_chain_(womens)':
        federalAsset = 'OTHER'

    else:
        federalAsset = 'OTHER'

    return federalAsset



class GLAccountService():

    def sendAccountDetails(self, fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_GL_ACCOUNT_INSERT
            payload = self.createRequestPayload(fba)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            print("Account Insert Request...")
            print(url)
            # json_object = json.dumps(payload, indent=4)
            # with open("gl_insert_api_body.json", "w") as outfile:
            #     outfile.write(json_object)
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, json=payload, cert=environment.FEDERAL_CERT_FILE_PATH)
            print("Account Insert Response: ", response.text, "\n")
            if(response.status_code == 200 ):
                # fba.update(gl_account_reference_id=reference_id)
                # response_dict = xmltodict.parse(response.text,process_namespaces=False)
                return response.json()
            
        except Exception as e:
            traceback.print_exc()
            return {}
        


    def createRequestPayload(self, fba: FederalBankApplication):
        lm = fba.application.Originatedby
        assets = fba.application.asset_application.all()
        account = fba.application.account.bankaccount_account.all().first()
        distinctPouchNumbers = assets.values('pouchnumber').distinct()
        data = {
            "SenderCode": "RADIAN",
            "ServiceAccessId": "RADIAN",
            "ServiceAccessCode": "RADIAN@123",
            "RequestId": common_utils.getFederalReferenceID(fba.application.application_number,"GLVALD"), # auto generate
            "ReferenceNumber": fba.application.application_number,
            "LoanId": fba.application.application_number,
            "LoanAccountDetails":{
                "LoanAmount": str(fba.application.loan_amount),
                "loanagentreqauthno": str(int(fba.agent_otp / 10)),
                # "loangldtotgrosswgt": str(float(fba.application.net_weight)),
                "loangldtotnetwgt": str(float(fba.application.net_weight)),
                "NumberOfPacket": str(len(distinctPouchNumbers)),
                "PacketSerialNumber": distinctPouchNumbers[0]['pouchnumber'],
                "FundTransferCustAccNo": account.account_number,
                "FundTransferIfscCode": account.ifsc,
                "FundTransferBankName": re.sub(r'[^a-zA-Z\s]','',account.bank_name),
                "LoanType":"LTN"
            },
            "GoldJewelryDetails":[],
            "AgentDetails":{
                "AgentName": lm.first_name +" "+lm.last_name,
                "employeeid": lm.employee_id,
                "id_no": lm.employee_id,
                "Mobile": lm.phone_to_str().replace('+',''),
                # "AgentPhoto":"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"
            }
        }
        if lm.employee_profile_photo:
            data['AgentDetails']['AgentPhoto'] = base64.b64encode(lm.employee_profile_photo.read()).decode(),
        else:
            data['AgentDetails']['AgentPhoto'] = "iVBORw0KGgoAAAANSUhEUgAAABEAAAAOCAMAAAD+MweGAAADAFBMVEUAAAAAAFUAAKoAAP8AJAAAJFUAJKoAJP8ASQAASVUASaoASf8AbQAAbVUAbaoAbf8AkgAAklUAkqoAkv8AtgAAtlUAtqoAtv8A2wAA21UA26oA2/8A/wAA/1UA/6oA//8kAAAkAFUkAKokAP8kJAAkJFUkJKokJP8kSQAkSVUkSaokSf8kbQAkbVUkbaokbf8kkgAkklUkkqokkv8ktgAktlUktqoktv8k2wAk21Uk26ok2/8k/wAk/1Uk/6ok//9JAABJAFVJAKpJAP9JJABJJFVJJKpJJP9JSQBJSVVJSapJSf9JbQBJbVVJbapJbf9JkgBJklVJkqpJkv9JtgBJtlVJtqpJtv9J2wBJ21VJ26pJ2/9J/wBJ/1VJ/6pJ//9tAABtAFVtAKptAP9tJABtJFVtJKptJP9tSQBtSVVtSaptSf9tbQBtbVVtbaptbf9tkgBtklVtkqptkv9ttgBttlVttqpttv9t2wBt21Vt26pt2/9t/wBt/1Vt/6pt//+SAACSAFWSAKqSAP+SJACSJFWSJKqSJP+SSQCSSVWSSaqSSf+SbQCSbVWSbaqSbf+SkgCSklWSkqqSkv+StgCStlWStqqStv+S2wCS21WS26qS2/+S/wCS/1WS/6qS//+2AAC2AFW2AKq2AP+2JAC2JFW2JKq2JP+2SQC2SVW2Saq2Sf+2bQC2bVW2baq2bf+2kgC2klW2kqq2kv+2tgC2tlW2tqq2tv+22wC221W226q22/+2/wC2/1W2/6q2///bAADbAFXbAKrbAP/bJADbJFXbJKrbJP/bSQDbSVXbSarbSf/bbQDbbVXbbarbbf/bkgDbklXbkqrbkv/btgDbtlXbtqrbtv/b2wDb21Xb26rb2//b/wDb/1Xb/6rb////AAD/AFX/AKr/AP//JAD/JFX/JKr/JP//SQD/SVX/Sar/Sf//bQD/bVX/bar/bf//kgD/klX/kqr/kv//tgD/tlX/tqr/tv//2wD/21X/26r/2////wD//1X//6r////qm24uAAAA1ElEQVR42h1PMW4CQQwc73mlFJGCQChFIp0Rh0RBGV5AFUXKC/KPfCFdqryEgoJ8IX0KEF64q0PPnow3jT2WxzNj+gAgAGfvvDdCQIHoSnGYcGDE2nH92DoRqTYJ2bTcsKgqhIi47VdgAWNmwFSFA1UAAT2sSFcnq8a3x/zkkJrhaHT3N+hD3aH7ZuabGHX7bsSMhxwTJLr3evf1e0nBVcwmqcTZuatKoJaB7dSHjTZdM0G1HBTWefly//q2EB7/BEvk5vmzeQaJ7/xKPImpzv8/s4grhAxHl0DsqGUAAAAASUVORK5CYII="

        # TODO: Now calculating gross weight but it should be stored in application model
        totalGrossWeight = 0.0
        for asset in assets:
            totalGrossWeight += float(asset.gross_weight)
            jewelImg = asset.asset_document_asset.all().filter(asset_document_type='PICTURE_OF_GOLD_JEWELLERY').first()
            weightScaleIMg = asset.asset_document_asset.all().filter(asset_document_type='PICTURE_OF_SCALE_WITH_GOLD').first()
            encodedJewelImg = base64.b64encode(jewelImg.file.read()).decode()
            encodedWeightScaleIMg = base64.b64encode(weightScaleIMg.file.read()).decode()
            data["GoldJewelryDetails"].append(
                {
                    "NumberOfItem": "1",
                    "JewelType": getFederalAssetType(asset.type),
                    "GrossWeight": str(int(asset.gross_weight)),
                    "NetWeight": str(int(asset.net_weight)),
                    "TotalAdjustment":"0",
                    "Karat": str(asset.karat_value),
                    "Wastage": str(int(asset.wastage)),
                    "JewelImg": "iVBORw0KGgoAAAANSUhEUgAAABEAAAAOCAMAAAD+MweGAAADAFBMVEUAAAAAAFUAAKoAAP8AJAAAJFUAJKoAJP8ASQAASVUASaoASf8AbQAAbVUAbaoAbf8AkgAAklUAkqoAkv8AtgAAtlUAtqoAtv8A2wAA21UA26oA2/8A/wAA/1UA/6oA//8kAAAkAFUkAKokAP8kJAAkJFUkJKokJP8kSQAkSVUkSaokSf8kbQAkbVUkbaokbf8kkgAkklUkkqokkv8ktgAktlUktqoktv8k2wAk21Uk26ok2/8k/wAk/1Uk/6ok//9JAABJAFVJAKpJAP9JJABJJFVJJKpJJP9JSQBJSVVJSapJSf9JbQBJbVVJbapJbf9JkgBJklVJkqpJkv9JtgBJtlVJtqpJtv9J2wBJ21VJ26pJ2/9J/wBJ/1VJ/6pJ//9tAABtAFVtAKptAP9tJABtJFVtJKptJP9tSQBtSVVtSaptSf9tbQBtbVVtbaptbf9tkgBtklVtkqptkv9ttgBttlVttqpttv9t2wBt21Vt26pt2/9t/wBt/1Vt/6pt//+SAACSAFWSAKqSAP+SJACSJFWSJKqSJP+SSQCSSVWSSaqSSf+SbQCSbVWSbaqSbf+SkgCSklWSkqqSkv+StgCStlWStqqStv+S2wCS21WS26qS2/+S/wCS/1WS/6qS//+2AAC2AFW2AKq2AP+2JAC2JFW2JKq2JP+2SQC2SVW2Saq2Sf+2bQC2bVW2baq2bf+2kgC2klW2kqq2kv+2tgC2tlW2tqq2tv+22wC221W226q22/+2/wC2/1W2/6q2///bAADbAFXbAKrbAP/bJADbJFXbJKrbJP/bSQDbSVXbSarbSf/bbQDbbVXbbarbbf/bkgDbklXbkqrbkv/btgDbtlXbtqrbtv/b2wDb21Xb26rb2//b/wDb/1Xb/6rb////AAD/AFX/AKr/AP//JAD/JFX/JKr/JP//SQD/SVX/Sar/Sf//bQD/bVX/bar/bf//kgD/klX/kqr/kv//tgD/tlX/tqr/tv//2wD/21X/26r/2////wD//1X//6r////qm24uAAAA1ElEQVR42h1PMW4CQQwc73mlFJGCQChFIp0Rh0RBGV5AFUXKC/KPfCFdqryEgoJ8IX0KEF64q0PPnow3jT2WxzNj+gAgAGfvvDdCQIHoSnGYcGDE2nH92DoRqTYJ2bTcsKgqhIi47VdgAWNmwFSFA1UAAT2sSFcnq8a3x/zkkJrhaHT3N+hD3aH7ZuabGHX7bsSMhxwTJLr3evf1e0nBVcwmqcTZuatKoJaB7dSHjTZdM0G1HBTWefly//q2EB7/BEvk5vmzeQaJ7/xKPImpzv8/s4grhAxHl0DsqGUAAAAASUVORK5CYII=",
                    "WeightScaleImg": "iVBORw0KGgoAAAANSUhEUgAAABEAAAAOCAMAAAD+MweGAAADAFBMVEUAAAAAAFUAAKoAAP8AJAAAJFUAJKoAJP8ASQAASVUASaoASf8AbQAAbVUAbaoAbf8AkgAAklUAkqoAkv8AtgAAtlUAtqoAtv8A2wAA21UA26oA2/8A/wAA/1UA/6oA//8kAAAkAFUkAKokAP8kJAAkJFUkJKokJP8kSQAkSVUkSaokSf8kbQAkbVUkbaokbf8kkgAkklUkkqokkv8ktgAktlUktqoktv8k2wAk21Uk26ok2/8k/wAk/1Uk/6ok//9JAABJAFVJAKpJAP9JJABJJFVJJKpJJP9JSQBJSVVJSapJSf9JbQBJbVVJbapJbf9JkgBJklVJkqpJkv9JtgBJtlVJtqpJtv9J2wBJ21VJ26pJ2/9J/wBJ/1VJ/6pJ//9tAABtAFVtAKptAP9tJABtJFVtJKptJP9tSQBtSVVtSaptSf9tbQBtbVVtbaptbf9tkgBtklVtkqptkv9ttgBttlVttqpttv9t2wBt21Vt26pt2/9t/wBt/1Vt/6pt//+SAACSAFWSAKqSAP+SJACSJFWSJKqSJP+SSQCSSVWSSaqSSf+SbQCSbVWSbaqSbf+SkgCSklWSkqqSkv+StgCStlWStqqStv+S2wCS21WS26qS2/+S/wCS/1WS/6qS//+2AAC2AFW2AKq2AP+2JAC2JFW2JKq2JP+2SQC2SVW2Saq2Sf+2bQC2bVW2baq2bf+2kgC2klW2kqq2kv+2tgC2tlW2tqq2tv+22wC221W226q22/+2/wC2/1W2/6q2///bAADbAFXbAKrbAP/bJADbJFXbJKrbJP/bSQDbSVXbSarbSf/bbQDbbVXbbarbbf/bkgDbklXbkqrbkv/btgDbtlXbtqrbtv/b2wDb21Xb26rb2//b/wDb/1Xb/6rb////AAD/AFX/AKr/AP//JAD/JFX/JKr/JP//SQD/SVX/Sar/Sf//bQD/bVX/bar/bf//kgD/klX/kqr/kv//tgD/tlX/tqr/tv//2wD/21X/26r/2////wD//1X//6r////qm24uAAAA1ElEQVR42h1PMW4CQQwc73mlFJGCQChFIp0Rh0RBGV5AFUXKC/KPfCFdqryEgoJ8IX0KEF64q0PPnow3jT2WxzNj+gAgAGfvvDdCQIHoSnGYcGDE2nH92DoRqTYJ2bTcsKgqhIi47VdgAWNmwFSFA1UAAT2sSFcnq8a3x/zkkJrhaHT3N+hD3aH7ZuabGHX7bsSMhxwTJLr3evf1e0nBVcwmqcTZuatKoJaB7dSHjTZdM0G1HBTWefly//q2EB7/BEvk5vmzeQaJ7/xKPImpzv8/s4grhAxHl0DsqGUAAAAASUVORK5CYII=",
                    # "JewelImg": encodedJewelImg,
                    # "WeightScaleImg": encodedWeightScaleIMg,
                }
            )
        data['LoanAccountDetails']['loangldtotgrosswgt'] = str(totalGrossWeight)
        return data


class GLOpenService():
    
    def createGLAccount(fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_GL_OPEN_PATH
            payload,reference_id = GLOpenService.createRequestPayload(fba)
            # print(payload)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            certFile = "radianfinserv_uat.pem"
            print("Sending GL OPEN Creation Request...")
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("GL OPEN Creation Response: ", response.text, "\n")
            if(response.status_code == 200 ):
                fba.gl_account_reference_id=reference_id
                fba.save()

                response_dict = xmltodict.parse(response.text,process_namespaces=False)
                return response_dict
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"is_eligible":False,"status":"Error","message":str(e)}
            
    
    def createRequestPayload(fba: FederalBankApplication):
        assets = fba.application.asset_application.all()
        ornaments = []
        for asset in assets:
            ornaments.append(getFederalAssetType(asset.type))
        ornaments = Counter(ornaments)
        ornamentStr = ''
        for k,v in ornaments.items():
            ornamentStr += f'{k}:{v}/'


        pan_no = fba.application.account.pan_no

        ####################
        # TODO: need to verify below RepaymentType and other fields logic:
        # EI is for Equated Installment
        repaymentType = 'Lumpsum' if fba.application.product.amortization_type == AMORTIZATIONTYPE.BULLET.value else 'EI'
        noOfInstallments = 1
        if fba.application.product.amortization_type == AMORTIZATIONTYPE.BULLET.value:
            noOfInstallments = 1


        ####################

        reference_id = common_utils.getFederalReferenceID(fba.application.application_number,"GLOPEN")
        # requestId = time() * 1000
        cusName = fba.account.user.first_name +" "+fba.account.user.last_name
        gender = "M" if fba.application.account.gender == "MALE" else "F"
        marital_status = "SING" if fba.application.account.maritial_status else "MARD"
        
                        # "<CustomerId>"+ fba.account.customer_id +"</CustomerId>"+\
        
        if environment.FEDERAL_ENV == 'PROD':
            sanctionLimit = "<SanctionLimit>"+ str(fba.application.eligible_amount) +"</SanctionLimit>"+\
                        "<LoanPeriodMonths>"+ str(fba.application.product.tenure) +"</LoanPeriodMonths>"+\
                        "<LoanPeriodDays>0</LoanPeriodDays>"+\
                        "<HolidayPeriod>0</HolidayPeriod>"+\
                        "<RepaymentType>"+ repaymentType +"</RepaymentType>"+\
                        "<NoOfInstallment>"+ str(noOfInstallments) +"</NoOfInstallment>"+\
                        "<ValueDate>"+str(datetime.date.today().strftime("%d-%m-%Y"))+"</ValueDate>"+\
                        "<InstallmentFrequency>B</InstallmentFrequency>"+\
                        "<InstallmentAmount>"+ str(fba.application.eligible_amount) +"</InstallmentAmount>"
                        
            drawingPower = "<DrawingPower>"+ str(fba.application.eligible_amount) +"</DrawingPower>"
        else:
            sanctionLimit = "<SanctionLimit>143548</SanctionLimit>"+\
                        "<LoanPeriodMonths>"+ str(fba.application.product.tenure) +"</LoanPeriodMonths>"+\
                        "<LoanPeriodDays>0</LoanPeriodDays>"+\
                        "<HolidayPeriod>0</HolidayPeriod>"+\
                        "<RepaymentType>"+ repaymentType +"</RepaymentType>"+\
                        "<NoOfInstallment>"+ str(noOfInstallments) +"</NoOfInstallment>"+\
                        "<ValueDate>"+str(datetime.date.today().strftime("%d-%m-%Y"))+"</ValueDate>"+\
                        "<InstallmentFrequency>B</InstallmentFrequency>"+\
                        "<InstallmentAmount>143548</InstallmentAmount>"
                        
            drawingPower = "<DrawingPower>143548</DrawingPower>"

        xml_body="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+\
                    "<GoldLoanOpening>"+\
                    "<SenderCredentials>"+\
                        "<UserAccessId>"+environment.FEDERAL_UAT_USER_ID+"</UserAccessId>"+\
                        "<UserAccessCode>"+environment.FEDERL_UAT_USER_ACCESS_CODE+"</UserAccessCode>"+\
                        "<SenderCode>"+environment.FEDERAL_UAT_CHANNEL_ID+"</SenderCode>"+\
                    "</SenderCredentials>"+\
                    "<GoldLoanDetails>"+\
                        "<RequestId>"+ reference_id +"</RequestId>"+\
                        "<SolId>"+ fba.solId +"</SolId>"+\
                        "<SchemeCode>"+ fba.application.product.product_number +"</SchemeCode>"+\
                        "<CustomerId>143357810</CustomerId>"+\
                        "<CustomerName>"+ cusName +"</CustomerName>"+\
                        "<PanNo>"+pan_no+"</PanNo>"+\
                        sanctionLimit +\
                        "<InterestRate>"+ str(fba.application.product.interest_rate) +"</InterestRate>"+\
                        "<ResetPeriodMonths>0</ResetPeriodMonths>"+\
                        "<UtilisationState>KA</UtilisationState>"+\
                        "<UtilisationDistrict>BGR</UtilisationDistrict>"+\
                        "<VariableProcessingFee>0</VariableProcessingFee>"+\
                        "<MarginMoneyFlag>N</MarginMoneyFlag>"+\
                        "<InterestSubventionFlag>N</InterestSubventionFlag>"+\
                        "<SanctionAuthorityCode>BM3</SanctionAuthorityCode>"+\
                        "<SanctionLevel>"+ fba.solId +"</SanctionLevel>"+\
                        "<IntTableCode>RPKV2</IntTableCode>"+\
                        "<GlSubHeadCode>78450</GlSubHeadCode>"+\
                        "<MCLRFixedSpread>0</MCLRFixedSpread>" +\
                        drawingPower +\
                        "<BCLoanId>"+ fba.application.application_number +"</BCLoanId>"+\
                        "<GrossWt>54.4</GrossWt>"+\
                        "<Wastage>2.4</Wastage>"+\
                        "<OrnamentDetails>"+ ornamentStr +"</OrnamentDetails>"+\
                        "<Co_Obligant_Data></Co_Obligant_Data>"+\
                    "</GoldLoanDetails>"+\
                   " </GoldLoanOpening>"
        return xml_body,reference_id
    
class GLCustomerValidationService():
    
    def validateCustomer(self):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_GL_CUSTOMER_VALIDATION
            # print("url: ",url)
            payload = self.createRequestPayload()
            # print(payload)
            headers = {
            'x-ibm-client-id': environment.FEDERAL_UAT_CLIENT_ID,
            'x-ibm-client-secret': environment.FEDERAL_UAT_CLIENT_SECRET,
            'Content-Type': 'application/json',
            }
            certFile = "radianfinserv_uat.pem"
            print("Customer Validation Request: \n\n",payload)
            print("Request: ",payload, "\n")
            print("headers: ",headers, "\n")
            response = requests.request("POST", url, headers=headers, data=payload, cert=certFile)
            print("Customer Validation Response: ", response.text, "\n")
            resp = response.json()
            if response.status_code == 200 and resp['ResponseAction'] != 'FAILURE':
                resp = response.json()
                return {"status":"success","data": resp}
            else:
                raise ValueError(resp)
            
            
        except Exception as e:
            print("Error:: ")
            print(e)
            return {"status":"error","message":str(e)}
    
    def createRequestPayload(self):
        return json.dumps(self.__dict__)
    
    def __init__(self,fba: FederalBankApplication):
        #fba=fba[0]
        # TODO: need to remove hard coded value in request body
        self.SenderCode=environment.FEDERAL_UAT_USER_ID
        self.ServiceAccessId=environment.FEDERAL_UAT_USER_ID
        self.ServiceAccessCode=environment.FEDERL_UAT_USER_ACCESS_CODE
        self.RequestId=common_utils.getFederalReferenceID(fba.application.application_number,"GLVALD")
        self.EkycApiReqId = fba.aadhar_rrn
        self.GoldLoanApiReqId=str(fba.gl_account_reference_id)
        # self.GoldLoanApiReqId="LOANFBL08852700110152"
        self.ReferenceNumber=fba.application.application_number
        self.SolId=fba.solId
        # self.CustomerId=str(fba.application.account.customer_id)
        # self.CustomerId="13157" + str(time())[-4:]
        # self.CustomerId=143357810
        self.CustomerName=str(fba.application.account.user.first_name)
        self.CustomerMobile=str(fba.application.account.user.phone).replace("+","")
        self.EkycStatus=str(fba.ekyc_status)
        self.EkycRefno=str(fba.ekyc_request_id)
        self.NameDobStatus= "1" if fba.name_dob_status == 'Y' else "0"
        self.NameDobApiReqId=str(fba.name_dob_request_id)
        self.PanStatus="1" if fba.pan_status == 'E' else "0"
        self.PanApiReqId=str(fba.pan_request_id)
        self.PanNumber=str(fba.pan)
        self.Form60Flag="0"
        self.UnNameStatus="1" if fba.unchck_status == 'S' else "0" #If name is not UN list than we got S from its API and need to send 1 if its not there in UN Name list
        self.UnNameApiReqId=str(fba.unchck_request_id)
        self.DedupStatus="0" if fba.ddupe_flag =='N' else "1"
        self.DedupApiReqId=str(fba.ddupe_request_id)
        
#class GLAccountInsertService():
  #  def insertLoanAccount(borrower_application,fba):

