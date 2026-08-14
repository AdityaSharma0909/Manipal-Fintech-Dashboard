from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from onboarding_v2.models import Customers

@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class ValidatePanDefaulterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_validate_pan_no_matching_customer(self):
        # When no customer exists in the Customers table, the validation does not trigger defaulter logic.
        response = self.client.post(
            "/api/v2/onboarding/validate-pan/",
            data={
                "pan_card_number": "bodpa6506h",
                "contact_number": "+918000000001"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()["data"]
        self.assertNotEqual(res_data.get("message"), "defaulter")

    def test_validate_pan_matching_non_defaulter(self):
        # Create a non-defaulter customer
        Customers.objects.create(
            customer_id="CUST-1",
            name="Non Defaulter",
            phone_number="8000000001",
            pan_number="BODPA6506H",
            is_defaulter=False
        )
        response = self.client.post(
            "/api/v2/onboarding/validate-pan/",
            data={
                "pan_card_number": "bodpa6506h",
                "contact_number": "+918000000001"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()["data"]
        self.assertNotEqual(res_data.get("message"), "defaulter")

    def test_validate_pan_matching_defaulter_by_pan(self):
        # Create a defaulter customer matched by PAN
        Customers.objects.create(
            customer_id="CUST-2",
            name="Defaulter 2",
            phone_number="9999999999",  # different phone number
            pan_number="BODPA6506H",
            is_defaulter=True
        )
        response = self.client.post(
            "/api/v2/onboarding/validate-pan/",
            data={
                "pan_card_number": "bodpa6506h",  # lowercase PAN in input
                "contact_number": "+918000000001"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()["data"]
        self.assertEqual(res_data.get("message"), "defaulter")
        self.assertEqual(res_data.get("valid"), False)

    def test_validate_pan_matching_defaurter_by_phone(self):
        # Create a defaulter customer matched by phone (last 10 digits)
        Customers.objects.create(
            customer_id="CUST-3",
            name="Defaulter 3",
            phone_number="+918000000001",
            pan_number="ABCDE1234F",  # different PAN
            is_defaulter=True
        )
        response = self.client.post(
            "/api/v2/onboarding/validate-pan/",
            data={
                "pan_card_number": "bodpa6506h",
                "contact_number": "8000000001"  # 10 digits without prefix
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()["data"]
        self.assertEqual(res_data.get("message"), "defaulter")
        self.assertEqual(res_data.get("valid"), False)
