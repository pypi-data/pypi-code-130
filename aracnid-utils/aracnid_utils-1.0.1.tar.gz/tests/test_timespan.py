"""Test functions for datetime_utils.py.
"""
from datetime import datetime, timedelta

from dateutil import tz

from aracnid_utils.datetime_utils import timespan, EST

# initialize module variables
REF_BEGIN_STR = '2020-06-01T00:00:00-04:00'
REF_THRU_STR = '2020-06-08T00:00:00-04:00'
REF_BEGIN_ISO = '2020-W10'
REF_THRU_ISO = '2020-W25'
REF_WEEK_STR = '2020-W23'
REF_BEGIN_DATE_ONLY_STR = '2020-06-07'
REF_BEGIN_DATETIME_STR = '2020-06-07T00:00:00-04:00'
REF_THRU_DATE_ONLY_STR = '2020-06-07'
REF_THRU_DATETIME_STR = '2020-06-08T00:00:00-04:00'


def test_timespan_args_begin_str_and_thru_str():
    """Tests timespan arguments: begin_str, thru_str.
    """
    start, end = timespan(begin_str=REF_BEGIN_STR, thru_str=REF_THRU_STR)

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_begin_str_and_thru_str_none():
    """Tests timespan arguments: begin_str, thru_str=None.
    """
    start, end = timespan(begin_str=REF_BEGIN_STR, thru_str=None)
    end_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == end_now.isoformat()[0:18]

def test_timespan_args_begin_str_and_thru_str_missing():
    """Tests timespan arguments: begin_str, thru_str missing.
    """
    start, end = timespan(begin_str=REF_BEGIN_STR)
    end_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == end_now.isoformat()[0:18]

def test_timespan_args_begin_str_none_and_thru_str():
    """Tests timespan arguments: begin_str=None, thru_str.
    """
    start, end = timespan(begin_str=None, thru_str=REF_THRU_STR)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))

    assert isinstance(start, datetime)
    assert start.isoformat() == start_first.isoformat()

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_begin_str_missing_and_thru_str():
    """Tests timespan arguments, begin_str missing, thru_str.
    """
    start, end = timespan(thru_str=REF_THRU_STR)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))

    assert isinstance(start, datetime)
    assert start.isoformat() == start_first.isoformat()

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_begin_and_thru():
    """Tests timespan arguments: begin, thru.
    """
    begin = datetime.fromisoformat(REF_BEGIN_STR)
    thru = datetime.fromisoformat(REF_THRU_STR)
    start, end = timespan(begin=begin, thru=thru)

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_begin_and_thru_none():
    """Tests timespan arguments: begin, thru=None.
    """
    begin = datetime.fromisoformat(REF_BEGIN_STR)
    start, end = timespan(begin=begin, thru=None)
    thru_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == thru_now.isoformat()[0:18]

def test_timespan_args_begin_and_thru_missing():
    """Tests timespan arguments: begin, thru missing.
    """
    begin = datetime.fromisoformat(REF_BEGIN_STR)
    start, end = timespan(begin=begin)
    thru_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == thru_now.isoformat()[0:18]

def test_timespan_args_begin_none_and_thru():
    """Tests timespan arguments: begin=None, thru.
    """
    thru = datetime.fromisoformat(REF_THRU_STR)
    start, end = timespan(begin=None, thru=thru)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))

    assert isinstance(start, datetime)
    assert start == start_first

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_begin_missing_and_thru():
    """Tests timespan arguments: begin missing, thru.
    """
    thru = datetime.fromisoformat(REF_THRU_STR)
    start, end = timespan(thru=thru)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))

    assert isinstance(start, datetime)
    assert start == start_first

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_begin_iso_week_and_thru_iso_week():
    """Tests timespan arguments: begin iso week, thru iso week.
    """
    start, end = timespan(begin_str=REF_BEGIN_ISO, thru_str=REF_THRU_ISO)
    begin = EST.localize(datetime.fromisocalendar(2020, 10, 1))
    thru = EST.localize(datetime.fromisocalendar(2020, 25, 1)) + timedelta(days=7)

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_begin_iso_week_and_thru_str_none():
    """Tests timespan arguments: begin iso week, thru_str=None.
    """
    start, end = timespan(begin_str=REF_BEGIN_ISO, thru_str=None)
    begin = EST.localize(datetime.fromisocalendar(2020, 10, 1))
    end_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == end_now.isoformat()[0:18]

