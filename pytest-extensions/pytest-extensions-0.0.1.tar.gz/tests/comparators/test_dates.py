from datetime import datetime, date, timedelta, time, tzinfo, timezone

from pytest_extensions.comparators.dates import a_datetime, a_date, a_timedelta, a_tzinfo, a_timezone, a_time


def test_a_date():
    assert date(2022, 1, 1) == a_date

    # /!\ datetime is a date
    assert datetime(2022, 1, 1) == a_date

    assert "2022-01-01" != a_date


def test_a_time():
    assert time() == a_time


def test_a_datetime():
    assert datetime(2022, 1, 1) == a_datetime

    assert date(2022, 1, 1) != a_datetime


def test_a_timedelta():
    assert timedelta(days=1) == a_timedelta

    assert date(2022, 1, 1) != a_timedelta


def test_a_tzinfo():
    assert timezone.utc == a_tzinfo

    assert date(2022, 1, 1) != a_tzinfo
    assert None != a_tzinfo


def test_a_timezone():
    assert timezone.utc == a_timezone

    assert date(2022, 1, 1) != a_timezone
    assert None != a_timezone
