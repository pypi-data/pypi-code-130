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
        uetdw__dll = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, uetdw__dll)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    vvytl__dagt = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yawp__dqe = c.pyapi.long_from_longlong(vvytl__dagt.n)
    wjf__bpss = c.pyapi.from_native_value(types.boolean, vvytl__dagt.
        normalize, c.env_manager)
    mdev__voklf = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    hcip__amkko = c.pyapi.call_function_objargs(mdev__voklf, (yawp__dqe,
        wjf__bpss))
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    c.pyapi.decref(mdev__voklf)
    return hcip__amkko


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    yawp__dqe = c.pyapi.object_getattr_string(val, 'n')
    wjf__bpss = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yawp__dqe)
    normalize = c.pyapi.to_native_value(types.bool_, wjf__bpss).value
    vvytl__dagt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vvytl__dagt.n = n
    vvytl__dagt.normalize = normalize
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    mehc__fitfj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vvytl__dagt._getvalue(), is_error=mehc__fitfj)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        vvytl__dagt = cgutils.create_struct_proxy(typ)(context, builder)
        vvytl__dagt.n = args[0]
        vvytl__dagt.normalize = args[1]
        return vvytl__dagt._getvalue()
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
        uetdw__dll = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, uetdw__dll)


@box(MonthEndType)
def box_month_end(typ, val, c):
    zyvfl__hoj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yawp__dqe = c.pyapi.long_from_longlong(zyvfl__hoj.n)
    wjf__bpss = c.pyapi.from_native_value(types.boolean, zyvfl__hoj.
        normalize, c.env_manager)
    icgr__dywa = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    hcip__amkko = c.pyapi.call_function_objargs(icgr__dywa, (yawp__dqe,
        wjf__bpss))
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    c.pyapi.decref(icgr__dywa)
    return hcip__amkko


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    yawp__dqe = c.pyapi.object_getattr_string(val, 'n')
    wjf__bpss = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yawp__dqe)
    normalize = c.pyapi.to_native_value(types.bool_, wjf__bpss).value
    zyvfl__hoj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zyvfl__hoj.n = n
    zyvfl__hoj.normalize = normalize
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    mehc__fitfj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zyvfl__hoj._getvalue(), is_error=mehc__fitfj)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        zyvfl__hoj = cgutils.create_struct_proxy(typ)(context, builder)
        zyvfl__hoj.n = args[0]
        zyvfl__hoj.normalize = args[1]
        return zyvfl__hoj._getvalue()
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
        zyvfl__hoj = get_days_in_month(year, month)
        if zyvfl__hoj > day:
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
        uetdw__dll = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, uetdw__dll)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    qivm__bwbln = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    baaj__utzu = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for ldh__byxqn, gsx__eab in enumerate(date_offset_fields):
        c.builder.store(getattr(qivm__bwbln, gsx__eab), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(baaj__utzu, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * ldh__byxqn)), lir.IntType(64)
            .as_pointer()))
    nminn__pkhv = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    yzlu__wpfx = cgutils.get_or_insert_function(c.builder.module,
        nminn__pkhv, name='box_date_offset')
    shuui__ciqak = c.builder.call(yzlu__wpfx, [qivm__bwbln.n, qivm__bwbln.
        normalize, baaj__utzu, qivm__bwbln.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return shuui__ciqak


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    yawp__dqe = c.pyapi.object_getattr_string(val, 'n')
    wjf__bpss = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yawp__dqe)
    normalize = c.pyapi.to_native_value(types.bool_, wjf__bpss).value
    baaj__utzu = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    nminn__pkhv = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    pyf__arstr = cgutils.get_or_insert_function(c.builder.module,
        nminn__pkhv, name='unbox_date_offset')
    has_kws = c.builder.call(pyf__arstr, [val, baaj__utzu])
    qivm__bwbln = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qivm__bwbln.n = n
    qivm__bwbln.normalize = normalize
    for ldh__byxqn, gsx__eab in enumerate(date_offset_fields):
        setattr(qivm__bwbln, gsx__eab, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(baaj__utzu, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * ldh__byxqn)), lir.IntType(64)
            .as_pointer())))
    qivm__bwbln.has_kws = has_kws
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    mehc__fitfj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qivm__bwbln._getvalue(), is_error=mehc__fitfj)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    zan__tpo = [n, normalize]
    has_kws = False
    ewrix__lyp = [0] * 9 + [-1] * 9
    for ldh__byxqn, gsx__eab in enumerate(date_offset_fields):
        if hasattr(pyval, gsx__eab):
            fnj__fuly = context.get_constant(types.int64, getattr(pyval,
                gsx__eab))
            has_kws = True
        else:
            fnj__fuly = context.get_constant(types.int64, ewrix__lyp[
                ldh__byxqn])
        zan__tpo.append(fnj__fuly)
    has_kws = context.get_constant(types.boolean, has_kws)
    zan__tpo.append(has_kws)
    return lir.Constant.literal_struct(zan__tpo)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    ter__jfce = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for wdkh__btn in ter__jfce:
        if not is_overload_none(wdkh__btn):
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
        qivm__bwbln = cgutils.create_struct_proxy(typ)(context, builder)
        qivm__bwbln.n = args[0]
        qivm__bwbln.normalize = args[1]
        qivm__bwbln.years = args[2]
        qivm__bwbln.months = args[3]
        qivm__bwbln.weeks = args[4]
        qivm__bwbln.days = args[5]
        qivm__bwbln.hours = args[6]
        qivm__bwbln.minutes = args[7]
        qivm__bwbln.seconds = args[8]
        qivm__bwbln.microseconds = args[9]
        qivm__bwbln.nanoseconds = args[10]
        qivm__bwbln.year = args[11]
        qivm__bwbln.month = args[12]
        qivm__bwbln.day = args[13]
        qivm__bwbln.weekday = args[14]
        qivm__bwbln.hour = args[15]
        qivm__bwbln.minute = args[16]
        qivm__bwbln.second = args[17]
        qivm__bwbln.microsecond = args[18]
        qivm__bwbln.nanosecond = args[19]
        qivm__bwbln.has_kws = args[20]
        return qivm__bwbln._getvalue()
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
        znqub__bbbc = -1 if dateoffset.n < 0 else 1
        for ljqv__kde in range(np.abs(dateoffset.n)):
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
            year += znqub__bbbc * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += znqub__bbbc * dateoffset._months
            year, month, etzvf__uwwqt = calculate_month_end_date(year,
                month, day, 0)
            if day > etzvf__uwwqt:
                day = etzvf__uwwqt
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
            frwd__yykz = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            frwd__yykz = frwd__yykz + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if znqub__bbbc == -1:
                frwd__yykz = -frwd__yykz
            ts = ts + frwd__yykz
            if dateoffset._weekday != -1:
                jhflt__rbx = ts.weekday()
                juxc__lqpj = (dateoffset._weekday - jhflt__rbx) % 7
                ts = ts + pd.Timedelta(days=juxc__lqpj)
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
        uetdw__dll = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, uetdw__dll)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        uiv__dgs = -1 if weekday is None else weekday
        return init_week(n, normalize, uiv__dgs)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        rvf__xfscx = cgutils.create_struct_proxy(typ)(context, builder)
        rvf__xfscx.n = args[0]
        rvf__xfscx.normalize = args[1]
        rvf__xfscx.weekday = args[2]
        return rvf__xfscx._getvalue()
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
    rvf__xfscx = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yawp__dqe = c.pyapi.long_from_longlong(rvf__xfscx.n)
    wjf__bpss = c.pyapi.from_native_value(types.boolean, rvf__xfscx.
        normalize, c.env_manager)
    cfgby__pky = c.pyapi.long_from_longlong(rvf__xfscx.weekday)
    scb__ahmt = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    xmmrh__wczrq = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), rvf__xfscx.weekday)
    with c.builder.if_else(xmmrh__wczrq) as (vnrm__lqda, qgumm__gfr):
        with vnrm__lqda:
            hpqwd__zkjw = c.pyapi.call_function_objargs(scb__ahmt, (
                yawp__dqe, wjf__bpss, cfgby__pky))
            xidp__xte = c.builder.block
        with qgumm__gfr:
            xhg__rql = c.pyapi.call_function_objargs(scb__ahmt, (yawp__dqe,
                wjf__bpss))
            tiycf__gepd = c.builder.block
    hcip__amkko = c.builder.phi(hpqwd__zkjw.type)
    hcip__amkko.add_incoming(hpqwd__zkjw, xidp__xte)
    hcip__amkko.add_incoming(xhg__rql, tiycf__gepd)
    c.pyapi.decref(cfgby__pky)
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    c.pyapi.decref(scb__ahmt)
    return hcip__amkko


