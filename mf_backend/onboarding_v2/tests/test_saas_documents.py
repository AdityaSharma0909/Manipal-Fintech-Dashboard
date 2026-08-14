import json
import shutil
import tempfile
from unittest.mock import patch


from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import ApplicationDocument, ApplicationStageSnapshot, ApplicationV2, LeadV2, Packet, JewelleryItem
from onboarding_v2.saas import build_create_loan_payload, build_rh_approval_notification_payload


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    SAAS_PRODUCT_ID="MANIPA__GOLD",
)
class SaasDocumentPayloadTests(TestCase):
    """
    Validate that document URLs are injected into the SAAS create-loan payload
    using presigned GET URLs.
    """

    def setUp(self):
        # Force local file storage for test uploads
        self._tmp_media = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self._tmp_media, ignore_errors=True))
        self._settings_cm = self.settings(
            MEDIA_ROOT=self._tmp_media,
            DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
        )
        self._settings_cm.enable()
        self.addCleanup(self._settings_cm.disable)

        self.lead = LeadV2.objects.create(
            customer_id="CUST-DOC-1",
            contact_number="9000000000",
            customer_name="Doc User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-DOC-1", lead=self.lead)

        # Minimal post-screen snapshots required by the builder
        ApplicationStageSnapshot.objects.bulk_create(
            [
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BASIC,
                    payload={
                        "full_name_as_pan": "Doc User",
                        "dob": "1990-01-01",
                        "dob_as_per_pan": "1990-01-01",
                        "phone_number": "9000000000",
                        "gender": "MALE",
                        "aadhar_number": "123412341234",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.PERSONAL,
                    payload={
                        "full_name": "Doc User",
                        "dob": "1990-01-01",
                        "dob_as_per_pan": "1990-01-01",
                        "gender": "MALE",
                        "category": "GENERAL",
                        "occupation": "ENGINEERS",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.ADDRESS,
                    payload={
                        "permanent": {"address_line1": "Line 1", "pincode": "560001", "state": "KA", "city": "BLR"},
                        "current_same_as_permanent": True,
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.LOAN,
                    payload={"eligible_amount": "100000", "tenure_years": 6, "interest_rate": "10.0"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BANK,
                    payload={
                        "bank_name": "Axis Bank",
                        "account_number": "1234567890",
                        "customer_name_as_per_bank": "Doc User",
                        "ifsc_code": "UTIB0000123",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.GOLD,
                    payload={"items": [], "packet": {}},
                    is_complete=True,
                ),
            ]
        )

        # Documents we want mapped
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            file_url="https://cdn.example.com/PAN_CARD_BACK.jpg",
            metadata={"pan_number": "ABCDE1234F"},
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.AADHAAR,
            subtype="AADHAAR_FRONT",
            file_url="https://cdn.example.com/AADHAR_CARD.jpg",
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.AADHAAR,
            subtype="AADHAAR_BACK",
            file_url="https://cdn.example.com/AADHAR_CARD_BACK.jpg",
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.VOTER_ID,
            file_url="https://cdn.example.com/VOTER_CARD.jpg",
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.OTHER,
            subtype="bureau_report",
            file_url="https://cdn.example.com/bureau.pdf",
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.SELFIE,
            file_url="https://cdn.example.com/selfie.jpg",
        )

        # Jewellery items with front/back URLs
        packet = Packet.objects.create(application=self.app, packet_id="PKT-TEST")
        JewelleryItem.objects.create(
            packet=packet,
            type_of_jewellery="BANGLE",
            number_of_articles=1,
            gross_weight="10",
            net_adjusted_weight="9",
            metadata={
                "front_image_url": "https://cdn.example.com/bangle_front.jpg",
                "back_image_url": "https://cdn.example.com/bangle_back.jpg",
            },
        )

    def _presign_side_effect(self, file_url=None, object_name=None):
        # Return a deterministic presigned URL to assert against
        name = object_name or file_url.split("/")[-1]
        return {"get_url": f"https://signed.example.com/{name}"}

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_document_urls_are_included_in_create_loan_payload(self, mock_presign):
        mock_presign.side_effect = self._presign_side_effect

        payload = build_create_loan_payload(self.app)

        # PAN mapped to pannumberUrl
        self.assertEqual(payload.get("pannumberUrl"), ["https://signed.example.com/PAN_CARD_BACK.jpg"])
        # Aadhaar front/back mapped to aadharNumberLink
        self.assertCountEqual(
            payload.get("aadharNumberLink"),
            ["https://signed.example.com/AADHAR_CARD.jpg", "https://signed.example.com/AADHAR_CARD_BACK.jpg"],
        )
        # Voter ID
        self.assertEqual(payload.get("votingIdLink"), ["https://signed.example.com/VOTER_CARD.jpg"])
        # Bureau report
        self.assertEqual(payload.get("bureauReportUrl"), "https://signed.example.com/bureau.pdf")
        # Approved selfie
        self.assertEqual(payload.get("selfieUrl"), ["https://signed.example.com/selfie.jpg"])
        # Jewellery images (from JewelleryItem front/back) with code-based filenames (BANGLE -> BN)
        self.assertEqual(
            payload.get("jewelleryUrl"),
            [
                "https://signed.example.com/BN_FRONT_1.jpg",
                "https://signed.example.com/BN_BACK_1.jpg",
            ],
        )
        # Unmapped fields should not be injected
        self.assertNotIn("form60Url", payload)
        self.assertNotIn("utilityBillsUrl", payload)

        # Ensure base required fields still present
        self.assertEqual(payload["productId"], "MANIPA__GOLD")
        self.assertEqual(payload["agreementId"], "2605")
        self.assertEqual(payload["clientLoanId"], self.app.application_id)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_rh_approval_notification_includes_selfie_url(self, mock_presign):
        mock_presign.side_effect = self._presign_side_effect
        self.app.rh_remarks = "Approved"

        payload = build_rh_approval_notification_payload(self.app)

        self.assertEqual(
            payload,
            {
                "applicationId": self.app.application_id,
                "status": "RH",
                "remarks": "Approved",
                "selfieUrl": "https://signed.example.com/selfie.jpg",
            },
        )
