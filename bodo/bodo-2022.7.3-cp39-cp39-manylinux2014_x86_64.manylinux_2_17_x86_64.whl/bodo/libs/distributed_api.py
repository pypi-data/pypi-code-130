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
    guwnr__urkwj = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, guwnr__urkwj, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    guwnr__urkwj = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, guwnr__urkwj, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            guwnr__urkwj = get_type_enum(arr)
            return _isend(arr.ctypes, size, guwnr__urkwj, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        guwnr__urkwj = np.int32(numba_to_c_type(arr.dtype))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            qsu__tterw = size + 7 >> 3
            pcl__anzg = _isend(arr._data.ctypes, size, guwnr__urkwj, pe,
                tag, cond)
            gsh__xuhql = _isend(arr._null_bitmap.ctypes, qsu__tterw,
                yyq__zrrg, pe, tag, cond)
            return pcl__anzg, gsh__xuhql
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        xbsnl__axrq = np.int32(numba_to_c_type(offset_type))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            rafn__jiqcq = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(rafn__jiqcq, pe, tag - 1)
            qsu__tterw = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                xbsnl__axrq, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), rafn__jiqcq,
                yyq__zrrg, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                qsu__tterw, yyq__zrrg, pe, tag)
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
            guwnr__urkwj = get_type_enum(arr)
            return _irecv(arr.ctypes, size, guwnr__urkwj, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        guwnr__urkwj = np.int32(numba_to_c_type(arr.dtype))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            qsu__tterw = size + 7 >> 3
            pcl__anzg = _irecv(arr._data.ctypes, size, guwnr__urkwj, pe,
                tag, cond)
            gsh__xuhql = _irecv(arr._null_bitmap.ctypes, qsu__tterw,
                yyq__zrrg, pe, tag, cond)
            return pcl__anzg, gsh__xuhql
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        xbsnl__axrq = np.int32(numba_to_c_type(offset_type))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            rgcza__ztpy = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rgcza__ztpy = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        blhcx__mxg = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {rgcza__ztpy}(size, n_chars)
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
        dxmbf__snnsm = dict()
        exec(blhcx__mxg, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            xbsnl__axrq, 'char_typ_enum': yyq__zrrg}, dxmbf__snnsm)
        impl = dxmbf__snnsm['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    guwnr__urkwj = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), guwnr__urkwj)


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
        stv__ihuin = n_pes if rank == root or allgather else 0
        ucdf__qcqk = np.empty(stv__ihuin, dtype)
        c_gather_scalar(send.ctypes, ucdf__qcqk.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return ucdf__qcqk
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
        fxqyu__cyz = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], fxqyu__cyz)
        return builder.bitcast(fxqyu__cyz, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        fxqyu__cyz = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(fxqyu__cyz)
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
    ijzo__yhl = types.unliteral(value)
    if isinstance(ijzo__yhl, IndexValueType):
        ijzo__yhl = ijzo__yhl.val_typ
        cdi__vzrw = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            cdi__vzrw.append(types.int64)
            cdi__vzrw.append(bodo.datetime64ns)
            cdi__vzrw.append(bodo.timedelta64ns)
            cdi__vzrw.append(bodo.datetime_date_type)
        if ijzo__yhl not in cdi__vzrw:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(ijzo__yhl))
    typ_enum = np.int32(numba_to_c_type(ijzo__yhl))

    def impl(value, reduce_op):
        etgu__cehg = value_to_ptr(value)
        yrrd__uxvl = value_to_ptr(value)
        _dist_reduce(etgu__cehg, yrrd__uxvl, reduce_op, typ_enum)
        return load_val_ptr(yrrd__uxvl, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    ijzo__yhl = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(ijzo__yhl))
    ttmc__yrx = ijzo__yhl(0)

    def impl(value, reduce_op):
        etgu__cehg = value_to_ptr(value)
        yrrd__uxvl = value_to_ptr(ttmc__yrx)
        _dist_exscan(etgu__cehg, yrrd__uxvl, reduce_op, typ_enum)
        return load_val_ptr(yrrd__uxvl, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    ibmd__uot = 0
    lkh__baanl = 0
    for i in range(len(recv_counts)):
        ynuqy__smym = recv_counts[i]
        qsu__tterw = recv_counts_nulls[i]
        wbfr__gvuby = tmp_null_bytes[ibmd__uot:ibmd__uot + qsu__tterw]
        for spdt__vmus in range(ynuqy__smym):
            set_bit_to(null_bitmap_ptr, lkh__baanl, get_bit(wbfr__gvuby,
                spdt__vmus))
            lkh__baanl += 1
        ibmd__uot += qsu__tterw


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            glxjt__vrxeh = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                glxjt__vrxeh, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            muwxt__glgy = data.size
            recv_counts = gather_scalar(np.int32(muwxt__glgy), allgather,
                root=root)
            gwbg__exqk = recv_counts.sum()
            wsac__axnh = empty_like_type(gwbg__exqk, data)
            kkviq__yjy = np.empty(1, np.int32)
            if rank == root or allgather:
                kkviq__yjy = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(muwxt__glgy), wsac__axnh.ctypes,
                recv_counts.ctypes, kkviq__yjy.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return wsac__axnh.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            wsac__axnh = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(wsac__axnh)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            wsac__axnh = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(wsac__axnh)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            muwxt__glgy = len(data)
            qsu__tterw = muwxt__glgy + 7 >> 3
            recv_counts = gather_scalar(np.int32(muwxt__glgy), allgather,
                root=root)
            gwbg__exqk = recv_counts.sum()
            wsac__axnh = empty_like_type(gwbg__exqk, data)
            kkviq__yjy = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sykf__mekc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kkviq__yjy = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sykf__mekc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(muwxt__glgy),
                wsac__axnh._days_data.ctypes, recv_counts.ctypes,
                kkviq__yjy.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(muwxt__glgy),
                wsac__axnh._seconds_data.ctypes, recv_counts.ctypes,
                kkviq__yjy.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(muwxt__glgy),
                wsac__axnh._microseconds_data.ctypes, recv_counts.ctypes,
                kkviq__yjy.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(qsu__tterw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, sykf__mekc
                .ctypes, yyq__zrrg, allgather, np.int32(root))
            copy_gathered_null_bytes(wsac__axnh._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return wsac__axnh
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            muwxt__glgy = len(data)
            qsu__tterw = muwxt__glgy + 7 >> 3
            recv_counts = gather_scalar(np.int32(muwxt__glgy), allgather,
                root=root)
            gwbg__exqk = recv_counts.sum()
            wsac__axnh = empty_like_type(gwbg__exqk, data)
            kkviq__yjy = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sykf__mekc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kkviq__yjy = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sykf__mekc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(muwxt__glgy), wsac__axnh.
                _data.ctypes, recv_counts.ctypes, kkviq__yjy.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(qsu__tterw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, sykf__mekc
                .ctypes, yyq__zrrg, allgather, np.int32(root))
            copy_gathered_null_bytes(wsac__axnh._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return wsac__axnh
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        plyb__updrf = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            kvl__xfe = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                kvl__xfe, plyb__updrf)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            elal__kkan = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            shi__app = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(elal__kkan,
                shi__app)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            xwdns__xby = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            spps__fcuq = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                spps__fcuq, xwdns__xby)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        vlv__yqd = np.iinfo(np.int64).max
        ibgih__ypup = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            gca__jtrd = data._start
            pyq__mzsyu = data._stop
            if len(data) == 0:
                gca__jtrd = vlv__yqd
                pyq__mzsyu = ibgih__ypup
            gca__jtrd = bodo.libs.distributed_api.dist_reduce(gca__jtrd, np
                .int32(Reduce_Type.Min.value))
            pyq__mzsyu = bodo.libs.distributed_api.dist_reduce(pyq__mzsyu,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if gca__jtrd == vlv__yqd and pyq__mzsyu == ibgih__ypup:
                gca__jtrd = 0
                pyq__mzsyu = 0
            yfc__jifrh = max(0, -(-(pyq__mzsyu - gca__jtrd) // data._step))
            if yfc__jifrh < total_len:
                pyq__mzsyu = gca__jtrd + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                gca__jtrd = 0
                pyq__mzsyu = 0
            return bodo.hiframes.pd_index_ext.init_range_index(gca__jtrd,
                pyq__mzsyu, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            bafe__syj = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, bafe__syj)
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
            wsac__axnh = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(wsac__axnh
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        wtuct__fgj = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        blhcx__mxg = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        blhcx__mxg += '  T = data\n'
        blhcx__mxg += '  T2 = init_table(T, True)\n'
        for ssfis__tdhag in data.type_to_blk.values():
            wtuct__fgj[f'arr_inds_{ssfis__tdhag}'] = np.array(data.
                block_to_arr_ind[ssfis__tdhag], dtype=np.int64)
            blhcx__mxg += (
                f'  arr_list_{ssfis__tdhag} = get_table_block(T, {ssfis__tdhag})\n'
                )
            blhcx__mxg += f"""  out_arr_list_{ssfis__tdhag} = alloc_list_like(arr_list_{ssfis__tdhag}, len(arr_list_{ssfis__tdhag}), True)
"""
            blhcx__mxg += f'  for i in range(len(arr_list_{ssfis__tdhag})):\n'
            blhcx__mxg += (
                f'    arr_ind_{ssfis__tdhag} = arr_inds_{ssfis__tdhag}[i]\n')
            blhcx__mxg += f"""    ensure_column_unboxed(T, arr_list_{ssfis__tdhag}, i, arr_ind_{ssfis__tdhag})
"""
            blhcx__mxg += f"""    out_arr_{ssfis__tdhag} = bodo.gatherv(arr_list_{ssfis__tdhag}[i], allgather, warn_if_rep, root)
"""
            blhcx__mxg += (
                f'    out_arr_list_{ssfis__tdhag}[i] = out_arr_{ssfis__tdhag}\n'
                )
            blhcx__mxg += f"""  T2 = set_table_block(T2, out_arr_list_{ssfis__tdhag}, {ssfis__tdhag})
"""
        blhcx__mxg += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        blhcx__mxg += f'  T2 = set_table_len(T2, length)\n'
        blhcx__mxg += f'  return T2\n'
        dxmbf__snnsm = {}
        exec(blhcx__mxg, wtuct__fgj, dxmbf__snnsm)
        swjky__aibgv = dxmbf__snnsm['impl_table']
        return swjky__aibgv
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        pab__bdr = len(data.columns)
        if pab__bdr == 0:
            xifi__hkd = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                ihrqc__foqji = bodo.gatherv(index, allgather, warn_if_rep, root
                    )
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    ihrqc__foqji, xifi__hkd)
            return impl
        nhan__lhq = ', '.join(f'g_data_{i}' for i in range(pab__bdr))
        blhcx__mxg = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            reha__mnl = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            nhan__lhq = 'T2'
            blhcx__mxg += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            blhcx__mxg += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(pab__bdr):
                blhcx__mxg += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                blhcx__mxg += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        blhcx__mxg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        blhcx__mxg += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        blhcx__mxg += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(nhan__lhq))
        dxmbf__snnsm = {}
        wtuct__fgj = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(blhcx__mxg, wtuct__fgj, dxmbf__snnsm)
        gnfwp__jap = dxmbf__snnsm['impl_df']
        return gnfwp__jap
    if isinstance(data, ArrayItemArrayType):
        lppvt__uvnta = np.int32(numba_to_c_type(types.int32))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            fqv__qkl = bodo.libs.array_item_arr_ext.get_offsets(data)
            wsc__zewyp = bodo.libs.array_item_arr_ext.get_data(data)
            wsc__zewyp = wsc__zewyp[:fqv__qkl[-1]]
            cjfw__dges = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            muwxt__glgy = len(data)
            tjdaw__tub = np.empty(muwxt__glgy, np.uint32)
            qsu__tterw = muwxt__glgy + 7 >> 3
            for i in range(muwxt__glgy):
                tjdaw__tub[i] = fqv__qkl[i + 1] - fqv__qkl[i]
            recv_counts = gather_scalar(np.int32(muwxt__glgy), allgather,
                root=root)
            gwbg__exqk = recv_counts.sum()
            kkviq__yjy = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sykf__mekc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kkviq__yjy = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for nft__dodf in range(len(recv_counts)):
                    recv_counts_nulls[nft__dodf] = recv_counts[nft__dodf
                        ] + 7 >> 3
                sykf__mekc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            mqut__pnd = np.empty(gwbg__exqk + 1, np.uint32)
            hfz__aqild = bodo.gatherv(wsc__zewyp, allgather, warn_if_rep, root)
            sfdrs__xcso = np.empty(gwbg__exqk + 7 >> 3, np.uint8)
            c_gatherv(tjdaw__tub.ctypes, np.int32(muwxt__glgy), mqut__pnd.
                ctypes, recv_counts.ctypes, kkviq__yjy.ctypes, lppvt__uvnta,
                allgather, np.int32(root))
            c_gatherv(cjfw__dges.ctypes, np.int32(qsu__tterw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, sykf__mekc
                .ctypes, yyq__zrrg, allgather, np.int32(root))
            dummy_use(data)
            ufcr__ahn = np.empty(gwbg__exqk + 1, np.uint64)
            convert_len_arr_to_offset(mqut__pnd.ctypes, ufcr__ahn.ctypes,
                gwbg__exqk)
            copy_gathered_null_bytes(sfdrs__xcso.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                gwbg__exqk, hfz__aqild, ufcr__ahn, sfdrs__xcso)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        bts__uqmmb = data.names
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ictn__aloe = bodo.libs.struct_arr_ext.get_data(data)
            fukvu__rvo = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            yhkv__wkv = bodo.gatherv(ictn__aloe, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            muwxt__glgy = len(data)
            qsu__tterw = muwxt__glgy + 7 >> 3
            recv_counts = gather_scalar(np.int32(muwxt__glgy), allgather,
                root=root)
            gwbg__exqk = recv_counts.sum()
            lklsy__vqft = np.empty(gwbg__exqk + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            sykf__mekc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sykf__mekc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(fukvu__rvo.ctypes, np.int32(qsu__tterw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, sykf__mekc
                .ctypes, yyq__zrrg, allgather, np.int32(root))
            copy_gathered_null_bytes(lklsy__vqft.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(yhkv__wkv,
                lklsy__vqft, bts__uqmmb)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            wsac__axnh = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(wsac__axnh)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            wsac__axnh = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(wsac__axnh)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            wsac__axnh = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(wsac__axnh)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            wsac__axnh = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            lat__omm = bodo.gatherv(data.indices, allgather, warn_if_rep, root)
            fotqe__foad = bodo.gatherv(data.indptr, allgather, warn_if_rep,
                root)
            qeo__neq = gather_scalar(data.shape[0], allgather, root=root)
            akznn__wqnu = qeo__neq.sum()
            pab__bdr = bodo.libs.distributed_api.dist_reduce(data.shape[1],
                np.int32(Reduce_Type.Max.value))
            cewxm__xni = np.empty(akznn__wqnu + 1, np.int64)
            lat__omm = lat__omm.astype(np.int64)
            cewxm__xni[0] = 0
            rnp__rgqnz = 1
            bwns__mjz = 0
            for vzclq__kfs in qeo__neq:
                for thskb__cdd in range(vzclq__kfs):
                    eyo__lgkw = fotqe__foad[bwns__mjz + 1] - fotqe__foad[
                        bwns__mjz]
                    cewxm__xni[rnp__rgqnz] = cewxm__xni[rnp__rgqnz - 1
                        ] + eyo__lgkw
                    rnp__rgqnz += 1
                    bwns__mjz += 1
                bwns__mjz += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(wsac__axnh,
                lat__omm, cewxm__xni, (akznn__wqnu, pab__bdr))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        blhcx__mxg = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        blhcx__mxg += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo}, dxmbf__snnsm)
        tuvg__xkst = dxmbf__snnsm['impl_tuple']
        return tuvg__xkst
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    try:
        import bodosql
        from bodosql.context_ext import BodoSQLContextType
    except ImportError as loglp__rcj:
        BodoSQLContextType = None
    if BodoSQLContextType is not None and isinstance(data, BodoSQLContextType):
        blhcx__mxg = f"""def impl_bodosql_context(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        jjis__lqd = ', '.join([f"'{xwdns__xby}'" for xwdns__xby in data.names])
        qjk__sbrfd = ', '.join([
            f'bodo.gatherv(data.dataframes[{i}], allgather, warn_if_rep, root)'
             for i in range(len(data.dataframes))])
        blhcx__mxg += f"""  return bodosql.context_ext.init_sql_context(({jjis__lqd}, ), ({qjk__sbrfd}, ))
"""
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo, 'bodosql': bodosql}, dxmbf__snnsm)
        hbkxw__zny = dxmbf__snnsm['impl_bodosql_context']
        return hbkxw__zny
    try:
        import bodosql
        from bodosql import TablePathType
    except ImportError as loglp__rcj:
        TablePathType = None
    if TablePathType is not None and isinstance(data, TablePathType):
        blhcx__mxg = f"""def impl_table_path(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        blhcx__mxg += f'  return data\n'
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {}, dxmbf__snnsm)
        mbfx__iazxm = dxmbf__snnsm['impl_table_path']
        return mbfx__iazxm
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    blhcx__mxg = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    blhcx__mxg += '    if random:\n'
    blhcx__mxg += '        if random_seed is None:\n'
    blhcx__mxg += '            random = 1\n'
    blhcx__mxg += '        else:\n'
    blhcx__mxg += '            random = 2\n'
    blhcx__mxg += '    if random_seed is None:\n'
    blhcx__mxg += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        vne__jwt = data
        pab__bdr = len(vne__jwt.columns)
        for i in range(pab__bdr):
            blhcx__mxg += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        blhcx__mxg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        nhan__lhq = ', '.join(f'data_{i}' for i in range(pab__bdr))
        blhcx__mxg += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(qgkxp__ulq) for
            qgkxp__ulq in range(pab__bdr))))
        blhcx__mxg += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        blhcx__mxg += '    if dests is None:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        blhcx__mxg += '    else:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for vel__mrva in range(pab__bdr):
            blhcx__mxg += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(vel__mrva))
        blhcx__mxg += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(pab__bdr))
        blhcx__mxg += '    delete_table(out_table)\n'
        blhcx__mxg += '    if parallel:\n'
        blhcx__mxg += '        delete_table(table_total)\n'
        nhan__lhq = ', '.join('out_arr_{}'.format(i) for i in range(pab__bdr))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        blhcx__mxg += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(nhan__lhq, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        blhcx__mxg += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        blhcx__mxg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        blhcx__mxg += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        blhcx__mxg += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        blhcx__mxg += '    if dests is None:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        blhcx__mxg += '    else:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        blhcx__mxg += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        blhcx__mxg += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        blhcx__mxg += '    delete_table(out_table)\n'
        blhcx__mxg += '    if parallel:\n'
        blhcx__mxg += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        blhcx__mxg += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        blhcx__mxg += '    if not parallel:\n'
        blhcx__mxg += '        return data\n'
        blhcx__mxg += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        blhcx__mxg += '    if dests is None:\n'
        blhcx__mxg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        blhcx__mxg += '    elif bodo.get_rank() not in dests:\n'
        blhcx__mxg += '        dim0_local_size = 0\n'
        blhcx__mxg += '    else:\n'
        blhcx__mxg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        blhcx__mxg += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        blhcx__mxg += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        blhcx__mxg += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        blhcx__mxg += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        blhcx__mxg += '    if dests is None:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        blhcx__mxg += '    else:\n'
        blhcx__mxg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        blhcx__mxg += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        blhcx__mxg += '    delete_table(out_table)\n'
        blhcx__mxg += '    if parallel:\n'
        blhcx__mxg += '        delete_table(table_total)\n'
        blhcx__mxg += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    dxmbf__snnsm = {}
    wtuct__fgj = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        wtuct__fgj.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(vne__jwt.columns)})
    exec(blhcx__mxg, wtuct__fgj, dxmbf__snnsm)
    impl = dxmbf__snnsm['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    blhcx__mxg = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        blhcx__mxg += '    if seed is None:\n'
        blhcx__mxg += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        blhcx__mxg += '    np.random.seed(seed)\n'
        blhcx__mxg += '    if not parallel:\n'
        blhcx__mxg += '        data = data.copy()\n'
        blhcx__mxg += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            blhcx__mxg += '        data = data[:n_samples]\n'
        blhcx__mxg += '        return data\n'
        blhcx__mxg += '    else:\n'
        blhcx__mxg += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        blhcx__mxg += '        permutation = np.arange(dim0_global_size)\n'
        blhcx__mxg += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            blhcx__mxg += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            blhcx__mxg += '        n_samples = dim0_global_size\n'
        blhcx__mxg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        blhcx__mxg += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        blhcx__mxg += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        blhcx__mxg += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        blhcx__mxg += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        blhcx__mxg += '        return output\n'
    else:
        blhcx__mxg += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            blhcx__mxg += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            blhcx__mxg += '    output = output[:local_n_samples]\n'
        blhcx__mxg += '    return output\n'
    dxmbf__snnsm = {}
    exec(blhcx__mxg, {'np': np, 'bodo': bodo}, dxmbf__snnsm)
    impl = dxmbf__snnsm['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    xplpg__vsvfe = np.empty(sendcounts_nulls.sum(), np.uint8)
    ibmd__uot = 0
    lkh__baanl = 0
    for uupn__yfdwi in range(len(sendcounts)):
        ynuqy__smym = sendcounts[uupn__yfdwi]
        qsu__tterw = sendcounts_nulls[uupn__yfdwi]
        wbfr__gvuby = xplpg__vsvfe[ibmd__uot:ibmd__uot + qsu__tterw]
        for spdt__vmus in range(ynuqy__smym):
            set_bit_to_arr(wbfr__gvuby, spdt__vmus, get_bit_bitmap(
                null_bitmap_ptr, lkh__baanl))
            lkh__baanl += 1
        ibmd__uot += qsu__tterw
    return xplpg__vsvfe


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    rfaj__pnu = MPI.COMM_WORLD
    data = rfaj__pnu.bcast(data, root)
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
    axbls__hxey = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    sfm__pkzd = (0,) * axbls__hxey

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        vuh__gmzl = np.ascontiguousarray(data)
        bljf__vkj = data.ctypes
        ryt__dlq = sfm__pkzd
        if rank == MPI_ROOT:
            ryt__dlq = vuh__gmzl.shape
        ryt__dlq = bcast_tuple(ryt__dlq)
        itizt__hkbty = get_tuple_prod(ryt__dlq[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes, ryt__dlq[0]
            )
        send_counts *= itizt__hkbty
        muwxt__glgy = send_counts[rank]
        eqkk__hzn = np.empty(muwxt__glgy, dtype)
        kkviq__yjy = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(bljf__vkj, send_counts.ctypes, kkviq__yjy.ctypes,
            eqkk__hzn.ctypes, np.int32(muwxt__glgy), np.int32(typ_val))
        return eqkk__hzn.reshape((-1,) + ryt__dlq[1:])
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
        nko__gpc = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], nko__gpc)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        xwdns__xby = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=xwdns__xby)
        qewyw__otp = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(qewyw__otp)
        return pd.Index(arr, name=xwdns__xby)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        xwdns__xby = _get_name_value_for_type(dtype.name_typ)
        bts__uqmmb = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        sayz__mmkp = tuple(get_value_for_type(t) for t in dtype.array_types)
        sayz__mmkp = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in sayz__mmkp)
        val = pd.MultiIndex.from_arrays(sayz__mmkp, names=bts__uqmmb)
        val.name = xwdns__xby
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        xwdns__xby = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=xwdns__xby)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        sayz__mmkp = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({xwdns__xby: arr for xwdns__xby, arr in zip(
            dtype.columns, sayz__mmkp)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        qewyw__otp = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(qewyw__otp[0],
            qewyw__otp[0])])
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
    if is_str_arr_type(data) or data == binary_array_type:
        lppvt__uvnta = np.int32(numba_to_c_type(types.int32))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            rgcza__ztpy = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rgcza__ztpy = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        blhcx__mxg = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            data = decode_if_dict_array(data)
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
            recv_arr = {rgcza__ztpy}(n_loc, n_loc_char)

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
        dxmbf__snnsm = dict()
        exec(blhcx__mxg, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            lppvt__uvnta, 'char_typ_enum': yyq__zrrg,
            'decode_if_dict_array': decode_if_dict_array}, dxmbf__snnsm)
        impl = dxmbf__snnsm['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        lppvt__uvnta = np.int32(numba_to_c_type(types.int32))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            iaffg__mqf = bodo.libs.array_item_arr_ext.get_offsets(data)
            cnd__pbh = bodo.libs.array_item_arr_ext.get_data(data)
            cnd__pbh = cnd__pbh[:iaffg__mqf[-1]]
            gfp__man = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            cyr__uipkr = bcast_scalar(len(data))
            hwfhi__povpb = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                hwfhi__povpb[i] = iaffg__mqf[i + 1] - iaffg__mqf[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                cyr__uipkr)
            kkviq__yjy = bodo.ir.join.calc_disp(send_counts)
            ocyi__ccj = np.empty(n_pes, np.int32)
            if rank == 0:
                gopd__kvdo = 0
                for i in range(n_pes):
                    naazs__muig = 0
                    for thskb__cdd in range(send_counts[i]):
                        naazs__muig += hwfhi__povpb[gopd__kvdo]
                        gopd__kvdo += 1
                    ocyi__ccj[i] = naazs__muig
            bcast(ocyi__ccj)
            ojhs__hynt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ojhs__hynt[i] = send_counts[i] + 7 >> 3
            sykf__mekc = bodo.ir.join.calc_disp(ojhs__hynt)
            muwxt__glgy = send_counts[rank]
            roa__ebpey = np.empty(muwxt__glgy + 1, np_offset_type)
            vtjjk__sqk = bodo.libs.distributed_api.scatterv_impl(cnd__pbh,
                ocyi__ccj)
            tqa__ydxx = muwxt__glgy + 7 >> 3
            esl__ibe = np.empty(tqa__ydxx, np.uint8)
            wtz__lzl = np.empty(muwxt__glgy, np.uint32)
            c_scatterv(hwfhi__povpb.ctypes, send_counts.ctypes, kkviq__yjy.
                ctypes, wtz__lzl.ctypes, np.int32(muwxt__glgy), lppvt__uvnta)
            convert_len_arr_to_offset(wtz__lzl.ctypes, roa__ebpey.ctypes,
                muwxt__glgy)
            yzy__upkxu = get_scatter_null_bytes_buff(gfp__man.ctypes,
                send_counts, ojhs__hynt)
            c_scatterv(yzy__upkxu.ctypes, ojhs__hynt.ctypes, sykf__mekc.
                ctypes, esl__ibe.ctypes, np.int32(tqa__ydxx), yyq__zrrg)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                muwxt__glgy, vtjjk__sqk, roa__ebpey, esl__ibe)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            zpg__qsqjw = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            zpg__qsqjw = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            zpg__qsqjw = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            zpg__qsqjw = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            vuh__gmzl = data._data
            fukvu__rvo = data._null_bitmap
            tmnb__ihixf = len(vuh__gmzl)
            zyib__drog = _scatterv_np(vuh__gmzl, send_counts)
            cyr__uipkr = bcast_scalar(tmnb__ihixf)
            iymff__xppi = len(zyib__drog) + 7 >> 3
            semnn__fapsy = np.empty(iymff__xppi, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                cyr__uipkr)
            ojhs__hynt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                ojhs__hynt[i] = send_counts[i] + 7 >> 3
            sykf__mekc = bodo.ir.join.calc_disp(ojhs__hynt)
            yzy__upkxu = get_scatter_null_bytes_buff(fukvu__rvo.ctypes,
                send_counts, ojhs__hynt)
            c_scatterv(yzy__upkxu.ctypes, ojhs__hynt.ctypes, sykf__mekc.
                ctypes, semnn__fapsy.ctypes, np.int32(iymff__xppi), yyq__zrrg)
            return zpg__qsqjw(zyib__drog, semnn__fapsy)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            hpcb__ktwcq = bodo.libs.distributed_api.scatterv_impl(data.
                _left, send_counts)
            tgl__nje = bodo.libs.distributed_api.scatterv_impl(data._right,
                send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(hpcb__ktwcq,
                tgl__nje)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            gca__jtrd = data._start
            pyq__mzsyu = data._stop
            daqc__tcn = data._step
            xwdns__xby = data._name
            xwdns__xby = bcast_scalar(xwdns__xby)
            gca__jtrd = bcast_scalar(gca__jtrd)
            pyq__mzsyu = bcast_scalar(pyq__mzsyu)
            daqc__tcn = bcast_scalar(daqc__tcn)
            yjn__nka = bodo.libs.array_kernels.calc_nitems(gca__jtrd,
                pyq__mzsyu, daqc__tcn)
            chunk_start = bodo.libs.distributed_api.get_start(yjn__nka,
                n_pes, rank)
            uqowg__ezqu = bodo.libs.distributed_api.get_node_portion(yjn__nka,
                n_pes, rank)
            jfe__jzt = gca__jtrd + daqc__tcn * chunk_start
            tke__qns = gca__jtrd + daqc__tcn * (chunk_start + uqowg__ezqu)
            tke__qns = min(tke__qns, pyq__mzsyu)
            return bodo.hiframes.pd_index_ext.init_range_index(jfe__jzt,
                tke__qns, daqc__tcn, xwdns__xby)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        bafe__syj = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            vuh__gmzl = data._data
            xwdns__xby = data._name
            xwdns__xby = bcast_scalar(xwdns__xby)
            arr = bodo.libs.distributed_api.scatterv_impl(vuh__gmzl,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                xwdns__xby, bafe__syj)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            vuh__gmzl = data._data
            xwdns__xby = data._name
            xwdns__xby = bcast_scalar(xwdns__xby)
            arr = bodo.libs.distributed_api.scatterv_impl(vuh__gmzl,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, xwdns__xby)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            wsac__axnh = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            xwdns__xby = bcast_scalar(data._name)
            bts__uqmmb = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(wsac__axnh
                , bts__uqmmb, xwdns__xby)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            xwdns__xby = bodo.hiframes.pd_series_ext.get_series_name(data)
            klmh__safum = bcast_scalar(xwdns__xby)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            spps__fcuq = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                spps__fcuq, klmh__safum)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        pab__bdr = len(data.columns)
        nhan__lhq = ', '.join('g_data_{}'.format(i) for i in range(pab__bdr))
        glnh__vfwrt = ColNamesMetaType(data.columns)
        blhcx__mxg = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(pab__bdr):
            blhcx__mxg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            blhcx__mxg += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        blhcx__mxg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        blhcx__mxg += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        blhcx__mxg += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({nhan__lhq},), g_index, __col_name_meta_scaterv_impl)
