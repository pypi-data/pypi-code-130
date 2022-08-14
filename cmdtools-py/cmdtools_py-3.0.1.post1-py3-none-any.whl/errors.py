__all__ = [
    "NotEnoughArgumentError",
    "NotFoundError",
    "ConversionError",
]


class CmdBaseException(Exception):
    def __init__(self, message: str, *args):
        self.message = message
        self.args = args
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotEnoughArgumentError(CmdBaseException):
    def __init__(self, message: str, option: str):
        self.message = message
        self.option = option
        super().__init__(message)


class NotFoundError(CmdBaseException):
    def __init__(self, message: str, name: str = None):
        self.message = message
        self.name = name
        super().__init__(name)


class ConversionError(CmdBaseException):
    """raises when failed to convert an object to a specific type"""

    def __init__(self, message: str, option: str):
        self.option = option
        super().__init__(message)
