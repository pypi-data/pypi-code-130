"""Timestamp extension for Pandas Timestamp with timezone support."""
import calendar
import datetime
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pytz
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import ConcreteTemplate, infer_global, signature
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo.libs.str_ext
import bodo.utils.utils
from bodo.hiframes.datetime_date_ext import DatetimeDateType, _ord2ymd, _ymd2ord, get_isocalendar
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, _no_input, datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdatetime_ext
from bodo.libs.pd_datetime_arr_ext import get_pytz_type_info
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import BodoError, check_unsupported_args, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_iterable_type, is_overload_constant_int, is_overload_constant_str, is_overload_none, raise_bodo_error
ll.add_symbol('extract_year_days', hdatetime_ext.extract_year_days)
ll.add_symbol('get_month_day', hdatetime_ext.get_month_day)
ll.add_symbol('npy_datetimestruct_to_datetime', hdatetime_ext.
    npy_datetimestruct_to_datetime)
npy_datetimestruct_to_datetime = types.ExternalFunction(
    'npy_datetimestruct_to_datetime', types.int64(types.int64, types.int32,
    types.int32, types.int32, types.int32, types.int32, types.int32))
date_fields = ['year', 'month', 'day', 'hour', 'minute', 'second',
    'microsecond', 'nanosecond', 'quarter', 'dayofyear', 'day_of_year',
    'dayofweek', 'day_of_week', 'daysinmonth', 'days_in_month',
    'is_leap_year', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end', 'week', 'weekofyear',
    'weekday']
date_methods = ['normalize', 'day_name', 'month_name']
timedelta_fields = ['days', 'seconds', 'microseconds', 'nanoseconds']
timedelta_methods = ['total_seconds', 'to_pytimedelta']
iNaT = pd._libs.tslibs.iNaT


class PandasTimestampType(types.Type):

    def __init__(self, tz_val=None):
        self.tz = tz_val
        if tz_val is None:
            nddsf__yghp = 'PandasTimestampType()'
        else:
            nddsf__yghp = f'PandasTimestampType({tz_val})'
        super(PandasTimestampType, self).__init__(name=nddsf__yghp)


pd_timestamp_type = PandasTimestampType()


def check_tz_aware_unsupported(val, func_name):
    if isinstance(val, bodo.hiframes.series_dt_impl.
        SeriesDatetimePropertiesType):
        val = val.stype
    if isinstance(val, PandasTimestampType) and val.tz is not None:
        raise BodoError(
            f'{func_name} on Timezone-aware timestamp not yet supported. Please convert to timezone naive with ts.tz_convert(None)'
            )
    elif isinstance(val, bodo.DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware array not yet supported. Please convert to timezone naive with arr.tz_convert(None)'
            )
    elif isinstance(val, bodo.DatetimeIndexType) and isinstance(val.data,
        bodo.DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware index not yet supported. Please convert to timezone naive with index.tz_convert(None)'
            )
    elif isinstance(val, bodo.SeriesType) and isinstance(val.data, bodo.
        DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware series not yet supported. Please convert to timezone naive with series.dt.tz_convert(None)'
            )
    elif isinstance(val, bodo.DataFrameType):
        for gar__xsgcp in val.data:
            if isinstance(gar__xsgcp, bodo.DatetimeArrayType):
                raise BodoError(
                    f'{func_name} on Timezone-aware columns not yet supported. Please convert each column to timezone naive with series.dt.tz_convert(None)'
                    )


@typeof_impl.register(pd.Timestamp)
def typeof_pd_timestamp(val, c):
    return PandasTimestampType(get_pytz_type_info(val.tz) if val.tz else None)


ts_field_typ = types.int64


@register_model(PandasTimestampType)
class PandasTimestampModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wotro__bcii = [('year', ts_field_typ), ('month', ts_field_typ), (
            'day', ts_field_typ), ('hour', ts_field_typ), ('minute',
            ts_field_typ), ('second', ts_field_typ), ('microsecond',
            ts_field_typ), ('nanosecond', ts_field_typ), ('value',
            ts_field_typ)]
        models.StructModel.__init__(self, dmm, fe_type, wotro__bcii)


make_attribute_wrapper(PandasTimestampType, 'year', 'year')
make_attribute_wrapper(PandasTimestampType, 'month', 'month')
make_attribute_wrapper(PandasTimestampType, 'day', 'day')
make_attribute_wrapper(PandasTimestampType, 'hour', 'hour')
make_attribute_wrapper(PandasTimestampType, 'minute', 'minute')
make_attribute_wrapper(PandasTimestampType, 'second', 'second')
make_attribute_wrapper(PandasTimestampType, 'microsecond', 'microsecond')
make_attribute_wrapper(PandasTimestampType, 'nanosecond', 'nanosecond')
make_attribute_wrapper(PandasTimestampType, 'value', 'value')


@unbox(PandasTimestampType)
def unbox_pandas_timestamp(typ, val, c):
    wbn__ogi = c.pyapi.object_getattr_string(val, 'year')
    urza__qfeo = c.pyapi.object_getattr_string(val, 'month')
    zjcp__idw = c.pyapi.object_getattr_string(val, 'day')
    rnhq__gplxo = c.pyapi.object_getattr_string(val, 'hour')
    nwex__rhd = c.pyapi.object_getattr_string(val, 'minute')
    qzo__xfq = c.pyapi.object_getattr_string(val, 'second')
    myhms__fhwf = c.pyapi.object_getattr_string(val, 'microsecond')
    pce__kvlx = c.pyapi.object_getattr_string(val, 'nanosecond')
    nfvh__hgg = c.pyapi.object_getattr_string(val, 'value')
    jbws__dhai = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jbws__dhai.year = c.pyapi.long_as_longlong(wbn__ogi)
    jbws__dhai.month = c.pyapi.long_as_longlong(urza__qfeo)
    jbws__dhai.day = c.pyapi.long_as_longlong(zjcp__idw)
    jbws__dhai.hour = c.pyapi.long_as_longlong(rnhq__gplxo)
    jbws__dhai.minute = c.pyapi.long_as_longlong(nwex__rhd)
    jbws__dhai.second = c.pyapi.long_as_longlong(qzo__xfq)
    jbws__dhai.microsecond = c.pyapi.long_as_longlong(myhms__fhwf)
    jbws__dhai.nanosecond = c.pyapi.long_as_longlong(pce__kvlx)
    jbws__dhai.value = c.pyapi.long_as_longlong(nfvh__hgg)
    c.pyapi.decref(wbn__ogi)
    c.pyapi.decref(urza__qfeo)
    c.pyapi.decref(zjcp__idw)
    c.pyapi.decref(rnhq__gplxo)
    c.pyapi.decref(nwex__rhd)
    c.pyapi.decref(qzo__xfq)
    c.pyapi.decref(myhms__fhwf)
    c.pyapi.decref(pce__kvlx)
    c.pyapi.decref(nfvh__hgg)
    bxtd__phjqc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jbws__dhai._getvalue(), is_error=bxtd__phjqc)


