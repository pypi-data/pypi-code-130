"""Array implementation for binary (bytes) objects, which are usually immutable.
It is equivalent to string array, except that it stores a 'bytes' object for each
element instead of 'str'.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, overload, overload_attribute, overload_method
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.utils.typing import BodoError, is_list_like_index_type
_bytes_fromhex = types.ExternalFunction('bytes_fromhex', types.int64(types.
    voidptr, types.voidptr, types.uint64))
ll.add_symbol('bytes_to_hex', hstr_ext.bytes_to_hex)
ll.add_symbol('bytes_fromhex', hstr_ext.bytes_fromhex)
bytes_type = types.Bytes(types.uint8, 1, 'C', readonly=True)


@overload(len)
def bytes_len_overload(bytes_obj):
    if isinstance(bytes_obj, types.Bytes):
        return lambda bytes_obj: bytes_obj._nitems


@overload(operator.getitem, no_unliteral=True)
def bytes_getitem(byte_obj, ind):
    if not isinstance(byte_obj, types.Bytes):
        return
    if isinstance(ind, types.SliceType):

        def impl(byte_obj, ind):
            arr = cast_bytes_uint8array(byte_obj)
            tqe__tijss = bodo.utils.conversion.ensure_contig_if_np(arr[ind])
            return cast_uint8array_bytes(tqe__tijss)
        return impl


class BinaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(BinaryArrayType, self).__init__(name='BinaryArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return bytes_type

    def copy(self):
        return BinaryArrayType()

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


binary_array_type = BinaryArrayType()


@overload(len, no_unliteral=True)
def bin_arr_len_overload(bin_arr):
    if bin_arr == binary_array_type:
        return lambda bin_arr: len(bin_arr._data)


make_attribute_wrapper(types.Bytes, 'nitems', '_nitems')


@overload_attribute(BinaryArrayType, 'size')
def bin_arr_size_overload(bin_arr):
    return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'shape')
def bin_arr_shape_overload(bin_arr):
    return lambda bin_arr: (len(bin_arr._data),)


@overload_attribute(BinaryArrayType, 'nbytes')
def bin_arr_nbytes_overload(bin_arr):
    return lambda bin_arr: bin_arr._data.nbytes


@overload_attribute(BinaryArrayType, 'ndim')
def overload_bin_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BinaryArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: np.dtype('O')


@numba.njit
def pre_alloc_binary_array(n_bytestrs, n_chars):
    if n_chars is None:
        n_chars = -1
    bin_arr = init_binary_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_bytestrs), (np.int64(n_chars)
        ,), bodo.libs.str_arr_ext.char_arr_type))
    if n_chars == 0:
        bodo.libs.str_arr_ext.set_all_offsets_to_0(bin_arr)
    return bin_arr


@intrinsic
def init_binary_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, sig, args):
        huui__eirgr, = args
        ntvp__mpypx = context.make_helper(builder, binary_array_type)
        ntvp__mpypx.data = huui__eirgr
        context.nrt.incref(builder, data_typ, huui__eirgr)
        return ntvp__mpypx._getvalue()
    return binary_array_type(data_typ), codegen


@intrinsic
def init_bytes_type(typingctx, data_typ, length_type):
    assert data_typ == types.Array(types.uint8, 1, 'C')
    assert length_type == types.int64

    def codegen(context, builder, sig, args):
        ccpb__lzw = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        pjbxa__yho = args[1]
        bhfm__obqnf = cgutils.create_struct_proxy(bytes_type)(context, builder)
        bhfm__obqnf.meminfo = context.nrt.meminfo_alloc(builder, pjbxa__yho)
        bhfm__obqnf.nitems = pjbxa__yho
        bhfm__obqnf.itemsize = lir.Constant(bhfm__obqnf.itemsize.type, 1)
        bhfm__obqnf.data = context.nrt.meminfo_data(builder, bhfm__obqnf.
            meminfo)
        bhfm__obqnf.parent = cgutils.get_null_value(bhfm__obqnf.parent.type)
        bhfm__obqnf.shape = cgutils.pack_array(builder, [pjbxa__yho],
            context.get_value_type(types.intp))
        bhfm__obqnf.strides = ccpb__lzw.strides
        cgutils.memcpy(builder, bhfm__obqnf.data, ccpb__lzw.data, pjbxa__yho)
        return bhfm__obqnf._getvalue()
    return bytes_type(data_typ, length_type), codegen


@intrinsic
def cast_bytes_uint8array(typingctx, data_typ):
    assert data_typ == bytes_type

    def codegen(context, builder, sig, args):
        return impl_ret_borrowed(context, builder, sig.return_type, args[0])
    return types.Array(types.uint8, 1, 'C')(data_typ), codegen


@intrinsic
def cast_uint8array_bytes(typingctx, data_typ):
    assert data_typ == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, sig, args):
        return impl_ret_borrowed(context, builder, sig.return_type, args[0])
    return bytes_type(data_typ), codegen


@overload_method(BinaryArrayType, 'copy', no_unliteral=True)
def binary_arr_copy_overload(arr):

    def copy_impl(arr):
        return init_binary_arr(arr._data.copy())
    return copy_impl


@overload_method(types.Bytes, 'hex')
def binary_arr_hex(arr):
    thrqz__djjs = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def impl(arr):
        pjbxa__yho = len(arr) * 2
        output = numba.cpython.unicode._empty_string(thrqz__djjs, pjbxa__yho, 1
            )
        bytes_to_hex(output, arr)
        return output
    return impl


@lower_cast(types.CPointer(types.uint8), types.voidptr)
def cast_uint8_array_to_voidptr(context, builder, fromty, toty, val):
    return val


make_attribute_wrapper(types.Bytes, 'data', '_data')


@overload_method(types.Bytes, '__hash__')
def bytes_hash(arr):

    def impl(arr):
        return numba.cpython.hashing._Py_HashBytes(arr._data, len(arr))
    return impl


@intrinsic
def bytes_to_hex(typingctx, output, arr):

    def codegen(context, builder, sig, args):
        zvicv__jtkm = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        viv__jce = cgutils.create_struct_proxy(sig.args[1])(context,
            builder, value=args[1])
        xyqn__ofe = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(64)])
        ghwfa__dpdf = cgutils.get_or_insert_function(builder.module,
            xyqn__ofe, name='bytes_to_hex')
        builder.call(ghwfa__dpdf, (zvicv__jtkm.data, viv__jce.data,
            viv__jce.nitems))
    return types.void(output, arr), codegen


@overload(operator.getitem, no_unliteral=True)
def binary_arr_getitem(arr, ind):
    if arr != binary_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl(arr, ind):
            fpwas__ghlp = arr._data[ind]
            return init_bytes_type(fpwas__ghlp, len(fpwas__ghlp))
        return impl
    if is_list_like_index_type(ind) and (ind.dtype == types.bool_ or
        isinstance(ind.dtype, types.Integer)) or isinstance(ind, types.
        SliceType):
        return lambda arr, ind: init_binary_arr(arr._data[ind])
    raise BodoError(
        f'getitem for Binary Array with indexing type {ind} not supported.')


def bytes_fromhex(hex_str):
    pass


@overload(bytes_fromhex)
def overload_bytes_fromhex(hex_str):
    hex_str = types.unliteral(hex_str)
    if hex_str == bodo.string_type:
        thrqz__djjs = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(hex_str):
            if not hex_str._is_ascii or hex_str._kind != thrqz__djjs:
                raise TypeError(
                    'bytes.fromhex is only supported on ascii strings')
            huui__eirgr = np.empty(len(hex_str) // 2, np.uint8)
            pjbxa__yho = _bytes_fromhex(huui__eirgr.ctypes, hex_str._data,
                len(hex_str))
            ejgdz__nppkj = init_bytes_type(huui__eirgr, pjbxa__yho)
            return ejgdz__nppkj
        return impl
    raise BodoError(f'bytes.fromhex not supported with argument type {hex_str}'
        )


@overload(operator.setitem)
def binary_arr_setitem(arr, ind, val):
    if arr != binary_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if val != bytes_type:
        raise BodoError(
            f'setitem for Binary Array only supported with bytes value and integer indexing'
            )
    if isinstance(ind, types.Integer):

        def impl(arr, ind, val):
            arr._data[ind] = cast_bytes_uint8array(val)
        return impl
    raise BodoError(
        f'setitem for Binary Array with indexing type {ind} not supported.')


def create_binary_cmp_op_overload(op):

    def overload_binary_cmp(lhs, rhs):
        kppcf__nzgg = lhs == binary_array_type
        vzte__wlufd = rhs == binary_array_type
        qbtlv__ubc = 'lhs' if kppcf__nzgg else 'rhs'
        emy__vjyfx = 'def impl(lhs, rhs):\n'
        emy__vjyfx += '  numba.parfors.parfor.init_prange()\n'
        emy__vjyfx += f'  n = len({qbtlv__ubc})\n'
        emy__vjyfx += (
            '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n)\n')
        emy__vjyfx += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        gipt__yvae = []
        if kppcf__nzgg:
            gipt__yvae.append('bodo.libs.array_kernels.isna(lhs, i)')
        if vzte__wlufd:
            gipt__yvae.append('bodo.libs.array_kernels.isna(rhs, i)')
        emy__vjyfx += f"    if {' or '.join(gipt__yvae)}:\n"
        emy__vjyfx += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        emy__vjyfx += '      continue\n'
        lvqbg__vlih = 'lhs[i]' if kppcf__nzgg else 'lhs'
        qasvg__nmutr = 'rhs[i]' if vzte__wlufd else 'rhs'
        emy__vjyfx += f'    out_arr[i] = op({lvqbg__vlih}, {qasvg__nmutr})\n'
        emy__vjyfx += '  return out_arr\n'
        rvtxb__fvrqn = {}
        exec(emy__vjyfx, {'bodo': bodo, 'numba': numba, 'op': op}, rvtxb__fvrqn
            )
        return rvtxb__fvrqn['impl']
    return overload_binary_cmp


lower_builtin('getiter', binary_array_type)(numba.np.arrayobj.getiter_array)


def pre_alloc_binary_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_binary_arr_ext_pre_alloc_binary_array
    ) = pre_alloc_binary_arr_equiv
