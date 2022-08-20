from datetime import date, datetime, time, timedelta
import functools
import re

__all__ = [
    "_DATE_DELTAS",
    "_DATE_SPLIT_CHARS",
    "_DATE_STYLES",
    "_DATE_SWITCHOVER",
    "_SUPPORTED_DATE_FORMATS",
    "_TIME_SPLIT_CHARS",
    "_TIME_STYLES",
    "_SUPPORTED_TIME_FORMATS",
]

_DATE_SPLIT_CHARS = ["-", "/"]
_TIME_SPLIT_CHARS = [":"]

# preference goes in this order as well, though it is baked into the code so
# changing the order of the below list will not affect, i.e. always prefer
# american style MM-DD over DD-MM
_DATE_STYLES = [
    "YYYY{sc}MM{sc}DD",
    "MM{sc}DD{sc}YYYY",
    "DD{sc}MM{sc}YYYY",
    "MM{sc}DD{sc}YY",
    "MM{sc}DD{sc}YY",
]

_TIME_STYLES = ["HH{sc}MM{sc}SS[.ZZZ]", "HH{sc}MM"]

# two digit years are assumed to be 1900+YY for anything > 65, or
# 2000 + YY for anything <= 65.  Use YYYY for better accuracy ;)
_DATE_SWITCHOVER = 65

_SUPPORTED_DATE_FORMATS = [
    item.format(sc=split_char)
    for split_char in _DATE_SPLIT_CHARS
    for item in _DATE_STYLES
]
_SUPPORTED_TIME_FORMATS = [
    item.format(sc=split_char)
    for split_char in _TIME_SPLIT_CHARS
    for item in _TIME_STYLES
]

# e.g. YYYYMMDD-M1D = YYYYMMDD format, translate minus 1 day before output
_PARSE_DT_SUB_REGEX = r"(%(?P<format>[^-^{^}]+?)(?:-(?P<translation>\w+))?%)"
_PARSE_DT_REGEX = re.compile("^" + _PARSE_DT_SUB_REGEX + "$")

# e.g. M1D for minus 1 day, P10Y for plus 10 years, etc.
_PARSE_DT_TRANSLATION = r"^(?P<dir>[MmPp])(?P<num>\d+)(?P<size>[A-Za-z])$"

_dtformat = functools.partialmethod(datetime.strftime)
_dttranslate = functools.partialmethod(timedelta)


def _translate_int_str(f, dt):
    return str(int(f(dt)))


_DATE_DELTAS = ["days", "weeks", "months", "years"]

# case sensitive
_SUPPORTED_TRANSLATION_SIZES = {
    "Y": "years",
    "m": "months",
    "D": "days",
    "W": "weeks",
    "H": "hours",
    "M": "minutes",
    "S": "seconds",
    "Z": "microseconds",
    "B": "business_days",
    "F": "business_weeks",
    "P": "business_months",
    "K": "business_years",
}

# not case sensitive
_SUPPORTED_TRANSLATION_DIRECTIONS = {
    "M": -1,
    "P": 1,
}
_SUPPORTED_TRANSLATION_DIRECTIONS.update(
    {k.lower(): v for k, v in _SUPPORTED_TRANSLATION_DIRECTIONS.items()}
)

# not case sensitive
_SUPPORTED_DATETIME_OUTPUT_FORMATS = {
    "DATE": "%Y-%m-%d",  # YYYY-MM-DD
    "DATETIME": "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS (24-hour)
    "USDATE": "%x",  # MM/DD/YY
    "USDATETIME": "%x %X",  # MM/DD/YY HH:MM:SS (24-hour)
    "TIME": "%X",  # HH:MM:SS (24-hour)
    "YEAR": "%Y",  # YYYY
    "YMD": "%Y%m%d",  # YYYYMMDD
    "YYYYMM": "%Y%m",  # YYYYMM
    "MMYYYY": "%m%Y",  # MMYYYY
    "YYMM": "%y%m",  # YYMM
    "MMYY": "%m%y",  # MMYY
    "YYYYMMDD": "%Y%m%d",  # YYYYMMDD
    "MMDDYY": "%m%d%y",  # MMDDYY
    "MMDDYYYY": "%m%d%Y",  # MMDDYYYY
    "ISODATE": "%Y-%m-%d",  # YYYY-MM-DD
    "ISODATETIME": datetime.isoformat,  # isoformat (including TZ)
    "MONTH": "%m",  # MM
    "MON": "%m",  # MM
    "MONTHABV": "%b",  # Jan, Feb, etc.
    "MONTHNAME": "%B",  # January, February, etc.
    "DAYABV": "%a",  # Mon, Tues, etc
    "DAYNAME": "%A",  # Monday, Tuesday, etc.
    "DAYNUM": "%w",  # 0-6 day of week, M = 0
    "DAYYEAR": "%j",  # 001-365(6) day of year, zero-padded
    "TZOFF": "%z",  # UTC offset +HHMM or -HHMM
    "TZNAME": "%Z",  # Time zone name
    "WEEKNUM": "%W",  # Num of week in year, 00-53, zero-padded
    "DAY": "%d",  # DD
    "DD": "%d",  # DD
    "MM": "%m",  # MM
    "YY": "%y",  # YY
    "YYYY": "%Y",  # YYYY
    "LOCALE_DT": "%c",  # Locale date-time representation
    "TIMESTAMP": (
        functools.partial(_translate_int_str, datetime.timestamp)
    ),  # timestamp (UTC)
    "TS": (
        functools.partial(_translate_int_str, datetime.timestamp)
    ),  # timestamp (UTC)
    "HHMMSS": "%H:%M:%S",  # HH:MM:SS (24-hour)
    "HHMMSSZZ": "%H:%M:%S.%f",  # HH:MM:SS.ZZZZZZ (24-hour)
    "AMPM": "%p",  # AM/PM
    "HH": "%H",  # HH (24-hour)
    "HH12": "%I",  # HH in 12-hour format
    "HOUR": "%H",  # HH (24-hour)
    "MIN": "%M",  # MM
    "SECOND": "%S",  # SS
    "SS": "%S",  # SS
    "MICROSECOND": "%f",  # ZZZZZZ (microseconds)
    "ZZ": "%f",  # ZZZZZZ (microseconds)
}
_SUPPORTED_DATETIME_OUTPUT_FORMATS.update(
    {k.lower(): v for k, v in _SUPPORTED_DATETIME_OUTPUT_FORMATS.items()}
)
