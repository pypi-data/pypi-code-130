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
        fjts__xwre = int(np.log2(self.dtype.bitwidth // 8))
        croi__adqe = 0 if self.dtype.signed else 4
        idx = fjts__xwre + croi__adqe
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        doz__hns = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, doz__hns)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    accxr__anih = 8 * val.dtype.itemsize
    totd__tvbnd = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(totd__tvbnd, accxr__anih))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        znowr__cwl = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(znowr__cwl)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    wsqka__maw = c.context.insert_const_string(c.builder.module, 'pandas')
    tnf__moi = c.pyapi.import_module_noblock(wsqka__maw)
    smt__cagsv = c.pyapi.call_method(tnf__moi, str(typ)[:-2], ())
    c.pyapi.decref(tnf__moi)
    return smt__cagsv


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    accxr__anih = 8 * val.itemsize
    totd__tvbnd = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(totd__tvbnd, accxr__anih))
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
    fgeg__lmjpg = n + 7 >> 3
    wpyom__pjyd = np.empty(fgeg__lmjpg, np.uint8)
    for i in range(n):
        qhtp__spgrm = i // 8
        wpyom__pjyd[qhtp__spgrm] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            wpyom__pjyd[qhtp__spgrm]) & kBitmask[i % 8]
    return wpyom__pjyd


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    rue__qvxnj = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(rue__qvxnj)
    c.pyapi.decref(rue__qvxnj)
    tswg__aydh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fgeg__lmjpg = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    cam__aqk = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types.
        Array(types.uint8, 1, 'C'), [fgeg__lmjpg])
    iwz__fvxft = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    venlf__efgxt = cgutils.get_or_insert_function(c.builder.module,
        iwz__fvxft, name='is_pd_int_array')
    klhe__epy = c.builder.call(venlf__efgxt, [obj])
    pwne__jmio = c.builder.icmp_unsigned('!=', klhe__epy, klhe__epy.type(0))
    with c.builder.if_else(pwne__jmio) as (mbki__oaf, zltd__cryp):
        with mbki__oaf:
            pjra__ecvss = c.pyapi.object_getattr_string(obj, '_data')
            tswg__aydh.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), pjra__ecvss).value
            rwuvw__bnd = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), rwuvw__bnd).value
            c.pyapi.decref(pjra__ecvss)
            c.pyapi.decref(rwuvw__bnd)
            skdcx__tros = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            iwz__fvxft = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            venlf__efgxt = cgutils.get_or_insert_function(c.builder.module,
                iwz__fvxft, name='mask_arr_to_bitmap')
            c.builder.call(venlf__efgxt, [cam__aqk.data, skdcx__tros.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with zltd__cryp:
            balwu__uylmj = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            iwz__fvxft = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            onr__hjm = cgutils.get_or_insert_function(c.builder.module,
                iwz__fvxft, name='int_array_from_sequence')
            c.builder.call(onr__hjm, [obj, c.builder.bitcast(balwu__uylmj.
                data, lir.IntType(8).as_pointer()), cam__aqk.data])
            tswg__aydh.data = balwu__uylmj._getvalue()
    tswg__aydh.null_bitmap = cam__aqk._getvalue()
    nbrk__ekt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tswg__aydh._getvalue(), is_error=nbrk__ekt)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    tswg__aydh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        tswg__aydh.data, c.env_manager)
    zdr__hvgk = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, tswg__aydh.null_bitmap).data
    rue__qvxnj = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(rue__qvxnj)
    wsqka__maw = c.context.insert_const_string(c.builder.module, 'numpy')
    blcxk__rnpkc = c.pyapi.import_module_noblock(wsqka__maw)
    ulh__jxv = c.pyapi.object_getattr_string(blcxk__rnpkc, 'bool_')
    mask_arr = c.pyapi.call_method(blcxk__rnpkc, 'empty', (rue__qvxnj,
        ulh__jxv))
    baxfh__zag = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    nhq__lptyn = c.pyapi.object_getattr_string(baxfh__zag, 'data')
    vvtc__nlhuc = c.builder.inttoptr(c.pyapi.long_as_longlong(nhq__lptyn),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as saiya__ysjfd:
        i = saiya__ysjfd.index
        jtl__slbb = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        oqngh__daq = c.builder.load(cgutils.gep(c.builder, zdr__hvgk,
            jtl__slbb))
        nnof__otdgw = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(oqngh__daq, nnof__otdgw), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        ffacd__mur = cgutils.gep(c.builder, vvtc__nlhuc, i)
        c.builder.store(val, ffacd__mur)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        tswg__aydh.null_bitmap)
    wsqka__maw = c.context.insert_const_string(c.builder.module, 'pandas')
    tnf__moi = c.pyapi.import_module_noblock(wsqka__maw)
    yqku__jpt = c.pyapi.object_getattr_string(tnf__moi, 'arrays')
    smt__cagsv = c.pyapi.call_method(yqku__jpt, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(tnf__moi)
    c.pyapi.decref(rue__qvxnj)
    c.pyapi.decref(blcxk__rnpkc)
    c.pyapi.decref(ulh__jxv)
    c.pyapi.decref(baxfh__zag)
    c.pyapi.decref(nhq__lptyn)
    c.pyapi.decref(yqku__jpt)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return smt__cagsv


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        mggih__skzz, yfylh__ledbo = args
        tswg__aydh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        tswg__aydh.data = mggih__skzz
        tswg__aydh.null_bitmap = yfylh__ledbo
        context.nrt.incref(builder, signature.args[0], mggih__skzz)
        context.nrt.incref(builder, signature.args[1], yfylh__ledbo)
        return tswg__aydh._getvalue()
    uzv__zqi = IntegerArrayType(data.dtype)
    yznoh__octoi = uzv__zqi(data, null_bitmap)
    return yznoh__octoi, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    hgp__maze = np.empty(n, pyval.dtype.type)
    cje__kkjd = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        zuarz__olmba = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(cje__kkjd, i, int(not
            zuarz__olmba))
        if not zuarz__olmba:
            hgp__maze[i] = s
    ydlmz__vuro = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), hgp__maze)
    attr__efz = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), cje__kkjd)
    return lir.Constant.literal_struct([ydlmz__vuro, attr__efz])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    qnhiu__xdpjt = args[0]
    if equiv_set.has_shape(qnhiu__xdpjt):
        return ArrayAnalysis.AnalyzeResult(shape=qnhiu__xdpjt, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qnhiu__xdpjt = args[0]
    if equiv_set.has_shape(qnhiu__xdpjt):
        return ArrayAnalysis.AnalyzeResult(shape=qnhiu__xdpjt, pre=[])
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
    hgp__maze = np.empty(n, dtype)
    lxaje__frbw = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(hgp__maze, lxaje__frbw)


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
            tcv__oti, blpus__pynsl = array_getitem_bool_index(A, ind)
            return init_integer_array(tcv__oti, blpus__pynsl)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            tcv__oti, blpus__pynsl = array_getitem_int_index(A, ind)
            return init_integer_array(tcv__oti, blpus__pynsl)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            tcv__oti, blpus__pynsl = array_getitem_slice_index(A, ind)
            return init_integer_array(tcv__oti, blpus__pynsl)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    nxam__vfjq = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    oldxi__xgw = isinstance(val, (types.Integer, types.Boolean, types.Float))
    if isinstance(idx, types.Integer):
        if oldxi__xgw:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(nxam__vfjq)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or oldxi__xgw):
        raise BodoError(nxam__vfjq)
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
            cjal__vzhiq = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                cjal__vzhiq[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    cjal__vzhiq[i] = np.nan
            return cjal__vzhiq
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
                sln__zrxe = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                pkax__zqis = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                ldtu__mxcg = sln__zrxe & pkax__zqis
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, ldtu__mxcg)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        fgeg__lmjpg = n + 7 >> 3
        cjal__vzhiq = np.empty(fgeg__lmjpg, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            sln__zrxe = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            pkax__zqis = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            ldtu__mxcg = sln__zrxe & pkax__zqis
            bodo.libs.int_arr_ext.set_bit_to_arr(cjal__vzhiq, i, ldtu__mxcg)
        return cjal__vzhiq
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
    for ggpi__yyfa in numba.np.ufunc_db.get_ufuncs():
        noub__zwi = create_op_overload(ggpi__yyfa, ggpi__yyfa.nin)
        overload(ggpi__yyfa, no_unliteral=True)(noub__zwi)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        noub__zwi = create_op_overload(op, 2)
        overload(op)(noub__zwi)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        noub__zwi = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(noub__zwi)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        noub__zwi = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(noub__zwi)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    vxile__ogqj = len(arrs.types)
    etuq__dttqk = 'def f(arrs):\n'
    smt__cagsv = ', '.join('arrs[{}]._data'.format(i) for i in range(
        vxile__ogqj))
    etuq__dttqk += '  return ({}{})\n'.format(smt__cagsv, ',' if 
        vxile__ogqj == 1 else '')
    fbkcd__cpu = {}
    exec(etuq__dttqk, {}, fbkcd__cpu)
    impl = fbkcd__cpu['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    vxile__ogqj = len(arrs.types)
    qdvc__rgquu = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        vxile__ogqj))
    etuq__dttqk = 'def f(arrs):\n'
    etuq__dttqk += '  n = {}\n'.format(qdvc__rgquu)
    etuq__dttqk += '  n_bytes = (n + 7) >> 3\n'
    etuq__dttqk += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    etuq__dttqk += '  curr_bit = 0\n'
    for i in range(vxile__ogqj):
        etuq__dttqk += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        etuq__dttqk += '  for j in range(len(arrs[{}])):\n'.format(i)
        etuq__dttqk += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        etuq__dttqk += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        etuq__dttqk += '    curr_bit += 1\n'
    etuq__dttqk += '  return new_mask\n'
    fbkcd__cpu = {}
    exec(etuq__dttqk, {'np': np, 'bodo': bodo}, fbkcd__cpu)
    impl = fbkcd__cpu['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    rrsai__jxvid = dict(skipna=skipna, min_count=min_count)
    akswm__sqhgq = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', rrsai__jxvid, akswm__sqhgq)

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
        nnof__otdgw = []
        iivu__sgd = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not iivu__sgd:
                    data.append(dtype(1))
                    nnof__otdgw.append(False)
                    iivu__sgd = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                nnof__otdgw.append(True)
        tcv__oti = np.array(data)
        n = len(tcv__oti)
        fgeg__lmjpg = n + 7 >> 3
        blpus__pynsl = np.empty(fgeg__lmjpg, np.uint8)
        for edye__qtd in range(n):
            set_bit_to_arr(blpus__pynsl, edye__qtd, nnof__otdgw[edye__qtd])
        return init_integer_array(tcv__oti, blpus__pynsl)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    rbyzu__uzvwk = numba.core.registry.cpu_target.typing_context
    tzy__ohi = rbyzu__uzvwk.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    tzy__ohi = to_nullable_type(tzy__ohi)

    def impl(A):
        n = len(A)
        wxx__quci = bodo.utils.utils.alloc_type(n, tzy__ohi, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(wxx__quci, i)
                continue
            wxx__quci[i] = op(A[i])
        return wxx__quci
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    hrc__pageb = isinstance(lhs, (types.Number, types.Boolean))
    srzk__zib = isinstance(rhs, (types.Number, types.Boolean))
    bylnf__jpzx = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    gfaz__lpl = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    rbyzu__uzvwk = numba.core.registry.cpu_target.typing_context
    tzy__ohi = rbyzu__uzvwk.resolve_function_type(op, (bylnf__jpzx,
        gfaz__lpl), {}).return_type
    tzy__ohi = to_nullable_type(tzy__ohi)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    ksr__zgn = 'lhs' if hrc__pageb else 'lhs[i]'
    uhuux__ulkud = 'rhs' if srzk__zib else 'rhs[i]'
    jrz__kesr = ('False' if hrc__pageb else
        'bodo.libs.array_kernels.isna(lhs, i)')
    xcy__rmcn = ('False' if srzk__zib else
        'bodo.libs.array_kernels.isna(rhs, i)')
    etuq__dttqk = 'def impl(lhs, rhs):\n'
    etuq__dttqk += '  n = len({})\n'.format('lhs' if not hrc__pageb else 'rhs')
    if inplace:
        etuq__dttqk += '  out_arr = {}\n'.format('lhs' if not hrc__pageb else
            'rhs')
    else:
        etuq__dttqk += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    etuq__dttqk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    etuq__dttqk += '    if ({}\n'.format(jrz__kesr)
    etuq__dttqk += '        or {}):\n'.format(xcy__rmcn)
    etuq__dttqk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    etuq__dttqk += '      continue\n'
    etuq__dttqk += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(ksr__zgn, uhuux__ulkud))
    etuq__dttqk += '  return out_arr\n'
    fbkcd__cpu = {}
    exec(etuq__dttqk, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        tzy__ohi, 'op': op}, fbkcd__cpu)
    impl = fbkcd__cpu['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        hrc__pageb = lhs in [pd_timedelta_type]
        srzk__zib = rhs in [pd_timedelta_type]
        if hrc__pageb:

            def impl(lhs, rhs):
                n = len(rhs)
                wxx__quci = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(wxx__quci, i)
                        continue
                    wxx__quci[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return wxx__quci
            return impl
        elif srzk__zib:

            def impl(lhs, rhs):
                n = len(lhs)
                wxx__quci = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(wxx__quci, i)
                        continue
                    wxx__quci[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return wxx__quci
            return impl
    return impl
