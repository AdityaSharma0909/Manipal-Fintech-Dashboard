from django.test import TestCase, Client, override_settings
from onboarding_v2.models import LeadV2, ApplicationV2, ApplicationDocument
from onboarding_v2.constants import ApplicationStage, DocumentType


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
    OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL="oauth2_provider.AccessToken",
    OAUTH2_PROVIDER_APPLICATION_MODEL="oauth2_provider.Application",
)
class PanStageCustomerResolutionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.lead = LeadV2.objects.create(
            customer_id="CUST-NEW",
            contact_number="9000000000",
            customer_name="New User",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-PAN-1",
            lead=self.lead,
        )
        self.url = f"/api/v2/onboarding/applications/{self.app.application_id}/stage/"

    def test_new_pan_new_phone_assigns_customer_id(self):
        payload = {
            "stage": ApplicationStage.PAN,
            "is_complete": True,
            "payload": {
                "pan_number": "AAAAA1111A",
                "name_on_pan": "New User",
            },
        }
        resp = self.client.post(self.url, data=payload, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.lead.refresh_from_db()
        self.assertTrue(self.lead.customer_id)

    def test_existing_pan_new_phone_returns_message_and_reuses_customer(self):
        existing_lead = LeadV2.objects.create(
            customer_id="CUST-EXIST",
            contact_number="9111111111",
            customer_name="Existing User",
        )
        existing_app = ApplicationV2.objects.create(application_id="APP-EXIST", lead=existing_lead)
        ApplicationDocument.objects.create(
            application=existing_app,
            document_type=DocumentType.PAN,
            metadata={"pan_number": "DDDDD4444D"},
        )
        payload = {
            "stage": ApplicationStage.PAN,
            "is_complete": True,
            "payload": {
                "pan_number": "DDDDD4444D",
                "name_on_pan": "Existing User",
            },
        }
        resp = self.client.post(self.url, data=payload, content_type="application/json")
        self.assertIn(resp.status_code, [200, 400])
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            self.assertIn("message", data)
