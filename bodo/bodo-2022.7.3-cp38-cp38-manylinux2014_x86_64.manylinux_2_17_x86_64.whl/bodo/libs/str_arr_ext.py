"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoArrayIterator, BodoError, decode_if_dict_array, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hcymi__hlpa = ArrayItemArrayType(char_arr_type)
        zyu__dnl = [('data', hcymi__hlpa)]
        models.StructModel.__init__(self, dmm, fe_type, zyu__dnl)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        aikj__ohagp, = args
        hovwp__maws = context.make_helper(builder, string_array_type)
        hovwp__maws.data = aikj__ohagp
        context.nrt.incref(builder, data_typ, aikj__ohagp)
        return hovwp__maws._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    jvuwx__wmb = c.context.insert_const_string(c.builder.module, 'pandas')
    drou__cmfq = c.pyapi.import_module_noblock(jvuwx__wmb)
    ucgeg__mfyyv = c.pyapi.call_method(drou__cmfq, 'StringDtype', ())
    c.pyapi.decref(drou__cmfq)
    return ucgeg__mfyyv


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        njkz__erzt = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if njkz__erzt is not None:
            return njkz__erzt
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                bfi__sdky = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bfi__sdky)
                for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                bfi__sdky = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bfi__sdky)
                for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                bfi__sdky = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bfi__sdky)
                for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise_bodo_error(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    ayqv__ivtx = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    mle__fvlz = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and mle__fvlz or ayqv__ivtx and is_str_arr_type(rhs
        ):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if is_str_arr_type(lhs) and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and is_str_arr_type(rhs):

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    dtzfo__uye = context.make_helper(builder, arr_typ, arr_value)
    hcymi__hlpa = ArrayItemArrayType(char_arr_type)
    bnv__oikt = _get_array_item_arr_payload(context, builder, hcymi__hlpa,
        dtzfo__uye.data)
    return bnv__oikt


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return bnv__oikt.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        sjbrh__bmz = context.make_helper(builder, offset_arr_type,
            bnv__oikt.offsets).data
        return _get_num_total_chars(builder, sjbrh__bmz, bnv__oikt.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        cbzoo__thsau = context.make_helper(builder, offset_arr_type,
            bnv__oikt.offsets)
        aaj__zgacu = context.make_helper(builder, offset_ctypes_type)
        aaj__zgacu.data = builder.bitcast(cbzoo__thsau.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        aaj__zgacu.meminfo = cbzoo__thsau.meminfo
        ucgeg__mfyyv = aaj__zgacu._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            ucgeg__mfyyv)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        aikj__ohagp = context.make_helper(builder, char_arr_type, bnv__oikt
            .data)
        aaj__zgacu = context.make_helper(builder, data_ctypes_type)
        aaj__zgacu.data = aikj__ohagp.data
        aaj__zgacu.meminfo = aikj__ohagp.meminfo
        ucgeg__mfyyv = aaj__zgacu._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            ucgeg__mfyyv)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        xbf__ppzc, ind = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder, xbf__ppzc,
            sig.args[0])
        aikj__ohagp = context.make_helper(builder, char_arr_type, bnv__oikt
            .data)
        aaj__zgacu = context.make_helper(builder, data_ctypes_type)
        aaj__zgacu.data = builder.gep(aikj__ohagp.data, [ind])
        aaj__zgacu.meminfo = aikj__ohagp.meminfo
        ucgeg__mfyyv = aaj__zgacu._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            ucgeg__mfyyv)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        kwak__qrx, rqxol__rnyw, rctmy__zqsk, vkyhr__oxy = args
        gjyl__yag = builder.bitcast(builder.gep(kwak__qrx, [rqxol__rnyw]),
            lir.IntType(8).as_pointer())
        ndvx__mlw = builder.bitcast(builder.gep(rctmy__zqsk, [vkyhr__oxy]),
            lir.IntType(8).as_pointer())
        mrgfu__xctp = builder.load(ndvx__mlw)
        builder.store(mrgfu__xctp, gjyl__yag)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        tupen__yaxim = context.make_helper(builder, null_bitmap_arr_type,
            bnv__oikt.null_bitmap)
        aaj__zgacu = context.make_helper(builder, data_ctypes_type)
        aaj__zgacu.data = tupen__yaxim.data
        aaj__zgacu.meminfo = tupen__yaxim.meminfo
        ucgeg__mfyyv = aaj__zgacu._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            ucgeg__mfyyv)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        sjbrh__bmz = context.make_helper(builder, offset_arr_type,
            bnv__oikt.offsets).data
        return builder.load(builder.gep(sjbrh__bmz, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, bnv__oikt.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        wcuxi__yxsie, ind = args
        if in_bitmap_typ == data_ctypes_type:
            aaj__zgacu = context.make_helper(builder, data_ctypes_type,
                wcuxi__yxsie)
            wcuxi__yxsie = aaj__zgacu.data
        return builder.load(builder.gep(wcuxi__yxsie, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        wcuxi__yxsie, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            aaj__zgacu = context.make_helper(builder, data_ctypes_type,
                wcuxi__yxsie)
            wcuxi__yxsie = aaj__zgacu.data
        builder.store(val, builder.gep(wcuxi__yxsie, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        mrjj__rzd = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ttvp__uuhk = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jqmvi__qkgvs = context.make_helper(builder, offset_arr_type,
            mrjj__rzd.offsets).data
        jcwn__ssyfe = context.make_helper(builder, offset_arr_type,
            ttvp__uuhk.offsets).data
        kins__lwga = context.make_helper(builder, char_arr_type, mrjj__rzd.data
            ).data
        jksms__rmauv = context.make_helper(builder, char_arr_type,
            ttvp__uuhk.data).data
        dszp__gzws = context.make_helper(builder, null_bitmap_arr_type,
            mrjj__rzd.null_bitmap).data
        pzdwj__hhym = context.make_helper(builder, null_bitmap_arr_type,
            ttvp__uuhk.null_bitmap).data
        miwk__dlk = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, jcwn__ssyfe, jqmvi__qkgvs, miwk__dlk)
        cgutils.memcpy(builder, jksms__rmauv, kins__lwga, builder.load(
            builder.gep(jqmvi__qkgvs, [ind])))
        kjqd__qkw = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        veqq__nannq = builder.lshr(kjqd__qkw, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, pzdwj__hhym, dszp__gzws, veqq__nannq)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        mrjj__rzd = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ttvp__uuhk = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jqmvi__qkgvs = context.make_helper(builder, offset_arr_type,
            mrjj__rzd.offsets).data
        kins__lwga = context.make_helper(builder, char_arr_type, mrjj__rzd.data
            ).data
        jksms__rmauv = context.make_helper(builder, char_arr_type,
            ttvp__uuhk.data).data
        num_total_chars = _get_num_total_chars(builder, jqmvi__qkgvs,
            mrjj__rzd.n_arrays)
        cgutils.memcpy(builder, jksms__rmauv, kins__lwga, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        mrjj__rzd = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ttvp__uuhk = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        jqmvi__qkgvs = context.make_helper(builder, offset_arr_type,
            mrjj__rzd.offsets).data
        jcwn__ssyfe = context.make_helper(builder, offset_arr_type,
            ttvp__uuhk.offsets).data
        dszp__gzws = context.make_helper(builder, null_bitmap_arr_type,
            mrjj__rzd.null_bitmap).data
        bfi__sdky = mrjj__rzd.n_arrays
        dsrra__plrof = context.get_constant(offset_type, 0)
        eqh__yrqxl = cgutils.alloca_once_value(builder, dsrra__plrof)
        with cgutils.for_range(builder, bfi__sdky) as fkbsx__uozi:
            sbtr__kcbu = lower_is_na(context, builder, dszp__gzws,
                fkbsx__uozi.index)
            with cgutils.if_likely(builder, builder.not_(sbtr__kcbu)):
                sclbq__rzii = builder.load(builder.gep(jqmvi__qkgvs, [
                    fkbsx__uozi.index]))
                korh__ghseb = builder.load(eqh__yrqxl)
                builder.store(sclbq__rzii, builder.gep(jcwn__ssyfe, [
                    korh__ghseb]))
                builder.store(builder.add(korh__ghseb, lir.Constant(context
                    .get_value_type(offset_type), 1)), eqh__yrqxl)
        korh__ghseb = builder.load(eqh__yrqxl)
        sclbq__rzii = builder.load(builder.gep(jqmvi__qkgvs, [bfi__sdky]))
        builder.store(sclbq__rzii, builder.gep(jcwn__ssyfe, [korh__ghseb]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        vsdpu__mblq, ind, str, megnl__pug = args
        vsdpu__mblq = context.make_array(sig.args[0])(context, builder,
            vsdpu__mblq)
        oird__kqvsi = builder.gep(vsdpu__mblq.data, [ind])
        cgutils.raw_memcpy(builder, oird__kqvsi, str, megnl__pug, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        oird__kqvsi, ind, kwzqj__uve, megnl__pug = args
        oird__kqvsi = builder.gep(oird__kqvsi, [ind])
        cgutils.raw_memcpy(builder, oird__kqvsi, kwzqj__uve, megnl__pug, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            ngfw__kbf = A._data
            return np.int64(getitem_str_offset(ngfw__kbf, idx + 1) -
                getitem_str_offset(ngfw__kbf, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    miwc__zufi = np.int64(getitem_str_offset(A, i))
    betfz__rfxcc = np.int64(getitem_str_offset(A, i + 1))
    l = betfz__rfxcc - miwc__zufi
    soyk__hmz = get_data_ptr_ind(A, miwc__zufi)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(soyk__hmz, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.generated_jit(no_cpython_wrapper=True, nopython=True)
def get_str_arr_item_copy(B, j, A, i):
    if B != string_array_type:
        raise BodoError(
            'get_str_arr_item_copy(): Output array must be a string array')
    if not is_str_arr_type(A):
        raise BodoError(
            'get_str_arr_item_copy(): Input array must be a string array or dictionary encoded array'
            )
    if A == bodo.dict_str_arr_type:
        sfp__oumu = 'in_str_arr = A._data'
        lopt__sjx = 'input_index = A._indices[i]'
    else:
        sfp__oumu = 'in_str_arr = A'
        lopt__sjx = 'input_index = i'
    koiis__jpshx = f"""def impl(B, j, A, i):
        if j == 0:
            setitem_str_offset(B, 0, 0)

        {sfp__oumu}
        {lopt__sjx}

        # set NA
        if bodo.libs.array_kernels.isna(A, i):
            str_arr_set_na(B, j)
            return
        else:
            str_arr_set_not_na(B, j)

        # get input array offsets
        in_start_offset = getitem_str_offset(in_str_arr, input_index)
        in_end_offset = getitem_str_offset(in_str_arr, input_index + 1)
        val_len = in_end_offset - in_start_offset

        # set output offset
        out_start_offset = getitem_str_offset(B, j)
        out_end_offset = out_start_offset + val_len
        setitem_str_offset(B, j + 1, out_end_offset)

        # copy data
        if val_len != 0:
            # ensure required space in output array
            data_arr = B._data
            bodo.libs.array_item_arr_ext.ensure_data_capacity(
                data_arr, np.int64(out_start_offset), np.int64(out_end_offset)
            )
            out_data_ptr = get_data_ptr(B).data
            in_data_ptr = get_data_ptr(in_str_arr).data
            memcpy_region(
                out_data_ptr,
                out_start_offset,
                in_data_ptr,
                in_start_offset,
                val_len,
                1,
            )"""
    tbmgw__ewtfv = {}
    exec(koiis__jpshx, {'setitem_str_offset': setitem_str_offset,
        'memcpy_region': memcpy_region, 'getitem_str_offset':
        getitem_str_offset, 'str_arr_set_na': str_arr_set_na,
        'str_arr_set_not_na': str_arr_set_not_na, 'get_data_ptr':
        get_data_ptr, 'bodo': bodo, 'np': np}, tbmgw__ewtfv)
    impl = tbmgw__ewtfv['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    bfi__sdky = len(str_arr)
    zueg__vku = np.empty(bfi__sdky, np.bool_)
    for i in range(bfi__sdky):
        zueg__vku[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return zueg__vku


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            bfi__sdky = len(data)
            l = []
            for i in range(bfi__sdky):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        dtcu__okryg = data.count
        vyaer__velpf = ['to_list_if_immutable_arr(data[{}])'.format(i) for
            i in range(dtcu__okryg)]
        if is_overload_true(str_null_bools):
            vyaer__velpf += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(dtcu__okryg) if is_str_arr_type(data.types[i]) or 
                data.types[i] == binary_array_type]
        koiis__jpshx = 'def f(data, str_null_bools=None):\n'
        koiis__jpshx += '  return ({}{})\n'.format(', '.join(vyaer__velpf),
            ',' if dtcu__okryg == 1 else '')
        tbmgw__ewtfv = {}
        exec(koiis__jpshx, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, tbmgw__ewtfv)
        nzc__clzj = tbmgw__ewtfv['f']
        return nzc__clzj
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                bfi__sdky = len(list_data)
                for i in range(bfi__sdky):
                    kwzqj__uve = list_data[i]
                    str_arr[i] = kwzqj__uve
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                bfi__sdky = len(list_data)
                for i in range(bfi__sdky):
                    kwzqj__uve = list_data[i]
                    str_arr[i] = kwzqj__uve
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        dtcu__okryg = str_arr.count
        cntmk__wlx = 0
        koiis__jpshx = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(dtcu__okryg):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                koiis__jpshx += (
                    """  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])
"""
                    .format(i, i, dtcu__okryg + cntmk__wlx))
                cntmk__wlx += 1
            else:
                koiis__jpshx += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        koiis__jpshx += '  return\n'
        tbmgw__ewtfv = {}
        exec(koiis__jpshx, {'cp_str_list_to_array': cp_str_list_to_array},
            tbmgw__ewtfv)
        gism__xxa = tbmgw__ewtfv['f']
        return gism__xxa
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            bfi__sdky = len(str_list)
            str_arr = pre_alloc_string_array(bfi__sdky, -1)
            for i in range(bfi__sdky):
                kwzqj__uve = str_list[i]
                str_arr[i] = kwzqj__uve
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            bfi__sdky = len(A)
            xaifh__mtxqd = 0
            for i in range(bfi__sdky):
                kwzqj__uve = A[i]
                xaifh__mtxqd += get_utf8_size(kwzqj__uve)
            return xaifh__mtxqd
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        bfi__sdky = len(arr)
        n_chars = num_total_chars(arr)
        wijc__ljcd = pre_alloc_string_array(bfi__sdky, np.int64(n_chars))
        copy_str_arr_slice(wijc__ljcd, arr, bfi__sdky)
        return wijc__ljcd
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    koiis__jpshx = 'def f(in_seq):\n'
    koiis__jpshx += '    n_strs = len(in_seq)\n'
    koiis__jpshx += '    A = pre_alloc_string_array(n_strs, -1)\n'
    koiis__jpshx += '    return A\n'
    tbmgw__ewtfv = {}
    exec(koiis__jpshx, {'pre_alloc_string_array': pre_alloc_string_array},
        tbmgw__ewtfv)
    iyi__vdjo = tbmgw__ewtfv['f']
    return iyi__vdjo


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        zdcha__kupid = 'pre_alloc_binary_array'
    else:
        zdcha__kupid = 'pre_alloc_string_array'
    koiis__jpshx = 'def f(in_seq):\n'
    koiis__jpshx += '    n_strs = len(in_seq)\n'
    koiis__jpshx += f'    A = {zdcha__kupid}(n_strs, -1)\n'
    koiis__jpshx += '    for i in range(n_strs):\n'
    koiis__jpshx += '        A[i] = in_seq[i]\n'
    koiis__jpshx += '    return A\n'
    tbmgw__ewtfv = {}
    exec(koiis__jpshx, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, tbmgw__ewtfv)
    iyi__vdjo = tbmgw__ewtfv['f']
    return iyi__vdjo


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        jjttm__qyipy = builder.add(bnv__oikt.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        cgjgv__vwyt = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        veqq__nannq = builder.mul(jjttm__qyipy, cgjgv__vwyt)
        cxlcr__zodsu = context.make_array(offset_arr_type)(context, builder,
            bnv__oikt.offsets).data
        cgutils.memset(builder, cxlcr__zodsu, veqq__nannq, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ikri__nevjs = bnv__oikt.n_arrays
        veqq__nannq = builder.lshr(builder.add(ikri__nevjs, lir.Constant(
            lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        yvtb__ykty = context.make_array(null_bitmap_arr_type)(context,
            builder, bnv__oikt.null_bitmap).data
        cgutils.memset(builder, yvtb__ykty, veqq__nannq, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    mqr__zniit = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        yjq__crbs = len(len_arr)
        for i in range(yjq__crbs):
            offsets[i] = mqr__zniit
            mqr__zniit += len_arr[i]
        offsets[yjq__crbs] = mqr__zniit
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    rdkhb__mzj = i // 8
    rhmpn__cbql = getitem_str_bitmap(bits, rdkhb__mzj)
    rhmpn__cbql ^= np.uint8(-np.uint8(bit_is_set) ^ rhmpn__cbql) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, rdkhb__mzj, rhmpn__cbql)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    dqe__onsy = get_null_bitmap_ptr(out_str_arr)
    wslsq__wfwqy = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        clhdi__farym = get_bit_bitmap(wslsq__wfwqy, j)
        set_bit_to(dqe__onsy, out_start + j, clhdi__farym)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, xbf__ppzc, iss__etfe, zwi__way = args
        mrjj__rzd = _get_str_binary_arr_payload(context, builder, xbf__ppzc,
            string_array_type)
        ttvp__uuhk = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        jqmvi__qkgvs = context.make_helper(builder, offset_arr_type,
            mrjj__rzd.offsets).data
        jcwn__ssyfe = context.make_helper(builder, offset_arr_type,
            ttvp__uuhk.offsets).data
        kins__lwga = context.make_helper(builder, char_arr_type, mrjj__rzd.data
            ).data
        jksms__rmauv = context.make_helper(builder, char_arr_type,
            ttvp__uuhk.data).data
        num_total_chars = _get_num_total_chars(builder, jqmvi__qkgvs,
            mrjj__rzd.n_arrays)
        izni__vvx = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        htq__zhil = cgutils.get_or_insert_function(builder.module,
            izni__vvx, name='set_string_array_range')
        builder.call(htq__zhil, [jcwn__ssyfe, jksms__rmauv, jqmvi__qkgvs,
            kins__lwga, iss__etfe, zwi__way, mrjj__rzd.n_arrays,
            num_total_chars])
        smzc__btu = context.typing_context.resolve_value_type(copy_nulls_range)
        zqy__pfcsi = smzc__btu.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        qigt__ggi = context.get_function(smzc__btu, zqy__pfcsi)
        qigt__ggi(builder, (out_arr, xbf__ppzc, iss__etfe))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    gnr__ccq = c.context.make_helper(c.builder, typ, val)
    hcymi__hlpa = ArrayItemArrayType(char_arr_type)
    bnv__oikt = _get_array_item_arr_payload(c.context, c.builder,
        hcymi__hlpa, gnr__ccq.data)
    laaom__ipkb = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    mkavq__etpd = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        mkavq__etpd = 'pd_array_from_string_array'
    izni__vvx = lir.FunctionType(c.context.get_argument_type(types.pyobject
        ), [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    odcb__fzddg = cgutils.get_or_insert_function(c.builder.module,
        izni__vvx, name=mkavq__etpd)
    sjbrh__bmz = c.context.make_array(offset_arr_type)(c.context, c.builder,
        bnv__oikt.offsets).data
    soyk__hmz = c.context.make_array(char_arr_type)(c.context, c.builder,
        bnv__oikt.data).data
    yvtb__ykty = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, bnv__oikt.null_bitmap).data
    arr = c.builder.call(odcb__fzddg, [bnv__oikt.n_arrays, sjbrh__bmz,
        soyk__hmz, yvtb__ykty, laaom__ipkb])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        yvtb__ykty = context.make_array(null_bitmap_arr_type)(context,
            builder, bnv__oikt.null_bitmap).data
        bsa__tff = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ksfkq__rcyk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        rhmpn__cbql = builder.load(builder.gep(yvtb__ykty, [bsa__tff],
            inbounds=True))
        mpjry__wqp = lir.ArrayType(lir.IntType(8), 8)
        jeia__sla = cgutils.alloca_once_value(builder, lir.Constant(
            mpjry__wqp, (1, 2, 4, 8, 16, 32, 64, 128)))
        xotsm__suhc = builder.load(builder.gep(jeia__sla, [lir.Constant(lir
            .IntType(64), 0), ksfkq__rcyk], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(rhmpn__cbql,
            xotsm__suhc), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bsa__tff = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ksfkq__rcyk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        yvtb__ykty = context.make_array(null_bitmap_arr_type)(context,
            builder, bnv__oikt.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, bnv__oikt.
            offsets).data
        lhj__llgo = builder.gep(yvtb__ykty, [bsa__tff], inbounds=True)
        rhmpn__cbql = builder.load(lhj__llgo)
        mpjry__wqp = lir.ArrayType(lir.IntType(8), 8)
        jeia__sla = cgutils.alloca_once_value(builder, lir.Constant(
            mpjry__wqp, (1, 2, 4, 8, 16, 32, 64, 128)))
        xotsm__suhc = builder.load(builder.gep(jeia__sla, [lir.Constant(lir
            .IntType(64), 0), ksfkq__rcyk], inbounds=True))
        xotsm__suhc = builder.xor(xotsm__suhc, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(rhmpn__cbql, xotsm__suhc), lhj__llgo)
        if str_arr_typ == string_array_type:
            yfb__scpbf = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            lhrbs__zly = builder.icmp_unsigned('!=', yfb__scpbf, bnv__oikt.
                n_arrays)
            with builder.if_then(lhrbs__zly):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [yfb__scpbf]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bsa__tff = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ksfkq__rcyk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        yvtb__ykty = context.make_array(null_bitmap_arr_type)(context,
            builder, bnv__oikt.null_bitmap).data
        lhj__llgo = builder.gep(yvtb__ykty, [bsa__tff], inbounds=True)
        rhmpn__cbql = builder.load(lhj__llgo)
        mpjry__wqp = lir.ArrayType(lir.IntType(8), 8)
        jeia__sla = cgutils.alloca_once_value(builder, lir.Constant(
            mpjry__wqp, (1, 2, 4, 8, 16, 32, 64, 128)))
        xotsm__suhc = builder.load(builder.gep(jeia__sla, [lir.Constant(lir
            .IntType(64), 0), ksfkq__rcyk], inbounds=True))
        builder.store(builder.or_(rhmpn__cbql, xotsm__suhc), lhj__llgo)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        veqq__nannq = builder.udiv(builder.add(bnv__oikt.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        yvtb__ykty = context.make_array(null_bitmap_arr_type)(context,
            builder, bnv__oikt.null_bitmap).data
        cgutils.memset(builder, yvtb__ykty, veqq__nannq, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    qqro__bmvo = context.make_helper(builder, string_array_type, str_arr)
    hcymi__hlpa = ArrayItemArrayType(char_arr_type)
    rzq__cnw = context.make_helper(builder, hcymi__hlpa, qqro__bmvo.data)
    dttd__gomof = ArrayItemArrayPayloadType(hcymi__hlpa)
    tbg__ybfpy = context.nrt.meminfo_data(builder, rzq__cnw.meminfo)
    zfol__krbrd = builder.bitcast(tbg__ybfpy, context.get_value_type(
        dttd__gomof).as_pointer())
    return zfol__krbrd


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        dmsb__ejhze, fhlp__tvax = args
        mno__wuu = _get_str_binary_arr_data_payload_ptr(context, builder,
            fhlp__tvax)
        iiilc__klz = _get_str_binary_arr_data_payload_ptr(context, builder,
            dmsb__ejhze)
        kibki__sxm = _get_str_binary_arr_payload(context, builder,
            fhlp__tvax, sig.args[1])
        bzbib__dmz = _get_str_binary_arr_payload(context, builder,
            dmsb__ejhze, sig.args[0])
        context.nrt.incref(builder, char_arr_type, kibki__sxm.data)
        context.nrt.incref(builder, offset_arr_type, kibki__sxm.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, kibki__sxm.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, bzbib__dmz.data)
        context.nrt.decref(builder, offset_arr_type, bzbib__dmz.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, bzbib__dmz.
            null_bitmap)
        builder.store(builder.load(mno__wuu), iiilc__klz)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        bfi__sdky = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return bfi__sdky
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, oird__kqvsi, yfl__kln = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, bnv__oikt.
            offsets).data
        data = context.make_helper(builder, char_arr_type, bnv__oikt.data).data
        izni__vvx = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        pcar__cgv = cgutils.get_or_insert_function(builder.module,
            izni__vvx, name='setitem_string_array')
        drxjt__amkmp = context.get_constant(types.int32, -1)
        haqw__wak = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, bnv__oikt.
            n_arrays)
        builder.call(pcar__cgv, [offsets, data, num_total_chars, builder.
            extract_value(oird__kqvsi, 0), yfl__kln, drxjt__amkmp,
            haqw__wak, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    izni__vvx = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64)])
    thg__xhe = cgutils.get_or_insert_function(builder.module, izni__vvx,
        name='is_na')
    return builder.call(thg__xhe, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        gjyl__yag, ndvx__mlw, dtcu__okryg, xkb__qiuho = args
        cgutils.raw_memcpy(builder, gjyl__yag, ndvx__mlw, dtcu__okryg,
            xkb__qiuho)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        uwxo__bggle, rkkml__nfn = unicode_to_utf8_and_len(val)
        pms__xnq = getitem_str_offset(A, ind)
        tpxq__ynot = getitem_str_offset(A, ind + 1)
        lja__bbahj = tpxq__ynot - pms__xnq
        if lja__bbahj != rkkml__nfn:
            return False
        oird__kqvsi = get_data_ptr_ind(A, pms__xnq)
        return memcmp(oird__kqvsi, uwxo__bggle, rkkml__nfn) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        pms__xnq = getitem_str_offset(A, ind)
        lja__bbahj = bodo.libs.str_ext.int_to_str_len(val)
        plpc__ohu = pms__xnq + lja__bbahj
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, pms__xnq,
            plpc__ohu)
        oird__kqvsi = get_data_ptr_ind(A, pms__xnq)
        inplace_int64_to_str(oird__kqvsi, lja__bbahj, val)
        setitem_str_offset(A, ind + 1, pms__xnq + lja__bbahj)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        oird__kqvsi, = args
        kho__octyb = context.insert_const_string(builder.module, '<NA>')
        gnrgt__efvsp = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, oird__kqvsi, kho__octyb, gnrgt__efvsp, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    hskp__mmq = len('<NA>')

    def impl(A, ind):
        pms__xnq = getitem_str_offset(A, ind)
        plpc__ohu = pms__xnq + hskp__mmq
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, pms__xnq,
            plpc__ohu)
        oird__kqvsi = get_data_ptr_ind(A, pms__xnq)
        inplace_set_NA_str(oird__kqvsi)
        setitem_str_offset(A, ind + 1, pms__xnq + hskp__mmq)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            pms__xnq = getitem_str_offset(A, ind)
            tpxq__ynot = getitem_str_offset(A, ind + 1)
            yfl__kln = tpxq__ynot - pms__xnq
            oird__kqvsi = get_data_ptr_ind(A, pms__xnq)
            kdi__drmoi = decode_utf8(oird__kqvsi, yfl__kln)
            return kdi__drmoi
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            bfi__sdky = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(bfi__sdky):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            gdzw__jbcrg = get_data_ptr(out_arr).data
            jwak__kmg = get_data_ptr(A).data
            cntmk__wlx = 0
            korh__ghseb = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(bfi__sdky):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    evh__shl = get_str_arr_item_length(A, i)
                    if evh__shl == 1:
                        copy_single_char(gdzw__jbcrg, korh__ghseb,
                            jwak__kmg, getitem_str_offset(A, i))
                    else:
                        memcpy_region(gdzw__jbcrg, korh__ghseb, jwak__kmg,
                            getitem_str_offset(A, i), evh__shl, 1)
                    korh__ghseb += evh__shl
                    setitem_str_offset(out_arr, cntmk__wlx + 1, korh__ghseb)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, cntmk__wlx)
                    else:
                        str_arr_set_not_na(out_arr, cntmk__wlx)
                    cntmk__wlx += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            bfi__sdky = len(ind)
            out_arr = pre_alloc_string_array(bfi__sdky, -1)
            cntmk__wlx = 0
            for i in range(bfi__sdky):
                kwzqj__uve = A[ind[i]]
                out_arr[cntmk__wlx] = kwzqj__uve
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, cntmk__wlx)
                cntmk__wlx += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            bfi__sdky = len(A)
            omtzr__nsq = numba.cpython.unicode._normalize_slice(ind, bfi__sdky)
            lqfry__lmrxl = numba.cpython.unicode._slice_span(omtzr__nsq)
            if omtzr__nsq.step == 1:
                pms__xnq = getitem_str_offset(A, omtzr__nsq.start)
                tpxq__ynot = getitem_str_offset(A, omtzr__nsq.stop)
                n_chars = tpxq__ynot - pms__xnq
                wijc__ljcd = pre_alloc_string_array(lqfry__lmrxl, np.int64(
                    n_chars))
                for i in range(lqfry__lmrxl):
                    wijc__ljcd[i] = A[omtzr__nsq.start + i]
                    if str_arr_is_na(A, omtzr__nsq.start + i):
                        str_arr_set_na(wijc__ljcd, i)
                return wijc__ljcd
            else:
                wijc__ljcd = pre_alloc_string_array(lqfry__lmrxl, -1)
                for i in range(lqfry__lmrxl):
                    wijc__ljcd[i] = A[omtzr__nsq.start + i * omtzr__nsq.step]
                    if str_arr_is_na(A, omtzr__nsq.start + i * omtzr__nsq.step
                        ):
                        str_arr_set_na(wijc__ljcd, i)
                return wijc__ljcd
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ztrdt__uuo = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(ztrdt__uuo)
        cizb__fgqz = 4

        def impl_scalar(A, idx, val):
            fffb__ekhe = (val._length if val._is_ascii else cizb__fgqz *
                val._length)
            aikj__ohagp = A._data
            pms__xnq = np.int64(getitem_str_offset(A, idx))
            plpc__ohu = pms__xnq + fffb__ekhe
            bodo.libs.array_item_arr_ext.ensure_data_capacity(aikj__ohagp,
                pms__xnq, plpc__ohu)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                plpc__ohu, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                omtzr__nsq = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                miwc__zufi = omtzr__nsq.start
                aikj__ohagp = A._data
                pms__xnq = np.int64(getitem_str_offset(A, miwc__zufi))
                plpc__ohu = pms__xnq + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(aikj__ohagp,
                    pms__xnq, plpc__ohu)
                set_string_array_range(A, val, miwc__zufi, pms__xnq)
                tetuv__esd = 0
                for i in range(omtzr__nsq.start, omtzr__nsq.stop,
                    omtzr__nsq.step):
                    if str_arr_is_na(val, tetuv__esd):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    tetuv__esd += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                brrai__ajaw = str_list_to_array(val)
                A[idx] = brrai__ajaw
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                omtzr__nsq = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(omtzr__nsq.start, omtzr__nsq.stop,
                    omtzr__nsq.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(ztrdt__uuo)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                bfi__sdky = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(bfi__sdky, -1)
                for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                bfi__sdky = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(bfi__sdky, -1)
                qsv__qpeqq = 0
                for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, qsv__qpeqq):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, qsv__qpeqq)
                        else:
                            out_arr[i] = str(val[qsv__qpeqq])
                        qsv__qpeqq += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(ztrdt__uuo)
    raise BodoError(ztrdt__uuo)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    pllt__qoxm = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(pllt__qoxm, (types.Float, types.Integer)
        ) and pllt__qoxm not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(pllt__qoxm, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bfi__sdky = len(A)
            B = np.empty(bfi__sdky, pllt__qoxm)
            for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif pllt__qoxm == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bfi__sdky = len(A)
            B = np.empty(bfi__sdky, pllt__qoxm)
            for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif pllt__qoxm == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bfi__sdky = len(A)
            B = np.empty(bfi__sdky, pllt__qoxm)
            for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bfi__sdky = len(A)
            B = np.empty(bfi__sdky, pllt__qoxm)
            for i in numba.parfors.parfor.internal_prange(bfi__sdky):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        oird__kqvsi, yfl__kln = args
        qub__xyy = context.get_python_api(builder)
        jaty__rds = qub__xyy.string_from_string_and_size(oird__kqvsi, yfl__kln)
        riy__mtzo = qub__xyy.to_native_value(string_type, jaty__rds).value
        ilyy__ygj = cgutils.create_struct_proxy(string_type)(context,
            builder, riy__mtzo)
        ilyy__ygj.hash = ilyy__ygj.hash.type(-1)
        qub__xyy.decref(jaty__rds)
        return ilyy__ygj._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    str_arr = decode_if_dict_array(str_arr)
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type, '_str_arr_item_to_numeric: str arr expected'
    assert ind_t == types.int64, '_str_arr_item_to_numeric: integer index expected'

    def codegen(context, builder, sig, args):
        mkd__pqqkg, arr, ind, uzrn__xor = args
        bnv__oikt = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, bnv__oikt.
            offsets).data
        data = context.make_helper(builder, char_arr_type, bnv__oikt.data).data
        izni__vvx = lir.FunctionType(lir.IntType(32), [mkd__pqqkg.type, lir
            .IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        eyg__pqlb = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            eyg__pqlb = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        esks__ctzi = cgutils.get_or_insert_function(builder.module,
            izni__vvx, eyg__pqlb)
        return builder.call(esks__ctzi, [mkd__pqqkg, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    laaom__ipkb = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    izni__vvx = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(32)])
    gfzgm__xea = cgutils.get_or_insert_function(c.builder.module, izni__vvx,
        name='string_array_from_sequence')
    majqy__gkjdb = c.builder.call(gfzgm__xea, [val, laaom__ipkb])
    hcymi__hlpa = ArrayItemArrayType(char_arr_type)
    rzq__cnw = c.context.make_helper(c.builder, hcymi__hlpa)
    rzq__cnw.meminfo = majqy__gkjdb
    qqro__bmvo = c.context.make_helper(c.builder, typ)
    aikj__ohagp = rzq__cnw._getvalue()
    qqro__bmvo.data = aikj__ohagp
    opbfj__wonz = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qqro__bmvo._getvalue(), is_error=opbfj__wonz)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    bfi__sdky = len(pyval)
    korh__ghseb = 0
    vtk__rjzlw = np.empty(bfi__sdky + 1, np_offset_type)
    zstlw__dqzk = []
    vrdp__ouab = np.empty(bfi__sdky + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        vtk__rjzlw[i] = korh__ghseb
        ymgg__atwfw = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(vrdp__ouab, i, int(not
            ymgg__atwfw))
        if ymgg__atwfw:
            continue
        ybvt__poj = list(s.encode()) if isinstance(s, str) else list(s)
        zstlw__dqzk.extend(ybvt__poj)
        korh__ghseb += len(ybvt__poj)
    vtk__rjzlw[bfi__sdky] = korh__ghseb
    phph__ywjp = np.array(zstlw__dqzk, np.uint8)
    pcxvj__nap = context.get_constant(types.int64, bfi__sdky)
    anzr__ckv = context.get_constant_generic(builder, char_arr_type, phph__ywjp
        )
    wjoa__wpog = context.get_constant_generic(builder, offset_arr_type,
        vtk__rjzlw)
    cejj__vpvce = context.get_constant_generic(builder,
        null_bitmap_arr_type, vrdp__ouab)
    bnv__oikt = lir.Constant.literal_struct([pcxvj__nap, anzr__ckv,
        wjoa__wpog, cejj__vpvce])
    bnv__oikt = cgutils.global_constant(builder, '.const.payload', bnv__oikt
        ).bitcast(cgutils.voidptr_t)
    mxar__msngj = context.get_constant(types.int64, -1)
    gncqh__voq = context.get_constant_null(types.voidptr)
    fwb__blov = lir.Constant.literal_struct([mxar__msngj, gncqh__voq,
        gncqh__voq, bnv__oikt, mxar__msngj])
    fwb__blov = cgutils.global_constant(builder, '.const.meminfo', fwb__blov
        ).bitcast(cgutils.voidptr_t)
    aikj__ohagp = lir.Constant.literal_struct([fwb__blov])
    qqro__bmvo = lir.Constant.literal_struct([aikj__ohagp])
    return qqro__bmvo


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
