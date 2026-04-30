class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class YoudaoParamError(CustomException):
    """ "youdao param error"""


class TextInputError(CustomException):
    """text input error"""
