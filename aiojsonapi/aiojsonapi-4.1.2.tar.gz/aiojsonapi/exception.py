"""Module for API exceptions."""


class ApiException(BaseException):
    """Base API exception."""

    def __init__(self, message, status=400):
        super().__init__(message)
        if isinstance(message, dict):
            self.message = message
            self.message["code"] = self.__class__.__name__
        else:
            self.message = {"code": self.__class__.__name__, "text": message}
        self.status = status


class WrongDataType(ApiException):  # pylint: disable=missing-class-docstring
    text = "Wrong data type."

    def __init__(self, path):
        super().__init__(
            {
                "text": self.text,
                "path": path,
            }
        )


class DataMissing(ApiException):  # pylint: disable=missing-class-docstring
    text = "Required data is missing."

    def __init__(self, path):
        super().__init__(
            {
                "text": self.text,
                "path": path,
            }
        )


class UnknownFields(ApiException): # pylint: disable=missing-class-docstring
    text = "Unknown fields."

    def __init__(self, fields):
        super().__init__(
            {
                "text": self.text,
                "path": fields,
            }
        )