@unbox(WeekType)
def unbox_week(typ, val, c):
    yawp__dqe = c.pyapi.object_getattr_string(val, 'n')
    wjf__bpss = c.pyapi.object_getattr_string(val, 'normalize')
    cfgby__pky = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(yawp__dqe)
    normalize = c.pyapi.to_native_value(types.bool_, wjf__bpss).value
    zknbc__sujg = c.pyapi.make_none()
    eam__lqrd = c.builder.icmp_unsigned('==', cfgby__pky, zknbc__sujg)
    with c.builder.if_else(eam__lqrd) as (qgumm__gfr, vnrm__lqda):
        with vnrm__lqda:
            hpqwd__zkjw = c.pyapi.long_as_longlong(cfgby__pky)
            xidp__xte = c.builder.block
        with qgumm__gfr:
            xhg__rql = lir.Constant(lir.IntType(64), -1)
            tiycf__gepd = c.builder.block
    hcip__amkko = c.builder.phi(hpqwd__zkjw.type)
    hcip__amkko.add_incoming(hpqwd__zkjw, xidp__xte)
    hcip__amkko.add_incoming(xhg__rql, tiycf__gepd)
    rvf__xfscx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rvf__xfscx.n = n
    rvf__xfscx.normalize = normalize
    rvf__xfscx.weekday = hcip__amkko
    c.pyapi.decref(yawp__dqe)
    c.pyapi.decref(wjf__bpss)
    c.pyapi.decref(cfgby__pky)
    mehc__fitfj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rvf__xfscx._getvalue(), is_error=mehc__fitfj)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            zlhgz__oqnfs = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                uirin__bhu = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                uirin__bhu = rhs
            return uirin__bhu + zlhgz__oqnfs
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            zlhgz__oqnfs = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                uirin__bhu = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                uirin__bhu = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return uirin__bhu + zlhgz__oqnfs
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            zlhgz__oqnfs = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            return rhs + zlhgz__oqnfs
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
        vjavr__jpx = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=vjavr__jpx)


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
    for mec__agt in date_offset_unsupported_attrs:
        vqf__ipkq = 'pandas.tseries.offsets.DateOffset.' + mec__agt
        overload_attribute(DateOffsetType, mec__agt)(
            create_unsupported_overload(vqf__ipkq))
    for mec__agt in date_offset_unsupported:
        vqf__ipkq = 'pandas.tseries.offsets.DateOffset.' + mec__agt
        overload_method(DateOffsetType, mec__agt)(create_unsupported_overload
            (vqf__ipkq))


