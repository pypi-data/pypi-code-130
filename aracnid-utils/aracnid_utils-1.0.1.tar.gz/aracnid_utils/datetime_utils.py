"""Provides additional datetime functions.
"""
import re

from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse
from pytz import timezone

# initialize constants
EST = timezone('US/Eastern')
START_MIN = EST.localize(datetime(2000, 1, 1, 0, 0))


def isoweek(datetime_obj):
    """Calculates the ISO Week from the specified datetime object.

    Args:
        datetime_obj: Datetime object.

    Returns:
        The ISO Week.
    """
    year, week, _ = datetime_obj.isocalendar()
    return f'{year}-W{week:02}'

def fromisoweek(week_string):
    """Calculates the datetime from the specified ISO Week string.

    Args:
        week_string: The ISO week string.

    Returns:
        The datetime object.
    """
    pattern_isoweek = r'^\d{4}-W\d{2}$'

    if re.search(pattern_isoweek, week_string):
        year = int(week_string[:4])
        week = int(week_string[-2:])
        return EST.localize(datetime.fromisocalendar(year, week, 1))

    return None

def timespan(**kwargs):
    """Calculates the endpoints of a timespan.

    The timespan is specified by a set of keyword arguments. Separate arguments
    are used to provide datetime objects or strings representing datetimes.
    The strings can be any parsable notation that results in a datetime object.
    This includes ISO Week Notation, e.g., "2020-W13".

    If the begin time is not specified, the minimum start time is used.
    If the thru time is not specified, the current time is used.
    If a week string is specified, the start time and the thru time will default
    to the week. The week string can be used in conjunction with either begin
    time or thru time.

    Args:
        begin: Datetime object representing the start of the timespan.
        begin_str: String representing the start of the timespan.
        thru: Datetime object representing the end of the timespan.
        thru_str: String representing the end of the timespan.
        week_str: String representing a single week.

    Returns:
        The start and end datetime objects that define the timespan.
    """
    begin_dt = kwargs.get('begin')
    thru_dt = kwargs.get('thru')
    begin_str = kwargs.get('begin_str') or kwargs.get('week_str')
    thru_str = kwargs.get('thru_str') or kwargs.get('week_str')

    # initialize week notation pattern
    pattern_isoweek = r'^\d{4}-W\d{2}$'
    pattern_isodate_only = r'^\d{4}-\d{2}-\d{2}$'

    # convert string arguments
    if not begin_dt and begin_str:
        # check iso week notation
        if re.search(pattern_isoweek, begin_str):
            year_num = int(begin_str[:4])
            week_num = int(begin_str[-2:])
            begin_dt = EST.localize(
                datetime.fromisocalendar(year_num, week_num, 1)
            )

        else:
            dtx = parse(begin_str)
            if dtx.tzinfo is None or dtx.tzinfo.utcoffset(dtx) is None:
                begin_dt = EST.localize(dtx)
            else:
                begin_dt = dtx.astimezone(EST)

    if not thru_dt and thru_str:
        # check iso week notation
        if re.search(pattern_isoweek, thru_str):
            year_num = int(thru_str[:4])
            week_num = int(thru_str[-2:])
            thru_dt = EST.localize(
                datetime.fromisocalendar(year_num, week_num, 1)
            )
            thru_dt += timedelta(days=7)

        else:
            # parse the date string
            dtx = parse(thru_str)
            if dtx.tzinfo is None or dtx.tzinfo.utcoffset(dtx) is None:
                thru_dt = EST.localize(dtx)
            else:
                thru_dt = dtx.astimezone(EST)

            # adjust if time not specified
            if re.search(pattern_isodate_only, thru_str):
                thru_dt += timedelta(days=1)

    # check missing bounds
    if not begin_dt:
        begin_dt = START_MIN
    if not thru_dt:
        thru_dt = datetime.now(tz.tzlocal())

    return begin_dt, thru_dt


if __name__ == '__main__':
    pass
