import uuid
import time
import json
import logging
import traceback
import threading
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
_thread_locals = threading.local()


def get_correlation_id() -> str:
    """Retrieves the current request's correlation ID from thread local storage."""
    return getattr(_thread_locals, 'correlation_id', '-')


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects correlation_id into log records."""
    
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        return True


class JSONFormatter(logging.Formatter):
    """Custom logging formatter outputting JSON blocks for structured logging."""
    
    def format(self, record):
        log_data = {
            "Timestamp": self.formatTime(record, self.datefmt),
            "Level": record.levelname,
            "Message": record.getMessage(),
            "Logger": record.name,
            "CorrelationId": getattr(record, 'correlation_id', '-'),
        }
        
        # Include exception details if present
        if record.exc_info:
            log_data["Exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


# class CorrelationIdMiddleware(MiddlewareMixin):
#     """Middleware extracting or generating X-Correlation-ID for logging context."""
    
#     def process_request(self, request):
#         corr_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
#         _thread_locals.correlation_id = corr_id
#         request.correlation_id = corr_id

#     def process_response(self, request, response):
#         corr_id = getattr(request, 'correlation_id', None)
#         if corr_id:
#             response['X-Correlation-ID'] = corr_id
        
#         # Clear local context
#         if hasattr(_thread_locals, 'correlation_id'):
#             delattr(_thread_locals, 'correlation_id')
            
#         return response


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging incoming web requests and outgoing responses.

    Audit logs all incoming web request paths, headers, payloads, and responses.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Try capturing body
        body = ""
        if request.body:
            try:
                body = request.body.decode('utf-8')
            except Exception:
                body = "<binary-body>"
                
        # Exclude documentation endpoints from logging clutter
        if not request.path.startswith('/api/docs/') and not request.path.startswith('/api/schema/'):
            logger.info(
                f"HTTP Request Started: {request.method} {request.path} | Query: {request.GET.urlencode()} | Body: {body}"
            )

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0.0

        if not request.path.startswith('/api/docs/') and not request.path.startswith('/api/schema/'):
            # Try capturing response content
            content = ""
            if response.headers.get('Content-Type') == 'application/json':
                try:
                    content = response.content.decode('utf-8')
                except Exception:
                    content = "<binary-content>"
            else:
                content = "<non-json-content>"
                
            logger.info(
                f"HTTP Response Finished: status={response.status_code} | duration={duration:.4f}s | Response Body: {content}"
            )
            
        return response


class ErrorHandlingMiddleware:
    """

    Catches all unhandled exceptions during request processing and returns
    a uniform JSON error response so that no HTML 500 page leaks to API consumers.
    Must be registered first in MIDDLEWARE so it wraps all other layers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            return self._handle_exception(exc)

    def _handle_exception(self, exc: Exception) -> JsonResponse:
        """Formats any unhandled exception as a JSON 500 response."""
        tb_str = traceback.format_exc()
        logger.error(
            f"Unhandled exception caught by ErrorHandlingMiddleware: {str(exc)}\n{tb_str}"
        )

        payload = {
            "StatusCode": 500,
            "StatusMessage": "An internal server error occurred. Please contact the administrator.",
            "Data": None
        }
        return JsonResponse(payload, status=500)
