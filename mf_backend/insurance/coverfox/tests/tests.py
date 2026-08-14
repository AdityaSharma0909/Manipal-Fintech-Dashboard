from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from insurance.coverfox.serializers import CoverFoxSerializer
from insurance.coverfox.views.coverfox import CoverFoxView


class CoverFoxSerializerTests(SimpleTestCase):
    def test_name_missing_returns_custom_error_message(self):
        serializer = CoverFoxSerializer(
            data={
                "mobile": "9876543210",
                "email": "test@example.com",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["name"][0], "Name is missing.")

    def test_mobile_must_be_exactly_10_digits(self):
        serializer = CoverFoxSerializer(
            data={
                "name": "John Doe",
                "mobile": "12345",
                "email": "test@example.com",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["mobile"][0],
            "Mobile number must be exactly 10 digits.",
        )

    def test_valid_payload_passes_validation(self):
        serializer = CoverFoxSerializer(
            data={
                "name": "John Doe",
                "mobile": "9876543210",
                "email": "test@example.com",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["mobile"],
            "9876543210",
        )


class CoverFoxViewTests(SimpleTestCase):
    def test_invalid_payload_returns_custom_response(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/insurance/coverfox/",
            {
                "mobile": "9876543210",
                "email": "test@example.com",
            },
            format="json",
        )
        user = type("User", (), {"is_authenticated": True, "role": "MEMBER"})()
        force_authenticate(request, user=user)

        response = CoverFoxView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {
                "success": False,
                "message": "Name is missing.",
                "data": None,
            },
        )
