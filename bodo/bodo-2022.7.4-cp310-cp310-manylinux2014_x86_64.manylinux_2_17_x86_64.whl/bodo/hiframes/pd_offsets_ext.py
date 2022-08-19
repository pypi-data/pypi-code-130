"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        neo__bgilf = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, neo__bgilf)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    fyrde__rugx = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    teyz__plgwh = c.pyapi.long_from_longlong(fyrde__rugx.n)
    uais__axg = c.pyapi.from_native_value(types.boolean, fyrde__rugx.
        normalize, c.env_manager)
    emn__yva = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    otjix__hlg = c.pyapi.call_function_objargs(emn__yva, (teyz__plgwh,
        uais__axg))
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    c.pyapi.decref(emn__yva)
    return otjix__hlg


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    teyz__plgwh = c.pyapi.object_getattr_string(val, 'n')
    uais__axg = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(teyz__plgwh)
    normalize = c.pyapi.to_native_value(types.bool_, uais__axg).value
    fyrde__rugx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fyrde__rugx.n = n
    fyrde__rugx.normalize = normalize
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    rmd__cvchq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fyrde__rugx._getvalue(), is_error=rmd__cvchq)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        fyrde__rugx = cgutils.create_struct_proxy(typ)(context, builder)
        fyrde__rugx.n = args[0]
        fyrde__rugx.normalize = args[1]
        return fyrde__rugx._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        neo__bgilf = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, neo__bgilf)


