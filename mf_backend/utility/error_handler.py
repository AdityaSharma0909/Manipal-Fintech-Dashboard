import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from django.core.exceptions import ObjectDoesNotExist

try:
    import sentry_sdk
except ImportError:  # pragma: no cover - exercised only before dependency install
    sentry_sdk = None


logger = logging.getLogger("api.error")


def _set_sentry_context(name, value):
    if sentry_sdk is not None:
        sentry_sdk.set_context(name, value)


def _capture_exception(exc):
    if sentry_sdk is not None:
        sentry_sdk.capture_exception(exc)


def exception_handler(exc, context):
    """Return 404 for ObjectDoesNotExist (e.g. Application.DoesNotExist) instead of 500."""
    if isinstance(exc, ObjectDoesNotExist):
        logger.warning("Object not found", exc_info=exc)
        return Response(
            {
                'status': 'error',
                'data': None,
                'error_msg': 'Resource not found.',
                'error_code': 'HTTP_404_NOT_FOUND',
                'status_code': 404,
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    response = drf_exception_handler(exc, context)

    if response is None:
        return response

    request = context.get("request")
    view = context.get("view")
    _set_sentry_context(
        "drf_exception",
        {
            "view": view.__class__.__name__ if view else None,
            "status_code": response.status_code,
            "path": getattr(request, "path", None),
            "method": getattr(request, "method", None),
        },
    )

    if response.status_code >= 500 or (isinstance(exc, APIException) and exc.status_code >= 500):
        logger.exception("Handled DRF exception", exc_info=exc)
        _capture_exception(exc)
    elif response.status_code >= 400:
        logger.warning("Handled DRF client error", exc_info=exc)

    return response


class ErrorSchema():
    def __init__(self, name, desc, status_code):
        self.description = desc
        self.name = name
        self.status_code = status_code

    def getErrorResponse(self):
        return Response({
            'status_code': self.status_code,
            'name': self.name,
            'response': self.description,
        }, status=self.status_code)


class HttpErrors():
    def Unauthorized(desc):
        err = ErrorSchema('HTTP_401_UNAUTHORIZED', desc,
                          status.HTTP_401_UNAUTHORIZED)
        return err.getErrorResponse()

    def BadRequest(desc):
        err = ErrorSchema('HTTP_400_BAD_REQUEST', desc,
                          status.HTTP_400_BAD_REQUEST)
        return err.getErrorResponse()

    def InternalServerError(desc):
        err = ErrorSchema('HTTP_500_INTERNAL_SERVER_ERROR',
                          desc, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return err.getErrorResponse()
