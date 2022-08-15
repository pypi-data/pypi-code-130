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
        xfd__ehiz = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, xfd__ehiz)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    apsfi__dsft = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    urbmb__ymts = c.pyapi.long_from_longlong(apsfi__dsft.value)
    lehyy__wcyi = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(lehyy__wcyi, (urbmb__ymts,))
    c.pyapi.decref(urbmb__ymts)
    c.pyapi.decref(lehyy__wcyi)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    urbmb__ymts = c.pyapi.object_getattr_string(val, 'value')
    yfn__lrw = c.pyapi.long_as_longlong(urbmb__ymts)
    apsfi__dsft = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    apsfi__dsft.value = yfn__lrw
    c.pyapi.decref(urbmb__ymts)
    xpz__xdg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(apsfi__dsft._getvalue(), is_error=xpz__xdg)


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
            oheu__lps = 1000 * microseconds
            return init_pd_timedelta(oheu__lps)
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
            oheu__lps = 1000 * microseconds
            return init_pd_timedelta(oheu__lps)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    gmqcg__ywx, der__nugw = pd._libs.tslibs.conversion.precision_from_unit(unit
        )

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * gmqcg__ywx)
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
            ilyvj__tdee = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + ilyvj__tdee
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            nzlm__mjt = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = nzlm__mjt + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            zvbk__xwez = rhs.toordinal()
            ekt__pxbt = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            vvkwv__hltot = rhs.microsecond
            ukzoa__sga = lhs.value // 1000
            ofekq__rfp = lhs.nanoseconds
            keg__ntwks = vvkwv__hltot + ukzoa__sga
            sga__guq = 1000000 * (zvbk__xwez * 86400 + ekt__pxbt) + keg__ntwks
            covl__cuq = ofekq__rfp
            return compute_pd_timestamp(sga__guq, covl__cuq)
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
            ligp__gkejp = datetime.timedelta(rhs.toordinal(), hours=rhs.
                hour, minutes=rhs.minute, seconds=rhs.second, microseconds=
                rhs.microsecond)
            ligp__gkejp = ligp__gkejp + lhs
            rey__fppgu, hpuk__pepd = divmod(ligp__gkejp.seconds, 3600)
            qdf__ymzy, dvodk__tgy = divmod(hpuk__pepd, 60)
            if 0 < ligp__gkejp.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    ligp__gkejp.days)
                return datetime.datetime(d.year, d.month, d.day, rey__fppgu,
                    qdf__ymzy, dvodk__tgy, ligp__gkejp.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ligp__gkejp = datetime.timedelta(lhs.toordinal(), hours=lhs.
                hour, minutes=lhs.minute, seconds=lhs.second, microseconds=
                lhs.microsecond)
            ligp__gkejp = ligp__gkejp + rhs
            rey__fppgu, hpuk__pepd = divmod(ligp__gkejp.seconds, 3600)
            qdf__ymzy, dvodk__tgy = divmod(hpuk__pepd, 60)
            if 0 < ligp__gkejp.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    ligp__gkejp.days)
                return datetime.datetime(d.year, d.month, d.day, rey__fppgu,
                    qdf__ymzy, dvodk__tgy, ligp__gkejp.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            gfd__ddqs = lhs.value - rhs.value
            return pd.Timedelta(gfd__ddqs)
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
            fzcd__vlm = lhs
            numba.parfors.parfor.init_prange()
            n = len(fzcd__vlm)
            A = alloc_datetime_timedelta_array(n)
            for thc__vcvx in numba.parfors.parfor.internal_prange(n):
                A[thc__vcvx] = fzcd__vlm[thc__vcvx] - rhs
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
            bks__akb = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, bks__akb)
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
            lxx__qhlac, bks__akb = divmod(lhs.value, rhs.value)
            return lxx__qhlac, pd.Timedelta(bks__akb)
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
        xfd__ehiz = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, xfd__ehiz)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    apsfi__dsft = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cnoqs__cee = c.pyapi.long_from_longlong(apsfi__dsft.days)
    xim__uoq = c.pyapi.long_from_longlong(apsfi__dsft.seconds)
    glxjp__mwat = c.pyapi.long_from_longlong(apsfi__dsft.microseconds)
    lehyy__wcyi = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(lehyy__wcyi, (cnoqs__cee, xim__uoq,
        glxjp__mwat))
    c.pyapi.decref(cnoqs__cee)
    c.pyapi.decref(xim__uoq)
    c.pyapi.decref(glxjp__mwat)
    c.pyapi.decref(lehyy__wcyi)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    cnoqs__cee = c.pyapi.object_getattr_string(val, 'days')
    xim__uoq = c.pyapi.object_getattr_string(val, 'seconds')
    glxjp__mwat = c.pyapi.object_getattr_string(val, 'microseconds')
    kvfn__opjz = c.pyapi.long_as_longlong(cnoqs__cee)
    dzma__lkn = c.pyapi.long_as_longlong(xim__uoq)
    bcmg__zoi = c.pyapi.long_as_longlong(glxjp__mwat)
    apsfi__dsft = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    apsfi__dsft.days = kvfn__opjz
    apsfi__dsft.seconds = dzma__lkn
    apsfi__dsft.microseconds = bcmg__zoi
    c.pyapi.decref(cnoqs__cee)
    c.pyapi.decref(xim__uoq)
    c.pyapi.decref(glxjp__mwat)
    xpz__xdg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(apsfi__dsft._getvalue(), is_error=xpz__xdg)


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
    lxx__qhlac, bks__akb = divmod(a, b)
    bks__akb *= 2
    bsb__jqp = bks__akb > b if b > 0 else bks__akb < b
    if bsb__jqp or bks__akb == b and lxx__qhlac % 2 == 1:
        lxx__qhlac += 1
    return lxx__qhlac


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
                xsij__wbtr = _cmp(_getstate(lhs), _getstate(rhs))
                return op(xsij__wbtr, 0)
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
            lxx__qhlac, bks__akb = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return lxx__qhlac, datetime.timedelta(0, 0, bks__akb)
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
    dsap__autn = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != dsap__autn
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
        xfd__ehiz = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, xfd__ehiz)


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
    untd__qsizb = types.Array(types.intp, 1, 'C')
    utc__bjg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        untd__qsizb, [n])
    rfqsg__qrl = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        untd__qsizb, [n])
    mkv__rrepk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        untd__qsizb, [n])
    ilu__rnw = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    ykf__rom = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types.
        Array(types.uint8, 1, 'C'), [ilu__rnw])
    udkhi__sqdoc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    ehh__penn = cgutils.get_or_insert_function(c.builder.module,
        udkhi__sqdoc, name='unbox_datetime_timedelta_array')
    c.builder.call(ehh__penn, [val, n, utc__bjg.data, rfqsg__qrl.data,
        mkv__rrepk.data, ykf__rom.data])
    bjrh__jbzw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bjrh__jbzw.days_data = utc__bjg._getvalue()
    bjrh__jbzw.seconds_data = rfqsg__qrl._getvalue()
    bjrh__jbzw.microseconds_data = mkv__rrepk._getvalue()
    bjrh__jbzw.null_bitmap = ykf__rom._getvalue()
    xpz__xdg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bjrh__jbzw._getvalue(), is_error=xpz__xdg)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    fzcd__vlm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    utc__bjg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fzcd__vlm.days_data)
    rfqsg__qrl = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fzcd__vlm.seconds_data).data
    mkv__rrepk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, fzcd__vlm.microseconds_data).data
    fkig__obkg = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, fzcd__vlm.null_bitmap).data
    n = c.builder.extract_value(utc__bjg.shape, 0)
    udkhi__sqdoc = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    ngg__umum = cgutils.get_or_insert_function(c.builder.module,
        udkhi__sqdoc, name='box_datetime_timedelta_array')
    dqjtz__zwzyr = c.builder.call(ngg__umum, [n, utc__bjg.data, rfqsg__qrl,
        mkv__rrepk, fkig__obkg])
    c.context.nrt.decref(c.builder, typ, val)
    return dqjtz__zwzyr


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        vxpo__lxra, skms__qom, mpqnp__lfywd, clzz__mqgn = args
        bhzwg__iygw = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        bhzwg__iygw.days_data = vxpo__lxra
        bhzwg__iygw.seconds_data = skms__qom
        bhzwg__iygw.microseconds_data = mpqnp__lfywd
        bhzwg__iygw.null_bitmap = clzz__mqgn
        context.nrt.incref(builder, signature.args[0], vxpo__lxra)
        context.nrt.incref(builder, signature.args[1], skms__qom)
        context.nrt.incref(builder, signature.args[2], mpqnp__lfywd)
        context.nrt.incref(builder, signature.args[3], clzz__mqgn)
        return bhzwg__iygw._getvalue()
    writb__wxbet = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return writb__wxbet, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    utc__bjg = np.empty(n, np.int64)
    rfqsg__qrl = np.empty(n, np.int64)
    mkv__rrepk = np.empty(n, np.int64)
    vpuw__cpsnm = np.empty(n + 7 >> 3, np.uint8)
    for thc__vcvx, s in enumerate(pyval):
        mhm__octvo = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(vpuw__cpsnm, thc__vcvx, int(
            not mhm__octvo))
        if not mhm__octvo:
            utc__bjg[thc__vcvx] = s.days
            rfqsg__qrl[thc__vcvx] = s.seconds
            mkv__rrepk[thc__vcvx] = s.microseconds
    qcf__jpdc = context.get_constant_generic(builder, days_data_type, utc__bjg)
    ooroa__uyknu = context.get_constant_generic(builder, seconds_data_type,
        rfqsg__qrl)
    fjp__nle = context.get_constant_generic(builder, microseconds_data_type,
        mkv__rrepk)
    nbbdp__lfbv = context.get_constant_generic(builder, nulls_type, vpuw__cpsnm
        )
    return lir.Constant.literal_struct([qcf__jpdc, ooroa__uyknu, fjp__nle,
        nbbdp__lfbv])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    utc__bjg = np.empty(n, dtype=np.int64)
    rfqsg__qrl = np.empty(n, dtype=np.int64)
    mkv__rrepk = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(utc__bjg, rfqsg__qrl, mkv__rrepk,
        nulls)


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
            mdv__yzcrc = bodo.utils.conversion.coerce_to_ndarray(ind)
            mmhw__hbn = A._null_bitmap
            cwps__hpgmh = A._days_data[mdv__yzcrc]
            bepnt__aza = A._seconds_data[mdv__yzcrc]
            dqsw__qsbs = A._microseconds_data[mdv__yzcrc]
            n = len(cwps__hpgmh)
            ypwd__ldqe = get_new_null_mask_bool_index(mmhw__hbn, ind, n)
            return init_datetime_timedelta_array(cwps__hpgmh, bepnt__aza,
                dqsw__qsbs, ypwd__ldqe)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            mdv__yzcrc = bodo.utils.conversion.coerce_to_ndarray(ind)
            mmhw__hbn = A._null_bitmap
            cwps__hpgmh = A._days_data[mdv__yzcrc]
            bepnt__aza = A._seconds_data[mdv__yzcrc]
            dqsw__qsbs = A._microseconds_data[mdv__yzcrc]
            n = len(cwps__hpgmh)
            ypwd__ldqe = get_new_null_mask_int_index(mmhw__hbn, mdv__yzcrc, n)
            return init_datetime_timedelta_array(cwps__hpgmh, bepnt__aza,
                dqsw__qsbs, ypwd__ldqe)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            mmhw__hbn = A._null_bitmap
            cwps__hpgmh = np.ascontiguousarray(A._days_data[ind])
            bepnt__aza = np.ascontiguousarray(A._seconds_data[ind])
            dqsw__qsbs = np.ascontiguousarray(A._microseconds_data[ind])
            ypwd__ldqe = get_new_null_mask_slice_index(mmhw__hbn, ind, n)
            return init_datetime_timedelta_array(cwps__hpgmh, bepnt__aza,
                dqsw__qsbs, ypwd__ldqe)
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
    fiyit__lwyn = (
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
            raise BodoError(fiyit__lwyn)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(fiyit__lwyn)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for thc__vcvx in range(n):
                    A._days_data[ind[thc__vcvx]] = val._days
                    A._seconds_data[ind[thc__vcvx]] = val._seconds
                    A._microseconds_data[ind[thc__vcvx]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[thc__vcvx], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for thc__vcvx in range(n):
                    A._days_data[ind[thc__vcvx]] = val._days_data[thc__vcvx]
                    A._seconds_data[ind[thc__vcvx]] = val._seconds_data[
                        thc__vcvx]
                    A._microseconds_data[ind[thc__vcvx]
                        ] = val._microseconds_data[thc__vcvx]
                    oeywl__mjfx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, thc__vcvx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[thc__vcvx], oeywl__mjfx)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for thc__vcvx in range(n):
                    if not bodo.libs.array_kernels.isna(ind, thc__vcvx
                        ) and ind[thc__vcvx]:
                        A._days_data[thc__vcvx] = val._days
                        A._seconds_data[thc__vcvx] = val._seconds
                        A._microseconds_data[thc__vcvx] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            thc__vcvx, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                aeaf__lqutq = 0
                for thc__vcvx in range(n):
                    if not bodo.libs.array_kernels.isna(ind, thc__vcvx
                        ) and ind[thc__vcvx]:
                        A._days_data[thc__vcvx] = val._days_data[aeaf__lqutq]
                        A._seconds_data[thc__vcvx] = val._seconds_data[
                            aeaf__lqutq]
                        A._microseconds_data[thc__vcvx
                            ] = val._microseconds_data[aeaf__lqutq]
                        oeywl__mjfx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, aeaf__lqutq)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            thc__vcvx, oeywl__mjfx)
                        aeaf__lqutq += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                ahkq__teiwt = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for thc__vcvx in range(ahkq__teiwt.start, ahkq__teiwt.stop,
                    ahkq__teiwt.step):
                    A._days_data[thc__vcvx] = val._days
                    A._seconds_data[thc__vcvx] = val._seconds
                    A._microseconds_data[thc__vcvx] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        thc__vcvx, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                vmw__khu = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, vmw__khu, ind, n)
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
            fzcd__vlm = arg1
            numba.parfors.parfor.init_prange()
            n = len(fzcd__vlm)
            A = alloc_datetime_timedelta_array(n)
            for thc__vcvx in numba.parfors.parfor.internal_prange(n):
                A[thc__vcvx] = fzcd__vlm[thc__vcvx] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            oztyq__ymrrh = True
        else:
            oztyq__ymrrh = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                meewo__nekab = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for thc__vcvx in numba.parfors.parfor.internal_prange(n):
                    ubsle__zfxcu = bodo.libs.array_kernels.isna(lhs, thc__vcvx)
                    awrlc__phme = bodo.libs.array_kernels.isna(rhs, thc__vcvx)
                    if ubsle__zfxcu or awrlc__phme:
                        nkda__pgdg = oztyq__ymrrh
                    else:
                        nkda__pgdg = op(lhs[thc__vcvx], rhs[thc__vcvx])
                    meewo__nekab[thc__vcvx] = nkda__pgdg
                return meewo__nekab
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                meewo__nekab = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for thc__vcvx in numba.parfors.parfor.internal_prange(n):
                    oeywl__mjfx = bodo.libs.array_kernels.isna(lhs, thc__vcvx)
                    if oeywl__mjfx:
                        nkda__pgdg = oztyq__ymrrh
                    else:
                        nkda__pgdg = op(lhs[thc__vcvx], rhs)
                    meewo__nekab[thc__vcvx] = nkda__pgdg
                return meewo__nekab
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                meewo__nekab = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for thc__vcvx in numba.parfors.parfor.internal_prange(n):
                    oeywl__mjfx = bodo.libs.array_kernels.isna(rhs, thc__vcvx)
                    if oeywl__mjfx:
                        nkda__pgdg = oztyq__ymrrh
                    else:
                        nkda__pgdg = op(lhs, rhs[thc__vcvx])
                    meewo__nekab[thc__vcvx] = nkda__pgdg
                return meewo__nekab
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for taepd__ukrl in timedelta_unsupported_attrs:
        qvq__fhyk = 'pandas.Timedelta.' + taepd__ukrl
        overload_attribute(PDTimeDeltaType, taepd__ukrl)(
            create_unsupported_overload(qvq__fhyk))
    for wva__qilr in timedelta_unsupported_methods:
        qvq__fhyk = 'pandas.Timedelta.' + wva__qilr
        overload_method(PDTimeDeltaType, wva__qilr)(create_unsupported_overload
            (qvq__fhyk + '()'))


_intstall_pd_timedelta_unsupported()
