import shutil
import tempfile
from unittest.mock import patch

from django.utils import timezone


def _add_months(value, months):
    if not value or not months:
        return value
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    import calendar

    last_day = calendar.monthrange(year, month)[1]
    day = min(value.day, last_day)
    return value.replace(year=year, month=month, day=day)
from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import (
    ApplicationDocument,
    ApplicationStageSnapshot,
    ApplicationV2,
    LeadV2,
    Packet,
    JewelleryItem,
)
from onboarding_v2.saas import build_create_loan_payload
from users.models import User


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    SAAS_PRODUCT_ID="MANIPA__GOLD",
)
class SaasFullPayloadTests(TestCase):
    """
    Ensure build_create_loan_payload populates fields from DB/client inputs as expected.
    """

    def setUp(self):
        # Use local storage for file fields
        self._tmp_media = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self._tmp_media, ignore_errors=True))
        settings_cm = self.settings(
            MEDIA_ROOT=self._tmp_media,
            DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
        )
        settings_cm.enable()
        self.addCleanup(settings_cm.disable)

        self.user = User.objects.create_user(
            username="so_user",
            phone="+911234567890",
            role="ADMIN",
            first_name="SO",
            last_name="Name",
            employee_id="EMPL123",
        )
        self.lead = LeadV2.objects.create(
            customer_id="CUST-999",
            contact_number="9000000000",
            customer_name="Test User",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_code="GL0001",
            created_by=self.user,
            pincode="560001",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-999",
            lead=self.lead,
            consent_ip="127.0.0.1",
            consent_timestamp=timezone.now(),
            bureau_name="CIBIL",
            bureau_report_link="https://example.com/report",
            bureau_reference_number="REF-123",
            bureau_pull_date="2025-01-01",
            ltr=75.5,
            processing_fee="10",
            stamp_duty="20",
            insurance_charges="30",
            documentation_charges="40",
            other_charges="50",
            total_charges="60",
            partner_branch_code="MB001",
            partner_branch_name="Manipal Branch",
            partner_product_code="MANIPA__GOLD",
            spread_id="SPR-001",
            compliance="MANIPAL",
            source_id="SRC-99",
            multi_appraisal=True,
        )

        # Stage snapshots
        ApplicationStageSnapshot.objects.bulk_create(
            [
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.PAN,
                    payload={"pan_number": "ABCDE1234F", "name_on_pan": "Test User", "dob_as_per_pan": "1990-01-01"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BASIC,
                    payload={
                        "full_name_as_pan": "Test User",
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
                        "full_name": "Mr. Test User",
                        "dob": "1990-01-01",
                        "gender": "MALE",
                        "category": "GENERAL",
                        "profession": "SALARIED",
                        "occupation": "ENGINEERS",
                        "primary_borrower_type": "SALARY",
                        "income_source": "SALARY",
                        "mobile_number": "9000000000",
                        "father_full_name": "Mr. Father Name",
                        "mother_full_name": "Ms. Mother Name",
                        "nationality": "Indian",
                        "nri_status": "N",
                        "marital_status": "UNMARRIED",
                        "religion": "HINDU",
                        "email": "testuser@gmail.com",
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
                        "requested_amount": "600000",
                        "eligible_amount": "600000",
                        "tenure_years": 6,
                        "interest_rate": "10.0",
                        "repayment_frequency": "BULLET",
                        "interest_type": "FIXED",
                        "type_of_emi": "FIXED",
                        "disbursement_type": "SINGLE",
                        "category": "SECURED",
                        "loan_subcategory": "FRESH",
                        "purpose": "BUSINESS_NEEDS",
                        "bank_appraiser_id": "BANK-1",
                        "bank_appraiser_name": "Bank Appraiser",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=self.app,
                    stage=ApplicationStage.BANK,
                    payload={
                        "bank_name": "Axis Bank",
                        "account_number": "1234567890",
                        "customer_name_as_per_bank": "Test User",
                        "ifsc_code": "UTIB0000123",
                        "branch_name": "Main",
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

        # Documents & metadata
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
            metadata={"aadhar_number": "123412341234"},
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
            metadata={"document_number": "VOTER123", "name": "Test User"},
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.DRIVING_LICENSE,
            file_url="https://cdn.example.com/DRIVING_LICENCE_NUMBER.jpg",
            metadata={"dl_number": "DL123", "name": "Test User", "expiry_date": "2030-01-01", "issue_date": "2020-01-01"},
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PASSPORT,
            file_url="https://cdn.example.com/PASSPORT.jpg",
            metadata={
                "passport_number": "J8369815",
                "passport_expiry_date": "2030-01-01",
                "passport_file_number": "K07767687",
                "passport_issue_date": "2015-03-01",
                "passport_place_of_issue": "chennai",
            },
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.OTHER,
            subtype="bureau_report",
            file_url="https://cdn.example.com/bureau.pdf",
        )

        # Jewellery
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
            number_of_articles=1,
            gross_weight="10",
            net_adjusted_weight="9",
            metadata={
                "front_image_url": "https://cdn.example.com/bangle_front.jpg",
                "back_image_url": "https://cdn.example.com/bangle_back.jpg",
            },
        )

    def _presign_passthrough(self, file_url=None, object_name=None):
        return {"get_url": file_url}

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_full_payload_population(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough

        payload = build_create_loan_payload(self.app)

        # Basic identifiers
        expected = {
            "leadId": "GL0001",
            "productId": "MANIPA__GOLD",
            "clientLoanId": self.app.application_id,
            "applicationId": self.app.application_id,
            "clientApplicationId": self.app.application_id,
            "clientCustomerId": self.lead.customer_id,
            "agreementId": "2605",
            "noOfAssets": 1,
            "spreadId": "SPR-001",
            "politicallyExposed": "N",
            "panNumber": "ABCDE1234F",
            "firstName": "Test",
            "middleName": "",
            "lastName": "User",
            "nameAsPerPan": "Test User",
            "dateOfBirth": "1990-01-01",
            "dateOfBirthAsPerPan": "1990-01-01",
            "aadharNumber": "123412341234",
            "mobileNumber": "9000000000",
            "poaType": "AADHAAR",
            "primaryBorrowerType": "INDIVIDUAL",
            "customerCategory": "salaried",
            "partnerBranchCode": "MB001",
            "partnerBranchName": "Manipal Branch",
            "partnerProductCode": "MANIPAL",
            "partnerSchemeCode": "MTPGL",
            "mailingAddress": "PERMANENT",
            "incomeSource": "Salary",
            "title": "Mr",
            "email": "testuser@gmail.com",
            "placeOfBirth": "",
            "gender": "m",
            "permanentPincode": "560001",
            "permanentState": "ka",
            "permanentCity": "BLR",
            "permanentAddress": "Line 1",
            "currentPincode": "560001",
            "currentState": "ka",
            "currentCity": "BLR",
            "currentAddress": "Line 1",
            "addressType": "current",
            "maritalStatus": "Unmarried",
            "religion": "Hindu",
            "category": "SECURED",
            "occupation": "Engineers",
            "nationality": "Indian",
            "nriStatus": "N",
            "caste": "General",
            "fatherNameTitle": "Mr",
            "fatherName": "Father Name",
            "motherTitle": "Ms",
            "motherName": "Mother Name",
            "loanCycle": 1,
            "nameOfBureau": "experian",
            "bureauScore": "",
            "cibilScore": -1,
            "bureauReportLink": "https://example.com/report",
            "bureauPullDate": "2025-01-01",
            "referenceNumber": "REF-123",
            "principalAmount": 600000,
            "tenure": 6,
            "typeOfEmi": "FIXED",
            "interestRate": 10.0,
            "interestStartDate": str(timezone.localdate()),
            "interestType": "FIXED",
            "repaymentFrequency": "bullet",
            "disbursementType": "SINGLE",
            "subCategory": "fresh",
            "purpose": "Business Needs",
            "loanMaturityDate": str(_add_months(timezone.localdate(), 6)),
            "firstRepaymentDate": str(_add_months(timezone.localdate(), 6)),
            "lastDisbDate": "",
            "numberOfRepayments": 1,
            "ltr": 75,
            "processingFee": 10,
            "stampDuty": 20,
            "insuranceCharges": 30,
            "documentationCharges": 40,
            "otherCharges": 50,
            "totalCharges": 60,
            "annualIncome": 0,
            "netMonthlyIncome": 0,
            "foir": 0,
            "tenureFrequency": "bullet",
            "consentipaddress": "127.0.0.1",
            "compliance": "MANIPAL",
            "sourceId": "SRC-99",
            "geoLocation": "south",
            "complianceSecurityFlag": "Y",
            "complianceDelinquency": "Y",
            "fatcaVerificationOfficialId": "EMPL123",
            "fatcaVerificationOfficialBranch": "Gurgaon",
            "fatcaVerificationOfficialDesignation": "SO",
            "fatcaVerificationOfficialName": "SO Name",
        }
        for k, v in expected.items():
            self.assertEqual(payload[k], v, f"Mismatch for key {k}")

        # KYC identity (DL/Voter) and passport
        self.assertEqual(payload["drivingLicenseNumber"], "DL123")
        self.assertEqual(payload["voterIdNumber"], "VOTER123")
        self.assertEqual(payload["passPortNumber"], "J8369815")
        self.assertEqual(payload["passPortExpiryDate"], "2030-01-01")
        self.assertEqual(payload["passPortFileNumber"], "K07767687")
        self.assertEqual(payload["passportissuedate"], "2015-03-01")
        self.assertEqual(payload["passportplaceofissue"], "chennai")

        # Consent/fatca
        self.assertEqual(payload["consentipaddress"], "127.0.0.1")
        self.assertEqual(payload["fatcaVerificationOfficialId"], "EMPL123")
        self.assertEqual(payload["fatcaVerificationOfficialBranch"], "Gurgaon")
        self.assertEqual(payload["fatcaVerificationOfficialDesignation"], "SO")
        self.assertEqual(payload["fatcaVerificationOfficialName"], "SO Name")

        # Numeric conversions
        self.assertIsInstance(payload["principalAmount"], (int, float))
        self.assertIsInstance(payload["interestRate"], (int, float))
        self.assertEqual(payload["foir"], 0)

        # Doc URL mapping
        self.assertIn("pannumberUrl", payload)
        self.assertIn("aadharNumberLink", payload)
        self.assertIn("votingIdLink", payload)
        self.assertIn("drivingLicenceNumberUrl", payload)
        self.assertIn("passportNumberUrl", payload)
        self.assertEqual(payload.get("bureauReportUrl"), "https://cdn.example.com/bureau.pdf")

        # Gold/jewellery URLs and details
        self.assertIn("jewelleryUrl", payload)
        self.assertTrue(payload["jewelleryDetails"])
        gold = payload.get("goldDetails", {})
        self.assertEqual(gold.get("packetId"), "PKT-1")
        self.assertEqual(gold.get("appraiserId"), "APP-1")
        self.assertEqual(gold.get("appraiserName"), "John Jacob")
        self.assertEqual(gold.get("grossWeightOfJewellery"), 140)
        self.assertEqual(gold.get("grossValueOfJewellery"), 100000)
        jd = payload["jewelleryDetails"][0]
        self.assertEqual(jd["typeOfJewelleryOrnament"], "Bangles")
        self.assertEqual(jd["unitsNumberOfOrnamentType"], 1)
        self.assertEqual(jd["grossWeightOfJewellery"], 10)
        self.assertEqual(jd["netAdjustedWeightOfJewellery"], 9)
        self.assertEqual(len(jd["appraiserEvaluations"]), 2)
        evals = jd["appraiserEvaluations"][0]
        self.assertEqual(evals["appraiserId"], "APP-1")
        self.assertEqual(evals["appraiserName"], "John Jacob")
        self.assertEqual(evals["jewelleryCount"], 1)
        self.assertEqual(evals["grossWeightOfJewellery"], 10)
        self.assertEqual(evals["actualPurityGrade"], 22)
        bank_evals = jd["appraiserEvaluations"][1]
        self.assertEqual(bank_evals["appraiserId"], "BANK-1")
        self.assertEqual(bank_evals["appraiserName"], "Bank Appraiser")

        # Disbursement account
        self.assertEqual(payload["disbursementAccounts"][0]["bankName"], "Axis Bank")
        self.assertEqual(payload["disbursementAccounts"][0]["accountName"], "Test User")
        self.assertEqual(payload["disbursementAccounts"][0]["ifscCode"], "UTIB0000123")
        self.assertEqual(payload["disbursementAccounts"][0]["accountNo"], "1234567890")

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_explicit_address_poa_type_maps_to_saas_payload(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough
        snapshot = ApplicationStageSnapshot.objects.get(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
        )
        snapshot.payload = {
            **snapshot.payload,
            "poa_type": "Gazetted office letter",
        }
        snapshot.save(update_fields=["payload"])

        payload = build_create_loan_payload(self.app)

        self.assertEqual(payload["poaType"], "Gazetted office letter")

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_multi_appraisal_calculated_from_requested_amount(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough

        lead = LeadV2.objects.create(
            customer_id="CUST-1000",
            contact_number="9000001000",
            customer_name="Calc User",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_code="GL1000",
            created_by=self.user,
            pincode="560001",
        )
        app = ApplicationV2.objects.create(
            application_id="APP-1000",
            lead=lead,
            consent_ip="127.0.0.1",
            consent_timestamp=timezone.now(),
            partner_branch_code="MB001",
            partner_branch_name="Manipal Branch",
            partner_product_code="MANIPA__GOLD",
            multi_appraisal=False,
        )

        ApplicationStageSnapshot.objects.bulk_create(
            [
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.PAN,
                    payload={"pan_number": "ABCDE1234F", "name_on_pan": "Calc User", "dob_as_per_pan": "1990-01-01"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.BASIC,
                    payload={
                        "full_name_as_pan": "Calc User",
                        "dob": "1990-01-01",
                        "dob_as_per_pan": "1990-01-01",
                        "phone_number": "9000001000",
                        "gender": "MALE",
                        "aadhar_number": "123412341234",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.PERSONAL,
                    payload={"full_name": "Calc User", "dob": "1990-01-01", "gender": "MALE"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.ADDRESS,
                    payload={
                        "permanent": {"address_line1": "Line 1", "pincode": "560001", "state": "KA", "city": "BLR"},
                        "current_same_as_permanent": True,
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.LOAN,
                    payload={
                        "requested_amount": "600000",
                        "eligible_amount": "600000",
                        "tenure_years": 6,
                        "interest_rate": "10.0",
                        "repayment_frequency": "BULLET",
                        "interest_type": "FIXED",
                        "type_of_emi": "FIXED",
                        "disbursement_type": "SINGLE",
                        "category": "SECURED",
                        "loan_subcategory": "FRESH",
                        "purpose": "BUSINESS_NEEDS",
                        "bank_appraiser_id": "BANK-1",
                        "bank_appraiser_name": "Bank Appraiser",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.BANK,
                    payload={
                        "bank_name": "Axis Bank",
                        "account_number": "1234567890",
                        "customer_name_as_per_bank": "Calc User",
                        "ifsc_code": "UTIB0000123",
                        "branch_name": "Main",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.GOLD,
                    payload={"items": [], "packet": {}},
                    is_complete=True,
                ),
            ]
        )

        packet = Packet.objects.create(
            application=app,
            packet_id="PKT-1000",
            barcode_id="BAR-1000",
            gross_weight="10.0",
            gross_value="10000",
            net_adjusted_weight="9",
            net_adjusted_value="9000",
            appraiser_id="APP-1",
            appraiser_name="John Jacob",
        )
        JewelleryItem.objects.create(
            packet=packet,
            type_of_jewellery="BANGLE",
            number_of_articles=1,
            gross_weight="10",
            net_adjusted_weight="9",
        )

        payload = build_create_loan_payload(app)

        self.assertTrue(payload.get("goldDetails", {}).get("multiAppraisal"))
        jd = payload["jewelleryDetails"][0]
        self.assertEqual(len(jd["appraiserEvaluations"]), 2)

    @patch("onboarding_v2.saas.generate_presigned_get")
    def test_multi_appraisal_disabled_below_threshold(self, mock_presign):
        mock_presign.side_effect = self._presign_passthrough

        lead = LeadV2.objects.create(
            customer_id="CUST-1001",
            contact_number="9000001001",
            customer_name="Below Threshold User",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_code="GL1001",
            created_by=self.user,
            pincode="560001",
        )
        app = ApplicationV2.objects.create(
            application_id="APP-1001",
            lead=lead,
            consent_ip="127.0.0.1",
            consent_timestamp=timezone.now(),
            partner_branch_code="MB001",
            partner_branch_name="Manipal Branch",
            partner_product_code="MANIPA__GOLD",
            multi_appraisal=False,
        )

        ApplicationStageSnapshot.objects.bulk_create(
            [
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.PAN,
                    payload={"pan_number": "ABCDE1234F", "name_on_pan": "Below User", "dob_as_per_pan": "1990-01-01"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.BASIC,
                    payload={
                        "full_name_as_pan": "Below User",
                        "dob": "1990-01-01",
                        "dob_as_per_pan": "1990-01-01",
                        "phone_number": "9000001001",
                        "gender": "MALE",
                        "aadhar_number": "123412341234",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.PERSONAL,
                    payload={"full_name": "Below User", "dob": "1990-01-01", "gender": "MALE"},
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.ADDRESS,
                    payload={
                        "permanent": {"address_line1": "Line 1", "pincode": "560001", "state": "KA", "city": "BLR"},
                        "current_same_as_permanent": True,
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.LOAN,
                    payload={
                        "requested_amount": "400000",
                        "eligible_amount": "400000",
                        "tenure_years": 6,
                        "interest_rate": "10.0",
                        "repayment_frequency": "BULLET",
                        "interest_type": "FIXED",
                        "type_of_emi": "FIXED",
                        "disbursement_type": "SINGLE",
                        "category": "SECURED",
                        "loan_subcategory": "FRESH",
                        "purpose": "BUSINESS_NEEDS",
                        "bank_appraiser_id": "BANK-1",
                        "bank_appraiser_name": "Bank Appraiser",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.BANK,
                    payload={
                        "bank_name": "Axis Bank",
                        "account_number": "1234567890",
                        "customer_name_as_per_bank": "Below User",
                        "ifsc_code": "UTIB0000123",
                        "branch_name": "Main",
                    },
                    is_complete=True,
                ),
                ApplicationStageSnapshot(
                    application=app,
                    stage=ApplicationStage.GOLD,
                    payload={"items": [], "packet": {}},
                    is_complete=True,
                ),
            ]
        )

        packet = Packet.objects.create(
            application=app,
            packet_id="PKT-1001",
            barcode_id="BAR-1001",
            gross_weight="10.0",
            gross_value="10000",
            net_adjusted_weight="9",
            net_adjusted_value="9000",
            appraiser_id="APP-1",
            appraiser_name="John Jacob",
        )
        JewelleryItem.objects.create(
            packet=packet,
            type_of_jewellery="BANGLE",
            number_of_articles=1,
            gross_weight="10",
            net_adjusted_weight="9",
        )

        payload = build_create_loan_payload(app)

        self.assertFalse(payload.get("goldDetails", {}).get("multiAppraisal"))
        jd = payload["jewelleryDetails"][0]
        self.assertEqual(len(jd["appraiserEvaluations"]), 1)

    def test_fatca_uses_user_fields(self):
        self.user.first_name = "Asha"
        self.user.last_name = "Khan"
        self.user.employee_id = "EMP-999"
        self.user.save(update_fields=["first_name", "last_name", "employee_id"])

        payload = build_create_loan_payload(self.app)
        self.assertEqual(payload["fatcaVerificationOfficialId"], "EMP-999")
        self.assertEqual(payload["fatcaVerificationOfficialName"], "Asha Khan")
