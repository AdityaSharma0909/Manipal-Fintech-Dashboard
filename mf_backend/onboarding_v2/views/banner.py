"""
Banner API Views
================

POST /banners/upload/  — Web-admin: upload multiple banner images (multipart/form-data)
GET  /banners/         — App-side : retrieve all active banners
GET  /banners/<id>/    — Admin    : retrieve a single banner
PATCH /banners/<id>/   — Admin    : update title / message / is_active
DELETE /banners/<id>/  — Admin    : soft-delete (set is_active=False) or hard-delete
"""

import io
import logging
import uuid
from urllib.parse import urljoin

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from onboarding_v2.views.common import DefaultPagination
from onboarding_v2.models import Banner
from onboarding_v2.serializers.banner import (
    BannerUploadSerializer,
    BannerCreateSerializer,
    BannerListSerializer,
    BannerDetailSerializer,
)
from onboarding_v2.storage import (
    get_minio_client,
    _resolve_bucket_name,
    ensure_bucket,
    _storage_scheme,
)
from utils.envSetup import environment
from utils.responseHandler import HttpResponse

log = logging.getLogger("logs")


# ---------------------------------------------------------------------------
# Helper – upload a single in-memory file to MinIO
# ---------------------------------------------------------------------------

def _upload_banner_image(file_obj) -> str:
    """
    Upload *file_obj* (InMemoryUploadedFile / TemporaryUploadedFile) to MinIO
    under the ``banners/`` prefix and return the canonical public URL.
    """
    client = get_minio_client()
    bucket = _resolve_bucket_name()
    ensure_bucket(client, bucket)

    ext = "." + file_obj.name.rsplit(".", 1)[-1].lower() if "." in file_obj.name else ".jpg"
    unique_id = uuid.uuid4().hex[:12]
    safe_name = f"banner_{unique_id}{ext}"
    env_prefix = (environment.APP_ENV or "env").lower()
    object_name = f"{env_prefix}/banners/{safe_name}"

    content_type = getattr(file_obj, "content_type", "image/jpeg") or "image/jpeg"

    # Read content into bytes
    file_obj.seek(0)
    content = file_obj.read()
    data_stream = io.BytesIO(content)

    client.put_object(
        bucket,
        object_name,
        data_stream,
        len(content),
        content_type=content_type,
    )

    scheme = _storage_scheme()
    base = f"{scheme}://{environment.STORAGE_ENDPOINT}/"
    object_url = urljoin(base, f"{bucket}/{object_name}")
    return object_url


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class BannerUploadView(APIView):
    """
    POST — Web-admin uploads one or more banner images.

    Request (multipart/form-data):
        file_0, title_0, message_0,
        file_1, title_1, message_1,
        ...  (indexed by position)

    Response 201:
        [
            {"id": "...", "file_url": "...", "title": "...", "message": "..."},
            ...
        ]
    """

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["Banner"],
        operation_id="banner_upload",
        summary="Upload multiple banners (web admin)",
        description=(
            "Accepts multiple banner images in a single multipart request. "
            "Each banner is identified by a numeric index suffix on the field names: "
            "``file_0``, ``title_0``, ``message_0``, ``file_1``, ``title_1``, ``message_1``, …\n\n"
            "**Constraints:** PNG / JPEG only, max 2 MB per file."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file_0": {"type": "string", "format": "binary", "description": "First banner image (PNG/JPEG)"},
                    "title_0": {"type": "string", "description": "Title for the first banner"},
                    "message_0": {"type": "string", "description": "Message for the first banner"},
                    "file_1": {"type": "string", "format": "binary", "description": "Second banner image (optional)"},
                    "title_1": {"type": "string", "description": "Title for the second banner (optional)"},
                    "message_1": {"type": "string", "description": "Message for the second banner (optional)"},
                    "status_1": {"type": "string", "description": "Status for the second banner (optional)"},
                },
                "required": ["file_0", "title_0"]
            }
        },
        responses={
            201: inline_serializer(
                name="BannerUploadResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "data": BannerCreateSerializer(many=True),
                }
            )
        },
    )
    def post(self, request):
        # ── Collect indexed banner groups from the multipart payload ──────
        banners_input = []
        index = 0
        while True:
            file_key = f"file_{index}"
            title_key = f"title_{index}"
            message_key = f"message_{index}"
            status_key = f"status_{index}"

            file_obj = request.FILES.get(file_key)
            title = request.data.get(title_key)
            message = request.data.get(message_key)
            status = request.data.get(status_key)

            # Stop when we no longer find an indexed entry
            if file_obj is None and title is None and message is None and status is None:
                break

            banners_input.append(
                {
                    "index": index,
                    "file": file_obj,
                    "title": title,
                    "message": message,
                    "status": status,
                }
            )
            index += 1

        if not banners_input:
            return HttpResponse.BadRequest(
                "No banner data found. "
                "Send fields as file_0, title_0, message_0, file_1, …"
            )

        # ── Validate every banner before persisting any ───────────────────
        validation_errors = []
        for item in banners_input:
            data = {
                "file": item["file"],
                "title": item["title"],
                "message": item["message"] or "",
            }
            if item.get("status"):
                data["status"] = item["status"]
            serializer = BannerUploadSerializer(data=data)
            if not serializer.is_valid():
                validation_errors.append(
                    {"index": item["index"], "errors": serializer.errors}
                )
            else:
                item.update(serializer.validated_data)

        if validation_errors:
            return HttpResponse.BadRequest(
                "Validation failed for one or more banners.",
                data=validation_errors,
            )

        # ── Upload & persist ──────────────────────────────────────────────
        created_banners = []
        upload_errors = []

        for item in banners_input:
            try:
                file_url = _upload_banner_image(item["file"])
                banner = Banner.objects.create(
                    file_url=file_url,
                    title=item["title"],
                    message=item["message"],
                )
                created_banners.append(banner)
                log.info("Banner created: id=%s title=%s", banner.id, banner.title)
            except Exception as exc:
                log.exception("Failed to upload banner at index %s", item["index"])
                upload_errors.append({"index": item["index"], "error": str(exc)})

        if upload_errors:
            # Partial success — return what was created and what failed
            return HttpResponse.BadRequest(
                "Some banners could not be uploaded.",
                data={
                    "created": BannerCreateSerializer(created_banners, many=True).data,
                    "failed": upload_errors,
                },
            )

        serializer = BannerCreateSerializer(created_banners, many=True)
        from rest_framework import status
        from rest_framework.response import Response
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class BannerListView(APIView):
    """
    GET — App-side retrieves all currently active banners.

    Response 200:
        [
            {"id": "...", "file_url": "...", "title": "...", "message": "..."},
            ...
        ]
    """

    @extend_schema(
        tags=["Banner"],
        operation_id="banner_list",
        summary="List banners",
        description="Returns all banners, including inactive ones. You can filter by `is_active` (true/false) if needed.",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, description="A page number within the paginated result set."),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Number of results to return per page."),
            OpenApiParameter("is_active", OpenApiTypes.BOOL, description="Filter by active status (true/false)."),
        ],
        responses={
            200: inline_serializer(
                name="BannerListResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "data": inline_serializer(
                        name="BannerPaginatedData",
                        fields={
                            "count": serializers.IntegerField(),
                            "next": serializers.URLField(allow_null=True),
                            "previous": serializers.URLField(allow_null=True),
                            "results": BannerListSerializer(many=True)
                        }
                    )
                }
            )
        },
    )
    def get(self, request):
        banners = Banner.objects.all().order_by("-created_at")
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = str(is_active).lower() in ["true", "1", "yes"]
            banners = banners.filter(is_active=is_active_bool)

        paginator = DefaultPagination()
        paginated_banners = paginator.paginate_queryset(banners, request)
        serializer = BannerListSerializer(paginated_banners, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        
        # We extract `.data` from the paginated response to wrap it inside HttpResponse.Success
        return HttpResponse.Success(paginated_response.data)


class BannerDetailView(APIView):
    """
    GET    /banners/<id>/  — Retrieve a single banner (admin).
    PATCH  /banners/<id>/  — Update title / message / is_active.
    DELETE /banners/<id>/  — Hard-delete the banner record.
    """

    def _get_banner(self, banner_id):
        try:
            return Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return None

    @extend_schema(
        tags=["Banner"],
        operation_id="banner_detail",
        summary="Retrieve a single banner",
        responses={
            200: inline_serializer(
                name="BannerDetailResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "data": BannerDetailSerializer(),
                }
            )
        },
    )
    def get(self, request, banner_id):
        banner = self._get_banner(banner_id)
        if banner is None:
            return HttpResponse.NotFound(f"Banner '{banner_id}' not found.")
        serializer = BannerDetailSerializer(banner)
        return HttpResponse.Success(serializer.data)

    @extend_schema(
        tags=["Banner"],
        operation_id="banner_partial_update",
        summary="Update a banner's title, message, or active status",
        request=BannerDetailSerializer,
        responses={
            200: inline_serializer(
                name="BannerUpdateResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "data": BannerDetailSerializer(),
                }
            )
        },
    )
    def patch(self, request, banner_id):
        banner = self._get_banner(banner_id)
        if banner is None:
            return HttpResponse.NotFound(f"Banner '{banner_id}' not found.")

        log.info("Banner PATCH request data: %s", request.data)
        serializer = BannerDetailSerializer(banner, data=request.data, partial=True)
        if not serializer.is_valid():
            return HttpResponse.BadRequest("Validation failed.", data=serializer.errors)

        log.info("Banner PATCH validated_data: %s", serializer.validated_data)
        serializer.save()
        log.info("Banner updated: id=%s, status=%s, is_active=%s", banner_id, banner.status, banner.is_active)
        return HttpResponse.Success(serializer.data)

    @extend_schema(
        tags=["Banner"],
        operation_id="banner_delete",
        summary="Delete a banner",
        responses={
            200: inline_serializer(
                name="BannerDeleteResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "data": inline_serializer(
                        name="BannerDeleteMessage",
                        fields={"message": serializers.CharField()}
                    ),
                }
            )
        },
    )
    def delete(self, request, banner_id):
        banner = self._get_banner(banner_id)
        if banner is None:
            return HttpResponse.NotFound(f"Banner '{banner_id}' not found.")

        banner.delete()
        log.info("Banner deleted: id=%s", banner_id)
        return HttpResponse.Success({"message": f"Banner '{banner_id}' deleted successfully."})
