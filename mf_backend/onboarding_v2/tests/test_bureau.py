from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import ApplicationDocument, ApplicationStageSnapshot, ApplicationV2, LeadV2
from onboarding_v2.bureau import build_bureau_payload, BureauError


@override_settings(
    MIGRATION_MODULES={
        "onboarding_v2": None,
        "users": None,
        "lead": None,
        "lender": None,
    },
)
class BureauPayloadTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-456",
            contact_number="8888888888",
            customer_name="Jane Smith",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-456",
            lead=self.lead,
        )

    def _create_snapshots(self):
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PAN,
            payload={"pan_number": "ABCDE6789Z", "name_on_pan": "Jane Smith", "dob_as_per_pan": "1992-02-02"},
            is_complete=True,
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            metadata={"pan_number": "ABCDE6789Z"},
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Jane Smith",
                "dob": "1992-02-02",
                "dob_as_per_pan": "1992-02-02",
                "phone_number": "8888888888",
                "gender": "FEMALE",
                "aadhar_number": "999988887777",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "456 High St",
                    "pincode": "560002",
                    "state": "KA",
                    "city": "Bengaluru",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )

    def test_build_bureau_payload(self):
        self._create_snapshots()
        payload = build_bureau_payload(self.app)
        self.assertEqual(payload["pan"], "ABCDE6789Z")
        self.assertEqual(payload["firstName"], "Jane")
        self.assertEqual(payload["lastName"], "Smith")
        self.assertEqual(str(payload["pincode"]), "560002")

    def test_build_bureau_payload_missing(self):
        with self.assertRaises(BureauError):
            build_bureau_payload(self.app)
