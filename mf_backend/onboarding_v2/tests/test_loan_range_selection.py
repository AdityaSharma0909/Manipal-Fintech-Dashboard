from django.test import TestCase, Client, override_settings
from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import ApplicationV2, LeadV2, ApplicationStageSnapshot
from onboarding_v2.serializers import LoanRangeSelectionSerializer
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
class LoanRangeSelectionTests(TestCase):
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
            created_by=self.user,
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-111",
            lead=self.lead,
        )
        # Force login the user to bypass authentication checks
        self.client.force_login(self.user)

    def test_serializer_validation(self):
        # Test with above_range=True
        data = {
            "loan_amount": 250000.00,
            "above_range": True
        }
        serializer = LoanRangeSelectionSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["loan_amount"], 250000.00)
        self.assertEqual(serializer.validated_data["above_range"], True)

        # Legacy typo should still be accepted and normalized.
        legacy_data = {
            "loan_amount": 250000.00,
            "avobe_range": True
        }
        legacy_serializer = LoanRangeSelectionSerializer(data=legacy_data)
        self.assertTrue(legacy_serializer.is_valid(), legacy_serializer.errors)
        self.assertEqual(legacy_serializer.validated_data["above_range"], True)

        # Test with above_range omitted (should still be valid)
        data_omitted = {
            "loan_amount": 150000.00
        }
        serializer_omitted = LoanRangeSelectionSerializer(data=data_omitted)
        self.assertTrue(serializer_omitted.is_valid(), serializer_omitted.errors)
        self.assertEqual(serializer_omitted.validated_data["loan_amount"], 150000.00)
        self.assertNotIn("above_range", serializer_omitted.validated_data)

    def test_stage_update_api_saves_above_range(self):
        post_data = {
            "stage": "LOAN_RANGE_SELECTION",
            "payload": {
                "loan_amount": 250000.00,
                "above_range": True
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
        self.assertIn("loan_range_selection", stage_payload)
        self.assertEqual(stage_payload["loan_range_selection"]["loan_amount"], "250000.00")
        self.assertEqual(stage_payload["loan_range_selection"]["above_range"], True)

        # Check lead amount updated
        self.app.lead.refresh_from_db()
        self.assertEqual(self.app.lead.amount, 250000.00)

        # Check snapshot is saved
        snapshot = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.LOAN_RANGE_SELECTION)
        self.assertTrue(snapshot.is_complete)
        self.assertEqual(snapshot.payload["loan_amount"], "250000.00")
        self.assertEqual(snapshot.payload["above_range"], True)
