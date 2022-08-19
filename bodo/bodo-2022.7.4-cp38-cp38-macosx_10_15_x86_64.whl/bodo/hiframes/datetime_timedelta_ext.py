"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iyrfz__bkcgn = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, iyrfz__bkcgn)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    kkm__nevl = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ieb__bglgf = c.pyapi.long_from_longlong(kkm__nevl.value)
    cszj__aes = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(cszj__aes, (ieb__bglgf,))
    c.pyapi.decref(ieb__bglgf)
    c.pyapi.decref(cszj__aes)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    ieb__bglgf = c.pyapi.object_getattr_string(val, 'value')
    vonsq__kncph = c.pyapi.long_as_longlong(ieb__bglgf)
    kkm__nevl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kkm__nevl.value = vonsq__kncph
    c.pyapi.decref(ieb__bglgf)
    aolfn__bec = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kkm__nevl._getvalue(), is_error=aolfn__bec)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            zfcr__cbbt = 1000 * microseconds
            return init_pd_timedelta(zfcr__cbbt)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            zfcr__cbbt = 1000 * microseconds
            return init_pd_timedelta(zfcr__cbbt)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    sffu__fff, giiz__wwly = pd._libs.tslibs.conversion.precision_from_unit(unit
        )

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * sffu__fff)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            kgm__dvxsd = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + kgm__dvxsd
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ptfv__dyzg = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = ptfv__dyzg + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            qgusn__kvlb = rhs.toordinal()
            hms__qffi = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            bgikf__vcmg = rhs.microsecond
            hoqb__jcoi = lhs.value // 1000
            meysf__uweme = lhs.nanoseconds
            wadgh__vcc = bgikf__vcmg + hoqb__jcoi
            pltws__vzo = 1000000 * (qgusn__kvlb * 86400 + hms__qffi
                ) + wadgh__vcc
            nrn__gqsjz = meysf__uweme
            return compute_pd_timestamp(pltws__vzo, nrn__gqsjz)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            nxl__opii = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            nxl__opii = nxl__opii + lhs
            zey__auw, jvlb__brp = divmod(nxl__opii.seconds, 3600)
            efe__xjr, cqubk__mqxvy = divmod(jvlb__brp, 60)
            if 0 < nxl__opii.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(nxl__opii
                    .days)
                return datetime.datetime(d.year, d.month, d.day, zey__auw,
                    efe__xjr, cqubk__mqxvy, nxl__opii.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            nxl__opii = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            nxl__opii = nxl__opii + rhs
            zey__auw, jvlb__brp = divmod(nxl__opii.seconds, 3600)
            efe__xjr, cqubk__mqxvy = divmod(jvlb__brp, 60)
            if 0 < nxl__opii.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(nxl__opii
                    .days)
                return datetime.datetime(d.year, d.month, d.day, zey__auw,
                    efe__xjr, cqubk__mqxvy, nxl__opii.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ujhuq__kfa = lhs.value - rhs.value
            return pd.Timedelta(ujhuq__kfa)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            lcoul__irrr = lhs
            numba.parfors.parfor.init_prange()
            n = len(lcoul__irrr)
            A = alloc_datetime_timedelta_array(n)
            for mfhr__azuql in numba.parfors.parfor.internal_prange(n):
                A[mfhr__azuql] = lcoul__irrr[mfhr__azuql] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            sdrpc__jvjc = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, sdrpc__jvjc)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ykvzc__xxgq, sdrpc__jvjc = divmod(lhs.value, rhs.value)
            return ykvzc__xxgq, pd.Timedelta(sdrpc__jvjc)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iyrfz__bkcgn = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, iyrfz__bkcgn
            )


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    kkm__nevl = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    gvxb__osjqt = c.pyapi.long_from_longlong(kkm__nevl.days)
    flkdf__krdj = c.pyapi.long_from_longlong(kkm__nevl.seconds)
    hfw__wsxcu = c.pyapi.long_from_longlong(kkm__nevl.microseconds)
    cszj__aes = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(cszj__aes, (gvxb__osjqt,
        flkdf__krdj, hfw__wsxcu))
    c.pyapi.decref(gvxb__osjqt)
    c.pyapi.decref(flkdf__krdj)
    c.pyapi.decref(hfw__wsxcu)
    c.pyapi.decref(cszj__aes)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    gvxb__osjqt = c.pyapi.object_getattr_string(val, 'days')
    flkdf__krdj = c.pyapi.object_getattr_string(val, 'seconds')
    hfw__wsxcu = c.pyapi.object_getattr_string(val, 'microseconds')
    jnint__xxc = c.pyapi.long_as_longlong(gvxb__osjqt)
    iiki__rgdi = c.pyapi.long_as_longlong(flkdf__krdj)
    ykzmc__swpa = c.pyapi.long_as_longlong(hfw__wsxcu)
    kkm__nevl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kkm__nevl.days = jnint__xxc
    kkm__nevl.seconds = iiki__rgdi
    kkm__nevl.microseconds = ykzmc__swpa
    c.pyapi.decref(gvxb__osjqt)
    c.pyapi.decref(flkdf__krdj)
    c.pyapi.decref(hfw__wsxcu)
    aolfn__bec = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kkm__nevl._getvalue(), is_error=aolfn__bec)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    ykvzc__xxgq, sdrpc__jvjc = divmod(a, b)
    sdrpc__jvjc *= 2
    umeh__qze = sdrpc__jvjc > b if b > 0 else sdrpc__jvjc < b
    if umeh__qze or sdrpc__jvjc == b and ykvzc__xxgq % 2 == 1:
        ykvzc__xxgq += 1
    return ykvzc__xxgq


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                zpii__xwn = _cmp(_getstate(lhs), _getstate(rhs))
                return op(zpii__xwn, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ykvzc__xxgq, sdrpc__jvjc = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return ykvzc__xxgq, datetime.timedelta(0, 0, sdrpc__jvjc)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    oxrmq__asyzy = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != oxrmq__asyzy
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        iyrfz__bkcgn = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, iyrfz__bkcgn)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    laeqa__upvsz = types.Array(types.intp, 1, 'C')
    pxmpv__qdji = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        laeqa__upvsz, [n])
    ztsl__oyn = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        laeqa__upvsz, [n])
    chil__rpglg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        laeqa__upvsz, [n])
    zqe__eibb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    cny__kjpp = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [zqe__eibb])
    sryw__fojha = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    pmfa__uuqzl = cgutils.get_or_insert_function(c.builder.module,
        sryw__fojha, name='unbox_datetime_timedelta_array')
    c.builder.call(pmfa__uuqzl, [val, n, pxmpv__qdji.data, ztsl__oyn.data,
        chil__rpglg.data, cny__kjpp.data])
    kfqln__nzwt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kfqln__nzwt.days_data = pxmpv__qdji._getvalue()
    kfqln__nzwt.seconds_data = ztsl__oyn._getvalue()
    kfqln__nzwt.microseconds_data = chil__rpglg._getvalue()
    kfqln__nzwt.null_bitmap = cny__kjpp._getvalue()
    aolfn__bec = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kfqln__nzwt._getvalue(), is_error=aolfn__bec)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    lcoul__irrr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    pxmpv__qdji = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, lcoul__irrr.days_data)
    ztsl__oyn = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, lcoul__irrr.seconds_data).data
    chil__rpglg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, lcoul__irrr.microseconds_data).data
    jihyk__kulzp = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, lcoul__irrr.null_bitmap).data
    n = c.builder.extract_value(pxmpv__qdji.shape, 0)
    sryw__fojha = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    sud__sunc = cgutils.get_or_insert_function(c.builder.module,
        sryw__fojha, name='box_datetime_timedelta_array')
    befgg__wxxl = c.builder.call(sud__sunc, [n, pxmpv__qdji.data, ztsl__oyn,
        chil__rpglg, jihyk__kulzp])
    c.context.nrt.decref(c.builder, typ, val)
    return befgg__wxxl


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        yzx__plwjf, pxv__qfjgt, kpk__mdbdk, wdtl__adugo = args
        oliun__hea = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        oliun__hea.days_data = yzx__plwjf
        oliun__hea.seconds_data = pxv__qfjgt
        oliun__hea.microseconds_data = kpk__mdbdk
        oliun__hea.null_bitmap = wdtl__adugo
        context.nrt.incref(builder, signature.args[0], yzx__plwjf)
        context.nrt.incref(builder, signature.args[1], pxv__qfjgt)
        context.nrt.incref(builder, signature.args[2], kpk__mdbdk)
        context.nrt.incref(builder, signature.args[3], wdtl__adugo)
        return oliun__hea._getvalue()
    gnj__iao = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return gnj__iao, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    pxmpv__qdji = np.empty(n, np.int64)
    ztsl__oyn = np.empty(n, np.int64)
    chil__rpglg = np.empty(n, np.int64)
    ntbn__phy = np.empty(n + 7 >> 3, np.uint8)
    for mfhr__azuql, s in enumerate(pyval):
        ymhql__ckz = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ntbn__phy, mfhr__azuql, int(
            not ymhql__ckz))
        if not ymhql__ckz:
            pxmpv__qdji[mfhr__azuql] = s.days
            ztsl__oyn[mfhr__azuql] = s.seconds
            chil__rpglg[mfhr__azuql] = s.microseconds
    swv__wgw = context.get_constant_generic(builder, days_data_type,
        pxmpv__qdji)
    mrrce__uovl = context.get_constant_generic(builder, seconds_data_type,
        ztsl__oyn)
    cqbb__cgs = context.get_constant_generic(builder,
        microseconds_data_type, chil__rpglg)
    ztl__jcp = context.get_constant_generic(builder, nulls_type, ntbn__phy)
    return lir.Constant.literal_struct([swv__wgw, mrrce__uovl, cqbb__cgs,
        ztl__jcp])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    pxmpv__qdji = np.empty(n, dtype=np.int64)
    ztsl__oyn = np.empty(n, dtype=np.int64)
    chil__rpglg = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(pxmpv__qdji, ztsl__oyn,
        chil__rpglg, nulls)


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            cqv__inexl = bodo.utils.conversion.coerce_to_ndarray(ind)
            pae__esoq = A._null_bitmap
            tln__rrrof = A._days_data[cqv__inexl]
            txfbi__ohv = A._seconds_data[cqv__inexl]
            htz__rrvki = A._microseconds_data[cqv__inexl]
            n = len(tln__rrrof)
            qxd__pfx = get_new_null_mask_bool_index(pae__esoq, ind, n)
            return init_datetime_timedelta_array(tln__rrrof, txfbi__ohv,
                htz__rrvki, qxd__pfx)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            cqv__inexl = bodo.utils.conversion.coerce_to_ndarray(ind)
            pae__esoq = A._null_bitmap
            tln__rrrof = A._days_data[cqv__inexl]
            txfbi__ohv = A._seconds_data[cqv__inexl]
            htz__rrvki = A._microseconds_data[cqv__inexl]
            n = len(tln__rrrof)
            qxd__pfx = get_new_null_mask_int_index(pae__esoq, cqv__inexl, n)
            return init_datetime_timedelta_array(tln__rrrof, txfbi__ohv,
                htz__rrvki, qxd__pfx)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            pae__esoq = A._null_bitmap
            tln__rrrof = np.ascontiguousarray(A._days_data[ind])
            txfbi__ohv = np.ascontiguousarray(A._seconds_data[ind])
            htz__rrvki = np.ascontiguousarray(A._microseconds_data[ind])
            qxd__pfx = get_new_null_mask_slice_index(pae__esoq, ind, n)
            return init_datetime_timedelta_array(tln__rrrof, txfbi__ohv,
                htz__rrvki, qxd__pfx)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    qbwgd__xtx = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(qbwgd__xtx)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(qbwgd__xtx)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for mfhr__azuql in range(n):
                    A._days_data[ind[mfhr__azuql]] = val._days
                    A._seconds_data[ind[mfhr__azuql]] = val._seconds
                    A._microseconds_data[ind[mfhr__azuql]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[mfhr__azuql], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for mfhr__azuql in range(n):
                    A._days_data[ind[mfhr__azuql]] = val._days_data[mfhr__azuql
                        ]
                    A._seconds_data[ind[mfhr__azuql]] = val._seconds_data[
                        mfhr__azuql]
                    A._microseconds_data[ind[mfhr__azuql]
                        ] = val._microseconds_data[mfhr__azuql]
                    bnsv__imaj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, mfhr__azuql)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[mfhr__azuql], bnsv__imaj)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for mfhr__azuql in range(n):
                    if not bodo.libs.array_kernels.isna(ind, mfhr__azuql
                        ) and ind[mfhr__azuql]:
                        A._days_data[mfhr__azuql] = val._days
                        A._seconds_data[mfhr__azuql] = val._seconds
                        A._microseconds_data[mfhr__azuql] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            mfhr__azuql, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                recjq__buyhi = 0
                for mfhr__azuql in range(n):
                    if not bodo.libs.array_kernels.isna(ind, mfhr__azuql
                        ) and ind[mfhr__azuql]:
                        A._days_data[mfhr__azuql] = val._days_data[recjq__buyhi
                            ]
                        A._seconds_data[mfhr__azuql] = val._seconds_data[
                            recjq__buyhi]
                        A._microseconds_data[mfhr__azuql
                            ] = val._microseconds_data[recjq__buyhi]
                        bnsv__imaj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, recjq__buyhi)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            mfhr__azuql, bnsv__imaj)
                        recjq__buyhi += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                gafas__qnzx = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for mfhr__azuql in range(gafas__qnzx.start, gafas__qnzx.
                    stop, gafas__qnzx.step):
                    A._days_data[mfhr__azuql] = val._days
                    A._seconds_data[mfhr__azuql] = val._seconds
                    A._microseconds_data[mfhr__azuql] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        mfhr__azuql, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                upavp__uitq = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, upavp__uitq,
                    ind, n)
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            lcoul__irrr = arg1
            numba.parfors.parfor.init_prange()
            n = len(lcoul__irrr)
            A = alloc_datetime_timedelta_array(n)
            for mfhr__azuql in numba.parfors.parfor.internal_prange(n):
                A[mfhr__azuql] = lcoul__irrr[mfhr__azuql] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            kdm__xflxf = True
        else:
            kdm__xflxf = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                cpak__jfd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for mfhr__azuql in numba.parfors.parfor.internal_prange(n):
                    nxdu__hgh = bodo.libs.array_kernels.isna(lhs, mfhr__azuql)
                    gmv__ovih = bodo.libs.array_kernels.isna(rhs, mfhr__azuql)
                    if nxdu__hgh or gmv__ovih:
                        xko__mgjqc = kdm__xflxf
                    else:
                        xko__mgjqc = op(lhs[mfhr__azuql], rhs[mfhr__azuql])
                    cpak__jfd[mfhr__azuql] = xko__mgjqc
                return cpak__jfd
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                cpak__jfd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for mfhr__azuql in numba.parfors.parfor.internal_prange(n):
                    bnsv__imaj = bodo.libs.array_kernels.isna(lhs, mfhr__azuql)
                    if bnsv__imaj:
                        xko__mgjqc = kdm__xflxf
                    else:
                        xko__mgjqc = op(lhs[mfhr__azuql], rhs)
                    cpak__jfd[mfhr__azuql] = xko__mgjqc
                return cpak__jfd
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                cpak__jfd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for mfhr__azuql in numba.parfors.parfor.internal_prange(n):
                    bnsv__imaj = bodo.libs.array_kernels.isna(rhs, mfhr__azuql)
                    if bnsv__imaj:
                        xko__mgjqc = kdm__xflxf
                    else:
                        xko__mgjqc = op(lhs, rhs[mfhr__azuql])
                    cpak__jfd[mfhr__azuql] = xko__mgjqc
                return cpak__jfd
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for bhvcs__jisn in timedelta_unsupported_attrs:
        pbur__icjz = 'pandas.Timedelta.' + bhvcs__jisn
        overload_attribute(PDTimeDeltaType, bhvcs__jisn)(
            create_unsupported_overload(pbur__icjz))
    for nhy__bqby in timedelta_unsupported_methods:
        pbur__icjz = 'pandas.Timedelta.' + nhy__bqby
        overload_method(PDTimeDeltaType, nhy__bqby)(create_unsupported_overload
            (pbur__icjz + '()'))


_intstall_pd_timedelta_unsupported()
