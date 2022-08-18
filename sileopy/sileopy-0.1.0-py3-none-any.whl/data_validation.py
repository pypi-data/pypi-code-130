# -*- coding: utf-8 -*-
"""
This method contains classes, methods and helper functions for data validation
"""
# Python module imports
from datetime import datetime
import logging
import re

# 3rd party module imports

# Local module imports
from sileopy.common_functions import tracelog


# Logger setup
logger = logging.getLogger(__name__)


@tracelog
def is_amount_above_zero(amount):
    """
    Verify that amount is not zero or below.

    Parameters
    ----------
    amount : Decimal
        Amount to check

    Returns
    -------
    True if `amount` is more than 0.0000
    False if `amount` is 0.0000 or less
    """
    if amount <= 0.0000:
        return False

    return True


@tracelog
def is_date_earlier_than_todays_date(date_to_check):
    """
    Verify that `date_to_check` is before todays date.

    Parameters
    ----------
    date_to_check : str
        Date formatted as string on the format YYYY-MM-DD

    Returns
    -------
    True if `date_to_check` is before todays date
    False if `date_to_check` is today or a future date
    """
    if datetime.now().date() < datetime.strptime(
            date_to_check, '%Y-%m-%d').date():
        return False

    return True


@tracelog
def is_not_empty(value):
    """
    Check if given `value` is not empty

    Parameters
    ----------
    value : any type convertable to str
        Value to check length of

    Returns
    -------
    True if `value` is not blank/empty
    False if `value` is blank/empty
    """
    if not str(value):
        return False

    return True


@tracelog
def is_valid_swedish_id_number(id_number):
    """
    Verify that given id number is on the format yymmdd-nnnc and that the
    checksum digit at the end is correct using the Luhn algoritm.

    Parameters
    ----------
    id_number : int or str
        Id number to validate

    Returns
    -------
    True if `id_number` is a valid Swedish ID number
    False if `id_number` is not a valid Swedish ID number
    """
    id_number = str(id_number)

    #if re.match(r'\d{6}[+-]\d{4}$', id_number) is None:
    if re.match(r'\d{12}$', id_number) is None:
        return False

    id_number = re.sub(r'\D', '', id_number)[2:]
    checksum = sum([int(x) for x in id_number[1::2]])

    for digit in id_number[::2]:
        digit = int(digit)*2
        checksum += digit - 9 if digit > 9 else digit

    if checksum % 10 != 0:
        return False

    return True
