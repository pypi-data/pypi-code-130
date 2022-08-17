import logging
import sys
from typing import Text, Union


def get_console_handler() -> logging.StreamHandler:
    """Get console handler.

    Returns: `logging.StreamHandler`, StreamHandler which logs into stdout
    """

    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    console_handler.setFormatter(formatter)

    return console_handler


def get_logger(
    name: Text = __name__, log_level: Union[Text, int] = logging.ERROR
) -> logging.Logger:
    """Get logger.

    name: `Text`, logger name
    log_level: `Text` or `int`, logging level; can be string name or integer value
    Returns: `logging.Logger`, logger instance
    """

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent duplicate outputs in Jypyter Notebook
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(get_console_handler())
    logger.propagate = False

    return logger
