import json
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType, AddressType
from onboarding_v2.models import LeadV2, ApplicationV2, AddressV2


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    SAAS_WEBHOOK_SECRET="secret-token",
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
    SAAS_DOCUMENT_ID_MAP={"PAN": 101, "AADHAAR": 102},
)
class EndToEndStageFlowTests(TestCase):
    """
    End-to-end screen-wise flow via stage endpoint, mocking externals.
    """

    def setUp(self):
        self.client = Client()
        self.lead = LeadV2.objects.create(
            customer_id="CUST-999",
            contact_number="7000000000",
            customer_name="Flow User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-999", lead=self.lead)

    def _post_stage(self, stage, payload):
        return self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/stage/",
            data=json.dumps({"stage": stage, "payload": payload, "is_complete": True}),
            content_type="application/json",
        )

    @patch("onboarding_v2.views.enqueue_pre_screen")
    @patch("onboarding_v2.views.verify_pan_number", return_value=(True, {}))
    def test_full_flow_screenwise(self, _mock_pan_verify, mock_submit_task):
        # PAN
        resp = self._post_stage(
            ApplicationStage.PAN,
            {
                "contact_number": "7000000000",
                "pan_number": "ABCDE1234Z",
                "name_on_pan": "Flow User",
                "dob_as_per_pan": "1990-01-01",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # BASIC
        resp = self._post_stage(
            ApplicationStage.BASIC,
            {
                "full_name_as_pan": "Flow User",
                "dob": "1990-01-01",
                "dob_as_per_pan": "1990-01-01",
                "phone_number": "7000000000",
                "gender": "MALE",
                "aadhar_number": "123412341234",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # ADDRESS
        resp = self._post_stage(
            ApplicationStage.ADDRESS,
            {
                "permanent": {
                    "address_line1": "Line 1",
                    "pincode": "560001",
                    "state": "KA",
                    "district": "BLR",
                    "city": "BLR",
                },
                "current_same_as_permanent": True,
                "mailing": {
                    "address_line1": "Mailing Line 1",
                    "pincode": "560002",
                    "state": "KA",
                    "district": "BLR",
                    "city": "BLR",
                },
            },
        )
        self.assertEqual(resp.status_code, 200)
        mailing = AddressV2.objects.filter(application=self.app, address_type=AddressType.MAILING).first()
        self.assertIsNotNone(mailing)
        self.assertEqual(mailing.address_line1, "Mailing Line 1")
        # DOCUMENTS
        resp = self._post_stage(
            ApplicationStage.DOCUMENTS,
            [
                {"document_type": DocumentType.PAN, "status": "UPLOADED", "file_url": "https://example.com/pan.jpg"},
                {
                    "document_type": DocumentType.AADHAAR,
                    "subtype": "AADHAAR_FRONT",
                    "status": "UPLOADED",
                    "file_url": "https://example.com/aadhaar.jpg",
                    "metadata": {"aadhar_number": "123412341234"},
                },
            ],
        )
        self.assertEqual(resp.status_code, 200)
        # PERSONAL
        resp = self._post_stage(
            ApplicationStage.PERSONAL,
            {
                "full_name": "Flow User",
                "dob": "1990-01-01",
                "dob_as_per_pan": "1990-01-01",
                "gender": "MALE",
                "mobile_number": "7000000000",
                "marital_status": "MARRIED",
                "profession": "SALARIED",
                "category": "GENERAL",
                "religion": "HINDU",
                "foir": "0.5",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # ADDRESS SECONDARY (with POA)
        resp = self._post_stage(
            ApplicationStage.ADDRESS_SECONDARY,
            {
                "permanent": {
                    "address_line1": "Line 1",
                    "pincode": "560001",
                    "state": "KA",
                    "district": "BLR",
                    "city": "BLR",
                },
                "current_same_as_permanent": True,
                "poa": [
                    {
                        "document_type": DocumentType.AADHAAR,
                        "subtype": "AADHAAR_FRONT",
                        "status": "UPLOADED",
                        "file_url": "https://example.com/poa.jpg",
                    }
                ],
            },
        )
        self.assertEqual(resp.status_code, 200)
        # GOLD
        resp = self._post_stage(
            ApplicationStage.GOLD,
            {
                "items": [
                    {
                        "type_of_jewellery": "RING",
                        "number_of_articles": 1,
                        "purity": "22K",
                        "gross_weight": "10.0",
                        "stone_weight": "0.0",
                        "net_weight": "10.0",
                        "impurity_deducted": "0.0",
                        "net_adjusted_weight": "10.0",
                        "percent_of_gold": "100",
                        "actual_gold_rate": "6000",
                        "gross_value": "60000",
                        "net_value": "60000",
                        "net_adjusted_value": "60000",
                        "front_image_url": "https://cdn.example.com/ring_front.jpg",
                        "back_image_url": "https://cdn.example.com/ring_back.jpg",
                    }
                ],
                "packet_id": "PKT1",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # LOAN
        resp = self._post_stage(
            ApplicationStage.LOAN,
            {
                "eligible_amount": "100000",
                "requested_amount": "90000",
                "interest_rate": "10.5",
                "tenure_years": 6,
                "type_of_emi": "FIXED",
                "interest_type": "FIXED",
                "repayment_frequency": "BULLET",
                "category": "SECURED",
                "disbursement_type": "SINGLE",
                "purpose": "BUSINESS_NEEDS",
                "loan_subcategory": "FRESH",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # BANK
        resp = self._post_stage(
            ApplicationStage.BANK,
            {
                "bank_name": "Axis Bank",
                "account_number": "1234567890",
                "customer_name_as_per_bank": "Flow User",
                "ifsc_code": "UTIB0000123",
                "branch_name": "Main",
            },
        )
        self.assertEqual(resp.status_code, 200)
        # ADDITIONAL
        resp = self._post_stage(
            ApplicationStage.ADDITIONAL,
            {
                "is_employee": False,
                "nominee_relation": "SPOUSE",
                "nominee_full_name": "Spouse Name",
                "nominee_contact_number": "7000000001",
            },
        )
        self.assertEqual(resp.status_code, 200)

        # Submit pre-screen should enqueue task
        submit_resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/submit/",
            data={},
        )
        self.assertEqual(submit_resp.status_code, 200)

        # Finalize should enqueue create-loan and doc uploads
        with patch("onboarding_v2.views.enqueue_create_loan") as mock_create:
            final_resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/finalize/",
                data={},
            )
            self.assertEqual(final_resp.status_code, 200)
            mock_create.assert_called_once()
