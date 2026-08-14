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
class CustomerDefaulterCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v2/onboarding/customers/defaulter-check/"

    def test_defaulter_match_by_pan(self):
        Customers.objects.create(
            customer_id="CUST-DF-PAN",
            name="Defaulter Pan",
            phone_number="9999999999",
            pan_number="ABCDE1234F",
            is_defaulter=True,
        )

        response = self.client.post(
            self.url,
            data={"pan": "abcde1234f", "contact_number": "8000000001"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["is_defaulter"])
        self.assertTrue(data["customer_found"])
        self.assertEqual(
            data["message"],
            "This applicant cannot be onboarded due to adverse repayment history.",
        )

    def test_defaulter_match_by_contact_number_last_10_digits(self):
        Customers.objects.create(
            customer_id="CUST-DF-PHONE",
            name="Defaulter Phone",
            phone_number="+918000000001",
            pan_number="ZZZZZ9999Z",
            is_defaulter=True,
        )

        response = self.client.post(
            self.url,
            data={"pan_number": "ABCDE1234F", "contact_number": "8000000001"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["is_defaulter"])
        self.assertTrue(data["customer_found"])

    def test_matching_non_defaulter_customer(self):
        Customers.objects.create(
            customer_id="CUST-NON-DF",
            name="Non Defaulter",
            phone_number="8000000001",
            pan_number="ABCDE1234F",
            is_defaulter=False,
        )

        response = self.client.post(
            self.url,
            data={"pan_number": "ABCDE1234F", "contact_number": "+918000000001"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertFalse(data["is_defaulter"])
        self.assertTrue(data["customer_found"])
        self.assertEqual(data["message"], "not_defaulter")

    def test_no_matching_customer(self):
        response = self.client.post(
            self.url,
            data={"pan_number": "ABCDE1234F", "contact_number": "8000000001"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertFalse(data["is_defaulter"])
        self.assertFalse(data["customer_found"])

    def test_invalid_payload_returns_bad_request(self):
        response = self.client.post(
            self.url,
            data={"pan_number": "", "contact_number": "12345"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
