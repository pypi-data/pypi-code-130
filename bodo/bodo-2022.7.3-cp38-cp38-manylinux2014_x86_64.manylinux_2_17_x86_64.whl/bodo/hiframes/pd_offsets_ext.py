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
        ntagm__ieilw = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, ntagm__ieilw)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    vqrof__ofvx = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ioglv__fyg = c.pyapi.long_from_longlong(vqrof__ofvx.n)
    mibt__dgsit = c.pyapi.from_native_value(types.boolean, vqrof__ofvx.
        normalize, c.env_manager)
    mpr__boet = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    phmg__umta = c.pyapi.call_function_objargs(mpr__boet, (ioglv__fyg,
        mibt__dgsit))
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    c.pyapi.decref(mpr__boet)
    return phmg__umta


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    ioglv__fyg = c.pyapi.object_getattr_string(val, 'n')
    mibt__dgsit = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioglv__fyg)
    normalize = c.pyapi.to_native_value(types.bool_, mibt__dgsit).value
    vqrof__ofvx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vqrof__ofvx.n = n
    vqrof__ofvx.normalize = normalize
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    vdq__ekz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vqrof__ofvx._getvalue(), is_error=vdq__ekz)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        vqrof__ofvx = cgutils.create_struct_proxy(typ)(context, builder)
        vqrof__ofvx.n = args[0]
        vqrof__ofvx.normalize = args[1]
        return vqrof__ofvx._getvalue()
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
        ntagm__ieilw = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, ntagm__ieilw)


