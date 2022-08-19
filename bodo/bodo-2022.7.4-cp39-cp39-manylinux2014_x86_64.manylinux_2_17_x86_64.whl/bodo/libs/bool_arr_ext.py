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
        tcoq__krviw = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, tcoq__krviw)


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
    grr__zutuk = c.context.insert_const_string(c.builder.module, 'pandas')
    byf__isx = c.pyapi.import_module_noblock(grr__zutuk)
    ckgq__dmqm = c.pyapi.call_method(byf__isx, 'BooleanDtype', ())
    c.pyapi.decref(byf__isx)
    return ckgq__dmqm


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    bece__uxrmk = n + 7 >> 3
    return np.full(bece__uxrmk, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    dvxo__gmaji = c.context.typing_context.resolve_value_type(func)
    vsnc__tjrdz = dvxo__gmaji.get_call_type(c.context.typing_context,
        arg_typs, {})
    ffdte__idqvp = c.context.get_function(dvxo__gmaji, vsnc__tjrdz)
    lss__oxgh = c.context.call_conv.get_function_type(vsnc__tjrdz.
        return_type, vsnc__tjrdz.args)
    yxv__gkbip = c.builder.module
    bny__ahyq = lir.Function(yxv__gkbip, lss__oxgh, name=yxv__gkbip.
        get_unique_name('.func_conv'))
    bny__ahyq.linkage = 'internal'
    icak__nju = lir.IRBuilder(bny__ahyq.append_basic_block())
    qzn__xypzs = c.context.call_conv.decode_arguments(icak__nju,
        vsnc__tjrdz.args, bny__ahyq)
    hub__uvse = ffdte__idqvp(icak__nju, qzn__xypzs)
    c.context.call_conv.return_value(icak__nju, hub__uvse)
    uznow__gotpw, vfd__zyi = c.context.call_conv.call_function(c.builder,
        bny__ahyq, vsnc__tjrdz.return_type, vsnc__tjrdz.args, args)
    return vfd__zyi


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    iiua__qlcr = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(iiua__qlcr)
    c.pyapi.decref(iiua__qlcr)
    lss__oxgh = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    cyft__osra = cgutils.get_or_insert_function(c.builder.module, lss__oxgh,
        name='is_bool_array')
    lss__oxgh = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    bny__ahyq = cgutils.get_or_insert_function(c.builder.module, lss__oxgh,
        name='is_pd_boolean_array')
    jgjtq__zxqp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vssq__brtj = c.builder.call(bny__ahyq, [obj])
    nzczf__dtt = c.builder.icmp_unsigned('!=', vssq__brtj, vssq__brtj.type(0))
    with c.builder.if_else(nzczf__dtt) as (nhtjy__qwqx, xuzen__ctjy):
        with nhtjy__qwqx:
            ydm__mnnj = c.pyapi.object_getattr_string(obj, '_data')
            jgjtq__zxqp.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), ydm__mnnj).value
            bvz__xrlfp = c.pyapi.object_getattr_string(obj, '_mask')
            wnrtr__tlpj = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), bvz__xrlfp).value
            bece__uxrmk = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            tdyae__ljio = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, wnrtr__tlpj)
            gxkb__dwqni = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [bece__uxrmk])
            lss__oxgh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            bny__ahyq = cgutils.get_or_insert_function(c.builder.module,
                lss__oxgh, name='mask_arr_to_bitmap')
            c.builder.call(bny__ahyq, [gxkb__dwqni.data, tdyae__ljio.data, n])
            jgjtq__zxqp.null_bitmap = gxkb__dwqni._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), wnrtr__tlpj)
            c.pyapi.decref(ydm__mnnj)
            c.pyapi.decref(bvz__xrlfp)
        with xuzen__ctjy:
            lhkx__dlqe = c.builder.call(cyft__osra, [obj])
            spouf__zvmdx = c.builder.icmp_unsigned('!=', lhkx__dlqe,
                lhkx__dlqe.type(0))
            with c.builder.if_else(spouf__zvmdx) as (rkxlh__xummm, sspqe__otjzi
                ):
                with rkxlh__xummm:
                    jgjtq__zxqp.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    jgjtq__zxqp.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with sspqe__otjzi:
                    jgjtq__zxqp.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    bece__uxrmk = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    jgjtq__zxqp.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [bece__uxrmk])._getvalue()
                    evg__inyjl = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, jgjtq__zxqp.data
                        ).data
                    exiri__swy = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, jgjtq__zxqp.
                        null_bitmap).data
                    lss__oxgh = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    bny__ahyq = cgutils.get_or_insert_function(c.builder.
                        module, lss__oxgh, name='unbox_bool_array_obj')
                    c.builder.call(bny__ahyq, [obj, evg__inyjl, exiri__swy, n])
    return NativeValue(jgjtq__zxqp._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    jgjtq__zxqp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        jgjtq__zxqp.data, c.env_manager)
    jjs__mtbid = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, jgjtq__zxqp.null_bitmap).data
    iiua__qlcr = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(iiua__qlcr)
    grr__zutuk = c.context.insert_const_string(c.builder.module, 'numpy')
    sjau__rqcgz = c.pyapi.import_module_noblock(grr__zutuk)
    vhbn__oyvg = c.pyapi.object_getattr_string(sjau__rqcgz, 'bool_')
    wnrtr__tlpj = c.pyapi.call_method(sjau__rqcgz, 'empty', (iiua__qlcr,
        vhbn__oyvg))
    jwt__zpyw = c.pyapi.object_getattr_string(wnrtr__tlpj, 'ctypes')
    oucqz__pmc = c.pyapi.object_getattr_string(jwt__zpyw, 'data')
    bdm__zbyc = c.builder.inttoptr(c.pyapi.long_as_longlong(oucqz__pmc),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as fmq__vthi:
        hvda__uzuo = fmq__vthi.index
        dcyuw__uhojx = c.builder.lshr(hvda__uzuo, lir.Constant(lir.IntType(
            64), 3))
        fhh__obt = c.builder.load(cgutils.gep(c.builder, jjs__mtbid,
            dcyuw__uhojx))
        nve__rdan = c.builder.trunc(c.builder.and_(hvda__uzuo, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(fhh__obt, nve__rdan), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        cadpt__snwb = cgutils.gep(c.builder, bdm__zbyc, hvda__uzuo)
        c.builder.store(val, cadpt__snwb)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        jgjtq__zxqp.null_bitmap)
    grr__zutuk = c.context.insert_const_string(c.builder.module, 'pandas')
    byf__isx = c.pyapi.import_module_noblock(grr__zutuk)
    boz__kmz = c.pyapi.object_getattr_string(byf__isx, 'arrays')
    ckgq__dmqm = c.pyapi.call_method(boz__kmz, 'BooleanArray', (data,
        wnrtr__tlpj))
    c.pyapi.decref(byf__isx)
    c.pyapi.decref(iiua__qlcr)
    c.pyapi.decref(sjau__rqcgz)
    c.pyapi.decref(vhbn__oyvg)
    c.pyapi.decref(jwt__zpyw)
    c.pyapi.decref(oucqz__pmc)
    c.pyapi.decref(boz__kmz)
    c.pyapi.decref(data)
    c.pyapi.decref(wnrtr__tlpj)
    return ckgq__dmqm


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    xzh__jtay = np.empty(n, np.bool_)
    zhva__uhr = np.empty(n + 7 >> 3, np.uint8)
    for hvda__uzuo, s in enumerate(pyval):
        rzp__inh = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(zhva__uhr, hvda__uzuo, int(not
            rzp__inh))
        if not rzp__inh:
            xzh__jtay[hvda__uzuo] = s
    vqns__tgg = context.get_constant_generic(builder, data_type, xzh__jtay)
    ddfny__hlvvw = context.get_constant_generic(builder, nulls_type, zhva__uhr)
    return lir.Constant.literal_struct([vqns__tgg, ddfny__hlvvw])


def lower_init_bool_array(context, builder, signature, args):
    xlmr__ttl, icgwu__kbi = args
    jgjtq__zxqp = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    jgjtq__zxqp.data = xlmr__ttl
    jgjtq__zxqp.null_bitmap = icgwu__kbi
    context.nrt.incref(builder, signature.args[0], xlmr__ttl)
    context.nrt.incref(builder, signature.args[1], icgwu__kbi)
    return jgjtq__zxqp._getvalue()


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
    hxe__otml = args[0]
    if equiv_set.has_shape(hxe__otml):
        return ArrayAnalysis.AnalyzeResult(shape=hxe__otml, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    hxe__otml = args[0]
    if equiv_set.has_shape(hxe__otml):
        return ArrayAnalysis.AnalyzeResult(shape=hxe__otml, pre=[])
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
    xzh__jtay = np.empty(n, dtype=np.bool_)
    awcn__ypwb = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(xzh__jtay, awcn__ypwb)


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
            hinv__pvg, flyv__nojz = array_getitem_bool_index(A, ind)
            return init_bool_array(hinv__pvg, flyv__nojz)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            hinv__pvg, flyv__nojz = array_getitem_int_index(A, ind)
            return init_bool_array(hinv__pvg, flyv__nojz)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            hinv__pvg, flyv__nojz = array_getitem_slice_index(A, ind)
            return init_bool_array(hinv__pvg, flyv__nojz)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    pjk__hgozr = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(pjk__hgozr)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(pjk__hgozr)
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
        for hvda__uzuo in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, hvda__uzuo):
                val = A[hvda__uzuo]
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
            bns__lejp = np.empty(n, nb_dtype)
            for hvda__uzuo in numba.parfors.parfor.internal_prange(n):
                bns__lejp[hvda__uzuo] = data[hvda__uzuo]
                if bodo.libs.array_kernels.isna(A, hvda__uzuo):
                    bns__lejp[hvda__uzuo] = np.nan
            return bns__lejp
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        bns__lejp = np.empty(n, dtype=np.bool_)
        for hvda__uzuo in numba.parfors.parfor.internal_prange(n):
            bns__lejp[hvda__uzuo] = data[hvda__uzuo]
            if bodo.libs.array_kernels.isna(A, hvda__uzuo):
                bns__lejp[hvda__uzuo] = value
        return bns__lejp
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
    lhe__sjj = op.__name__
    lhe__sjj = ufunc_aliases.get(lhe__sjj, lhe__sjj)
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
    for tgx__eoyai in numba.np.ufunc_db.get_ufuncs():
        abgp__kftsl = create_op_overload(tgx__eoyai, tgx__eoyai.nin)
        overload(tgx__eoyai, no_unliteral=True)(abgp__kftsl)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        abgp__kftsl = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(abgp__kftsl)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        abgp__kftsl = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(abgp__kftsl)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        abgp__kftsl = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(abgp__kftsl)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        nve__rdan = []
        rayz__ngu = False
        kcrw__isepi = False
        jvcex__gyy = False
        for hvda__uzuo in range(len(A)):
            if bodo.libs.array_kernels.isna(A, hvda__uzuo):
                if not rayz__ngu:
                    data.append(False)
                    nve__rdan.append(False)
                    rayz__ngu = True
                continue
            val = A[hvda__uzuo]
            if val and not kcrw__isepi:
                data.append(True)
                nve__rdan.append(True)
                kcrw__isepi = True
            if not val and not jvcex__gyy:
                data.append(False)
                nve__rdan.append(True)
                jvcex__gyy = True
            if rayz__ngu and kcrw__isepi and jvcex__gyy:
                break
        hinv__pvg = np.array(data)
        n = len(hinv__pvg)
        bece__uxrmk = 1
        flyv__nojz = np.empty(bece__uxrmk, np.uint8)
        for zrxh__qqnx in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(flyv__nojz, zrxh__qqnx,
                nve__rdan[zrxh__qqnx])
        return init_bool_array(hinv__pvg, flyv__nojz)
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
    ckgq__dmqm = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, ckgq__dmqm)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    zanbw__qzgyp = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        yjgfh__iqb = bodo.utils.utils.is_array_typ(val1, False)
        dbyt__rgbm = bodo.utils.utils.is_array_typ(val2, False)
        wla__eub = 'val1' if yjgfh__iqb else 'val2'
        pxbot__qpyb = 'def impl(val1, val2):\n'
        pxbot__qpyb += f'  n = len({wla__eub})\n'
        pxbot__qpyb += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        pxbot__qpyb += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if yjgfh__iqb:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            cjp__xoav = 'val1[i]'
        else:
            null1 = 'False\n'
            cjp__xoav = 'val1'
        if dbyt__rgbm:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            dnc__jtnrb = 'val2[i]'
        else:
            null2 = 'False\n'
            dnc__jtnrb = 'val2'
        if zanbw__qzgyp:
            pxbot__qpyb += f"""    result, isna_val = compute_or_body({null1}, {null2}, {cjp__xoav}, {dnc__jtnrb})
"""
        else:
            pxbot__qpyb += f"""    result, isna_val = compute_and_body({null1}, {null2}, {cjp__xoav}, {dnc__jtnrb})
"""
        pxbot__qpyb += '    out_arr[i] = result\n'
        pxbot__qpyb += '    if isna_val:\n'
        pxbot__qpyb += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        pxbot__qpyb += '      continue\n'
        pxbot__qpyb += '  return out_arr\n'
        yqv__zwikt = {}
        exec(pxbot__qpyb, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, yqv__zwikt)
        impl = yqv__zwikt['impl']
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
        glgj__vuoff = boolean_array
        return glgj__vuoff(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    nqznx__mxa = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return nqznx__mxa


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        bbcv__pty = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(bbcv__pty)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(bbcv__pty)


_install_nullable_logical_lowering()
