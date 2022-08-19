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
        lpfrd__pog = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, lpfrd__pog)


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
    bcw__oyuw = c.context.insert_const_string(c.builder.module, 'pandas')
    nowm__feoig = c.pyapi.import_module_noblock(bcw__oyuw)
    aejp__cnci = c.pyapi.call_method(nowm__feoig, 'BooleanDtype', ())
    c.pyapi.decref(nowm__feoig)
    return aejp__cnci


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    wpxs__yneix = n + 7 >> 3
    return np.full(wpxs__yneix, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    gpji__mqvg = c.context.typing_context.resolve_value_type(func)
    emz__kvv = gpji__mqvg.get_call_type(c.context.typing_context, arg_typs, {})
    lkxqo__sbpe = c.context.get_function(gpji__mqvg, emz__kvv)
    mgcc__bxf = c.context.call_conv.get_function_type(emz__kvv.return_type,
        emz__kvv.args)
    bhe__qbah = c.builder.module
    mnws__epcpp = lir.Function(bhe__qbah, mgcc__bxf, name=bhe__qbah.
        get_unique_name('.func_conv'))
    mnws__epcpp.linkage = 'internal'
    xjd__wdwoq = lir.IRBuilder(mnws__epcpp.append_basic_block())
    ahkp__wpff = c.context.call_conv.decode_arguments(xjd__wdwoq, emz__kvv.
        args, mnws__epcpp)
    vsxgj__pmsyi = lkxqo__sbpe(xjd__wdwoq, ahkp__wpff)
    c.context.call_conv.return_value(xjd__wdwoq, vsxgj__pmsyi)
    zwb__doglt, qzt__unhoy = c.context.call_conv.call_function(c.builder,
        mnws__epcpp, emz__kvv.return_type, emz__kvv.args, args)
    return qzt__unhoy


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    ghl__beu = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ghl__beu)
    c.pyapi.decref(ghl__beu)
    mgcc__bxf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    qgq__zpl = cgutils.get_or_insert_function(c.builder.module, mgcc__bxf,
        name='is_bool_array')
    mgcc__bxf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    mnws__epcpp = cgutils.get_or_insert_function(c.builder.module,
        mgcc__bxf, name='is_pd_boolean_array')
    ihhy__veiba = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mppb__izoy = c.builder.call(mnws__epcpp, [obj])
    exql__alc = c.builder.icmp_unsigned('!=', mppb__izoy, mppb__izoy.type(0))
    with c.builder.if_else(exql__alc) as (bowk__djao, cppj__cfle):
        with bowk__djao:
            nfmjp__yjn = c.pyapi.object_getattr_string(obj, '_data')
            ihhy__veiba.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), nfmjp__yjn).value
            tsigw__bzw = c.pyapi.object_getattr_string(obj, '_mask')
            yskqj__mmvb = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), tsigw__bzw).value
            wpxs__yneix = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            oawe__nqhls = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, yskqj__mmvb)
            ljbq__das = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [wpxs__yneix])
            mgcc__bxf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            mnws__epcpp = cgutils.get_or_insert_function(c.builder.module,
                mgcc__bxf, name='mask_arr_to_bitmap')
            c.builder.call(mnws__epcpp, [ljbq__das.data, oawe__nqhls.data, n])
            ihhy__veiba.null_bitmap = ljbq__das._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), yskqj__mmvb)
            c.pyapi.decref(nfmjp__yjn)
            c.pyapi.decref(tsigw__bzw)
        with cppj__cfle:
            irafz__wpcag = c.builder.call(qgq__zpl, [obj])
            wdhcm__ppzrl = c.builder.icmp_unsigned('!=', irafz__wpcag,
                irafz__wpcag.type(0))
            with c.builder.if_else(wdhcm__ppzrl) as (eoqw__xsh, plb__kwbj):
                with eoqw__xsh:
                    ihhy__veiba.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    ihhy__veiba.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with plb__kwbj:
                    ihhy__veiba.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    wpxs__yneix = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    ihhy__veiba.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [wpxs__yneix])._getvalue()
                    qbzr__waf = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, ihhy__veiba.data
                        ).data
                    sfmu__pzpqx = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, ihhy__veiba.
                        null_bitmap).data
                    mgcc__bxf = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    mnws__epcpp = cgutils.get_or_insert_function(c.builder.
                        module, mgcc__bxf, name='unbox_bool_array_obj')
                    c.builder.call(mnws__epcpp, [obj, qbzr__waf,
                        sfmu__pzpqx, n])
    return NativeValue(ihhy__veiba._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    ihhy__veiba = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ihhy__veiba.data, c.env_manager)
    tontg__vfk = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ihhy__veiba.null_bitmap).data
    ghl__beu = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ghl__beu)
    bcw__oyuw = c.context.insert_const_string(c.builder.module, 'numpy')
    lum__evdo = c.pyapi.import_module_noblock(bcw__oyuw)
    iawoh__knmu = c.pyapi.object_getattr_string(lum__evdo, 'bool_')
    yskqj__mmvb = c.pyapi.call_method(lum__evdo, 'empty', (ghl__beu,
        iawoh__knmu))
    eiiwg__iqdfi = c.pyapi.object_getattr_string(yskqj__mmvb, 'ctypes')
    jvdbv__eiu = c.pyapi.object_getattr_string(eiiwg__iqdfi, 'data')
    metnd__xhpdr = c.builder.inttoptr(c.pyapi.long_as_longlong(jvdbv__eiu),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as ahzt__esr:
        vznnk__ngp = ahzt__esr.index
        dupw__qhk = c.builder.lshr(vznnk__ngp, lir.Constant(lir.IntType(64), 3)
            )
        sebjk__gszr = c.builder.load(cgutils.gep(c.builder, tontg__vfk,
            dupw__qhk))
        yzyot__fepid = c.builder.trunc(c.builder.and_(vznnk__ngp, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(sebjk__gszr, yzyot__fepid), lir
            .Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        hirxi__wqsl = cgutils.gep(c.builder, metnd__xhpdr, vznnk__ngp)
        c.builder.store(val, hirxi__wqsl)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        ihhy__veiba.null_bitmap)
    bcw__oyuw = c.context.insert_const_string(c.builder.module, 'pandas')
    nowm__feoig = c.pyapi.import_module_noblock(bcw__oyuw)
    zbx__xhj = c.pyapi.object_getattr_string(nowm__feoig, 'arrays')
    aejp__cnci = c.pyapi.call_method(zbx__xhj, 'BooleanArray', (data,
        yskqj__mmvb))
    c.pyapi.decref(nowm__feoig)
    c.pyapi.decref(ghl__beu)
    c.pyapi.decref(lum__evdo)
    c.pyapi.decref(iawoh__knmu)
    c.pyapi.decref(eiiwg__iqdfi)
    c.pyapi.decref(jvdbv__eiu)
    c.pyapi.decref(zbx__xhj)
    c.pyapi.decref(data)
    c.pyapi.decref(yskqj__mmvb)
    return aejp__cnci


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    log__buyol = np.empty(n, np.bool_)
    djtp__yspm = np.empty(n + 7 >> 3, np.uint8)
    for vznnk__ngp, s in enumerate(pyval):
        igegk__deugo = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(djtp__yspm, vznnk__ngp, int(
            not igegk__deugo))
        if not igegk__deugo:
            log__buyol[vznnk__ngp] = s
    bcvp__xfui = context.get_constant_generic(builder, data_type, log__buyol)
    dotd__sck = context.get_constant_generic(builder, nulls_type, djtp__yspm)
    return lir.Constant.literal_struct([bcvp__xfui, dotd__sck])


def lower_init_bool_array(context, builder, signature, args):
    wlz__smv, zovg__smta = args
    ihhy__veiba = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    ihhy__veiba.data = wlz__smv
    ihhy__veiba.null_bitmap = zovg__smta
    context.nrt.incref(builder, signature.args[0], wlz__smv)
    context.nrt.incref(builder, signature.args[1], zovg__smta)
    return ihhy__veiba._getvalue()


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
    hvnj__wck = args[0]
    if equiv_set.has_shape(hvnj__wck):
        return ArrayAnalysis.AnalyzeResult(shape=hvnj__wck, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    hvnj__wck = args[0]
    if equiv_set.has_shape(hvnj__wck):
        return ArrayAnalysis.AnalyzeResult(shape=hvnj__wck, pre=[])
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
    log__buyol = np.empty(n, dtype=np.bool_)
    gtdqv__kju = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(log__buyol, gtdqv__kju)


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
            gqhq__vwdrm, lpaa__ryrrg = array_getitem_bool_index(A, ind)
            return init_bool_array(gqhq__vwdrm, lpaa__ryrrg)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            gqhq__vwdrm, lpaa__ryrrg = array_getitem_int_index(A, ind)
            return init_bool_array(gqhq__vwdrm, lpaa__ryrrg)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            gqhq__vwdrm, lpaa__ryrrg = array_getitem_slice_index(A, ind)
            return init_bool_array(gqhq__vwdrm, lpaa__ryrrg)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    kmywb__ggq = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(kmywb__ggq)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(kmywb__ggq)
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
        for vznnk__ngp in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, vznnk__ngp):
                val = A[vznnk__ngp]
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
            dngl__vslhr = np.empty(n, nb_dtype)
            for vznnk__ngp in numba.parfors.parfor.internal_prange(n):
                dngl__vslhr[vznnk__ngp] = data[vznnk__ngp]
                if bodo.libs.array_kernels.isna(A, vznnk__ngp):
                    dngl__vslhr[vznnk__ngp] = np.nan
            return dngl__vslhr
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        dngl__vslhr = np.empty(n, dtype=np.bool_)
        for vznnk__ngp in numba.parfors.parfor.internal_prange(n):
            dngl__vslhr[vznnk__ngp] = data[vznnk__ngp]
            if bodo.libs.array_kernels.isna(A, vznnk__ngp):
                dngl__vslhr[vznnk__ngp] = value
        return dngl__vslhr
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
    ixmjf__thmyp = op.__name__
    ixmjf__thmyp = ufunc_aliases.get(ixmjf__thmyp, ixmjf__thmyp)
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
    for tzojz__fgpz in numba.np.ufunc_db.get_ufuncs():
        gvioe__atci = create_op_overload(tzojz__fgpz, tzojz__fgpz.nin)
        overload(tzojz__fgpz, no_unliteral=True)(gvioe__atci)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        gvioe__atci = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(gvioe__atci)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        gvioe__atci = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(gvioe__atci)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        gvioe__atci = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(gvioe__atci)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        yzyot__fepid = []
        taox__lebe = False
        gyu__jdjy = False
        pydv__jrwf = False
        for vznnk__ngp in range(len(A)):
            if bodo.libs.array_kernels.isna(A, vznnk__ngp):
                if not taox__lebe:
                    data.append(False)
                    yzyot__fepid.append(False)
                    taox__lebe = True
                continue
            val = A[vznnk__ngp]
            if val and not gyu__jdjy:
                data.append(True)
                yzyot__fepid.append(True)
                gyu__jdjy = True
            if not val and not pydv__jrwf:
                data.append(False)
                yzyot__fepid.append(True)
                pydv__jrwf = True
            if taox__lebe and gyu__jdjy and pydv__jrwf:
                break
        gqhq__vwdrm = np.array(data)
        n = len(gqhq__vwdrm)
        wpxs__yneix = 1
        lpaa__ryrrg = np.empty(wpxs__yneix, np.uint8)
        for afz__pazyq in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(lpaa__ryrrg, afz__pazyq,
                yzyot__fepid[afz__pazyq])
        return init_bool_array(gqhq__vwdrm, lpaa__ryrrg)
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
    aejp__cnci = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, aejp__cnci)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    jvct__iqz = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        uajkl__dxv = bodo.utils.utils.is_array_typ(val1, False)
        ahoet__pcom = bodo.utils.utils.is_array_typ(val2, False)
        qfgoz__vwa = 'val1' if uajkl__dxv else 'val2'
        vml__zymmb = 'def impl(val1, val2):\n'
        vml__zymmb += f'  n = len({qfgoz__vwa})\n'
        vml__zymmb += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        vml__zymmb += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if uajkl__dxv:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            erhvd__fke = 'val1[i]'
        else:
            null1 = 'False\n'
            erhvd__fke = 'val1'
        if ahoet__pcom:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            gvzd__onnif = 'val2[i]'
        else:
            null2 = 'False\n'
            gvzd__onnif = 'val2'
        if jvct__iqz:
            vml__zymmb += f"""    result, isna_val = compute_or_body({null1}, {null2}, {erhvd__fke}, {gvzd__onnif})
"""
        else:
            vml__zymmb += f"""    result, isna_val = compute_and_body({null1}, {null2}, {erhvd__fke}, {gvzd__onnif})
"""
        vml__zymmb += '    out_arr[i] = result\n'
        vml__zymmb += '    if isna_val:\n'
        vml__zymmb += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        vml__zymmb += '      continue\n'
        vml__zymmb += '  return out_arr\n'
        nauw__ygnpe = {}
        exec(vml__zymmb, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, nauw__ygnpe)
        impl = nauw__ygnpe['impl']
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
        woud__awt = boolean_array
        return woud__awt(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    frbex__okfa = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return frbex__okfa


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        etje__ibsm = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(etje__ibsm)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(etje__ibsm)


_install_nullable_logical_lowering()
