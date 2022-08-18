# -*- coding: utf-8 -*-
"""
This module contains functions with functionality common for several modules
and helper methods for other modules
"""
# Python module imports
import os
import logging
import sys
from datetime import datetime
import functools

# 3rd party module imports

# Local module imports


# Logger setup
logger = logging.getLogger(__name__)

# Define DEV logging level
logging.DEV = logging.DEBUG - 1

# Define verbose logging level
logging.VERBOSE = logging.DEBUG - 2


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """
    Print stack trace to log-file for unhandled exeptions
    """
    # Do not log program interrupts from keyboard
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Print trace to log file
    logger.critical("Unhandled exception", exc_info=(
        exc_type, exc_value, exc_traceback
        ))


def isdate(value):
    """
    Check if `value` is a date on format YYYY-MM-DD.

    Parameters
    ----------
    value : str
        Value to check

    Returns
    -------
    bool
        True if value is a date, otherwise False
    """
    try:
        value = datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def tracelog(func):
    """
    Decorator function for printing tracelogs. Prints timestamp when entering
    function, arguments to function, timestamp when exiting function and return
    value. Also prints docstring line with header "Tracelog".
    Usage: add @tracelog before funktion to decorate. Add "Tracelog: <comment>"
    to function docstring print <comment> from docstring.
    """
    @functools.wraps(func)
    def tracelog_wrapper(*args, **kwargs):

        logger.debug(
            "TRACELOG: %s entered %s() in module %s",
            datetime.now(),
            func.__name__,
            func.__module__,
        )

        logger.verbose(
            "TRACELOG: with parameters %s, %s",
            args,
            kwargs
        )

        if func.__doc__:
            if "Tracelog" in func.__doc__:
                doc_list = [s.strip() for s in func.__doc__.splitlines()]
                logger.debug(
                    "TRACELOG: %s function %s docstring comments: %s",
                    datetime.now(),
                    func.__name__,
                    doc_list[doc_list.index('Tracelog') + 2]
                )

        function_result = func(*args, **kwargs)

        logger.debug(
            "TRACELOG: %s exited %s() in module %s",
            datetime.now(),
            func.__name__,
            func.__module__,
        )

        logger.verbose(
            "TRACELOG: returning %s",
            function_result
        )

        return function_result

    return tracelog_wrapper


def log_level_dev(self, msg, *args, **kwargs):
    """
    Custom log level for development. This log level should only be used locally
    and never be pushed.
    """
    if self.isEnabledFor(logging.DEV):
        self._log(logging.DEV, msg, args, **kwargs)


def log_level_verbose(self, msg, *args, **kwargs):
    """
    Custom log level for verbose messages.
    """
    if self.isEnabledFor(logging.VERBOSE):
        self._log(logging.VERBOSE, msg, args, **kwargs)


def format_verbose_log_header(debug_object, debug_string):
    """
    Construct log-print header

    Parameters
    ----------
    debug_object : object
        The object to print
    debug_string : string
        String with information about the debug print

    Returns
    -------
    -
    """
    debug_header = (
        "\n" +"-" *50 + debug_string +"-" *100 +"\n{0}\n".format(debug_object)
    )

    return debug_header


@tracelog
def get_age_from_id_number(id_number):
    """
    Calculate age from Swedish personnummer/samordningsnummer. The id number
    format supported is yyyymmddnnnc

    Parameters
    ----------
    id_number : str or int
        Id number to use for age calculation. Will be converted to string.
        Supported format is yyyymmddnnnc

    Returns
    -------
    Age calculated from id number.
    """
    id_number = str(id_number)

    year = int(id_number[0:4])
    month = int(id_number[4:6])
    day = int(id_number[6:8])

    # Company
    if month > 12:
        return 0

    # Samordningsnummer has dd+60
    if day > 60:
        day = day - 60

    try:
        date_of_birth = datetime.strptime(
            str(year) + ' '
            + str(month) + ' '
            + str(day), "%Y %m %d"
        ).date()

        age = (
            datetime.now().year - date_of_birth.year
            - ((datetime.now().month, datetime.now().day)
            < (date_of_birth.month, date_of_birth.day))
        )
    except (ValueError) as value_error:
        logger.error("ValueError in calculating age from idnumber: %s", value_error)
        return 0

    return age
