from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch

from onboarding_v2.models import LeadV2
from users.models import User


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class IciciDuplicateLeadTests(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username="agent-1", password="Pass@123")
        self.client.force_authenticate(user=self.user)

    def _payload(self, contact_number="9123549511"):
        return {
            "contact_number": contact_number,
            "customer_name": "Anishi Mondal",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": "150000",
            "pincode": "560001",
            "source": "SELF",
            "lending_partner": "ICICI Bank",
            "bank": "ICICI Bank",
            "bank_branch": "MG Road Branch",
            "gender": "FEMALE",
            "dob": "1995-08-15",
            "pan_number": "AQIPG4459M",
            "is_pan_verified": True,
        }

    @patch("onboarding_v2.views.leads.sendToIcici")
    def test_icici_duplicate_business_response_returns_bad_request(self, mock_send_to_icici) -> None:
        mock_send_to_icici.return_value = {
            "IsSucessCode": True,
            "Response": (
                '{"StatusCode":"OK","StatusText":"OK","Response":"A lead already exists '
                "with same details. New Lead Cannot be created. Duplicate Lead Id's: DC000873596\"}"
            ),
            "statusCode": "200",
            "statusText": "OK",
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=self._payload(), format="json")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("ICICI integration rejected", resp.json().get("error_msg", ""))
        self.assertFalse(LeadV2.objects.filter(contact_number="9123549511").exists())

    @patch("onboarding_v2.views.leads.sendToIcici")
    def test_icici_successful_lead_creation(self, mock_send_to_icici) -> None:
        mock_send_to_icici.return_value = {
            "Response": '{"StatusCode":"OK","StatusText":"OK","Response":"Lead Number is ICICI12345"}',
            "statusCode": "200",
            "statusText": "OK",
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=self._payload("9123549512"), format="json")

        self.assertEqual(resp.status_code, 200)
        lead = LeadV2.objects.get(contact_number="9123549512")
        self.assertEqual(lead.BankLeadID, "ICICI12345")

    @patch("onboarding_v2.views.leads.sendToIcici")
    def test_icici_missing_bank_lead_id_returns_bad_request(self, mock_send_to_icici) -> None:
        mock_send_to_icici.return_value = {
            "Response": '{"StatusCode":"OK","StatusText":"OK","Response":"Lead request processed"}',
            "statusCode": "200",
            "statusText": "OK",
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=self._payload("9123549513"), format="json")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("BankLeadID was not returned", resp.json().get("error_msg", ""))
        self.assertFalse(LeadV2.objects.filter(contact_number="9123549513").exists())
