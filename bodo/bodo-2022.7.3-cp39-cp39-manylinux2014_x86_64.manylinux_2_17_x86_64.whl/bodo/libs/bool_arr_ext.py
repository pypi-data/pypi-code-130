"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gyiq__rrx = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, gyiq__rrx)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    mmehe__gvbfs = c.context.insert_const_string(c.builder.module, 'pandas')
    iei__zhk = c.pyapi.import_module_noblock(mmehe__gvbfs)
    ofpn__tgtg = c.pyapi.call_method(iei__zhk, 'BooleanDtype', ())
    c.pyapi.decref(iei__zhk)
    return ofpn__tgtg


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    tpt__osunk = n + 7 >> 3
    return np.full(tpt__osunk, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    impr__uct = c.context.typing_context.resolve_value_type(func)
    wiqh__akxm = impr__uct.get_call_type(c.context.typing_context, arg_typs, {}
        )
    dpub__huneb = c.context.get_function(impr__uct, wiqh__akxm)
    qjdml__drdu = c.context.call_conv.get_function_type(wiqh__akxm.
        return_type, wiqh__akxm.args)
    raw__wbwm = c.builder.module
    hdc__sods = lir.Function(raw__wbwm, qjdml__drdu, name=raw__wbwm.
        get_unique_name('.func_conv'))
    hdc__sods.linkage = 'internal'
    mlofy__nyv = lir.IRBuilder(hdc__sods.append_basic_block())
    gxyt__airc = c.context.call_conv.decode_arguments(mlofy__nyv,
        wiqh__akxm.args, hdc__sods)
    ywyvi__vepf = dpub__huneb(mlofy__nyv, gxyt__airc)
    c.context.call_conv.return_value(mlofy__nyv, ywyvi__vepf)
    pllcf__whs, xmt__ghtkn = c.context.call_conv.call_function(c.builder,
        hdc__sods, wiqh__akxm.return_type, wiqh__akxm.args, args)
    return xmt__ghtkn


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    vye__nopz = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(vye__nopz)
    c.pyapi.decref(vye__nopz)
    qjdml__drdu = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    wxdrm__qvpj = cgutils.get_or_insert_function(c.builder.module,
        qjdml__drdu, name='is_bool_array')
    qjdml__drdu = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    hdc__sods = cgutils.get_or_insert_function(c.builder.module,
        qjdml__drdu, name='is_pd_boolean_array')
    ooomm__tvk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bnran__duf = c.builder.call(hdc__sods, [obj])
    ijlll__aequz = c.builder.icmp_unsigned('!=', bnran__duf, bnran__duf.type(0)
        )
    with c.builder.if_else(ijlll__aequz) as (zccg__nouvp, cyild__aaoxx):
        with zccg__nouvp:
            ozti__iwp = c.pyapi.object_getattr_string(obj, '_data')
            ooomm__tvk.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), ozti__iwp).value
            upx__uwwo = c.pyapi.object_getattr_string(obj, '_mask')
            tsuv__ktfl = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), upx__uwwo).value
            tpt__osunk = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            hwy__mqqp = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, tsuv__ktfl)
            qhtw__rkkl = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [tpt__osunk])
            qjdml__drdu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            hdc__sods = cgutils.get_or_insert_function(c.builder.module,
                qjdml__drdu, name='mask_arr_to_bitmap')
            c.builder.call(hdc__sods, [qhtw__rkkl.data, hwy__mqqp.data, n])
            ooomm__tvk.null_bitmap = qhtw__rkkl._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), tsuv__ktfl)
            c.pyapi.decref(ozti__iwp)
            c.pyapi.decref(upx__uwwo)
        with cyild__aaoxx:
            owtm__gsblb = c.builder.call(wxdrm__qvpj, [obj])
            tdcdf__nlzp = c.builder.icmp_unsigned('!=', owtm__gsblb,
                owtm__gsblb.type(0))
            with c.builder.if_else(tdcdf__nlzp) as (evs__zdo, usvsr__iirg):
                with evs__zdo:
                    ooomm__tvk.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    ooomm__tvk.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with usvsr__iirg:
                    ooomm__tvk.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    tpt__osunk = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    ooomm__tvk.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [tpt__osunk])._getvalue()
                    alm__ecbbb = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, ooomm__tvk.data
                        ).data
                    hnk__ftk = c.context.make_array(types.Array(types.uint8,
                        1, 'C'))(c.context, c.builder, ooomm__tvk.null_bitmap
                        ).data
                    qjdml__drdu = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    hdc__sods = cgutils.get_or_insert_function(c.builder.
                        module, qjdml__drdu, name='unbox_bool_array_obj')
                    c.builder.call(hdc__sods, [obj, alm__ecbbb, hnk__ftk, n])
    return NativeValue(ooomm__tvk._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    ooomm__tvk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ooomm__tvk.data, c.env_manager)
    dyw__zqnf = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ooomm__tvk.null_bitmap).data
    vye__nopz = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(vye__nopz)
    mmehe__gvbfs = c.context.insert_const_string(c.builder.module, 'numpy')
    jsl__nisq = c.pyapi.import_module_noblock(mmehe__gvbfs)
    ftp__lrm = c.pyapi.object_getattr_string(jsl__nisq, 'bool_')
    tsuv__ktfl = c.pyapi.call_method(jsl__nisq, 'empty', (vye__nopz, ftp__lrm))
    hgp__lrqme = c.pyapi.object_getattr_string(tsuv__ktfl, 'ctypes')
    ejqkx__rkyk = c.pyapi.object_getattr_string(hgp__lrqme, 'data')
    nbfi__jos = c.builder.inttoptr(c.pyapi.long_as_longlong(ejqkx__rkyk),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as myhc__vjc:
        jwhk__ngany = myhc__vjc.index
        xzsif__ycoja = c.builder.lshr(jwhk__ngany, lir.Constant(lir.IntType
            (64), 3))
        tjfwe__amuep = c.builder.load(cgutils.gep(c.builder, dyw__zqnf,
            xzsif__ycoja))
        ubb__poxzf = c.builder.trunc(c.builder.and_(jwhk__ngany, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(tjfwe__amuep, ubb__poxzf), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        wgmbw__aqitb = cgutils.gep(c.builder, nbfi__jos, jwhk__ngany)
        c.builder.store(val, wgmbw__aqitb)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        ooomm__tvk.null_bitmap)
    mmehe__gvbfs = c.context.insert_const_string(c.builder.module, 'pandas')
    iei__zhk = c.pyapi.import_module_noblock(mmehe__gvbfs)
    ytzb__xacji = c.pyapi.object_getattr_string(iei__zhk, 'arrays')
    ofpn__tgtg = c.pyapi.call_method(ytzb__xacji, 'BooleanArray', (data,
        tsuv__ktfl))
    c.pyapi.decref(iei__zhk)
    c.pyapi.decref(vye__nopz)
    c.pyapi.decref(jsl__nisq)
    c.pyapi.decref(ftp__lrm)
    c.pyapi.decref(hgp__lrqme)
    c.pyapi.decref(ejqkx__rkyk)
    c.pyapi.decref(ytzb__xacji)
    c.pyapi.decref(data)
    c.pyapi.decref(tsuv__ktfl)
    return ofpn__tgtg


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    ipw__istvq = np.empty(n, np.bool_)
    ypo__mhyhj = np.empty(n + 7 >> 3, np.uint8)
    for jwhk__ngany, s in enumerate(pyval):
        tdd__nbq = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ypo__mhyhj, jwhk__ngany, int(
            not tdd__nbq))
        if not tdd__nbq:
            ipw__istvq[jwhk__ngany] = s
    thfi__qilgu = context.get_constant_generic(builder, data_type, ipw__istvq)
    bzh__mpihf = context.get_constant_generic(builder, nulls_type, ypo__mhyhj)
    return lir.Constant.literal_struct([thfi__qilgu, bzh__mpihf])


def lower_init_bool_array(context, builder, signature, args):
    pbat__wyfs, faofm__yaonq = args
    ooomm__tvk = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    ooomm__tvk.data = pbat__wyfs
    ooomm__tvk.null_bitmap = faofm__yaonq
    context.nrt.incref(builder, signature.args[0], pbat__wyfs)
    context.nrt.incref(builder, signature.args[1], faofm__yaonq)
    return ooomm__tvk._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ytzm__pcp = args[0]
    if equiv_set.has_shape(ytzm__pcp):
        return ArrayAnalysis.AnalyzeResult(shape=ytzm__pcp, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ytzm__pcp = args[0]
    if equiv_set.has_shape(ytzm__pcp):
        return ArrayAnalysis.AnalyzeResult(shape=ytzm__pcp, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    ipw__istvq = np.empty(n, dtype=np.bool_)
    lcuhi__lzgs = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(ipw__istvq, lcuhi__lzgs)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            cqke__xey, nuxn__mook = array_getitem_bool_index(A, ind)
            return init_bool_array(cqke__xey, nuxn__mook)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            cqke__xey, nuxn__mook = array_getitem_int_index(A, ind)
            return init_bool_array(cqke__xey, nuxn__mook)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            cqke__xey, nuxn__mook = array_getitem_slice_index(A, ind)
            return init_bool_array(cqke__xey, nuxn__mook)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    icxdk__opj = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(icxdk__opj)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(icxdk__opj)
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
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'size')
def overload_bool_arr_size(A):
    return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for jwhk__ngany in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, jwhk__ngany):
                val = A[jwhk__ngany]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
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
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            lhhvv__wjc = np.empty(n, nb_dtype)
            for jwhk__ngany in numba.parfors.parfor.internal_prange(n):
                lhhvv__wjc[jwhk__ngany] = data[jwhk__ngany]
                if bodo.libs.array_kernels.isna(A, jwhk__ngany):
                    lhhvv__wjc[jwhk__ngany] = np.nan
            return lhhvv__wjc
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        lhhvv__wjc = np.empty(n, dtype=np.bool_)
        for jwhk__ngany in numba.parfors.parfor.internal_prange(n):
            lhhvv__wjc[jwhk__ngany] = data[jwhk__ngany]
            if bodo.libs.array_kernels.isna(A, jwhk__ngany):
                lhhvv__wjc[jwhk__ngany] = value
        return lhhvv__wjc
    return impl


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    usmc__yujq = op.__name__
    usmc__yujq = ufunc_aliases.get(usmc__yujq, usmc__yujq)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for cuz__xbm in numba.np.ufunc_db.get_ufuncs():
        ybrmj__oreyw = create_op_overload(cuz__xbm, cuz__xbm.nin)
        overload(cuz__xbm, no_unliteral=True)(ybrmj__oreyw)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ybrmj__oreyw = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ybrmj__oreyw)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ybrmj__oreyw = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ybrmj__oreyw)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ybrmj__oreyw = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ybrmj__oreyw)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        ubb__poxzf = []
        lfwq__ehox = False
        txz__ffc = False
        nhoue__jtmz = False
        for jwhk__ngany in range(len(A)):
            if bodo.libs.array_kernels.isna(A, jwhk__ngany):
                if not lfwq__ehox:
                    data.append(False)
                    ubb__poxzf.append(False)
                    lfwq__ehox = True
                continue
            val = A[jwhk__ngany]
            if val and not txz__ffc:
                data.append(True)
                ubb__poxzf.append(True)
                txz__ffc = True
            if not val and not nhoue__jtmz:
                data.append(False)
                ubb__poxzf.append(True)
                nhoue__jtmz = True
            if lfwq__ehox and txz__ffc and nhoue__jtmz:
                break
        cqke__xey = np.array(data)
        n = len(cqke__xey)
        tpt__osunk = 1
        nuxn__mook = np.empty(tpt__osunk, np.uint8)
        for xaxg__phar in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(nuxn__mook, xaxg__phar,
                ubb__poxzf[xaxg__phar])
        return init_bool_array(cqke__xey, nuxn__mook)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    ofpn__tgtg = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, ofpn__tgtg)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    qci__advg = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        gvdbm__vspz = bodo.utils.utils.is_array_typ(val1, False)
        iae__ghbzz = bodo.utils.utils.is_array_typ(val2, False)
        rca__plg = 'val1' if gvdbm__vspz else 'val2'
        qok__xoc = 'def impl(val1, val2):\n'
        qok__xoc += f'  n = len({rca__plg})\n'
        qok__xoc += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        qok__xoc += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if gvdbm__vspz:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            ilvgu__nggto = 'val1[i]'
        else:
            null1 = 'False\n'
            ilvgu__nggto = 'val1'
        if iae__ghbzz:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            yca__qhkmm = 'val2[i]'
        else:
            null2 = 'False\n'
            yca__qhkmm = 'val2'
        if qci__advg:
            qok__xoc += f"""    result, isna_val = compute_or_body({null1}, {null2}, {ilvgu__nggto}, {yca__qhkmm})
"""
        else:
            qok__xoc += f"""    result, isna_val = compute_and_body({null1}, {null2}, {ilvgu__nggto}, {yca__qhkmm})
"""
        qok__xoc += '    out_arr[i] = result\n'
        qok__xoc += '    if isna_val:\n'
        qok__xoc += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        qok__xoc += '      continue\n'
        qok__xoc += '  return out_arr\n'
        zkb__forc = {}
        exec(qok__xoc, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, zkb__forc)
        impl = zkb__forc['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        uoq__tqtm = boolean_array
        return uoq__tqtm(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    llp__lqo = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array) and (
        bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype == types.
        bool_ or typ1 == types.bool_) and (bodo.utils.utils.is_array_typ(
        typ2, False) and typ2.dtype == types.bool_ or typ2 == types.bool_)
    return llp__lqo


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        yio__krcf = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(yio__krcf)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(yio__krcf)


_install_nullable_logical_lowering()
