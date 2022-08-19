""" Exceptions for Flair Client """

from typing import Any


class FlairError(Exception):
    """ Error from Flair Api """

    def __init__(self, *args: Any) -> None:
        """ Initialize the exception. """
        Exception.__init__(self, *args)

class FlairAuthError(Exception):
    """ Authentication Error """

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)