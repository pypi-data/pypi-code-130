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
        zlme__nsyt = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, zlme__nsyt)


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
    xtzj__accm = context.get_value_type(str_arr_split_view_payload_type)
    tijl__tqtga = context.get_abi_sizeof(xtzj__accm)
    ufre__rrn = context.get_value_type(types.voidptr)
    zkb__hccu = context.get_value_type(types.uintp)
    yggh__puog = lir.FunctionType(lir.VoidType(), [ufre__rrn, zkb__hccu,
        ufre__rrn])
    vnqo__pqxc = cgutils.get_or_insert_function(builder.module, yggh__puog,
        name='dtor_str_arr_split_view')
    tnsq__pcpn = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tijl__tqtga), vnqo__pqxc)
    cxhfv__lwsgu = context.nrt.meminfo_data(builder, tnsq__pcpn)
    uor__bnh = builder.bitcast(cxhfv__lwsgu, xtzj__accm.as_pointer())
    return tnsq__pcpn, uor__bnh


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        tqg__jlzw, xpqhu__pln = args
        tnsq__pcpn, uor__bnh = construct_str_arr_split_view(context, builder)
        icexi__jdo = _get_str_binary_arr_payload(context, builder,
            tqg__jlzw, string_array_type)
        zlywo__sbpo = lir.FunctionType(lir.VoidType(), [uor__bnh.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        itg__dita = cgutils.get_or_insert_function(builder.module,
            zlywo__sbpo, name='str_arr_split_view_impl')
        rvnz__lvc = context.make_helper(builder, offset_arr_type,
            icexi__jdo.offsets).data
        mvqx__xbiwz = context.make_helper(builder, char_arr_type,
            icexi__jdo.data).data
        kqn__qywuq = context.make_helper(builder, null_bitmap_arr_type,
            icexi__jdo.null_bitmap).data
        ertop__cznpz = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(itg__dita, [uor__bnh, icexi__jdo.n_arrays, rvnz__lvc,
            mvqx__xbiwz, kqn__qywuq, ertop__cznpz])
        nsld__yne = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(uor__bnh))
        huzz__krssb = context.make_helper(builder, string_array_split_view_type
            )
        huzz__krssb.num_items = icexi__jdo.n_arrays
        huzz__krssb.index_offsets = nsld__yne.index_offsets
        huzz__krssb.data_offsets = nsld__yne.data_offsets
        huzz__krssb.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [tqg__jlzw])
        huzz__krssb.null_bitmap = nsld__yne.null_bitmap
        huzz__krssb.meminfo = tnsq__pcpn
        xmx__xsjx = huzz__krssb._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, xmx__xsjx)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    tkegk__vka = context.make_helper(builder, string_array_split_view_type, val
        )
    xacoz__pyede = context.insert_const_string(builder.module, 'numpy')
    sznsk__wnbwu = c.pyapi.import_module_noblock(xacoz__pyede)
    dtype = c.pyapi.object_getattr_string(sznsk__wnbwu, 'object_')
    umm__tnclf = builder.sext(tkegk__vka.num_items, c.pyapi.longlong)
    vmbdm__hfop = c.pyapi.long_from_longlong(umm__tnclf)
    yeto__inc = c.pyapi.call_method(sznsk__wnbwu, 'ndarray', (vmbdm__hfop,
        dtype))
    qvfj__hhm = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    nchi__qxhqm = c.pyapi._get_function(qvfj__hhm, name='array_getptr1')
    yutnp__byxa = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    bvyv__zpna = c.pyapi._get_function(yutnp__byxa, name='array_setitem')
    qkaq__jlslb = c.pyapi.object_getattr_string(sznsk__wnbwu, 'nan')
    with cgutils.for_range(builder, tkegk__vka.num_items) as xnm__ombjn:
        str_ind = xnm__ombjn.index
        prgw__elm = builder.sext(builder.load(builder.gep(tkegk__vka.
            index_offsets, [str_ind])), lir.IntType(64))
        kyp__qtkzz = builder.sext(builder.load(builder.gep(tkegk__vka.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        bkpyi__jwo = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        lajg__aipvb = builder.gep(tkegk__vka.null_bitmap, [bkpyi__jwo])
        kei__grwa = builder.load(lajg__aipvb)
        krral__fywvk = builder.trunc(builder.and_(str_ind, lir.Constant(lir
            .IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(kei__grwa, krral__fywvk), lir.
            Constant(lir.IntType(8), 1))
        toiv__amb = builder.sub(kyp__qtkzz, prgw__elm)
        toiv__amb = builder.sub(toiv__amb, toiv__amb.type(1))
        dyk__fqeyu = builder.call(nchi__qxhqm, [yeto__inc, str_ind])
        fnnnx__cjef = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(fnnnx__cjef) as (ffe__ojnq, stal__dji):
            with ffe__ojnq:
                byjwz__gesnq = c.pyapi.list_new(toiv__amb)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    byjwz__gesnq), likely=True):
                    with cgutils.for_range(c.builder, toiv__amb) as xnm__ombjn:
                        wnj__iqot = builder.add(prgw__elm, xnm__ombjn.index)
                        data_start = builder.load(builder.gep(tkegk__vka.
                            data_offsets, [wnj__iqot]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        zdl__pxqy = builder.load(builder.gep(tkegk__vka.
                            data_offsets, [builder.add(wnj__iqot, wnj__iqot
                            .type(1))]))
                        ztx__tmgfg = builder.gep(builder.extract_value(
                            tkegk__vka.data, 0), [data_start])
                        aee__buc = builder.sext(builder.sub(zdl__pxqy,
                            data_start), lir.IntType(64))
                        ogmjv__gab = c.pyapi.string_from_string_and_size(
                            ztx__tmgfg, aee__buc)
                        c.pyapi.list_setitem(byjwz__gesnq, xnm__ombjn.index,
                            ogmjv__gab)
                builder.call(bvyv__zpna, [yeto__inc, dyk__fqeyu, byjwz__gesnq])
            with stal__dji:
                builder.call(bvyv__zpna, [yeto__inc, dyk__fqeyu, qkaq__jlslb])
    c.pyapi.decref(sznsk__wnbwu)
    c.pyapi.decref(dtype)
    c.pyapi.decref(qkaq__jlslb)
    return yeto__inc


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ohcvy__dguy, qwn__kyi, ztx__tmgfg = args
        tnsq__pcpn, uor__bnh = construct_str_arr_split_view(context, builder)
        zlywo__sbpo = lir.FunctionType(lir.VoidType(), [uor__bnh.type, lir.
            IntType(64), lir.IntType(64)])
        itg__dita = cgutils.get_or_insert_function(builder.module,
            zlywo__sbpo, name='str_arr_split_view_alloc')
        builder.call(itg__dita, [uor__bnh, ohcvy__dguy, qwn__kyi])
        nsld__yne = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(uor__bnh))
        huzz__krssb = context.make_helper(builder, string_array_split_view_type
            )
        huzz__krssb.num_items = ohcvy__dguy
        huzz__krssb.index_offsets = nsld__yne.index_offsets
        huzz__krssb.data_offsets = nsld__yne.data_offsets
        huzz__krssb.data = ztx__tmgfg
        huzz__krssb.null_bitmap = nsld__yne.null_bitmap
        context.nrt.incref(builder, data_t, ztx__tmgfg)
        huzz__krssb.meminfo = tnsq__pcpn
        xmx__xsjx = huzz__krssb._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, xmx__xsjx)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        lql__cft, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lql__cft = builder.extract_value(lql__cft, 0)
        return builder.bitcast(builder.gep(lql__cft, [ind]), lir.IntType(8)
            .as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        lql__cft, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lql__cft = builder.extract_value(lql__cft, 0)
        return builder.load(builder.gep(lql__cft, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        lql__cft, ind, vjzi__ohhk = args
        ahmg__gllld = builder.gep(lql__cft, [ind])
        builder.store(vjzi__ohhk, ahmg__gllld)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        vwo__jzzzn, ind = args
        uxocd__upo = context.make_helper(builder, arr_ctypes_t, vwo__jzzzn)
        wfjc__cjmpp = context.make_helper(builder, arr_ctypes_t)
        wfjc__cjmpp.data = builder.gep(uxocd__upo.data, [ind])
        wfjc__cjmpp.meminfo = uxocd__upo.meminfo
        jwdeg__qpt = wfjc__cjmpp._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, jwdeg__qpt)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    zfki__jtwv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not zfki__jtwv:
        return 0, 0, 0
    wnj__iqot = getitem_c_arr(arr._index_offsets, item_ind)
    bsc__qzii = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    yhz__tilhi = bsc__qzii - wnj__iqot
    if str_ind >= yhz__tilhi:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, wnj__iqot + str_ind)
    data_start += 1
    if wnj__iqot + str_ind == 0:
        data_start = 0
    zdl__pxqy = getitem_c_arr(arr._data_offsets, wnj__iqot + str_ind + 1)
    kckau__bqd = zdl__pxqy - data_start
    return 1, data_start, kckau__bqd


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
        gyimx__paa = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            wnj__iqot = getitem_c_arr(A._index_offsets, ind)
            bsc__qzii = getitem_c_arr(A._index_offsets, ind + 1)
            lyvy__kxhrz = bsc__qzii - wnj__iqot - 1
            tqg__jlzw = bodo.libs.str_arr_ext.pre_alloc_string_array(
                lyvy__kxhrz, -1)
            for euimg__wqbaw in range(lyvy__kxhrz):
                data_start = getitem_c_arr(A._data_offsets, wnj__iqot +
                    euimg__wqbaw)
                data_start += 1
                if wnj__iqot + euimg__wqbaw == 0:
                    data_start = 0
                zdl__pxqy = getitem_c_arr(A._data_offsets, wnj__iqot +
                    euimg__wqbaw + 1)
                kckau__bqd = zdl__pxqy - data_start
                ahmg__gllld = get_array_ctypes_ptr(A._data, data_start)
                scjmr__dcmzi = bodo.libs.str_arr_ext.decode_utf8(ahmg__gllld,
                    kckau__bqd)
                tqg__jlzw[euimg__wqbaw] = scjmr__dcmzi
            return tqg__jlzw
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        myykj__cvtw = offset_type.bitwidth // 8

        def _impl(A, ind):
            lyvy__kxhrz = len(A)
            if lyvy__kxhrz != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ohcvy__dguy = 0
            qwn__kyi = 0
            for euimg__wqbaw in range(lyvy__kxhrz):
                if ind[euimg__wqbaw]:
                    ohcvy__dguy += 1
                    wnj__iqot = getitem_c_arr(A._index_offsets, euimg__wqbaw)
                    bsc__qzii = getitem_c_arr(A._index_offsets, 
                        euimg__wqbaw + 1)
                    qwn__kyi += bsc__qzii - wnj__iqot
            yeto__inc = pre_alloc_str_arr_view(ohcvy__dguy, qwn__kyi, A._data)
            item_ind = 0
            vdpy__sih = 0
            for euimg__wqbaw in range(lyvy__kxhrz):
                if ind[euimg__wqbaw]:
                    wnj__iqot = getitem_c_arr(A._index_offsets, euimg__wqbaw)
                    bsc__qzii = getitem_c_arr(A._index_offsets, 
                        euimg__wqbaw + 1)
                    hvt__hvt = bsc__qzii - wnj__iqot
                    setitem_c_arr(yeto__inc._index_offsets, item_ind, vdpy__sih
                        )
                    ahmg__gllld = get_c_arr_ptr(A._data_offsets, wnj__iqot)
                    almhu__hzk = get_c_arr_ptr(yeto__inc._data_offsets,
                        vdpy__sih)
                    _memcpy(almhu__hzk, ahmg__gllld, hvt__hvt, myykj__cvtw)
                    zfki__jtwv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, euimg__wqbaw)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yeto__inc.
                        _null_bitmap, item_ind, zfki__jtwv)
                    item_ind += 1
                    vdpy__sih += hvt__hvt
            setitem_c_arr(yeto__inc._index_offsets, item_ind, vdpy__sih)
            return yeto__inc
        return _impl