@box(MonthEndType)
def box_month_end(typ, val, c):
    biufm__lygq = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    teyz__plgwh = c.pyapi.long_from_longlong(biufm__lygq.n)
    uais__axg = c.pyapi.from_native_value(types.boolean, biufm__lygq.
        normalize, c.env_manager)
    eef__iactb = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    otjix__hlg = c.pyapi.call_function_objargs(eef__iactb, (teyz__plgwh,
        uais__axg))
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    c.pyapi.decref(eef__iactb)
    return otjix__hlg


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    teyz__plgwh = c.pyapi.object_getattr_string(val, 'n')
    uais__axg = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(teyz__plgwh)
    normalize = c.pyapi.to_native_value(types.bool_, uais__axg).value
    biufm__lygq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    biufm__lygq.n = n
    biufm__lygq.normalize = normalize
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    rmd__cvchq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(biufm__lygq._getvalue(), is_error=rmd__cvchq)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        biufm__lygq = cgutils.create_struct_proxy(typ)(context, builder)
        biufm__lygq.n = args[0]
        biufm__lygq.normalize = args[1]
        return biufm__lygq._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        biufm__lygq = get_days_in_month(year, month)
        if biufm__lygq > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        neo__bgilf = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, neo__bgilf)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    zxjek__xxf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    zxxmh__apnn = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for nuv__udo, pss__sitps in enumerate(date_offset_fields):
        c.builder.store(getattr(zxjek__xxf, pss__sitps), c.builder.inttoptr
            (c.builder.add(c.builder.ptrtoint(zxxmh__apnn, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * nuv__udo)), lir.IntType(64).
            as_pointer()))
    zng__rfw = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    dhbrc__uqqjk = cgutils.get_or_insert_function(c.builder.module,
        zng__rfw, name='box_date_offset')
    fbov__yxx = c.builder.call(dhbrc__uqqjk, [zxjek__xxf.n, zxjek__xxf.
        normalize, zxxmh__apnn, zxjek__xxf.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return fbov__yxx


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    teyz__plgwh = c.pyapi.object_getattr_string(val, 'n')
    uais__axg = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(teyz__plgwh)
    normalize = c.pyapi.to_native_value(types.bool_, uais__axg).value
    zxxmh__apnn = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    zng__rfw = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer(
        ), lir.IntType(64).as_pointer()])
    qnmx__hdyyr = cgutils.get_or_insert_function(c.builder.module, zng__rfw,
        name='unbox_date_offset')
    has_kws = c.builder.call(qnmx__hdyyr, [val, zxxmh__apnn])
    zxjek__xxf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zxjek__xxf.n = n
    zxjek__xxf.normalize = normalize
    for nuv__udo, pss__sitps in enumerate(date_offset_fields):
        setattr(zxjek__xxf, pss__sitps, c.builder.load(c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(zxxmh__apnn, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * nuv__udo)), lir.IntType(64).
            as_pointer())))
    zxjek__xxf.has_kws = has_kws
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    rmd__cvchq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zxjek__xxf._getvalue(), is_error=rmd__cvchq)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    hvdw__mjvc = [n, normalize]
    has_kws = False
    auzj__gio = [0] * 9 + [-1] * 9
    for nuv__udo, pss__sitps in enumerate(date_offset_fields):
        if hasattr(pyval, pss__sitps):
            nols__kofwt = context.get_constant(types.int64, getattr(pyval,
                pss__sitps))
            has_kws = True
        else:
            nols__kofwt = context.get_constant(types.int64, auzj__gio[nuv__udo]
                )
        hvdw__mjvc.append(nols__kofwt)
    has_kws = context.get_constant(types.boolean, has_kws)
    hvdw__mjvc.append(has_kws)
    return lir.Constant.literal_struct(hvdw__mjvc)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    nqh__sxl = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for bmuwz__qky in nqh__sxl:
        if not is_overload_none(bmuwz__qky):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        zxjek__xxf = cgutils.create_struct_proxy(typ)(context, builder)
        zxjek__xxf.n = args[0]
        zxjek__xxf.normalize = args[1]
        zxjek__xxf.years = args[2]
        zxjek__xxf.months = args[3]
        zxjek__xxf.weeks = args[4]
        zxjek__xxf.days = args[5]
        zxjek__xxf.hours = args[6]
        zxjek__xxf.minutes = args[7]
        zxjek__xxf.seconds = args[8]
        zxjek__xxf.microseconds = args[9]
        zxjek__xxf.nanoseconds = args[10]
        zxjek__xxf.year = args[11]
        zxjek__xxf.month = args[12]
        zxjek__xxf.day = args[13]
        zxjek__xxf.weekday = args[14]
        zxjek__xxf.hour = args[15]
        zxjek__xxf.minute = args[16]
        zxjek__xxf.second = args[17]
        zxjek__xxf.microsecond = args[18]
        zxjek__xxf.nanosecond = args[19]
        zxjek__xxf.has_kws = args[20]
        return zxjek__xxf._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        ftzbb__erw = -1 if dateoffset.n < 0 else 1
        for urny__ldb in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += ftzbb__erw * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += ftzbb__erw * dateoffset._months
            year, month, oqlh__roi = calculate_month_end_date(year, month,
                day, 0)
            if day > oqlh__roi:
                day = oqlh__roi
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            if dateoffset._nanosecond != -1:
                nanosecond = dateoffset._nanosecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            mfogn__ncs = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            mfogn__ncs = mfogn__ncs + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if ftzbb__erw == -1:
                mfogn__ncs = -mfogn__ncs
            ts = ts + mfogn__ncs
            if dateoffset._weekday != -1:
                omu__qxv = ts.weekday()
                qxvup__dgo = (dateoffset._weekday - omu__qxv) % 7
                ts = ts + pd.Timedelta(days=qxvup__dgo)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        neo__bgilf = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, neo__bgilf)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        xfkfi__rikss = -1 if weekday is None else weekday
        return init_week(n, normalize, xfkfi__rikss)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        oox__fyyyv = cgutils.create_struct_proxy(typ)(context, builder)
        oox__fyyyv.n = args[0]
        oox__fyyyv.normalize = args[1]
        oox__fyyyv.weekday = args[2]
        return oox__fyyyv._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    oox__fyyyv = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    teyz__plgwh = c.pyapi.long_from_longlong(oox__fyyyv.n)
    uais__axg = c.pyapi.from_native_value(types.boolean, oox__fyyyv.
        normalize, c.env_manager)
    vnq__ept = c.pyapi.long_from_longlong(oox__fyyyv.weekday)
    pcgi__vxjel = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    amtlb__babhr = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), oox__fyyyv.weekday)
    with c.builder.if_else(amtlb__babhr) as (tusw__hwo, kncn__vusv):
        with tusw__hwo:
            nmqaf__slzg = c.pyapi.call_function_objargs(pcgi__vxjel, (
                teyz__plgwh, uais__axg, vnq__ept))
            ars__qwcv = c.builder.block
        with kncn__vusv:
            aho__aefd = c.pyapi.call_function_objargs(pcgi__vxjel, (
                teyz__plgwh, uais__axg))
            wxck__ntr = c.builder.block
    otjix__hlg = c.builder.phi(nmqaf__slzg.type)
    otjix__hlg.add_incoming(nmqaf__slzg, ars__qwcv)
    otjix__hlg.add_incoming(aho__aefd, wxck__ntr)
    c.pyapi.decref(vnq__ept)
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    c.pyapi.decref(pcgi__vxjel)
    return otjix__hlg


