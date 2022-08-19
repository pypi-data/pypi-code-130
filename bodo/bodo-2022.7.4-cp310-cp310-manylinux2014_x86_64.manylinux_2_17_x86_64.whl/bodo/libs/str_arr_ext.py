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
        kef__eqxv = ArrayItemArrayType(char_arr_type)
        cloh__zoigz = [('data', kef__eqxv)]
        models.StructModel.__init__(self, dmm, fe_type, cloh__zoigz)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        xto__mycav, = args
        aaq__sngx = context.make_helper(builder, string_array_type)
        aaq__sngx.data = xto__mycav
        context.nrt.incref(builder, data_typ, xto__mycav)
        return aaq__sngx._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    ysuib__ntqj = c.context.insert_const_string(c.builder.module, 'pandas')
    xtjqq__wzmy = c.pyapi.import_module_noblock(ysuib__ntqj)
    lbuwy__aoca = c.pyapi.call_method(xtjqq__wzmy, 'StringDtype', ())
    c.pyapi.decref(xtjqq__wzmy)
    return lbuwy__aoca


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        plyno__jhws = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs,
            rhs)
        if plyno__jhws is not None:
            return plyno__jhws
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                veebv__vtp = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(veebv__vtp)
                for i in numba.parfors.parfor.internal_prange(veebv__vtp):
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
                veebv__vtp = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(veebv__vtp)
                for i in numba.parfors.parfor.internal_prange(veebv__vtp):
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
                veebv__vtp = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(veebv__vtp)
                for i in numba.parfors.parfor.internal_prange(veebv__vtp):
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
    iwksn__lvtzx = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    phh__ypguy = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and phh__ypguy or iwksn__lvtzx and is_str_arr_type(
        rhs):

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
    xbbvm__jzb = context.make_helper(builder, arr_typ, arr_value)
    kef__eqxv = ArrayItemArrayType(char_arr_type)
    ula__kygfk = _get_array_item_arr_payload(context, builder, kef__eqxv,
        xbbvm__jzb.data)
    return ula__kygfk


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return ula__kygfk.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dhcjv__ylu = context.make_helper(builder, offset_arr_type,
            ula__kygfk.offsets).data
        return _get_num_total_chars(builder, dhcjv__ylu, ula__kygfk.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ofn__vcrwg = context.make_helper(builder, offset_arr_type,
            ula__kygfk.offsets)
        mbz__euk = context.make_helper(builder, offset_ctypes_type)
        mbz__euk.data = builder.bitcast(ofn__vcrwg.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        mbz__euk.meminfo = ofn__vcrwg.meminfo
        lbuwy__aoca = mbz__euk._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            lbuwy__aoca)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xto__mycav = context.make_helper(builder, char_arr_type, ula__kygfk
            .data)
        mbz__euk = context.make_helper(builder, data_ctypes_type)
        mbz__euk.data = xto__mycav.data
        mbz__euk.meminfo = xto__mycav.meminfo
        lbuwy__aoca = mbz__euk._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            lbuwy__aoca)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        wgt__hulp, ind = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            wgt__hulp, sig.args[0])
        xto__mycav = context.make_helper(builder, char_arr_type, ula__kygfk
            .data)
        mbz__euk = context.make_helper(builder, data_ctypes_type)
        mbz__euk.data = builder.gep(xto__mycav.data, [ind])
        mbz__euk.meminfo = xto__mycav.meminfo
        lbuwy__aoca = mbz__euk._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            lbuwy__aoca)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        nvlxn__ghujy, tnx__ditt, zxq__ghj, yzce__pncfb = args
        eiwkj__mvoyx = builder.bitcast(builder.gep(nvlxn__ghujy, [tnx__ditt
            ]), lir.IntType(8).as_pointer())
        cnpq__fpw = builder.bitcast(builder.gep(zxq__ghj, [yzce__pncfb]),
            lir.IntType(8).as_pointer())
        twmeq__zqhhw = builder.load(cnpq__fpw)
        builder.store(twmeq__zqhhw, eiwkj__mvoyx)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dbvy__swc = context.make_helper(builder, null_bitmap_arr_type,
            ula__kygfk.null_bitmap)
        mbz__euk = context.make_helper(builder, data_ctypes_type)
        mbz__euk.data = dbvy__swc.data
        mbz__euk.meminfo = dbvy__swc.meminfo
        lbuwy__aoca = mbz__euk._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            lbuwy__aoca)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dhcjv__ylu = context.make_helper(builder, offset_arr_type,
            ula__kygfk.offsets).data
        return builder.load(builder.gep(dhcjv__ylu, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ula__kygfk.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        tucqe__pxsfg, ind = args
        if in_bitmap_typ == data_ctypes_type:
            mbz__euk = context.make_helper(builder, data_ctypes_type,
                tucqe__pxsfg)
            tucqe__pxsfg = mbz__euk.data
        return builder.load(builder.gep(tucqe__pxsfg, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        tucqe__pxsfg, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            mbz__euk = context.make_helper(builder, data_ctypes_type,
                tucqe__pxsfg)
            tucqe__pxsfg = mbz__euk.data
        builder.store(val, builder.gep(tucqe__pxsfg, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        aflqt__pwojh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        swsut__elbbc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        rhd__didg = context.make_helper(builder, offset_arr_type,
            aflqt__pwojh.offsets).data
        dux__ydiyx = context.make_helper(builder, offset_arr_type,
            swsut__elbbc.offsets).data
        asmwo__aml = context.make_helper(builder, char_arr_type,
            aflqt__pwojh.data).data
        kmcjd__zvbcj = context.make_helper(builder, char_arr_type,
            swsut__elbbc.data).data
        boket__gxma = context.make_helper(builder, null_bitmap_arr_type,
            aflqt__pwojh.null_bitmap).data
        oogld__sxdgn = context.make_helper(builder, null_bitmap_arr_type,
            swsut__elbbc.null_bitmap).data
        hshb__uzyw = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, dux__ydiyx, rhd__didg, hshb__uzyw)
        cgutils.memcpy(builder, kmcjd__zvbcj, asmwo__aml, builder.load(
            builder.gep(rhd__didg, [ind])))
        ibi__ngmcg = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        mxxu__rlw = builder.lshr(ibi__ngmcg, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, oogld__sxdgn, boket__gxma, mxxu__rlw)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        aflqt__pwojh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        swsut__elbbc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        rhd__didg = context.make_helper(builder, offset_arr_type,
            aflqt__pwojh.offsets).data
        asmwo__aml = context.make_helper(builder, char_arr_type,
            aflqt__pwojh.data).data
        kmcjd__zvbcj = context.make_helper(builder, char_arr_type,
            swsut__elbbc.data).data
        num_total_chars = _get_num_total_chars(builder, rhd__didg,
            aflqt__pwojh.n_arrays)
        cgutils.memcpy(builder, kmcjd__zvbcj, asmwo__aml, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        aflqt__pwojh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        swsut__elbbc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        rhd__didg = context.make_helper(builder, offset_arr_type,
            aflqt__pwojh.offsets).data
        dux__ydiyx = context.make_helper(builder, offset_arr_type,
            swsut__elbbc.offsets).data
        boket__gxma = context.make_helper(builder, null_bitmap_arr_type,
            aflqt__pwojh.null_bitmap).data
        veebv__vtp = aflqt__pwojh.n_arrays
        bakyt__crjvk = context.get_constant(offset_type, 0)
        zkz__kuf = cgutils.alloca_once_value(builder, bakyt__crjvk)
        with cgutils.for_range(builder, veebv__vtp) as bdkz__uxbt:
            mys__vbw = lower_is_na(context, builder, boket__gxma,
                bdkz__uxbt.index)
            with cgutils.if_likely(builder, builder.not_(mys__vbw)):
                pkta__xfcnj = builder.load(builder.gep(rhd__didg, [
                    bdkz__uxbt.index]))
                jrwif__werfy = builder.load(zkz__kuf)
                builder.store(pkta__xfcnj, builder.gep(dux__ydiyx, [
                    jrwif__werfy]))
                builder.store(builder.add(jrwif__werfy, lir.Constant(
                    context.get_value_type(offset_type), 1)), zkz__kuf)
        jrwif__werfy = builder.load(zkz__kuf)
        pkta__xfcnj = builder.load(builder.gep(rhd__didg, [veebv__vtp]))
        builder.store(pkta__xfcnj, builder.gep(dux__ydiyx, [jrwif__werfy]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        jnqa__oysrh, ind, str, uji__smgn = args
        jnqa__oysrh = context.make_array(sig.args[0])(context, builder,
            jnqa__oysrh)
        atj__kcy = builder.gep(jnqa__oysrh.data, [ind])
        cgutils.raw_memcpy(builder, atj__kcy, str, uji__smgn, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        atj__kcy, ind, zjv__oxcd, uji__smgn = args
        atj__kcy = builder.gep(atj__kcy, [ind])
        cgutils.raw_memcpy(builder, atj__kcy, zjv__oxcd, uji__smgn, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            dphdg__yxcey = A._data
            return np.int64(getitem_str_offset(dphdg__yxcey, idx + 1) -
                getitem_str_offset(dphdg__yxcey, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    unn__oir = np.int64(getitem_str_offset(A, i))
    rkyib__ggokg = np.int64(getitem_str_offset(A, i + 1))
    l = rkyib__ggokg - unn__oir
    unb__pegd = get_data_ptr_ind(A, unn__oir)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(unb__pegd, j) >= 128:
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
        trrrs__gavfy = 'in_str_arr = A._data'
        oyhp__lctlp = 'input_index = A._indices[i]'
    else:
        trrrs__gavfy = 'in_str_arr = A'
        oyhp__lctlp = 'input_index = i'
    lvktd__ixn = f"""def impl(B, j, A, i):
        if j == 0:
            setitem_str_offset(B, 0, 0)

        {trrrs__gavfy}
        {oyhp__lctlp}

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
    iked__wrv = {}
    exec(lvktd__ixn, {'setitem_str_offset': setitem_str_offset,
        'memcpy_region': memcpy_region, 'getitem_str_offset':
        getitem_str_offset, 'str_arr_set_na': str_arr_set_na,
        'str_arr_set_not_na': str_arr_set_not_na, 'get_data_ptr':
        get_data_ptr, 'bodo': bodo, 'np': np}, iked__wrv)
    impl = iked__wrv['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    veebv__vtp = len(str_arr)
    adssc__okrz = np.empty(veebv__vtp, np.bool_)
    for i in range(veebv__vtp):
        adssc__okrz[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return adssc__okrz


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            veebv__vtp = len(data)
            l = []
            for i in range(veebv__vtp):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        ntlfj__lpm = data.count
        huv__pqtt = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(ntlfj__lpm)]
        if is_overload_true(str_null_bools):
            huv__pqtt += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(ntlfj__lpm) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        lvktd__ixn = 'def f(data, str_null_bools=None):\n'
        lvktd__ixn += '  return ({}{})\n'.format(', '.join(huv__pqtt), ',' if
            ntlfj__lpm == 1 else '')
        iked__wrv = {}
        exec(lvktd__ixn, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, iked__wrv)
        iapg__iapn = iked__wrv['f']
        return iapg__iapn
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                veebv__vtp = len(list_data)
                for i in range(veebv__vtp):
                    zjv__oxcd = list_data[i]
                    str_arr[i] = zjv__oxcd
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                veebv__vtp = len(list_data)
                for i in range(veebv__vtp):
                    zjv__oxcd = list_data[i]
                    str_arr[i] = zjv__oxcd
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        ntlfj__lpm = str_arr.count
        ycg__rrsn = 0
        lvktd__ixn = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(ntlfj__lpm):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                lvktd__ixn += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, ntlfj__lpm + ycg__rrsn))
                ycg__rrsn += 1
            else:
                lvktd__ixn += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        lvktd__ixn += '  return\n'
        iked__wrv = {}
        exec(lvktd__ixn, {'cp_str_list_to_array': cp_str_list_to_array},
            iked__wrv)
        ebl__foe = iked__wrv['f']
        return ebl__foe
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            veebv__vtp = len(str_list)
            str_arr = pre_alloc_string_array(veebv__vtp, -1)
            for i in range(veebv__vtp):
                zjv__oxcd = str_list[i]
                str_arr[i] = zjv__oxcd
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            veebv__vtp = len(A)
            rozt__pxycz = 0
            for i in range(veebv__vtp):
                zjv__oxcd = A[i]
                rozt__pxycz += get_utf8_size(zjv__oxcd)
            return rozt__pxycz
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        veebv__vtp = len(arr)
        n_chars = num_total_chars(arr)
        hqhen__qtmyd = pre_alloc_string_array(veebv__vtp, np.int64(n_chars))
        copy_str_arr_slice(hqhen__qtmyd, arr, veebv__vtp)
        return hqhen__qtmyd
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
    lvktd__ixn = 'def f(in_seq):\n'
    lvktd__ixn += '    n_strs = len(in_seq)\n'
    lvktd__ixn += '    A = pre_alloc_string_array(n_strs, -1)\n'
    lvktd__ixn += '    return A\n'
    iked__wrv = {}
    exec(lvktd__ixn, {'pre_alloc_string_array': pre_alloc_string_array},
        iked__wrv)
    nbp__ekmi = iked__wrv['f']
    return nbp__ekmi


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        kath__tnqlc = 'pre_alloc_binary_array'
    else:
        kath__tnqlc = 'pre_alloc_string_array'
    lvktd__ixn = 'def f(in_seq):\n'
    lvktd__ixn += '    n_strs = len(in_seq)\n'
    lvktd__ixn += f'    A = {kath__tnqlc}(n_strs, -1)\n'
    lvktd__ixn += '    for i in range(n_strs):\n'
    lvktd__ixn += '        A[i] = in_seq[i]\n'
    lvktd__ixn += '    return A\n'
    iked__wrv = {}
    exec(lvktd__ixn, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, iked__wrv)
    nbp__ekmi = iked__wrv['f']
    return nbp__ekmi


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        aya__vuhu = builder.add(ula__kygfk.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        aps__gmb = builder.lshr(lir.Constant(lir.IntType(64), offset_type.
            bitwidth), lir.Constant(lir.IntType(64), 3))
        mxxu__rlw = builder.mul(aya__vuhu, aps__gmb)
        dwxn__wofev = context.make_array(offset_arr_type)(context, builder,
            ula__kygfk.offsets).data
        cgutils.memset(builder, dwxn__wofev, mxxu__rlw, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        rba__nii = ula__kygfk.n_arrays
        mxxu__rlw = builder.lshr(builder.add(rba__nii, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        gijdt__dbzs = context.make_array(null_bitmap_arr_type)(context,
            builder, ula__kygfk.null_bitmap).data
        cgutils.memset(builder, gijdt__dbzs, mxxu__rlw, 0)
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
    rjhg__axcy = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        nqua__aua = len(len_arr)
        for i in range(nqua__aua):
            offsets[i] = rjhg__axcy
            rjhg__axcy += len_arr[i]
        offsets[nqua__aua] = rjhg__axcy
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    eioyp__hda = i // 8
    wewmb__cvlde = getitem_str_bitmap(bits, eioyp__hda)
    wewmb__cvlde ^= np.uint8(-np.uint8(bit_is_set) ^ wewmb__cvlde) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, eioyp__hda, wewmb__cvlde)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    jnh__zyilu = get_null_bitmap_ptr(out_str_arr)
    nrh__btwx = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        wzd__kydyt = get_bit_bitmap(nrh__btwx, j)
        set_bit_to(jnh__zyilu, out_start + j, wzd__kydyt)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, wgt__hulp, frc__rbllg, kyv__xkki = args
        aflqt__pwojh = _get_str_binary_arr_payload(context, builder,
            wgt__hulp, string_array_type)
        swsut__elbbc = _get_str_binary_arr_payload(context, builder,
            out_arr, string_array_type)
        rhd__didg = context.make_helper(builder, offset_arr_type,
            aflqt__pwojh.offsets).data
        dux__ydiyx = context.make_helper(builder, offset_arr_type,
            swsut__elbbc.offsets).data
        asmwo__aml = context.make_helper(builder, char_arr_type,
            aflqt__pwojh.data).data
        kmcjd__zvbcj = context.make_helper(builder, char_arr_type,
            swsut__elbbc.data).data
        num_total_chars = _get_num_total_chars(builder, rhd__didg,
            aflqt__pwojh.n_arrays)
        paq__vwvo = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        yxlyt__ust = cgutils.get_or_insert_function(builder.module,
            paq__vwvo, name='set_string_array_range')
        builder.call(yxlyt__ust, [dux__ydiyx, kmcjd__zvbcj, rhd__didg,
            asmwo__aml, frc__rbllg, kyv__xkki, aflqt__pwojh.n_arrays,
            num_total_chars])
        kwsov__izrn = context.typing_context.resolve_value_type(
            copy_nulls_range)
        uzfz__yrg = kwsov__izrn.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        eae__yli = context.get_function(kwsov__izrn, uzfz__yrg)
        eae__yli(builder, (out_arr, wgt__hulp, frc__rbllg))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    tlfo__irjk = c.context.make_helper(c.builder, typ, val)
    kef__eqxv = ArrayItemArrayType(char_arr_type)
    ula__kygfk = _get_array_item_arr_payload(c.context, c.builder,
        kef__eqxv, tlfo__irjk.data)
    yfl__lwy = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    aqe__ydw = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        aqe__ydw = 'pd_array_from_string_array'
    paq__vwvo = lir.FunctionType(c.context.get_argument_type(types.pyobject
        ), [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    hnyqi__beii = cgutils.get_or_insert_function(c.builder.module,
        paq__vwvo, name=aqe__ydw)
    dhcjv__ylu = c.context.make_array(offset_arr_type)(c.context, c.builder,
        ula__kygfk.offsets).data
    unb__pegd = c.context.make_array(char_arr_type)(c.context, c.builder,
        ula__kygfk.data).data
    gijdt__dbzs = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, ula__kygfk.null_bitmap).data
    arr = c.builder.call(hnyqi__beii, [ula__kygfk.n_arrays, dhcjv__ylu,
        unb__pegd, gijdt__dbzs, yfl__lwy])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gijdt__dbzs = context.make_array(null_bitmap_arr_type)(context,
            builder, ula__kygfk.null_bitmap).data
        gjhwr__vejnt = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        htin__alc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        wewmb__cvlde = builder.load(builder.gep(gijdt__dbzs, [gjhwr__vejnt],
            inbounds=True))
        lvzk__cxtm = lir.ArrayType(lir.IntType(8), 8)
        clj__zuyp = cgutils.alloca_once_value(builder, lir.Constant(
            lvzk__cxtm, (1, 2, 4, 8, 16, 32, 64, 128)))
        vqooz__ehcou = builder.load(builder.gep(clj__zuyp, [lir.Constant(
            lir.IntType(64), 0), htin__alc], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(wewmb__cvlde,
            vqooz__ehcou), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gjhwr__vejnt = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        htin__alc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        gijdt__dbzs = context.make_array(null_bitmap_arr_type)(context,
            builder, ula__kygfk.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, ula__kygfk.
            offsets).data
        mmc__uzytw = builder.gep(gijdt__dbzs, [gjhwr__vejnt], inbounds=True)
        wewmb__cvlde = builder.load(mmc__uzytw)
        lvzk__cxtm = lir.ArrayType(lir.IntType(8), 8)
        clj__zuyp = cgutils.alloca_once_value(builder, lir.Constant(
            lvzk__cxtm, (1, 2, 4, 8, 16, 32, 64, 128)))
        vqooz__ehcou = builder.load(builder.gep(clj__zuyp, [lir.Constant(
            lir.IntType(64), 0), htin__alc], inbounds=True))
        vqooz__ehcou = builder.xor(vqooz__ehcou, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(wewmb__cvlde, vqooz__ehcou), mmc__uzytw)
        if str_arr_typ == string_array_type:
            ateco__gmv = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            axj__ikhe = builder.icmp_unsigned('!=', ateco__gmv, ula__kygfk.
                n_arrays)
            with builder.if_then(axj__ikhe):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [ateco__gmv]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gjhwr__vejnt = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        htin__alc = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        gijdt__dbzs = context.make_array(null_bitmap_arr_type)(context,
            builder, ula__kygfk.null_bitmap).data
        mmc__uzytw = builder.gep(gijdt__dbzs, [gjhwr__vejnt], inbounds=True)
        wewmb__cvlde = builder.load(mmc__uzytw)
        lvzk__cxtm = lir.ArrayType(lir.IntType(8), 8)
        clj__zuyp = cgutils.alloca_once_value(builder, lir.Constant(
            lvzk__cxtm, (1, 2, 4, 8, 16, 32, 64, 128)))
        vqooz__ehcou = builder.load(builder.gep(clj__zuyp, [lir.Constant(
            lir.IntType(64), 0), htin__alc], inbounds=True))
        builder.store(builder.or_(wewmb__cvlde, vqooz__ehcou), mmc__uzytw)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        mxxu__rlw = builder.udiv(builder.add(ula__kygfk.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        gijdt__dbzs = context.make_array(null_bitmap_arr_type)(context,
            builder, ula__kygfk.null_bitmap).data
        cgutils.memset(builder, gijdt__dbzs, mxxu__rlw, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    yeuup__jjfg = context.make_helper(builder, string_array_type, str_arr)
    kef__eqxv = ArrayItemArrayType(char_arr_type)
    cml__vhwyt = context.make_helper(builder, kef__eqxv, yeuup__jjfg.data)
    ggaax__ukwo = ArrayItemArrayPayloadType(kef__eqxv)
    vau__mca = context.nrt.meminfo_data(builder, cml__vhwyt.meminfo)
    ouulo__hhul = builder.bitcast(vau__mca, context.get_value_type(
        ggaax__ukwo).as_pointer())
    return ouulo__hhul


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        jqg__jylxa, uzm__uczky = args
        snrd__agtzr = _get_str_binary_arr_data_payload_ptr(context, builder,
            uzm__uczky)
        ngtsp__vvok = _get_str_binary_arr_data_payload_ptr(context, builder,
            jqg__jylxa)
        gbq__ebgl = _get_str_binary_arr_payload(context, builder,
            uzm__uczky, sig.args[1])
        qxnvp__bzq = _get_str_binary_arr_payload(context, builder,
            jqg__jylxa, sig.args[0])
        context.nrt.incref(builder, char_arr_type, gbq__ebgl.data)
        context.nrt.incref(builder, offset_arr_type, gbq__ebgl.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, gbq__ebgl.null_bitmap
            )
        context.nrt.decref(builder, char_arr_type, qxnvp__bzq.data)
        context.nrt.decref(builder, offset_arr_type, qxnvp__bzq.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, qxnvp__bzq.
            null_bitmap)
        builder.store(builder.load(snrd__agtzr), ngtsp__vvok)
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
        veebv__vtp = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return veebv__vtp
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, atj__kcy, bvhre__jfhp = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder, arr, sig
            .args[0])
        offsets = context.make_helper(builder, offset_arr_type, ula__kygfk.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ula__kygfk.data
            ).data
        paq__vwvo = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        unidh__qea = cgutils.get_or_insert_function(builder.module,
            paq__vwvo, name='setitem_string_array')
        rnnmh__vsem = context.get_constant(types.int32, -1)
        ryed__wpsae = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, ula__kygfk
            .n_arrays)
        builder.call(unidh__qea, [offsets, data, num_total_chars, builder.
            extract_value(atj__kcy, 0), bvhre__jfhp, rnnmh__vsem,
            ryed__wpsae, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    paq__vwvo = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64)])
    vwrwt__nogv = cgutils.get_or_insert_function(builder.module, paq__vwvo,
        name='is_na')
    return builder.call(vwrwt__nogv, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        eiwkj__mvoyx, cnpq__fpw, ntlfj__lpm, xrvpb__rmu = args
        cgutils.raw_memcpy(builder, eiwkj__mvoyx, cnpq__fpw, ntlfj__lpm,
            xrvpb__rmu)
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
        fbhlr__pqdps, pgkg__xil = unicode_to_utf8_and_len(val)
        euxvl__fhk = getitem_str_offset(A, ind)
        fkau__vxpsv = getitem_str_offset(A, ind + 1)
        mviq__rgph = fkau__vxpsv - euxvl__fhk
        if mviq__rgph != pgkg__xil:
            return False
        atj__kcy = get_data_ptr_ind(A, euxvl__fhk)
        return memcmp(atj__kcy, fbhlr__pqdps, pgkg__xil) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        euxvl__fhk = getitem_str_offset(A, ind)
        mviq__rgph = bodo.libs.str_ext.int_to_str_len(val)
        jpe__rbse = euxvl__fhk + mviq__rgph
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            euxvl__fhk, jpe__rbse)
        atj__kcy = get_data_ptr_ind(A, euxvl__fhk)
        inplace_int64_to_str(atj__kcy, mviq__rgph, val)
        setitem_str_offset(A, ind + 1, euxvl__fhk + mviq__rgph)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        atj__kcy, = args
        gtc__lxo = context.insert_const_string(builder.module, '<NA>')
        dikcu__uyp = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, atj__kcy, gtc__lxo, dikcu__uyp, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    smlpc__wmpib = len('<NA>')

    def impl(A, ind):
        euxvl__fhk = getitem_str_offset(A, ind)
        jpe__rbse = euxvl__fhk + smlpc__wmpib
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            euxvl__fhk, jpe__rbse)
        atj__kcy = get_data_ptr_ind(A, euxvl__fhk)
        inplace_set_NA_str(atj__kcy)
        setitem_str_offset(A, ind + 1, euxvl__fhk + smlpc__wmpib)
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
            euxvl__fhk = getitem_str_offset(A, ind)
            fkau__vxpsv = getitem_str_offset(A, ind + 1)
            bvhre__jfhp = fkau__vxpsv - euxvl__fhk
            atj__kcy = get_data_ptr_ind(A, euxvl__fhk)
            rgrf__vtp = decode_utf8(atj__kcy, bvhre__jfhp)
            return rgrf__vtp
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            veebv__vtp = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(veebv__vtp):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            ydod__czi = get_data_ptr(out_arr).data
            xpxc__roiu = get_data_ptr(A).data
            ycg__rrsn = 0
            jrwif__werfy = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(veebv__vtp):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    yspy__mval = get_str_arr_item_length(A, i)
                    if yspy__mval == 1:
                        copy_single_char(ydod__czi, jrwif__werfy,
                            xpxc__roiu, getitem_str_offset(A, i))
                    else:
                        memcpy_region(ydod__czi, jrwif__werfy, xpxc__roiu,
                            getitem_str_offset(A, i), yspy__mval, 1)
                    jrwif__werfy += yspy__mval
                    setitem_str_offset(out_arr, ycg__rrsn + 1, jrwif__werfy)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, ycg__rrsn)
                    else:
                        str_arr_set_not_na(out_arr, ycg__rrsn)
                    ycg__rrsn += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            veebv__vtp = len(ind)
            out_arr = pre_alloc_string_array(veebv__vtp, -1)
            ycg__rrsn = 0
            for i in range(veebv__vtp):
                zjv__oxcd = A[ind[i]]
                out_arr[ycg__rrsn] = zjv__oxcd
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, ycg__rrsn)
                ycg__rrsn += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            veebv__vtp = len(A)
            xlbj__ivect = numba.cpython.unicode._normalize_slice(ind,
                veebv__vtp)
            hpyp__pvu = numba.cpython.unicode._slice_span(xlbj__ivect)
            if xlbj__ivect.step == 1:
                euxvl__fhk = getitem_str_offset(A, xlbj__ivect.start)
                fkau__vxpsv = getitem_str_offset(A, xlbj__ivect.stop)
                n_chars = fkau__vxpsv - euxvl__fhk
                hqhen__qtmyd = pre_alloc_string_array(hpyp__pvu, np.int64(
                    n_chars))
                for i in range(hpyp__pvu):
                    hqhen__qtmyd[i] = A[xlbj__ivect.start + i]
                    if str_arr_is_na(A, xlbj__ivect.start + i):
                        str_arr_set_na(hqhen__qtmyd, i)
                return hqhen__qtmyd
            else:
                hqhen__qtmyd = pre_alloc_string_array(hpyp__pvu, -1)
                for i in range(hpyp__pvu):
                    hqhen__qtmyd[i] = A[xlbj__ivect.start + i * xlbj__ivect
                        .step]
                    if str_arr_is_na(A, xlbj__ivect.start + i * xlbj__ivect
                        .step):
                        str_arr_set_na(hqhen__qtmyd, i)
                return hqhen__qtmyd
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
    hcvg__hue = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(hcvg__hue)
        pvyb__kxml = 4

        def impl_scalar(A, idx, val):
            ylft__kum = (val._length if val._is_ascii else pvyb__kxml * val
                ._length)
            xto__mycav = A._data
            euxvl__fhk = np.int64(getitem_str_offset(A, idx))
            jpe__rbse = euxvl__fhk + ylft__kum
            bodo.libs.array_item_arr_ext.ensure_data_capacity(xto__mycav,
                euxvl__fhk, jpe__rbse)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                jpe__rbse, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                xlbj__ivect = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                unn__oir = xlbj__ivect.start
                xto__mycav = A._data
                euxvl__fhk = np.int64(getitem_str_offset(A, unn__oir))
                jpe__rbse = euxvl__fhk + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(xto__mycav,
                    euxvl__fhk, jpe__rbse)
                set_string_array_range(A, val, unn__oir, euxvl__fhk)
                cyqd__joxnd = 0
                for i in range(xlbj__ivect.start, xlbj__ivect.stop,
                    xlbj__ivect.step):
                    if str_arr_is_na(val, cyqd__joxnd):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    cyqd__joxnd += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                zxzvd__ekjlu = str_list_to_array(val)
                A[idx] = zxzvd__ekjlu
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                xlbj__ivect = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(xlbj__ivect.start, xlbj__ivect.stop,
                    xlbj__ivect.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(hcvg__hue)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                veebv__vtp = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(veebv__vtp, -1)
                for i in numba.parfors.parfor.internal_prange(veebv__vtp):
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
                veebv__vtp = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(veebv__vtp, -1)
                lsg__jfgpx = 0
                for i in numba.parfors.parfor.internal_prange(veebv__vtp):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, lsg__jfgpx):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, lsg__jfgpx)
                        else:
                            out_arr[i] = str(val[lsg__jfgpx])
                        lsg__jfgpx += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(hcvg__hue)
    raise BodoError(hcvg__hue)


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
    eozh__selym = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(eozh__selym, (types.Float, types.Integer)
        ) and eozh__selym not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(eozh__selym, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            veebv__vtp = len(A)
            B = np.empty(veebv__vtp, eozh__selym)
            for i in numba.parfors.parfor.internal_prange(veebv__vtp):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif eozh__selym == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            veebv__vtp = len(A)
            B = np.empty(veebv__vtp, eozh__selym)
            for i in numba.parfors.parfor.internal_prange(veebv__vtp):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif eozh__selym == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            veebv__vtp = len(A)
            B = np.empty(veebv__vtp, eozh__selym)
            for i in numba.parfors.parfor.internal_prange(veebv__vtp):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            veebv__vtp = len(A)
            B = np.empty(veebv__vtp, eozh__selym)
            for i in numba.parfors.parfor.internal_prange(veebv__vtp):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        atj__kcy, bvhre__jfhp = args
        uxznn__czwg = context.get_python_api(builder)
        dovc__jwxgw = uxznn__czwg.string_from_string_and_size(atj__kcy,
            bvhre__jfhp)
        mxt__xyj = uxznn__czwg.to_native_value(string_type, dovc__jwxgw).value
        tizop__xsju = cgutils.create_struct_proxy(string_type)(context,
            builder, mxt__xyj)
        tizop__xsju.hash = tizop__xsju.hash.type(-1)
        uxznn__czwg.decref(dovc__jwxgw)
        return tizop__xsju._getvalue()
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
        kswv__ecx, arr, ind, cez__xxxtr = args
        ula__kygfk = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ula__kygfk.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ula__kygfk.data
            ).data
        paq__vwvo = lir.FunctionType(lir.IntType(32), [kswv__ecx.type, lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        vcu__qpdnc = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            vcu__qpdnc = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        zzah__dec = cgutils.get_or_insert_function(builder.module,
            paq__vwvo, vcu__qpdnc)
        return builder.call(zzah__dec, [kswv__ecx, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    yfl__lwy = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    paq__vwvo = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(32)])
    vbhy__cvn = cgutils.get_or_insert_function(c.builder.module, paq__vwvo,
        name='string_array_from_sequence')
    pinj__alf = c.builder.call(vbhy__cvn, [val, yfl__lwy])
    kef__eqxv = ArrayItemArrayType(char_arr_type)
    cml__vhwyt = c.context.make_helper(c.builder, kef__eqxv)
    cml__vhwyt.meminfo = pinj__alf
    yeuup__jjfg = c.context.make_helper(c.builder, typ)
    xto__mycav = cml__vhwyt._getvalue()
    yeuup__jjfg.data = xto__mycav
    bwptw__ufss = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(yeuup__jjfg._getvalue(), is_error=bwptw__ufss)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    veebv__vtp = len(pyval)
    jrwif__werfy = 0
    qesi__wxqqj = np.empty(veebv__vtp + 1, np_offset_type)
    ekrze__ulmx = []
    mpu__maldz = np.empty(veebv__vtp + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        qesi__wxqqj[i] = jrwif__werfy
        jlb__ssty = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(mpu__maldz, i, int(not jlb__ssty))
        if jlb__ssty:
            continue
        qsejj__wie = list(s.encode()) if isinstance(s, str) else list(s)
        ekrze__ulmx.extend(qsejj__wie)
        jrwif__werfy += len(qsejj__wie)
    qesi__wxqqj[veebv__vtp] = jrwif__werfy
    porer__tty = np.array(ekrze__ulmx, np.uint8)
    epo__qnfu = context.get_constant(types.int64, veebv__vtp)
    jdzo__rui = context.get_constant_generic(builder, char_arr_type, porer__tty
        )
    iznic__ejxxp = context.get_constant_generic(builder, offset_arr_type,
        qesi__wxqqj)
    gnqu__xak = context.get_constant_generic(builder, null_bitmap_arr_type,
        mpu__maldz)
    ula__kygfk = lir.Constant.literal_struct([epo__qnfu, jdzo__rui,
        iznic__ejxxp, gnqu__xak])
    ula__kygfk = cgutils.global_constant(builder, '.const.payload', ula__kygfk
        ).bitcast(cgutils.voidptr_t)
    tfkr__tesri = context.get_constant(types.int64, -1)
    vcl__wjhb = context.get_constant_null(types.voidptr)
    amz__ouwb = lir.Constant.literal_struct([tfkr__tesri, vcl__wjhb,
        vcl__wjhb, ula__kygfk, tfkr__tesri])
    amz__ouwb = cgutils.global_constant(builder, '.const.meminfo', amz__ouwb
        ).bitcast(cgutils.voidptr_t)
    xto__mycav = lir.Constant.literal_struct([amz__ouwb])
    yeuup__jjfg = lir.Constant.literal_struct([xto__mycav])
    return yeuup__jjfg


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
