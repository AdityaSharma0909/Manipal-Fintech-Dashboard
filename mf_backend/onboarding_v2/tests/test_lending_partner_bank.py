from django.test import TestCase, Client, override_settings
from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import ApplicationV2, LeadV2, ApplicationStageSnapshot, LendingPartnerMaster, BankBranch
from onboarding_v2.serializers import LendingPartnerBankSerializer
from onboarding_v2.views.stages import SubmitApplicationView
from users.models import User

@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
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
)
class LendingPartnerBankTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="so_user",
            phone="+911234567890",
            role="ADMIN",
            employee_id="EMPL123",
        )
        self.lead = LeadV2.objects.create(
            customer_id="CUST-111",
            contact_number="8888888888",
            customer_name="Bob Doe",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_type="CO_LENDING",
            created_by=self.user,
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-111",
            lead=self.lead,
            loan_type="CO_LENDING",
            stage=ApplicationStage.LENDING_PARTNER_BANK,
        )
        # Create LendingPartnerMaster entries
        LendingPartnerMaster.objects.create(bank_name="AXIS_BANK", available_for="GOLD_LOAN")
        BankBranch.objects.create(
            bank_name="Axis Bank",
            branch_name="Axis Kargil Branch",
            branch_code="BR123",
            pincode="148401",
            sol_id="0056",
        )
        # Force login the user to bypass authentication checks
        self.client.force_login(self.user)

        # Mock SubmitApplicationView authentication to prevent 401 in tests
        self.original_auth = SubmitApplicationView.authentication_classes
        self.original_perm = SubmitApplicationView.permission_classes
        SubmitApplicationView.authentication_classes = []
        SubmitApplicationView.permission_classes = []

    def tearDown(self):
        SubmitApplicationView.authentication_classes = self.original_auth
        SubmitApplicationView.permission_classes = self.original_perm

    def test_serializer_validation(self):
        data = {
            "lending_partner": "AXIS_BANK",
            "pincode": "148401",
            "lending_partner_branch_code": "BR123",
            "lending_partner_branch_name": "Axis Kargil Branch"
        }
        serializer = LendingPartnerBankSerializer(
            data=data,
            context={"application": self.app}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["lending_partner"], "AXIS_BANK")
        self.assertEqual(serializer.validated_data["pincode"], "148401")
        self.assertEqual(serializer.validated_data["lending_partner_branch_code"], "BR123")
        self.assertEqual(serializer.validated_data["lending_partner_branch_name"], "Axis Kargil Branch")

        # Invalid lending partner check
        data_invalid = {
            "lending_partner": "INVALID_BANK",
            "pincode": "148401",
            "lending_partner_branch_code": "BR123",
            "lending_partner_branch_name": "Axis Kargil Branch"
        }
        serializer_invalid = LendingPartnerBankSerializer(
            data=data_invalid,
            context={"application": self.app}
        )
        self.assertFalse(serializer_invalid.is_valid())

        # Test optional lending_partner_branch_code (missing)
        data_missing = {
            "lending_partner": "AXIS_BANK",
            "pincode": "148401",
            "lending_partner_branch_name": "Axis Kargil Branch"
        }
        serializer_missing = LendingPartnerBankSerializer(
            data=data_missing,
            context={"application": self.app}
        )
        self.assertTrue(serializer_missing.is_valid(), serializer_missing.errors)
        self.assertNotIn("lending_partner_branch_code", serializer_missing.validated_data)

        # Test optional lending_partner_branch_code (null)
        data_null = {
            "lending_partner": "AXIS_BANK",
            "pincode": "148401",
            "lending_partner_branch_code": None,
            "lending_partner_branch_name": "Axis Kargil Branch"
        }
        serializer_null = LendingPartnerBankSerializer(
            data=data_null,
            context={"application": self.app}
        )
        self.assertTrue(serializer_null.is_valid(), serializer_null.errors)
        self.assertIsNone(serializer_null.validated_data["lending_partner_branch_code"])

        # Test optional lending_partner_branch_code (blank)
        data_blank = {
            "lending_partner": "AXIS_BANK",
            "pincode": "148401",
            "lending_partner_branch_code": "",
            "lending_partner_branch_name": "Axis Kargil Branch"
        }
        serializer_blank = LendingPartnerBankSerializer(
            data=data_blank,
            context={"application": self.app}
        )
        self.assertTrue(serializer_blank.is_valid(), serializer_blank.errors)
        self.assertEqual(serializer_blank.validated_data["lending_partner_branch_code"], "")

    def test_stage_update_api_saves_lending_partner(self):
        post_data = {
            "stage": "LENDING_PARTNER_BANK",
            "payload": {
                "lending_partner": "AXIS_BANK",
                "pincode": "148401",
                "lending_partner_branch_code": "BR123",
                "lending_partner_branch_name": "Axis Kargil Branch"
            },
            "is_complete": True
        }
        response = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/stage/",
            data=post_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200, response.content)

        # Refresh application and check stage_payload
        self.app.refresh_from_db()
        stage_payload = self.app.stage_payload
        self.assertIn("lending_partner_bank", stage_payload)
        self.assertEqual(stage_payload["lending_partner_bank"]["lending_partner"], "AXIS_BANK")
        self.assertEqual(stage_payload["lending_partner_bank"]["pincode"], "148401")
        self.assertEqual(stage_payload["lending_partner_bank"]["lending_partner_branch_code"], "BR123")
        self.assertEqual(stage_payload["lending_partner_bank"]["lending_partner_branch_name"], "Axis Kargil Branch")
        self.assertEqual(stage_payload["lending_partner_bank"]["client_loan_id"], "GLN00567")

        # Check fields updated on application and lead
        self.assertEqual(self.app.lending_partner, "AXIS_BANK")
        self.assertEqual(self.app.partner_branch_code, "BR123")
        self.assertEqual(self.app.partner_branch_name, "Axis Kargil Branch")
        self.assertEqual(self.app.client_loan_id, "GLN00567")
        self.app.lead.refresh_from_db()
        self.assertEqual(self.app.lead.lending_partner, "AXIS_BANK")

        # Check stage is LENDING_PARTNER_BANK
        self.assertEqual(self.app.stage, ApplicationStage.LENDING_PARTNER_BANK)

        # Check snapshot is saved
        snapshot = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.LENDING_PARTNER_BANK)
        self.assertTrue(snapshot.is_complete)
        self.assertEqual(snapshot.payload["lending_partner"], "AXIS_BANK")
        self.assertEqual(snapshot.payload["pincode"], "148401")
        self.assertEqual(snapshot.payload["lending_partner_branch_code"], "BR123")
        self.assertEqual(snapshot.payload["lending_partner_branch_name"], "Axis Kargil Branch")
        self.assertEqual(snapshot.payload["client_loan_id"], "GLN00567")

        # Submit / transition stage
        submit_data = {
            "current_stage": "LENDING_PARTNER_BANK"
        }
        submit_resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/submit/",
            data=submit_data,
            content_type="application/json"
        )
        self.assertEqual(submit_resp.status_code, 200, submit_resp.content)
        resp_data = submit_resp.json()
        self.assertEqual(resp_data["data"]["next_stage"], ApplicationStage.LOAN_RANGE_SELECTION)
        self.assertEqual(resp_data["data"]["completion_percentage"], 25)

    def test_stage_update_api_saves_lending_partner_without_branch_code(self):
        post_data = {
            "stage": "LENDING_PARTNER_BANK",
            "payload": {
                "lending_partner": "AXIS_BANK",
                "pincode": "148401",
                "lending_partner_branch_name": "Axis Kargil Branch"
            },
            "is_complete": True
        }
        response = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/stage/",
            data=post_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200, response.content)

        # Refresh application and check stage_payload
        self.app.refresh_from_db()
        stage_payload = self.app.stage_payload
        self.assertIn("lending_partner_bank", stage_payload)
        self.assertEqual(stage_payload["lending_partner_bank"]["lending_partner"], "AXIS_BANK")
        self.assertEqual(stage_payload["lending_partner_bank"]["pincode"], "148401")
        self.assertNotIn("lending_partner_branch_code", stage_payload["lending_partner_bank"])
        self.assertEqual(stage_payload["lending_partner_bank"]["lending_partner_branch_name"], "Axis Kargil Branch")

        # Check fields on application
        self.assertEqual(self.app.lending_partner, "AXIS_BANK")
        self.assertIsNone(self.app.partner_branch_code)
        self.assertEqual(self.app.partner_branch_name, "Axis Kargil Branch")
