import logging

from rest_framework.views import APIView

from utils.responseHandler import HttpResponse
from utility.error_handler import HttpErrors
from onboarding_v2.models import ApplicationV2
from onboarding_v2.helpers.presign_helpers import build_jewellery_presign
from onboarding_v2.serializers import PresignDocumentSerializer, PresignGetDocumentSerializer


logger = logging.getLogger("onboarding_v2.views")


class JewelleryPresignView(APIView):
    """
    Presign upload for jewellery images (front/back/weighing/appraiser_certificate).
    Client supplies the jewellery type, side, and optional index. If index is omitted, we auto-calculate.
    """

    def post(self, request, application_id):
        logger.info("Jewllery Presign Request | app=%s payload=%s", application_id, request.data)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        try:
            presign = build_jewellery_presign(application, request.data)
            logger.info("Jewllery Presign Response | app=%s response=%s", application_id, presign)
            return HttpResponse.Success({"upload": presign})
        except ValueError as ve:
            return HttpResponse.BadRequest(str(ve))
        except Exception as exc:
            logger.exception("Jewellery presign failed | app=%s", application_id)
            return HttpErrors.InternalServerError("Failed to generate presigned URL")


class PresignDocumentUploadView(APIView):
    """
    Generates a presigned PUT URL so mobile can upload documents directly to object storage.
    Client then calls the stage endpoint with file_url=object_url to persist metadata/status.
    """

    def post(self, request, application_id):
        logger.info("Presign Document Upload Request | app=%s payload=%s", application_id, request.data)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        serializer = PresignDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)

        data = serializer.validated_data
        from onboarding_v2 import views as views_module

        presign = views_module.build_document_presign(application, data)
        logger.info(
            "Presign upload generated | app=%s doc_type=%s presign=%s",
            application_id,
            data["document_type"],
            presign,
        )
        return HttpResponse.Success({"upload": presign})


class PresignDocumentDownloadView(APIView):
    """
    Generates a presigned GET URL for a stored document so mobile can download securely.
    """

    def post(self, request, application_id):
        logger.info("Presign Document Download Request | app=%s payload=%s", application_id, request.data)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        serializer = PresignGetDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)
        data = serializer.validated_data

        try:
            from onboarding_v2 import views as views_module

            presign = views_module.build_document_download_presign(application, data)
        except ValueError as ve:
            return HttpResponse.BadRequest(str(ve))
        logger.info("Presign Document Upload Response | app=%s payload=%s", application_id, presign)
        return HttpResponse.Success({"download": presign})