def test_timespan_args_begin_iso_week_and_thru_str_missing():
    """Tests timespan arguments: begin iso week, thru_str missing.
    """
    start, end = timespan(begin_str=REF_BEGIN_ISO)
    begin = EST.localize(datetime.fromisocalendar(2020, 10, 1))
    end_now = datetime.now(tz.tzlocal())

    assert isinstance(start, datetime)
    assert start == begin

    assert isinstance(end, datetime)
    assert end.isoformat()[0:18] == end_now.isoformat()[0:18]

def test_timespan_args_begin_str_none_and_thru_iso_week():
    """Tests timespan arguments: begin_str=None, thru iso week.
    """
    start, end = timespan(begin_str=None, thru_str=REF_THRU_ISO)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))
    thru = EST.localize(datetime.fromisocalendar(2020, 25, 1)) + timedelta(days=7)

    assert isinstance(start, datetime)
    assert start.isoformat() == start_first.isoformat()

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_begin_str_missing_and_thru_iso_week():
    """Tests timespan arguments: begin_str missing, thru iso week.
    """
    start, end = timespan(thru_str=REF_THRU_ISO)
    start_first = EST.localize(datetime(2000, 1, 1, 0, 0))
    thru = EST.localize(datetime.fromisocalendar(2020, 25, 1)) + timedelta(days=7)

    assert isinstance(start, datetime)
    assert start.isoformat() == start_first.isoformat()

    assert isinstance(end, datetime)
    assert end == thru

def test_timespan_args_week_str():
    """Tests timespan argument: week_str.
    """
    start, end = timespan(week_str=REF_WEEK_STR)

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_week_str_and_begin_str():
    """Tests timespan arguments: week_str, begin_str.
    """
    start, end = timespan(week_str=REF_THRU_ISO, begin_str=REF_BEGIN_STR)
    thru = EST.localize(datetime.fromisocalendar(2020, 25, 1)) + timedelta(days=7)

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat() == thru.isoformat()

def test_timespan_args_week_str_and_thru_str():
    """Tests timespan arguments: week_str, thru_str.
    """
    start, end = timespan(week_str=REF_BEGIN_ISO, thru_str=REF_THRU_STR)
    begin = EST.localize(datetime.fromisocalendar(2020, 10, 1))

    assert isinstance(start, datetime)
    assert start.isoformat() == begin.isoformat()

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_week_str_and_begin_str_and_thru_str():
    """Tests timespan arguments: week_str, begin_str, thru_str.

    The week string is ignored in this case.
    """
    start, end = timespan(week_str=REF_WEEK_STR, begin_str=REF_BEGIN_STR, thru_str=REF_THRU_STR)

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_STR

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_STR

def test_timespan_args_begin_date_only_str_and_thru_str():
    """Tests timespan arguments: begin_str date only, thru_str.
    """
    start, _ = timespan(begin_str=REF_BEGIN_DATE_ONLY_STR)

    assert isinstance(start, datetime)
    assert start.isoformat() == REF_BEGIN_DATETIME_STR

def test_timespan_args_begin_str_and_thru_date_only_str():
    """Tests timespan arguments: begin_str date only, thru_str.
    """
    _, end = timespan(
        begin_str=REF_BEGIN_STR,
        thru_str=REF_THRU_DATE_ONLY_STR)

    assert isinstance(end, datetime)
    assert end.isoformat() == REF_THRU_DATETIME_STR
