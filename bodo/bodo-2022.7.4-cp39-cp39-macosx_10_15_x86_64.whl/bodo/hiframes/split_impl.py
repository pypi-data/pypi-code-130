import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kgei__pxhsk = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, kgei__pxhsk)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    yymo__ptj = context.get_value_type(str_arr_split_view_payload_type)
    jud__ytik = context.get_abi_sizeof(yymo__ptj)
    zleqr__thbm = context.get_value_type(types.voidptr)
    tgny__vhbem = context.get_value_type(types.uintp)
    gcg__vyvh = lir.FunctionType(lir.VoidType(), [zleqr__thbm, tgny__vhbem,
        zleqr__thbm])
    abul__antv = cgutils.get_or_insert_function(builder.module, gcg__vyvh,
        name='dtor_str_arr_split_view')
    jjmn__vgl = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, jud__ytik), abul__antv)
    agnx__kguc = context.nrt.meminfo_data(builder, jjmn__vgl)
    tyypi__zhp = builder.bitcast(agnx__kguc, yymo__ptj.as_pointer())
    return jjmn__vgl, tyypi__zhp


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        rwlzr__pjqsc, wua__lhge = args
        jjmn__vgl, tyypi__zhp = construct_str_arr_split_view(context, builder)
        lrlav__vjkxl = _get_str_binary_arr_payload(context, builder,
            rwlzr__pjqsc, string_array_type)
        kwjc__tfbwn = lir.FunctionType(lir.VoidType(), [tyypi__zhp.type,
            lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        ory__adzz = cgutils.get_or_insert_function(builder.module,
            kwjc__tfbwn, name='str_arr_split_view_impl')
        kjmd__uqgud = context.make_helper(builder, offset_arr_type,
            lrlav__vjkxl.offsets).data
        yhxlf__poy = context.make_helper(builder, char_arr_type,
            lrlav__vjkxl.data).data
        ornyl__fqfd = context.make_helper(builder, null_bitmap_arr_type,
            lrlav__vjkxl.null_bitmap).data
        byq__ontwj = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(ory__adzz, [tyypi__zhp, lrlav__vjkxl.n_arrays,
            kjmd__uqgud, yhxlf__poy, ornyl__fqfd, byq__ontwj])
        pby__bfm = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(tyypi__zhp))
        zym__xhw = context.make_helper(builder, string_array_split_view_type)
        zym__xhw.num_items = lrlav__vjkxl.n_arrays
        zym__xhw.index_offsets = pby__bfm.index_offsets
        zym__xhw.data_offsets = pby__bfm.data_offsets
        zym__xhw.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [
            rwlzr__pjqsc])
        zym__xhw.null_bitmap = pby__bfm.null_bitmap
        zym__xhw.meminfo = jjmn__vgl
        lcjc__vzzt = zym__xhw._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, lcjc__vzzt)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    ukrvj__vbt = context.make_helper(builder, string_array_split_view_type, val
        )
    awc__fbc = context.insert_const_string(builder.module, 'numpy')
    msy__usfps = c.pyapi.import_module_noblock(awc__fbc)
    dtype = c.pyapi.object_getattr_string(msy__usfps, 'object_')
    jbheq__dnamq = builder.sext(ukrvj__vbt.num_items, c.pyapi.longlong)
    byf__zog = c.pyapi.long_from_longlong(jbheq__dnamq)
    kyxkd__vpdug = c.pyapi.call_method(msy__usfps, 'ndarray', (byf__zog, dtype)
        )
    bec__vneq = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    arazc__rlha = c.pyapi._get_function(bec__vneq, name='array_getptr1')
    vjk__bzv = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.IntType
        (8).as_pointer(), c.pyapi.pyobj])
    wvky__czas = c.pyapi._get_function(vjk__bzv, name='array_setitem')
    ckct__uvf = c.pyapi.object_getattr_string(msy__usfps, 'nan')
    with cgutils.for_range(builder, ukrvj__vbt.num_items) as hmf__txn:
        str_ind = hmf__txn.index
        bymx__brpb = builder.sext(builder.load(builder.gep(ukrvj__vbt.
            index_offsets, [str_ind])), lir.IntType(64))
        urc__prm = builder.sext(builder.load(builder.gep(ukrvj__vbt.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        liebq__xgecl = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        bfzz__nfb = builder.gep(ukrvj__vbt.null_bitmap, [liebq__xgecl])
        tqai__vhkbq = builder.load(bfzz__nfb)
        vfhi__qiif = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(tqai__vhkbq, vfhi__qiif), lir.
            Constant(lir.IntType(8), 1))
        etz__vaoj = builder.sub(urc__prm, bymx__brpb)
        etz__vaoj = builder.sub(etz__vaoj, etz__vaoj.type(1))
        dyjsp__pxz = builder.call(arazc__rlha, [kyxkd__vpdug, str_ind])
        lqwo__hvvnk = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(lqwo__hvvnk) as (iyoq__nlv, uum__wbyik):
            with iyoq__nlv:
                moeez__cfmb = c.pyapi.list_new(etz__vaoj)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    moeez__cfmb), likely=True):
                    with cgutils.for_range(c.builder, etz__vaoj) as hmf__txn:
                        rkp__nltzg = builder.add(bymx__brpb, hmf__txn.index)
                        data_start = builder.load(builder.gep(ukrvj__vbt.
                            data_offsets, [rkp__nltzg]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        mdqbm__ypszc = builder.load(builder.gep(ukrvj__vbt.
                            data_offsets, [builder.add(rkp__nltzg,
                            rkp__nltzg.type(1))]))
                        eqtgx__hwz = builder.gep(builder.extract_value(
                            ukrvj__vbt.data, 0), [data_start])
                        ducn__hsq = builder.sext(builder.sub(mdqbm__ypszc,
                            data_start), lir.IntType(64))
                        eww__lky = c.pyapi.string_from_string_and_size(
                            eqtgx__hwz, ducn__hsq)
                        c.pyapi.list_setitem(moeez__cfmb, hmf__txn.index,
                            eww__lky)
                builder.call(wvky__czas, [kyxkd__vpdug, dyjsp__pxz,
                    moeez__cfmb])
            with uum__wbyik:
                builder.call(wvky__czas, [kyxkd__vpdug, dyjsp__pxz, ckct__uvf])
    c.pyapi.decref(msy__usfps)
    c.pyapi.decref(dtype)
    c.pyapi.decref(ckct__uvf)
    return kyxkd__vpdug


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        vpwo__kxjk, omlhz__maesf, eqtgx__hwz = args
        jjmn__vgl, tyypi__zhp = construct_str_arr_split_view(context, builder)
        kwjc__tfbwn = lir.FunctionType(lir.VoidType(), [tyypi__zhp.type,
            lir.IntType(64), lir.IntType(64)])
        ory__adzz = cgutils.get_or_insert_function(builder.module,
            kwjc__tfbwn, name='str_arr_split_view_alloc')
        builder.call(ory__adzz, [tyypi__zhp, vpwo__kxjk, omlhz__maesf])
        pby__bfm = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(tyypi__zhp))
        zym__xhw = context.make_helper(builder, string_array_split_view_type)
        zym__xhw.num_items = vpwo__kxjk
        zym__xhw.index_offsets = pby__bfm.index_offsets
        zym__xhw.data_offsets = pby__bfm.data_offsets
        zym__xhw.data = eqtgx__hwz
        zym__xhw.null_bitmap = pby__bfm.null_bitmap
        context.nrt.incref(builder, data_t, eqtgx__hwz)
        zym__xhw.meminfo = jjmn__vgl
        lcjc__vzzt = zym__xhw._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, lcjc__vzzt)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        oohhf__uohy, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            oohhf__uohy = builder.extract_value(oohhf__uohy, 0)
        return builder.bitcast(builder.gep(oohhf__uohy, [ind]), lir.IntType
            (8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        oohhf__uohy, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            oohhf__uohy = builder.extract_value(oohhf__uohy, 0)
        return builder.load(builder.gep(oohhf__uohy, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        oohhf__uohy, ind, oqi__ebz = args
        lmgc__yjj = builder.gep(oohhf__uohy, [ind])
        builder.store(oqi__ebz, lmgc__yjj)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        izlje__arz, ind = args
        eryp__tty = context.make_helper(builder, arr_ctypes_t, izlje__arz)
        vtkxh__mjfsr = context.make_helper(builder, arr_ctypes_t)
        vtkxh__mjfsr.data = builder.gep(eryp__tty.data, [ind])
        vtkxh__mjfsr.meminfo = eryp__tty.meminfo
        uwlw__tocek = vtkxh__mjfsr._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, uwlw__tocek)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    ifhef__rsmfy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
        _null_bitmap, item_ind)
    if not ifhef__rsmfy:
        return 0, 0, 0
    rkp__nltzg = getitem_c_arr(arr._index_offsets, item_ind)
    nygeu__dsa = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    ewnxn__vwkz = nygeu__dsa - rkp__nltzg
    if str_ind >= ewnxn__vwkz:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, rkp__nltzg + str_ind)
    data_start += 1
    if rkp__nltzg + str_ind == 0:
        data_start = 0
    mdqbm__ypszc = getitem_c_arr(arr._data_offsets, rkp__nltzg + str_ind + 1)
    tenr__nohgw = mdqbm__ypszc - data_start
    return 1, data_start, tenr__nohgw


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        jdvbi__bnfx = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            rkp__nltzg = getitem_c_arr(A._index_offsets, ind)
            nygeu__dsa = getitem_c_arr(A._index_offsets, ind + 1)
            nklg__qikj = nygeu__dsa - rkp__nltzg - 1
            rwlzr__pjqsc = bodo.libs.str_arr_ext.pre_alloc_string_array(
                nklg__qikj, -1)
            for qbsqo__guba in range(nklg__qikj):
                data_start = getitem_c_arr(A._data_offsets, rkp__nltzg +
                    qbsqo__guba)
                data_start += 1
                if rkp__nltzg + qbsqo__guba == 0:
                    data_start = 0
                mdqbm__ypszc = getitem_c_arr(A._data_offsets, rkp__nltzg +
                    qbsqo__guba + 1)
                tenr__nohgw = mdqbm__ypszc - data_start
                lmgc__yjj = get_array_ctypes_ptr(A._data, data_start)
                wbrti__ccfc = bodo.libs.str_arr_ext.decode_utf8(lmgc__yjj,
                    tenr__nohgw)
                rwlzr__pjqsc[qbsqo__guba] = wbrti__ccfc
            return rwlzr__pjqsc
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        xyy__gfsh = offset_type.bitwidth // 8

        def _impl(A, ind):
            nklg__qikj = len(A)
            if nklg__qikj != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            vpwo__kxjk = 0
            omlhz__maesf = 0
            for qbsqo__guba in range(nklg__qikj):
                if ind[qbsqo__guba]:
                    vpwo__kxjk += 1
                    rkp__nltzg = getitem_c_arr(A._index_offsets, qbsqo__guba)
                    nygeu__dsa = getitem_c_arr(A._index_offsets, 
                        qbsqo__guba + 1)
                    omlhz__maesf += nygeu__dsa - rkp__nltzg
            kyxkd__vpdug = pre_alloc_str_arr_view(vpwo__kxjk, omlhz__maesf,
                A._data)
            item_ind = 0
            iltu__xrfl = 0
            for qbsqo__guba in range(nklg__qikj):
                if ind[qbsqo__guba]:
                    rkp__nltzg = getitem_c_arr(A._index_offsets, qbsqo__guba)
                    nygeu__dsa = getitem_c_arr(A._index_offsets, 
                        qbsqo__guba + 1)
                    iab__cyz = nygeu__dsa - rkp__nltzg
                    setitem_c_arr(kyxkd__vpdug._index_offsets, item_ind,
                        iltu__xrfl)
                    lmgc__yjj = get_c_arr_ptr(A._data_offsets, rkp__nltzg)
                    osdd__kax = get_c_arr_ptr(kyxkd__vpdug._data_offsets,
                        iltu__xrfl)
                    _memcpy(osdd__kax, lmgc__yjj, iab__cyz, xyy__gfsh)
                    ifhef__rsmfy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, qbsqo__guba)
                    bodo.libs.int_arr_ext.set_bit_to_arr(kyxkd__vpdug.
                        _null_bitmap, item_ind, ifhef__rsmfy)
                    item_ind += 1
                    iltu__xrfl += iab__cyz
            setitem_c_arr(kyxkd__vpdug._index_offsets, item_ind, iltu__xrfl)
            return kyxkd__vpdug
        return _impl
