class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class LLMParamError(CustomException):
    """llm param error"""


class TextInputError(CustomException):
    """text input error"""


class InitDialogError(CustomException):
    """init dialog error"""
