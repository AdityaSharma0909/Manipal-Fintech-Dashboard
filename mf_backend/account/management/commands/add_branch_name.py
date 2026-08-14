from django.core.management.base import BaseCommand
import requests
from account.models import BankAccount

class Command(BaseCommand):
    help = 'Fetches branch name using IFSC and updates the BankAccount table'

    def handle(self, *args, **kwargs):
        # Fetch all BankAccount records from the database
        bank_accounts = BankAccount.objects.all()

        for account in bank_accounts:
            # Get the IFSC code from the current BankAccount object
            ifsc_code = account.ifsc
            # Construct the API URL using the IFSC code
            api_url = f'https://ifsc.razorpay.com/{ifsc_code}'

            try:
                # Send a GET request to the API URL
                response = requests.get(api_url)
                # Raise an exception if the response status code is not in the 2xx range
                response.raise_for_status()
                # Parse the response JSON data
                data = response.json()
                # Get the BRANCH value from the JSON data
                branch_name = data.get('BRANCH')

                if branch_name:
                    # If the BRANCH value is present, update the branch_name field of the BankAccount object
                    account.branch_name = branch_name
                    # Save the changes to the database
                    account.save()
                    # self.stdout.write() method is used to print output to the console or terminal
                    self.stdout.write(self.style.SUCCESS(f'Updated branch name for IFSC {ifsc_code} to {branch_name}'))
                else:
                    # If the BRANCH value is not present, print a warning message
                    self.stdout.write(self.style.WARNING(f'No branch name found for IFSC {ifsc_code}'))

            except requests.exceptions.RequestException as e:
                # If there's an error fetching data from the API, print an error message
                self.stdout.write(self.style.ERROR(f'Error fetching data for IFSC {ifsc_code}: {e}'))











