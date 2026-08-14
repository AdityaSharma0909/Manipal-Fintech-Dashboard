import requests
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class V2IntegrationClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.lead_id = None
        self.application_id = None

    def login(self, username, password):
        logging.info("Logging in...")
        url = f"{self.base_url}/user/login/"
        payload = {
            "username": username,
            "password": password,
            "platform": "phone"
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Raw Login Response: {json.dumps(data, indent=2)}")

        # Token is located in data['data']['user']['access_token'] based on our debugging output
        user_data = data.get('data', {}).get('user', {})
        self.token = user_data.get('access_token') or data.get('token')

        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            logging.info("Login successful. Token obtained.")
        else:
            logging.warning("Login succeeded but no token was found in the response.")

        return data

    def create_lead(self, payload=None):
        logging.info("Creating V2 Lead...")
        url = f"{self.base_url}/api/v2/onboarding/leads/"

        # Default payload if none provided
        if not payload:
            payload = {
                "customer_name": "Test User",
                "contact_number": "9988776655", # Use a unique number or clear db if testing multiple times
                "lead_type": "FRESH",
                "product_category": "LOAN",
                "product_subcategory": "PERSONAL_LOAN"
            }

        response = self.session.post(url, json=payload)

        try:
            response.raise_for_status()
            data = response.json()

            # Adjust based on your LeadCreateSerializer response
            lead_data = data.get('data', {}).get('lead', {}) or data.get('lead', {})
            self.lead_id = lead_data.get('id')
            logging.info(f"Lead created successfully. Lead ID: {self.lead_id}")
            return data
        except requests.exceptions.HTTPError as e:
            logging.error(f"Failed to create lead. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            raise e

    def create_application(self, payload=None):
        if not self.lead_id:
            logging.error("No lead_id available. Please create a lead first.")
            return None

        logging.info("Creating V2 Application...")
        url = f"{self.base_url}/api/v2/onboarding/applications/"

        if not payload:
            payload = {
                "lead": self.lead_id,
            }
        else:
            # Ensure lead_id is injected if not present
            if "lead" not in payload:
                payload["lead"] = self.lead_id

        response = self.session.post(url, json=payload)

        try:
            response.raise_for_status()
            data = response.json()

            app_data = data.get('data', {}).get('application', {}) or data.get('application', {})
            self.application_id = app_data.get('application_id') or app_data.get('id')
            logging.info(f"Application created successfully. Application ID: {self.application_id}")
            return data
        except requests.exceptions.HTTPError as e:
            logging.error(f"Failed to create application. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            raise e

    def update_application_stage(self, application_id, payload):
        logging.info(f"Updating V2 Application {application_id} stage...")
        url = f"{self.base_url}/api/v2/onboarding/applications/{application_id}/stage/"
        response = self.session.post(url, json=payload)
        
        try:
            response.raise_for_status()
            data = response.json()
            logging.info(f"Application stage updated successfully.")
            return data
        except requests.exceptions.HTTPError as e:
            logging.error(f"Failed to update application stage. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            raise e

if __name__ == "__main__":
    import argparse
    import sys
    import os
    import environ

    # Initialize environ and read .env file if it exists
    env = environ.Env()
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        environ.Env.read_env(env_file)

    default_base_url = env('BASE_URL', default="http://127.0.0.1:8000")

    parser = argparse.ArgumentParser(description="V2 API Integration Script")
    parser.add_argument("--base-url", default=default_base_url, help="Base URL of the API")
    parser.add_argument("--username", required=True, help="Username to login")
    parser.add_argument("--password", required=True, help="Password to login")
    parser.add_argument("--customer-name", default="Test User", help="Name of the lead customer")
    parser.add_argument("--contact-number", default="9988776655", help="Contact number of the lead")
    parser.add_argument("--product-subcategories", default="PERSONAL_LOAN,GOLD_LOAN", help="Comma separated list of product subcategories to test, or 'ALL'")

    args = parser.parse_args()

    client = V2IntegrationClient(args.base_url)

    try:
        # 1. Login
        print(f"Attempting to login to {args.base_url}/user/login/ ...")
        client.login(args.username, args.password)
        print(f"Login successful! Token: {client.token}")

        subcategories = [s.strip().upper() for s in args.product_subcategories.split(',')]
        if 'ALL' in subcategories:
            subcategories = [
                "GOLD_LOAN", "HOME_LOAN", "PERSONAL_LOAN", "BUSINESS_LOAN", 
                "LOAN_AGAINST_PROPERTY", "MOTOR_LOAN", "HEALTH_INSURANCE", "MOTOR_INSURANCE"
            ]

        base_contact = args.contact_number
        if len(base_contact) == 10 and base_contact.isdigit():
            base_contact_int = int(base_contact)
        else:
            base_contact_int = 9988776655

        for i, subcat in enumerate(subcategories):
            if not subcat:
                continue
                
            product_category = "INSURANCE" if "INSURANCE" in subcat else "LOAN"
            current_contact = str(base_contact_int + i)

            print(f"\n{'-'*40}")
            print(f"--- Testing for Product: {product_category} / {subcat} ---")
            print(f"{'-'*40}")
            print(f"Attempting to create V2 Lead with contact {current_contact}...")

            payload = {
                "customer_name": f"{args.customer_name} {subcat}",
                "contact_number": current_contact,
                "lead_type": "FRESH",
                "product_category": product_category,
                "product_subcategory": subcat
            }

            try:
                lead_response = client.create_lead(payload)
                print(f"Lead creation successful! Response: {json.dumps(lead_response, indent=2)}")

                print("\nAttempting to create V2 Application...")
                app_response = client.create_application()
                print(f"Application creation successful! Response: {json.dumps(app_response, indent=2)}")

                if client.application_id:
                    print(f"\nAttempting to update application {client.application_id} to stage PAN...")
                    pan_payload = {
                        "stage": "PAN",
                        "is_complete": True,
                        "payload": {
                            "contact_number": current_contact,
                            "pan_number": "ABCDE1234F",
                            "name_on_pan": f"{args.customer_name} {subcat}".upper(),
                            "dob_as_per_pan": "1990-01-01"
                        }
                    }
                    stage_response = client.update_application_stage(client.application_id, pan_payload)
                    print(f"Stage update successful! Response: {json.dumps(stage_response, indent=2)}")
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP Error occurred for {subcat}: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logging.error(f"An error occurred for {subcat}: {str(e)}")

    except Exception as e:
        logging.error(f"A critical error occurred: {str(e)}")
