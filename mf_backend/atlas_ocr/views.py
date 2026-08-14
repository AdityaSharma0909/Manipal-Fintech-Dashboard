from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    GoldPledgeCardResultQuerySerializer,
    GoldPledgeCardUploadSerializer,
)
from .services import (
    AtlasAPIError,
    AtlasConfigurationError,
    AtlasGoldPledgeCardClient,
)


class AtlasAPIView(APIView):
    permission_classes = []

    @staticmethod
    def error_response(exc):
        if isinstance(exc, AtlasConfigurationError):
            return Response(
                {"status": "error", "message": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        payload = {"status": "error", "message": str(exc)}
        if exc.details:
            payload["provider_error"] = exc.details
        return Response(payload, status=exc.status_code)


class GoldPledgeCardUploadView(AtlasAPIView):
    @extend_schema(
        request=GoldPledgeCardUploadSerializer,
        summary="Submit multiple Gold Pledge Cards under one OCR batch",
    )
    def post(self, request):
        serializer = GoldPledgeCardUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AtlasGoldPledgeCardClient().submit(
                file_urls=serializer.validated_data["file_urls"],
            )
        except (AtlasConfigurationError, AtlasAPIError) as exc:
            return self.error_response(exc)

        return Response(
            {
                "status": "accepted",
                "message": "Gold Pledge Cards submitted for OCR.",
                "document_count": len(serializer.validated_data["file_urls"]),
                **result,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class GoldPledgeCardResultView(AtlasAPIView):
    @extend_schema(
        parameters=[GoldPledgeCardResultQuerySerializer],
        summary="Retrieve Gold Pledge Card OCR result",
    )
    def get(self, request):
        serializer = GoldPledgeCardResultQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            result = AtlasGoldPledgeCardClient().get_result(
                **serializer.validated_data
            )
        except (AtlasConfigurationError, AtlasAPIError) as exc:
            return self.error_response(exc)

        return Response({"status": "success", **result})
