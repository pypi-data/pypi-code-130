import datetime
import timeit
import glog as log
import os
from pytz import timezone
import dateutil.parser


def time_start():
    return timeit.default_timer()


def timer(time_start, length=1):
    """Returns time elapsed time in minutes and time per unit.

    Args:
        time_start (timeit.default_timer()): Start time in timeit.default_timer()
        length (int): [description]
    """
    time_end = timeit.default_timer()
    elapsed_minutes = round((time_end - time_start) / 60, 2)
    elapsed_rate_seconds = round((time_end - time_start) / length, 2)
    log.info(f'--- Total Running Time: {elapsed_minutes} minutes, on average {elapsed_rate_seconds} seconds per unit.')
    return (elapsed_minutes, elapsed_rate_seconds)


def convert_timezone(intime, timezone_origin, timezone_new):
    """Convert time to specified timezone

    Args:
        intime ([type]): [description]
        timezone_origin ([type]): [description]
        timezone_new ([type]): [description]

    Returns:
        [type]: [description]
    """
    dt = dateutil.parser.parse(intime)
    ct = timezone(timezone_origin).localize(dt)
    new_time = ct.astimezone(timezone(timezone_new))
    outtime = new_time.isoformat()
    # str(new_time.strftime("%m/%d/%Y %H:%M:%S"))
    return outtime
