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
        gmcgp__vjq = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, gmcgp__vjq)


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
    atf__hjhtn = context.get_value_type(str_arr_split_view_payload_type)
    hozxa__myls = context.get_abi_sizeof(atf__hjhtn)
    qhtx__jbmlg = context.get_value_type(types.voidptr)
    xypwa__qmn = context.get_value_type(types.uintp)
    hbvn__tvwlw = lir.FunctionType(lir.VoidType(), [qhtx__jbmlg, xypwa__qmn,
        qhtx__jbmlg])
    ectnb__retg = cgutils.get_or_insert_function(builder.module,
        hbvn__tvwlw, name='dtor_str_arr_split_view')
    xjez__kft = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, hozxa__myls), ectnb__retg)
    uyskv__juni = context.nrt.meminfo_data(builder, xjez__kft)
    jom__fqmkp = builder.bitcast(uyskv__juni, atf__hjhtn.as_pointer())
    return xjez__kft, jom__fqmkp


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        gkvxk__hfzmf, jzdq__jnej = args
        xjez__kft, jom__fqmkp = construct_str_arr_split_view(context, builder)
        noqcp__ddeav = _get_str_binary_arr_payload(context, builder,
            gkvxk__hfzmf, string_array_type)
        rtjhu__pcwt = lir.FunctionType(lir.VoidType(), [jom__fqmkp.type,
            lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        bnbuy__sjir = cgutils.get_or_insert_function(builder.module,
            rtjhu__pcwt, name='str_arr_split_view_impl')
        vzbj__esiei = context.make_helper(builder, offset_arr_type,
            noqcp__ddeav.offsets).data
        qdoui__fjwqc = context.make_helper(builder, char_arr_type,
            noqcp__ddeav.data).data
        sovzn__oog = context.make_helper(builder, null_bitmap_arr_type,
            noqcp__ddeav.null_bitmap).data
        oqte__ylozm = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(bnbuy__sjir, [jom__fqmkp, noqcp__ddeav.n_arrays,
            vzbj__esiei, qdoui__fjwqc, sovzn__oog, oqte__ylozm])
        pei__wrf = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(jom__fqmkp))
        olkut__jpej = context.make_helper(builder, string_array_split_view_type
            )
        olkut__jpej.num_items = noqcp__ddeav.n_arrays
        olkut__jpej.index_offsets = pei__wrf.index_offsets
        olkut__jpej.data_offsets = pei__wrf.data_offsets
        olkut__jpej.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [
            gkvxk__hfzmf])
        olkut__jpej.null_bitmap = pei__wrf.null_bitmap
        olkut__jpej.meminfo = xjez__kft
        ubutp__vjrfh = olkut__jpej._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ubutp__vjrfh)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    ley__tiln = context.make_helper(builder, string_array_split_view_type, val)
    qut__viul = context.insert_const_string(builder.module, 'numpy')
    xnd__xokp = c.pyapi.import_module_noblock(qut__viul)
    dtype = c.pyapi.object_getattr_string(xnd__xokp, 'object_')
    xcol__mqmu = builder.sext(ley__tiln.num_items, c.pyapi.longlong)
    yodl__crbpq = c.pyapi.long_from_longlong(xcol__mqmu)
    lctp__uxpz = c.pyapi.call_method(xnd__xokp, 'ndarray', (yodl__crbpq, dtype)
        )
    banju__gvjl = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    ayhr__ombyn = c.pyapi._get_function(banju__gvjl, name='array_getptr1')
    yckq__tdb = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    jozh__cqi = c.pyapi._get_function(yckq__tdb, name='array_setitem')
    wvrj__sbm = c.pyapi.object_getattr_string(xnd__xokp, 'nan')
    with cgutils.for_range(builder, ley__tiln.num_items) as jzwa__eev:
        str_ind = jzwa__eev.index
        vrxa__sssr = builder.sext(builder.load(builder.gep(ley__tiln.
            index_offsets, [str_ind])), lir.IntType(64))
        wytsp__lmii = builder.sext(builder.load(builder.gep(ley__tiln.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        oysy__afrwr = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        jbc__ivac = builder.gep(ley__tiln.null_bitmap, [oysy__afrwr])
        ezpl__mchgv = builder.load(jbc__ivac)
        sus__thhst = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(ezpl__mchgv, sus__thhst), lir.
            Constant(lir.IntType(8), 1))
        ptg__gnm = builder.sub(wytsp__lmii, vrxa__sssr)
        ptg__gnm = builder.sub(ptg__gnm, ptg__gnm.type(1))
        iybk__xoc = builder.call(ayhr__ombyn, [lctp__uxpz, str_ind])
        ugdgj__jwkm = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(ugdgj__jwkm) as (bvbaa__mctbk, xxr__xgz):
            with bvbaa__mctbk:
                vxzvf__ucy = c.pyapi.list_new(ptg__gnm)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    vxzvf__ucy), likely=True):
                    with cgutils.for_range(c.builder, ptg__gnm) as jzwa__eev:
                        dbyzx__lvzru = builder.add(vrxa__sssr, jzwa__eev.index)
                        data_start = builder.load(builder.gep(ley__tiln.
                            data_offsets, [dbyzx__lvzru]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        kpu__msr = builder.load(builder.gep(ley__tiln.
                            data_offsets, [builder.add(dbyzx__lvzru,
                            dbyzx__lvzru.type(1))]))
                        rrh__ndgsh = builder.gep(builder.extract_value(
                            ley__tiln.data, 0), [data_start])
                        wvygi__kbk = builder.sext(builder.sub(kpu__msr,
                            data_start), lir.IntType(64))
                        zrti__lyl = c.pyapi.string_from_string_and_size(
                            rrh__ndgsh, wvygi__kbk)
                        c.pyapi.list_setitem(vxzvf__ucy, jzwa__eev.index,
                            zrti__lyl)
                builder.call(jozh__cqi, [lctp__uxpz, iybk__xoc, vxzvf__ucy])
            with xxr__xgz:
                builder.call(jozh__cqi, [lctp__uxpz, iybk__xoc, wvrj__sbm])
    c.pyapi.decref(xnd__xokp)
    c.pyapi.decref(dtype)
    c.pyapi.decref(wvrj__sbm)
    return lctp__uxpz


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ttll__kmqhw, wfyu__caig, rrh__ndgsh = args
        xjez__kft, jom__fqmkp = construct_str_arr_split_view(context, builder)
        rtjhu__pcwt = lir.FunctionType(lir.VoidType(), [jom__fqmkp.type,
            lir.IntType(64), lir.IntType(64)])
        bnbuy__sjir = cgutils.get_or_insert_function(builder.module,
            rtjhu__pcwt, name='str_arr_split_view_alloc')
        builder.call(bnbuy__sjir, [jom__fqmkp, ttll__kmqhw, wfyu__caig])
        pei__wrf = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(jom__fqmkp))
        olkut__jpej = context.make_helper(builder, string_array_split_view_type
            )
        olkut__jpej.num_items = ttll__kmqhw
        olkut__jpej.index_offsets = pei__wrf.index_offsets
        olkut__jpej.data_offsets = pei__wrf.data_offsets
        olkut__jpej.data = rrh__ndgsh
        olkut__jpej.null_bitmap = pei__wrf.null_bitmap
        context.nrt.incref(builder, data_t, rrh__ndgsh)
        olkut__jpej.meminfo = xjez__kft
        ubutp__vjrfh = olkut__jpej._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ubutp__vjrfh)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        qqivj__gorsk, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            qqivj__gorsk = builder.extract_value(qqivj__gorsk, 0)
        return builder.bitcast(builder.gep(qqivj__gorsk, [ind]), lir.
            IntType(8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        qqivj__gorsk, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            qqivj__gorsk = builder.extract_value(qqivj__gorsk, 0)
        return builder.load(builder.gep(qqivj__gorsk, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        qqivj__gorsk, ind, ayy__jyo = args
        zslh__lpmd = builder.gep(qqivj__gorsk, [ind])
        builder.store(ayy__jyo, zslh__lpmd)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        bwzw__gzra, ind = args
        ajbr__jtfk = context.make_helper(builder, arr_ctypes_t, bwzw__gzra)
        yujev__haeoy = context.make_helper(builder, arr_ctypes_t)
        yujev__haeoy.data = builder.gep(ajbr__jtfk.data, [ind])
        yujev__haeoy.meminfo = ajbr__jtfk.meminfo
        xtlq__dpyj = yujev__haeoy._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, xtlq__dpyj)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    suq__ffma = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not suq__ffma:
        return 0, 0, 0
    dbyzx__lvzru = getitem_c_arr(arr._index_offsets, item_ind)
    oxmr__xwcls = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    ian__iyoh = oxmr__xwcls - dbyzx__lvzru
    if str_ind >= ian__iyoh:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, dbyzx__lvzru + str_ind)
    data_start += 1
    if dbyzx__lvzru + str_ind == 0:
        data_start = 0
    kpu__msr = getitem_c_arr(arr._data_offsets, dbyzx__lvzru + str_ind + 1)
    qkvjp__oecm = kpu__msr - data_start
    return 1, data_start, qkvjp__oecm


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
        vwmlq__qweg = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            dbyzx__lvzru = getitem_c_arr(A._index_offsets, ind)
            oxmr__xwcls = getitem_c_arr(A._index_offsets, ind + 1)
            mow__wxrk = oxmr__xwcls - dbyzx__lvzru - 1
            gkvxk__hfzmf = bodo.libs.str_arr_ext.pre_alloc_string_array(
                mow__wxrk, -1)
            for pgk__rgd in range(mow__wxrk):
                data_start = getitem_c_arr(A._data_offsets, dbyzx__lvzru +
                    pgk__rgd)
                data_start += 1
                if dbyzx__lvzru + pgk__rgd == 0:
                    data_start = 0
                kpu__msr = getitem_c_arr(A._data_offsets, dbyzx__lvzru +
                    pgk__rgd + 1)
                qkvjp__oecm = kpu__msr - data_start
                zslh__lpmd = get_array_ctypes_ptr(A._data, data_start)
                rdigc__qyt = bodo.libs.str_arr_ext.decode_utf8(zslh__lpmd,
                    qkvjp__oecm)
                gkvxk__hfzmf[pgk__rgd] = rdigc__qyt
            return gkvxk__hfzmf
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        xleo__pfu = offset_type.bitwidth // 8

        def _impl(A, ind):
            mow__wxrk = len(A)
            if mow__wxrk != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ttll__kmqhw = 0
            wfyu__caig = 0
            for pgk__rgd in range(mow__wxrk):
                if ind[pgk__rgd]:
                    ttll__kmqhw += 1
                    dbyzx__lvzru = getitem_c_arr(A._index_offsets, pgk__rgd)
                    oxmr__xwcls = getitem_c_arr(A._index_offsets, pgk__rgd + 1)
                    wfyu__caig += oxmr__xwcls - dbyzx__lvzru
            lctp__uxpz = pre_alloc_str_arr_view(ttll__kmqhw, wfyu__caig, A.
                _data)
            item_ind = 0
            nhc__luh = 0
            for pgk__rgd in range(mow__wxrk):
                if ind[pgk__rgd]:
                    dbyzx__lvzru = getitem_c_arr(A._index_offsets, pgk__rgd)
                    oxmr__xwcls = getitem_c_arr(A._index_offsets, pgk__rgd + 1)
                    yuk__cwfex = oxmr__xwcls - dbyzx__lvzru
                    setitem_c_arr(lctp__uxpz._index_offsets, item_ind, nhc__luh
                        )
                    zslh__lpmd = get_c_arr_ptr(A._data_offsets, dbyzx__lvzru)
                    vejd__isc = get_c_arr_ptr(lctp__uxpz._data_offsets,
                        nhc__luh)
                    _memcpy(vejd__isc, zslh__lpmd, yuk__cwfex, xleo__pfu)
                    suq__ffma = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, pgk__rgd)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lctp__uxpz.
                        _null_bitmap, item_ind, suq__ffma)
                    item_ind += 1
                    nhc__luh += yuk__cwfex
            setitem_c_arr(lctp__uxpz._index_offsets, item_ind, nhc__luh)
            return lctp__uxpz
        return _impl
