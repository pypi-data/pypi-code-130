"""
Error handling module.
"""

import logging
from enum import Enum, auto
from typing import Optional


class OnError(Enum):
    """
    Enum that defines behaviors when errors occur.
    """

    RAISE = auto()
    LOG = auto()
    IGNORE = auto()


def handle_error(
    error: Exception,
    behavior: OnError,
    *,
    logger: Optional[logging.Logger] = None,
    message: str = None,
):
    """Error handling function.

    :param error: The exception instance :param behavior: The behavior
    to adopt. :param logger: An instance of logger. If not provided uses
    the default logger :param message: A custom message to log

    """
    match behavior:
        case OnError.RAISE:
            raise error
        case OnError.LOG:
            logger = logger or logging.getLogger()
            logger.error(
                f"Error {error}: {message}" if message else f"An error occurred {error}",
                stacklevel=2,
            )