@unbox(WeekType)
def unbox_week(typ, val, c):
    teyz__plgwh = c.pyapi.object_getattr_string(val, 'n')
    uais__axg = c.pyapi.object_getattr_string(val, 'normalize')
    vnq__ept = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(teyz__plgwh)
    normalize = c.pyapi.to_native_value(types.bool_, uais__axg).value
    ngv__boyr = c.pyapi.make_none()
    xre__leaeo = c.builder.icmp_unsigned('==', vnq__ept, ngv__boyr)
    with c.builder.if_else(xre__leaeo) as (kncn__vusv, tusw__hwo):
        with tusw__hwo:
            nmqaf__slzg = c.pyapi.long_as_longlong(vnq__ept)
            ars__qwcv = c.builder.block
        with kncn__vusv:
            aho__aefd = lir.Constant(lir.IntType(64), -1)
            wxck__ntr = c.builder.block
    otjix__hlg = c.builder.phi(nmqaf__slzg.type)
    otjix__hlg.add_incoming(nmqaf__slzg, ars__qwcv)
    otjix__hlg.add_incoming(aho__aefd, wxck__ntr)
    oox__fyyyv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oox__fyyyv.n = n
    oox__fyyyv.normalize = normalize
    oox__fyyyv.weekday = otjix__hlg
    c.pyapi.decref(teyz__plgwh)
    c.pyapi.decref(uais__axg)
    c.pyapi.decref(vnq__ept)
    rmd__cvchq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(oox__fyyyv._getvalue(), is_error=rmd__cvchq)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            frfj__bcue = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                sawj__huims = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                sawj__huims = rhs
            return sawj__huims + frfj__bcue
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            frfj__bcue = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                sawj__huims = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                sawj__huims = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return sawj__huims + frfj__bcue
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            frfj__bcue = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + frfj__bcue
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        xloi__tpq = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=xloi__tpq)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for xlcw__uzn in date_offset_unsupported_attrs:
        sgyj__hxguk = 'pandas.tseries.offsets.DateOffset.' + xlcw__uzn
        overload_attribute(DateOffsetType, xlcw__uzn)(
            create_unsupported_overload(sgyj__hxguk))
    for xlcw__uzn in date_offset_unsupported:
        sgyj__hxguk = 'pandas.tseries.offsets.DateOffset.' + xlcw__uzn
        overload_method(DateOffsetType, xlcw__uzn)(create_unsupported_overload
            (sgyj__hxguk))


def _install_month_begin_unsupported():
    for xlcw__uzn in month_begin_unsupported_attrs:
        sgyj__hxguk = 'pandas.tseries.offsets.MonthBegin.' + xlcw__uzn
        overload_attribute(MonthBeginType, xlcw__uzn)(
            create_unsupported_overload(sgyj__hxguk))
    for xlcw__uzn in month_begin_unsupported:
        sgyj__hxguk = 'pandas.tseries.offsets.MonthBegin.' + xlcw__uzn
        overload_method(MonthBeginType, xlcw__uzn)(create_unsupported_overload
            (sgyj__hxguk))


def _install_month_end_unsupported():
    for xlcw__uzn in date_offset_unsupported_attrs:
        sgyj__hxguk = 'pandas.tseries.offsets.MonthEnd.' + xlcw__uzn
        overload_attribute(MonthEndType, xlcw__uzn)(create_unsupported_overload
            (sgyj__hxguk))
    for xlcw__uzn in date_offset_unsupported:
        sgyj__hxguk = 'pandas.tseries.offsets.MonthEnd.' + xlcw__uzn
        overload_method(MonthEndType, xlcw__uzn)(create_unsupported_overload
            (sgyj__hxguk))


def _install_week_unsupported():
    for xlcw__uzn in week_unsupported_attrs:
        sgyj__hxguk = 'pandas.tseries.offsets.Week.' + xlcw__uzn
        overload_attribute(WeekType, xlcw__uzn)(create_unsupported_overload
            (sgyj__hxguk))
    for xlcw__uzn in week_unsupported:
        sgyj__hxguk = 'pandas.tseries.offsets.Week.' + xlcw__uzn
        overload_method(WeekType, xlcw__uzn)(create_unsupported_overload(
            sgyj__hxguk))


def _install_offsets_unsupported():
    for nols__kofwt in offsets_unsupported:
        sgyj__hxguk = 'pandas.tseries.offsets.' + nols__kofwt.__name__
        overload(nols__kofwt)(create_unsupported_overload(sgyj__hxguk))


def _install_frequencies_unsupported():
    for nols__kofwt in frequencies_unsupported:
        sgyj__hxguk = 'pandas.tseries.frequencies.' + nols__kofwt.__name__
        overload(nols__kofwt)(create_unsupported_overload(sgyj__hxguk))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
