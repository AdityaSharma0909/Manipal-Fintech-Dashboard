from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from .serializers import GoldPledgeCardUploadSerializer
from .services import AtlasAPIError, AtlasGoldPledgeCardClient


ATLAS_SETTINGS = {
    "ATLAS_DOCSTREAM_BASE_URL": "https://docstream.example.com",
    "ATLAS_CLIENT_ID": "client-id",
    "ATLAS_CLIENT_SECRET": "client-secret",
    "ATLAS_PRODUCT_TYPE": "MANIPAL_FINTECH_POC",
    "ATLAS_REQUEST_TIMEOUT": 20,
}


@override_settings(**ATLAS_SETTINGS)
class AtlasGoldPledgeCardClientTests(SimpleTestCase):
    @patch("atlas_ocr.services.requests.post")
    def test_submit_authenticates_and_uploads_expected_payload(self, post):
        auth_response = Mock(ok=True)
        auth_response.json.return_value = {"access_token": "jwt-token"}
        upload_response = Mock(ok=True)
        upload_response.json.return_value = {"batch_id": "batch-1"}
        post.side_effect = [auth_response, upload_response]

        files = [
            {
                "file_url": "https://files.example.com/card-1.jpg",
                "document_id": "gold-card-1",
            },
            {
                "file_url": "https://files.example.com/card-2.jpg",
                "document_id": "gold-card-2",
            },
        ]
        result = AtlasGoldPledgeCardClient().submit(files)

        self.assertEqual(result, {"batch_id": "batch-1"})
        self.assertEqual(
            post.call_args_list[1].kwargs["json"],
            {
                "product_type": "MANIPAL_FINTECH_POC",
                "file_urls": files,
            },
        )

    @patch("atlas_ocr.services.requests.post")
    def test_invalid_credentials_become_provider_error(self, post):
        response = Mock(ok=False, status_code=401)
        response.json.return_value = {"message": "Invalid credentials"}
        post.return_value = response

        with self.assertRaises(AtlasAPIError) as context:
            AtlasGoldPledgeCardClient().submit(
                "https://files.example.com/card.jpg", "gold-card-1"
            )

        self.assertEqual(context.exception.status_code, 401)

    @patch("atlas_ocr.services.requests.get")
    @patch("atlas_ocr.services.requests.post")
    def test_get_result_uses_batch_id(self, post, get):
        auth_response = Mock(ok=True)
        auth_response.json.return_value = {"access_token": "jwt-token"}
        post.return_value = auth_response
        result_response = Mock(ok=True)
        result_response.json.return_value = {"data": []}
        get.return_value = result_response

        result = AtlasGoldPledgeCardClient().get_result("batch-1")

        self.assertEqual(result, {"data": []})
        self.assertEqual(get.call_args.kwargs["params"]["batch_id"], "batch-1")


class GoldPledgeCardUploadSerializerTests(SimpleTestCase):
    def test_accepts_multiple_files(self):
        serializer = GoldPledgeCardUploadSerializer(
            data={
                "file_urls": [
                    {
                        "file_url": "https://files.example.com/card-1.jpg",
                        "document_id": "card-1",
                    },
                    {
                        "file_url": "https://files.example.com/card-2.jpg",
                        "document_id": "card-2",
                    },
                ]
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data["file_urls"]), 2)

    def test_rejects_duplicate_document_ids(self):
        serializer = GoldPledgeCardUploadSerializer(
            data={
                "file_urls": [
                    {
                        "file_url": "https://files.example.com/card-1.jpg",
                        "document_id": "same-id",
                    },
                    {
                        "file_url": "https://files.example.com/card-2.jpg",
                        "document_id": "same-id",
                    },
                ]
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_preserves_single_file_payload_compatibility(self):
        serializer = GoldPledgeCardUploadSerializer(
            data={
                "file_url": "https://files.example.com/card.jpg",
                "document_id": "card-1",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data["file_urls"]), 1)
