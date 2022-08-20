import datetime  # type: ignore
from dateutil.relativedelta import relativedelta  # type: ignore
import math
import re

from .__formats import (
    _DATE_DELTAS,
    _DATE_SWITCHOVER,
    _DATE_SPLIT_CHARS,
    _SUPPORTED_DATE_FORMATS,
    _SUPPORTED_TIME_FORMATS,
    _TIME_SPLIT_CHARS,
)


def _date_to_datetime(date):
    return datetime.datetime.combine(
        date,
        datetime.time(hour=0, minute=0, second=0, microsecond=0),
        tzinfo=None,
    )


def _time_to_datetime(time):
    return datetime.datetime.combine(
        datetime.date.today(),
        time,
        tzinfo=None,
    )


def _int_to_datetime(i):
    # hack - check for 19 or 20 in first 2 digits
    str_i = str(i)
    if len(str_i) < 4:
        raise ValueError(f"cannot convert {i} to time, too short")
    if len(str_i) == 6 or len(str_i) == 8:
        if str_i[0:2] == "19" or str_i[0:2] == "20":
            try:
                return _date_to_datetime(_int_to_date(i))
            except ValueError as ve_date:
                try:
                    return _time_to_datetime(_int_to_time(i))
                except ValueError as ve_time:
                    raise ValueError(
                        "Error(s): could not convert to either date or time.\n"
                        "Conversion to date resulted in following error:\n"
                        f"\t{str(ve_date)}\n"
                        "Conversion to time resulted in following error:\n"
                        f"\t{str(ve_time)}"
                    )
    try:
        return _time_to_datetime(_int_to_time(i))
    except ValueError as ve_time:
        try:
            return _date_to_datetime(_int_to_date(i))
        except ValueError as ve_date:
            raise ValueError(
                "Error(s): could not convert to either time or date.\n"
                "Conversion to time resulted in following error:\n"
                f"\t{str(ve_time)}\n"
                "Conversion to date resulted in following error:\n"
                f"\t{str(ve_date)}"
            )


