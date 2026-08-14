from unittest.mock import patch
import json
from datetime import date, datetime, timedelta, timezone

from django.test import TestCase, Client, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType, ApplicationStatus
from onboarding_v2.models import (
    ApplicationDocument,
    ApplicationStageSnapshot,
    ApplicationV2,
    LeadV2,
    WebhookEvent,
)
from users.models import User
from onboarding_v2.saas import build_create_loan_payload
from onboarding_v2.views.stages import (
    SubmitApplicationView,
    FinalizeApplicationView,
    ApplicationStateView,
)


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    SAAS_WEBHOOK_SECRET="secret-token",
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
    },
    SAAS_DOCUMENT_ID_MAP={"PAN": 101},
)
class APISmokeFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="so_user",
            phone="+911234567890",
            role="ADMIN",
            first_name="SO",
            last_name="Name",
            employee_id="EMPL123",
        )
        self.lead = LeadV2.objects.create(
            customer_id="CUST-789",
            contact_number="7777777777",
            customer_name="Alice Doe",
            product_category="LOAN",
            created_by=self.user,
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-789",
            lead=self.lead,
        )
        self.client.force_login(self.user)

        self.original_submit_auth = SubmitApplicationView.authentication_classes
        self.original_submit_perm = SubmitApplicationView.permission_classes
        SubmitApplicationView.authentication_classes = []
        SubmitApplicationView.permission_classes = []

        self.original_finalize_auth = FinalizeApplicationView.authentication_classes
        self.original_finalize_perm = FinalizeApplicationView.permission_classes
        FinalizeApplicationView.authentication_classes = []
        FinalizeApplicationView.permission_classes = []

        self.original_state_auth = ApplicationStateView.authentication_classes
        self.original_state_perm = ApplicationStateView.permission_classes
        ApplicationStateView.authentication_classes = []
        ApplicationStateView.permission_classes = []

    def tearDown(self):
        SubmitApplicationView.authentication_classes = self.original_submit_auth
        SubmitApplicationView.permission_classes = self.original_submit_perm

        FinalizeApplicationView.authentication_classes = self.original_finalize_auth
        FinalizeApplicationView.permission_classes = self.original_finalize_perm

        ApplicationStateView.authentication_classes = self.original_state_auth
        ApplicationStateView.permission_classes = self.original_state_perm

    def test_stage_update_and_submit(self):
        # Create snapshots directly to bypass endpoint validation complexities
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PAN,
            payload={"pan_number": "AAAAA1111A", "name_on_pan": "Alice Doe", "dob_as_per_pan": "1991-01-01"},
            is_complete=True,
        )
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            metadata={"pan_number": "AAAAA1111A"},
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Alice Doe",
                "dob": "1991-01-01",
                "dob_as_per_pan": "1991-01-01",
                "phone_number": "7777777777",
                "gender": "FEMALE",
                "aadhar_number": "123412341234",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "1 Street",
                    "pincode": "560003",
                    "state": "KA",
                    "city": "BLR",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )

        with patch("onboarding_v2.views.enqueue_pre_screen") as mock_delay:
            submit_resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/submit/",
                {},
            )
            self.assertEqual(submit_resp.status_code, 200)
            mock_delay.assert_called_once()

    def test_webhook_eligible_enqueues_bureau(self):
        self.app.saas_request_id = "REQ-1"
        self.app.save()
        with patch("onboarding_v2.views.run_bureau_check_task.delay") as mock_bureau:
            resp = self.client.post(
                "/api/v2/onboarding/webhooks/saastech/pre-screen/",
                {
                    "applicationId": self.app.application_id,
                    "status": "READY FOR LOAN",
                    "remarks": "Eligible from SAAS",
                    "meta": {"source": "saas_tech_prescreening"},
                },
                HTTP_X_SAAS_TOKEN="secret-token",
            )
            self.assertEqual(resp.status_code, 200)
            mock_bureau.assert_called_once()
            self.app.refresh_from_db()
            self.assertEqual(self.app.status, ApplicationStatus.READY_FOR_LOAN)
            self.assertEqual(self.app.saas_status, "READY FOR LOAN")
            self.assertEqual(self.app.saas_prescreen_remarks, "Eligible from SAAS")
            event = WebhookEvent.objects.get(application_id=self.app.application_id)
            self.assertEqual(event.purpose, WebhookEvent.Purpose.PRESCREEN)

    def test_webhook_loan_creation_updates_without_bureau(self):
        with patch("onboarding_v2.views.run_bureau_check_task.delay") as mock_bureau:
            resp = self.client.post(
                "/api/v2/onboarding/webhooks/saastech/pre-screen/",
                {
                    "applicationId": self.app.application_id,
                    "status": "approved",
                    "remarks": "Loan approved successfully",
                    "meta": {"source": "saas_tech_loan_creation"},
                },
                HTTP_X_SAAS_TOKEN="secret-token",
            )
            self.assertEqual(resp.status_code, 200)
            mock_bureau.assert_not_called()
            self.app.refresh_from_db()
            self.assertEqual(self.app.saas_create_loan_status, "approved")
            self.assertEqual(self.app.saas_loan_remarks, "Loan approved successfully")
            event = WebhookEvent.objects.get(application_id=self.app.application_id)
            self.assertEqual(event.purpose, WebhookEvent.Purpose.LOAN_CREATION)

    def test_application_state_endpoint(self):
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PAN,
            payload={"pan_number": "ABCDE1234F"},
            is_complete=True,
        )
        resp = self.client.get(f"/api/v2/onboarding/applications/{self.app.application_id}/state/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json().get("data", {}).get("application", {})
        self.assertIn("application_id", data)
        self.assertTrue(data.get("snapshots") is not None)

    def test_finalize_enqueues_create_loan_and_docs(self):
        # minimal doc and snapshots for finalize
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            file_url="https://example.com/pan.jpg",
        )
        # required snapshots
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Alice Doe",
                "dob": "1991-01-01",
                "dob_as_per_pan": "1991-01-01",
                "phone_number": "7777777777",
                "gender": "FEMALE",
                "aadhar_number": "123412341234",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PERSONAL,
            payload={"full_name": "Alice Doe", "dob": "1991-01-01", "dob_as_per_pan": "1991-01-01", "gender": "FEMALE"},
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "1 Street",
                    "pincode": "560003",
                    "state": "KA",
                    "city": "BLR",
                    "district": "BLR",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LOAN,
            payload={
                "requested_amount": "600000",
                "eligible_amount": "600000",
                "tenure_years": 6,
                "interest_rate": "10.0",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BANK,
            payload={
                "bank_name": "Axis Bank",
                "account_number": "1234567890",
                "customer_name_as_per_bank": "Alice Doe",
                "ifsc_code": "UTIB0000123",
                "branch_name": "Main",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.GOLD,
            payload={"items": []},
            is_complete=True,
        )
        with patch("onboarding_v2.views.enqueue_create_loan") as mock_create:
            resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/finalize/",
                {},
            )
            self.assertEqual(resp.status_code, 200)
            mock_create.assert_called_once()

    def test_finalize_co_lending_sends_state_payload(self):
        from onboarding_v2.constants import LeadType
        from decimal import Decimal
        self.app.loan_type = LeadType.CO_LENDING
        self.app.save()

        self.lead.amount = Decimal("50000.50")
        self.lead.save()

        # Create basic snapshot so ApplicationStateSerializer has snapshot data
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Alice Doe",
                "phone_number": "7777777777",
            },
            is_complete=True,
        )

        with patch("onboarding_v2.helpers.saas_helpers.create_loan_task.delay") as mock_create:
            resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/finalize/",
                {},
            )
            self.assertEqual(resp.status_code, 200)
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            payload = args[1]
            self.assertEqual(payload["application_id"], self.app.application_id)
            self.assertEqual(payload["status"], "DRAFT")
            self.assertEqual(payload["lead_amount"], 50000.5)
            self.assertEqual(len(payload["snapshots"]), 1)
            self.assertEqual(payload["snapshots"][0]["stage"], "BASIC")
            self.assertIsInstance(payload["snapshots"][0]["created_at"], str)

    def test_build_create_loan_payload_includes_new_fields(self):
        # Populate application-level SAAS fields
        now = datetime.now(timezone.utc)
        self.app.partner_branch_code = "MB001"
        self.app.partner_branch_name = "Manipal Branch"
        self.app.partner_product_code = "MANIPA__GOLD"
        self.app.agreement_id = "MANIPA__GOLD_1"
        self.app.spread_id = "SPR-001"
        self.app.ltr = 75
        self.app.interest_start_date = date.today()
        self.app.loan_maturity_date = date.today() + timedelta(days=365)
        self.app.first_repayment_date = date.today() + timedelta(days=30)
        self.app.processing_fee = 100.50
        self.app.stamp_duty = 50
        self.app.insurance_charges = 25
        self.app.documentation_charges = 10
        self.app.other_charges = 5
        self.app.total_charges = 190.5
        self.app.consent_timestamp = now
        self.app.consent_ip = "127.0.0.1"
        self.app.bureau_name = "CIBIL"
        self.app.bureau_report_link = "https://example.com/report"
        self.app.bureau_pull_date = date.today()
        self.app.bureau_reference_number = "REF-123"
        self.app.reference_number = "CLIENT-REF"
        self.app.compliance = "MANIPAL"
        self.app.source_id = "SRC-99"
        self.app.multi_appraisal = True
        self.app.primary_borrower_type = "INDIVIDUAL"
        self.app.income_source = "SALARY"
        self.app.occupation = "ENGINEERS"
        self.app.nationality = "INDIAN"
        self.app.nri_status = "N"
        self.app.caste = "GENERAL"
        self.app.save()

        # Required stage payloads
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BASIC,
            payload={
                "full_name_as_pan": "Alice Doe",
                "dob": "1991-01-01",
                "dob_as_per_pan": "1991-01-01",
                "phone_number": "7777777777",
                "gender": "FEMALE",
                "aadhar_number": "123412341234",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PERSONAL,
            payload={
                "full_name": "Alice Doe",
                "dob": "1991-01-01",
                "dob_as_per_pan": "1991-01-01",
                "gender": "FEMALE",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "1 Street",
                    "pincode": "560003",
                    "state": "KA",
                    "city": "BLR",
                    "district": "BLR",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.LOAN,
            payload={
                "requested_amount": "600000",
                "eligible_amount": "600000",
                "tenure_years": 6,
                "interest_rate": "10.0",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.BANK,
            payload={
                "bank_name": "Axis Bank",
                "account_number": "1234567890",
                "customer_name_as_per_bank": "Alice Doe",
                "ifsc_code": "UTIB0000123",
                "branch_name": "Main",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.GOLD,
            payload={"items": []},
            is_complete=True,
        )

        payload = build_create_loan_payload(self.app)
        self.assertEqual(payload["partnerBranchCode"], "MB001")
        self.assertEqual(payload["partnerBranchName"], "Manipal Branch")
        self.assertEqual(payload["partnerProductCode"], "MANIPAL")
        self.assertEqual(payload["agreementId"], "2605")
        self.assertEqual(payload["spreadId"], "SPR-001")
        self.assertEqual(payload["ltr"], 75)
        self.assertEqual(payload["interestStartDate"], str(self.app.interest_start_date))
        self.assertEqual(payload["loanMaturityDate"], str(self.app.loan_maturity_date))
        self.assertEqual(payload["firstRepaymentDate"], str(self.app.first_repayment_date))
        self.assertEqual(payload["processingFee"], self.app.processing_fee)
        self.assertEqual(payload["stampDuty"], self.app.stamp_duty)
        self.assertEqual(payload["insuranceCharges"], self.app.insurance_charges)
        self.assertEqual(payload["documentationCharges"], self.app.documentation_charges)
        self.assertEqual(payload["otherCharges"], self.app.other_charges)
        self.assertEqual(payload["totalCharges"], self.app.total_charges)
        self.assertEqual(payload["consentipaddress"], "127.0.0.1")
        self.assertEqual(payload["compliance"], "MANIPAL")
        self.assertEqual(payload["sourceId"], "SRC-99")
        self.assertTrue(payload["goldDetails"]["multiAppraisal"])
        self.assertEqual(payload["nameOfBureau"], "experian")
        self.assertEqual(payload["bureauReportLink"], "https://example.com/report")
        self.assertEqual(payload["referenceNumber"], "REF-123")
        self.assertEqual(payload["bureauPullDate"], str(self.app.bureau_pull_date))
        expected_ts = self.app.consent_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        self.assertEqual(payload["consentTimestamp"], expected_ts)
        self.assertEqual(payload["fatcaVerificationOfficialId"], "EMPL123")
        self.assertEqual(payload["fatcaVerificationOfficialBranch"], "Gurgaon")
        self.assertEqual(payload["fatcaVerificationOfficialDesignation"], "SO")
        self.assertEqual(payload["fatcaVerificationOfficialName"], "SO Name")
        self.assertEqual(payload["fatcaPlace"], "BLR")
        self.assertEqual(payload["geoLocation"], "south")
        self.assertEqual(payload["fatcaVerificationDate"], str(self.app.created_at.date()))
        self.assertEqual(payload["fatcaDeclarationDate"], str(self.app.created_at.date()))
