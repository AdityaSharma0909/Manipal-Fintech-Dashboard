from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from application.models import LoanDocument
from scoreme.models import ScoreMeBankAnalysis
from scoreme.utils.bank_analysis_utils import BsaUtils, FieldsForCamCaluculator
from utils.responseHandler import HttpResponse
from rest_framework.permissions import AllowAny
import requests
import traceback
from utils.constants import APPLICATION_STATUS

class BsaWebhookView(APIView):
    permission_classes = [AllowAny]
    
    SUCCESS_RESPONSE_CODE = 'SRC001'

    def get(self, request, *args, **kwargs):
        try:
            print("**** Hello Score Me BSA Webhook (GET) ****")
            print(request.data)

            data = request.data
            reference_id = data['data']['referenceId']
            response_code = data['responseCode']
            webhook_response = str(request.data)

            if response_code == self.SUCCESS_RESPONSE_CODE:
                bank_analysis_obj = BsaUtils.get_bank_analysis_object(reference_id)
                
                BsaUtils.update_bank_analysis_object(bank_analysis_obj, data, webhook_response)
                
                # Download the JSON file
                json_document = LoanDocument.objects.get(
                    application=bank_analysis_obj.application,
                    document_type="BSA_JSON_FILE"
                )
                json_file_url = json_document.file.url
                json_data = requests.get(json_file_url).json()
                
                # Instantiate FieldsForCamCaluculator and perform calculations
                financial_calculator = FieldsForCamCaluculator(json_data["Data"])
                cash_flow = financial_calculator.calculate_cash_flow()
                average_monthly_balance = financial_calculator.calculate_average_monthly_balance()
                leverage_to_income = financial_calculator.calculate_leverage_to_income(average_monthly_balance)
                
                # Update the bank_analysis_obj with the new fields
                bank_analysis_obj.cash_flow = cash_flow
                bank_analysis_obj.average_monthly_balance = average_monthly_balance
                bank_analysis_obj.leverage_to_income = leverage_to_income
                
                # Save the updated object
                bank_analysis_obj.save()
                # Update the application status to BANK_STATEMENT_REPORT_GENERATED
                application_obj = bank_analysis_obj.application
                application_obj.status = APPLICATION_STATUS.BANK_STATEMENT_REPORT_GENERATED.value
                application_obj.save()

                return Response(status=status.HTTP_201_CREATED)
            else:
                return HttpResponse.BadRequest("ResponseCode is not SRC001.")
        except ScoreMeBankAnalysis.DoesNotExist:
            return HttpResponse.BadRequest("Bank analysis object not found.")
        except KeyError as e:
            return HttpResponse.BadRequest(f"Missing key: {str(e)}")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def post(self, request, *args, **kwargs):
        try:
            print("**** Hello Score Me BSA Webhook (POST) ****")
            print(request.data)

            data = request.data
            reference_id = data['data']['referenceId']
            response_code = data['responseCode']
            webhook_response = str(request.data)

            if response_code == self.SUCCESS_RESPONSE_CODE:
                bank_analysis_obj = BsaUtils.get_bank_analysis_object(reference_id)
                
                BsaUtils.update_bank_analysis_object(bank_analysis_obj, data, webhook_response)
                
                # Download the JSON file
                json_document = LoanDocument.objects.get(
                    application=bank_analysis_obj.application,
                    document_type="BSA_JSON_FILE"
                )
                json_file_url = json_document.file.url
                json_data = requests.get(json_file_url).json()
                
                # Instantiate FieldsForCamCaluculator and perform calculations
                financial_calculator = FieldsForCamCaluculator(json_data["Data"])
                cash_flow = financial_calculator.calculate_cash_flow()
                average_monthly_balance = financial_calculator.calculate_average_monthly_balance()
                leverage_to_income = financial_calculator.calculate_leverage_to_income(average_monthly_balance)
                
                # Update the bank_analysis_obj with the new fields
                bank_analysis_obj.cash_flow = cash_flow
                bank_analysis_obj.average_monthly_balance = average_monthly_balance
                bank_analysis_obj.leverage_to_income = leverage_to_income
                
                # Save the updated object
                bank_analysis_obj.save()
                # Update the application status to BANK_STATEMENT_REPORT_GENERATED
                application_obj = bank_analysis_obj.application
                application_obj.status = APPLICATION_STATUS.BANK_STATEMENT_REPORT_GENERATED.value
                application_obj.save()

                return Response(status=status.HTTP_201_CREATED)
            else:
                return HttpResponse.BadRequest("ResponseCode is not SRC001.")
        except ScoreMeBankAnalysis.DoesNotExist:
            return HttpResponse.BadRequest("Bank analysis object not found.")
        except KeyError as e:
            return HttpResponse.BadRequest(f"Missing key: {str(e)}")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
