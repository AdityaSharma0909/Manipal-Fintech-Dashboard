from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import (
    ApplicationDocument,
    ApplicationStageSnapshot,
    ApplicationV2,
    LeadV2,
)
from onboarding_v2.saas import (
    build_pre_screen_payload,
    validate_pre_screen_requirements,
)


@override_settings(
    MIGRATION_MODULES={
        "onboarding_v2": None,
        "users": None,
        "lead": None,
        "lender": None,
    },
)
class PreScreenPayloadTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-123",
            lead_code="GL0001",
            contact_number="9999999999",
            customer_name="John Doe",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-123",
            lead=self.lead,
        )

    def _create_snapshots(self, include_pan=True):
        if include_pan:
            ApplicationStageSnapshot.objects.create(
                application=self.app,
                stage=ApplicationStage.PAN,
                payload={
                    "pan_number": "ABCDE1234F",
                    "name_on_pan": "John Doe",
                    "dob_as_per_pan": "1990-01-01",
                },
                is_complete=True,
            )
            ApplicationDocument.objects.create(
                application=self.app,
                document_type=DocumentType.PAN,
                metadata={"pan_number": "ABCDE1234F"},
            )

        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "John Doe",
                "dob": "1990-01-01",
                "dob_as_per_pan": "1990-01-01",
                "phone_number": "9999999999",
                "gender": "MALE",
                "aadhar_number": "123412341234",
            },
            is_complete=True,
        )

        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "123 Main St",
                    "pincode": "560001",
                    "state": "KA",
                    "city": "Bengaluru",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LENDING_PARTNER_BANK,
            payload={
                "lending_partner": "AXIS_BANK",
                "client_loan_id": "GLN00567",
            },
            is_complete=True,
        )

    def test_validate_pre_screen_requirements_passes(self):
        self._create_snapshots()
        pan, basic, address, pan_number = validate_pre_screen_requirements(self.app)
        self.assertEqual(pan_number, "ABCDE1234F")
        self.assertEqual(basic["phone_number"], "9999999999")
        self.assertEqual(address["permanent"]["city"], "Bengaluru")

    def test_validate_pre_screen_requirements_missing_pan(self):
        self._create_snapshots(include_pan=False)
        with self.assertRaises(ValueError):
            validate_pre_screen_requirements(self.app)

    def test_build_pre_screen_payload(self):
        self._create_snapshots()
        payload = build_pre_screen_payload(self.app)
        self.assertEqual(payload["customerId"], "CUST-123")
        self.assertEqual(payload["leadId"], "GL0001")
        self.assertEqual(payload["clientLoanId"], "GLN00567")
        self.assertEqual(payload["applicationId"], "APP-123")
        self.assertEqual(payload["pan"], "ABCDE1234F")
        self.assertEqual(payload["firstName"], "John")
        self.assertEqual(payload["lastName"], "Doe")
        self.assertEqual(payload["address"][0]["addressPincode"], "560001")
