
class BajajIntegrationError(Exception):
    pass


class BajajConfigurationError(BajajIntegrationError):
    pass


class BajajRequestError(BajajIntegrationError):
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class BajajTokenError(BajajRequestError):
    pass