def _string_to_datetime(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        pass
    try:
        return _int_to_datetime(int(s))
    except ValueError:
        pass

    subs = re.sub(r"\s+", r" ", s)
    dts = subs.split(" ")
    if len(dts) > 2 or len(dts) <= 0:
        raise ValueError(
            "Invalid datetime string provided - date/time should be separated "
            "by single space, e.g. 2005/02/03 08:01:03"
        )
    elif len(dts) == 2:
        return datetime.datetime.combine(
            _string_to_date(dts[0]), _string_to_time(dts[1])
        )
    else:
        if len(dts[0]) < 4:
            raise ValueError(f"Invalid datetime provided {dts[0]}-- too short")

        if dts[0][0:2] == "19" or dts[0][0:2] == 20:
            try:
                return _date_to_datetime(_string_to_date(s))
            except ValueError as ve_date:
                try:
                    return _time_to_datetime(_string_to_time(s))
                except ValueError as ve_time:
                    raise ValueError(
                        "Error(s): could not convert to either date or time.\n"
                        "Conversion to date resulted in following error:\n"
                        f"\t{str(ve_date)}\n"
                        "Conversion to time resulted in following error:\n"
                        f"\t{str(ve_time)}"
                    )
        try:
            return _time_to_datetime(_string_to_time(s))
        except ValueError as ve_time:
            try:
                return _date_to_datetime(_string_to_date(s))
            except ValueError as ve_date:
                raise ValueError(
                    "Error(s): could not convert to either time or date.\n"
                    "Conversion to time resulted in following error:\n"
                    f"\t{str(ve_time)}\n"
                    "Conversion to date resulted in following error:\n"
                    f"\t{str(ve_date)}"
                )


def _try_yyyy_mm_dd(fields):
    if len(fields[0]) != 4:
        return None
    yyyy = int(fields[0])
    mm = int(fields[1])
    dd = int(fields[2])
    return datetime.date(year=yyyy, month=mm, day=dd)


def _try_end_yyyy(fields):
    if len(fields[2]) != 4:
        return None
    yyyy = int(fields[2])
    mm = int(fields[0])
    dd = int(fields[1])
    if mm > 12:
        # must be dd-mm, so swap mm and dd
        return datetime.date(year=yyyy, month=dd, day=mm)
    return datetime.date(year=yyyy, month=mm, day=dd)


def _try_end_yy(fields):
    if len(fields[2]) != 2:
        return None
    yy = int(fields[2])
    mm = int(fields[0])
    dd = int(fields[1])
    yyyy = yy + 2000
    if yy > _DATE_SWITCHOVER:
        yyyy = yy + 1900
    if mm > 12:
        # must be dd-mm, so swap mm and dd
        return datetime.date(year=yyyy, month=dd, day=mm)
    return datetime.date(year=yyyy, month=mm, day=dd)


def _convert_non_isostring_date(s):
    for sc in _DATE_SPLIT_CHARS:
        fields = s.split(sc)
        if len(fields) == 3:
            break
        if len(fields) == 2 or len(fields) > 3:
            raise ValueError(
                "invalid date format used ({s}), must be one of:\n"
                f"{', '.join(_SUPPORTED_DATE_FORMATS)}"
            )
    if len(fields) != 3:
        raise ValueError(
            f"invalid date format used, could not find split char in ({s}), "
            f"format must be one of:\n{', '.join(_SUPPORTED_DATE_FORMATS)}"
        )
    date = _try_yyyy_mm_dd(fields)
    if date is None:
        date = _try_end_yyyy(fields)
    if date is None:
        date = _try_end_yy(fields)
    return date


def _string_to_time(s):
    try:
        return _int_to_time(int(s))
    except Exception:
        pass
    times = s.split(".")
    if len(times) > 2:
        raise ValueError(
            f"Error: invalid microseconds provided (too many '.') in {s}"
        )
    if len(times) > 1:
        if len(str(times[1])) > 6:
            raise ValueError(
                f"Error: invalid microseconds {times[1]} "
                "provided (too long)"
            )
        us = int(math.pow(10, (6 - len(times[1]))) * int(times[1]))
    else:
        us = 0

    for sc in _TIME_SPLIT_CHARS:
        fields = times[0].split(sc)
        fields_len = len(fields)
        if fields_len > 1:
            break
    if fields_len < 2 or fields_len >= 4:  # more than h,m,s
        raise ValueError(
            "invalid time format used ({s}), must be one of:\n"
            f"{', '.join(_SUPPORTED_TIME_FORMATS)}"
        )
    hh = int(fields[0])
    mm = int(fields[1])
    if fields_len > 2:
        ss = int(fields[2])
    else:
        ss = 0
    _check_time(hh, mm, ss, us)
    return datetime.time(hh, mm, ss, us)


def _check_time(hh, mm, ss, zz=0):
    if hh > 23 or hh < 0:
        raise ValueError(f"invalid hour {hh} detected using HHMMSS format")
    if mm > 59 or mm < 0:
        raise ValueError(f"invalid minute {mm} detected using HHMMSS format")
    if ss > 59 or ss < 0:
        raise ValueError(f"invalid second {ss} detected HHMMSS format")

    if zz > 999999 or zz < 0:
        raise ValueError(
            f"invalid microsecond {zz} detected using HHMMSS.ZZZZZZ format"
        )


def _check_month(yyyy, mm):
    if yyyy > 3000 or yyyy < 1000:
        raise ValueError(f"invalid year {yyyy} detected")
    if mm > 12 or mm < 1:
        raise ValueError(f"invalid month {mm} detected")


def _is_leap(yyyy):
    return (yyyy % 100 == 0 and yyyy % 400 == 0) or (
        yyyy % 100 != 0 and yyyy % 4 == 0
    )


def _check_date(yyyy, mm, dd):
    _check_month(yyyy, mm)
    if dd < 1:
        raise ValueError(f"invalid day {dd} detected < 1")

    if mm == 2:
        if _is_leap(yyyy):
            if dd > 29:
                raise ValueError(
                    f"Invalid day {dd} detected, leap year {yyyy} but "
                    f"in february {mm} and day > 29"
                )
        elif dd > 28:
            raise ValueError(
                f"Invalid day {dd} detected, non-leap year {yyyy} but "
                f"in february {mm} and day > 28"
            )
    elif mm in [4, 6, 9, 11]:
        if dd > 30:
            raise ValueError(
                f"Invalid day {dd} detected, in Apr, Jun, Sep, Nov {mm} "
                f"but day > 30"
            )
    elif dd > 31:
        raise ValueError(f"Invalid day {dd} detected, day > 31")


def _string_to_date(s):
    # no other 8 char meaning that can be converted as integer
    if len(s) <= 8:
        try:
            return _int_to_date(int(s))
        except ValueError:
            pass
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        if any([sc in s for sc in _TIME_SPLIT_CHARS]):
            # support date times, not just dates
            pass
        # this can be one of many types of date, but cannot be a datetime
        # e.g. ISO (YYYY-MM-DD), non-ISO: (YYYY/MM/DD, MM/DD/YYYY)
        # The above are the three formats we support
        date = _convert_non_isostring_date(s)
        if date is None:
            raise ValueError(f"could not convert {s} to date")
        return date


def _int_to_month(i):
    _min_allowed = 100001
    if i < _min_allowed:
        raise ValueError(
            f"integer month {i} smaller than min allowed {_min_allowed})"
        )
    yyyy = i // 100
    mm = i - yyyy * 100
    _check_month(yyyy, mm)
    return datetime.date(yyyy, mm, 1)


def _int_to_date(i):
    if len(str(i)) == 6 and i % 100 <= 12:
        return _int_to_month(i)
    _min_allowed = 10000000
    if i < _min_allowed:
        raise ValueError(
            f"integer date {i} smaller than min allowed ({_min_allowed})"
        )
    # convert YYYY to <YYYY>MMDD multiply by 1000,
    # then add biggest MMDD possible
    _max_allowed = datetime.MAXYEAR * 10000 + 1231
    if i > _max_allowed:
        raise ValueError(
            f"integer date {i} greater than max allowed (){_max_allowed})"
        )
    yyyy = i // 10000
    mm = (i - yyyy * 10000) // 100
    dd = i - yyyy * 10000 - mm * 100
    _check_date(yyyy, mm, dd)
    return datetime.date(year=yyyy, month=mm, day=dd)


def _int_to_time(i):
    _max_allowed = 235959
    if i < 0 or i > _max_allowed:
        raise ValueError(f"integer time {i} violates min/max of 24H time")
    if i >= 10000:
        hh = i // 10000
        mm = (i - hh * 10000) // 100
        ss = i - (hh * 10000 + mm * 100)
    elif i >= 100:
        hh = i // 100
        mm = max(0, i - hh * 100)
        ss = 0
    else:
        hh = i
        mm = 0
        ss = 0
    _check_time(hh, mm, ss)
    return datetime.time(hh, mm, ss)


def _inc_dt(dt, deltakw, dir, holidays, weekends):
    new = dt
    origdeltakw = deltakw
    origdir = dir
    iters = 0
    should_iterate = True
    while should_iterate:
        if iters > 35:
            raise ValueError(
                "cannot find valid date for iteration with parameters: "
                "(date, deltakw, direction, holidays, weekends?) == "
                f"({dt}, {deltakw}, {dir}, {holidays}, {weekends})"
            )
        iters += 1
        new = new + relativedelta(**{deltakw: dir})
        # after first iteration, we revert to days
        # e.g. jump a week, but then iterate by days to find a non-holiday
        deltakw = "days"

        # if we're iterating by months, then we need to make sure we iterate
        # backwards to find a non-holiday/non-weekend
        if origdeltakw == "months":
            if (
                abs(origdir * (new.month - dt.month) % 12) > 1
                or new.month - dt.month == 0
            ):
                dir = dir * -1
                continue
        # if we're iterating by years we should end up in the same month
        elif origdeltakw == "years" and new.month - dt.month != 0:
            dir = dir * -1
            continue
        if new.strftime("%Y-%m-%d") in holidays:
            continue
        if not weekends and new.isoweekday() in [6, 7]:
            continue
        should_iterate = False
    return new


class _DateTime:
    def __init__(self, arg=None):
        self.dt = None
        if arg is None:
            self.dt = datetime.datetime.now()
        elif isinstance(arg, str):
            self.dt = _string_to_datetime(arg)
        elif isinstance(arg, int):
            self.dt = _int_to_datetime(arg)
        elif isinstance(arg, datetime.datetime):
            self.dt = arg
        elif isinstance(arg, datetime.date):
            self.dt = _date_to_datetime(arg)
        elif isinstance(arg, datetime.time):
            self.dt = _time_to_datetime(arg)
        # aggressive, but useful especially for Pandas interop without
        # having to import Pandas
        elif callable(getattr(arg, "to_datetime", None)):
            self.dt = arg.to_datetime()
        else:
            raise ValueError(
                f"invalid datetime {arg} provided, could not process"
            )

    def translate(self, inc, num, holidays=None):
        if num == 0:
            return self.dt
        if holidays is None:
            holidays = {}
        weekends = True
        if inc == "business_days":
            inc = "days"
            weekends = False
        elif inc == "business_weeks":
            inc = "weeks"
            weekends = False
        elif inc == "business_months":
            inc = "months"
            weekends = False
        elif inc == "business_years":
            inc = "years"
            weekends = False
        dt = self.dt
        if inc in _DATE_DELTAS:
            for i in range(0, abs(num) - 1):
                # for large period jumps, we don't take holidays/weekends
                # into account until the final jump into the destination
                # month/year
                if inc in ["weeks", "months", "years"]:
                    dt = _inc_dt(dt, inc, math.copysign(1, num), {}, True)
                else:
                    dt = _inc_dt(
                        dt, inc, math.copysign(1, num), holidays, weekends
                    )
            dt = _inc_dt(dt, inc, math.copysign(1, num), holidays, weekends)
        else:
            dt = dt + relativedelta(**{inc: num})
        return dt
