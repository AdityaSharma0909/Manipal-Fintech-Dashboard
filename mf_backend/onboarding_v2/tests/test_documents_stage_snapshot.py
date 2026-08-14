import json

from django.test import Client, TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, DocumentType
from onboarding_v2.models import ApplicationV2, LeadV2


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class DocumentStageSnapshotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.lead = LeadV2.objects.create(
            customer_id="CUST-DOC-2",
            lead_code="GLDOC2",
            contact_number="9000000001",
            customer_name="Doc Snapshot User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(application_id="APP-DOC-2", lead=self.lead)

    def _post_documents_stage(self, payload):
        return self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/stage/",
            data=json.dumps({"stage": ApplicationStage.DOCUMENTS, "payload": payload, "is_complete": True}),
            content_type="application/json",
        )

    def _get_documents_snapshot_payload(self):
        resp = self.client.get(
            f"/api/v2/onboarding/applications/{self.app.application_id}/state/"
        )
        self.assertEqual(resp.status_code, 200)
        snapshots = resp.json()["data"]["application"]["snapshots"]
        doc_snap = next(s for s in snapshots if s["stage"] == ApplicationStage.DOCUMENTS)
        return doc_snap["payload"]

    def test_documents_stage_merges_across_calls(self):
        resp = self._post_documents_stage(
            [{"document_type": DocumentType.PAN, "file_url": "https://cdn.example.com/pan-1.jpg"}]
        )
        self.assertEqual(resp.status_code, 200)

        resp = self._post_documents_stage(
            [{"document_type": DocumentType.PAN, "file_url": "https://cdn.example.com/pan-2.jpg"}]
        )
        self.assertEqual(resp.status_code, 200)

        payload = self._get_documents_snapshot_payload()
        urls = [item["file_url"] for item in payload if item["document_type"] == DocumentType.PAN]
        self.assertEqual(urls, ["https://cdn.example.com/pan-2.jpg"])

    def test_documents_stage_dedupes_same_file_url(self):
        doc = {
            "document_type": DocumentType.AADHAAR,
            "subtype": "AADHAAR_FRONT",
            "file_url": "https://cdn.example.com/aadhaar.jpg",
        }
        resp = self._post_documents_stage([doc])
        self.assertEqual(resp.status_code, 200)

        resp = self._post_documents_stage([doc])
        self.assertEqual(resp.status_code, 200)

        payload = self._get_documents_snapshot_payload()
        urls = [item["file_url"] for item in payload if item["document_type"] == DocumentType.AADHAAR]
        self.assertEqual(urls, ["https://cdn.example.com/aadhaar.jpg"])

    def test_documents_stage_keeps_distinct_subtypes(self):
        resp = self._post_documents_stage(
            [
                {
                    "document_type": DocumentType.VOTER_ID,
                    "subtype": "VOTER_FRONT",
                    "file_url": "https://cdn.example.com/voter-front.jpg",
                }
            ]
        )
        self.assertEqual(resp.status_code, 200)

        resp = self._post_documents_stage(
            [
                {
                    "document_type": DocumentType.VOTER_ID,
                    "subtype": "VOTER_BACK",
                    "file_url": "https://cdn.example.com/voter-back.jpg",
                }
            ]
        )
        self.assertEqual(resp.status_code, 200)

        payload = self._get_documents_snapshot_payload()
        urls = [item["file_url"] for item in payload if item["document_type"] == DocumentType.VOTER_ID]
        self.assertEqual(
            set(urls),
            {"https://cdn.example.com/voter-front.jpg", "https://cdn.example.com/voter-back.jpg"},
        )

    def test_documents_stage_keeps_distinct_subtypes_with_same_url(self):
        shared_url = "https://cdn.example.com/voter-both.jpg"
        resp = self._post_documents_stage(
            [
                {
                    "document_type": DocumentType.VOTER_ID,
                    "subtype": "VOTER_FRONT",
                    "file_url": shared_url,
                }
            ]
        )
        self.assertEqual(resp.status_code, 200)

        resp = self._post_documents_stage(
            [
                {
                    "document_type": DocumentType.VOTER_ID,
                    "subtype": "VOTER_BACK",
                    "file_url": shared_url,
                }
            ]
        )
        self.assertEqual(resp.status_code, 200)

        payload = self._get_documents_snapshot_payload()
        voter_docs = [item for item in payload if item["document_type"] == DocumentType.VOTER_ID]
        self.assertEqual({item.get("subtype") for item in voter_docs}, {"VOTER_FRONT", "VOTER_BACK"})
