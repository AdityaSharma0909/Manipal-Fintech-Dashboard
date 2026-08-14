import io
import os
import uuid
import unittest

import requests
from minio.error import S3Error

from onboarding_v2.storage import (
    get_minio_client,
    _resolve_bucket_name,
    ensure_bucket,
    generate_presigned_upload,
    generate_presigned_get,
)


@unittest.skipUnless(os.getenv("ENABLE_STORAGE_INTEGRATION_TEST") == "1", "Integration test disabled")
class StorageIntegrationTests(unittest.TestCase):
    """
    End-to-end check against the configured object storage (E2E/MinIO).
    Skips unless ENABLE_STORAGE_INTEGRATION_TEST=1 is set in the environment.
    """

    def test_put_get_delete_object(self):
        client = get_minio_client()
        bucket = _resolve_bucket_name()
        ensure_bucket(client, bucket)

        object_name = f"test/presign/{uuid.uuid4().hex}.txt"
        content = b"storage integration ping"
        data_stream = io.BytesIO(content)

        try:
            client.put_object(bucket, object_name, data_stream, len(content))
            resp = client.get_object(bucket, object_name)
            downloaded = resp.read()
            self.assertEqual(downloaded, content)
        finally:
            try:
                client.remove_object(bucket, object_name)
            except S3Error:
                pass

    def test_presign_put_and_get(self):
        """
        Use presigned PUT to upload and presigned GET to download, end-to-end against storage.
        """
        client = get_minio_client()
        bucket = _resolve_bucket_name()
        ensure_bucket(client, bucket)

        # Generate presign for upload
        presign = generate_presigned_upload(
            application_id="APP-INTEG",
            document_type="PAN",
            filename="test.txt",
            content_type="text/plain",
        )
        print(presign)
        upload_url = presign["upload_url"]
        object_name = presign["object_name"]
        content = b"presign integration content"

        # Upload via signed URL
        headers = presign.get("headers") or {}
        put_resp = requests.put(upload_url, data=content, headers=headers)
        self.assertEqual(put_resp.status_code, 200)

        # Presign GET and download
        get_url = generate_presigned_get(object_name=object_name)["get_url"]
        get_resp = requests.get(get_url)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.content, content)

        # Cleanup
        try:
            client.remove_object(bucket, object_name)
        except S3Error:
            pass
