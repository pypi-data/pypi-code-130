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
        fkfs__epw = ArrayItemArrayType(char_arr_type)
        idc__mxv = [('data', fkfs__epw)]
        models.StructModel.__init__(self, dmm, fe_type, idc__mxv)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        spopa__bwj, = args
        dmggn__quup = context.make_helper(builder, string_array_type)
        dmggn__quup.data = spopa__bwj
        context.nrt.incref(builder, data_typ, spopa__bwj)
        return dmggn__quup._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    saygh__eumk = c.context.insert_const_string(c.builder.module, 'pandas')
    jyfl__qdgaa = c.pyapi.import_module_noblock(saygh__eumk)
    xibak__rtg = c.pyapi.call_method(jyfl__qdgaa, 'StringDtype', ())
    c.pyapi.decref(jyfl__qdgaa)
    return xibak__rtg


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        ktmh__gir = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs)
        if ktmh__gir is not None:
            return ktmh__gir
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                knrm__kqwn = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(knrm__kqwn)
                for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
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
                knrm__kqwn = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(knrm__kqwn)
                for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
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
                knrm__kqwn = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(knrm__kqwn)
                for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
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
    krkuk__slsd = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    bmpp__yys = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and bmpp__yys or krkuk__slsd and is_str_arr_type(
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
    tic__zycw = context.make_helper(builder, arr_typ, arr_value)
    fkfs__epw = ArrayItemArrayType(char_arr_type)
    kct__azdf = _get_array_item_arr_payload(context, builder, fkfs__epw,
        tic__zycw.data)
    return kct__azdf


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return kct__azdf.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        zfvvw__mbdxx = context.make_helper(builder, offset_arr_type,
            kct__azdf.offsets).data
        return _get_num_total_chars(builder, zfvvw__mbdxx, kct__azdf.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        vxui__kocl = context.make_helper(builder, offset_arr_type,
            kct__azdf.offsets)
        ywbz__ksid = context.make_helper(builder, offset_ctypes_type)
        ywbz__ksid.data = builder.bitcast(vxui__kocl.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        ywbz__ksid.meminfo = vxui__kocl.meminfo
        xibak__rtg = ywbz__ksid._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            xibak__rtg)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        spopa__bwj = context.make_helper(builder, char_arr_type, kct__azdf.data
            )
        ywbz__ksid = context.make_helper(builder, data_ctypes_type)
        ywbz__ksid.data = spopa__bwj.data
        ywbz__ksid.meminfo = spopa__bwj.meminfo
        xibak__rtg = ywbz__ksid._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, xibak__rtg
            )
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        wufgj__gpbkd, ind = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            wufgj__gpbkd, sig.args[0])
        spopa__bwj = context.make_helper(builder, char_arr_type, kct__azdf.data
            )
        ywbz__ksid = context.make_helper(builder, data_ctypes_type)
        ywbz__ksid.data = builder.gep(spopa__bwj.data, [ind])
        ywbz__ksid.meminfo = spopa__bwj.meminfo
        xibak__rtg = ywbz__ksid._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, xibak__rtg
            )
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        jcopr__fks, kdrb__cker, nvu__bpmwv, vmf__dltak = args
        zfad__zjk = builder.bitcast(builder.gep(jcopr__fks, [kdrb__cker]),
            lir.IntType(8).as_pointer())
        beq__woq = builder.bitcast(builder.gep(nvu__bpmwv, [vmf__dltak]),
            lir.IntType(8).as_pointer())
        jowka__ztl = builder.load(beq__woq)
        builder.store(jowka__ztl, zfad__zjk)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        mmfzn__elg = context.make_helper(builder, null_bitmap_arr_type,
            kct__azdf.null_bitmap)
        ywbz__ksid = context.make_helper(builder, data_ctypes_type)
        ywbz__ksid.data = mmfzn__elg.data
        ywbz__ksid.meminfo = mmfzn__elg.meminfo
        xibak__rtg = ywbz__ksid._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, xibak__rtg
            )
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        zfvvw__mbdxx = context.make_helper(builder, offset_arr_type,
            kct__azdf.offsets).data
        return builder.load(builder.gep(zfvvw__mbdxx, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, kct__azdf.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        mhdi__fgd, ind = args
        if in_bitmap_typ == data_ctypes_type:
            ywbz__ksid = context.make_helper(builder, data_ctypes_type,
                mhdi__fgd)
            mhdi__fgd = ywbz__ksid.data
        return builder.load(builder.gep(mhdi__fgd, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        mhdi__fgd, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            ywbz__ksid = context.make_helper(builder, data_ctypes_type,
                mhdi__fgd)
            mhdi__fgd = ywbz__ksid.data
        builder.store(val, builder.gep(mhdi__fgd, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        lwlf__vutk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bxf__xtuvq = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ollpd__wiec = context.make_helper(builder, offset_arr_type,
            lwlf__vutk.offsets).data
        paka__kwul = context.make_helper(builder, offset_arr_type,
            bxf__xtuvq.offsets).data
        ddurl__tko = context.make_helper(builder, char_arr_type, lwlf__vutk
            .data).data
        wbh__iaxrd = context.make_helper(builder, char_arr_type, bxf__xtuvq
            .data).data
        oacns__kld = context.make_helper(builder, null_bitmap_arr_type,
            lwlf__vutk.null_bitmap).data
        phlzb__utwl = context.make_helper(builder, null_bitmap_arr_type,
            bxf__xtuvq.null_bitmap).data
        aqdgz__ymi = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, paka__kwul, ollpd__wiec, aqdgz__ymi)
        cgutils.memcpy(builder, wbh__iaxrd, ddurl__tko, builder.load(
            builder.gep(ollpd__wiec, [ind])))
        wjn__zna = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        ftjo__rtna = builder.lshr(wjn__zna, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, phlzb__utwl, oacns__kld, ftjo__rtna)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        lwlf__vutk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bxf__xtuvq = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ollpd__wiec = context.make_helper(builder, offset_arr_type,
            lwlf__vutk.offsets).data
        ddurl__tko = context.make_helper(builder, char_arr_type, lwlf__vutk
            .data).data
        wbh__iaxrd = context.make_helper(builder, char_arr_type, bxf__xtuvq
            .data).data
        num_total_chars = _get_num_total_chars(builder, ollpd__wiec,
            lwlf__vutk.n_arrays)
        cgutils.memcpy(builder, wbh__iaxrd, ddurl__tko, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        lwlf__vutk = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bxf__xtuvq = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ollpd__wiec = context.make_helper(builder, offset_arr_type,
            lwlf__vutk.offsets).data
        paka__kwul = context.make_helper(builder, offset_arr_type,
            bxf__xtuvq.offsets).data
        oacns__kld = context.make_helper(builder, null_bitmap_arr_type,
            lwlf__vutk.null_bitmap).data
        knrm__kqwn = lwlf__vutk.n_arrays
        fny__apxf = context.get_constant(offset_type, 0)
        cnlih__qhua = cgutils.alloca_once_value(builder, fny__apxf)
        with cgutils.for_range(builder, knrm__kqwn) as rkc__kogu:
            zpr__rmyb = lower_is_na(context, builder, oacns__kld, rkc__kogu
                .index)
            with cgutils.if_likely(builder, builder.not_(zpr__rmyb)):
                hix__scpr = builder.load(builder.gep(ollpd__wiec, [
                    rkc__kogu.index]))
                exob__fqro = builder.load(cnlih__qhua)
                builder.store(hix__scpr, builder.gep(paka__kwul, [exob__fqro]))
                builder.store(builder.add(exob__fqro, lir.Constant(context.
                    get_value_type(offset_type), 1)), cnlih__qhua)
        exob__fqro = builder.load(cnlih__qhua)
        hix__scpr = builder.load(builder.gep(ollpd__wiec, [knrm__kqwn]))
        builder.store(hix__scpr, builder.gep(paka__kwul, [exob__fqro]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        rjl__susns, ind, str, lgaop__wtji = args
        rjl__susns = context.make_array(sig.args[0])(context, builder,
            rjl__susns)
        pfm__ktsii = builder.gep(rjl__susns.data, [ind])
        cgutils.raw_memcpy(builder, pfm__ktsii, str, lgaop__wtji, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        pfm__ktsii, ind, cyb__lakf, lgaop__wtji = args
        pfm__ktsii = builder.gep(pfm__ktsii, [ind])
        cgutils.raw_memcpy(builder, pfm__ktsii, cyb__lakf, lgaop__wtji, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            hkb__dfbbx = A._data
            return np.int64(getitem_str_offset(hkb__dfbbx, idx + 1) -
                getitem_str_offset(hkb__dfbbx, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    frg__wikt = np.int64(getitem_str_offset(A, i))
    tiqrn__ixm = np.int64(getitem_str_offset(A, i + 1))
    l = tiqrn__ixm - frg__wikt
    fuznd__wqmmn = get_data_ptr_ind(A, frg__wikt)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(fuznd__wqmmn, j) >= 128:
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
        gsk__sqa = 'in_str_arr = A._data'
        snr__udglt = 'input_index = A._indices[i]'
    else:
        gsk__sqa = 'in_str_arr = A'
        snr__udglt = 'input_index = i'
    rtwco__vjco = f"""def impl(B, j, A, i):
        if j == 0:
            setitem_str_offset(B, 0, 0)

        {gsk__sqa}
        {snr__udglt}

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
    sqgr__egr = {}
    exec(rtwco__vjco, {'setitem_str_offset': setitem_str_offset,
        'memcpy_region': memcpy_region, 'getitem_str_offset':
        getitem_str_offset, 'str_arr_set_na': str_arr_set_na,
        'str_arr_set_not_na': str_arr_set_not_na, 'get_data_ptr':
        get_data_ptr, 'bodo': bodo, 'np': np}, sqgr__egr)
    impl = sqgr__egr['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    knrm__kqwn = len(str_arr)
    axzv__qgbpj = np.empty(knrm__kqwn, np.bool_)
    for i in range(knrm__kqwn):
        axzv__qgbpj[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return axzv__qgbpj


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            knrm__kqwn = len(data)
            l = []
            for i in range(knrm__kqwn):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        xwgze__gdogd = data.count
        jslse__qgj = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(xwgze__gdogd)]
        if is_overload_true(str_null_bools):
            jslse__qgj += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(xwgze__gdogd) if is_str_arr_type(data.types[i]) or 
                data.types[i] == binary_array_type]
        rtwco__vjco = 'def f(data, str_null_bools=None):\n'
        rtwco__vjco += '  return ({}{})\n'.format(', '.join(jslse__qgj), 
            ',' if xwgze__gdogd == 1 else '')
        sqgr__egr = {}
        exec(rtwco__vjco, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, sqgr__egr)
        akcqm__xmtdp = sqgr__egr['f']
        return akcqm__xmtdp
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                knrm__kqwn = len(list_data)
                for i in range(knrm__kqwn):
                    cyb__lakf = list_data[i]
                    str_arr[i] = cyb__lakf
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                knrm__kqwn = len(list_data)
                for i in range(knrm__kqwn):
                    cyb__lakf = list_data[i]
                    str_arr[i] = cyb__lakf
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        xwgze__gdogd = str_arr.count
        aqv__jsak = 0
        rtwco__vjco = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(xwgze__gdogd):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                rtwco__vjco += (
                    """  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])
"""
                    .format(i, i, xwgze__gdogd + aqv__jsak))
                aqv__jsak += 1
            else:
                rtwco__vjco += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        rtwco__vjco += '  return\n'
        sqgr__egr = {}
        exec(rtwco__vjco, {'cp_str_list_to_array': cp_str_list_to_array},
            sqgr__egr)
        vrorb__vnzh = sqgr__egr['f']
        return vrorb__vnzh
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            knrm__kqwn = len(str_list)
            str_arr = pre_alloc_string_array(knrm__kqwn, -1)
            for i in range(knrm__kqwn):
                cyb__lakf = str_list[i]
                str_arr[i] = cyb__lakf
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            knrm__kqwn = len(A)
            aaumj__dtg = 0
            for i in range(knrm__kqwn):
                cyb__lakf = A[i]
                aaumj__dtg += get_utf8_size(cyb__lakf)
            return aaumj__dtg
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        knrm__kqwn = len(arr)
        n_chars = num_total_chars(arr)
        avg__qxhwk = pre_alloc_string_array(knrm__kqwn, np.int64(n_chars))
        copy_str_arr_slice(avg__qxhwk, arr, knrm__kqwn)
        return avg__qxhwk
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
    rtwco__vjco = 'def f(in_seq):\n'
    rtwco__vjco += '    n_strs = len(in_seq)\n'
    rtwco__vjco += '    A = pre_alloc_string_array(n_strs, -1)\n'
    rtwco__vjco += '    return A\n'
    sqgr__egr = {}
    exec(rtwco__vjco, {'pre_alloc_string_array': pre_alloc_string_array},
        sqgr__egr)
    fyg__twuyh = sqgr__egr['f']
    return fyg__twuyh


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        cds__ewmqp = 'pre_alloc_binary_array'
    else:
        cds__ewmqp = 'pre_alloc_string_array'
    rtwco__vjco = 'def f(in_seq):\n'
    rtwco__vjco += '    n_strs = len(in_seq)\n'
    rtwco__vjco += f'    A = {cds__ewmqp}(n_strs, -1)\n'
    rtwco__vjco += '    for i in range(n_strs):\n'
    rtwco__vjco += '        A[i] = in_seq[i]\n'
    rtwco__vjco += '    return A\n'
    sqgr__egr = {}
    exec(rtwco__vjco, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, sqgr__egr)
    fyg__twuyh = sqgr__egr['f']
    return fyg__twuyh


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        fwe__gaoly = builder.add(kct__azdf.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        ymdln__rywn = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        ftjo__rtna = builder.mul(fwe__gaoly, ymdln__rywn)
        sxbw__wvxl = context.make_array(offset_arr_type)(context, builder,
            kct__azdf.offsets).data
        cgutils.memset(builder, sxbw__wvxl, ftjo__rtna, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kdiw__aylcp = kct__azdf.n_arrays
        ftjo__rtna = builder.lshr(builder.add(kdiw__aylcp, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        gtruh__kou = context.make_array(null_bitmap_arr_type)(context,
            builder, kct__azdf.null_bitmap).data
        cgutils.memset(builder, gtruh__kou, ftjo__rtna, 0)
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
    udvo__aaaz = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        bac__rgeir = len(len_arr)
        for i in range(bac__rgeir):
            offsets[i] = udvo__aaaz
            udvo__aaaz += len_arr[i]
        offsets[bac__rgeir] = udvo__aaaz
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    qptzy__cgou = i // 8
    vap__nzrfm = getitem_str_bitmap(bits, qptzy__cgou)
    vap__nzrfm ^= np.uint8(-np.uint8(bit_is_set) ^ vap__nzrfm) & kBitmask[i % 8
        ]
    setitem_str_bitmap(bits, qptzy__cgou, vap__nzrfm)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    jcr__omcea = get_null_bitmap_ptr(out_str_arr)
    xilpk__wnshm = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        fvz__qpo = get_bit_bitmap(xilpk__wnshm, j)
        set_bit_to(jcr__omcea, out_start + j, fvz__qpo)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, wufgj__gpbkd, cgsf__rhn, srhot__tsd = args
        lwlf__vutk = _get_str_binary_arr_payload(context, builder,
            wufgj__gpbkd, string_array_type)
        bxf__xtuvq = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        ollpd__wiec = context.make_helper(builder, offset_arr_type,
            lwlf__vutk.offsets).data
        paka__kwul = context.make_helper(builder, offset_arr_type,
            bxf__xtuvq.offsets).data
        ddurl__tko = context.make_helper(builder, char_arr_type, lwlf__vutk
            .data).data
        wbh__iaxrd = context.make_helper(builder, char_arr_type, bxf__xtuvq
            .data).data
        num_total_chars = _get_num_total_chars(builder, ollpd__wiec,
            lwlf__vutk.n_arrays)
        ivz__nwzp = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        hkvh__brgzv = cgutils.get_or_insert_function(builder.module,
            ivz__nwzp, name='set_string_array_range')
        builder.call(hkvh__brgzv, [paka__kwul, wbh__iaxrd, ollpd__wiec,
            ddurl__tko, cgsf__rhn, srhot__tsd, lwlf__vutk.n_arrays,
            num_total_chars])
        dnkg__wdfm = context.typing_context.resolve_value_type(copy_nulls_range
            )
        fjgb__mdim = dnkg__wdfm.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        qyn__kat = context.get_function(dnkg__wdfm, fjgb__mdim)
        qyn__kat(builder, (out_arr, wufgj__gpbkd, cgsf__rhn))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    acvp__ctu = c.context.make_helper(c.builder, typ, val)
    fkfs__epw = ArrayItemArrayType(char_arr_type)
    kct__azdf = _get_array_item_arr_payload(c.context, c.builder, fkfs__epw,
        acvp__ctu.data)
    jexvx__qtzs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    vokb__olplq = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        vokb__olplq = 'pd_array_from_string_array'
    ivz__nwzp = lir.FunctionType(c.context.get_argument_type(types.pyobject
        ), [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    bvu__upk = cgutils.get_or_insert_function(c.builder.module, ivz__nwzp,
        name=vokb__olplq)
    zfvvw__mbdxx = c.context.make_array(offset_arr_type)(c.context, c.
        builder, kct__azdf.offsets).data
    fuznd__wqmmn = c.context.make_array(char_arr_type)(c.context, c.builder,
        kct__azdf.data).data
    gtruh__kou = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, kct__azdf.null_bitmap).data
    arr = c.builder.call(bvu__upk, [kct__azdf.n_arrays, zfvvw__mbdxx,
        fuznd__wqmmn, gtruh__kou, jexvx__qtzs])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gtruh__kou = context.make_array(null_bitmap_arr_type)(context,
            builder, kct__azdf.null_bitmap).data
        vgqw__ayj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        pou__kfa = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        vap__nzrfm = builder.load(builder.gep(gtruh__kou, [vgqw__ayj],
            inbounds=True))
        zzru__bmyi = lir.ArrayType(lir.IntType(8), 8)
        hjsg__dpqnp = cgutils.alloca_once_value(builder, lir.Constant(
            zzru__bmyi, (1, 2, 4, 8, 16, 32, 64, 128)))
        mxwtc__myum = builder.load(builder.gep(hjsg__dpqnp, [lir.Constant(
            lir.IntType(64), 0), pou__kfa], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(vap__nzrfm,
            mxwtc__myum), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        vgqw__ayj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        pou__kfa = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        gtruh__kou = context.make_array(null_bitmap_arr_type)(context,
            builder, kct__azdf.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, kct__azdf.
            offsets).data
        krfa__eiwmg = builder.gep(gtruh__kou, [vgqw__ayj], inbounds=True)
        vap__nzrfm = builder.load(krfa__eiwmg)
        zzru__bmyi = lir.ArrayType(lir.IntType(8), 8)
        hjsg__dpqnp = cgutils.alloca_once_value(builder, lir.Constant(
            zzru__bmyi, (1, 2, 4, 8, 16, 32, 64, 128)))
        mxwtc__myum = builder.load(builder.gep(hjsg__dpqnp, [lir.Constant(
            lir.IntType(64), 0), pou__kfa], inbounds=True))
        mxwtc__myum = builder.xor(mxwtc__myum, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(vap__nzrfm, mxwtc__myum), krfa__eiwmg)
        if str_arr_typ == string_array_type:
            pzeh__gbmmw = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            zikjg__anvpz = builder.icmp_unsigned('!=', pzeh__gbmmw,
                kct__azdf.n_arrays)
            with builder.if_then(zikjg__anvpz):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [pzeh__gbmmw]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        vgqw__ayj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        pou__kfa = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        gtruh__kou = context.make_array(null_bitmap_arr_type)(context,
            builder, kct__azdf.null_bitmap).data
        krfa__eiwmg = builder.gep(gtruh__kou, [vgqw__ayj], inbounds=True)
        vap__nzrfm = builder.load(krfa__eiwmg)
        zzru__bmyi = lir.ArrayType(lir.IntType(8), 8)
        hjsg__dpqnp = cgutils.alloca_once_value(builder, lir.Constant(
            zzru__bmyi, (1, 2, 4, 8, 16, 32, 64, 128)))
        mxwtc__myum = builder.load(builder.gep(hjsg__dpqnp, [lir.Constant(
            lir.IntType(64), 0), pou__kfa], inbounds=True))
        builder.store(builder.or_(vap__nzrfm, mxwtc__myum), krfa__eiwmg)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        kct__azdf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ftjo__rtna = builder.udiv(builder.add(kct__azdf.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        gtruh__kou = context.make_array(null_bitmap_arr_type)(context,
            builder, kct__azdf.null_bitmap).data
        cgutils.memset(builder, gtruh__kou, ftjo__rtna, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    awsci__hxa = context.make_helper(builder, string_array_type, str_arr)
    fkfs__epw = ArrayItemArrayType(char_arr_type)
    csoo__boji = context.make_helper(builder, fkfs__epw, awsci__hxa.data)
    mzjfs__nhlgo = ArrayItemArrayPayloadType(fkfs__epw)
    htx__ylf = context.nrt.meminfo_data(builder, csoo__boji.meminfo)
    ktz__uhqxl = builder.bitcast(htx__ylf, context.get_value_type(
        mzjfs__nhlgo).as_pointer())
    return ktz__uhqxl


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        oiib__gnx, phpps__dry = args
        sldm__ojss = _get_str_binary_arr_data_payload_ptr(context, builder,
            phpps__dry)
        mow__ypv = _get_str_binary_arr_data_payload_ptr(context, builder,
            oiib__gnx)
        vqe__qkxob = _get_str_binary_arr_payload(context, builder,
            phpps__dry, sig.args[1])
        onbk__jijv = _get_str_binary_arr_payload(context, builder,
            oiib__gnx, sig.args[0])
        context.nrt.incref(builder, char_arr_type, vqe__qkxob.data)
        context.nrt.incref(builder, offset_arr_type, vqe__qkxob.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, vqe__qkxob.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, onbk__jijv.data)
        context.nrt.decref(builder, offset_arr_type, onbk__jijv.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, onbk__jijv.
            null_bitmap)
        builder.store(builder.load(sldm__ojss), mow__ypv)
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
        knrm__kqwn = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return knrm__kqwn
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, pfm__ktsii, ubm__jskal = args
        kct__azdf = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, kct__azdf.
            offsets).data
        data = context.make_helper(builder, char_arr_type, kct__azdf.data).data
        ivz__nwzp = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        knste__exh = cgutils.get_or_insert_function(builder.module,
            ivz__nwzp, name='setitem_string_array')
        bajjt__wwdy = context.get_constant(types.int32, -1)
        nxbjz__fdqk = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, kct__azdf.
            n_arrays)
        builder.call(knste__exh, [offsets, data, num_total_chars, builder.
            extract_value(pfm__ktsii, 0), ubm__jskal, bajjt__wwdy,
            nxbjz__fdqk, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    ivz__nwzp = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64)])
    idr__kqtou = cgutils.get_or_insert_function(builder.module, ivz__nwzp,
        name='is_na')
    return builder.call(idr__kqtou, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        zfad__zjk, beq__woq, xwgze__gdogd, xwj__zeu = args
        cgutils.raw_memcpy(builder, zfad__zjk, beq__woq, xwgze__gdogd, xwj__zeu
            )
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
        bkk__msvn, grwds__fenxv = unicode_to_utf8_and_len(val)
        melr__pagsl = getitem_str_offset(A, ind)
        gcurv__dzs = getitem_str_offset(A, ind + 1)
        sbtwv__vcyae = gcurv__dzs - melr__pagsl
        if sbtwv__vcyae != grwds__fenxv:
            return False
        pfm__ktsii = get_data_ptr_ind(A, melr__pagsl)
        return memcmp(pfm__ktsii, bkk__msvn, grwds__fenxv) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        melr__pagsl = getitem_str_offset(A, ind)
        sbtwv__vcyae = bodo.libs.str_ext.int_to_str_len(val)
        luji__cgl = melr__pagsl + sbtwv__vcyae
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            melr__pagsl, luji__cgl)
        pfm__ktsii = get_data_ptr_ind(A, melr__pagsl)
        inplace_int64_to_str(pfm__ktsii, sbtwv__vcyae, val)
        setitem_str_offset(A, ind + 1, melr__pagsl + sbtwv__vcyae)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        pfm__ktsii, = args
        aqu__swtj = context.insert_const_string(builder.module, '<NA>')
        phe__znhu = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, pfm__ktsii, aqu__swtj, phe__znhu, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    phk__dyhag = len('<NA>')

    def impl(A, ind):
        melr__pagsl = getitem_str_offset(A, ind)
        luji__cgl = melr__pagsl + phk__dyhag
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            melr__pagsl, luji__cgl)
        pfm__ktsii = get_data_ptr_ind(A, melr__pagsl)
        inplace_set_NA_str(pfm__ktsii)
        setitem_str_offset(A, ind + 1, melr__pagsl + phk__dyhag)
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
            melr__pagsl = getitem_str_offset(A, ind)
            gcurv__dzs = getitem_str_offset(A, ind + 1)
            ubm__jskal = gcurv__dzs - melr__pagsl
            pfm__ktsii = get_data_ptr_ind(A, melr__pagsl)
            hzdp__xec = decode_utf8(pfm__ktsii, ubm__jskal)
            return hzdp__xec
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            knrm__kqwn = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(knrm__kqwn):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            ssq__lma = get_data_ptr(out_arr).data
            vxvjj__ppw = get_data_ptr(A).data
            aqv__jsak = 0
            exob__fqro = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(knrm__kqwn):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    slq__ryyb = get_str_arr_item_length(A, i)
                    if slq__ryyb == 1:
                        copy_single_char(ssq__lma, exob__fqro, vxvjj__ppw,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(ssq__lma, exob__fqro, vxvjj__ppw,
                            getitem_str_offset(A, i), slq__ryyb, 1)
                    exob__fqro += slq__ryyb
                    setitem_str_offset(out_arr, aqv__jsak + 1, exob__fqro)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, aqv__jsak)
                    else:
                        str_arr_set_not_na(out_arr, aqv__jsak)
                    aqv__jsak += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            knrm__kqwn = len(ind)
            out_arr = pre_alloc_string_array(knrm__kqwn, -1)
            aqv__jsak = 0
            for i in range(knrm__kqwn):
                cyb__lakf = A[ind[i]]
                out_arr[aqv__jsak] = cyb__lakf
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, aqv__jsak)
                aqv__jsak += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            knrm__kqwn = len(A)
            jayj__chjx = numba.cpython.unicode._normalize_slice(ind, knrm__kqwn
                )
            ldi__vhfo = numba.cpython.unicode._slice_span(jayj__chjx)
            if jayj__chjx.step == 1:
                melr__pagsl = getitem_str_offset(A, jayj__chjx.start)
                gcurv__dzs = getitem_str_offset(A, jayj__chjx.stop)
                n_chars = gcurv__dzs - melr__pagsl
                avg__qxhwk = pre_alloc_string_array(ldi__vhfo, np.int64(
                    n_chars))
                for i in range(ldi__vhfo):
                    avg__qxhwk[i] = A[jayj__chjx.start + i]
                    if str_arr_is_na(A, jayj__chjx.start + i):
                        str_arr_set_na(avg__qxhwk, i)
                return avg__qxhwk
            else:
                avg__qxhwk = pre_alloc_string_array(ldi__vhfo, -1)
                for i in range(ldi__vhfo):
                    avg__qxhwk[i] = A[jayj__chjx.start + i * jayj__chjx.step]
                    if str_arr_is_na(A, jayj__chjx.start + i * jayj__chjx.step
                        ):
                        str_arr_set_na(avg__qxhwk, i)
                return avg__qxhwk
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
    hje__wbai = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(hje__wbai)
        dzwhr__tpv = 4

        def impl_scalar(A, idx, val):
            wghys__qmj = (val._length if val._is_ascii else dzwhr__tpv *
                val._length)
            spopa__bwj = A._data
            melr__pagsl = np.int64(getitem_str_offset(A, idx))
            luji__cgl = melr__pagsl + wghys__qmj
            bodo.libs.array_item_arr_ext.ensure_data_capacity(spopa__bwj,
                melr__pagsl, luji__cgl)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                luji__cgl, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                jayj__chjx = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                frg__wikt = jayj__chjx.start
                spopa__bwj = A._data
                melr__pagsl = np.int64(getitem_str_offset(A, frg__wikt))
                luji__cgl = melr__pagsl + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(spopa__bwj,
                    melr__pagsl, luji__cgl)
                set_string_array_range(A, val, frg__wikt, melr__pagsl)
                dsfp__wqxb = 0
                for i in range(jayj__chjx.start, jayj__chjx.stop,
                    jayj__chjx.step):
                    if str_arr_is_na(val, dsfp__wqxb):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    dsfp__wqxb += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                isi__dtfur = str_list_to_array(val)
                A[idx] = isi__dtfur
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                jayj__chjx = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(jayj__chjx.start, jayj__chjx.stop,
                    jayj__chjx.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(hje__wbai)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                knrm__kqwn = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(knrm__kqwn, -1)
                for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
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
                knrm__kqwn = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(knrm__kqwn, -1)
                inibr__unwv = 0
                for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, inibr__unwv):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, inibr__unwv)
                        else:
                            out_arr[i] = str(val[inibr__unwv])
                        inibr__unwv += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(hje__wbai)
    raise BodoError(hje__wbai)


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
    eapw__ffa = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(eapw__ffa, (types.Float, types.Integer)
        ) and eapw__ffa not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(eapw__ffa, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            knrm__kqwn = len(A)
            B = np.empty(knrm__kqwn, eapw__ffa)
            for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif eapw__ffa == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            knrm__kqwn = len(A)
            B = np.empty(knrm__kqwn, eapw__ffa)
            for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif eapw__ffa == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            knrm__kqwn = len(A)
            B = np.empty(knrm__kqwn, eapw__ffa)
            for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            knrm__kqwn = len(A)
            B = np.empty(knrm__kqwn, eapw__ffa)
            for i in numba.parfors.parfor.internal_prange(knrm__kqwn):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        pfm__ktsii, ubm__jskal = args
        ffu__wih = context.get_python_api(builder)
        vtljx__rdy = ffu__wih.string_from_string_and_size(pfm__ktsii,
            ubm__jskal)
        knfd__jdts = ffu__wih.to_native_value(string_type, vtljx__rdy).value
        ehgs__oxz = cgutils.create_struct_proxy(string_type)(context,
            builder, knfd__jdts)
        ehgs__oxz.hash = ehgs__oxz.hash.type(-1)
        ffu__wih.decref(vtljx__rdy)
        return ehgs__oxz._getvalue()
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
        cvug__fkhs, arr, ind, rrboy__anik = args
        kct__azdf = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, kct__azdf.
            offsets).data
        data = context.make_helper(builder, char_arr_type, kct__azdf.data).data
        ivz__nwzp = lir.FunctionType(lir.IntType(32), [cvug__fkhs.type, lir
            .IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        rudkk__dxdp = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            rudkk__dxdp = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        pes__fyiw = cgutils.get_or_insert_function(builder.module,
            ivz__nwzp, rudkk__dxdp)
        return builder.call(pes__fyiw, [cvug__fkhs, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    jexvx__qtzs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    ivz__nwzp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(32)])
    hvzk__lxyil = cgutils.get_or_insert_function(c.builder.module,
        ivz__nwzp, name='string_array_from_sequence')
    htasp__yeq = c.builder.call(hvzk__lxyil, [val, jexvx__qtzs])
    fkfs__epw = ArrayItemArrayType(char_arr_type)
    csoo__boji = c.context.make_helper(c.builder, fkfs__epw)
    csoo__boji.meminfo = htasp__yeq
    awsci__hxa = c.context.make_helper(c.builder, typ)
    spopa__bwj = csoo__boji._getvalue()
    awsci__hxa.data = spopa__bwj
    gwz__iltrf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(awsci__hxa._getvalue(), is_error=gwz__iltrf)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    knrm__kqwn = len(pyval)
    exob__fqro = 0
    yefcu__qlgo = np.empty(knrm__kqwn + 1, np_offset_type)
    vwiv__mylz = []
    oauy__fsndm = np.empty(knrm__kqwn + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        yefcu__qlgo[i] = exob__fqro
        tzxn__fepry = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(oauy__fsndm, i, int(not
            tzxn__fepry))
        if tzxn__fepry:
            continue
        tkhjg__uvrq = list(s.encode()) if isinstance(s, str) else list(s)
        vwiv__mylz.extend(tkhjg__uvrq)
        exob__fqro += len(tkhjg__uvrq)
    yefcu__qlgo[knrm__kqwn] = exob__fqro
    lovxr__uyfhs = np.array(vwiv__mylz, np.uint8)
    sdyzn__fjb = context.get_constant(types.int64, knrm__kqwn)
    hvurg__vojvi = context.get_constant_generic(builder, char_arr_type,
        lovxr__uyfhs)
    tjd__qad = context.get_constant_generic(builder, offset_arr_type,
        yefcu__qlgo)
    hdl__hxjpw = context.get_constant_generic(builder, null_bitmap_arr_type,
        oauy__fsndm)
    kct__azdf = lir.Constant.literal_struct([sdyzn__fjb, hvurg__vojvi,
        tjd__qad, hdl__hxjpw])
    kct__azdf = cgutils.global_constant(builder, '.const.payload', kct__azdf
        ).bitcast(cgutils.voidptr_t)
    xjz__xhipy = context.get_constant(types.int64, -1)
    dpu__iflul = context.get_constant_null(types.voidptr)
    ghas__gbydw = lir.Constant.literal_struct([xjz__xhipy, dpu__iflul,
        dpu__iflul, kct__azdf, xjz__xhipy])
    ghas__gbydw = cgutils.global_constant(builder, '.const.meminfo',
        ghas__gbydw).bitcast(cgutils.voidptr_t)
    spopa__bwj = lir.Constant.literal_struct([ghas__gbydw])
    awsci__hxa = lir.Constant.literal_struct([spopa__bwj])
    return awsci__hxa


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
