from unittest.mock import patch

from django.test import TestCase, override_settings

from onboarding_v2.models import LeadV2, ApplicationV2
import logging


@override_settings(MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None})
class PresignEndpointTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-PRE-1",
            lead_code="GL0001",
            contact_number="9000000000",
            customer_name="Presign User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-PRE-1", lead=self.lead)

    @patch("onboarding_v2.views.build_document_presign")
    def test_presign_upload_success(self, mock_presign):
        mock_presign.return_value = {
            "bucket": "manipal-dev",
            "object_name": "env/manipal/APP-PRE-1/pan/PAN_CARD_BACK.jpg",
            "upload_url": "https://example.com/upload",
            "object_url": "https://example.com/object",
            "headers": {"Content-Type": "image/jpeg"},
        }

        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/documents/presign/",
            data={
                "document_type": "PAN",
                "filename": "pan.jpg",
                "content_type": "image/jpeg",
            },
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json().get("data", {})
        self.assertIn("upload", payload)
        upload = payload["upload"]
        self.assertEqual(upload["bucket"], "manipal-dev")
        self.assertEqual(upload["upload_url"], "https://example.com/upload")

    def test_presign_upload_bad_application(self):
        resp = self.client.post(
            "/api/v2/onboarding/applications/APP-MISSING/documents/presign/",
            data={"document_type": "PAN"},
        )
        self.assertEqual(resp.status_code, 400)

    @patch("onboarding_v2.views.build_document_presign")
    def test_presign_logs_payload(self, mock_presign):
        mock_presign.return_value = {
            "bucket": "manipal-dev",
            "object_name": "env/manipal/APP-PRE-1/pan/PAN_CARD_BACK.jpg",
            "upload_url": "https://example.com/upload",
            "object_url": "https://example.com/object",
            "headers": {"Content-Type": "image/jpeg"},
        }
        with self.assertLogs("onboarding_v2.views", level="INFO") as cm:
            resp = self.client.post(
                f"/api/v2/onboarding/applications/{self.app.application_id}/documents/presign/",
                data={
                    "document_type": "PAN",
                    "filename": "pan.jpg",
                    "content_type": "image/jpeg",
                },
            )
        self.assertEqual(resp.status_code, 200)
        combined = " ".join(cm.output)
        self.assertIn("Presign upload generated", combined)
        self.assertIn("PAN_CARD_BACK.jpg", combined)
