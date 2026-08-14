from datetime import timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from rest_framework import serializers

from onboarding_v2.constants import ApplicationStatus, LeadType
from onboarding_v2.models import ApplicationV2, LeadV2
from onboarding_v2.serializers import (
    BTAdditionalDetailsSerializer,
    LeadCreateSerializer,
    LoanDetailsSerializer,
)
from onboarding_v2.serializers.loan_punch import LoanPunchSerializer
from users.models import User
from utils.constants import ROLES


class LoanDetailsValidationTests(SimpleTestCase):
    def test_high_amount_requires_bank_appraiser_fields(self):
        payload = {
            "requested_amount": "600000",
            "purpose": "ANY_RANDOM_PURPOSE",
        }
        serializer = LoanDetailsSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("bank_appraiser_id", serializer.errors)
        self.assertIn("bank_appraiser_name", serializer.errors)

    def test_high_amount_allows_bank_appraiser_fields(self):
        payload = {
            "requested_amount": "600000",
            "loan_subcategory": "FRESH",
            "purpose": "ANOTHER_RANDOM_PURPOSE",
            "bank_appraiser_id": "AP-1",
            "bank_appraiser_name": "Appraiser Name",
        }
        serializer = LoanDetailsSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_bt_high_amount_does_not_require_bank_appraiser_fields(self):
        payload = {
            "total_existing_loan_amount": "4,50,000.00",
            "total_article": "12",
            "total_gross_weight": "120.500",
            "total_net_weight": "112.250",
            "purpose_of_loan": "PERSONAL_NEEDS",
            "eligible_bt_amount": "450000.00",
            "required_bt_amount": "600000.00",
            "credit_score_status": "Good",
            "bt_category": "EXTERNAL",
        }
        serializer = LoanDetailsSerializer(
            data=payload,
            context={
                "application": type("Application", (), {"loan_type": LeadType.BALANCE_TRANSFER, "lead": None})(),
                "is_complete": True,
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_non_fresh_loan_type_is_rejected(self):
        payload = {
            "requested_amount": "200000",
            "loan_type": "TOPUP",
            "loan_subcategory": "FRESH",
        }
        serializer = LoanDetailsSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("loan_type", serializer.errors)

    def test_non_fresh_loan_subcategory_is_rejected(self):
        payload = {
            "requested_amount": "200000",
            "loan_subcategory": "TOPUP",
        }
        serializer = LoanDetailsSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("loan_subcategory", serializer.errors)

    def test_empty_loan_subcategory_is_accepted(self):
        serializer = LoanDetailsSerializer(
            data={
                "requested_amount": "200000",
                "loan_subcategory": "",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["loan_subcategory"], "")

    def test_empty_number_of_animal_cattle_is_treated_as_omitted(self):
        serializer = LoanDetailsSerializer(
            data={
                "requested_amount": "200000",
                "number_of_animal_cattle": "",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("number_of_animal_cattle", serializer.validated_data)

    def test_bank_branch_address_and_empty_maturity_date(self):
        payload = {
            "requested_amount": "200000",
            "loan_subcategory": "FRESH",
            "bank_name": "Axis Bank",
            "bank_branch_address": "bade khantura",
            "loan_maturity_date": "",
        }
        serializer = LoanDetailsSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data.get("bank_branch_address"), "bade khantura")
        self.assertEqual(serializer.validated_data.get("bank_name"), "Axis Bank")
        self.assertIsNone(serializer.validated_data.get("loan_maturity_date"))

    def test_monthly_repayment_frequency_is_accepted_and_normalized(self):
        serializer = LoanDetailsSerializer(
            data={"repayment_frequency": "Monthly"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["repayment_frequency"],
            "MONTHLY",
        )

    def test_quarterly_repayment_frequency_is_accepted_and_normalized(self):
        serializer = LoanDetailsSerializer(
            data={"repayment_frequency": "Quarterly"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["repayment_frequency"],
            "QUARTERLY",
        )



class LoanPunchSerializerValidationTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-LP-1",
            contact_number="9000003333",
            customer_name="Loan Punch User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-LP-1",
            lead=self.lead,
        )

    def _loan_payload(self, **overrides):
        payload = {
            "approval_status": "APPROVED",
            "bank_name": "Axis Bank",
            "loan_account_number": "123456789",
            "loan_opening_date": "2026-01-01",
            "sanctioned_amount": "100000.00",
            "approved_tenure": 12,
            "disbursed_amount": "90000.00",
            "rate_of_interest": "10.500",
        }
        payload.update(overrides)
        return payload

    def test_changed_loans_must_have_same_new_bank_name(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(is_bank_changed=True, new_bank_name="HDFC Bank", loan_account_number="ACC1"),
                    self._loan_payload(is_bank_changed=True, new_bank_name="ICICI Bank", loan_account_number="ACC2"),
                ],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("loans", serializer.errors)

    def test_changed_loans_allow_same_new_bank_name_case_insensitive(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(is_bank_changed=True, new_bank_name="HDFC Bank", loan_account_number="ACC1"),
                    self._loan_payload(is_bank_changed=True, new_bank_name=" hdfc bank ", loan_account_number="ACC2"),
                ],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_changed_bank_crm_id_validates_against_new_bank_name(self):
        self.lead.BankLeadID = "CRM-LP-1"
        self.lead.bank = "HDFC Bank"
        self.lead.save()

        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(
                        bank_name="Axis Bank",
                        crm_id="CRM-LP-1",
                        is_bank_changed=True,
                        new_bank_name=" hdfc bank ",
                    ),
                ],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_changed_bank_crm_id_rejects_mismatched_new_bank_name(self):
        self.lead.BankLeadID = "CRM-LP-2"
        self.lead.bank = "HDFC Bank"
        self.lead.save()

        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(
                        bank_name="Axis Bank",
                        crm_id="CRM-LP-2",
                        is_bank_changed=True,
                        new_bank_name="ICICI Bank",
                    ),
                ],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_bank_name", serializer.errors["loans"][0])

    def test_loan_account_number_must_be_unique_across_applications(self):
        # Create an existing loan punch with the target loan account number
        from onboarding_v2.models import LoanPunchV2
        LoanPunchV2.objects.create(
            application=self.app,
            approval_status="APPROVED",
            bank_name="Axis Bank",
            loan_account_number="ACC99999",
        )

        # Create another lead/application
        other_lead = LeadV2.objects.create(
            customer_id="CUST-LP-2",
            contact_number="9000004444",
            customer_name="Other User",
            product_category="LOAN",
        )
        other_app = ApplicationV2.objects.create(
            application_id="APP-LP-2",
            lead=other_lead,
        )

        # Attempting to validate a new loan punch using the same loan account number for the new application should fail
        serializer = LoanPunchSerializer(
            data={
                "application_id": other_app.application_id,
                "loans": [
                    self._loan_payload(
                        bank_name="Axis Bank",
                        loan_account_number="ACC99999",
                    ),
                ],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("loan_account_number", serializer.errors)
        self.assertEqual(
            serializer.errors["loan_account_number"][0],
            "The entered Loan Account Number is already in use. Please enter a different Loan Account Number."
        )

    def test_loan_account_number_can_be_re_submitted_for_same_application(self):
        # Create an existing loan punch with the target loan account number
        from onboarding_v2.models import LoanPunchV2
        LoanPunchV2.objects.create(
            application=self.app,
            approval_status="APPROVED",
            bank_name="Axis Bank",
            loan_account_number="ACC88888",
        )

        # Re-submitting/validating the same loan account number for the same application should be valid
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(
                        bank_name="Axis Bank",
                        loan_account_number="ACC88888",
                    ),
                ],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duplicate_loan_account_numbers_in_same_request_are_rejected(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(bank_name="Axis Bank", loan_account_number="ACC77777"),
                    self._loan_payload(bank_name="Axis Bank", loan_account_number="ACC77777"),
                ],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("loan_account_number", serializer.errors)
        self.assertEqual(
            serializer.errors["loan_account_number"][0],
            "The entered Loan Account Number is already in use. Please enter a different Loan Account Number."
        )

    def test_bajaj_final_submission_requires_both_reconciliation_documents(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [self._loan_payload(bank_name="Bajaj Finserv")],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("loan_account_document", serializer.errors)
        self.assertIn("product_approval_screenshot", serializer.errors)

        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [self._loan_payload(
                    bank_name="Bajaj Finserv",
                    loan_account_document="https://example.com/lan.jpg",
                )],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("product_approval_screenshot", serializer.errors)

    def test_bajaj_multiple_loans_return_one_consolidated_document_error(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [
                    self._loan_payload(bank_name="Bajaj Finserv", loan_account_number="BAJAJ-1"),
                    self._loan_payload(
                        bank_name="Bajaj Finserv",
                        loan_account_number="BAJAJ-2",
                        loan_account_document="https://example.com/lan-2.jpg",
                        product_approval_screenshot="https://example.com/approval-2.jpg",
                    ),
                ],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertNotIn("loans", serializer.errors)
        self.assertIn("loan_account_document", serializer.errors)
        self.assertIn("product_approval_screenshot", serializer.errors)

    def test_bajaj_final_submission_accepts_both_reconciliation_documents(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [self._loan_payload(
                    bank_name="Bajaj Finserv",
                    loan_account_document="https://example.com/lan.jpg",
                    product_approval_screenshot="https://example.com/approval.jpg",
                )],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_bajaj_save_and_exit_allows_missing_documents(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "is_submit": False,
                "loans": [self._loan_payload(bank_name="Bajaj Finserv")],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_other_bank_documents_remain_optional(self):
        serializer = LoanPunchSerializer(
            data={
                "application_id": self.app.application_id,
                "loans": [self._loan_payload(bank_name="Axis Bank")],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


class BTAdditionalDetailsValidationTests(SimpleTestCase):
    def test_income_values_are_stored_in_mobile_format(self):
        payload = {
            "rental_income": "50-70k",
            "annual_income_family_range": "10-15L",
            "house_ownership": "Self Owned",
            "due_diligence_checklist": ["Furniture Seen"],
            "reference_1": {
                "relationship": "FATHER",
                "full_name": "Ramesh Kumar",
                "mobile_number": "9876543210",
            },
            "reference_2": {
                "relationship": "FRIEND",
                "full_name": "Suresh Nair",
                "mobile_number": "9123456789",
            },
        }
        serializer = BTAdditionalDetailsSerializer(data=payload, context={"is_complete": True})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["rental_income"], "50-70k")
        self.assertEqual(serializer.validated_data["annual_income_family_range"], "10-15L")
        self.assertEqual(serializer.validated_data["house_ownership"], "SELF_OWNED")


class BTLeadCreatorEligibilityTests(SimpleTestCase):
    def _user(self, role, days_since_joining=None, exclude_from_bt_date_logic=False):
        date_of_joining = None
        if days_since_joining is not None:
            date_of_joining = timezone.localdate() - timedelta(days=days_since_joining)
        return User(
            role=role,
            date_of_joining=date_of_joining,
            exclude_from_bt_date_logic=exclude_from_bt_date_logic,
        )

    def test_bt_lead_requires_sales_officer_creator(self):
        serializer = LeadCreateSerializer()
        user = self._user(ROLES.AGENT.value, days_since_joining=90)

        with self.assertRaises(serializers.ValidationError):
            serializer._validate_bt_creator_eligibility({"created_by": user})

    def test_bt_lead_requires_sales_officer_to_complete_60_days(self):
        serializer = LeadCreateSerializer()
        user = self._user(ROLES.SALES_OFFICER.value, days_since_joining=59)

        with self.assertRaises(serializers.ValidationError):
            serializer._validate_bt_creator_eligibility({"created_by": user})

    def test_bt_lead_allows_sales_officer_after_60_days(self):
        serializer = LeadCreateSerializer()
        user = self._user(ROLES.SALES_OFFICER.value, days_since_joining=60)

        self.assertIsNone(serializer._validate_bt_creator_eligibility({"created_by": user}))

    def test_bt_lead_allows_excluded_sales_officer_before_60_days(self):
        serializer = LeadCreateSerializer()
        user = self._user(
            ROLES.SALES_OFFICER.value,
            days_since_joining=0,
            exclude_from_bt_date_logic=True,
        )

        self.assertIsNone(serializer._validate_bt_creator_eligibility({"created_by": user}))

    def test_bt_lead_exclusion_does_not_allow_non_sales_officer(self):
        serializer = LeadCreateSerializer()
        user = self._user(
            ROLES.AGENT.value,
            days_since_joining=0,
            exclude_from_bt_date_logic=True,
        )

        with self.assertRaises(serializers.ValidationError):
            serializer._validate_bt_creator_eligibility({"created_by": user})


class CoLendingLeadConflictTests(TestCase):
    contact_number = "9000004444"

    def setUp(self):
        lead = LeadV2.objects.create(
            lead_code="LEAD-CO-LENDING-IN-PROGRESS",
            contact_number=self.contact_number,
            customer_name="Existing Co-Lending Customer",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_type=LeadType.CO_LENDING,
        )
        ApplicationV2.objects.create(
            application_id="APP-CO-LENDING-IN-PROGRESS",
            lead=lead,
            loan_type=LeadType.CO_LENDING,
            status=ApplicationStatus.IN_PROGRESS,
        )

    def _attrs(self, lead_type):
        attrs = {
            "contact_number": self.contact_number,
            "customer_name": "Existing Co-Lending Customer",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": lead_type,
        }
        if lead_type == LeadType.BALANCE_TRANSFER:
            attrs["created_by"] = User(
                role=ROLES.SALES_OFFICER.value,
                date_of_joining=timezone.localdate() - timedelta(days=60),
            )
        return attrs

    def test_fresh_lead_is_rejected_when_co_lending_is_in_progress(self):
        serializer = LeadCreateSerializer()

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(self._attrs(LeadType.FRESH))

        self.assertIn("contact_number", context.exception.detail)

    def test_bt_lead_is_rejected_when_co_lending_is_in_progress(self):
        serializer = LeadCreateSerializer()

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(self._attrs(LeadType.BALANCE_TRANSFER))

        self.assertIn("contact_number", context.exception.detail)
