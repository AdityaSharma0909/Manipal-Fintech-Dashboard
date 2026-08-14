from typing import Any, Optional

class AxisIntegrationError(Exception):
    pass


class AxisConfigurationError(AxisIntegrationError):
    pass


class AxisRequestError(AxisIntegrationError):
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        decrypted_response: Optional[Any] = None,
        partner_message: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
        self.decrypted_response = decrypted_response
        self.partner_message = partner_message
