import json
from pathlib import Path
from types import SimpleNamespace
from contextlib import nullcontext
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from onboarding_v2.constants import (
    ApplicationStage,
    DocumentType,
    LeadType,
    SELF_LENDING_STAGES,
)
from onboarding_v2.models import RoiConfigurationLeadType
from onboarding_v2.serializers import (
    AdditionalDetailsSerializer,
    AddressStageSerializer,
    ChargesDetailsSerializer,
    DocumentUploadSerializer,
    GoldPacketSerializer,
    EligibilityStageSerializer,
    LendingPartnerBankSerializer,
    LoanDetailsSerializer,
    PanStageSerializer,
    PersonalDetailsSerializer,
    ProductSelectionSerializer,
    SelfDeclarationSerializer,
)
from onboarding_v2.serializers.roi_configuration import RoiConfigurationSerializer
from onboarding_v2.saas import (
    _resolve_aadhar_number,
    validate_pre_screen_requirements,
)


class SelfLendingSerializerTests(SimpleTestCase):
    def setUp(self):
        self.application = SimpleNamespace(
            loan_type=LeadType.SELF_LENDING,
            lead=SimpleNamespace(
                lead_type=LeadType.SELF_LENDING,
                contact_number="9000000000",
                product_subcategory="GOLD_LOAN",
            ),
        )

    def test_self_declaration_requires_consent_and_verified_otp(self):
        serializer = SelfDeclarationSerializer(
            data={
                "consent_given": True,
                "otp_verified": False,
                "consent_text": "I consent to KYC and bureau checks.",
            },
            context={"application": self.application, "is_complete": True},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("otp_verified", serializer.errors)

    def test_self_declaration_records_timestamp_and_request_ip(self):
        request = APIRequestFactory().post(
            "/api/v2/onboarding/applications/MPAGL0001/stage/",
            REMOTE_ADDR="127.0.0.1",
        )
        serializer = SelfDeclarationSerializer(
            data={
                "consent_given": True,
                "otp_verified": True,
                "consent_text": "I consent to KYC and bureau checks.",
            },
            context={
                "application": self.application,
                "is_complete": True,
                "request": request,
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["consent_ip"], "127.0.0.1")
        self.assertIsNotNone(serializer.validated_data["consent_timestamp"])

    def test_personal_details_normalizes_professional_income(self):
        base_payload = {
            "full_name": "Test User",
            "dob": "1990-01-01",
            "dob_as_per_pan": "1990-01-01",
            "gender": "MALE",
            "mobile_number": "9000000000",
            "foir": "0.45",
        }
        for val in ["professional_income", "professional", "Professional Income", "PROFESSIONAL_INCOME"]:
            payload = base_payload.copy()
            payload["income_source"] = val
            serializer = PersonalDetailsSerializer(data=payload)
            self.assertTrue(serializer.is_valid(), f"Failed for {val}: {serializer.errors}")
            self.assertEqual(
                serializer.validated_data["income_source"],
                "PROFESSIONAL_INCOME"
            )

    def test_self_lending_loan_requires_figma_fields(self):
        serializer = LoanDetailsSerializer(
            data={"eligible_amount": "150000.00"},
            context={"application": self.application, "is_complete": True},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("requested_amount", serializer.errors)
        self.assertIn("purpose", serializer.errors)

    def test_charges_total_is_calculated(self):
        application = SimpleNamespace(
            processing_fee="100.00",
            stamp_duty="20.00",
            insurance_charges="30.00",
            documentation_charges="40.00",
            other_charges="10.00",
            stage_snapshots=SimpleNamespace(
                filter=lambda **kwargs: SimpleNamespace(
                    first=lambda: SimpleNamespace(
                        payload={"requested_amount": "1000.00"}
                    )
                )
            ),
        )
        serializer = ChargesDetailsSerializer(
            data={},
            context={"application": application, "is_complete": True},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(str(serializer.validated_data["total_charges"]), "200.00")
        self.assertEqual(
            str(serializer.validated_data["net_disbursement_amount"]), "800.00"
        )

    def test_roi_product_table_accepts_self_lending(self):
        serializer = RoiConfigurationSerializer()
        result = serializer.validate_lead_type(
            RoiConfigurationLeadType.SELF_LENDING
        )
        self.assertEqual(result, RoiConfigurationLeadType.SELF_LENDING)

    def test_self_lending_stage_order_matches_mobile_journey(self):
        self.assertEqual(
            [stage for stage, _ in SELF_LENDING_STAGES],
            [
                ApplicationStage.LENDING_PARTNER_BANK,
                ApplicationStage.PAN,
                ApplicationStage.ELIGIBILITY,
                ApplicationStage.PRODUCT_SELECTION,
                ApplicationStage.SELF_DECLARATION,
                ApplicationStage.DOCUMENTS,
                ApplicationStage.PERSONAL,
                ApplicationStage.ADDRESS,
                ApplicationStage.GOLD,
                ApplicationStage.LOAN,
                ApplicationStage.ADDITIONAL,
                ApplicationStage.CHARGES,
            ],
        )

    @patch("onboarding_v2.saas._get_documents")
    @patch("onboarding_v2.saas._get_snapshot_payload")
    def test_self_lending_pre_screen_uses_personal_instead_of_basic(
        self,
        get_snapshot_payload,
        _get_documents,
    ):
        payloads = {
            ApplicationStage.PAN: {
                "pan_number": "ABCDE1234F",
                "name_on_pan": "Self Lending Customer",
                "dob_as_per_pan": "1990-01-01",
            },
            ApplicationStage.BASIC: None,
            ApplicationStage.PERSONAL: {
                "full_name": "Self Lending Customer",
                "dob": "1990-01-01",
                "dob_as_per_pan": "1990-01-01",
                "mobile_number": "9000000000",
                "gender": "MALE",
                "email": "self.lending@example.com",
            },
            ApplicationStage.ADDRESS: {
                "permanent": {
                    "address_line1": "12 MG Road",
                    "pincode": "560001",
                    "state": "Karnataka",
                    "city": "Bengaluru",
                },
                "current_same_as_permanent": True,
            },
        }
        get_snapshot_payload.side_effect = (
            lambda application, stage: payloads.get(stage)
        )
        _get_documents.return_value = [
            SimpleNamespace(
                document_type=DocumentType.AADHAAR,
                subtype="AADHAAR_FRONT",
                metadata={
                    "aadhar_number": "999999999999",
                    "verified": True,
                },
            )
        ]

        pan, personal, address, pan_number = (
            validate_pre_screen_requirements(self.application)
        )

        self.assertEqual(pan_number, "ABCDE1234F")
        self.assertEqual(personal["full_name"], "Self Lending Customer")
        self.assertEqual(personal["mobile_number"], "9000000000")
        self.assertNotIn("full_name_as_pan", personal)
        self.assertEqual(address, payloads[ApplicationStage.ADDRESS])

    def test_pre_screen_reads_aadhar_from_front_document_metadata(self):
        documents = [
            SimpleNamespace(
                document_type=DocumentType.AADHAAR,
                subtype="AADHAAR_FRONT",
                metadata={
                    "aadhar_number": "999999999999",
                    "verified": True,
                },
            )
        ]

        self.assertEqual(
            _resolve_aadhar_number(documents),
            "999999999999",
        )

    def test_postman_collection_stage_payloads_complete_full_journey(self):
        collection_path = Path(__file__).resolve().parents[2] / (
            "MoneyPal Self Lending E2E.postman_collection.json"
        )
        collection = json.loads(collection_path.read_text())
        serializer_by_stage = {
            ApplicationStage.LENDING_PARTNER_BANK: LendingPartnerBankSerializer,
            ApplicationStage.PAN: PanStageSerializer,
            ApplicationStage.ELIGIBILITY: EligibilityStageSerializer,
            ApplicationStage.PRODUCT_SELECTION: ProductSelectionSerializer,
            ApplicationStage.SELF_DECLARATION: SelfDeclarationSerializer,
            ApplicationStage.DOCUMENTS: DocumentUploadSerializer,
            ApplicationStage.PERSONAL: PersonalDetailsSerializer,
            ApplicationStage.ADDRESS: AddressStageSerializer,
            ApplicationStage.GOLD: GoldPacketSerializer,
            ApplicationStage.LOAN: LoanDetailsSerializer,
            ApplicationStage.ADDITIONAL: AdditionalDetailsSerializer,
            ApplicationStage.CHARGES: ChargesDetailsSerializer,
        }
        validated_stages = []

        for item in collection["item"]:
            raw_body = item.get("request", {}).get("body", {}).get("raw")
            if not raw_body:
                continue
            raw_body = (
                raw_body.replace("{{mobile_number}}", "9000000000")
                .replace("{{pan_number}}", "ABCDE1234F")
                .replace("{{required_amount}}", "200000.00")
                .replace("{{tenure_months}}", "12")
                .replace("{{repayment_frequency}}", "BULLET")
                .replace("{{product_category}}", "GENERAL_PURPOSE")
                .replace("{{product_code}}", "SL_TEST_001")
            )
            body = json.loads(raw_body)
            stage = body.get("stage")
            if stage not in serializer_by_stage:
                continue
            payload = json.loads(
                json.dumps(body["payload"])
                .replace("{{mobile_number}}", "9000000000")
                .replace("{{customer_photo_url}}", "https://example.com/photo.jpg")
                .replace("{{pan_url}}", "https://example.com/pan.jpg")
                .replace("{{aadhaar_front_url}}", "https://example.com/aadhaar-front.jpg")
                .replace("{{aadhaar_back_url}}", "https://example.com/aadhaar-back.jpg")
                .replace("{{bank_document_url}}", "https://example.com/cheque.jpg")
            )
            partner_lookup = (
                patch(
                    "onboarding_v2.serializers.canonicalize_lending_partner_value",
                    side_effect=lambda value, available_for: value,
                )
                if stage == ApplicationStage.LENDING_PARTNER_BANK
                else nullcontext()
            )
            product_lookup = (
                patch(
                    "onboarding_v2.serializers.ProductV2.objects.filter",
                    return_value=SimpleNamespace(
                        first=lambda: SimpleNamespace(
                            available_for=[LeadType.SELF_LENDING],
                            minimum_ticket_size=0,
                            maximum_ticket_size=500000,
                            tenure_months=12,
                            repayment_frequency="BULLET",
                            category="GENERAL_PURPOSE",
                            interest_rate="11.1100",
                            ltv="80.0000",
                        )
                    ),
                )
                if stage == ApplicationStage.PRODUCT_SELECTION
                else nullcontext()
            )
            with partner_lookup, product_lookup:
                serializer = serializer_by_stage[stage](
                    data=payload,
                    many=stage == ApplicationStage.DOCUMENTS,
                    context={
                        "application": self.application,
                        "is_complete": True,
                        "stage": stage,
                    },
                )
                self.assertTrue(
                    serializer.is_valid(),
                    f"{stage} payload failed validation: {serializer.errors}",
                )
            validated_stages.append(stage)

        self.assertEqual(
            validated_stages,
            [stage for stage, _ in SELF_LENDING_STAGES],
        )