def _install_month_begin_unsupported():
    for mec__agt in month_begin_unsupported_attrs:
        vqf__ipkq = 'pandas.tseries.offsets.MonthBegin.' + mec__agt
        overload_attribute(MonthBeginType, mec__agt)(
            create_unsupported_overload(vqf__ipkq))
    for mec__agt in month_begin_unsupported:
        vqf__ipkq = 'pandas.tseries.offsets.MonthBegin.' + mec__agt
        overload_method(MonthBeginType, mec__agt)(create_unsupported_overload
            (vqf__ipkq))


def _install_month_end_unsupported():
    for mec__agt in date_offset_unsupported_attrs:
        vqf__ipkq = 'pandas.tseries.offsets.MonthEnd.' + mec__agt
        overload_attribute(MonthEndType, mec__agt)(create_unsupported_overload
            (vqf__ipkq))
    for mec__agt in date_offset_unsupported:
        vqf__ipkq = 'pandas.tseries.offsets.MonthEnd.' + mec__agt
        overload_method(MonthEndType, mec__agt)(create_unsupported_overload
            (vqf__ipkq))


def _install_week_unsupported():
    for mec__agt in week_unsupported_attrs:
        vqf__ipkq = 'pandas.tseries.offsets.Week.' + mec__agt
        overload_attribute(WeekType, mec__agt)(create_unsupported_overload(
            vqf__ipkq))
    for mec__agt in week_unsupported:
        vqf__ipkq = 'pandas.tseries.offsets.Week.' + mec__agt
        overload_method(WeekType, mec__agt)(create_unsupported_overload(
            vqf__ipkq))


def _install_offsets_unsupported():
    for fnj__fuly in offsets_unsupported:
        vqf__ipkq = 'pandas.tseries.offsets.' + fnj__fuly.__name__
        overload(fnj__fuly)(create_unsupported_overload(vqf__ipkq))


def _install_frequencies_unsupported():
    for fnj__fuly in frequencies_unsupported:
        vqf__ipkq = 'pandas.tseries.frequencies.' + fnj__fuly.__name__
        overload(fnj__fuly)(create_unsupported_overload(vqf__ipkq))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