"""
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            glnh__vfwrt}, dxmbf__snnsm)
        gnfwp__jap = dxmbf__snnsm['impl_df']
        return gnfwp__jap
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            glxjt__vrxeh = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                glxjt__vrxeh, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        blhcx__mxg = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        blhcx__mxg += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo}, dxmbf__snnsm)
        tuvg__xkst = dxmbf__snnsm['impl_tuple']
        return tuvg__xkst
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
        xbsnl__axrq = np.int32(numba_to_c_type(offset_type))
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            muwxt__glgy = len(data)
            teem__ccl = num_total_chars(data)
            assert muwxt__glgy < INT_MAX
            assert teem__ccl < INT_MAX
            tlqt__gwca = get_offset_ptr(data)
            bljf__vkj = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            qsu__tterw = muwxt__glgy + 7 >> 3
            c_bcast(tlqt__gwca, np.int32(muwxt__glgy + 1), xbsnl__axrq, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(bljf__vkj, np.int32(teem__ccl), yyq__zrrg, np.array([-1
                ]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(qsu__tterw), yyq__zrrg, np.
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
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                cfuxx__xqiur = 0
                pdcrf__zodl = np.empty(0, np.uint8).ctypes
            else:
                pdcrf__zodl, cfuxx__xqiur = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            cfuxx__xqiur = bodo.libs.distributed_api.bcast_scalar(cfuxx__xqiur,
                root)
            if rank != root:
                jppfi__efwua = np.empty(cfuxx__xqiur + 1, np.uint8)
                jppfi__efwua[cfuxx__xqiur] = 0
                pdcrf__zodl = jppfi__efwua.ctypes
            c_bcast(pdcrf__zodl, np.int32(cfuxx__xqiur), yyq__zrrg, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(pdcrf__zodl, cfuxx__xqiur)
        return impl_str
    typ_val = numba_to_c_type(val)
    blhcx__mxg = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    dxmbf__snnsm = {}
    exec(blhcx__mxg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, dxmbf__snnsm)
    hjg__wazq = dxmbf__snnsm['bcast_scalar_impl']
    return hjg__wazq


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    qzc__syxpt = len(val)
    blhcx__mxg = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    blhcx__mxg += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(qzc__syxpt)),
        ',' if qzc__syxpt else '')
    dxmbf__snnsm = {}
    exec(blhcx__mxg, {'bcast_scalar': bcast_scalar}, dxmbf__snnsm)
    wxj__ehkah = dxmbf__snnsm['bcast_tuple_impl']
    return wxj__ehkah


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            muwxt__glgy = bcast_scalar(len(arr), root)
            ohquh__rch = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(muwxt__glgy, ohquh__rch)
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
            jfe__jzt = max(arr_start, slice_index.start) - arr_start
            tke__qns = max(slice_index.stop - arr_start, 0)
            return slice(jfe__jzt, tke__qns)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            gca__jtrd = slice_index.start
            daqc__tcn = slice_index.step
            xjixb__ddzev = (0 if daqc__tcn == 1 or gca__jtrd > arr_start else
                abs(daqc__tcn - arr_start % daqc__tcn) % daqc__tcn)
            jfe__jzt = max(arr_start, slice_index.start
                ) - arr_start + xjixb__ddzev
            tke__qns = max(slice_index.stop - arr_start, 0)
            return slice(jfe__jzt, tke__qns, daqc__tcn)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        zti__igv = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[zti__igv])
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
        fpfkv__osor = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        yyq__zrrg = np.int32(numba_to_c_type(types.uint8))
        ykdxj__ugj = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            fxqaa__yopeh = np.int32(10)
            tag = np.int32(11)
            aih__zgk = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                wsc__zewyp = arr._data
                ztt__lpbc = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wsc__zewyp, ind)
                nljj__vbsbs = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wsc__zewyp, ind + 1)
                length = nljj__vbsbs - ztt__lpbc
                fxqyu__cyz = wsc__zewyp[ind]
                aih__zgk[0] = length
                isend(aih__zgk, np.int32(1), root, fxqaa__yopeh, True)
                isend(fxqyu__cyz, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(ykdxj__ugj
                , fpfkv__osor, 0, 1)
            yfc__jifrh = 0
            if rank == root:
                yfc__jifrh = recv(np.int64, ANY_SOURCE, fxqaa__yopeh)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ykdxj__ugj, fpfkv__osor, yfc__jifrh, 1)
                bljf__vkj = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(bljf__vkj, np.int32(yfc__jifrh), yyq__zrrg,
                    ANY_SOURCE, tag)
            dummy_use(aih__zgk)
            yfc__jifrh = bcast_scalar(yfc__jifrh)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    ykdxj__ugj, fpfkv__osor, yfc__jifrh, 1)
            bljf__vkj = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(bljf__vkj, np.int32(yfc__jifrh), yyq__zrrg, np.array([-
                1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, yfc__jifrh)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        yrk__lbqnt = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, yrk__lbqnt)
            if arr_start <= ind < arr_start + len(arr):
                glxjt__vrxeh = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = glxjt__vrxeh[ind - arr_start]
                send_arr = np.full(1, data, yrk__lbqnt)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = yrk__lbqnt(-1)
            if rank == root:
                val = recv(yrk__lbqnt, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            kxr__myt = arr.dtype.categories[max(val, 0)]
            return kxr__myt
        return cat_getitem_impl
    tbe__lrvi = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, tbe__lrvi)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, tbe__lrvi)[0]
        if rank == root:
            val = recv(tbe__lrvi, ANY_SOURCE, tag)
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
    kcke__rodns = get_type_enum(out_data)
    assert typ_enum == kcke__rodns
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
    blhcx__mxg = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        blhcx__mxg += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    blhcx__mxg += '  return\n'
    dxmbf__snnsm = {}
    exec(blhcx__mxg, {'alltoallv': alltoallv}, dxmbf__snnsm)
    atnc__ssdl = dxmbf__snnsm['f']
    return atnc__ssdl


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    gca__jtrd = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return gca__jtrd, count


@numba.njit
def get_start(total_size, pes, rank):
    ucdf__qcqk = total_size % pes
    bck__atb = (total_size - ucdf__qcqk) // pes
    return rank * bck__atb + min(rank, ucdf__qcqk)


@numba.njit
def get_end(total_size, pes, rank):
    ucdf__qcqk = total_size % pes
    bck__atb = (total_size - ucdf__qcqk) // pes
    return (rank + 1) * bck__atb + min(rank + 1, ucdf__qcqk)


@numba.njit
def get_node_portion(total_size, pes, rank):
    ucdf__qcqk = total_size % pes
    bck__atb = (total_size - ucdf__qcqk) // pes
    if rank < ucdf__qcqk:
        return bck__atb + 1
    else:
        return bck__atb


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    ttmc__yrx = in_arr.dtype(0)
    huhrs__kwe = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        naazs__muig = ttmc__yrx
        for qkwtg__ifqln in np.nditer(in_arr):
            naazs__muig += qkwtg__ifqln.item()
        sgpv__wow = dist_exscan(naazs__muig, huhrs__kwe)
        for i in range(in_arr.size):
            sgpv__wow += in_arr[i]
            out_arr[i] = sgpv__wow
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    hts__uzkux = in_arr.dtype(1)
    huhrs__kwe = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        naazs__muig = hts__uzkux
        for qkwtg__ifqln in np.nditer(in_arr):
            naazs__muig *= qkwtg__ifqln.item()
        sgpv__wow = dist_exscan(naazs__muig, huhrs__kwe)
        if get_rank() == 0:
            sgpv__wow = hts__uzkux
        for i in range(in_arr.size):
            sgpv__wow *= in_arr[i]
            out_arr[i] = sgpv__wow
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        hts__uzkux = np.finfo(in_arr.dtype(1).dtype).max
    else:
        hts__uzkux = np.iinfo(in_arr.dtype(1).dtype).max
    huhrs__kwe = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        naazs__muig = hts__uzkux
        for qkwtg__ifqln in np.nditer(in_arr):
            naazs__muig = min(naazs__muig, qkwtg__ifqln.item())
        sgpv__wow = dist_exscan(naazs__muig, huhrs__kwe)
        if get_rank() == 0:
            sgpv__wow = hts__uzkux
        for i in range(in_arr.size):
            sgpv__wow = min(sgpv__wow, in_arr[i])
            out_arr[i] = sgpv__wow
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        hts__uzkux = np.finfo(in_arr.dtype(1).dtype).min
    else:
        hts__uzkux = np.iinfo(in_arr.dtype(1).dtype).min
    hts__uzkux = in_arr.dtype(1)
    huhrs__kwe = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        naazs__muig = hts__uzkux
        for qkwtg__ifqln in np.nditer(in_arr):
            naazs__muig = max(naazs__muig, qkwtg__ifqln.item())
        sgpv__wow = dist_exscan(naazs__muig, huhrs__kwe)
        if get_rank() == 0:
            sgpv__wow = hts__uzkux
        for i in range(in_arr.size):
            sgpv__wow = max(sgpv__wow, in_arr[i])
            out_arr[i] = sgpv__wow
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    guwnr__urkwj = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), guwnr__urkwj)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    hztx__erfeh = args[0]
    if equiv_set.has_shape(hztx__erfeh):
        return ArrayAnalysis.AnalyzeResult(shape=hztx__erfeh, pre=[])
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
    auiv__xsy = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for i,
        hrxc__dwdf in enumerate(args) if is_array_typ(hrxc__dwdf) or
        isinstance(hrxc__dwdf, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    blhcx__mxg = f"""def impl(*args):
    if {auiv__xsy} or bodo.get_rank() == 0:
        print(*args)"""
    dxmbf__snnsm = {}
    exec(blhcx__mxg, globals(), dxmbf__snnsm)
    impl = dxmbf__snnsm['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        aelt__eghr = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        blhcx__mxg = 'def f(req, cond=True):\n'
        blhcx__mxg += f'  return {aelt__eghr}\n'
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'_wait': _wait}, dxmbf__snnsm)
        impl = dxmbf__snnsm['f']
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
        ucdf__qcqk = 1
        for a in t:
            ucdf__qcqk *= a
        return ucdf__qcqk
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    juar__szkzl = np.ascontiguousarray(in_arr)
    ualy__wzgf = get_tuple_prod(juar__szkzl.shape[1:])
    xmd__ecb = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        txing__naz = np.array(dest_ranks, dtype=np.int32)
    else:
        txing__naz = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, juar__szkzl.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * xmd__ecb, dtype_size *
        ualy__wzgf, len(txing__naz), txing__naz.ctypes)
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
    apk__qyu = np.ascontiguousarray(rhs)
    lvlw__tdqnv = get_tuple_prod(apk__qyu.shape[1:])
    vijh__aphdj = dtype_size * lvlw__tdqnv
    permutation_array_index(lhs.ctypes, lhs_len, vijh__aphdj, apk__qyu.
        ctypes, apk__qyu.shape[0], p.ctypes, p_len, n_samples)
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
        blhcx__mxg = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, dxmbf__snnsm)
        hjg__wazq = dxmbf__snnsm['bcast_scalar_impl']
        return hjg__wazq
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        pab__bdr = len(data.columns)
        nhan__lhq = ', '.join('g_data_{}'.format(i) for i in range(pab__bdr))
        bljr__ull = ColNamesMetaType(data.columns)
        blhcx__mxg = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(pab__bdr):
            blhcx__mxg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            blhcx__mxg += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        blhcx__mxg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        blhcx__mxg += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        blhcx__mxg += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(nhan__lhq))
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            bljr__ull}, dxmbf__snnsm)
        gnfwp__jap = dxmbf__snnsm['impl_df']
        return gnfwp__jap
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            gca__jtrd = data._start
            pyq__mzsyu = data._stop
            daqc__tcn = data._step
            xwdns__xby = data._name
            xwdns__xby = bcast_scalar(xwdns__xby, root)
            gca__jtrd = bcast_scalar(gca__jtrd, root)
            pyq__mzsyu = bcast_scalar(pyq__mzsyu, root)
            daqc__tcn = bcast_scalar(daqc__tcn, root)
            yjn__nka = bodo.libs.array_kernels.calc_nitems(gca__jtrd,
                pyq__mzsyu, daqc__tcn)
            chunk_start = bodo.libs.distributed_api.get_start(yjn__nka,
                n_pes, rank)
            uqowg__ezqu = bodo.libs.distributed_api.get_node_portion(yjn__nka,
                n_pes, rank)
            jfe__jzt = gca__jtrd + daqc__tcn * chunk_start
            tke__qns = gca__jtrd + daqc__tcn * (chunk_start + uqowg__ezqu)
            tke__qns = min(tke__qns, pyq__mzsyu)
            return bodo.hiframes.pd_index_ext.init_range_index(jfe__jzt,
                tke__qns, daqc__tcn, xwdns__xby)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            vuh__gmzl = data._data
            xwdns__xby = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(vuh__gmzl,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, xwdns__xby)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            xwdns__xby = bodo.hiframes.pd_series_ext.get_series_name(data)
            klmh__safum = bodo.libs.distributed_api.bcast_comm_impl(xwdns__xby,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            spps__fcuq = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                spps__fcuq, klmh__safum)
        return impl_series
    if isinstance(data, types.BaseTuple):
        blhcx__mxg = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        blhcx__mxg += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        dxmbf__snnsm = {}
        exec(blhcx__mxg, {'bcast_comm_impl': bcast_comm_impl}, dxmbf__snnsm)
        tuvg__xkst = dxmbf__snnsm['impl_tuple']
        return tuvg__xkst
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    axbls__hxey = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    sfm__pkzd = (0,) * axbls__hxey

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        vuh__gmzl = np.ascontiguousarray(data)
        bljf__vkj = data.ctypes
        ryt__dlq = sfm__pkzd
        if rank == root:
            ryt__dlq = vuh__gmzl.shape
        ryt__dlq = bcast_tuple(ryt__dlq, root)
        itizt__hkbty = get_tuple_prod(ryt__dlq[1:])
        send_counts = ryt__dlq[0] * itizt__hkbty
        eqkk__hzn = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(bljf__vkj, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(eqkk__hzn.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return eqkk__hzn.reshape((-1,) + ryt__dlq[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        rfaj__pnu = MPI.COMM_WORLD
        bdedv__brinr = MPI.Get_processor_name()
        jqux__gjnmw = rfaj__pnu.allgather(bdedv__brinr)
        node_ranks = defaultdict(list)
        for i, hlp__utar in enumerate(jqux__gjnmw):
            node_ranks[hlp__utar].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    rfaj__pnu = MPI.COMM_WORLD
    nxhs__fzbhn = rfaj__pnu.Get_group()
    qikz__kuei = nxhs__fzbhn.Incl(comm_ranks)
    qjbs__etpoz = rfaj__pnu.Create_group(qikz__kuei)
    return qjbs__etpoz


def get_nodes_first_ranks():
    wlr__fcogo = get_host_ranks()
    return np.array([vms__fedor[0] for vms__fedor in wlr__fcogo.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
