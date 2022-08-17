import logging
import logging.config

__doc__ = """
Logger
======

Based on:
https://docs.python.org/3/howto/logging-cookbook.html#formatting-times-using-utc-gmt-via-configuration

https://realpython.com/lessons/logger-dictionary/

The Galaxy Project has the same base:
https://docs.galaxyproject.org/en/release_20.05/admin/config_logging.html

https://docs.python.org/3/library/logging.html#logrecord-attributes
"""

from .settings import LOGGING

logging.getLogger(__name__).addHandler(logging.NullHandler())


def config(log_name):
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(log_name)
    self_log = logging.getLogger(__name__)
    self_log.debug(f"Loading log config: {LOGGING}")
    return log


def getLevelName(log_level):
    """Wapper for logging.getLevelName
    for skipping to import logging"""
    return logging.getLevelName(log_level)
