import logging
import logging.handlers as handlers
import sys

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from .configuration import ghost_writer_config

from .package_data import (
    get_path_of_data_file,
    get_path_of_log_dir,
    get_path_of_log_file,
)

_log_file_names = ["usr.log", "dev.log"]


class LogFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno != self.__level


# now create the developer handler that rotates every day and keeps
# 10 days worth of backup
ghost_writer_dev_log_handler = handlers.TimedRotatingFileHandler(
    get_path_of_log_file("dev.log"), when="D", interval=1, backupCount=10
)

# lots of info written out

_dev_formatter = logging.Formatter(
    "%(asctime)s | %(name)s | %(levelname)s| %(funcName)s | %(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

ghost_writer_dev_log_handler.setFormatter(_dev_formatter)
ghost_writer_dev_log_handler.setLevel(logging.DEBUG)
# now set up the usr log which will save the info

ghost_writer_usr_log_handler = handlers.TimedRotatingFileHandler(
    get_path_of_log_file("usr.log"), when="D", interval=1, backupCount=10
)

ghost_writer_usr_log_handler.setLevel(logging.INFO)

# lots of info written out
_usr_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

ghost_writer_usr_log_handler.setFormatter(_usr_formatter)

mytheme = Theme().read(get_path_of_data_file("log_theme.ini"))
console = Console(theme=mytheme)

_console_formatter = logging.Formatter(
    ' %(message)s',
    datefmt="%H:%M:%S",
)


ghost_writer_console_log_handler = RichHandler(
    level=ghost_writer_config.logging.level,
    rich_tracebacks=True,
    markup=True,
    console=console,
)
ghost_writer_console_log_handler.setFormatter(_console_formatter)


warning_filter = LogFilter(logging.WARNING)


def silence_warnings():
    """
    supress warning messages in console and file usr logs
    """

    ghost_writer_usr_log_handler.addFilter(warning_filter)
    ghost_writer_console_log_handler.addFilter(warning_filter)


def activate_warnings():
    """
    supress warning messages in console and file usr logs
    """

    ghost_writer_usr_log_handler.removeFilter(warning_filter)
    ghost_writer_console_log_handler.removeFilter(warning_filter)


def update_logging_level(level):

    ghost_writer_console_log_handler.setLevel(level)


def setup_logger(name):

    # A logger with name name will be created
    # and then add it to the print stream
    log = logging.getLogger(name)

    # this must be set to allow debug messages through
    log.setLevel(logging.DEBUG)

    # add the handlers

    log.addHandler(ghost_writer_dev_log_handler)

    log.addHandler(ghost_writer_console_log_handler)

    log.addHandler(ghost_writer_usr_log_handler)

    # we do not want to duplicate teh messages in the parents
    log.propagate = False

    return log
