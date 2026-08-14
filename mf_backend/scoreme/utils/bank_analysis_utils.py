from django.conf import settings
import requests
from scoreme.models import ScoreMeBankAnalysis
import json
import os
from django.core.files.base import ContentFile
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from application.models import LoanDocument
from django.db import transaction

class BsaUtils:
    
    def get_headers():
        """
        Get headers required for the API requests.
        """
        return {
            'clientId': settings.SCORE_ME_CLIENT_ID,
            'clientSecret': settings.SCORE_ME_CLIENT_SECRET
        }

    def process_bank_statements(bank_statement_1, bank_statement_2=None, password1=None, password2=None):
        """
        Process the bank statements and prepare files and file_passwords for upload.
        """
        files = []
        file_passwords = {}

        def process_statement(statement, password):
            if not statement:
                return None

            # Retrieve the file URL and name
            file_url = statement.file.url
            file_name = file_url.rsplit('/', 1)[-1]

            # Download the file content
            response = requests.get(file_url)
            response.raise_for_status()

            # Append file and its password (if protected) to the respective lists
            files.append(('file', (file_name, response.content, 'application/pdf')))
            file_passwords[file_name] = password if statement.is_password else None

        # Process the first bank statement
        process_statement(bank_statement_1, password1)
        # Process the second bank statement if it exists
        process_statement(bank_statement_2, password2)
        
        return files, file_passwords

    def create_bsa_payload(file_passwords):
        """
        Create the payload for the bank statement analysis API.
        """
        return {'data': json.dumps({'filePassword': file_passwords})}

    def call_upload_statement_api(payload, files):
        """
        Call the API to upload bank statement files.
        """
        url = settings.SCORE_ME_BASE_URL + "/bsa/external/uploadBankStatementFiles/v4"
        headers = BsaUtils.get_headers()
        
        # Make the API request to upload the files
        response = requests.post(url, headers=headers, data=payload, files=files)
        print("*** Response after uploading bank statements: ", response)
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()

    def create_scoreme_bank_analysis_object(application_id, reference_id):
        """
        Create a new ScoreMeBankAnalysis object.
        """
        return ScoreMeBankAnalysis.objects.create(
            application_id=application_id,
            reference_id=reference_id,
        )

    def call_merge_bsa_report_api(reference_id_1, reference_id_2):
        """
        Call the API to merge two bank statement analysis reports.
        """
        url = settings.SCORE_ME_BASE_URL + "/bsa/external/mergebankstatement"
        headers = BsaUtils.get_headers()
        payload = {
            "referenceIds": [reference_id_1, reference_id_2]
        }
        
        # Make the API request to merge the reports
        response = requests.post(url, json=payload, headers=headers)
        print("--- Response after merging bank statements: ", response)
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()

    def get_bank_analysis_object(reference_id):
        """
        Retrieve a ScoreMeBankAnalysis object using the reference ID.
        """
        return ScoreMeBankAnalysis.objects.get(reference_id=reference_id)

    def update_bank_analysis_object(bank_analysis_obj, data, webhook_response):
        """
        Update a ScoreMeBankAnalysis object with new data and save files to LoanDocument.
        """
        bank_analysis_obj.json_url = data['data']['jsonUrl']
        bank_analysis_obj.excel_url = data['data']['excelUrl']
        bank_analysis_obj.webhook_response = webhook_response

        # Extract file names from the URLs
        json_filename = os.path.basename(data['data']['jsonUrl'])
        # excel_filename = os.path.basename(data['data']['excelUrl'])
        
        # Get the application associated with this bank analysis
        application = bank_analysis_obj.application
        
        excel_filename = f"ScoreMe_{application.application_number}.xlsx"
        # Download and save the JSON file
        BsaUtils.download_and_save_file(url=data['data']['jsonUrl'], filename=json_filename, document_type="BSA_JSON_FILE", application=application)

        # Download and save the Excel file
        BsaUtils.download_and_save_file(url=data['data']['excelUrl'], filename=excel_filename, document_type="BSA_EXCEL_FILE", application=application)

        # Save the updated bank analysis object
        bank_analysis_obj.save()

    @transaction.atomic
    def download_and_save_file(url, filename, document_type, application):
        """
        Download a file from a URL and save it as a LoanDocument.
        If a document of the same type already exists, update it instead of creating a new one.
        """
        headers = BsaUtils.get_headers()
        
        # Make the request to download the file
        response = requests.get(url, headers=headers)

        # Try to get an existing LoanDocument
        loan_document, created = LoanDocument.objects.get_or_create(application=application, document_type=document_type, defaults={'file_name': filename,})

        # If the document already existed, update its file_name
        if not created:
            loan_document.file_name = filename

        # Save the new file content
        loan_document.file.save(filename, ContentFile(response.content), save=False)

        # Save the LoanDocument instance
        loan_document.save()


class FieldsForCamCaluculator:
    def __init__(self, data):
        self.data = data

    def get_last_six_months_dates(self):
        current_date = datetime.now()
        six_months_ago = current_date - relativedelta(months=6)
        print("+++ Six months ago as per current date: ", six_months_ago)
        return six_months_ago, current_date

    def calculate_cash_flow(self):
        six_months_ago, current_date = self.get_last_six_months_dates()
        total_credits = 0

        for statement in self.data.get("Bank Statement", []):
            transaction_date = datetime.strptime(statement["Date"], "%d-%m-%Y")
            if six_months_ago <= transaction_date <= current_date:
                total_credits += float(statement["Credit"])
        
        total_credits = round(total_credits, 2)
        print("``` total_credits: ", total_credits)
        return total_credits

    def calculate_average_monthly_balance(self):
        six_months_ago, current_date = self.get_last_six_months_dates()

        # Check in place because some JSON files have objects in Eod analysis, while others in EOD MONTH WISE
        if "Eod Analysis" in self.data:
            eod_month_wise = self.data["Eod Analysis"]
        elif "Eod analysis" in self.data and "EOD MONTH WISE" in self.data["Eod analysis"]:
            eod_month_wise = self.data["Eod analysis"]["EOD MONTH WISE"]
        last_six_months_data = []

        for record in eod_month_wise:
            record_date = datetime.strptime(record["monthYear"], "%b %Y")
            if six_months_ago <= record_date <= current_date:
                last_six_months_data.append(float(record["averageEod"]))

        if len(last_six_months_data) == 0:
            return 0
        
        average_monthly_balance = sum(last_six_months_data) / len(last_six_months_data)
        average_monthly_balance = round(average_monthly_balance, 2)
        print("*** average_monthly_balance: ", average_monthly_balance)
        return average_monthly_balance

    def calculate_leverage_to_income(self, average_monthly_balance):
        leverage_income = average_monthly_balance * 1.5
        leverage_income = round(leverage_income, 2)
        print("*** leverage_income: ", leverage_income)
        return leverage_income