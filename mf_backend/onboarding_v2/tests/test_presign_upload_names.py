from unittest.mock import patch

from django.test import TestCase, override_settings

from onboarding_v2.storage import generate_presigned_upload


class _DummyMinioClient:
    def __init__(self):
        self.created = []

    def bucket_exists(self, bucket):
        return True

    def make_bucket(self, bucket):
        self.created.append(bucket)

    def presigned_put_object(self, bucket, object_name, expires):
        return f"https://dummy/{bucket}/{object_name}"


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
)
class PresignUploadNameTests(TestCase):
    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_pan_uses_front_back_codes(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1", document_type="PAN", subtype="PAN_FRONT"
        )
        self.assertIn("/pan/", res["object_name"])
        self.assertIn("PAN_CARD_FRONT", res["object_name"])
        self.assertTrue(res["object_name"].endswith(".jpg"))
        res = generate_presigned_upload(
            application_id="APP-1", document_type="PAN", subtype="PAN_BACK"
        )
        self.assertIn("PAN_CARD_BACK", res["object_name"])

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_aadhaar_front_png_preserves_extension(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="AADHAAR",
            subtype="AADHAAR_FRONT",
            filename="anything.png",
            content_type="image/png",
        )
        self.assertIn("AADHAR_CARD_FRONT", res["object_name"])
        self.assertTrue(res["object_name"].endswith(".png"))
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="AADHAAR",
            subtype="AADHAAR_BACK",
            filename="anything.png",
            content_type="image/png",
        )
        self.assertIn("AADHAR_CARD_BACK", res["object_name"])

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_other_subtype_maps_form60(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="OTHER",
            subtype="form60",
            filename="file.pdf",
            content_type="application/pdf",
        )
        self.assertIn("FORM_60", res["object_name"])
        self.assertTrue(res["object_name"].endswith(".pdf"))

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_other_subtype_maps_utility_bill_default_ext(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="OTHER",
            subtype="utility_bill",
        )
        self.assertIn("UTILITY_BILL", res["object_name"])
        self.assertTrue(res["object_name"].endswith(".jpg"))

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_other_subtype_falls_back_to_normalized_code(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="OTHER",
            subtype="Cheque Copy",
            filename="cheque.jpeg",
        )
        self.assertIn("CHEQUE_COPY", res["object_name"])
        self.assertNotIn("/other/other", res["object_name"])

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_front_back_docs_use_distinct_codes(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="VOTER_ID",
            subtype="VOTER_ID_FRONT",
        )
        self.assertIn("VOTER_CARD_FRONT", res["object_name"])
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="VOTER_ID",
            subtype="VOTER_ID_BACK",
        )
        self.assertIn("VOTER_CARD_BACK", res["object_name"])
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="DRIVING_LICENSE",
            subtype="DRIVING_LICENSE_FRONT",
        )
        self.assertIn("DRIVING_LICENCE_FRONT", res["object_name"])
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="DRIVING_LICENSE",
            subtype="DRIVING_LICENSE_BACK",
        )
        self.assertIn("DRIVING_LICENCE_BACK", res["object_name"])
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="PASSPORT",
            subtype="PASSPORT_FRONT",
        )
        self.assertIn("PASSPORT_FRONT", res["object_name"])
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="PASSPORT",
            subtype="PASSPORT_BACK",
        )
        self.assertIn("PASSPORT_BACK", res["object_name"])

    @patch("onboarding_v2.storage.get_minio_client", return_value=_DummyMinioClient())
    def test_other_subtype_supports_saas_codes(self, _mock_client):
        res = generate_presigned_upload(
            application_id="APP-1",
            document_type="OTHER",
            subtype="ELECTRICITY_BILL",
        )
        self.assertIn("ELECTRICITY_BILL", res["object_name"])