@box(MonthEndType)
def box_month_end(typ, val, c):
    mvgvu__mdqw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ioglv__fyg = c.pyapi.long_from_longlong(mvgvu__mdqw.n)
    mibt__dgsit = c.pyapi.from_native_value(types.boolean, mvgvu__mdqw.
        normalize, c.env_manager)
    xcxw__kipq = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    phmg__umta = c.pyapi.call_function_objargs(xcxw__kipq, (ioglv__fyg,
        mibt__dgsit))
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    c.pyapi.decref(xcxw__kipq)
    return phmg__umta


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    ioglv__fyg = c.pyapi.object_getattr_string(val, 'n')
    mibt__dgsit = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioglv__fyg)
    normalize = c.pyapi.to_native_value(types.bool_, mibt__dgsit).value
    mvgvu__mdqw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mvgvu__mdqw.n = n
    mvgvu__mdqw.normalize = normalize
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    vdq__ekz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mvgvu__mdqw._getvalue(), is_error=vdq__ekz)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        mvgvu__mdqw = cgutils.create_struct_proxy(typ)(context, builder)
        mvgvu__mdqw.n = args[0]
        mvgvu__mdqw.normalize = args[1]
        return mvgvu__mdqw._getvalue()
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
        mvgvu__mdqw = get_days_in_month(year, month)
        if mvgvu__mdqw > day:
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
        ntagm__ieilw = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, ntagm__ieilw)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    zcy__rlia = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    gcjwz__hdia = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for daf__ylymo, ukc__ghzn in enumerate(date_offset_fields):
        c.builder.store(getattr(zcy__rlia, ukc__ghzn), c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(gcjwz__hdia, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * daf__ylymo)), lir.IntType(64)
            .as_pointer()))
    rab__upma = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    zrnq__mlsx = cgutils.get_or_insert_function(c.builder.module, rab__upma,
        name='box_date_offset')
    ridu__nhia = c.builder.call(zrnq__mlsx, [zcy__rlia.n, zcy__rlia.
        normalize, gcjwz__hdia, zcy__rlia.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return ridu__nhia


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    ioglv__fyg = c.pyapi.object_getattr_string(val, 'n')
    mibt__dgsit = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioglv__fyg)
    normalize = c.pyapi.to_native_value(types.bool_, mibt__dgsit).value
    gcjwz__hdia = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    rab__upma = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    ddp__celho = cgutils.get_or_insert_function(c.builder.module, rab__upma,
        name='unbox_date_offset')
    has_kws = c.builder.call(ddp__celho, [val, gcjwz__hdia])
    zcy__rlia = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zcy__rlia.n = n
    zcy__rlia.normalize = normalize
    for daf__ylymo, ukc__ghzn in enumerate(date_offset_fields):
        setattr(zcy__rlia, ukc__ghzn, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(gcjwz__hdia, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * daf__ylymo)), lir.IntType(64)
            .as_pointer())))
    zcy__rlia.has_kws = has_kws
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    vdq__ekz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zcy__rlia._getvalue(), is_error=vdq__ekz)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    emc__twp = [n, normalize]
    has_kws = False
    awv__iqcax = [0] * 9 + [-1] * 9
    for daf__ylymo, ukc__ghzn in enumerate(date_offset_fields):
        if hasattr(pyval, ukc__ghzn):
            ictnq__wfua = context.get_constant(types.int64, getattr(pyval,
                ukc__ghzn))
            has_kws = True
        else:
            ictnq__wfua = context.get_constant(types.int64, awv__iqcax[
                daf__ylymo])
        emc__twp.append(ictnq__wfua)
    has_kws = context.get_constant(types.boolean, has_kws)
    emc__twp.append(has_kws)
    return lir.Constant.literal_struct(emc__twp)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    tric__iuf = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for rjry__jnov in tric__iuf:
        if not is_overload_none(rjry__jnov):
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
        zcy__rlia = cgutils.create_struct_proxy(typ)(context, builder)
        zcy__rlia.n = args[0]
        zcy__rlia.normalize = args[1]
        zcy__rlia.years = args[2]
        zcy__rlia.months = args[3]
        zcy__rlia.weeks = args[4]
        zcy__rlia.days = args[5]
        zcy__rlia.hours = args[6]
        zcy__rlia.minutes = args[7]
        zcy__rlia.seconds = args[8]
        zcy__rlia.microseconds = args[9]
        zcy__rlia.nanoseconds = args[10]
        zcy__rlia.year = args[11]
        zcy__rlia.month = args[12]
        zcy__rlia.day = args[13]
        zcy__rlia.weekday = args[14]
        zcy__rlia.hour = args[15]
        zcy__rlia.minute = args[16]
        zcy__rlia.second = args[17]
        zcy__rlia.microsecond = args[18]
        zcy__rlia.nanosecond = args[19]
        zcy__rlia.has_kws = args[20]
        return zcy__rlia._getvalue()
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
        dcdfe__rhj = -1 if dateoffset.n < 0 else 1
        for bgty__eyo in range(np.abs(dateoffset.n)):
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
            year += dcdfe__rhj * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += dcdfe__rhj * dateoffset._months
            year, month, lungl__vixnx = calculate_month_end_date(year,
                month, day, 0)
            if day > lungl__vixnx:
                day = lungl__vixnx
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
            tkezr__ncv = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            tkezr__ncv = tkezr__ncv + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if dcdfe__rhj == -1:
                tkezr__ncv = -tkezr__ncv
            ts = ts + tkezr__ncv
            if dateoffset._weekday != -1:
                inkz__cte = ts.weekday()
                tuzwq__pzdp = (dateoffset._weekday - inkz__cte) % 7
                ts = ts + pd.Timedelta(days=tuzwq__pzdp)
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
        ntagm__ieilw = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, ntagm__ieilw)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        ubilr__sju = -1 if weekday is None else weekday
        return init_week(n, normalize, ubilr__sju)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        ejm__mgl = cgutils.create_struct_proxy(typ)(context, builder)
        ejm__mgl.n = args[0]
        ejm__mgl.normalize = args[1]
        ejm__mgl.weekday = args[2]
        return ejm__mgl._getvalue()
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
    ejm__mgl = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    ioglv__fyg = c.pyapi.long_from_longlong(ejm__mgl.n)
    mibt__dgsit = c.pyapi.from_native_value(types.boolean, ejm__mgl.
        normalize, c.env_manager)
    fvnc__mht = c.pyapi.long_from_longlong(ejm__mgl.weekday)
    zhmmu__vjet = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    ldl__gao = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -1
        ), ejm__mgl.weekday)
    with c.builder.if_else(ldl__gao) as (noi__mkreo, aiu__dqgln):
        with noi__mkreo:
            srnkk__nyebn = c.pyapi.call_function_objargs(zhmmu__vjet, (
                ioglv__fyg, mibt__dgsit, fvnc__mht))
            hob__foyt = c.builder.block
        with aiu__dqgln:
            deacz__kbs = c.pyapi.call_function_objargs(zhmmu__vjet, (
                ioglv__fyg, mibt__dgsit))
            awct__kcl = c.builder.block
    phmg__umta = c.builder.phi(srnkk__nyebn.type)
    phmg__umta.add_incoming(srnkk__nyebn, hob__foyt)
    phmg__umta.add_incoming(deacz__kbs, awct__kcl)
    c.pyapi.decref(fvnc__mht)
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    c.pyapi.decref(zhmmu__vjet)
    return phmg__umta


