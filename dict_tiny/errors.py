class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class LLMParamError(CustomException):
    """param error"""
