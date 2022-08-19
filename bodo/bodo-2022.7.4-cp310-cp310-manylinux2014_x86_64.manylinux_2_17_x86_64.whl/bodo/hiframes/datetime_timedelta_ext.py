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
        ywxw__rjlt = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, ywxw__rjlt)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    mddkp__ffgr = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    skx__esegm = c.pyapi.long_from_longlong(mddkp__ffgr.value)
    rbbc__cwxcq = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(rbbc__cwxcq, (skx__esegm,))
    c.pyapi.decref(skx__esegm)
    c.pyapi.decref(rbbc__cwxcq)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    skx__esegm = c.pyapi.object_getattr_string(val, 'value')
    qkz__phk = c.pyapi.long_as_longlong(skx__esegm)
    mddkp__ffgr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mddkp__ffgr.value = qkz__phk
    c.pyapi.decref(skx__esegm)
    obnap__wnc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mddkp__ffgr._getvalue(), is_error=obnap__wnc)


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
            gqii__hgnw = 1000 * microseconds
            return init_pd_timedelta(gqii__hgnw)
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
            gqii__hgnw = 1000 * microseconds
            return init_pd_timedelta(gqii__hgnw)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    cre__usqct, peo__wkboz = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * cre__usqct)
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
            hcs__vhmkw = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + hcs__vhmkw
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            hbqxr__uufpy = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = hbqxr__uufpy + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            kuw__oft = rhs.toordinal()
            kxk__hriu = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            yic__gigal = rhs.microsecond
            ynxo__liwp = lhs.value // 1000
            idyn__bwbmv = lhs.nanoseconds
            afwr__blcxz = yic__gigal + ynxo__liwp
            uwrj__yzdd = 1000000 * (kuw__oft * 86400 + kxk__hriu) + afwr__blcxz
            cay__sndce = idyn__bwbmv
            return compute_pd_timestamp(uwrj__yzdd, cay__sndce)
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
            pbz__pege = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            pbz__pege = pbz__pege + lhs
            qqqeu__woypg, qnz__kfki = divmod(pbz__pege.seconds, 3600)
            uaeqp__vxl, jwb__xjy = divmod(qnz__kfki, 60)
            if 0 < pbz__pege.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(pbz__pege
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    qqqeu__woypg, uaeqp__vxl, jwb__xjy, pbz__pege.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            pbz__pege = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            pbz__pege = pbz__pege + rhs
            qqqeu__woypg, qnz__kfki = divmod(pbz__pege.seconds, 3600)
            uaeqp__vxl, jwb__xjy = divmod(qnz__kfki, 60)
            if 0 < pbz__pege.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(pbz__pege
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    qqqeu__woypg, uaeqp__vxl, jwb__xjy, pbz__pege.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            aylh__odz = lhs.value - rhs.value
            return pd.Timedelta(aylh__odz)
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
            hnl__ciys = lhs
            numba.parfors.parfor.init_prange()
            n = len(hnl__ciys)
            A = alloc_datetime_timedelta_array(n)
            for wbvn__iszb in numba.parfors.parfor.internal_prange(n):
                A[wbvn__iszb] = hnl__ciys[wbvn__iszb] - rhs
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
            fjmg__wwsay = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, fjmg__wwsay)
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
            ome__rju, fjmg__wwsay = divmod(lhs.value, rhs.value)
            return ome__rju, pd.Timedelta(fjmg__wwsay)
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
        ywxw__rjlt = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, ywxw__rjlt)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    mddkp__ffgr = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    dbe__awto = c.pyapi.long_from_longlong(mddkp__ffgr.days)
    yhfw__glc = c.pyapi.long_from_longlong(mddkp__ffgr.seconds)
    bqe__iqae = c.pyapi.long_from_longlong(mddkp__ffgr.microseconds)
    rbbc__cwxcq = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(rbbc__cwxcq, (dbe__awto, yhfw__glc,
        bqe__iqae))
    c.pyapi.decref(dbe__awto)
    c.pyapi.decref(yhfw__glc)
    c.pyapi.decref(bqe__iqae)
    c.pyapi.decref(rbbc__cwxcq)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    dbe__awto = c.pyapi.object_getattr_string(val, 'days')
    yhfw__glc = c.pyapi.object_getattr_string(val, 'seconds')
    bqe__iqae = c.pyapi.object_getattr_string(val, 'microseconds')
    hut__zwxd = c.pyapi.long_as_longlong(dbe__awto)
    asen__skco = c.pyapi.long_as_longlong(yhfw__glc)
    cuac__xkq = c.pyapi.long_as_longlong(bqe__iqae)
    mddkp__ffgr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mddkp__ffgr.days = hut__zwxd
    mddkp__ffgr.seconds = asen__skco
    mddkp__ffgr.microseconds = cuac__xkq
    c.pyapi.decref(dbe__awto)
    c.pyapi.decref(yhfw__glc)
    c.pyapi.decref(bqe__iqae)
    obnap__wnc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mddkp__ffgr._getvalue(), is_error=obnap__wnc)


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
    ome__rju, fjmg__wwsay = divmod(a, b)
    fjmg__wwsay *= 2
    eypru__abwqn = fjmg__wwsay > b if b > 0 else fjmg__wwsay < b
    if eypru__abwqn or fjmg__wwsay == b and ome__rju % 2 == 1:
        ome__rju += 1
    return ome__rju


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
                rds__xxyps = _cmp(_getstate(lhs), _getstate(rhs))
                return op(rds__xxyps, 0)
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
            ome__rju, fjmg__wwsay = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return ome__rju, datetime.timedelta(0, 0, fjmg__wwsay)
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
    blwe__rllcm = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != blwe__rllcm
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
        ywxw__rjlt = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ywxw__rjlt)


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
    jwae__skoc = types.Array(types.intp, 1, 'C')
    qgsq__jkiz = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        jwae__skoc, [n])
    upnng__dnb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        jwae__skoc, [n])
    qyvl__cavhz = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        jwae__skoc, [n])
    mvp__ztmkr = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    lpzd__kfc = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [mvp__ztmkr])
    qtian__ebqoq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    jshbj__rob = cgutils.get_or_insert_function(c.builder.module,
        qtian__ebqoq, name='unbox_datetime_timedelta_array')
    c.builder.call(jshbj__rob, [val, n, qgsq__jkiz.data, upnng__dnb.data,
        qyvl__cavhz.data, lpzd__kfc.data])
    ddj__hjiu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ddj__hjiu.days_data = qgsq__jkiz._getvalue()
    ddj__hjiu.seconds_data = upnng__dnb._getvalue()
    ddj__hjiu.microseconds_data = qyvl__cavhz._getvalue()
    ddj__hjiu.null_bitmap = lpzd__kfc._getvalue()
    obnap__wnc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ddj__hjiu._getvalue(), is_error=obnap__wnc)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    hnl__ciys = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    qgsq__jkiz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, hnl__ciys.days_data)
    upnng__dnb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, hnl__ciys.seconds_data).data
    qyvl__cavhz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, hnl__ciys.microseconds_data).data
    ltcim__cgxf = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, hnl__ciys.null_bitmap).data
    n = c.builder.extract_value(qgsq__jkiz.shape, 0)
    qtian__ebqoq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    pznac__lizb = cgutils.get_or_insert_function(c.builder.module,
        qtian__ebqoq, name='box_datetime_timedelta_array')
    bkyxa__njn = c.builder.call(pznac__lizb, [n, qgsq__jkiz.data,
        upnng__dnb, qyvl__cavhz, ltcim__cgxf])
    c.context.nrt.decref(c.builder, typ, val)
    return bkyxa__njn


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        mdb__pzaj, cdu__deii, nmqza__cfg, hjebt__quby = args
        kql__upsl = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        kql__upsl.days_data = mdb__pzaj
        kql__upsl.seconds_data = cdu__deii
        kql__upsl.microseconds_data = nmqza__cfg
        kql__upsl.null_bitmap = hjebt__quby
        context.nrt.incref(builder, signature.args[0], mdb__pzaj)
        context.nrt.incref(builder, signature.args[1], cdu__deii)
        context.nrt.incref(builder, signature.args[2], nmqza__cfg)
        context.nrt.incref(builder, signature.args[3], hjebt__quby)
        return kql__upsl._getvalue()
    pxg__jrvu = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return pxg__jrvu, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    qgsq__jkiz = np.empty(n, np.int64)
    upnng__dnb = np.empty(n, np.int64)
    qyvl__cavhz = np.empty(n, np.int64)
    dmb__fphp = np.empty(n + 7 >> 3, np.uint8)
    for wbvn__iszb, s in enumerate(pyval):
        ahh__ffvud = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(dmb__fphp, wbvn__iszb, int(not
            ahh__ffvud))
        if not ahh__ffvud:
            qgsq__jkiz[wbvn__iszb] = s.days
            upnng__dnb[wbvn__iszb] = s.seconds
            qyvl__cavhz[wbvn__iszb] = s.microseconds
    jwe__uzc = context.get_constant_generic(builder, days_data_type, qgsq__jkiz
        )
    qqzy__dfr = context.get_constant_generic(builder, seconds_data_type,
        upnng__dnb)
    nhlnn__zvo = context.get_constant_generic(builder,
        microseconds_data_type, qyvl__cavhz)
    eycua__hev = context.get_constant_generic(builder, nulls_type, dmb__fphp)
    return lir.Constant.literal_struct([jwe__uzc, qqzy__dfr, nhlnn__zvo,
        eycua__hev])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    qgsq__jkiz = np.empty(n, dtype=np.int64)
    upnng__dnb = np.empty(n, dtype=np.int64)
    qyvl__cavhz = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(qgsq__jkiz, upnng__dnb,
        qyvl__cavhz, nulls)


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
            xftlk__jutu = bodo.utils.conversion.coerce_to_ndarray(ind)
            olja__dgvpg = A._null_bitmap
            ghd__twsuz = A._days_data[xftlk__jutu]
            ujux__kfv = A._seconds_data[xftlk__jutu]
            mrkk__kqnk = A._microseconds_data[xftlk__jutu]
            n = len(ghd__twsuz)
            jvkhx__tkuw = get_new_null_mask_bool_index(olja__dgvpg, ind, n)
            return init_datetime_timedelta_array(ghd__twsuz, ujux__kfv,
                mrkk__kqnk, jvkhx__tkuw)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            xftlk__jutu = bodo.utils.conversion.coerce_to_ndarray(ind)
            olja__dgvpg = A._null_bitmap
            ghd__twsuz = A._days_data[xftlk__jutu]
            ujux__kfv = A._seconds_data[xftlk__jutu]
            mrkk__kqnk = A._microseconds_data[xftlk__jutu]
            n = len(ghd__twsuz)
            jvkhx__tkuw = get_new_null_mask_int_index(olja__dgvpg,
                xftlk__jutu, n)
            return init_datetime_timedelta_array(ghd__twsuz, ujux__kfv,
                mrkk__kqnk, jvkhx__tkuw)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            olja__dgvpg = A._null_bitmap
            ghd__twsuz = np.ascontiguousarray(A._days_data[ind])
            ujux__kfv = np.ascontiguousarray(A._seconds_data[ind])
            mrkk__kqnk = np.ascontiguousarray(A._microseconds_data[ind])
            jvkhx__tkuw = get_new_null_mask_slice_index(olja__dgvpg, ind, n)
            return init_datetime_timedelta_array(ghd__twsuz, ujux__kfv,
                mrkk__kqnk, jvkhx__tkuw)
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
    ggf__gek = (
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
            raise BodoError(ggf__gek)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(ggf__gek)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for wbvn__iszb in range(n):
                    A._days_data[ind[wbvn__iszb]] = val._days
                    A._seconds_data[ind[wbvn__iszb]] = val._seconds
                    A._microseconds_data[ind[wbvn__iszb]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[wbvn__iszb], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for wbvn__iszb in range(n):
                    A._days_data[ind[wbvn__iszb]] = val._days_data[wbvn__iszb]
                    A._seconds_data[ind[wbvn__iszb]] = val._seconds_data[
                        wbvn__iszb]
                    A._microseconds_data[ind[wbvn__iszb]
                        ] = val._microseconds_data[wbvn__iszb]
                    zfmy__som = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, wbvn__iszb)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[wbvn__iszb], zfmy__som)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for wbvn__iszb in range(n):
                    if not bodo.libs.array_kernels.isna(ind, wbvn__iszb
                        ) and ind[wbvn__iszb]:
                        A._days_data[wbvn__iszb] = val._days
                        A._seconds_data[wbvn__iszb] = val._seconds
                        A._microseconds_data[wbvn__iszb] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            wbvn__iszb, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                iig__acmzw = 0
                for wbvn__iszb in range(n):
                    if not bodo.libs.array_kernels.isna(ind, wbvn__iszb
                        ) and ind[wbvn__iszb]:
                        A._days_data[wbvn__iszb] = val._days_data[iig__acmzw]
                        A._seconds_data[wbvn__iszb] = val._seconds_data[
                            iig__acmzw]
                        A._microseconds_data[wbvn__iszb
                            ] = val._microseconds_data[iig__acmzw]
                        zfmy__som = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, iig__acmzw)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            wbvn__iszb, zfmy__som)
                        iig__acmzw += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                sme__oebbr = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for wbvn__iszb in range(sme__oebbr.start, sme__oebbr.stop,
                    sme__oebbr.step):
                    A._days_data[wbvn__iszb] = val._days
                    A._seconds_data[wbvn__iszb] = val._seconds
                    A._microseconds_data[wbvn__iszb] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        wbvn__iszb, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                fna__asi = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, fna__asi, ind, n)
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
            hnl__ciys = arg1
            numba.parfors.parfor.init_prange()
            n = len(hnl__ciys)
            A = alloc_datetime_timedelta_array(n)
            for wbvn__iszb in numba.parfors.parfor.internal_prange(n):
                A[wbvn__iszb] = hnl__ciys[wbvn__iszb] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            mof__zghyq = True
        else:
            mof__zghyq = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                nsqmk__bsd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for wbvn__iszb in numba.parfors.parfor.internal_prange(n):
                    shnbi__hxy = bodo.libs.array_kernels.isna(lhs, wbvn__iszb)
                    tps__gpsv = bodo.libs.array_kernels.isna(rhs, wbvn__iszb)
                    if shnbi__hxy or tps__gpsv:
                        rge__qcw = mof__zghyq
                    else:
                        rge__qcw = op(lhs[wbvn__iszb], rhs[wbvn__iszb])
                    nsqmk__bsd[wbvn__iszb] = rge__qcw
                return nsqmk__bsd
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                nsqmk__bsd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for wbvn__iszb in numba.parfors.parfor.internal_prange(n):
                    zfmy__som = bodo.libs.array_kernels.isna(lhs, wbvn__iszb)
                    if zfmy__som:
                        rge__qcw = mof__zghyq
                    else:
                        rge__qcw = op(lhs[wbvn__iszb], rhs)
                    nsqmk__bsd[wbvn__iszb] = rge__qcw
                return nsqmk__bsd
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                nsqmk__bsd = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for wbvn__iszb in numba.parfors.parfor.internal_prange(n):
                    zfmy__som = bodo.libs.array_kernels.isna(rhs, wbvn__iszb)
                    if zfmy__som:
                        rge__qcw = mof__zghyq
                    else:
                        rge__qcw = op(lhs, rhs[wbvn__iszb])
                    nsqmk__bsd[wbvn__iszb] = rge__qcw
                return nsqmk__bsd
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for djy__ccczz in timedelta_unsupported_attrs:
        gylip__hldxc = 'pandas.Timedelta.' + djy__ccczz
        overload_attribute(PDTimeDeltaType, djy__ccczz)(
            create_unsupported_overload(gylip__hldxc))
    for iiiew__yses in timedelta_unsupported_methods:
        gylip__hldxc = 'pandas.Timedelta.' + iiiew__yses
        overload_method(PDTimeDeltaType, iiiew__yses)(
            create_unsupported_overload(gylip__hldxc + '()'))


_intstall_pd_timedelta_unsupported()
