import traceback

import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from application.models import Application , LoanDocument
from application.services.esign_application import EsignApplicationUtil
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj
from utility.frs.frs_helper import FrsHelper
from federal.services.pledge_card import GLPledgeCardService
from utils.constants import APPLICATION_STATUS , ROLES

"""
{
  "esign_id": "",
  "document_status": "",
  "download_link": ""
}

https://uat-api.radianfinserv.com/core/frs/callback
Post request

URL Redirect feature (Optional):
---------------------------------------

Client eSign success URL:
--------------------------
https://frslabs.com/esign/success


on eSign success we will trigger:
---------------------------------- 
https://frslabs.com/esign/success?esign_id=xxx&token=xxxx&document_status=COMPLETED

sample response from FRS

{'esign_status': ['{
"download_link":"https://esign-v2.atlaskyc.com/v2/prod/web/download/signed/document?token=u003desd-dc6cfd63-5634-4bc7-9800-c84620066630",
"document_status":"COMPLETED",
"esign_id":"es-1f8beb3b-477a-4ccf-a88b-5230a7f3583e"}
']}
<QueryDict: {'esign_status': ['{"download_link":"https://esign-v2.atlaskyc.com/v2/prod/web/download/signed/document?token\\u003desd-deeb60ad-60e3-4d18-a507-17d49a6f3431","document_status":"COMPLETED","esign_id":"es-27b3b8b4-105b-47d3-9069-9fae5397e9b6"}']}
"""




class FrsCallbackUtil(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data
        self.response=''

    def run_logic(self):
        try:

            esign_status=self.__data.get('esign_status')
            if len(esign_status)>0:
                esign_status=json.loads(esign_status)
                
                document_status = esign_status.get("document_status")
                if document_status == "COMPLETED":
                    esign_id=esign_status.get("esign_id")
                    # TODO e-sign:
                    # loan_doc=LoanDocument.objects.get(esign_id=esign_id)
                    # loan_doc.signed_doc_link = esign_status.get('download_link')
                    # loan_doc.save()
                    # EsignApplicationUtil().save_document(esign_status.get('download_link'), application=app, loan_doc)
                    # if app.Orifinatedby.role == 'RM':
                    #     signed_document_types = LoanDocument.objects.filter(application=application, signed_doc_link__isnull=False).value('document_type')
                    #     if 'SIGNED_UNSECURED_LOAN_DOCUMENT' in signed_document_types or \
                    #     'SIGNED_SANCTION_LETTER' in signed_document_types or \
                    #     'SIGNED_DPN_DOCUMENT' in signed_document_types: 
                    #         app.status=APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                    #         app.save()
                    # elif (app.Orifinatedby.role == 'LM' or 'BM') and loan_doc.document_type == 'SIGNED_LOAN_DOCUMENT':
                    #     app.status=APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                    #     app.save()
                    # # comment below application line

                    loan_doc = LoanDocument.objects.get(esign_id=esign_id)
                    
                    loan_doc.esign_signed_doc_link = esign_status.get('download_link')
                    loan_doc.save()
                   
                    EsignApplicationUtil().save_document(esign_status.get('download_link'), loan_doc=loan_doc)
                    application_id=loan_doc.application.application_id
                   
                    app=Application.objects.get(application_id=application_id)
                    
                    if app.Originatedby.role == ROLES.RELATIONSHIP_MANAGER.value:
                        signed_document_types = set(LoanDocument.objects.filter(application=app, esign_signed_doc_link__isnull=False).values_list('document_type', flat=True))
                        required_documents = {'SIGNED_UNSECURED_LOAN_DOCUMENT', 'SIGNED_SANCTION_LETTER', 'SIGNED_DPN_DOCUMENT'}
                        
                        if required_documents.issubset(signed_document_types):
                            app.status = APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                            app.save()

                    elif app.Originatedby.role in [ROLES.LOAN_OFFICER.value, ROLES.BRANCH_MANAGER.value] and loan_doc.document_type == 'SIGNED_LOAN_DOCUMENT':
                        app.status = APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                        app.save()
                    else:
                        pass


                    # app=Application.objects.get(esign_application_id=esign_id)
                    # app.esign_signed_doc_link=esign_status.get('download_link')
                    # app.status=APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                    # app.save()
                    # EsignApplicationUtil().save_document(esign_status.get('download_link'), application=app)

            
            # TODO: Need to call this method asynchronously in background
            # Sending pledge card to Federal Bank if application lender is Federal Bank
            fba = app.federal_application.all()
            if len(fba)>0:
                GLPledgeCardService().sendPledgeCard(fba[0])
        except ObjectDoesNotExist:
            print('not found')
            #requests.post('https://dev-api.radianfinserv.com/core/frs/callback')
        except Exception:
            traceback.print_exc()
    def process(self):
        self.response=custom_response_obj(message='Callback successful', code=200)
        return self.response

class FrsCallbackView(APIView):

    permission_classes = [AllowAny]
    def post(self, request):
        data=request.data
        print('FRS data---------->',data)
        return FrsCallbackUtil(data=data).main()



import json
from rest_framework.response import Response
from rest_framework.views import APIView

class CheckDocumentStatusView(APIView):
    def post(self, request):
        # Get the "esign_status" value from the request data (QueryDict)
        esign_status_data = request.data.get("esign_status")

        if esign_status_data:
            # Parse the JSON string in "esign_status"
            try:
                esign_status = json.loads(esign_status_data)

                # Check if the "document_status" is "COMPLETED"
                document_status = esign_status.get("document_status")
                if document_status == "COMPLETED":
                    return Response({"message": "Document status is COMPLETED"})
                else:
                    return Response({"message": "Document status is not COMPLETED"})
            except json.JSONDecodeError:
                return Response({"message": "Invalid JSON in 'esign_status' field"}, status=400)
        else:
            return Response({"message": "'esign_status' field is missing in the request data"}, status=400)



class UpdateFrsCallbackManully(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        application=Application.objects.filter(esign_signed_doc_link__isnull=True)
        print(application)
        for app in application:
            resp = FrsHelper().verify_esign_status(data={'id': app.esign_application_id})
            if resp.get('status_code') == 200 and resp.get('data').get("document_status") == "COMPLETED":
                link = resp.get('data').get('download_link')
                if app.status==APPLICATION_STATUS.GENERATE_LOAN_DOCUMENT.value:
                    app.status = APPLICATION_STATUS.SIGNED_LOAN_DOCUMENT_SUBMITED.value
                app.esign_signed_doc_link = link
                app.save()
                EsignApplicationUtil().save_document(link, app)

        return Response(status=204)