import json
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from onboarding_v2.constants import DocumentType
from onboarding_v2.models import LeadV2, ApplicationV2


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class PresignDocumentTests(TestCase):
    def setUp(self):
        self.client = Client()
        lead = LeadV2.objects.create(
            customer_id="CUST-PS-1",
            contact_number="9999999999",
            customer_name="Presign User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-PS-1", lead=lead)

    @patch("onboarding_v2.views.build_document_presign")
    def test_presign_returns_upload_urls(self, mock_presign):
        mock_presign.return_value = {
            "upload_url": "http://upload-url",
            "object_url": "http://object-url",
            "bucket": "bucket",
            "object_name": "key",
            "headers": {"Content-Type": "image/jpeg"},
        }
        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/documents/presign/",
            data=json.dumps({"document_type": DocumentType.PAN, "filename": "pan.jpg", "content_type": "image/jpeg"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]["upload"]
        self.assertEqual(data["upload_url"], "http://upload-url")
        self.assertEqual(data["object_url"], "http://object-url")
