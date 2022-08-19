"""Numba extension support for time objects and their arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
_nanos_per_micro = 1000
_nanos_per_milli = 1000 * _nanos_per_micro
_nanos_per_second = 1000 * _nanos_per_milli
_nanos_per_minute = 60 * _nanos_per_second
_nanos_per_hour = 60 * _nanos_per_minute


class Time:

    def __init__(self, hour=0, minute=0, second=0, millisecond=0,
        microsecond=0, nanosecond=0, precision=9):
        self.precision = precision
        self.value = np.int64(hour * _nanos_per_hour + minute *
            _nanos_per_minute + second * _nanos_per_second + millisecond *
            _nanos_per_milli + microsecond * _nanos_per_micro + nanosecond)

    def __repr__(self):
        return (
            f'Time({self.hour}, {self.minute}, {self.second}, {self.millisecond}, {self.microsecond}, {self.nanosecond}, precision={self.precision})'
            )

    def __eq__(self, other):
        if not isinstance(other, Time):
            return False
        return self.value == other.value and self.precision == other.precision

    def _check_can_compare(self, other):
        if self.precision != other.precision:
            raise BodoError(
                f'Cannot compare times with different precisions: {self} and {other}'
                )

    def __lt__(self, other):
        self._check_can_compare(other)
        return self.value < other.value

    def __le__(self, other):
        self._check_can_compare(other)
        return self.value <= other.value

    def __int__(self):
        if self.precision == 9:
            return self.value
        if self.precision == 6:
            return self.value // _nanos_per_micro
        if self.precision == 3:
            return self.value // _nanos_per_milli
        if self.precision == 0:
            return self.value // _nanos_per_second
        raise BodoError(f'Unsupported precision: {self.precision}')

    def __hash__(self):
        return hash((self.value, self.precision))

    @property
    def hour(self):
        return self.value // _nanos_per_hour

    @property
    def minute(self):
        return self.value % _nanos_per_hour // _nanos_per_minute

    @property
    def second(self):
        return self.value % _nanos_per_minute // _nanos_per_second

    @property
    def millisecond(self):
        return self.value % _nanos_per_second // _nanos_per_milli

    @property
    def microsecond(self):
        return self.value % _nanos_per_milli // _nanos_per_micro

    @property
    def nanosecond(self):
        return self.value % _nanos_per_micro


ll.add_symbol('box_time_array', hdatetime_ext.box_time_array)
ll.add_symbol('unbox_time_array', hdatetime_ext.unbox_time_array)


class TimeType(types.Type):

    def __init__(self, precision):
        assert isinstance(precision, int
            ) and precision >= 0 and precision <= 9, 'precision must be an integer between 0 and 9'
        self.precision = precision
        super(TimeType, self).__init__(name=f'TimeType({precision})')
        self.bitwidth = 64


@typeof_impl.register(Time)
def typeof_time(val, c):
    return TimeType(val.precision)


@overload(Time)
def overload_time(hour=0, min=0, second=0, millisecond=0, microsecond=0,
    nanosecond=0, precision=9):

    def impl(hour=0, min=0, second=0, millisecond=0, microsecond=0,
        nanosecond=0, precision=9):
        return cast_int_to_time(_nanos_per_hour * hour + _nanos_per_minute *
            min + _nanos_per_second * second + _nanos_per_milli *
            millisecond + _nanos_per_micro * microsecond + nanosecond,
            precision)
    return impl


register_model(TimeType)(models.IntegerModel)


@overload_attribute(TimeType, 'hour')
def time_hour_attribute(val):
    return lambda val: cast_time_to_int(val) // _nanos_per_hour


@overload_attribute(TimeType, 'minute')
def time_minute_attribute(val):
    return lambda val: cast_time_to_int(val
        ) % _nanos_per_hour // _nanos_per_minute


@overload_attribute(TimeType, 'second')
def time_second_attribute(val):
    return lambda val: cast_time_to_int(val
        ) % _nanos_per_minute // _nanos_per_second


@overload_attribute(TimeType, 'millisecond')
def time_millisecond_attribute(val):
    return lambda val: cast_time_to_int(val
        ) % _nanos_per_second // _nanos_per_milli


@overload_attribute(TimeType, 'microsecond')
def time_microsecond_attribute(val):
    return lambda val: cast_time_to_int(val
        ) % _nanos_per_milli // _nanos_per_micro


@overload_attribute(TimeType, 'nanosecond')
def time_nanosecond_attribute(val):
    return lambda val: cast_time_to_int(val) % _nanos_per_micro


def _to_nanos_codegen(c, hour_ll, minute_ll, second_ll, millisecond_ll,
    microsecond_ll, nanosecond_ll):
    return c.builder.add(nanosecond_ll, c.builder.add(c.builder.mul(
        microsecond_ll, lir.Constant(lir.IntType(64), _nanos_per_micro)), c
        .builder.add(c.builder.mul(millisecond_ll, lir.Constant(lir.IntType
        (64), _nanos_per_milli)), c.builder.add(c.builder.mul(second_ll,
        lir.Constant(lir.IntType(64), _nanos_per_second)), c.builder.add(c.
        builder.mul(minute_ll, lir.Constant(lir.IntType(64),
        _nanos_per_minute)), c.builder.mul(hour_ll, lir.Constant(lir.
        IntType(64), _nanos_per_hour)))))))


def _from_nanos_codegen(c, val):
    icq__lyok = c.pyapi.long_from_longlong(c.builder.udiv(val, lir.Constant
        (lir.IntType(64), _nanos_per_hour)))
    yfr__qxqg = c.pyapi.long_from_longlong(c.builder.udiv(c.builder.urem(
        val, lir.Constant(lir.IntType(64), _nanos_per_hour)), lir.Constant(
        lir.IntType(64), _nanos_per_minute)))
    cpxhh__wpu = c.pyapi.long_from_longlong(c.builder.udiv(c.builder.urem(
        val, lir.Constant(lir.IntType(64), _nanos_per_minute)), lir.
        Constant(lir.IntType(64), _nanos_per_second)))
    yxhhv__ckz = c.pyapi.long_from_longlong(c.builder.udiv(c.builder.urem(
        val, lir.Constant(lir.IntType(64), _nanos_per_second)), lir.
        Constant(lir.IntType(64), _nanos_per_milli)))
    pllmc__robt = c.pyapi.long_from_longlong(c.builder.udiv(c.builder.urem(
        val, lir.Constant(lir.IntType(64), _nanos_per_milli)), lir.Constant
        (lir.IntType(64), _nanos_per_micro)))
    yqpz__hacuh = c.pyapi.long_from_longlong(c.builder.urem(val, lir.
        Constant(lir.IntType(64), _nanos_per_micro)))
    return (icq__lyok, yfr__qxqg, cpxhh__wpu, yxhhv__ckz, pllmc__robt,
        yqpz__hacuh)


@unbox(TimeType)
def unbox_time(typ, val, c):
    icq__lyok = c.pyapi.object_getattr_string(val, 'hour')
    yfr__qxqg = c.pyapi.object_getattr_string(val, 'minute')
    cpxhh__wpu = c.pyapi.object_getattr_string(val, 'second')
    yxhhv__ckz = c.pyapi.object_getattr_string(val, 'millisecond')
    pllmc__robt = c.pyapi.object_getattr_string(val, 'microsecond')
    yqpz__hacuh = c.pyapi.object_getattr_string(val, 'nanosecond')
    hour_ll = c.pyapi.long_as_longlong(icq__lyok)
    minute_ll = c.pyapi.long_as_longlong(yfr__qxqg)
    second_ll = c.pyapi.long_as_longlong(cpxhh__wpu)
    millisecond_ll = c.pyapi.long_as_longlong(yxhhv__ckz)
    microsecond_ll = c.pyapi.long_as_longlong(pllmc__robt)
    nanosecond_ll = c.pyapi.long_as_longlong(yqpz__hacuh)
    jmhh__rfdo = _to_nanos_codegen(c, hour_ll, minute_ll, second_ll,
        millisecond_ll, microsecond_ll, nanosecond_ll)
    c.pyapi.decref(icq__lyok)
    c.pyapi.decref(yfr__qxqg)
    c.pyapi.decref(cpxhh__wpu)
    c.pyapi.decref(yxhhv__ckz)
    c.pyapi.decref(pllmc__robt)
    c.pyapi.decref(yqpz__hacuh)
    mns__ooh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jmhh__rfdo, is_error=mns__ooh)


@lower_constant(TimeType)
def lower_constant_time(context, builder, ty, pyval):
    hour_ll = context.get_constant(types.int64, pyval.hour)
    minute_ll = context.get_constant(types.int64, pyval.minute)
    second_ll = context.get_constant(types.int64, pyval.second)
    millisecond_ll = context.get_constant(types.int64, pyval.millisecond)
    microsecond_ll = context.get_constant(types.int64, pyval.microsecond)
    nanosecond_ll = context.get_constant(types.int64, pyval.nanosecond)
    jmhh__rfdo = _to_nanos_codegen(context, hour_ll, minute_ll, second_ll,
        millisecond_ll, microsecond_ll, nanosecond_ll)
    return jmhh__rfdo


@box(TimeType)
def box_time(typ, val, c):
    (icq__lyok, yfr__qxqg, cpxhh__wpu, yxhhv__ckz, pllmc__robt, yqpz__hacuh
        ) = _from_nanos_codegen(c, val)
    wpgu__dqxyl = c.pyapi.unserialize(c.pyapi.serialize_object(Time))
    bkqe__mqd = c.pyapi.call_function_objargs(wpgu__dqxyl, (icq__lyok,
        yfr__qxqg, cpxhh__wpu, yxhhv__ckz, pllmc__robt, yqpz__hacuh, c.
        pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.precision)))
        )
    c.pyapi.decref(icq__lyok)
    c.pyapi.decref(yfr__qxqg)
    c.pyapi.decref(cpxhh__wpu)
    c.pyapi.decref(yxhhv__ckz)
    c.pyapi.decref(pllmc__robt)
    c.pyapi.decref(yqpz__hacuh)
    c.pyapi.decref(wpgu__dqxyl)
    return bkqe__mqd


@lower_builtin(Time, types.int64, types.int64, types.int64, types.int64,
    types.int64, types.int64)
def impl_ctor_time(context, builder, sig, args):
    (hour_ll, minute_ll, second_ll, millisecond_ll, microsecond_ll,
        nanosecond_ll) = args
    jmhh__rfdo = _to_nanos_codegen(context, hour_ll, minute_ll, second_ll,
        millisecond_ll, microsecond_ll, nanosecond_ll)
    return jmhh__rfdo


@intrinsic
def cast_int_to_time(typingctx, val, precision):
    assert val == types.int64, 'val must be int64'
    assert isinstance(precision, types.IntegerLiteral
        ), 'precision must be an integer literal'

    def codegen(context, builder, signature, args):
        return args[0]
    return TimeType(precision.literal_value)(types.int64, types.int64), codegen


@intrinsic
def cast_time_to_int(typingctx, val):
    assert isinstance(val, TimeType), 'val must be Time'

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


class TimeArrayType(types.ArrayCompatible):

    def __init__(self, precision):
        assert isinstance(precision, int
            ) and precision >= 0 and precision <= 9, 'precision must be an integer between 0 and 9'
        self.precision = precision
        super(TimeArrayType, self).__init__(name=f'TimeArrayType({precision})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return TimeType(self.precision)

    def copy(self):
        return TimeArrayType(self.precision)


data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(TimeArrayType)
class TimeArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oeqk__dudnc = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, oeqk__dudnc)


make_attribute_wrapper(TimeArrayType, 'data', '_data')
make_attribute_wrapper(TimeArrayType, 'null_bitmap', '_null_bitmap')


@overload_method(TimeArrayType, 'copy', no_unliteral=True)
def overload_time_arr_copy(A):
    return lambda A: bodo.hiframes.time_ext.init_time_array(A._data.copy(),
        A._null_bitmap.copy())


@overload_attribute(TimeArrayType, 'dtype')
def overload_time_arr_dtype(A):
    return lambda A: np.object_


@unbox(TimeArrayType)
def unbox_time_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    kfxu__kcsfo = types.Array(types.intp, 1, 'C')
    stqd__syxb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        kfxu__kcsfo, [n])
    ixav__qzlum = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    wvtgc__afc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [ixav__qzlum])
    fja__xpm = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    gnwpi__jtd = cgutils.get_or_insert_function(c.builder.module, fja__xpm,
        name='unbox_time_array')
    c.builder.call(gnwpi__jtd, [val, n, stqd__syxb.data, wvtgc__afc.data])
    dtv__xtk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    dtv__xtk.data = stqd__syxb._getvalue()
    dtv__xtk.null_bitmap = wvtgc__afc._getvalue()
    mns__ooh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(dtv__xtk._getvalue(), is_error=mns__ooh)


@box(TimeArrayType)
def box_time_array(typ, val, c):
    usy__myx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    stqd__syxb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, usy__myx.data)
    tkipp__mswak = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, usy__myx.null_bitmap).data
    n = c.builder.extract_value(stqd__syxb.shape, 0)
    fja__xpm = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8)])
    asjc__syhg = cgutils.get_or_insert_function(c.builder.module, fja__xpm,
        name='box_time_array')
    xjmn__kltmm = c.builder.call(asjc__syhg, [n, stqd__syxb.data,
        tkipp__mswak, lir.Constant(lir.IntType(8), typ.precision)])
    c.context.nrt.decref(c.builder, typ, val)
    return xjmn__kltmm


@intrinsic
def init_time_array(typingctx, data, nulls, precision):
    assert data == types.Array(types.int64, 1, 'C'
        ), 'data must be an array of int64'
    assert nulls == types.Array(types.uint8, 1, 'C'
        ), 'nulls must be an array of uint8'
    assert isinstance(precision, types.IntegerLiteral
        ), 'precision must be an integer literal'

    def codegen(context, builder, signature, args):
        qvmp__wvu, nrzo__nhfgp, vhnc__wsmo = args
        fwox__nvmc = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        fwox__nvmc.data = qvmp__wvu
        fwox__nvmc.null_bitmap = nrzo__nhfgp
        context.nrt.incref(builder, signature.args[0], qvmp__wvu)
        context.nrt.incref(builder, signature.args[1], nrzo__nhfgp)
        return fwox__nvmc._getvalue()
    sig = TimeArrayType(precision.literal_value)(data, nulls, precision)
    return sig, codegen


@lower_constant(TimeArrayType)
def lower_constant_time_arr(context, builder, typ, pyval):
    n = len(pyval)
    stqd__syxb = np.full(n, 0, np.int64)
    ijqni__eoeoi = np.empty(n + 7 >> 3, np.uint8)
    for tpuqo__fnx, qjoag__bqo in enumerate(pyval):
        mwc__tzb = pd.isna(qjoag__bqo)
        bodo.libs.int_arr_ext.set_bit_to_arr(ijqni__eoeoi, tpuqo__fnx, int(
            not mwc__tzb))
        if not mwc__tzb:
            stqd__syxb[tpuqo__fnx] = (qjoag__bqo.hour * _nanos_per_hour + 
                qjoag__bqo.minute * _nanos_per_minute + qjoag__bqo.second *
                _nanos_per_second + qjoag__bqo.millisecond *
                _nanos_per_milli + qjoag__bqo.microsecond *
                _nanos_per_micro + qjoag__bqo.nanosecond)
    yfwi__iee = context.get_constant_generic(builder, data_type, stqd__syxb)
    pmbgv__lyus = context.get_constant_generic(builder, nulls_type,
        ijqni__eoeoi)
    return lir.Constant.literal_struct([yfwi__iee, pmbgv__lyus])


@numba.njit(no_cpython_wrapper=True)
def alloc_time_array(n):
    stqd__syxb = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_time_array(stqd__syxb, nulls)


def alloc_time_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws, 'Only one argument allowed'
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_time_ext_alloc_time_array = (
    alloc_time_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def time_arr_getitem(A, ind):
    if not isinstance(A, TimeArrayType):
        return
    precision = A.precision
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: cast_int_to_time(A._data[ind], precision)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            npq__vne, nroiy__nohzc = array_getitem_bool_index(A, ind)
            return init_time_array(npq__vne, nroiy__nohzc, precision)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            npq__vne, nroiy__nohzc = array_getitem_int_index(A, ind)
            return init_time_array(npq__vne, nroiy__nohzc, precision)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            npq__vne, nroiy__nohzc = array_getitem_slice_index(A, ind)
            return init_time_array(npq__vne, nroiy__nohzc, precision)
        return impl_slice
    raise BodoError(
        f'getitem for TimeArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def time_arr_setitem(A, idx, val):
    if not isinstance(A, TimeArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    elki__wks = (
        f"setitem for TimeArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if isinstance(types.unliteral(val), TimeType):

            def impl(A, idx, val):
                A._data[idx] = cast_time_to_int(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl
        else:
            raise BodoError(elki__wks)
    if not (is_iterable_type(val) and isinstance(val.dtype, TimeType) or
        isinstance(types.unliteral(val), TimeType)):
        raise BodoError(elki__wks)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if isinstance(types.unliteral(val), TimeType):
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                cast_time_to_int(val))

        def impl_arr_ind(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if isinstance(types.unliteral(val), TimeType):
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                cast_time_to_int(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if isinstance(types.unliteral(val), TimeType):
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                cast_time_to_int(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for TimeArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_len_time_arr(A):
    if isinstance(A, TimeArrayType):
        return lambda A: len(A._data)


@overload_attribute(TimeArrayType, 'shape')
def overload_time_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(TimeArrayType, 'nbytes')
def time_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


def create_cmp_op_overload(op):

    def overload_time_cmp(lhs, rhs):
        if isinstance(lhs, TimeType) and isinstance(rhs, TimeType):

            def impl(lhs, rhs):
                ksxen__tddsu = cast_time_to_int(lhs)
                nelfn__pewo = cast_time_to_int(rhs)
                return op(0 if ksxen__tddsu == nelfn__pewo else 1 if 
                    ksxen__tddsu > nelfn__pewo else -1, 0)
            return impl
    return overload_time_cmp