@box(PandasTimestampType)
def box_pandas_timestamp(typ, val, c):
    mzd__yvr = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    wbn__ogi = c.pyapi.long_from_longlong(mzd__yvr.year)
    urza__qfeo = c.pyapi.long_from_longlong(mzd__yvr.month)
    zjcp__idw = c.pyapi.long_from_longlong(mzd__yvr.day)
    rnhq__gplxo = c.pyapi.long_from_longlong(mzd__yvr.hour)
    nwex__rhd = c.pyapi.long_from_longlong(mzd__yvr.minute)
    qzo__xfq = c.pyapi.long_from_longlong(mzd__yvr.second)
    hhj__jojnw = c.pyapi.long_from_longlong(mzd__yvr.microsecond)
    fuaj__hqnw = c.pyapi.long_from_longlong(mzd__yvr.nanosecond)
    ynzb__jvma = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timestamp))
    if typ.tz is None:
        res = c.pyapi.call_function_objargs(ynzb__jvma, (wbn__ogi,
            urza__qfeo, zjcp__idw, rnhq__gplxo, nwex__rhd, qzo__xfq,
            hhj__jojnw, fuaj__hqnw))
    else:
        if isinstance(typ.tz, int):
            hhp__wodvp = c.pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), typ.tz))
        else:
            kzdy__oqt = c.context.insert_const_string(c.builder.module, str
                (typ.tz))
            hhp__wodvp = c.pyapi.string_from_string(kzdy__oqt)
        args = c.pyapi.tuple_pack(())
        kwargs = c.pyapi.dict_pack([('year', wbn__ogi), ('month',
            urza__qfeo), ('day', zjcp__idw), ('hour', rnhq__gplxo), (
            'minute', nwex__rhd), ('second', qzo__xfq), ('microsecond',
            hhj__jojnw), ('nanosecond', fuaj__hqnw), ('tz', hhp__wodvp)])
        res = c.pyapi.call(ynzb__jvma, args, kwargs)
        c.pyapi.decref(args)
        c.pyapi.decref(kwargs)
        c.pyapi.decref(hhp__wodvp)
    c.pyapi.decref(wbn__ogi)
    c.pyapi.decref(urza__qfeo)
    c.pyapi.decref(zjcp__idw)
    c.pyapi.decref(rnhq__gplxo)
    c.pyapi.decref(nwex__rhd)
    c.pyapi.decref(qzo__xfq)
    c.pyapi.decref(hhj__jojnw)
    c.pyapi.decref(fuaj__hqnw)
    return res


@intrinsic
def init_timestamp(typingctx, year, month, day, hour, minute, second,
    microsecond, nanosecond, value, tz):

    def codegen(context, builder, sig, args):
        (year, month, day, hour, minute, second, jfq__dxm, nhq__cudjg,
            value, gqsab__pqims) = args
        ts = cgutils.create_struct_proxy(sig.return_type)(context, builder)
        ts.year = year
        ts.month = month
        ts.day = day
        ts.hour = hour
        ts.minute = minute
        ts.second = second
        ts.microsecond = jfq__dxm
        ts.nanosecond = nhq__cudjg
        ts.value = value
        return ts._getvalue()
    if is_overload_none(tz):
        typ = pd_timestamp_type
    elif is_overload_constant_str(tz):
        typ = PandasTimestampType(get_overload_const_str(tz))
    elif is_overload_constant_int(tz):
        typ = PandasTimestampType(get_overload_const_int(tz))
    else:
        raise_bodo_error('tz must be a constant string, int, or None')
    return typ(types.int64, types.int64, types.int64, types.int64, types.
        int64, types.int64, types.int64, types.int64, types.int64, tz), codegen


@numba.generated_jit
def zero_if_none(value):
    if value == types.none:
        return lambda value: 0
    return lambda value: value


