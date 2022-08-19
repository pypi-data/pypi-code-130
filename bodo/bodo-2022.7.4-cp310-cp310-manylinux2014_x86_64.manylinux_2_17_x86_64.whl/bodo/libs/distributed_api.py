import atexit
import datetime
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload, register_jitable
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, decode_if_dict_array, is_overload_false, is_overload_none, is_str_arr_type
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, is_array_typ, numba_to_c_type
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    hooun__fgbg = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, hooun__fgbg, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    hooun__fgbg = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, hooun__fgbg, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            hooun__fgbg = get_type_enum(arr)
            return _isend(arr.ctypes, size, hooun__fgbg, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        hooun__fgbg = np.int32(numba_to_c_type(arr.dtype))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            rhj__ryn = size + 7 >> 3
            izpio__hugk = _isend(arr._data.ctypes, size, hooun__fgbg, pe,
                tag, cond)
            cytj__qbhzb = _isend(arr._null_bitmap.ctypes, rhj__ryn,
                jzxn__kqx, pe, tag, cond)
            return izpio__hugk, cytj__qbhzb
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        zfys__iiu = np.int32(numba_to_c_type(offset_type))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            zojyx__frmds = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(zojyx__frmds, pe, tag - 1)
            rhj__ryn = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                zfys__iiu, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), zojyx__frmds,
                jzxn__kqx, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), rhj__ryn,
                jzxn__kqx, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            hooun__fgbg = get_type_enum(arr)
            return _irecv(arr.ctypes, size, hooun__fgbg, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        hooun__fgbg = np.int32(numba_to_c_type(arr.dtype))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            rhj__ryn = size + 7 >> 3
            izpio__hugk = _irecv(arr._data.ctypes, size, hooun__fgbg, pe,
                tag, cond)
            cytj__qbhzb = _irecv(arr._null_bitmap.ctypes, rhj__ryn,
                jzxn__kqx, pe, tag, cond)
            return izpio__hugk, cytj__qbhzb
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        zfys__iiu = np.int32(numba_to_c_type(offset_type))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            wtagy__ugis = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            wtagy__ugis = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zca__xaxeo = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {wtagy__ugis}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        xmy__sovj = dict()
        exec(zca__xaxeo, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            zfys__iiu, 'char_typ_enum': jzxn__kqx}, xmy__sovj)
        impl = xmy__sovj['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    hooun__fgbg = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), hooun__fgbg)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        yhk__sre = n_pes if rank == root or allgather else 0
        rxu__zhdkz = np.empty(yhk__sre, dtype)
        c_gather_scalar(send.ctypes, rxu__zhdkz.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return rxu__zhdkz
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        anij__hyi = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], anij__hyi)
        return builder.bitcast(anij__hyi, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        anij__hyi = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(anij__hyi)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    tqb__wyj = types.unliteral(value)
    if isinstance(tqb__wyj, IndexValueType):
        tqb__wyj = tqb__wyj.val_typ
        siuv__durb = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            siuv__durb.append(types.int64)
            siuv__durb.append(bodo.datetime64ns)
            siuv__durb.append(bodo.timedelta64ns)
            siuv__durb.append(bodo.datetime_date_type)
            siuv__durb.append(bodo.TimeType)
        if tqb__wyj not in siuv__durb:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(tqb__wyj))
    typ_enum = np.int32(numba_to_c_type(tqb__wyj))

    def impl(value, reduce_op):
        qnu__oxcqt = value_to_ptr(value)
        jpnbg__btop = value_to_ptr(value)
        _dist_reduce(qnu__oxcqt, jpnbg__btop, reduce_op, typ_enum)
        return load_val_ptr(jpnbg__btop, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    tqb__wyj = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(tqb__wyj))
    amv__zgz = tqb__wyj(0)

    def impl(value, reduce_op):
        qnu__oxcqt = value_to_ptr(value)
        jpnbg__btop = value_to_ptr(amv__zgz)
        _dist_exscan(qnu__oxcqt, jpnbg__btop, reduce_op, typ_enum)
        return load_val_ptr(jpnbg__btop, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    kdit__uxssg = 0
    jank__tejf = 0
    for i in range(len(recv_counts)):
        zex__qeme = recv_counts[i]
        rhj__ryn = recv_counts_nulls[i]
        evmbd__qykw = tmp_null_bytes[kdit__uxssg:kdit__uxssg + rhj__ryn]
        for axrr__tqkqo in range(zex__qeme):
            set_bit_to(null_bitmap_ptr, jank__tejf, get_bit(evmbd__qykw,
                axrr__tqkqo))
            jank__tejf += 1
        kdit__uxssg += rhj__ryn


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            kios__igdlm = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                kios__igdlm, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            nckok__bcqq = data.size
            recv_counts = gather_scalar(np.int32(nckok__bcqq), allgather,
                root=root)
            fguda__qjzxg = recv_counts.sum()
            ptc__vqo = empty_like_type(fguda__qjzxg, data)
            vyh__wwvm = np.empty(1, np.int32)
            if rank == root or allgather:
                vyh__wwvm = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(nckok__bcqq), ptc__vqo.ctypes,
                recv_counts.ctypes, vyh__wwvm.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return ptc__vqo.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            ptc__vqo = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(ptc__vqo)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ptc__vqo = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(ptc__vqo)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nckok__bcqq = len(data)
            rhj__ryn = nckok__bcqq + 7 >> 3
            recv_counts = gather_scalar(np.int32(nckok__bcqq), allgather,
                root=root)
            fguda__qjzxg = recv_counts.sum()
            ptc__vqo = empty_like_type(fguda__qjzxg, data)
            vyh__wwvm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sglth__yreez = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                vyh__wwvm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sglth__yreez = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(nckok__bcqq),
                ptc__vqo._days_data.ctypes, recv_counts.ctypes, vyh__wwvm.
                ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(nckok__bcqq),
                ptc__vqo._seconds_data.ctypes, recv_counts.ctypes,
                vyh__wwvm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(nckok__bcqq),
                ptc__vqo._microseconds_data.ctypes, recv_counts.ctypes,
                vyh__wwvm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(rhj__ryn),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sglth__yreez.ctypes, jzxn__kqx, allgather, np.int32(root))
            copy_gathered_null_bytes(ptc__vqo._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ptc__vqo
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nckok__bcqq = len(data)
            rhj__ryn = nckok__bcqq + 7 >> 3
            recv_counts = gather_scalar(np.int32(nckok__bcqq), allgather,
                root=root)
            fguda__qjzxg = recv_counts.sum()
            ptc__vqo = empty_like_type(fguda__qjzxg, data)
            vyh__wwvm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sglth__yreez = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                vyh__wwvm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sglth__yreez = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(nckok__bcqq), ptc__vqo.
                _data.ctypes, recv_counts.ctypes, vyh__wwvm.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(rhj__ryn),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sglth__yreez.ctypes, jzxn__kqx, allgather, np.int32(root))
            copy_gathered_null_bytes(ptc__vqo._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ptc__vqo
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        zzfd__atn = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            yafw__gus = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                yafw__gus, zzfd__atn)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            swzv__inpz = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            ipmvy__aantb = bodo.gatherv(data._right, allgather, warn_if_rep,
                root)
            return bodo.libs.interval_arr_ext.init_interval_array(swzv__inpz,
                ipmvy__aantb)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            aooei__ypfw = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            inyng__qljb = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                inyng__qljb, aooei__ypfw)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        qcud__fuoh = np.iinfo(np.int64).max
        muu__fjj = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            fosx__amxf = data._start
            tva__ofmj = data._stop
            if len(data) == 0:
                fosx__amxf = qcud__fuoh
                tva__ofmj = muu__fjj
            fosx__amxf = bodo.libs.distributed_api.dist_reduce(fosx__amxf,
                np.int32(Reduce_Type.Min.value))
            tva__ofmj = bodo.libs.distributed_api.dist_reduce(tva__ofmj, np
                .int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if fosx__amxf == qcud__fuoh and tva__ofmj == muu__fjj:
                fosx__amxf = 0
                tva__ofmj = 0
            vvtq__dbe = max(0, -(-(tva__ofmj - fosx__amxf) // data._step))
            if vvtq__dbe < total_len:
                tva__ofmj = fosx__amxf + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                fosx__amxf = 0
                tva__ofmj = 0
            return bodo.hiframes.pd_index_ext.init_range_index(fosx__amxf,
                tva__ofmj, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            ssuk__uttu = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, ssuk__uttu)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ptc__vqo = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(ptc__vqo,
                data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        awu__lql = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        zca__xaxeo = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        zca__xaxeo += '  T = data\n'
        zca__xaxeo += '  T2 = init_table(T, True)\n'
        for ztx__lvpei in data.type_to_blk.values():
            awu__lql[f'arr_inds_{ztx__lvpei}'] = np.array(data.
                block_to_arr_ind[ztx__lvpei], dtype=np.int64)
            zca__xaxeo += (
                f'  arr_list_{ztx__lvpei} = get_table_block(T, {ztx__lvpei})\n'
                )
            zca__xaxeo += f"""  out_arr_list_{ztx__lvpei} = alloc_list_like(arr_list_{ztx__lvpei}, len(arr_list_{ztx__lvpei}), True)
"""
            zca__xaxeo += f'  for i in range(len(arr_list_{ztx__lvpei})):\n'
            zca__xaxeo += (
                f'    arr_ind_{ztx__lvpei} = arr_inds_{ztx__lvpei}[i]\n')
            zca__xaxeo += f"""    ensure_column_unboxed(T, arr_list_{ztx__lvpei}, i, arr_ind_{ztx__lvpei})
"""
            zca__xaxeo += f"""    out_arr_{ztx__lvpei} = bodo.gatherv(arr_list_{ztx__lvpei}[i], allgather, warn_if_rep, root)
"""
            zca__xaxeo += (
                f'    out_arr_list_{ztx__lvpei}[i] = out_arr_{ztx__lvpei}\n')
            zca__xaxeo += (
                f'  T2 = set_table_block(T2, out_arr_list_{ztx__lvpei}, {ztx__lvpei})\n'
                )
        zca__xaxeo += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        zca__xaxeo += f'  T2 = set_table_len(T2, length)\n'
        zca__xaxeo += f'  return T2\n'
        xmy__sovj = {}
        exec(zca__xaxeo, awu__lql, xmy__sovj)
        dxs__cbac = xmy__sovj['impl_table']
        return dxs__cbac
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ajwq__vjhw = len(data.columns)
        if ajwq__vjhw == 0:
            xkx__hvule = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                sfa__txg = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    sfa__txg, xkx__hvule)
            return impl
        hmrb__joyt = ', '.join(f'g_data_{i}' for i in range(ajwq__vjhw))
        zca__xaxeo = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            wpej__iobk = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            hmrb__joyt = 'T2'
            zca__xaxeo += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            zca__xaxeo += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(ajwq__vjhw):
                zca__xaxeo += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                zca__xaxeo += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        zca__xaxeo += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zca__xaxeo += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        zca__xaxeo += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(hmrb__joyt))
        xmy__sovj = {}
        awu__lql = {'bodo': bodo, '__col_name_meta_value_gatherv_with_cols':
            ColNamesMetaType(data.columns)}
        exec(zca__xaxeo, awu__lql, xmy__sovj)
        qupsr__xoa = xmy__sovj['impl_df']
        return qupsr__xoa
    if isinstance(data, ArrayItemArrayType):
        szd__tpdhd = np.int32(numba_to_c_type(types.int32))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            qxo__udy = bodo.libs.array_item_arr_ext.get_offsets(data)
            yzrsm__sbbr = bodo.libs.array_item_arr_ext.get_data(data)
            yzrsm__sbbr = yzrsm__sbbr[:qxo__udy[-1]]
            pqv__pwjf = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            nckok__bcqq = len(data)
            tqchb__jxfoi = np.empty(nckok__bcqq, np.uint32)
            rhj__ryn = nckok__bcqq + 7 >> 3
            for i in range(nckok__bcqq):
                tqchb__jxfoi[i] = qxo__udy[i + 1] - qxo__udy[i]
            recv_counts = gather_scalar(np.int32(nckok__bcqq), allgather,
                root=root)
            fguda__qjzxg = recv_counts.sum()
            vyh__wwvm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sglth__yreez = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                vyh__wwvm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for shkho__qsv in range(len(recv_counts)):
                    recv_counts_nulls[shkho__qsv] = recv_counts[shkho__qsv
                        ] + 7 >> 3
                sglth__yreez = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            zbn__gaarl = np.empty(fguda__qjzxg + 1, np.uint32)
            qyez__pyeku = bodo.gatherv(yzrsm__sbbr, allgather, warn_if_rep,
                root)
            bctbd__izydl = np.empty(fguda__qjzxg + 7 >> 3, np.uint8)
            c_gatherv(tqchb__jxfoi.ctypes, np.int32(nckok__bcqq),
                zbn__gaarl.ctypes, recv_counts.ctypes, vyh__wwvm.ctypes,
                szd__tpdhd, allgather, np.int32(root))
            c_gatherv(pqv__pwjf.ctypes, np.int32(rhj__ryn), tmp_null_bytes.
                ctypes, recv_counts_nulls.ctypes, sglth__yreez.ctypes,
                jzxn__kqx, allgather, np.int32(root))
            dummy_use(data)
            hzwh__wlasy = np.empty(fguda__qjzxg + 1, np.uint64)
            convert_len_arr_to_offset(zbn__gaarl.ctypes, hzwh__wlasy.ctypes,
                fguda__qjzxg)
            copy_gathered_null_bytes(bctbd__izydl.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                fguda__qjzxg, qyez__pyeku, hzwh__wlasy, bctbd__izydl)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        rktk__laurb = data.names
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vpvo__mcxsr = bodo.libs.struct_arr_ext.get_data(data)
            qfmaw__rhud = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            gqrc__avn = bodo.gatherv(vpvo__mcxsr, allgather=allgather, root
                =root)
            rank = bodo.libs.distributed_api.get_rank()
            nckok__bcqq = len(data)
            rhj__ryn = nckok__bcqq + 7 >> 3
            recv_counts = gather_scalar(np.int32(nckok__bcqq), allgather,
                root=root)
            fguda__qjzxg = recv_counts.sum()
            ukrbs__ixl = np.empty(fguda__qjzxg + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            sglth__yreez = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sglth__yreez = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(qfmaw__rhud.ctypes, np.int32(rhj__ryn),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sglth__yreez.ctypes, jzxn__kqx, allgather, np.int32(root))
            copy_gathered_null_bytes(ukrbs__ixl.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(gqrc__avn,
                ukrbs__ixl, rktk__laurb)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ptc__vqo = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(ptc__vqo)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ptc__vqo = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(ptc__vqo)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ptc__vqo = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(ptc__vqo)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ptc__vqo = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            ttvag__gvdh = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            qjh__xtd = bodo.gatherv(data.indptr, allgather, warn_if_rep, root)
            afi__jwq = gather_scalar(data.shape[0], allgather, root=root)
            ulxno__stkux = afi__jwq.sum()
            ajwq__vjhw = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            fts__yev = np.empty(ulxno__stkux + 1, np.int64)
            ttvag__gvdh = ttvag__gvdh.astype(np.int64)
            fts__yev[0] = 0
            vdyv__vqb = 1
            poen__daing = 0
            for hyhkv__wijtn in afi__jwq:
                for elbhm__gcjb in range(hyhkv__wijtn):
                    vrg__chx = qjh__xtd[poen__daing + 1] - qjh__xtd[poen__daing
                        ]
                    fts__yev[vdyv__vqb] = fts__yev[vdyv__vqb - 1] + vrg__chx
                    vdyv__vqb += 1
                    poen__daing += 1
                poen__daing += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(ptc__vqo,
                ttvag__gvdh, fts__yev, (ulxno__stkux, ajwq__vjhw))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        zca__xaxeo = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        zca__xaxeo += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo}, xmy__sovj)
        ediem__fre = xmy__sovj['impl_tuple']
        return ediem__fre
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    try:
        import bodosql
        from bodosql.context_ext import BodoSQLContextType
    except ImportError as fdcrk__sjg:
        BodoSQLContextType = None
    if BodoSQLContextType is not None and isinstance(data, BodoSQLContextType):
        zca__xaxeo = f"""def impl_bodosql_context(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        cjz__wurp = ', '.join([f"'{aooei__ypfw}'" for aooei__ypfw in data.
            names])
        pnua__vjwzp = ', '.join([
            f'bodo.gatherv(data.dataframes[{i}], allgather, warn_if_rep, root)'
             for i in range(len(data.dataframes))])
        zca__xaxeo += f"""  return bodosql.context_ext.init_sql_context(({cjz__wurp}, ), ({pnua__vjwzp}, ), data.catalog)
"""
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo, 'bodosql': bodosql}, xmy__sovj)
        kezp__ynpk = xmy__sovj['impl_bodosql_context']
        return kezp__ynpk
    try:
        import bodosql
        from bodosql import TablePathType
    except ImportError as fdcrk__sjg:
        TablePathType = None
    if TablePathType is not None and isinstance(data, TablePathType):
        zca__xaxeo = f"""def impl_table_path(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        zca__xaxeo += f'  return data\n'
        xmy__sovj = {}
        exec(zca__xaxeo, {}, xmy__sovj)
        rveq__mzgb = xmy__sovj['impl_table_path']
        return rveq__mzgb
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    zca__xaxeo = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    zca__xaxeo += '    if random:\n'
    zca__xaxeo += '        if random_seed is None:\n'
    zca__xaxeo += '            random = 1\n'
    zca__xaxeo += '        else:\n'
    zca__xaxeo += '            random = 2\n'
    zca__xaxeo += '    if random_seed is None:\n'
    zca__xaxeo += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        omznt__xhmuz = data
        ajwq__vjhw = len(omznt__xhmuz.columns)
        for i in range(ajwq__vjhw):
            zca__xaxeo += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        zca__xaxeo += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        hmrb__joyt = ', '.join(f'data_{i}' for i in range(ajwq__vjhw))
        zca__xaxeo += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(xogtm__bwveu) for
            xogtm__bwveu in range(ajwq__vjhw))))
        zca__xaxeo += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        zca__xaxeo += '    if dests is None:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zca__xaxeo += '    else:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for opm__lqgm in range(ajwq__vjhw):
            zca__xaxeo += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(opm__lqgm))
        zca__xaxeo += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(ajwq__vjhw))
        zca__xaxeo += '    delete_table(out_table)\n'
        zca__xaxeo += '    if parallel:\n'
        zca__xaxeo += '        delete_table(table_total)\n'
        hmrb__joyt = ', '.join('out_arr_{}'.format(i) for i in range(
            ajwq__vjhw))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zca__xaxeo += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(hmrb__joyt, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        zca__xaxeo += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        zca__xaxeo += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        zca__xaxeo += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        zca__xaxeo += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        zca__xaxeo += '    if dests is None:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zca__xaxeo += '    else:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zca__xaxeo += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        zca__xaxeo += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        zca__xaxeo += '    delete_table(out_table)\n'
        zca__xaxeo += '    if parallel:\n'
        zca__xaxeo += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zca__xaxeo += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        zca__xaxeo += '    if not parallel:\n'
        zca__xaxeo += '        return data\n'
        zca__xaxeo += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zca__xaxeo += '    if dests is None:\n'
        zca__xaxeo += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zca__xaxeo += '    elif bodo.get_rank() not in dests:\n'
        zca__xaxeo += '        dim0_local_size = 0\n'
        zca__xaxeo += '    else:\n'
        zca__xaxeo += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        zca__xaxeo += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zca__xaxeo += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        zca__xaxeo += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        zca__xaxeo += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        zca__xaxeo += '    if dests is None:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zca__xaxeo += '    else:\n'
        zca__xaxeo += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zca__xaxeo += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        zca__xaxeo += '    delete_table(out_table)\n'
        zca__xaxeo += '    if parallel:\n'
        zca__xaxeo += '        delete_table(table_total)\n'
        zca__xaxeo += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    xmy__sovj = {}
    awu__lql = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        awu__lql.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(omznt__xhmuz.columns)})
    exec(zca__xaxeo, awu__lql, xmy__sovj)
    impl = xmy__sovj['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    zca__xaxeo = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        zca__xaxeo += '    if seed is None:\n'
        zca__xaxeo += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        zca__xaxeo += '    np.random.seed(seed)\n'
        zca__xaxeo += '    if not parallel:\n'
        zca__xaxeo += '        data = data.copy()\n'
        zca__xaxeo += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            zca__xaxeo += '        data = data[:n_samples]\n'
        zca__xaxeo += '        return data\n'
        zca__xaxeo += '    else:\n'
        zca__xaxeo += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zca__xaxeo += '        permutation = np.arange(dim0_global_size)\n'
        zca__xaxeo += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            zca__xaxeo += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            zca__xaxeo += '        n_samples = dim0_global_size\n'
        zca__xaxeo += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zca__xaxeo += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        zca__xaxeo += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zca__xaxeo += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        zca__xaxeo += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        zca__xaxeo += '        return output\n'
    else:
        zca__xaxeo += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            zca__xaxeo += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            zca__xaxeo += '    output = output[:local_n_samples]\n'
        zca__xaxeo += '    return output\n'
    xmy__sovj = {}
    exec(zca__xaxeo, {'np': np, 'bodo': bodo}, xmy__sovj)
    impl = xmy__sovj['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    phasf__bdr = np.empty(sendcounts_nulls.sum(), np.uint8)
    kdit__uxssg = 0
    jank__tejf = 0
    for rqoep__qxa in range(len(sendcounts)):
        zex__qeme = sendcounts[rqoep__qxa]
        rhj__ryn = sendcounts_nulls[rqoep__qxa]
        evmbd__qykw = phasf__bdr[kdit__uxssg:kdit__uxssg + rhj__ryn]
        for axrr__tqkqo in range(zex__qeme):
            set_bit_to_arr(evmbd__qykw, axrr__tqkqo, get_bit_bitmap(
                null_bitmap_ptr, jank__tejf))
            jank__tejf += 1
        kdit__uxssg += rhj__ryn
    return phasf__bdr


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    lqj__gdeb = MPI.COMM_WORLD
    data = lqj__gdeb.bcast(data, root)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    sepoy__fihyv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    spjit__vovti = (0,) * sepoy__fihyv

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        ujlgs__kmca = np.ascontiguousarray(data)
        qhymy__zvdy = data.ctypes
        qcblp__qzv = spjit__vovti
        if rank == MPI_ROOT:
            qcblp__qzv = ujlgs__kmca.shape
        qcblp__qzv = bcast_tuple(qcblp__qzv)
        fmyx__tzw = get_tuple_prod(qcblp__qzv[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            qcblp__qzv[0])
        send_counts *= fmyx__tzw
        nckok__bcqq = send_counts[rank]
        yzqvg__qdtc = np.empty(nckok__bcqq, dtype)
        vyh__wwvm = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(qhymy__zvdy, send_counts.ctypes, vyh__wwvm.ctypes,
            yzqvg__qdtc.ctypes, np.int32(nckok__bcqq), np.int32(typ_val))
        return yzqvg__qdtc.reshape((-1,) + qcblp__qzv[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == bodo.dict_str_arr_type:
        import pyarrow as pa
        return pa.array(['a'], type=pa.dictionary(pa.int32(), pa.string()))
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        dqvp__nzgp = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], dqvp__nzgp)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        aooei__ypfw = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=aooei__ypfw)
        jioq__fysdg = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(jioq__fysdg)
        return pd.Index(arr, name=aooei__ypfw)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        aooei__ypfw = _get_name_value_for_type(dtype.name_typ)
        rktk__laurb = tuple(_get_name_value_for_type(t) for t in dtype.
            names_typ)
        zvuu__pqq = tuple(get_value_for_type(t) for t in dtype.array_types)
        zvuu__pqq = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in zvuu__pqq)
        val = pd.MultiIndex.from_arrays(zvuu__pqq, names=rktk__laurb)
        val.name = aooei__ypfw
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        aooei__ypfw = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=aooei__ypfw)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        zvuu__pqq = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({aooei__ypfw: arr for aooei__ypfw, arr in zip(
            dtype.columns, zvuu__pqq)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        jioq__fysdg = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(jioq__fysdg[0],
            jioq__fysdg[0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if data in (string_array_type, binary_array_type):
        szd__tpdhd = np.int32(numba_to_c_type(types.int32))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            wtagy__ugis = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            wtagy__ugis = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zca__xaxeo = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {wtagy__ugis}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        xmy__sovj = dict()
        exec(zca__xaxeo, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            szd__tpdhd, 'char_typ_enum': jzxn__kqx, 'decode_if_dict_array':
            decode_if_dict_array}, xmy__sovj)
        impl = xmy__sovj['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        szd__tpdhd = np.int32(numba_to_c_type(types.int32))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            jfcu__rixf = bodo.libs.array_item_arr_ext.get_offsets(data)
            nsjg__wgc = bodo.libs.array_item_arr_ext.get_data(data)
            nsjg__wgc = nsjg__wgc[:jfcu__rixf[-1]]
            jzil__nxigm = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            iqmsm__bhh = bcast_scalar(len(data))
            uvgvu__lya = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                uvgvu__lya[i] = jfcu__rixf[i + 1] - jfcu__rixf[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                iqmsm__bhh)
            vyh__wwvm = bodo.ir.join.calc_disp(send_counts)
            spcao__ntda = np.empty(n_pes, np.int32)
            if rank == 0:
                jma__guh = 0
                for i in range(n_pes):
                    etnx__lvqlh = 0
                    for elbhm__gcjb in range(send_counts[i]):
                        etnx__lvqlh += uvgvu__lya[jma__guh]
                        jma__guh += 1
                    spcao__ntda[i] = etnx__lvqlh
            bcast(spcao__ntda)
            xcydq__mxfmt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xcydq__mxfmt[i] = send_counts[i] + 7 >> 3
            sglth__yreez = bodo.ir.join.calc_disp(xcydq__mxfmt)
            nckok__bcqq = send_counts[rank]
            ygk__vwv = np.empty(nckok__bcqq + 1, np_offset_type)
            uvm__gwcij = bodo.libs.distributed_api.scatterv_impl(nsjg__wgc,
                spcao__ntda)
            zwzn__drd = nckok__bcqq + 7 >> 3
            ssmyr__njce = np.empty(zwzn__drd, np.uint8)
            sada__zqw = np.empty(nckok__bcqq, np.uint32)
            c_scatterv(uvgvu__lya.ctypes, send_counts.ctypes, vyh__wwvm.
                ctypes, sada__zqw.ctypes, np.int32(nckok__bcqq), szd__tpdhd)
            convert_len_arr_to_offset(sada__zqw.ctypes, ygk__vwv.ctypes,
                nckok__bcqq)
            vry__ehys = get_scatter_null_bytes_buff(jzil__nxigm.ctypes,
                send_counts, xcydq__mxfmt)
            c_scatterv(vry__ehys.ctypes, xcydq__mxfmt.ctypes, sglth__yreez.
                ctypes, ssmyr__njce.ctypes, np.int32(zwzn__drd), jzxn__kqx)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                nckok__bcqq, uvm__gwcij, ygk__vwv, ssmyr__njce)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            lihxo__apqh = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            lihxo__apqh = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            lihxo__apqh = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            lihxo__apqh = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            ujlgs__kmca = data._data
            qfmaw__rhud = data._null_bitmap
            lfo__qvp = len(ujlgs__kmca)
            nsyfu__saaku = _scatterv_np(ujlgs__kmca, send_counts)
            iqmsm__bhh = bcast_scalar(lfo__qvp)
            vvjzk__itei = len(nsyfu__saaku) + 7 >> 3
            fekya__idrf = np.empty(vvjzk__itei, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                iqmsm__bhh)
            xcydq__mxfmt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xcydq__mxfmt[i] = send_counts[i] + 7 >> 3
            sglth__yreez = bodo.ir.join.calc_disp(xcydq__mxfmt)
            vry__ehys = get_scatter_null_bytes_buff(qfmaw__rhud.ctypes,
                send_counts, xcydq__mxfmt)
            c_scatterv(vry__ehys.ctypes, xcydq__mxfmt.ctypes, sglth__yreez.
                ctypes, fekya__idrf.ctypes, np.int32(vvjzk__itei), jzxn__kqx)
            return lihxo__apqh(nsyfu__saaku, fekya__idrf)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            rhr__qvuas = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            xshy__tnbv = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(rhr__qvuas,
                xshy__tnbv)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            fosx__amxf = data._start
            tva__ofmj = data._stop
            pxq__uofx = data._step
            aooei__ypfw = data._name
            aooei__ypfw = bcast_scalar(aooei__ypfw)
            fosx__amxf = bcast_scalar(fosx__amxf)
            tva__ofmj = bcast_scalar(tva__ofmj)
            pxq__uofx = bcast_scalar(pxq__uofx)
            xedf__cfes = bodo.libs.array_kernels.calc_nitems(fosx__amxf,
                tva__ofmj, pxq__uofx)
            chunk_start = bodo.libs.distributed_api.get_start(xedf__cfes,
                n_pes, rank)
            eua__sprfa = bodo.libs.distributed_api.get_node_portion(xedf__cfes,
                n_pes, rank)
            gayh__hhj = fosx__amxf + pxq__uofx * chunk_start
            ffqgg__lsv = fosx__amxf + pxq__uofx * (chunk_start + eua__sprfa)
            ffqgg__lsv = min(ffqgg__lsv, tva__ofmj)
            return bodo.hiframes.pd_index_ext.init_range_index(gayh__hhj,
                ffqgg__lsv, pxq__uofx, aooei__ypfw)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        ssuk__uttu = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            ujlgs__kmca = data._data
            aooei__ypfw = data._name
            aooei__ypfw = bcast_scalar(aooei__ypfw)
            arr = bodo.libs.distributed_api.scatterv_impl(ujlgs__kmca,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                aooei__ypfw, ssuk__uttu)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            ujlgs__kmca = data._data
            aooei__ypfw = data._name
            aooei__ypfw = bcast_scalar(aooei__ypfw)
            arr = bodo.libs.distributed_api.scatterv_impl(ujlgs__kmca,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, aooei__ypfw)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            ptc__vqo = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            aooei__ypfw = bcast_scalar(data._name)
            rktk__laurb = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(ptc__vqo,
                rktk__laurb, aooei__ypfw)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            aooei__ypfw = bodo.hiframes.pd_series_ext.get_series_name(data)
            onbqa__qoepg = bcast_scalar(aooei__ypfw)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            inyng__qljb = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                inyng__qljb, onbqa__qoepg)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ajwq__vjhw = len(data.columns)
        nus__gionh = ColNamesMetaType(data.columns)
        zca__xaxeo = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        if data.is_table_format:
            zca__xaxeo += (
                '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            zca__xaxeo += """  g_table = bodo.libs.distributed_api.scatterv_impl(table, send_counts)
"""
            hmrb__joyt = 'g_table'
        else:
            for i in range(ajwq__vjhw):
                zca__xaxeo += f"""  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
                zca__xaxeo += f"""  g_data_{i} = bodo.libs.distributed_api.scatterv_impl(data_{i}, send_counts)
"""
            hmrb__joyt = ', '.join(f'g_data_{i}' for i in range(ajwq__vjhw))
        zca__xaxeo += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zca__xaxeo += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        zca__xaxeo += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({hmrb__joyt},), g_index, __col_name_meta_scaterv_impl)
"""
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            nus__gionh}, xmy__sovj)
        qupsr__xoa = xmy__sovj['impl_df']
        return qupsr__xoa
    if isinstance(data, bodo.TableType):
        zca__xaxeo = (
            'def impl_table(data, send_counts=None, warn_if_dist=True):\n')
        zca__xaxeo += '  T = data\n'
        zca__xaxeo += '  T2 = init_table(T, False)\n'
        zca__xaxeo += '  l = 0\n'
        awu__lql = {}
        for ztx__lvpei in data.type_to_blk.values():
            awu__lql[f'arr_inds_{ztx__lvpei}'] = np.array(data.
                block_to_arr_ind[ztx__lvpei], dtype=np.int64)
            zca__xaxeo += (
                f'  arr_list_{ztx__lvpei} = get_table_block(T, {ztx__lvpei})\n'
                )
            zca__xaxeo += f"""  out_arr_list_{ztx__lvpei} = alloc_list_like(arr_list_{ztx__lvpei}, len(arr_list_{ztx__lvpei}), False)
"""
            zca__xaxeo += f'  for i in range(len(arr_list_{ztx__lvpei})):\n'
            zca__xaxeo += (
                f'    arr_ind_{ztx__lvpei} = arr_inds_{ztx__lvpei}[i]\n')
            zca__xaxeo += f"""    ensure_column_unboxed(T, arr_list_{ztx__lvpei}, i, arr_ind_{ztx__lvpei})
"""
            zca__xaxeo += f"""    out_arr_{ztx__lvpei} = bodo.libs.distributed_api.scatterv_impl(arr_list_{ztx__lvpei}[i], send_counts)
"""
            zca__xaxeo += (
                f'    out_arr_list_{ztx__lvpei}[i] = out_arr_{ztx__lvpei}\n')
            zca__xaxeo += f'    l = len(out_arr_{ztx__lvpei})\n'
            zca__xaxeo += (
                f'  T2 = set_table_block(T2, out_arr_list_{ztx__lvpei}, {ztx__lvpei})\n'
                )
        zca__xaxeo += f'  T2 = set_table_len(T2, l)\n'
        zca__xaxeo += f'  return T2\n'
        awu__lql.update({'bodo': bodo, 'init_table': bodo.hiframes.table.
            init_table, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like})
        xmy__sovj = {}
        exec(zca__xaxeo, awu__lql, xmy__sovj)
        return xmy__sovj['impl_table']
    if data == bodo.dict_str_arr_type:

        def impl_dict_arr(data, send_counts=None, warn_if_dist=True):
            if bodo.get_rank() == 0:
                hphai__xpp = data._data
                bodo.libs.distributed_api.bcast_scalar(len(hphai__xpp))
                bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.libs.
                    str_arr_ext.num_total_chars(hphai__xpp)))
            else:
                vvtq__dbe = bodo.libs.distributed_api.bcast_scalar(0)
                zojyx__frmds = bodo.libs.distributed_api.bcast_scalar(0)
                hphai__xpp = bodo.libs.str_arr_ext.pre_alloc_string_array(
                    vvtq__dbe, zojyx__frmds)
            bodo.libs.distributed_api.bcast(hphai__xpp)
            yoth__ngq = bodo.libs.distributed_api.scatterv_impl(data.
                _indices, send_counts)
            return bodo.libs.dict_arr_ext.init_dict_arr(hphai__xpp,
                yoth__ngq, True)
        return impl_dict_arr
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            kios__igdlm = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                kios__igdlm, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        zca__xaxeo = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        zca__xaxeo += '  return ({}{})\n'.format(', '.join(
            f'bodo.libs.distributed_api.scatterv_impl(data[{i}], send_counts)'
             for i in range(len(data))), ',' if len(data) > 0 else '')
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo}, xmy__sovj)
        ediem__fre = xmy__sovj['impl_tuple']
        return ediem__fre
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data, root=MPI_ROOT):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data, root=MPI_ROOT):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.bcast()')
    if isinstance(data, types.Array):

        def bcast_impl(data, root=MPI_ROOT):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0, np.int32(root))
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data, root=MPI_ROOT):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0, np.int32(root))
            bcast(data._null_bitmap, root)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data, root=MPI_ROOT):
            bcast(data._data, root)
            bcast(data._null_bitmap, root)
            return
        return bcast_impl_int_arr
    if is_str_arr_type(data) or data == binary_array_type:
        zfys__iiu = np.int32(numba_to_c_type(offset_type))
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            nckok__bcqq = len(data)
            qmc__pcjsy = num_total_chars(data)
            assert nckok__bcqq < INT_MAX
            assert qmc__pcjsy < INT_MAX
            rrb__gwt = get_offset_ptr(data)
            qhymy__zvdy = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            rhj__ryn = nckok__bcqq + 7 >> 3
            c_bcast(rrb__gwt, np.int32(nckok__bcqq + 1), zfys__iiu, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(qhymy__zvdy, np.int32(qmc__pcjsy), jzxn__kqx, np.array(
                [-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(rhj__ryn), jzxn__kqx, np.
                array([-1]).ctypes, 0, np.int32(root))
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def bcast_scalar(val, root=MPI_ROOT):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise BodoError(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val, root=MPI_ROOT: None
    if val == bodo.string_type:
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                xba__bcor = 0
                qcpz__zgm = np.empty(0, np.uint8).ctypes
            else:
                qcpz__zgm, xba__bcor = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            xba__bcor = bodo.libs.distributed_api.bcast_scalar(xba__bcor, root)
            if rank != root:
                zpj__fmc = np.empty(xba__bcor + 1, np.uint8)
                zpj__fmc[xba__bcor] = 0
                qcpz__zgm = zpj__fmc.ctypes
            c_bcast(qcpz__zgm, np.int32(xba__bcor), jzxn__kqx, np.array([-1
                ]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(qcpz__zgm, xba__bcor)
        return impl_str
    typ_val = numba_to_c_type(val)
    zca__xaxeo = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    xmy__sovj = {}
    exec(zca__xaxeo, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, xmy__sovj)
    chu__uodjf = xmy__sovj['bcast_scalar_impl']
    return chu__uodjf


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    jif__cmg = len(val)
    zca__xaxeo = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    zca__xaxeo += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(jif__cmg)), 
        ',' if jif__cmg else '')
    xmy__sovj = {}
    exec(zca__xaxeo, {'bcast_scalar': bcast_scalar}, xmy__sovj)
    ragg__ogri = xmy__sovj['bcast_tuple_impl']
    return ragg__ogri


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nckok__bcqq = bcast_scalar(len(arr), root)
            fak__clms = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(nckok__bcqq, fak__clms)
            return arr
        return prealloc_impl
    return lambda arr, root=MPI_ROOT: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):
    if not idx.has_step:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            gayh__hhj = max(arr_start, slice_index.start) - arr_start
            ffqgg__lsv = max(slice_index.stop - arr_start, 0)
            return slice(gayh__hhj, ffqgg__lsv)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            fosx__amxf = slice_index.start
            pxq__uofx = slice_index.step
            vdqvd__coxk = (0 if pxq__uofx == 1 or fosx__amxf > arr_start else
                abs(pxq__uofx - arr_start % pxq__uofx) % pxq__uofx)
            gayh__hhj = max(arr_start, slice_index.start
                ) - arr_start + vdqvd__coxk
            ffqgg__lsv = max(slice_index.stop - arr_start, 0)
            return slice(gayh__hhj, ffqgg__lsv, pxq__uofx)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        fvkoc__cvn = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[fvkoc__cvn])
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if is_str_arr_type(arr) or arr == bodo.binary_array_type:
        qfma__cwig = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        jzxn__kqx = np.int32(numba_to_c_type(types.uint8))
        luzrx__ageu = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            gjo__mfv = np.int32(10)
            tag = np.int32(11)
            fmcf__epn = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                yzrsm__sbbr = arr._data
                pdo__qljg = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    yzrsm__sbbr, ind)
                ytnv__qtsmt = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    yzrsm__sbbr, ind + 1)
                length = ytnv__qtsmt - pdo__qljg
                anij__hyi = yzrsm__sbbr[ind]
                fmcf__epn[0] = length
                isend(fmcf__epn, np.int32(1), root, gjo__mfv, True)
                isend(anij__hyi, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                luzrx__ageu, qfma__cwig, 0, 1)
            vvtq__dbe = 0
            if rank == root:
                vvtq__dbe = recv(np.int64, ANY_SOURCE, gjo__mfv)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    luzrx__ageu, qfma__cwig, vvtq__dbe, 1)
                qhymy__zvdy = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(qhymy__zvdy, np.int32(vvtq__dbe), jzxn__kqx,
                    ANY_SOURCE, tag)
            dummy_use(fmcf__epn)
            vvtq__dbe = bcast_scalar(vvtq__dbe)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    luzrx__ageu, qfma__cwig, vvtq__dbe, 1)
            qhymy__zvdy = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(qhymy__zvdy, np.int32(vvtq__dbe), jzxn__kqx, np.array([
                -1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, vvtq__dbe)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        oxxzz__tuz = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, oxxzz__tuz)
            if arr_start <= ind < arr_start + len(arr):
                kios__igdlm = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = kios__igdlm[ind - arr_start]
                send_arr = np.full(1, data, oxxzz__tuz)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = oxxzz__tuz(-1)
            if rank == root:
                val = recv(oxxzz__tuz, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            dxdb__bzra = arr.dtype.categories[max(val, 0)]
            return dxdb__bzra
        return cat_getitem_impl
    eppgx__yxahf = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, eppgx__yxahf)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, eppgx__yxahf)[0]
        if rank == root:
            val = recv(eppgx__yxahf, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    jpdso__ugygt = get_type_enum(out_data)
    assert typ_enum == jpdso__ugygt
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    zca__xaxeo = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        zca__xaxeo += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    zca__xaxeo += '  return\n'
    xmy__sovj = {}
    exec(zca__xaxeo, {'alltoallv': alltoallv}, xmy__sovj)
    wrnm__dgz = xmy__sovj['f']
    return wrnm__dgz


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    fosx__amxf = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return fosx__amxf, count


@numba.njit
def get_start(total_size, pes, rank):
    rxu__zhdkz = total_size % pes
    vod__avfi = (total_size - rxu__zhdkz) // pes
    return rank * vod__avfi + min(rank, rxu__zhdkz)


@numba.njit
def get_end(total_size, pes, rank):
    rxu__zhdkz = total_size % pes
    vod__avfi = (total_size - rxu__zhdkz) // pes
    return (rank + 1) * vod__avfi + min(rank + 1, rxu__zhdkz)


@numba.njit
def get_node_portion(total_size, pes, rank):
    rxu__zhdkz = total_size % pes
    vod__avfi = (total_size - rxu__zhdkz) // pes
    if rank < rxu__zhdkz:
        return vod__avfi + 1
    else:
        return vod__avfi


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    amv__zgz = in_arr.dtype(0)
    qigja__zvx = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        etnx__lvqlh = amv__zgz
        for vqrma__ejrm in np.nditer(in_arr):
            etnx__lvqlh += vqrma__ejrm.item()
        fbpbj__mgm = dist_exscan(etnx__lvqlh, qigja__zvx)
        for i in range(in_arr.size):
            fbpbj__mgm += in_arr[i]
            out_arr[i] = fbpbj__mgm
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    gjl__glb = in_arr.dtype(1)
    qigja__zvx = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        etnx__lvqlh = gjl__glb
        for vqrma__ejrm in np.nditer(in_arr):
            etnx__lvqlh *= vqrma__ejrm.item()
        fbpbj__mgm = dist_exscan(etnx__lvqlh, qigja__zvx)
        if get_rank() == 0:
            fbpbj__mgm = gjl__glb
        for i in range(in_arr.size):
            fbpbj__mgm *= in_arr[i]
            out_arr[i] = fbpbj__mgm
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        gjl__glb = np.finfo(in_arr.dtype(1).dtype).max
    else:
        gjl__glb = np.iinfo(in_arr.dtype(1).dtype).max
    qigja__zvx = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        etnx__lvqlh = gjl__glb
        for vqrma__ejrm in np.nditer(in_arr):
            etnx__lvqlh = min(etnx__lvqlh, vqrma__ejrm.item())
        fbpbj__mgm = dist_exscan(etnx__lvqlh, qigja__zvx)
        if get_rank() == 0:
            fbpbj__mgm = gjl__glb
        for i in range(in_arr.size):
            fbpbj__mgm = min(fbpbj__mgm, in_arr[i])
            out_arr[i] = fbpbj__mgm
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        gjl__glb = np.finfo(in_arr.dtype(1).dtype).min
    else:
        gjl__glb = np.iinfo(in_arr.dtype(1).dtype).min
    gjl__glb = in_arr.dtype(1)
    qigja__zvx = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        etnx__lvqlh = gjl__glb
        for vqrma__ejrm in np.nditer(in_arr):
            etnx__lvqlh = max(etnx__lvqlh, vqrma__ejrm.item())
        fbpbj__mgm = dist_exscan(etnx__lvqlh, qigja__zvx)
        if get_rank() == 0:
            fbpbj__mgm = gjl__glb
        for i in range(in_arr.size):
            fbpbj__mgm = max(fbpbj__mgm, in_arr[i])
            out_arr[i] = fbpbj__mgm
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    hooun__fgbg = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), hooun__fgbg)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lvvn__xnx = args[0]
    if equiv_set.has_shape(lvvn__xnx):
        return ArrayAnalysis.AnalyzeResult(shape=lvvn__xnx, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)
ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_rep_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
@infer_global(rep_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


def print_if_not_empty(args):
    pass


@overload(print_if_not_empty)
def overload_print_if_not_empty(*args):
    ysqzh__nisbr = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, jeo__qujyb in enumerate(args) if is_array_typ(jeo__qujyb) or
        isinstance(jeo__qujyb, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    zca__xaxeo = f"""def impl(*args):
    if {ysqzh__nisbr} or bodo.get_rank() == 0:
        print(*args)"""
    xmy__sovj = {}
    exec(zca__xaxeo, globals(), xmy__sovj)
    impl = xmy__sovj['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        btg__dgiu = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        zca__xaxeo = 'def f(req, cond=True):\n'
        zca__xaxeo += f'  return {btg__dgiu}\n'
        xmy__sovj = {}
        exec(zca__xaxeo, {'_wait': _wait}, xmy__sovj)
        impl = xmy__sovj['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        rxu__zhdkz = 1
        for a in t:
            rxu__zhdkz *= a
        return rxu__zhdkz
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    blv__fcpk = np.ascontiguousarray(in_arr)
    vmwpg__fucrf = get_tuple_prod(blv__fcpk.shape[1:])
    dxs__cmfaq = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        jib__eqt = np.array(dest_ranks, dtype=np.int32)
    else:
        jib__eqt = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, blv__fcpk.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * dxs__cmfaq, dtype_size * vmwpg__fucrf,
        len(jib__eqt), jib__eqt.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp, types.int64))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len,
    n_samples):
    znd__jbj = np.ascontiguousarray(rhs)
    piwf__ygk = get_tuple_prod(znd__jbj.shape[1:])
    axmx__isp = dtype_size * piwf__ygk
    permutation_array_index(lhs.ctypes, lhs_len, axmx__isp, znd__jbj.ctypes,
        znd__jbj.shape[0], p.ctypes, p_len, n_samples)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks, root=MPI_ROOT):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype, root)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks, root)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks, root=MPI_ROOT):
    return lambda data, comm_ranks, nranks, root=MPI_ROOT: bcast_comm_impl(data
        , comm_ranks, nranks, root)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks, root=MPI_ROOT):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        zca__xaxeo = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, xmy__sovj)
        chu__uodjf = xmy__sovj['bcast_scalar_impl']
        return chu__uodjf
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ajwq__vjhw = len(data.columns)
        hmrb__joyt = ', '.join('g_data_{}'.format(i) for i in range(ajwq__vjhw)
            )
        vpytz__clks = ColNamesMetaType(data.columns)
        zca__xaxeo = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(ajwq__vjhw):
            zca__xaxeo += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            zca__xaxeo += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        zca__xaxeo += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zca__xaxeo += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        zca__xaxeo += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(hmrb__joyt))
        xmy__sovj = {}
        exec(zca__xaxeo, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            vpytz__clks}, xmy__sovj)
        qupsr__xoa = xmy__sovj['impl_df']
        return qupsr__xoa
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            fosx__amxf = data._start
            tva__ofmj = data._stop
            pxq__uofx = data._step
            aooei__ypfw = data._name
            aooei__ypfw = bcast_scalar(aooei__ypfw, root)
            fosx__amxf = bcast_scalar(fosx__amxf, root)
            tva__ofmj = bcast_scalar(tva__ofmj, root)
            pxq__uofx = bcast_scalar(pxq__uofx, root)
            xedf__cfes = bodo.libs.array_kernels.calc_nitems(fosx__amxf,
                tva__ofmj, pxq__uofx)
            chunk_start = bodo.libs.distributed_api.get_start(xedf__cfes,
                n_pes, rank)
            eua__sprfa = bodo.libs.distributed_api.get_node_portion(xedf__cfes,
                n_pes, rank)
            gayh__hhj = fosx__amxf + pxq__uofx * chunk_start
            ffqgg__lsv = fosx__amxf + pxq__uofx * (chunk_start + eua__sprfa)
            ffqgg__lsv = min(ffqgg__lsv, tva__ofmj)
            return bodo.hiframes.pd_index_ext.init_range_index(gayh__hhj,
                ffqgg__lsv, pxq__uofx, aooei__ypfw)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            ujlgs__kmca = data._data
            aooei__ypfw = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(ujlgs__kmca,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, aooei__ypfw)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            aooei__ypfw = bodo.hiframes.pd_series_ext.get_series_name(data)
            onbqa__qoepg = bodo.libs.distributed_api.bcast_comm_impl(
                aooei__ypfw, comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            inyng__qljb = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                inyng__qljb, onbqa__qoepg)
        return impl_series
    if isinstance(data, types.BaseTuple):
        zca__xaxeo = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        zca__xaxeo += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        xmy__sovj = {}
        exec(zca__xaxeo, {'bcast_comm_impl': bcast_comm_impl}, xmy__sovj)
        ediem__fre = xmy__sovj['impl_tuple']
        return ediem__fre
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    sepoy__fihyv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    spjit__vovti = (0,) * sepoy__fihyv

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        ujlgs__kmca = np.ascontiguousarray(data)
        qhymy__zvdy = data.ctypes
        qcblp__qzv = spjit__vovti
        if rank == root:
            qcblp__qzv = ujlgs__kmca.shape
        qcblp__qzv = bcast_tuple(qcblp__qzv, root)
        fmyx__tzw = get_tuple_prod(qcblp__qzv[1:])
        send_counts = qcblp__qzv[0] * fmyx__tzw
        yzqvg__qdtc = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(qhymy__zvdy, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(yzqvg__qdtc.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return yzqvg__qdtc.reshape((-1,) + qcblp__qzv[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        lqj__gdeb = MPI.COMM_WORLD
        kcga__zdnv = MPI.Get_processor_name()
        ahmu__oek = lqj__gdeb.allgather(kcga__zdnv)
        node_ranks = defaultdict(list)
        for i, akcxj__mqq in enumerate(ahmu__oek):
            node_ranks[akcxj__mqq].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    lqj__gdeb = MPI.COMM_WORLD
    fpz__bwyo = lqj__gdeb.Get_group()
    swla__fwclx = fpz__bwyo.Incl(comm_ranks)
    fxeo__ign = lqj__gdeb.Create_group(swla__fwclx)
    return fxeo__ign


def get_nodes_first_ranks():
    udoew__wgd = get_host_ranks()
    return np.array([jbh__bvqz[0] for jbh__bvqz in udoew__wgd.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
