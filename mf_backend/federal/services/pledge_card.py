import requests
from utils.envSetup import environment
from utility import common_utils
from federal.models import FederalBankApplication
from federal.services.pledge_card_doc import PledgeCardCreation
import traceback


class GLPledgeCardService:
    def sendPledgeCard(self, fba):
        try:
            url = environment.FEDERAL_UAT_BASE_URL + environment.FEDERAL_GL_PLEDGE_CARD
            payload = self.createRequestPayload(fba)
            headers = {
                "x-ibm-client-id": environment.FEDERAL_UAT_CLIENT_ID,
                "x-ibm-client-secret": environment.FEDERAL_UAT_CLIENT_SECRET,
            }
            print("Request: ", payload)
            print("headers: ", headers)
            print("Uploading Pledge Card...")
            response = requests.request(
                "POST",
                url,
                headers=headers,
                json=payload,
                cert=environment.FEDERAL_CERT_FILE_PATH,
            )
            print(response.text)
            if response.status_code == 200:
                # fba.update(gl_account_reference_id=reference_id)
                # response_dict = xmltodict.parse(response.text,process_namespaces=False)
                return response.json()

        except Exception as e:
            traceback.print_exc()
            return {}

    def createRequestPayload(self, fba: FederalBankApplication):
        assets = fba.application.asset_application.all()
        pledgeCardBase64 = PledgeCardCreation().get_image(str(fba.application.application_id))
        print(" :::::::::: assets ::::::::::::;;")
        print(assets)
        data = {
            "SenderCode": "RADIAN",
            "ServiceAccessId": "RADIAN",
            "ServiceAccessCode": "RADIAN@123",
            "RequestId": common_utils.getFederalReferenceID(
                fba.application.application_number, "GLVALD"
            ),  # auto generate
            "LoanId": fba.application.application_number,
            "PledgeCardImg": pledgeCardBase64,
        }
        return data
