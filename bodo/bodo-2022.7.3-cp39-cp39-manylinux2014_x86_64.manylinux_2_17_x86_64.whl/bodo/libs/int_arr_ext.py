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
        tqqj__keojd = int(np.log2(self.dtype.bitwidth // 8))
        tmwr__ofjzx = 0 if self.dtype.signed else 4
        idx = tqqj__keojd + tmwr__ofjzx
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ohsew__nyd = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ohsew__nyd)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    opifc__zrq = 8 * val.dtype.itemsize
    hriaw__qnisk = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(hriaw__qnisk, opifc__zrq))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        zilrm__erigp = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(zilrm__erigp)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    uvzu__dzs = c.context.insert_const_string(c.builder.module, 'pandas')
    jfosb__qqky = c.pyapi.import_module_noblock(uvzu__dzs)
    xymz__avfk = c.pyapi.call_method(jfosb__qqky, str(typ)[:-2], ())
    c.pyapi.decref(jfosb__qqky)
    return xymz__avfk


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    opifc__zrq = 8 * val.itemsize
    hriaw__qnisk = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(hriaw__qnisk, opifc__zrq))
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
    gcnw__kpssy = n + 7 >> 3
    ixxxi__ihoj = np.empty(gcnw__kpssy, np.uint8)
    for i in range(n):
        fcs__mmkjf = i // 8
        ixxxi__ihoj[fcs__mmkjf] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            ixxxi__ihoj[fcs__mmkjf]) & kBitmask[i % 8]
    return ixxxi__ihoj


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    nmi__ozdei = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(nmi__ozdei)
    c.pyapi.decref(nmi__ozdei)
    ndf__mgcri = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gcnw__kpssy = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    iuqvb__tci = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [gcnw__kpssy])
    lnfzc__pygf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    vkbjh__xbuq = cgutils.get_or_insert_function(c.builder.module,
        lnfzc__pygf, name='is_pd_int_array')
    qwr__zouh = c.builder.call(vkbjh__xbuq, [obj])
    fxqri__jexme = c.builder.icmp_unsigned('!=', qwr__zouh, qwr__zouh.type(0))
    with c.builder.if_else(fxqri__jexme) as (lxtr__gtfzg, euyu__yycr):
        with lxtr__gtfzg:
            bruw__otosh = c.pyapi.object_getattr_string(obj, '_data')
            ndf__mgcri.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), bruw__otosh).value
            naxm__hgk = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), naxm__hgk).value
            c.pyapi.decref(bruw__otosh)
            c.pyapi.decref(naxm__hgk)
            vwjou__uyid = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            lnfzc__pygf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            vkbjh__xbuq = cgutils.get_or_insert_function(c.builder.module,
                lnfzc__pygf, name='mask_arr_to_bitmap')
            c.builder.call(vkbjh__xbuq, [iuqvb__tci.data, vwjou__uyid.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with euyu__yycr:
            lmnj__hjxy = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            lnfzc__pygf = lir.FunctionType(lir.IntType(32), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            udjj__zcu = cgutils.get_or_insert_function(c.builder.module,
                lnfzc__pygf, name='int_array_from_sequence')
            c.builder.call(udjj__zcu, [obj, c.builder.bitcast(lmnj__hjxy.
                data, lir.IntType(8).as_pointer()), iuqvb__tci.data])
            ndf__mgcri.data = lmnj__hjxy._getvalue()
    ndf__mgcri.null_bitmap = iuqvb__tci._getvalue()
    mwgcd__xgvci = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ndf__mgcri._getvalue(), is_error=mwgcd__xgvci)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    ndf__mgcri = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ndf__mgcri.data, c.env_manager)
    rsgvm__jzdp = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ndf__mgcri.null_bitmap).data
    nmi__ozdei = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(nmi__ozdei)
    uvzu__dzs = c.context.insert_const_string(c.builder.module, 'numpy')
    jjca__njb = c.pyapi.import_module_noblock(uvzu__dzs)
    bsvyo__hhsp = c.pyapi.object_getattr_string(jjca__njb, 'bool_')
    mask_arr = c.pyapi.call_method(jjca__njb, 'empty', (nmi__ozdei,
        bsvyo__hhsp))
    rdo__zcsd = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    hmeu__jqtc = c.pyapi.object_getattr_string(rdo__zcsd, 'data')
    mcbgj__dxzh = c.builder.inttoptr(c.pyapi.long_as_longlong(hmeu__jqtc),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as vljb__mogvd:
        i = vljb__mogvd.index
        dgbb__jcp = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        mtpg__jdtl = c.builder.load(cgutils.gep(c.builder, rsgvm__jzdp,
            dgbb__jcp))
        qidlx__qyu = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(mtpg__jdtl, qidlx__qyu), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        gqljo__aawz = cgutils.gep(c.builder, mcbgj__dxzh, i)
        c.builder.store(val, gqljo__aawz)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        ndf__mgcri.null_bitmap)
    uvzu__dzs = c.context.insert_const_string(c.builder.module, 'pandas')
    jfosb__qqky = c.pyapi.import_module_noblock(uvzu__dzs)
    tbtj__nwcp = c.pyapi.object_getattr_string(jfosb__qqky, 'arrays')
    xymz__avfk = c.pyapi.call_method(tbtj__nwcp, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(jfosb__qqky)
    c.pyapi.decref(nmi__ozdei)
    c.pyapi.decref(jjca__njb)
    c.pyapi.decref(bsvyo__hhsp)
    c.pyapi.decref(rdo__zcsd)
    c.pyapi.decref(hmeu__jqtc)
    c.pyapi.decref(tbtj__nwcp)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return xymz__avfk


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        tqgx__hnrm, zfs__odja = args
        ndf__mgcri = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ndf__mgcri.data = tqgx__hnrm
        ndf__mgcri.null_bitmap = zfs__odja
        context.nrt.incref(builder, signature.args[0], tqgx__hnrm)
        context.nrt.incref(builder, signature.args[1], zfs__odja)
        return ndf__mgcri._getvalue()
    frl__sptb = IntegerArrayType(data.dtype)
    uqza__xlok = frl__sptb(data, null_bitmap)
    return uqza__xlok, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    drry__ria = np.empty(n, pyval.dtype.type)
    edk__ieojz = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        xloz__woag = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(edk__ieojz, i, int(not xloz__woag)
            )
        if not xloz__woag:
            drry__ria[i] = s
    eht__jljv = context.get_constant_generic(builder, types.Array(typ.dtype,
        1, 'C'), drry__ria)
    fedsc__bevt = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), edk__ieojz)
    return lir.Constant.literal_struct([eht__jljv, fedsc__bevt])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    oiiqi__ylx = args[0]
    if equiv_set.has_shape(oiiqi__ylx):
        return ArrayAnalysis.AnalyzeResult(shape=oiiqi__ylx, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    oiiqi__ylx = args[0]
    if equiv_set.has_shape(oiiqi__ylx):
        return ArrayAnalysis.AnalyzeResult(shape=oiiqi__ylx, pre=[])
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
    drry__ria = np.empty(n, dtype)
    clsiy__vbu = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(drry__ria, clsiy__vbu)


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
            vgxlt__nwo, yivpe__kjiaj = array_getitem_bool_index(A, ind)
            return init_integer_array(vgxlt__nwo, yivpe__kjiaj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            vgxlt__nwo, yivpe__kjiaj = array_getitem_int_index(A, ind)
            return init_integer_array(vgxlt__nwo, yivpe__kjiaj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            vgxlt__nwo, yivpe__kjiaj = array_getitem_slice_index(A, ind)
            return init_integer_array(vgxlt__nwo, yivpe__kjiaj)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    zpk__cgoxb = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    kxp__jjju = isinstance(val, (types.Integer, types.Boolean, types.Float))
    if isinstance(idx, types.Integer):
        if kxp__jjju:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(zpk__cgoxb)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean, types.Float)) or kxp__jjju):
        raise BodoError(zpk__cgoxb)
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
            rmsds__bvypk = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                rmsds__bvypk[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    rmsds__bvypk[i] = np.nan
            return rmsds__bvypk
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
                fewus__kng = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                tmz__ozn = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                bbij__yfwe = fewus__kng & tmz__ozn
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, bbij__yfwe)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        gcnw__kpssy = n + 7 >> 3
        rmsds__bvypk = np.empty(gcnw__kpssy, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            fewus__kng = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            tmz__ozn = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            bbij__yfwe = fewus__kng & tmz__ozn
            bodo.libs.int_arr_ext.set_bit_to_arr(rmsds__bvypk, i, bbij__yfwe)
        return rmsds__bvypk
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
    for xliul__ybv in numba.np.ufunc_db.get_ufuncs():
        qpe__wqhfk = create_op_overload(xliul__ybv, xliul__ybv.nin)
        overload(xliul__ybv, no_unliteral=True)(qpe__wqhfk)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        qpe__wqhfk = create_op_overload(op, 2)
        overload(op)(qpe__wqhfk)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        qpe__wqhfk = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(qpe__wqhfk)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        qpe__wqhfk = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(qpe__wqhfk)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    mqbha__mql = len(arrs.types)
    inivk__muukc = 'def f(arrs):\n'
    xymz__avfk = ', '.join('arrs[{}]._data'.format(i) for i in range(
        mqbha__mql))
    inivk__muukc += '  return ({}{})\n'.format(xymz__avfk, ',' if 
        mqbha__mql == 1 else '')
    xztv__rshx = {}
    exec(inivk__muukc, {}, xztv__rshx)
    impl = xztv__rshx['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    mqbha__mql = len(arrs.types)
    lrcc__mmm = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        mqbha__mql))
    inivk__muukc = 'def f(arrs):\n'
    inivk__muukc += '  n = {}\n'.format(lrcc__mmm)
    inivk__muukc += '  n_bytes = (n + 7) >> 3\n'
    inivk__muukc += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    inivk__muukc += '  curr_bit = 0\n'
    for i in range(mqbha__mql):
        inivk__muukc += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        inivk__muukc += '  for j in range(len(arrs[{}])):\n'.format(i)
        inivk__muukc += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        inivk__muukc += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        inivk__muukc += '    curr_bit += 1\n'
    inivk__muukc += '  return new_mask\n'
    xztv__rshx = {}
    exec(inivk__muukc, {'np': np, 'bodo': bodo}, xztv__rshx)
    impl = xztv__rshx['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    kre__mljau = dict(skipna=skipna, min_count=min_count)
    akro__aowz = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', kre__mljau, akro__aowz)

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
        qidlx__qyu = []
        gykj__eazxq = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not gykj__eazxq:
                    data.append(dtype(1))
                    qidlx__qyu.append(False)
                    gykj__eazxq = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                qidlx__qyu.append(True)
        vgxlt__nwo = np.array(data)
        n = len(vgxlt__nwo)
        gcnw__kpssy = n + 7 >> 3
        yivpe__kjiaj = np.empty(gcnw__kpssy, np.uint8)
        for wtjb__ajnxc in range(n):
            set_bit_to_arr(yivpe__kjiaj, wtjb__ajnxc, qidlx__qyu[wtjb__ajnxc])
        return init_integer_array(vgxlt__nwo, yivpe__kjiaj)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    suat__ooxe = numba.core.registry.cpu_target.typing_context
    lgv__rnnd = suat__ooxe.resolve_function_type(op, (types.Array(A.dtype, 
        1, 'C'),), {}).return_type
    lgv__rnnd = to_nullable_type(lgv__rnnd)

    def impl(A):
        n = len(A)
        ebjry__zyz = bodo.utils.utils.alloc_type(n, lgv__rnnd, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(ebjry__zyz, i)
                continue
            ebjry__zyz[i] = op(A[i])
        return ebjry__zyz
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    zuz__cfdk = isinstance(lhs, (types.Number, types.Boolean))
    cqeyc__wuuf = isinstance(rhs, (types.Number, types.Boolean))
    olnq__vxud = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    zslh__rkbug = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    suat__ooxe = numba.core.registry.cpu_target.typing_context
    lgv__rnnd = suat__ooxe.resolve_function_type(op, (olnq__vxud,
        zslh__rkbug), {}).return_type
    lgv__rnnd = to_nullable_type(lgv__rnnd)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    fgkep__aid = 'lhs' if zuz__cfdk else 'lhs[i]'
    txd__ctd = 'rhs' if cqeyc__wuuf else 'rhs[i]'
    egikb__wikdf = ('False' if zuz__cfdk else
        'bodo.libs.array_kernels.isna(lhs, i)')
    pgf__szo = ('False' if cqeyc__wuuf else
        'bodo.libs.array_kernels.isna(rhs, i)')
    inivk__muukc = 'def impl(lhs, rhs):\n'
    inivk__muukc += '  n = len({})\n'.format('lhs' if not zuz__cfdk else 'rhs')
    if inplace:
        inivk__muukc += '  out_arr = {}\n'.format('lhs' if not zuz__cfdk else
            'rhs')
    else:
        inivk__muukc += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    inivk__muukc += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    inivk__muukc += '    if ({}\n'.format(egikb__wikdf)
    inivk__muukc += '        or {}):\n'.format(pgf__szo)
    inivk__muukc += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    inivk__muukc += '      continue\n'
    inivk__muukc += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(fgkep__aid, txd__ctd))
    inivk__muukc += '  return out_arr\n'
    xztv__rshx = {}
    exec(inivk__muukc, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        lgv__rnnd, 'op': op}, xztv__rshx)
    impl = xztv__rshx['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        zuz__cfdk = lhs in [pd_timedelta_type]
        cqeyc__wuuf = rhs in [pd_timedelta_type]
        if zuz__cfdk:

            def impl(lhs, rhs):
                n = len(rhs)
                ebjry__zyz = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(ebjry__zyz, i)
                        continue
                    ebjry__zyz[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return ebjry__zyz
            return impl
        elif cqeyc__wuuf:

            def impl(lhs, rhs):
                n = len(lhs)
                ebjry__zyz = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(ebjry__zyz, i)
                        continue
                    ebjry__zyz[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return ebjry__zyz
            return impl
    return impl
