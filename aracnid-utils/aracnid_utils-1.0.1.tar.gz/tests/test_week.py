"""Test functions for datetime_utils.py.
"""
from datetime import datetime

from aracnid_utils.datetime_utils import isoweek, fromisoweek

# initialize module variables
REF_ISO_WEEK = '2020-W25'
REF_WEEK_DATE1 = '2020-06-15T00:00:00-04:00'
REF_WEEK_DATE2 = '2020-06-21T23:59:59-04:00'
REF_WEEK_DATE3 = '2020-06-22T00:00:00-04:00'

def test_get_isoweek_from_date_start():
    """Tests isoweek() given the earliest possible date in the week.
    """
    week_date = datetime.fromisoformat(REF_WEEK_DATE1)
    week_str = isoweek(week_date)
    assert week_str == REF_ISO_WEEK

def test_get_isoweek_from_date_end():
    """Tests isoweek() given the latest possible date in the week.
    """
    week_date = datetime.fromisoformat(REF_WEEK_DATE2)
    week_str = isoweek(week_date)
    assert week_str == REF_ISO_WEEK

def test_get_isoweek_from_date_next_week():
    """Tests isoweek() given a date in the following week.
    """
    week_date = datetime.fromisoformat(REF_WEEK_DATE3)
    week_str = isoweek(week_date)
    assert week_str != REF_ISO_WEEK

def test_get_date_from_isoweek():
    """Tests fromisoweek() given a standard ISO Week date string.
    """
    week_date = fromisoweek(REF_ISO_WEEK)
    assert week_date.isoformat() == REF_WEEK_DATE1
