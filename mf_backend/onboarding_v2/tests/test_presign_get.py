import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from onboarding_v2.constants import DocumentType
from onboarding_v2.models import LeadV2, ApplicationV2, ApplicationDocument
from users.models import User


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class PresignGetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(username="agent", password="pass", phone="9000000000")
        self.client.force_authenticate(user=user)
        lead = LeadV2.objects.create(
            customer_id="CUST-PSG-1",
            contact_number="9999999999",
            customer_name="Presign User",
            product_category="LOAN",
            assigned_to=user,
        )
        self.app = ApplicationV2.objects.create(application_id="APP-PSG-1", lead=lead)
        ApplicationDocument.objects.create(
            application=self.app,
            document_type=DocumentType.PAN,
            file_url="http://minio/bucket/env/manipal/APP-PSG-1/pan/pan.jpg",
        )

    @patch("onboarding_v2.views.build_document_download_presign")
    def test_presign_get_by_document_type(self, mock_presign):
        mock_presign.return_value = {"get_url": "http://signed-url", "bucket": "bucket", "object_name": "path"}
        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/documents/presign-get/",
            data=json.dumps({"document_type": DocumentType.PAN}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]["download"]
        self.assertEqual(data["get_url"], "http://signed-url")
