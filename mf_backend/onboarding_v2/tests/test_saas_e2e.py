import json
from datetime import date
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import (
    ApplicationDocument,
    ApplicationStageSnapshot,
    ApplicationV2,
    LeadV2,
)


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
    SAAS_URL="https://uat-manipal-api.finncub.com/kyc/api/lead/addLeadDetail",
    SAAS_CREATE_LOAN_URL="https://uat-manipal-api.finncub.com/kyc/api/lead/createLoan",
    SAAS_ACCESS_KEY_PRE_SCREEN="d88dd0722a834114b99ed1dc83260a35",
    SAAS_SECRET_KEY_PRE_SCREEN="e9920f996e184895a0726e24e98b46c2",
    SAAS_CLIENT_CODE_PRE_SCREEN="UAT-MANIPAL",
    SAAS_ACCESS_KEY_CREATE_LOAN="0722a834114d88ddb99ed1dc832",
    SAAS_SECRET_KEY_CREATE_LOAN="996e184895ae9920f0726e24e98b",
    SAAS_CLIENT_CODE_CREATE_LOAN="UAT-GETAFIX",
    SAAS_PRODUCT_ID="MANIPA__GOLD",
    SAAS_MODEL_NAME="CLM1",
    SAAS_WEBHOOK_SECRET="secret-token",
)
class SaasEndToEndTests(TestCase):
    """
    Simulates the SAAS Tech pre-screen -> webhook -> create-loan flow with mocked tasks/HTTP.
    """

    def setUp(self):
        self.client = Client()
        self.lead = LeadV2.objects.create(
            customer_id="CUST-SAAS-1",
            contact_number="9000000000",
            customer_name="Flow User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-SAAS-1", lead=self.lead)

        # Minimal artifacts required by payload builders
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            metadata={"pan_number": "ABCDE1234F"},
            file_url="https://example.com/pan.jpg",
        )
        # Pre-screen snapshots
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PAN,
            payload={"pan_number": "ABCDE1234F", "name_on_pan": "Flow User", "dob_as_per_pan": "1990-01-01"},
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Flow User",
                "dob": "1990-01-01",
                "dob_as_per_pan": "1990-01-01",
                "phone_number": "9000000000",
                "gender": "MALE",
                "aadhar_number": "123412341234",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {"address_line1": "Line 1", "pincode": "560001", "state": "KA", "city": "BLR"},
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )
        # Post-screen snapshots for create-loan
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PERSONAL,
            payload={"full_name": "Flow User", "dob": "1990-01-01", "dob_as_per_pan": "1990-01-01", "gender": "MALE"},
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LOAN,
            payload={
                "eligible_amount": "100000",
                "tenure_years": 6,
                "interest_rate": "10.0",
                "purpose": "BUSINESS_NEEDS",
                "loan_subcategory": "FRESH",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BANK,
            payload={
                "bank_name": "Axis Bank",
                "account_number": "1234567890",
                "customer_name_as_per_bank": "Flow User",
                "ifsc_code": "UTIB0000123",
                "branch_name": "Main",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.GOLD,
            payload={"items": [], "packet": {}},
            is_complete=True,
        )

    @patch("onboarding_v2.helpers.saas_helpers.submit_pre_screen_task.delay")
    def test_pre_screen_to_create_loan_flow(self, mock_pre_screen_delay):
        # Submit pre-screen
        resp = self.client.post(f"/api/v2/onboarding/applications/{self.app.application_id}/submit/", data={})
        self.assertEqual(resp.status_code, 200)
        mock_pre_screen_delay.assert_called_once()

        # Webhook marks eligible and queues bureau
        with patch("onboarding_v2.views.run_bureau_check_task.delay") as mock_bureau:
            webhook_resp = self.client.post(
                "/api/v2/onboarding/webhooks/saastech/pre-screen/",
                {"applicationId": self.app.application_id, "status": "ELIGIBLE"},
                HTTP_X_SAAS_TOKEN="secret-token",
            )
            self.assertEqual(webhook_resp.status_code, 200)
            mock_bureau.assert_called_once()

        # Finalize triggers create-loan enqueue with full payload
        with patch("onboarding_v2.helpers.saas_helpers.create_loan_task.delay") as mock_create:
            final_resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/finalize/",
                data=json.dumps({}),
                content_type="application/json",
            )
            self.assertEqual(final_resp.status_code, 200)
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            payload = args[1]
            # Sanity checks on payload keys critical to SAAS contract
            self.assertEqual(payload["productId"], "MANIPA__GOLD")
            self.assertEqual(payload["agreementId"], "2605")
            self.assertEqual(payload["nameOfBureau"], "experian")  # default
            self.assertEqual(payload["clientLoanId"], self.app.application_id)
            self.assertIn("disbursementAccounts", payload)
            self.assertEqual(payload["fatcaVerificationOfficialBranch"], "Gurgaon")
            self.assertEqual(payload["fatcaVerificationOfficialDesignation"], "SO")

    def test_webhook_rejects_invalid_token_or_missing_app(self):
        # Invalid token should 400
        resp = self.client.post(
            "/api/v2/onboarding/webhooks/saastech/pre-screen/",
            {"applicationId": self.app.application_id, "status": "ELIGIBLE"},
            HTTP_X_SAAS_TOKEN="bad-token",
        )
        self.assertEqual(resp.status_code, 400)

        # Valid token but unknown application should 400
        resp = self.client.post(
            "/api/v2/onboarding/webhooks/saastech/pre-screen/",
            {"applicationId": "MISSING-APP", "status": "ELIGIBLE"},
            HTTP_X_SAAS_TOKEN="secret-token",
        )
        self.assertEqual(resp.status_code, 400)