@lower_constant(PandasTimestampType)
def constant_timestamp(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    nanosecond = context.get_constant(types.int64, pyval.nanosecond)
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct((year, month, day, hour, minute,
        second, microsecond, nanosecond, value))


@overload(pd.Timestamp, no_unliteral=True)
def overload_pd_timestamp(ts_input=_no_input, freq=None, tz=None, unit=None,
    year=None, month=None, day=None, hour=None, minute=None, second=None,
    microsecond=None, nanosecond=None, tzinfo=None):
    if not is_overload_none(tz) and is_overload_constant_str(tz
        ) and get_overload_const_str(tz) not in pytz.all_timezones_set:
        raise BodoError(
            "pandas.Timestamp(): 'tz', if provided, must be constant string found in pytz.all_timezones"
            )
    if ts_input == _no_input or getattr(ts_input, 'value', None) == _no_input:

        def impl_kw(ts_input=_no_input, freq=None, tz=None, unit=None, year
            =None, month=None, day=None, hour=None, minute=None, second=
            None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, tz)
        return impl_kw
    if isinstance(types.unliteral(freq), types.Integer):

        def impl_pos(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(ts_input, freq, tz,
                zero_if_none(unit), zero_if_none(year), zero_if_none(month),
                zero_if_none(day))
            value += zero_if_none(hour)
            return init_timestamp(ts_input, freq, tz, zero_if_none(unit),
                zero_if_none(year), zero_if_none(month), zero_if_none(day),
                zero_if_none(hour), value, None)
        return impl_pos
    if isinstance(ts_input, types.Number):
        if is_overload_none(unit):
            unit = 'ns'
        if not is_overload_constant_str(unit):
            raise BodoError(
                'pandas.Timedelta(): unit argument must be a constant str')
        unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
            get_overload_const_str(unit))
        pqrdm__rxc, precision = pd._libs.tslibs.conversion.precision_from_unit(
            unit)
        if isinstance(ts_input, types.Integer):

            def impl_int(ts_input=_no_input, freq=None, tz=None, unit=None,
                year=None, month=None, day=None, hour=None, minute=None,
                second=None, microsecond=None, nanosecond=None, tzinfo=None):
                value = ts_input * pqrdm__rxc
                return convert_val_to_timestamp(value, tz)
            return impl_int

        def impl_float(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            tqqq__msar = np.int64(ts_input)
            ahxo__dbyk = ts_input - tqqq__msar
            if precision:
                ahxo__dbyk = np.round(ahxo__dbyk, precision)
            value = tqqq__msar * pqrdm__rxc + np.int64(ahxo__dbyk * pqrdm__rxc)
            return convert_val_to_timestamp(value, tz)
        return impl_float
    if ts_input == bodo.string_type or is_overload_constant_str(ts_input):
        types.pd_timestamp_type = pd_timestamp_type
        if is_overload_none(tz):
            tz_val = None
        elif is_overload_constant_str(tz):
            tz_val = get_overload_const_str(tz)
        else:
            raise_bodo_error(
                'pandas.Timestamp(): tz argument must be a constant string or None'
                )
        typ = PandasTimestampType(tz_val)

        def impl_str(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            with numba.objmode(res=typ):
                res = pd.Timestamp(ts_input, tz=tz)
            return res
        return impl_str
    if ts_input == pd_timestamp_type:
        return (lambda ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None: ts_input)
    if ts_input == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:

        def impl_datetime(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            hour = ts_input.hour
            minute = ts_input.minute
            second = ts_input.second
            microsecond = ts_input.microsecond
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, tz)
        return impl_datetime
    if ts_input == bodo.hiframes.datetime_date_ext.datetime_date_type:

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, None)
        return impl_date
    if isinstance(ts_input, numba.core.types.scalars.NPDatetime):
        pqrdm__rxc, precision = pd._libs.tslibs.conversion.precision_from_unit(
            ts_input.unit)

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = np.int64(ts_input) * pqrdm__rxc
            return convert_datetime64_to_timestamp(integer_to_dt64(value))
        return impl_date


@overload_attribute(PandasTimestampType, 'dayofyear')
@overload_attribute(PandasTimestampType, 'day_of_year')
def overload_pd_dayofyear(ptt):

    def pd_dayofyear(ptt):
        return get_day_of_year(ptt.year, ptt.month, ptt.day)
    return pd_dayofyear


@overload_method(PandasTimestampType, 'weekday')
@overload_attribute(PandasTimestampType, 'dayofweek')
@overload_attribute(PandasTimestampType, 'day_of_week')
def overload_pd_dayofweek(ptt):

    def pd_dayofweek(ptt):
        return get_day_of_week(ptt.year, ptt.month, ptt.day)
    return pd_dayofweek


@overload_attribute(PandasTimestampType, 'week')
@overload_attribute(PandasTimestampType, 'weekofyear')
def overload_week_number(ptt):

    def pd_week_number(ptt):
        gqsab__pqims, wix__pkes, gqsab__pqims = get_isocalendar(ptt.year,
            ptt.month, ptt.day)
        return wix__pkes
    return pd_week_number


@overload_method(PandasTimestampType, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(val.value)


@overload_attribute(PandasTimestampType, 'days_in_month')
@overload_attribute(PandasTimestampType, 'daysinmonth')
def overload_pd_daysinmonth(ptt):

    def pd_daysinmonth(ptt):
        return get_days_in_month(ptt.year, ptt.month)
    return pd_daysinmonth


@overload_attribute(PandasTimestampType, 'is_leap_year')
def overload_pd_is_leap_year(ptt):

    def pd_is_leap_year(ptt):
        return is_leap_year(ptt.year)
    return pd_is_leap_year


@overload_attribute(PandasTimestampType, 'is_month_start')
def overload_pd_is_month_start(ptt):

    def pd_is_month_start(ptt):
        return ptt.day == 1
    return pd_is_month_start


@overload_attribute(PandasTimestampType, 'is_month_end')
def overload_pd_is_month_end(ptt):

    def pd_is_month_end(ptt):
        return ptt.day == get_days_in_month(ptt.year, ptt.month)
    return pd_is_month_end


@overload_attribute(PandasTimestampType, 'is_quarter_start')
def overload_pd_is_quarter_start(ptt):

    def pd_is_quarter_start(ptt):
        return ptt.day == 1 and ptt.month % 3 == 1
    return pd_is_quarter_start


@overload_attribute(PandasTimestampType, 'is_quarter_end')
def overload_pd_is_quarter_end(ptt):

    def pd_is_quarter_end(ptt):
        return ptt.month % 3 == 0 and ptt.day == get_days_in_month(ptt.year,
            ptt.month)
    return pd_is_quarter_end


@overload_attribute(PandasTimestampType, 'is_year_start')
def overload_pd_is_year_start(ptt):

    def pd_is_year_start(ptt):
        return ptt.day == 1 and ptt.month == 1
    return pd_is_year_start


@overload_attribute(PandasTimestampType, 'is_year_end')
def overload_pd_is_year_end(ptt):

    def pd_is_year_end(ptt):
        return ptt.day == 31 and ptt.month == 12
    return pd_is_year_end


@overload_attribute(PandasTimestampType, 'quarter')
def overload_quarter(ptt):

    def quarter(ptt):
        return (ptt.month - 1) // 3 + 1
    return quarter


@overload_method(PandasTimestampType, 'date', no_unliteral=True)
def overload_pd_timestamp_date(ptt):

    def pd_timestamp_date_impl(ptt):
        return datetime.date(ptt.year, ptt.month, ptt.day)
    return pd_timestamp_date_impl


@overload_method(PandasTimestampType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(ptt):

    def impl(ptt):
        year, wix__pkes, ohph__cftkx = get_isocalendar(ptt.year, ptt.month,
            ptt.day)
        return year, wix__pkes, ohph__cftkx
    return impl


@overload_method(PandasTimestampType, 'isoformat', no_unliteral=True)
def overload_pd_timestamp_isoformat(ts, sep=None):
    if is_overload_none(sep):

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            oehu__rte = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + 'T' + oehu__rte
            return res
        return timestamp_isoformat_impl
    else:

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            oehu__rte = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + sep + oehu__rte
            return res
    return timestamp_isoformat_impl


@overload_method(PandasTimestampType, 'normalize', no_unliteral=True)
def overload_pd_timestamp_normalize(ptt):

    def impl(ptt):
        return pd.Timestamp(year=ptt.year, month=ptt.month, day=ptt.day)
    return impl


@overload_method(PandasTimestampType, 'day_name', no_unliteral=True)
def overload_pd_timestamp_day_name(ptt, locale=None):
    fmjo__teru = dict(locale=locale)
    meo__akdq = dict(locale=None)
    check_unsupported_args('Timestamp.day_name', fmjo__teru, meo__akdq,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        ylr__xssid = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday')
        gqsab__pqims, gqsab__pqims, rvh__oidk = ptt.isocalendar()
        return ylr__xssid[rvh__oidk - 1]
    return impl


@overload_method(PandasTimestampType, 'month_name', no_unliteral=True)
def overload_pd_timestamp_month_name(ptt, locale=None):
    fmjo__teru = dict(locale=locale)
    meo__akdq = dict(locale=None)
    check_unsupported_args('Timestamp.month_name', fmjo__teru, meo__akdq,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        htra__urum = ('January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November',
            'December')
        return htra__urum[ptt.month - 1]
    return impl


@overload_method(PandasTimestampType, 'tz_convert', no_unliteral=True)
def overload_pd_timestamp_tz_convert(ptt, tz):
    if ptt.tz is None:
        raise BodoError(
            'Cannot convert tz-naive Timestamp, use tz_localize to localize')
    if is_overload_none(tz):
        return lambda ptt, tz: convert_val_to_timestamp(ptt.value)
    elif is_overload_constant_str(tz):
        return lambda ptt, tz: convert_val_to_timestamp(ptt.value, tz=tz)


@overload_method(PandasTimestampType, 'tz_localize', no_unliteral=True)
def overload_pd_timestamp_tz_localize(ptt, tz, ambiguous='raise',
    nonexistent='raise'):
    if ptt.tz is not None and not is_overload_none(tz):
        raise BodoError(
            'Cannot localize tz-aware Timestamp, use tz_convert for conversions'
            )
    fmjo__teru = dict(ambiguous=ambiguous, nonexistent=nonexistent)
    ejc__sfyh = dict(ambiguous='raise', nonexistent='raise')
    check_unsupported_args('Timestamp.tz_localize', fmjo__teru, ejc__sfyh,
        package_name='pandas', module_name='Timestamp')
    if is_overload_none(tz):
        return (lambda ptt, tz, ambiguous='raise', nonexistent='raise':
            convert_val_to_timestamp(ptt.value, is_convert=False))
    elif is_overload_constant_str(tz):
        return (lambda ptt, tz, ambiguous='raise', nonexistent='raise':
            convert_val_to_timestamp(ptt.value, tz=tz, is_convert=False))


@numba.njit
def str_2d(a):
    res = str(a)
    if len(res) == 1:
        return '0' + res
    return res


@overload(str, no_unliteral=True)
def ts_str_overload(a):
    if a == pd_timestamp_type:
        return lambda a: a.isoformat(' ')


@intrinsic
def extract_year_days(typingctx, dt64_t=None):
    assert dt64_t in (types.int64, types.NPDatetime('ns'))

    def codegen(context, builder, sig, args):
        olmj__tsjji = cgutils.alloca_once(builder, lir.IntType(64))
        builder.store(args[0], olmj__tsjji)
        year = cgutils.alloca_once(builder, lir.IntType(64))
        afayq__rwqda = cgutils.alloca_once(builder, lir.IntType(64))
        pgkf__yubwb = lir.FunctionType(lir.VoidType(), [lir.IntType(64).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        pyqln__ywgq = cgutils.get_or_insert_function(builder.module,
            pgkf__yubwb, name='extract_year_days')
        builder.call(pyqln__ywgq, [olmj__tsjji, year, afayq__rwqda])
        return cgutils.pack_array(builder, [builder.load(olmj__tsjji),
            builder.load(year), builder.load(afayq__rwqda)])
    return types.Tuple([types.int64, types.int64, types.int64])(dt64_t
        ), codegen


@intrinsic
def get_month_day(typingctx, year_t, days_t=None):
    assert year_t == types.int64
    assert days_t == types.int64

    def codegen(context, builder, sig, args):
        month = cgutils.alloca_once(builder, lir.IntType(64))
        day = cgutils.alloca_once(builder, lir.IntType(64))
        pgkf__yubwb = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        pyqln__ywgq = cgutils.get_or_insert_function(builder.module,
            pgkf__yubwb, name='get_month_day')
        builder.call(pyqln__ywgq, [args[0], args[1], month, day])
        return cgutils.pack_array(builder, [builder.load(month), builder.
            load(day)])
    return types.Tuple([types.int64, types.int64])(types.int64, types.int64
        ), codegen


@register_jitable
def get_day_of_year(year, month, day):
    nzx__oimfq = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 
        365, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    eogw__pocr = is_leap_year(year)
    rno__bymlg = nzx__oimfq[eogw__pocr * 13 + month - 1]
    jjr__pvxrx = rno__bymlg + day
    return jjr__pvxrx


@register_jitable
def get_day_of_week(y, m, d):
    vhok__wttd = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    day = (y + y // 4 - y // 100 + y // 400 + vhok__wttd[m - 1] + d) % 7
    return (day + 6) % 7


@register_jitable
def get_days_in_month(year, month):
    is_leap_year = year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)
    nnegh__moda = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 29, 
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return nnegh__moda[12 * is_leap_year + month - 1]


@register_jitable
def is_leap_year(year):
    return year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)


@numba.generated_jit(nopython=True)
def convert_val_to_timestamp(ts_input, tz=None, is_convert=True):
    tpcou__xek = djoz__pqo = np.array([])
    pzn__kju = '0'
    if is_overload_constant_str(tz):
        kzdy__oqt = get_overload_const_str(tz)
        hhp__wodvp = pytz.timezone(kzdy__oqt)
        if isinstance(hhp__wodvp, pytz.tzinfo.DstTzInfo):
            tpcou__xek = np.array(hhp__wodvp._utc_transition_times, dtype=
                'M8[ns]').view('i8')
            djoz__pqo = np.array(hhp__wodvp._transition_info)[:, 0]
            djoz__pqo = (pd.Series(djoz__pqo).dt.total_seconds() * 1000000000
                ).astype(np.int64).values
            pzn__kju = (
                "deltas[np.searchsorted(trans, ts_input, side='right') - 1]")
        else:
            djoz__pqo = np.int64(hhp__wodvp._utcoffset.total_seconds() * 
                1000000000)
            pzn__kju = 'deltas'
    elif is_overload_constant_int(tz):
        mnzfq__xaqhz = get_overload_const_int(tz)
        pzn__kju = str(mnzfq__xaqhz)
    elif not is_overload_none(tz):
        raise_bodo_error(
            'convert_val_to_timestamp(): tz value must be a constant string or None'
            )
    is_convert = get_overload_const_bool(is_convert)
    if is_convert:
        laeiy__llzi = 'tz_ts_input'
        bcz__fnvt = 'ts_input'
    else:
        laeiy__llzi = 'ts_input'
        bcz__fnvt = 'tz_ts_input'
    ilne__rbp = 'def impl(ts_input, tz=None, is_convert=True):\n'
    ilne__rbp += f'  tz_ts_input = ts_input + {pzn__kju}\n'
    ilne__rbp += (
        f'  dt, year, days = extract_year_days(integer_to_dt64({laeiy__llzi}))\n'
        )
    ilne__rbp += '  month, day = get_month_day(year, days)\n'
    ilne__rbp += '  return init_timestamp(\n'
    ilne__rbp += '    year=year,\n'
    ilne__rbp += '    month=month,\n'
    ilne__rbp += '    day=day,\n'
    ilne__rbp += '    hour=dt // (60 * 60 * 1_000_000_000),\n'
    ilne__rbp += '    minute=(dt // (60 * 1_000_000_000)) % 60,\n'
    ilne__rbp += '    second=(dt // 1_000_000_000) % 60,\n'
    ilne__rbp += '    microsecond=(dt // 1000) % 1_000_000,\n'
    ilne__rbp += '    nanosecond=dt % 1000,\n'
    ilne__rbp += f'    value={bcz__fnvt},\n'
    ilne__rbp += '    tz=tz,\n'
    ilne__rbp += '  )\n'
    svjlk__giy = {}
    exec(ilne__rbp, {'np': np, 'pd': pd, 'trans': tpcou__xek, 'deltas':
        djoz__pqo, 'integer_to_dt64': integer_to_dt64, 'extract_year_days':
        extract_year_days, 'get_month_day': get_month_day, 'init_timestamp':
        init_timestamp, 'zero_if_none': zero_if_none}, svjlk__giy)
    impl = svjlk__giy['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def convert_datetime64_to_timestamp(dt64):
    olmj__tsjji, year, afayq__rwqda = extract_year_days(dt64)
    month, day = get_month_day(year, afayq__rwqda)
    return init_timestamp(year=year, month=month, day=day, hour=olmj__tsjji //
        (60 * 60 * 1000000000), minute=olmj__tsjji // (60 * 1000000000) % 
        60, second=olmj__tsjji // 1000000000 % 60, microsecond=olmj__tsjji //
        1000 % 1000000, nanosecond=olmj__tsjji % 1000, value=dt64, tz=None)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_datetime_timedelta(dt64):
    lfd__ppdp = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    itse__lxai = lfd__ppdp // (86400 * 1000000000)
    qikhc__xbw = lfd__ppdp - itse__lxai * 86400 * 1000000000
    wjne__huemv = qikhc__xbw // 1000000000
    zuby__cyiqv = qikhc__xbw - wjne__huemv * 1000000000
    bfqkp__mge = zuby__cyiqv // 1000
    return datetime.timedelta(itse__lxai, wjne__huemv, bfqkp__mge)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_pd_timedelta(dt64):
    lfd__ppdp = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    return pd.Timedelta(lfd__ppdp)


@intrinsic
def integer_to_timedelta64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPTimedelta('ns')(val), codegen


@intrinsic
def integer_to_dt64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPDatetime('ns')(val), codegen


@intrinsic
def dt64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(types.NPDatetime('ns'), types.int64)
def cast_dt64_to_integer(context, builder, fromty, toty, val):
    return val


@overload_method(types.NPDatetime, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@overload_method(types.NPTimedelta, '__hash__', no_unliteral=True)
def td64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@intrinsic
def timedelta64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(bodo.timedelta64ns, types.int64)
def cast_td64_to_integer(context, builder, fromty, toty, val):
    return val


@numba.njit
def parse_datetime_str(val):
    with numba.objmode(res='int64'):
        res = pd.Timestamp(val).value
    return integer_to_dt64(res)


@numba.njit
def datetime_timedelta_to_timedelta64(val):
    with numba.objmode(res='NPTimedelta("ns")'):
        res = pd.to_timedelta(val)
        res = res.to_timedelta64()
    return res


@numba.njit
def series_str_dt64_astype(data):
    with numba.objmode(res="NPDatetime('ns')[::1]"):
        res = pd.Series(data).astype('datetime64[ns]').values
    return res


@numba.njit
def series_str_td64_astype(data):
    with numba.objmode(res="NPTimedelta('ns')[::1]"):
        res = data.astype('timedelta64[ns]')
    return res


@numba.njit
def datetime_datetime_to_dt64(val):
    with numba.objmode(res='NPDatetime("ns")'):
        res = np.datetime64(val).astype('datetime64[ns]')
    return res


@register_jitable
def datetime_date_arr_to_dt64_arr(arr):
    with numba.objmode(res='NPDatetime("ns")[::1]'):
        res = np.array(arr, dtype='datetime64[ns]')
    return res


types.pd_timestamp_type = pd_timestamp_type


@register_jitable
def to_datetime_scalar(a, errors='raise', dayfirst=False, yearfirst=False,
    utc=None, format=None, exact=True, unit=None, infer_datetime_format=
    False, origin='unix', cache=True):
    with numba.objmode(t='pd_timestamp_type'):
        t = pd.to_datetime(a, errors=errors, dayfirst=dayfirst, yearfirst=
            yearfirst, utc=utc, format=format, exact=exact, unit=unit,
            infer_datetime_format=infer_datetime_format, origin=origin,
            cache=cache)
    return t


@numba.njit
def pandas_string_array_to_datetime(arr, errors, dayfirst, yearfirst, utc,
    format, exact, unit, infer_datetime_format, origin, cache):
    with numba.objmode(result='datetime_index'):
        result = pd.to_datetime(arr, errors=errors, dayfirst=dayfirst,
            yearfirst=yearfirst, utc=utc, format=format, exact=exact, unit=
            unit, infer_datetime_format=infer_datetime_format, origin=
            origin, cache=cache)
    return result


@numba.njit
def pandas_dict_string_array_to_datetime(arr, errors, dayfirst, yearfirst,
    utc, format, exact, unit, infer_datetime_format, origin, cache):
    xkbq__xior = len(arr)
    pvvmr__xer = np.empty(xkbq__xior, 'datetime64[ns]')
    fcc__tjso = arr._indices
    bun__uyuue = pandas_string_array_to_datetime(arr._data, errors,
        dayfirst, yearfirst, utc, format, exact, unit,
        infer_datetime_format, origin, cache).values
    for rrls__qoyjn in range(xkbq__xior):
        if bodo.libs.array_kernels.isna(fcc__tjso, rrls__qoyjn):
            bodo.libs.array_kernels.setna(pvvmr__xer, rrls__qoyjn)
            continue
        pvvmr__xer[rrls__qoyjn] = bun__uyuue[fcc__tjso[rrls__qoyjn]]
    return pvvmr__xer


@overload(pd.to_datetime, inline='always', no_unliteral=True)
def overload_to_datetime(arg_a, errors='raise', dayfirst=False, yearfirst=
    False, utc=None, format=None, exact=True, unit=None,
    infer_datetime_format=False, origin='unix', cache=True):
    if arg_a == bodo.string_type or is_overload_constant_str(arg_a
        ) or is_overload_constant_int(arg_a) or isinstance(arg_a, types.Integer
        ):

        def pd_to_datetime_impl(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return to_datetime_scalar(arg_a, errors=errors, dayfirst=
                dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                exact=exact, unit=unit, infer_datetime_format=
                infer_datetime_format, origin=origin, cache=cache)
        return pd_to_datetime_impl
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            dmajc__dcqrj = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nddsf__yghp = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            edsp__hwufl = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_datetime(arr, errors=errors, dayfirst=dayfirst,
                yearfirst=yearfirst, utc=utc, format=format, exact=exact,
                unit=unit, infer_datetime_format=infer_datetime_format,
                origin=origin, cache=cache))
            return bodo.hiframes.pd_series_ext.init_series(edsp__hwufl,
                dmajc__dcqrj, nddsf__yghp)
        return impl_series
    if arg_a == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        dypat__ouvj = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            xkbq__xior = len(arg_a)
            pvvmr__xer = np.empty(xkbq__xior, dypat__ouvj)
            for rrls__qoyjn in numba.parfors.parfor.internal_prange(xkbq__xior
                ):
                val = iNaT
                if not bodo.libs.array_kernels.isna(arg_a, rrls__qoyjn):
                    data = arg_a[rrls__qoyjn]
                    val = (bodo.hiframes.pd_timestamp_ext.
                        npy_datetimestruct_to_datetime(data.year, data.
                        month, data.day, 0, 0, 0, 0))
                pvvmr__xer[rrls__qoyjn
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(pvvmr__xer,
                None)
        return impl_date_arr
    if arg_a == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return (lambda arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True: bodo.
            hiframes.pd_index_ext.init_datetime_index(arg_a, None))
    if arg_a == string_array_type:

        def impl_string_array(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return pandas_string_array_to_datetime(arg_a, errors, dayfirst,
                yearfirst, utc, format, exact, unit, infer_datetime_format,
                origin, cache)
        return impl_string_array
    if isinstance(arg_a, types.Array) and isinstance(arg_a.dtype, types.Integer
        ):
        dypat__ouvj = np.dtype('datetime64[ns]')

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            xkbq__xior = len(arg_a)
            pvvmr__xer = np.empty(xkbq__xior, dypat__ouvj)
            for rrls__qoyjn in numba.parfors.parfor.internal_prange(xkbq__xior
                ):
                data = arg_a[rrls__qoyjn]
                val = to_datetime_scalar(data, errors=errors, dayfirst=
                    dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                    exact=exact, unit=unit, infer_datetime_format=
                    infer_datetime_format, origin=origin, cache=cache)
                pvvmr__xer[rrls__qoyjn
                    ] = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(pvvmr__xer,
                None)
        return impl_date_arr
    if isinstance(arg_a, CategoricalArrayType
        ) and arg_a.dtype.elem_type == bodo.string_type:
        dypat__ouvj = np.dtype('datetime64[ns]')

        def impl_cat_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            xkbq__xior = len(arg_a)
            pvvmr__xer = np.empty(xkbq__xior, dypat__ouvj)
            dbuyx__qzasg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arg_a))
            bun__uyuue = pandas_string_array_to_datetime(arg_a.dtype.
                categories.values, errors, dayfirst, yearfirst, utc, format,
                exact, unit, infer_datetime_format, origin, cache).values
            for rrls__qoyjn in numba.parfors.parfor.internal_prange(xkbq__xior
                ):
                c = dbuyx__qzasg[rrls__qoyjn]
                if c == -1:
                    bodo.libs.array_kernels.setna(pvvmr__xer, rrls__qoyjn)
                    continue
                pvvmr__xer[rrls__qoyjn] = bun__uyuue[c]
            return bodo.hiframes.pd_index_ext.init_datetime_index(pvvmr__xer,
                None)
        return impl_cat_arr
    if arg_a == bodo.dict_str_arr_type:

        def impl_dict_str_arr(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            pvvmr__xer = pandas_dict_string_array_to_datetime(arg_a, errors,
                dayfirst, yearfirst, utc, format, exact, unit,
                infer_datetime_format, origin, cache)
            return bodo.hiframes.pd_index_ext.init_datetime_index(pvvmr__xer,
                None)
        return impl_dict_str_arr
    if isinstance(arg_a, PandasTimestampType):

        def impl_timestamp(arg_a, errors='raise', dayfirst=False, yearfirst
            =False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return arg_a
        return impl_timestamp
    raise_bodo_error(f'pd.to_datetime(): cannot convert date type {arg_a}')


@overload(pd.to_timedelta, inline='always', no_unliteral=True)
def overload_to_timedelta(arg_a, unit='ns', errors='raise'):
    if not is_overload_constant_str(unit):
        raise BodoError(
            'pandas.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, unit='ns', errors='raise'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            dmajc__dcqrj = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nddsf__yghp = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            edsp__hwufl = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_timedelta(arr, unit, errors))
            return bodo.hiframes.pd_series_ext.init_series(edsp__hwufl,
                dmajc__dcqrj, nddsf__yghp)
        return impl_series
    if is_overload_constant_str(arg_a) or arg_a in (pd_timedelta_type,
        datetime_timedelta_type, bodo.string_type):

        def impl_string(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a)
        return impl_string
    if isinstance(arg_a, types.Float):
        m, agcx__fdjh = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_float_scalar(arg_a, unit='ns', errors='raise'):
            val = float_to_timedelta_val(arg_a, agcx__fdjh, m)
            return pd.Timedelta(val)
        return impl_float_scalar
    if isinstance(arg_a, types.Integer):
        m, gqsab__pqims = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_integer_scalar(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a * m)
        return impl_integer_scalar
    if is_iterable_type(arg_a) and not isinstance(arg_a, types.BaseTuple):
        m, agcx__fdjh = pd._libs.tslibs.conversion.precision_from_unit(unit)
        hrtj__sbo = np.dtype('timedelta64[ns]')
        if isinstance(arg_a.dtype, types.Float):

            def impl_float(arg_a, unit='ns', errors='raise'):
                xkbq__xior = len(arg_a)
                pvvmr__xer = np.empty(xkbq__xior, hrtj__sbo)
                for rrls__qoyjn in numba.parfors.parfor.internal_prange(
                    xkbq__xior):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rrls__qoyjn):
                        val = float_to_timedelta_val(arg_a[rrls__qoyjn],
                            agcx__fdjh, m)
                    pvvmr__xer[rrls__qoyjn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    pvvmr__xer, None)
            return impl_float
        if isinstance(arg_a.dtype, types.Integer):

            def impl_int(arg_a, unit='ns', errors='raise'):
                xkbq__xior = len(arg_a)
                pvvmr__xer = np.empty(xkbq__xior, hrtj__sbo)
                for rrls__qoyjn in numba.parfors.parfor.internal_prange(
                    xkbq__xior):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rrls__qoyjn):
                        val = arg_a[rrls__qoyjn] * m
                    pvvmr__xer[rrls__qoyjn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    pvvmr__xer, None)
            return impl_int
        if arg_a.dtype == bodo.timedelta64ns:

            def impl_td64(arg_a, unit='ns', errors='raise'):
                arr = bodo.utils.conversion.coerce_to_ndarray(arg_a)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(arr,
                    None)
            return impl_td64
        if arg_a.dtype == bodo.string_type or isinstance(arg_a.dtype, types
            .UnicodeCharSeq):

            def impl_str(arg_a, unit='ns', errors='raise'):
                return pandas_string_array_to_timedelta(arg_a, unit, errors)
            return impl_str
        if arg_a.dtype == datetime_timedelta_type:

            def impl_datetime_timedelta(arg_a, unit='ns', errors='raise'):
                xkbq__xior = len(arg_a)
                pvvmr__xer = np.empty(xkbq__xior, hrtj__sbo)
                for rrls__qoyjn in numba.parfors.parfor.internal_prange(
                    xkbq__xior):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rrls__qoyjn):
                        awlpf__fbasc = arg_a[rrls__qoyjn]
                        val = (awlpf__fbasc.microseconds + 1000 * 1000 * (
                            awlpf__fbasc.seconds + 24 * 60 * 60 *
                            awlpf__fbasc.days)) * 1000
                    pvvmr__xer[rrls__qoyjn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    pvvmr__xer, None)
            return impl_datetime_timedelta
    raise_bodo_error(
        f'pd.to_timedelta(): cannot convert date type {arg_a.dtype}')


@register_jitable
def float_to_timedelta_val(data, precision, multiplier):
    tqqq__msar = np.int64(data)
    ahxo__dbyk = data - tqqq__msar
    if precision:
        ahxo__dbyk = np.round(ahxo__dbyk, precision)
    return tqqq__msar * multiplier + np.int64(ahxo__dbyk * multiplier)


@numba.njit
def pandas_string_array_to_timedelta(arg_a, unit='ns', errors='raise'):
    with numba.objmode(result='timedelta_index'):
        result = pd.to_timedelta(arg_a, errors=errors)
    return result


def create_timestamp_cmp_op_overload(op):

    def overload_date_timestamp_cmp(lhs, rhs):
        if (lhs == pd_timestamp_type and rhs == bodo.hiframes.
            datetime_date_ext.datetime_date_type):
            return lambda lhs, rhs: op(lhs.value, bodo.hiframes.
                pd_timestamp_ext.npy_datetimestruct_to_datetime(rhs.year,
                rhs.month, rhs.day, 0, 0, 0, 0))
        if (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and 
            rhs == pd_timestamp_type):
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                npy_datetimestruct_to_datetime(lhs.year, lhs.month, lhs.day,
                0, 0, 0, 0), rhs.value)
        if lhs == pd_timestamp_type and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs.value, rhs.value)
        if lhs == pd_timestamp_type and rhs == bodo.datetime64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(lhs.value), rhs)
        if lhs == bodo.datetime64ns and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(rhs.value))
    return overload_date_timestamp_cmp


@overload_method(PandasTimestampType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


def overload_freq_methods(method):

    def freq_overload(td, freq, ambiguous='raise', nonexistent='raise'):
        check_tz_aware_unsupported(td, f'Timestamp.{method}()')
        fmjo__teru = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        bjbph__mrjbx = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Timestamp.{method}', fmjo__teru,
            bjbph__mrjbx, package_name='pandas', module_name='Timestamp')
        pgmle__pak = ["freq == 'D'", "freq == 'H'",
            "freq == 'min' or freq == 'T'", "freq == 'S'",
            "freq == 'ms' or freq == 'L'", "freq == 'U' or freq == 'us'",
            "freq == 'N'"]
        cgpv__bxalu = [24 * 60 * 60 * 1000000 * 1000, 60 * 60 * 1000000 * 
            1000, 60 * 1000000 * 1000, 1000000 * 1000, 1000 * 1000, 1000, 1]
        ilne__rbp = (
            "def impl(td, freq, ambiguous='raise', nonexistent='raise'):\n")
        for rrls__qoyjn, tovss__zqytm in enumerate(pgmle__pak):
            ggfkt__vra = 'if' if rrls__qoyjn == 0 else 'elif'
            ilne__rbp += '    {} {}:\n'.format(ggfkt__vra, tovss__zqytm)
            ilne__rbp += '        unit_value = {}\n'.format(cgpv__bxalu[
                rrls__qoyjn])
        ilne__rbp += '    else:\n'
        ilne__rbp += (
            "        raise ValueError('Incorrect Frequency specification')\n")
        if td == pd_timedelta_type:
            ilne__rbp += (
                """    return pd.Timedelta(unit_value * np.int64(np.{}(td.value / unit_value)))
"""
                .format(method))
        elif td == pd_timestamp_type:
            if method == 'ceil':
                ilne__rbp += (
                    '    value = td.value + np.remainder(-td.value, unit_value)\n'
                    )
            if method == 'floor':
                ilne__rbp += (
                    '    value = td.value - np.remainder(td.value, unit_value)\n'
                    )
            if method == 'round':
                ilne__rbp += '    if unit_value == 1:\n'
                ilne__rbp += '        value = td.value\n'
                ilne__rbp += '    else:\n'
                ilne__rbp += (
                    '        quotient, remainder = np.divmod(td.value, unit_value)\n'
                    )
                ilne__rbp += """        mask = np.logical_or(remainder > (unit_value // 2), np.logical_and(remainder == (unit_value // 2), quotient % 2))
"""
                ilne__rbp += '        if mask:\n'
                ilne__rbp += '            quotient = quotient + 1\n'
                ilne__rbp += '        value = quotient * unit_value\n'
            ilne__rbp += '    return pd.Timestamp(value)\n'
        svjlk__giy = {}
        exec(ilne__rbp, {'np': np, 'pd': pd}, svjlk__giy)
        impl = svjlk__giy['impl']
        return impl
    return freq_overload


def _install_freq_methods():
    vmc__jxb = ['ceil', 'floor', 'round']
    for method in vmc__jxb:
        rau__ddj = overload_freq_methods(method)
        overload_method(PDTimeDeltaType, method, no_unliteral=True)(rau__ddj)
        overload_method(PandasTimestampType, method, no_unliteral=True)(
            rau__ddj)


_install_freq_methods()


@register_jitable
def compute_pd_timestamp(totmicrosec, nanosecond):
    microsecond = totmicrosec % 1000000
    tlx__omo = totmicrosec // 1000000
    second = tlx__omo % 60
    dfdpg__sxv = tlx__omo // 60
    minute = dfdpg__sxv % 60
    pod__hjgfb = dfdpg__sxv // 60
    hour = pod__hjgfb % 24
    twvz__elza = pod__hjgfb // 24
    year, month, day = _ord2ymd(twvz__elza)
    value = npy_datetimestruct_to_datetime(year, month, day, hour, minute,
        second, microsecond)
    value += zero_if_none(nanosecond)
    return init_timestamp(year, month, day, hour, minute, second,
        microsecond, nanosecond, value, None)


def overload_sub_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            hrc__aoyi = lhs.toordinal()
            tys__xzypf = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ygya__leei = lhs.microsecond
            nanosecond = lhs.nanosecond
            nfqw__icpn = rhs.days
            qahz__wwwhf = rhs.seconds
            lha__nxnlg = rhs.microseconds
            nupb__sgq = hrc__aoyi - nfqw__icpn
            hvu__ezmb = tys__xzypf - qahz__wwwhf
            xlk__zrwiq = ygya__leei - lha__nxnlg
            totmicrosec = 1000000 * (nupb__sgq * 86400 + hvu__ezmb
                ) + xlk__zrwiq
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl_timestamp(lhs, rhs):
            return convert_numpy_timedelta64_to_pd_timedelta(lhs.value -
                rhs.value)
        return impl_timestamp
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


def overload_add_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            hrc__aoyi = lhs.toordinal()
            tys__xzypf = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ygya__leei = lhs.microsecond
            nanosecond = lhs.nanosecond
            nfqw__icpn = rhs.days
            qahz__wwwhf = rhs.seconds
            lha__nxnlg = rhs.microseconds
            nupb__sgq = hrc__aoyi + nfqw__icpn
            hvu__ezmb = tys__xzypf + qahz__wwwhf
            xlk__zrwiq = ygya__leei + lha__nxnlg
            totmicrosec = 1000000 * (nupb__sgq * 86400 + hvu__ezmb
                ) + xlk__zrwiq
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            hrc__aoyi = lhs.toordinal()
            tys__xzypf = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ygya__leei = lhs.microsecond
            oayb__gtes = lhs.nanosecond
            lha__nxnlg = rhs.value // 1000
            pws__hrsz = rhs.nanoseconds
            xlk__zrwiq = ygya__leei + lha__nxnlg
            totmicrosec = 1000000 * (hrc__aoyi * 86400 + tys__xzypf
                ) + xlk__zrwiq
            igvyc__lete = oayb__gtes + pws__hrsz
            return compute_pd_timestamp(totmicrosec, igvyc__lete)
        return impl
    if (lhs == pd_timedelta_type and rhs == pd_timestamp_type or lhs ==
        datetime_timedelta_type and rhs == pd_timestamp_type):

        def impl(lhs, rhs):
            return rhs + lhs
        return impl


@overload(min, no_unliteral=True)
def timestamp_min(lhs, rhs):
    check_tz_aware_unsupported(lhs, f'Timestamp.min()')
    check_tz_aware_unsupported(rhs, f'Timestamp.min()')
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def timestamp_max(lhs, rhs):
    check_tz_aware_unsupported(lhs, f'Timestamp.max()')
    check_tz_aware_unsupported(rhs, f'Timestamp.max()')
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, 'strftime')
@overload_method(PandasTimestampType, 'strftime')
def strftime(ts, format):
    if isinstance(ts, DatetimeDateType):
        iaks__bjpx = 'datetime.date'
    else:
        iaks__bjpx = 'pandas.Timestamp'
    if types.unliteral(format) != types.unicode_type:
        raise BodoError(
            f"{iaks__bjpx}.strftime(): 'strftime' argument must be a string")

    def impl(ts, format):
        with numba.objmode(res='unicode_type'):
            res = ts.strftime(format)
        return res
    return impl


@overload_method(PandasTimestampType, 'to_datetime64')
def to_datetime64(ts):

    def impl(ts):
        return integer_to_dt64(ts.value)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='pd_timestamp_type'):
        d = pd.Timestamp.now()
    return d


class CompDT64(ConcreteTemplate):
    cases = [signature(types.boolean, types.NPDatetime('ns'), types.
        NPDatetime('ns'))]


@infer_global(operator.lt)
class CmpOpLt(CompDT64):
    key = operator.lt


@infer_global(operator.le)
class CmpOpLe(CompDT64):
    key = operator.le


@infer_global(operator.gt)
class CmpOpGt(CompDT64):
    key = operator.gt


@infer_global(operator.ge)
class CmpOpGe(CompDT64):
    key = operator.ge


@infer_global(operator.eq)
class CmpOpEq(CompDT64):
    key = operator.eq


@infer_global(operator.ne)
class CmpOpNe(CompDT64):
    key = operator.ne


@typeof_impl.register(calendar._localized_month)
def typeof_python_calendar(val, c):
    return types.Tuple([types.StringLiteral(ptgyu__vkobc) for ptgyu__vkobc in
        val])


@overload(str)
def overload_datetime64_str(val):
    if val == bodo.datetime64ns:

        def impl(val):
            return (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(val).isoformat('T'))
        return impl


timestamp_unsupported_attrs = ['asm8', 'components', 'freqstr', 'tz',
    'fold', 'tzinfo', 'freq']
timestamp_unsupported_methods = ['astimezone', 'ctime', 'dst', 'isoweekday',
    'replace', 'strptime', 'time', 'timestamp', 'timetuple', 'timetz',
    'to_julian_date', 'to_numpy', 'to_period', 'to_pydatetime', 'tzname',
    'utcoffset', 'utctimetuple']


def _install_pd_timestamp_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for bxt__tth in timestamp_unsupported_attrs:
        lxc__bnvn = 'pandas.Timestamp.' + bxt__tth
        overload_attribute(PandasTimestampType, bxt__tth)(
            create_unsupported_overload(lxc__bnvn))
    for wakix__atwe in timestamp_unsupported_methods:
        lxc__bnvn = 'pandas.Timestamp.' + wakix__atwe
        overload_method(PandasTimestampType, wakix__atwe)(
            create_unsupported_overload(lxc__bnvn + '()'))


_install_pd_timestamp_unsupported()


@lower_builtin(numba.core.types.functions.NumberClass, pd_timestamp_type,
    types.StringLiteral)
def datetime64_constructor(context, builder, sig, args):

    def datetime64_constructor_impl(a, b):
        return integer_to_dt64(a.value)
    return context.compile_internal(builder, datetime64_constructor_impl,
        sig, args)
