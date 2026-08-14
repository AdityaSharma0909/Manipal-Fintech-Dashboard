import uuid
import logging
import requests
from rest_framework import status
from document.models import Document
from rest_framework.views import APIView
from application.models import Application
from rest_framework.response import Response
from utils.responseHandler import HttpResponse
from django.shortcuts import get_object_or_404
from scoreme.models import ScoreMeBankAnalysis
from rest_framework.permissions import AllowAny
from scoreme.utils.bank_analysis_utils import BsaUtils
from scoreme.serializers import ScoreMeBankAnalysisSerializer
from utils.constants import APPLICATION_STATUS

logger = logging.getLogger('radian')

class UploadBankStatements(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the application_id from the GET parameters
            application_id = request.GET.get('application_id')
            if not application_id:
                return HttpResponse.BadRequest("application_id is required")

            # Check if there is an existing ScoreMeBankAnalysis object for the given application_id
            existing_object = ScoreMeBankAnalysis.objects.filter(application_id=application_id).first()
            if existing_object:
                serializer = ScoreMeBankAnalysisSerializer(existing_object)
                data = serializer.data

                if not existing_object.excel_url:
                    data['responseMessage'] = 'Please wait, bank analysis is under process.'
                    return HttpResponse.Success(data)
                else:
                    data['responseMessage'] = 'Downloading Bank Analysis Report'
                    return HttpResponse.Success(data)

            # Retrieve the Application object using the application_id
            application = get_object_or_404(Application, application_id=application_id)
            account = application.account

            # Retrieve the bank statements associated with the account
            documents = Document.objects.filter(document_type__in=['BANK_STATEMENT_1', 'BANK_STATEMENT_2'], account=account)
            bank_statement_1 = documents.filter(document_type='BANK_STATEMENT_1').first()
            bank_statement_2 = documents.filter(document_type='BANK_STATEMENT_2').first()

            # Ensure at least one of the bank statements exists
            if not bank_statement_1 and not bank_statement_2:
                return HttpResponse.BadRequest('At least one of the bank statements is required')

            # Check if the bank statements are password protected
            is_statement_1_protected = bank_statement_1.is_password if bank_statement_1 else False
            is_statement_2_protected = bank_statement_2.is_password if bank_statement_2 else False

            # Fetch passwords directly from bank_statement objects
            password1 = bank_statement_1.password if bank_statement_1 else None
            password2 = bank_statement_2.password if bank_statement_2 else None

            # Ensure password1 is provided if BANK_STATEMENT_1 is protected
            if is_statement_1_protected and not password1:
                return HttpResponse.BadRequest("password1 is required as BANK_STATEMENT_1 is protected")

            # Ensure password2 is provided if BANK_STATEMENT_2 is protected
            if is_statement_2_protected and not password2:
                return HttpResponse.BadRequest('password2 is required as BANK_STATEMENT_2 is protected')

            # Process and upload BANK_STATEMENT_1 if it exists
            if bank_statement_1:
                files_1, file_passwords_1 = BsaUtils.process_bank_statements(bank_statement_1, None, password1, None)
                payload_1 = BsaUtils.create_bsa_payload(file_passwords_1)
                response_json_1 = BsaUtils.call_upload_statement_api(payload_1, files_1)
                print(response_json_1, "=== Printing response json 1 ===")

                # Check for errors in the response of BANK_STATEMENT_1 upload
                if "responseCode" in response_json_1 and response_json_1["responseCode"] != "SRS016":
                    return HttpResponse.BadRequest(f'Bank Statement 1 error: {response_json_1["responseMessage"]}')

                reference_id_1 = response_json_1.get('data', {}).get('referenceId')
            else:
                reference_id_1 = None

            # Process and upload BANK_STATEMENT_2 if it exists
            if bank_statement_2:
                files_2, file_passwords_2 = BsaUtils.process_bank_statements(bank_statement_2, None, password2, None)
                payload_2 = BsaUtils.create_bsa_payload(file_passwords_2)
                response_json_2 = BsaUtils.call_upload_statement_api(payload_2, files_2)
                print(response_json_2, "=== Printing response json 2 ===")

                # Check for errors in the response of BANK_STATEMENT_2 upload
                if "responseCode" in response_json_2 and response_json_2["responseCode"] != "SRS016":
                    return HttpResponse.BadRequest(f'Bank Statement 2 error: {response_json_2["responseMessage"]}')

                reference_id_2 = response_json_2.get('data', {}).get('referenceId')
            else:
                reference_id_2 = None

            # If both bank statements exist, merge their reports
            if reference_id_1 and reference_id_2:
                merge_response = BsaUtils.call_merge_bsa_report_api(reference_id_1, reference_id_2)
                print(merge_response, "=== Printing merge response ===")

                # Check for errors in the merge response
                if "responseCode" in merge_response and merge_response["responseCode"] != "SRS016":
                    return HttpResponse.BadRequest(f'Merge error: {merge_response["responseMessage"]}')

                merge_reference_id = merge_response.get('data', {}).get('referenceId')

                # Create a new ScoreMeBankAnalysis object with the merged reference ID
                new_object = BsaUtils.create_scoreme_bank_analysis_object(application_id=application_id, reference_id=merge_reference_id)
                response_to_return = Response(merge_response, status=status.HTTP_200_OK)

            else:
                # If only one bank statement exists, create a new ScoreMeBankAnalysis object with its reference ID
                single_reference_id = reference_id_1 if reference_id_1 else reference_id_2
                new_object = BsaUtils.create_scoreme_bank_analysis_object(application_id=application_id, reference_id=single_reference_id)
                if reference_id_1 and not reference_id_2:
                    # If only BANK_STATEMENT_1 exists, return response_json_1
                    response_to_return = Response(response_json_1, status=status.HTTP_200_OK)
                elif not reference_id_1 and reference_id_2:
                    # If only BANK_STATEMENT_2 exists, return response_json_2
                    response_to_return = Response(response_json_2, status=status.HTTP_200_OK)
                    
            # Update the Application status to BANK_STATEMENT_REPORT_INITIATED
            if response_to_return:
                application.status = APPLICATION_STATUS.BANK_STATEMENT_REPORT_INITIATED.value
                application.save()

            return response_to_return
        except requests.RequestException as e:
            logger.error(f'Third-party API request failed: {str(e)}')
            return Response(e.response.json(), status=e.response.status_code)

        except Exception as e:
            logger.exception(f'An unexpected error occurred: {str(e)}')
            return HttpResponse.InternalServerError(str(e))
