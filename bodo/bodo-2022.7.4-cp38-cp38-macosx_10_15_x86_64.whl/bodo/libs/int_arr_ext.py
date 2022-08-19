"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name=
            f'IntegerArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)

    @property
    def get_pandas_scalar_type_instance(self):
        htd__rxxn = int(np.log2(self.dtype.bitwidth // 8))
        mxnra__pnx = 0 if self.dtype.signed else 4
        idx = htd__rxxn + mxnra__pnx
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pfqb__czuq = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, pfqb__czuq)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    qmko__enb = 8 * val.dtype.itemsize
    kgf__kcemw = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(kgf__kcemw, qmko__enb))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        hxjmu__gcm = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(hxjmu__gcm)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    zwyv__arnt = c.context.insert_const_string(c.builder.module, 'pandas')
    rxb__vonx = c.pyapi.import_module_noblock(zwyv__arnt)
    jnhu__hkgf = c.pyapi.call_method(rxb__vonx, str(typ)[:-2], ())
    c.pyapi.decref(rxb__vonx)
    return jnhu__hkgf


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    qmko__enb = 8 * val.itemsize
    kgf__kcemw = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(kgf__kcemw, qmko__enb))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    rfk__lompk = n + 7 >> 3
    lozv__vlkwg = np.empty(rfk__lompk, np.uint8)
    for i in range(n):
        kfgyq__dlyse = i // 8
        lozv__vlkwg[kfgyq__dlyse] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            lozv__vlkwg[kfgyq__dlyse]) & kBitmask[i % 8]
    return lozv__vlkwg


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    gnbij__pse = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(gnbij__pse)
    c.pyapi.decref(gnbij__pse)
    utobo__nrf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rfk__lompk = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ucg__sqbo = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [rfk__lompk])
    srw__bmbe = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    kcnu__lgl = cgutils.get_or_insert_function(c.builder.module, srw__bmbe,
        name='is_pd_int_array')
    qme__yuy = c.builder.call(kcnu__lgl, [obj])
    mkifr__rotjh = c.builder.icmp_unsigned('!=', qme__yuy, qme__yuy.type(0))
    with c.builder.if_else(mkifr__rotjh) as (ppbti__knl, nxamr__vwaqj):
        with ppbti__knl:
            jrj__lhe = c.pyapi.object_getattr_string(obj, '_data')
            utobo__nrf.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), jrj__lhe).value
            uvaxl__xjj = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), uvaxl__xjj).value
            c.pyapi.decref(jrj__lhe)
            c.pyapi.decref(uvaxl__xjj)
            cbjux__ccjo = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            srw__bmbe = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            kcnu__lgl = cgutils.get_or_insert_function(c.builder.module,
                srw__bmbe, name='mask_arr_to_bitmap')
            c.builder.call(kcnu__lgl, [ucg__sqbo.data, cbjux__ccjo.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with nxamr__vwaqj:
            asnwm__xbvb = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            srw__bmbe = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            cwut__zbdw = cgutils.get_or_insert_function(c.builder.module,
                srw__bmbe, name='int_array_from_sequence')
            c.builder.call(cwut__zbdw, [obj, c.builder.bitcast(asnwm__xbvb.
                data, lir.IntType(8).as_pointer()), ucg__sqbo.data])
            utobo__nrf.data = asnwm__xbvb._getvalue()
    utobo__nrf.null_bitmap = ucg__sqbo._getvalue()
    gvwr__iurq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(utobo__nrf._getvalue(), is_error=gvwr__iurq)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    utobo__nrf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        utobo__nrf.data, c.env_manager)
    xmtr__rhclw = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, utobo__nrf.null_bitmap).data
    gnbij__pse = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(gnbij__pse)
    zwyv__arnt = c.context.insert_const_string(c.builder.module, 'numpy')
    exw__obw = c.pyapi.import_module_noblock(zwyv__arnt)
    zdzh__jio = c.pyapi.object_getattr_string(exw__obw, 'bool_')
    mask_arr = c.pyapi.call_method(exw__obw, 'empty', (gnbij__pse, zdzh__jio))
    tcji__oead = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    wyxp__gpfvj = c.pyapi.object_getattr_string(tcji__oead, 'data')
    srvkz__gui = c.builder.inttoptr(c.pyapi.long_as_longlong(wyxp__gpfvj),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as dvu__bgz:
        i = dvu__bgz.index
        qgx__pmm = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        bks__gkmd = c.builder.load(cgutils.gep(c.builder, xmtr__rhclw,
            qgx__pmm))
        gdhh__tepqf = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(bks__gkmd, gdhh__tepqf), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        asd__nuh = cgutils.gep(c.builder, srvkz__gui, i)
        c.builder.store(val, asd__nuh)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        utobo__nrf.null_bitmap)
    zwyv__arnt = c.context.insert_const_string(c.builder.module, 'pandas')
    rxb__vonx = c.pyapi.import_module_noblock(zwyv__arnt)
    ggw__onn = c.pyapi.object_getattr_string(rxb__vonx, 'arrays')
    jnhu__hkgf = c.pyapi.call_method(ggw__onn, 'IntegerArray', (data, mask_arr)
        )
    c.pyapi.decref(rxb__vonx)
    c.pyapi.decref(gnbij__pse)
    c.pyapi.decref(exw__obw)
    c.pyapi.decref(zdzh__jio)
    c.pyapi.decref(tcji__oead)
    c.pyapi.decref(wyxp__gpfvj)
    c.pyapi.decref(ggw__onn)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return jnhu__hkgf


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        txt__jbhgh, azr__rzyuy = args
        utobo__nrf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        utobo__nrf.data = txt__jbhgh
        utobo__nrf.null_bitmap = azr__rzyuy
        context.nrt.incref(builder, signature.args[0], txt__jbhgh)
        context.nrt.incref(builder, signature.args[1], azr__rzyuy)
        return utobo__nrf._getvalue()
    lep__tiqp = IntegerArrayType(data.dtype)
    jtyed__pwp = lep__tiqp(data, null_bitmap)
    return jtyed__pwp, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    yujs__qnpad = np.empty(n, pyval.dtype.type)
    tok__ouk = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        eqeoc__nzhz = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(tok__ouk, i, int(not eqeoc__nzhz))
        if not eqeoc__nzhz:
            yujs__qnpad[i] = s
    dtmju__wse = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), yujs__qnpad)
    zhy__pfvxm = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), tok__ouk)
    return lir.Constant.literal_struct([dtmju__wse, zhy__pfvxm])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lubx__gdt = args[0]
    if equiv_set.has_shape(lubx__gdt):
        return ArrayAnalysis.AnalyzeResult(shape=lubx__gdt, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lubx__gdt = args[0]
    if equiv_set.has_shape(lubx__gdt):
        return ArrayAnalysis.AnalyzeResult(shape=lubx__gdt, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    yujs__qnpad = np.empty(n, dtype)
    bgiu__qwg = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(yujs__qnpad, bgiu__qwg)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            xqmvr__nnbya, engr__xuby = array_getitem_bool_index(A, ind)
            return init_integer_array(xqmvr__nnbya, engr__xuby)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            xqmvr__nnbya, engr__xuby = array_getitem_int_index(A, ind)
            return init_integer_array(xqmvr__nnbya, engr__xuby)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            xqmvr__nnbya, engr__xuby = array_getitem_slice_index(A, ind)
            return init_integer_array(xqmvr__nnbya, engr__xuby)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ptvl__wez = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    vfjct__hdc = isinstance(val, (types.Integer, types.Boolean, types.Float))
    if isinstance(idx, types.Integer):
        if vfjct__hdc:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ptvl__wez)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or vfjct__hdc):
        raise BodoError(ptvl__wez)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            nhuu__uvol = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                nhuu__uvol[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    nhuu__uvol[i] = np.nan
            return nhuu__uvol
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                jflz__meud = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                wyb__dheav = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                cbzz__iofnz = jflz__meud & wyb__dheav
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, cbzz__iofnz)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        rfk__lompk = n + 7 >> 3
        nhuu__uvol = np.empty(rfk__lompk, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            jflz__meud = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            wyb__dheav = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            cbzz__iofnz = jflz__meud & wyb__dheav
            bodo.libs.int_arr_ext.set_bit_to_arr(nhuu__uvol, i, cbzz__iofnz)
        return nhuu__uvol
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for wtw__bmeyh in numba.np.ufunc_db.get_ufuncs():
        wjuf__fqz = create_op_overload(wtw__bmeyh, wtw__bmeyh.nin)
        overload(wtw__bmeyh, no_unliteral=True)(wjuf__fqz)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        wjuf__fqz = create_op_overload(op, 2)
        overload(op)(wjuf__fqz)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        wjuf__fqz = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(wjuf__fqz)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        wjuf__fqz = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(wjuf__fqz)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    ssex__aaf = len(arrs.types)
    ivln__ksjj = 'def f(arrs):\n'
    jnhu__hkgf = ', '.join('arrs[{}]._data'.format(i) for i in range(ssex__aaf)
        )
    ivln__ksjj += '  return ({}{})\n'.format(jnhu__hkgf, ',' if ssex__aaf ==
        1 else '')
    mlzp__ypnpf = {}
    exec(ivln__ksjj, {}, mlzp__ypnpf)
    impl = mlzp__ypnpf['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    ssex__aaf = len(arrs.types)
    xqija__vebyu = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        ssex__aaf))
    ivln__ksjj = 'def f(arrs):\n'
    ivln__ksjj += '  n = {}\n'.format(xqija__vebyu)
    ivln__ksjj += '  n_bytes = (n + 7) >> 3\n'
    ivln__ksjj += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    ivln__ksjj += '  curr_bit = 0\n'
    for i in range(ssex__aaf):
        ivln__ksjj += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        ivln__ksjj += '  for j in range(len(arrs[{}])):\n'.format(i)
        ivln__ksjj += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        ivln__ksjj += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        ivln__ksjj += '    curr_bit += 1\n'
    ivln__ksjj += '  return new_mask\n'
    mlzp__ypnpf = {}
    exec(ivln__ksjj, {'np': np, 'bodo': bodo}, mlzp__ypnpf)
    impl = mlzp__ypnpf['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    cjm__agm = dict(skipna=skipna, min_count=min_count)
    gvr__kheus = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', cjm__agm, gvr__kheus)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        gdhh__tepqf = []
        vxmpa__kuair = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not vxmpa__kuair:
                    data.append(dtype(1))
                    gdhh__tepqf.append(False)
                    vxmpa__kuair = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                gdhh__tepqf.append(True)
        xqmvr__nnbya = np.array(data)
        n = len(xqmvr__nnbya)
        rfk__lompk = n + 7 >> 3
        engr__xuby = np.empty(rfk__lompk, np.uint8)
        for xgoqi__pyed in range(n):
            set_bit_to_arr(engr__xuby, xgoqi__pyed, gdhh__tepqf[xgoqi__pyed])
        return init_integer_array(xqmvr__nnbya, engr__xuby)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    uij__qwm = numba.core.registry.cpu_target.typing_context
    kmjn__jvtyl = uij__qwm.resolve_function_type(op, (types.Array(A.dtype, 
        1, 'C'),), {}).return_type
    kmjn__jvtyl = to_nullable_type(kmjn__jvtyl)

    def impl(A):
        n = len(A)
        tbsh__hewp = bodo.utils.utils.alloc_type(n, kmjn__jvtyl, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(tbsh__hewp, i)
                continue
            tbsh__hewp[i] = op(A[i])
        return tbsh__hewp
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    wuj__wmkc = isinstance(lhs, (types.Number, types.Boolean))
    vlxkq__cbzx = isinstance(rhs, (types.Number, types.Boolean))
    allk__tlcg = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    owe__otmx = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    uij__qwm = numba.core.registry.cpu_target.typing_context
    kmjn__jvtyl = uij__qwm.resolve_function_type(op, (allk__tlcg, owe__otmx
        ), {}).return_type
    kmjn__jvtyl = to_nullable_type(kmjn__jvtyl)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    euo__wnok = 'lhs' if wuj__wmkc else 'lhs[i]'
    kbr__gmzo = 'rhs' if vlxkq__cbzx else 'rhs[i]'
    mvx__hrxrt = ('False' if wuj__wmkc else
        'bodo.libs.array_kernels.isna(lhs, i)')
    ufjdz__zlr = ('False' if vlxkq__cbzx else
        'bodo.libs.array_kernels.isna(rhs, i)')
    ivln__ksjj = 'def impl(lhs, rhs):\n'
    ivln__ksjj += '  n = len({})\n'.format('lhs' if not wuj__wmkc else 'rhs')
    if inplace:
        ivln__ksjj += '  out_arr = {}\n'.format('lhs' if not wuj__wmkc else
            'rhs')
    else:
        ivln__ksjj += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    ivln__ksjj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ivln__ksjj += '    if ({}\n'.format(mvx__hrxrt)
    ivln__ksjj += '        or {}):\n'.format(ufjdz__zlr)
    ivln__ksjj += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    ivln__ksjj += '      continue\n'
    ivln__ksjj += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(euo__wnok, kbr__gmzo))
    ivln__ksjj += '  return out_arr\n'
    mlzp__ypnpf = {}
    exec(ivln__ksjj, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        kmjn__jvtyl, 'op': op}, mlzp__ypnpf)
    impl = mlzp__ypnpf['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        wuj__wmkc = lhs in [pd_timedelta_type]
        vlxkq__cbzx = rhs in [pd_timedelta_type]
        if wuj__wmkc:

            def impl(lhs, rhs):
                n = len(rhs)
                tbsh__hewp = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(tbsh__hewp, i)
                        continue
                    tbsh__hewp[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return tbsh__hewp
            return impl
        elif vlxkq__cbzx:

            def impl(lhs, rhs):
                n = len(lhs)
                tbsh__hewp = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(tbsh__hewp, i)
                        continue
                    tbsh__hewp[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return tbsh__hewp
            return impl
    return impl
