import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class BajajFinServoApiException(Exception):
    """Custom exception matching C# BajajFinServoApiException."""
    def __init__(self, message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, response_body=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class TokenApiException(Exception):
    """Custom exception matching C# TokenApiException."""
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, response_body=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)
    
    # Custom formatting for our specific exceptions
    if isinstance(exc, (BajajFinServoApiException, TokenApiException)):
        status_code = exc.status_code
        message = exc.message
        
        data = {
            "StatusCode": status_code,
            "StatusMessage": message,
            "Data": message
        }
        
        logger.error(f"Custom API Exception: {message} | StatusCode: {status_code}")
        return Response(data, status=status_code)
    
    # Format fallback for other unexpected exceptions
    if response is None:
        message = "Unhandled exception occurred. Please contact the administrator."
        data = {
            "StatusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "StatusMessage": message,
            "Data": str(exc)
        }
        logger.exception("Unhandled exception caught in DRF views")
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Format DRF validation/permission exceptions to match the same payload layout
    if response is not None:
        # Standardize the payload format
        error_msg = str(response.data)
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_msg = response.data['detail']
        elif isinstance(response.data, list):
            error_msg = response.data[0]
        elif isinstance(response.data, dict):
            # Just extract first error item message if serializer failed validation
            first_key = next(iter(response.data))
            error_msg = f"{first_key}: {response.data[first_key]}"
            if isinstance(response.data[first_key], list):
                error_msg = response.data[first_key][0]
                
        response.data = {
            "StatusCode": response.status_code,
            "StatusMessage": error_msg,
            "Data": "Request failed"
        }
        
    return response
