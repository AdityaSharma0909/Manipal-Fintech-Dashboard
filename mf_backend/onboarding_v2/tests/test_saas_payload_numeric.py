from unittest.mock import patch

from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import (
    ApplicationStageSnapshot,
    ApplicationV2,
    LeadV2,
    Packet,
    JewelleryItem,
    RoiConfiguration,
)
from onboarding_v2.saas import build_create_loan_payload


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    SAAS_PRODUCT_ID="MANIPA__GOLD",
)
class SaasNumericPayloadTests(TestCase):
    """
    Validate that numeric fields in the create-loan payload are emitted as numbers,
    and that jewellery details carry numeric values.
    """

    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-NUM-1",
            contact_number="9000000000",
            customer_name="Num User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-NUM-1", lead=self.lead)

        ApplicationStageSnapshot.objects.bulk_create(
            [
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BASIC,
                    payload={
                        "full_name_as_pan": "Num User",
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
                        "full_name": "Num User",
                        "dob": "1990-01-01",
                        "gender": "MALE",
                        "category": "GENERAL",
                        "occupation": "ENGINEERS",
                        "annual_income": "200000",
                        "net_monthly_income": "15000",
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
                    payload={
                        "requested_amount": "499999",
                        "tenure_years": 6,
                        "interest_rate": "16.0",
                        "foir": "0.5",
                        "number_of_repayments": 1,
                        "repayment_frequency": "BULLET",
                        "tenure_frequency": "BULLET",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BANK,
                    payload={
                        "bank_name": "Axis Bank",
                        "account_number": "1234567890",
                        "customer_name_as_per_bank": "Num User",
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

        packet = Packet.objects.create(
            application=self.app,
            packet_id="PKT-1",
            barcode_id="BAR-1",
            gross_weight="140.0",
            gross_value="100000",
            net_adjusted_weight="110",
            net_adjusted_value="100000",
            appraiser_id="APP-1",
            appraiser_name="John Jacob",
        )
        JewelleryItem.objects.create(
            packet=packet,
            type_of_jewellery="BANGLE",
            number_of_articles=3,
            gross_weight="60",
            stone_weight="35",
            net_weight="20.2",
            impurity_deducted="15",
            net_adjusted_weight="22.5",
            percent_of_gold="50",
            actual_gold_rate="6500.7",
            gross_value="20000",
            net_value="30000",
            net_adjusted_value="35000",
        )

    def _presign_passthrough(self, file_url=None, object_name=None):
        # Don’t alter URL; prevents MinIO calls during tests.
        return {"get_url": file_url}

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_numeric_fields_and_jewellery_details_are_numbers(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough

        payload = build_create_loan_payload(self.app)

        self.assertIsInstance(payload["principalAmount"], (int, float))
        self.assertEqual(payload["principalAmount"], 499999)
        self.assertEqual(payload["numberOfRepayments"], 1)
        self.assertEqual(payload["tenure"], 6)
        self.assertEqual(payload["repaymentFrequency"], "bullet")
        self.assertEqual(payload["tenureFrequency"], "bullet")
        self.assertEqual(payload["foir"], 0.5)
        self.assertEqual(payload["interestRate"], 16.0)

        jd = payload["jewelleryDetails"][0]
        self.assertEqual(jd["unitsNumberOfOrnamentType"], 3)
        self.assertEqual(jd["grossWeightOfJewellery"], 60)
        self.assertEqual(jd["netAdjustedWeightOfJewellery"], 22.5)
        self.assertEqual(jd["grossValueOfJewellery"], 20000)
        self.assertEqual(jd["netAdjustedValueOfJewellery"], 35000)
        self.assertEqual(jd["netValueOfMetal"], 30000)
        self.assertEqual(jd["actualGoldRateConsidered"], 6500.7)
        self.assertEqual(jd["actualPurityGrade"], 22)
        self.assertEqual(jd["adjustedPurityGrade"], 22)

        evals = jd["appraiserEvaluations"][0]
        self.assertEqual(evals["jewelleryCount"], 3)
        self.assertEqual(evals["grossWeightOfJewellery"], 60)
        self.assertEqual(evals["grossValueOfJewellery"], 20000)
        self.assertEqual(evals["netAdjustedValueOfJewellery"], 35000)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_adjusted_purity_grade_mapping(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough
        # Test mapping: Actual Fineness -> Adjusted Fineness
        # 18K -> 18K
        # 19K -> 18K
        # 20K -> 22K
        # 21K -> 22K
        # 22K -> 22K
        # 23K -> 24K
        # 24K -> 24K
        mapping = {
            "18K": (18, 18),
            "19K": (19, 18),
            "20K": (20, 22),
            "21K": (21, 22),
            "22K": (22, 22),
            "23K": (23, 24),
            "24K": (24, 24),
        }
        for actual_purity_str, (expected_actual, expected_adjusted) in mapping.items():
            JewelleryItem.objects.filter(packet__application=self.app).update(purity=actual_purity_str)
            payload = build_create_loan_payload(self.app)
            jd = payload["jewelleryDetails"][0]
            self.assertEqual(jd["actualPurityGrade"], expected_actual)
            self.assertEqual(jd["adjustedPurityGrade"], expected_adjusted)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_tenure_months_in_loan_stage(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough
        # Update the snapshot to have tenure_months instead of tenure_years
        snap = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.LOAN)
        payload_data = dict(snap.payload)
        payload_data.pop("tenure_years", None)
        payload_data["tenure_months"] = 9
        snap.payload = payload_data
        snap.save()

        payload = build_create_loan_payload(self.app)
        self.assertEqual(payload["tenure"], 9)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_originator_roi_for_blended_yield(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough
        # Create staging snapshots for LOAN_RANGE_SELECTION and PRODUCT_SELECTION
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LOAN_RANGE_SELECTION,
            payload={
                "above_range": True,
                "loan_amount": "250000.00"
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PRODUCT_SELECTION,
            payload={
                "product_type": "GENERAL_PURPOSE"
            },
            is_complete=True,
        )

        # Create RoiConfiguration
        RoiConfiguration.objects.create(
            bank="AXIS_BANK",
            lead_type="CO_LENDING",
            loan_range="MORE_THAN_2_5_LAKHS",
            product_type="GENERAL_PURPOSE",
            tenure="6_MONTHS",
            repayment_schedule="BULLET",
            manipal_roi=23.00,
        )

        # Ensure application has correct lending partner and loan type
        self.app.lending_partner = "AXIS_BANK"
        self.app.loan_type = "CO_LENDING"
        self.app.save()

        # Build create-loan payload
        payload = build_create_loan_payload(self.app)
        self.assertEqual(payload["originatorRoiForBlendedYield"], 23)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_originator_roi_uses_below_range_when_flag_is_false_at_threshold(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LOAN_RANGE_SELECTION,
            payload={
                "above_range": False,
                "loan_amount": "250000.00",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PRODUCT_SELECTION,
            payload={
                "product_type": "GENERAL_PURPOSE",
            },
            is_complete=True,
        )

        RoiConfiguration.objects.create(
            bank="AXIS_BANK",
            lead_type="CO_LENDING",
            loan_range="LESS_THAN_2_5_LAKHS",
            product_type="GENERAL_PURPOSE",
            tenure="6_MONTHS",
            repayment_schedule="BULLET",
            manipal_roi=82.00,
        )

        self.app.lending_partner = "AXIS_BANK"
        self.app.loan_type = "CO_LENDING"
        self.app.save()

        payload = build_create_loan_payload(self.app)
        self.assertEqual(payload["originatorRoiForBlendedYield"], 82)
