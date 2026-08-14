from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch
from users.models import User
from onboarding_v2.models import LeadV2


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class BajajDuplicateLeadTests(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username="agent-1", password="Pass@123")
        self.client.force_authenticate(user=self.user)

    @patch("onboarding_v2.views.leads.sendToBajaj")
    def test_bajaj_duplicate_lead_returns_bad_request(self, mock_send_to_bajaj) -> None:
        # Mocking the response of sendToBajaj to mimic a duplicate/rejected lead response
        mock_send_to_bajaj.return_value = {
            'status': 'Success',
            'statusCode': 200,
            'message': 'Successful request',
            'data': {
                'remarks': 'Lead against mobile no. already EXISTS',
                'lead_id': 15575565,
                'status': 'REJECT',
                'loan_officier_id': None,
                'loan_officer_mobile': '8672872877',
                'loan_officier_name': None,
                'branch': None,
                'customer_type': ''
            }
        }

        payload = {
            "contact_number": "9372364858",
            "customer_name": "Vicky Yadav",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": "20400.00",
            "pincode": "360050",
            "source": "SELF",
            "bank": "Bajaj Finserv"
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn(
            "Bajaj integration rejected: Lead against mobile no. already EXISTS, existing lead_id: 15575565",
            resp.json().get("error_msg", ""),
        )

        # Verify no lead is created for this contact number
        self.assertFalse(LeadV2.objects.filter(contact_number="9372364858").exists())

        # Verify BankLeadTrace status is REJECTED and bank_lead_id is None
        from onboarding_v2.models import BankLeadTrace
        trace = BankLeadTrace.objects.filter(contact_number="9372364858").first()
        self.assertIsNotNone(trace)
        self.assertEqual(trace.status, BankLeadTrace.Status.REJECTED)
        self.assertIsNone(trace.bank_lead_id)

    @patch("onboarding_v2.views.leads.sendToBajaj")
    def test_bajaj_successful_lead_creation(self, mock_send_to_bajaj) -> None:
        mock_send_to_bajaj.return_value = {
            'status': 'Success',
            'statusCode': 200,
            'message': 'Successful request',
            'data': {
                'remarks': 'Lead created successfully',
                'lead_id': 15575565,
                'status': 'SUCCESS',
                'loan_officier_id': None,
                'loan_officer_mobile': '8672872877',
                'loan_officier_name': None,
                'branch': None,
                'customer_type': ''
            }
        }

        payload = {
            "contact_number": "9372364859",
            "customer_name": "Vicky Yadav",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": "20400.00",
            "pincode": "360050",
            "source": "SELF",
            "bank": "Bajaj Finserv"
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(LeadV2.objects.filter(contact_number="9372364859").exists())

    @patch("onboarding_v2.views.leads.sendToBajaj")
    def test_bajaj_failed_request_returns_bad_request(self, mock_send_to_bajaj) -> None:
        # Mocking the response of sendToBajaj to mimic a failed request
        mock_send_to_bajaj.return_value = {
            "status": "Fail",
            "statusCode": 400,
            "message": "Invalid Request",
            "data": None
        }

        payload = {
            "contact_number": "9372364857",
            "customer_name": "Vicky Yadav",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": "20400.00",
            "pincode": "360050",
            "source": "SELF",
            "bank": "Bajaj Finserv"
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Bajaj integration failed: Invalid Request", resp.json().get("error_msg", ""))

        # Verify no lead is created for this contact number
        self.assertFalse(LeadV2.objects.filter(contact_number="9372364857").exists())