@unbox(WeekType)
def unbox_week(typ, val, c):
    ioglv__fyg = c.pyapi.object_getattr_string(val, 'n')
    mibt__dgsit = c.pyapi.object_getattr_string(val, 'normalize')
    fvnc__mht = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(ioglv__fyg)
    normalize = c.pyapi.to_native_value(types.bool_, mibt__dgsit).value
    dlwy__iww = c.pyapi.make_none()
    tumgp__unzyn = c.builder.icmp_unsigned('==', fvnc__mht, dlwy__iww)
    with c.builder.if_else(tumgp__unzyn) as (aiu__dqgln, noi__mkreo):
        with noi__mkreo:
            srnkk__nyebn = c.pyapi.long_as_longlong(fvnc__mht)
            hob__foyt = c.builder.block
        with aiu__dqgln:
            deacz__kbs = lir.Constant(lir.IntType(64), -1)
            awct__kcl = c.builder.block
    phmg__umta = c.builder.phi(srnkk__nyebn.type)
    phmg__umta.add_incoming(srnkk__nyebn, hob__foyt)
    phmg__umta.add_incoming(deacz__kbs, awct__kcl)
    ejm__mgl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ejm__mgl.n = n
    ejm__mgl.normalize = normalize
    ejm__mgl.weekday = phmg__umta
    c.pyapi.decref(ioglv__fyg)
    c.pyapi.decref(mibt__dgsit)
    c.pyapi.decref(fvnc__mht)
    vdq__ekz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ejm__mgl._getvalue(), is_error=vdq__ekz)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            aefr__vfp = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                dhfd__nps = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                dhfd__nps = rhs
            return dhfd__nps + aefr__vfp
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            aefr__vfp = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                dhfd__nps = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                dhfd__nps = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return dhfd__nps + aefr__vfp
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            aefr__vfp = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + aefr__vfp
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
        rqm__vcdqb = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=rqm__vcdqb)


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
    for owy__xcza in date_offset_unsupported_attrs:
        kbm__xoxwt = 'pandas.tseries.offsets.DateOffset.' + owy__xcza
        overload_attribute(DateOffsetType, owy__xcza)(
            create_unsupported_overload(kbm__xoxwt))
    for owy__xcza in date_offset_unsupported:
        kbm__xoxwt = 'pandas.tseries.offsets.DateOffset.' + owy__xcza
        overload_method(DateOffsetType, owy__xcza)(create_unsupported_overload
            (kbm__xoxwt))


def _install_month_begin_unsupported():
    for owy__xcza in month_begin_unsupported_attrs:
        kbm__xoxwt = 'pandas.tseries.offsets.MonthBegin.' + owy__xcza
        overload_attribute(MonthBeginType, owy__xcza)(
            create_unsupported_overload(kbm__xoxwt))
    for owy__xcza in month_begin_unsupported:
        kbm__xoxwt = 'pandas.tseries.offsets.MonthBegin.' + owy__xcza
        overload_method(MonthBeginType, owy__xcza)(create_unsupported_overload
            (kbm__xoxwt))


def _install_month_end_unsupported():
    for owy__xcza in date_offset_unsupported_attrs:
        kbm__xoxwt = 'pandas.tseries.offsets.MonthEnd.' + owy__xcza
        overload_attribute(MonthEndType, owy__xcza)(create_unsupported_overload
            (kbm__xoxwt))
    for owy__xcza in date_offset_unsupported:
        kbm__xoxwt = 'pandas.tseries.offsets.MonthEnd.' + owy__xcza
        overload_method(MonthEndType, owy__xcza)(create_unsupported_overload
            (kbm__xoxwt))


def _install_week_unsupported():
    for owy__xcza in week_unsupported_attrs:
        kbm__xoxwt = 'pandas.tseries.offsets.Week.' + owy__xcza
        overload_attribute(WeekType, owy__xcza)(create_unsupported_overload
            (kbm__xoxwt))
    for owy__xcza in week_unsupported:
        kbm__xoxwt = 'pandas.tseries.offsets.Week.' + owy__xcza
        overload_method(WeekType, owy__xcza)(create_unsupported_overload(
            kbm__xoxwt))


def _install_offsets_unsupported():
    for ictnq__wfua in offsets_unsupported:
        kbm__xoxwt = 'pandas.tseries.offsets.' + ictnq__wfua.__name__
        overload(ictnq__wfua)(create_unsupported_overload(kbm__xoxwt))


def _install_frequencies_unsupported():
    for ictnq__wfua in frequencies_unsupported:
        kbm__xoxwt = 'pandas.tseries.frequencies.' + ictnq__wfua.__name__
        overload(ictnq__wfua)(create_unsupported_overload(kbm__xoxwt))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
