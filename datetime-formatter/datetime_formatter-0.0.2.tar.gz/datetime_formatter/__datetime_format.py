import attr  # type: ignore
import datetime  # type: ignore
import dateutil.tz  # type: ignore
from holidays.holiday_base import HolidayBase
import re
from string import Formatter

from typing import (
    Dict,
    Optional,
    Protocol,
    Union,
)

from .__datetime import _DateTime

from .__formats import (
    _PARSE_DT_REGEX,
    _PARSE_DT_SUB_REGEX,
    _PARSE_DT_TRANSLATION,
    _SUPPORTED_TRANSLATION_SIZES,
    _SUPPORTED_TRANSLATION_DIRECTIONS,
    _SUPPORTED_DATETIME_OUTPUT_FORMATS,
    _dtformat,
    _dttranslate,
)

__all__ = [
    "dtfmt",
    "dtformat",
    "DateTimeFormatter",
    "DateTimeFormatTimeZoneError",
    "DateTimeFormatTranslationError",
    "DateTimeFormatFieldError",
]


class SupportsToDateTime(Protocol):
    def to_datetime(self) -> datetime.datetime:
        ...  # pragma: no cover


def dtformat(
    dt: Union[
        str,
        int,
        datetime.datetime,
        datetime.date,
        datetime.time,
        SupportsToDateTime,
    ],
    fmtstr: str,
    output_tz: Optional[Union[str, datetime.tzinfo]] = None,
    holidays: Optional[Union[Dict[str, str], HolidayBase]] = None,
) -> str:
    if fmtstr is None:
        return None
    if not fmtstr.startswith("%") and not fmtstr.endswith("%"):
        fmtstr = f"%{fmtstr}%"
    # mypy complains about kw use in the below, which is weird, but best
    # to skip
    dtf = DateTimeFormatter(dt, holidays=holidays)  # type:ignore
    if isinstance(output_tz, str):
        orig_tz = output_tz
        output_tz = dateutil.tz.gettz(output_tz)
        if output_tz is None:
            raise DateTimeFormatTimeZoneError(
                f"invalid tz specification {orig_tz}, could not convert to "
                "tzinfo"
            )
    if output_tz is not None:
        if dtf.dt.dt.tzinfo is None:
            raise DateTimeFormatTimeZoneError(
                f"tried to translate to an output timezone ({output_tz}), "
                "but provided datetime is naive"
            )
        dtf.dt.dt = dtf.dt.dt.astimezone(output_tz)
    return dtf.format(fmtstr)


dtfmt = dtformat


class DateTimeFormatTimeZoneError(Exception):
    pass


class DateTimeFormatTranslationError(Exception):
    pass


class DateTimeFormatFieldError(Exception):
    pass


@attr.s(auto_attribs=True)
class DateTimeFormatter(Formatter):
    dt: _DateTime = attr.ib(converter=_DateTime)
    holidays: Optional[HolidayBase] = None

    def __call__(self, *args, **kwargs):
        return self.format(*args, **kwargs)

    def format(self, s, *args, **kwargs):
        # magic to make sure %%-wrapped are recognized
        s = re.sub(_PARSE_DT_SUB_REGEX, r"{\1}", s)

        parse_fields = self.parse(s)
        for _, fld, _, _ in parse_fields:
            if fld is None:
                continue
            if len(fld) == 0:
                continue
            matches = re.match(_PARSE_DT_REGEX, fld)
            if matches is None:
                continue
            fmt = matches.group("format")
            translation = matches.group("translation")

            use_dt = _translate_dt(self.dt, translation, self.holidays)
            if use_dt is None:
                raise DateTimeFormatTranslationError(
                    f"error in datetime_format specification {fld}, "
                    f"found but could not identify translation {translation}"
                )

            stfmt = _SUPPORTED_DATETIME_OUTPUT_FORMATS.get(fmt, None)
            if stfmt is None:
                raise DateTimeFormatFieldError(
                    f"Found format specification {fmt} in date format {fld},  "
                    f"but this is an unsupported specification."
                )
            if isinstance(stfmt, str):
                kwargs.update({fld: use_dt.strftime(stfmt)})
            else:
                kwargs.update({fld: stfmt(use_dt)})
        return super().format(s, *args, **kwargs)


def _get_dir(d):
    return _SUPPORTED_TRANSLATION_DIRECTIONS[d]


def _get_size(s):
    return _SUPPORTED_TRANSLATION_SIZES[s]


def _translate_dt(dt, translation, holidays):
    if translation is None:
        return dt.dt
    trans_matches = re.match(_PARSE_DT_TRANSLATION, translation)
    if trans_matches is None:
        return None
    dir_name = trans_matches.group("dir")
    num = int(trans_matches.group("num"))
    size_name = trans_matches.group("size")
    try:
        dir = _get_dir(dir_name)
        size = _get_size(size_name)
    except KeyError as ke:
        raise DateTimeFormatTranslationError(
            f"Error decoding translation: {translation}, error was:\n"
            f"KeyError: {str(ke)}"
        )
    return dt.translate(size, num * dir, holidays=holidays)
