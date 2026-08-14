from rest_framework import serializers


class GoldPledgeCardFileSerializer(serializers.Serializer):
    file_url = serializers.URLField(
        help_text="Publicly accessible or pre-signed URL of a Gold Pledge Card image/PDF."
    )
    document_id = serializers.CharField(max_length=255)


class GoldPledgeCardUploadSerializer(serializers.Serializer):
    file_urls = GoldPledgeCardFileSerializer(
        many=True,
        required=False,
        allow_empty=False,
        max_length=100,
        help_text="Gold Pledge Cards to process together under one batch ID.",
    )
    # Legacy single-card fields. New clients should use file_urls.
    file_url = serializers.URLField(required=False, write_only=True)
    document_id = serializers.CharField(required=False, max_length=255, write_only=True)

    def validate(self, attrs):
        files = attrs.get("file_urls")
        legacy_file_url = attrs.get("file_url")
        legacy_document_id = attrs.get("document_id")

        if files and (legacy_file_url or legacy_document_id):
            raise serializers.ValidationError(
                "Use either file_urls or the single-card fields, not both."
            )

        if not files:
            if not legacy_file_url or not legacy_document_id:
                raise serializers.ValidationError(
                    "file_urls is required, or provide both file_url and document_id."
                )
            files = [
                {
                    "file_url": legacy_file_url,
                    "document_id": legacy_document_id,
                }
            ]

        document_ids = [item["document_id"] for item in files]
        if len(document_ids) != len(set(document_ids)):
            raise serializers.ValidationError(
                {"file_urls": "Each document_id must be unique within the batch."}
            )

        attrs["file_urls"] = files
        return attrs


class GoldPledgeCardResultQuerySerializer(serializers.Serializer):
    batch_id = serializers.CharField(max_length=255)
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    per_page = serializers.IntegerField(
        required=False, default=50, min_value=1, max_value=100
    )
