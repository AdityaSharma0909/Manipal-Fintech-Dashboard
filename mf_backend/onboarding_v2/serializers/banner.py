import os

from rest_framework import serializers

from onboarding_v2.models import Banner
from onboarding_v2.storage import generate_presigned_get

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


class BannerUploadSerializer(serializers.Serializer):
    """
    Used when the web side uploads banners in bulk.

    Accepts a list of objects via the parent ``BannerBulkUploadSerializer``.
    Each object must carry a valid image ``file`` (multipart), a ``title``,
    and a ``message``.  The ``file_url`` is populated by the view after
    persisting / uploading the file.
    """

    file = serializers.ImageField(
        help_text="Banner image — PNG or JPEG, max 2 MB.",
        error_messages={
            "required": "Banner image file is required.",
            "invalid": "Upload a valid image file.",
            "empty": "Uploaded file is empty.",
        },
    )
    title = serializers.CharField(
        max_length=255,
        error_messages={
            "required": "Title is required.",
            "blank": "Title cannot be blank.",
        },
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        error_messages={
            "blank": "Message cannot be blank.",
        },
    )
    status = serializers.ChoiceField(
        choices=Banner.Status.choices,
        required=False,
        default=Banner.Status.ACTIVE,
    )

    def validate_file(self, value):
        # ── size check ────────────────────────────────────────────────────
        if value.size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"File size must be less than 2 MB. "
                f"Uploaded file is {value.size / (1024 * 1024):.2f} MB."
            )

        # ── content-type check ────────────────────────────────────────────
        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Unsupported file type '{content_type}'. "
                "Only PNG and JPEG images are allowed."
            )

        # ── extension check (secondary guard) ────────────────────────────
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported file extension '{ext}'. "
                "Only .png, .jpg, and .jpeg files are allowed."
            )

        return value


class BannerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used **after** the file has been uploaded and its URL is known.
    Saves the banner record to the database.
    """

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ["id", "file_url", "title", "message", "status", "is_active", "created_at"]
        read_only_fields = ["id", "status", "is_active", "created_at"]

    def get_file_url(self, obj):
        return _public_banner_url(obj.file_url)


class BannerListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer returned to the **app side** (GET request).
    Returns only active banners by default (filtered at the view level).
    """

    file_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ["id", "file_url", "title", "message", "status", "is_active", "created_at"]

    def get_file_url(self, obj):
        return _public_banner_url(obj.file_url)

    def get_status(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"


class BannerDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for detail / update / delete operations (admin web side).
    """

    file_url = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Banner
        fields = ["id", "file_url", "title", "message", "status", "is_active", "created_at", "modified_at"]
        read_only_fields = ["id", "status", "created_at", "modified_at"]
        extra_kwargs = {
            "message": {"required": False, "allow_blank": True},
        }

    def get_file_url(self, obj):
        return _public_banner_url(obj.file_url)

    def get_status(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"


def _public_banner_url(file_url):
    if not file_url:
        return file_url

    try:
        presigned = generate_presigned_get(file_url=file_url)
    except Exception:
        return file_url

    return presigned.get("get_url") or file_url
