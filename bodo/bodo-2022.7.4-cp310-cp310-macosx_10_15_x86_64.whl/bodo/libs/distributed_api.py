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
    fboqa__ooeoe = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, fboqa__ooeoe, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    fboqa__ooeoe = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, fboqa__ooeoe, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            fboqa__ooeoe = get_type_enum(arr)
            return _isend(arr.ctypes, size, fboqa__ooeoe, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        fboqa__ooeoe = np.int32(numba_to_c_type(arr.dtype))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            jci__dni = size + 7 >> 3
            rwnt__mzyrd = _isend(arr._data.ctypes, size, fboqa__ooeoe, pe,
                tag, cond)
            srse__clk = _isend(arr._null_bitmap.ctypes, jci__dni,
                ggk__bhopf, pe, tag, cond)
            return rwnt__mzyrd, srse__clk
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        jhatd__kadn = np.int32(numba_to_c_type(offset_type))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            aymxk__trf = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(aymxk__trf, pe, tag - 1)
            jci__dni = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                jhatd__kadn, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), aymxk__trf,
                ggk__bhopf, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), jci__dni,
                ggk__bhopf, pe, tag)
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
            fboqa__ooeoe = get_type_enum(arr)
            return _irecv(arr.ctypes, size, fboqa__ooeoe, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        fboqa__ooeoe = np.int32(numba_to_c_type(arr.dtype))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            jci__dni = size + 7 >> 3
            rwnt__mzyrd = _irecv(arr._data.ctypes, size, fboqa__ooeoe, pe,
                tag, cond)
            srse__clk = _irecv(arr._null_bitmap.ctypes, jci__dni,
                ggk__bhopf, pe, tag, cond)
            return rwnt__mzyrd, srse__clk
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        jhatd__kadn = np.int32(numba_to_c_type(offset_type))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            imlem__hdjxh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            imlem__hdjxh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        iylrb__ted = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {imlem__hdjxh}(size, n_chars)
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
        lpjsy__pivc = dict()
        exec(iylrb__ted, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            jhatd__kadn, 'char_typ_enum': ggk__bhopf}, lpjsy__pivc)
        impl = lpjsy__pivc['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    fboqa__ooeoe = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), fboqa__ooeoe)


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
        vluo__xwk = n_pes if rank == root or allgather else 0
        fds__bshdg = np.empty(vluo__xwk, dtype)
        c_gather_scalar(send.ctypes, fds__bshdg.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return fds__bshdg
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
        rhk__uagqq = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], rhk__uagqq)
        return builder.bitcast(rhk__uagqq, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        rhk__uagqq = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(rhk__uagqq)
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
    eybcy__hpdf = types.unliteral(value)
    if isinstance(eybcy__hpdf, IndexValueType):
        eybcy__hpdf = eybcy__hpdf.val_typ
        emgty__vac = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            emgty__vac.append(types.int64)
            emgty__vac.append(bodo.datetime64ns)
            emgty__vac.append(bodo.timedelta64ns)
            emgty__vac.append(bodo.datetime_date_type)
            emgty__vac.append(bodo.TimeType)
        if eybcy__hpdf not in emgty__vac:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(eybcy__hpdf))
    typ_enum = np.int32(numba_to_c_type(eybcy__hpdf))

    def impl(value, reduce_op):
        mvd__pqz = value_to_ptr(value)
        obb__bmi = value_to_ptr(value)
        _dist_reduce(mvd__pqz, obb__bmi, reduce_op, typ_enum)
        return load_val_ptr(obb__bmi, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    eybcy__hpdf = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(eybcy__hpdf))
    bdtm__jzxtu = eybcy__hpdf(0)

    def impl(value, reduce_op):
        mvd__pqz = value_to_ptr(value)
        obb__bmi = value_to_ptr(bdtm__jzxtu)
        _dist_exscan(mvd__pqz, obb__bmi, reduce_op, typ_enum)
        return load_val_ptr(obb__bmi, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    ifcui__ufb = 0
    euatz__nizu = 0
    for i in range(len(recv_counts)):
        yhg__ufl = recv_counts[i]
        jci__dni = recv_counts_nulls[i]
        uso__yzolc = tmp_null_bytes[ifcui__ufb:ifcui__ufb + jci__dni]
        for tfeh__uhu in range(yhg__ufl):
            set_bit_to(null_bitmap_ptr, euatz__nizu, get_bit(uso__yzolc,
                tfeh__uhu))
            euatz__nizu += 1
        ifcui__ufb += jci__dni


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            khyyu__sgl = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                khyyu__sgl, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            kded__iahk = data.size
            recv_counts = gather_scalar(np.int32(kded__iahk), allgather,
                root=root)
            uewv__paj = recv_counts.sum()
            eod__rmhw = empty_like_type(uewv__paj, data)
            kmju__gyj = np.empty(1, np.int32)
            if rank == root or allgather:
                kmju__gyj = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(kded__iahk), eod__rmhw.ctypes,
                recv_counts.ctypes, kmju__gyj.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return eod__rmhw.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            eod__rmhw = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(eod__rmhw)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            eod__rmhw = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(eod__rmhw)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            kded__iahk = len(data)
            jci__dni = kded__iahk + 7 >> 3
            recv_counts = gather_scalar(np.int32(kded__iahk), allgather,
                root=root)
            uewv__paj = recv_counts.sum()
            eod__rmhw = empty_like_type(uewv__paj, data)
            kmju__gyj = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            lwk__vbxj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kmju__gyj = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                lwk__vbxj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(kded__iahk),
                eod__rmhw._days_data.ctypes, recv_counts.ctypes, kmju__gyj.
                ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(kded__iahk),
                eod__rmhw._seconds_data.ctypes, recv_counts.ctypes,
                kmju__gyj.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(kded__iahk),
                eod__rmhw._microseconds_data.ctypes, recv_counts.ctypes,
                kmju__gyj.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(jci__dni),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, lwk__vbxj.
                ctypes, ggk__bhopf, allgather, np.int32(root))
            copy_gathered_null_bytes(eod__rmhw._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return eod__rmhw
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            kded__iahk = len(data)
            jci__dni = kded__iahk + 7 >> 3
            recv_counts = gather_scalar(np.int32(kded__iahk), allgather,
                root=root)
            uewv__paj = recv_counts.sum()
            eod__rmhw = empty_like_type(uewv__paj, data)
            kmju__gyj = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            lwk__vbxj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kmju__gyj = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                lwk__vbxj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(kded__iahk), eod__rmhw.
                _data.ctypes, recv_counts.ctypes, kmju__gyj.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(jci__dni),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, lwk__vbxj.
                ctypes, ggk__bhopf, allgather, np.int32(root))
            copy_gathered_null_bytes(eod__rmhw._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return eod__rmhw
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        evupd__ctw = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            qiapq__ulp = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                qiapq__ulp, evupd__ctw)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            gcy__hvv = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            prx__pzvm = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(gcy__hvv,
                prx__pzvm)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qzpub__pxtaq = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            etmp__sxt = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                etmp__sxt, qzpub__pxtaq)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        vxf__gutyx = np.iinfo(np.int64).max
        bgbfd__ndx = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vffxg__ibumq = data._start
            fhn__mokm = data._stop
            if len(data) == 0:
                vffxg__ibumq = vxf__gutyx
                fhn__mokm = bgbfd__ndx
            vffxg__ibumq = bodo.libs.distributed_api.dist_reduce(vffxg__ibumq,
                np.int32(Reduce_Type.Min.value))
            fhn__mokm = bodo.libs.distributed_api.dist_reduce(fhn__mokm, np
                .int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if vffxg__ibumq == vxf__gutyx and fhn__mokm == bgbfd__ndx:
                vffxg__ibumq = 0
                fhn__mokm = 0
            srnw__vpx = max(0, -(-(fhn__mokm - vffxg__ibumq) // data._step))
            if srnw__vpx < total_len:
                fhn__mokm = vffxg__ibumq + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                vffxg__ibumq = 0
                fhn__mokm = 0
            return bodo.hiframes.pd_index_ext.init_range_index(vffxg__ibumq,
                fhn__mokm, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            gqc__hibq = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, gqc__hibq)
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
            eod__rmhw = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(eod__rmhw,
                data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        djaeh__pisou = {'bodo': bodo, 'get_table_block': bodo.hiframes.
            table.get_table_block, 'ensure_column_unboxed': bodo.hiframes.
            table.ensure_column_unboxed, 'set_table_block': bodo.hiframes.
            table.set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        iylrb__ted = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        iylrb__ted += '  T = data\n'
        iylrb__ted += '  T2 = init_table(T, True)\n'
        for fqjs__qpw in data.type_to_blk.values():
            djaeh__pisou[f'arr_inds_{fqjs__qpw}'] = np.array(data.
                block_to_arr_ind[fqjs__qpw], dtype=np.int64)
            iylrb__ted += (
                f'  arr_list_{fqjs__qpw} = get_table_block(T, {fqjs__qpw})\n')
            iylrb__ted += f"""  out_arr_list_{fqjs__qpw} = alloc_list_like(arr_list_{fqjs__qpw}, len(arr_list_{fqjs__qpw}), True)
"""
            iylrb__ted += f'  for i in range(len(arr_list_{fqjs__qpw})):\n'
            iylrb__ted += (
                f'    arr_ind_{fqjs__qpw} = arr_inds_{fqjs__qpw}[i]\n')
            iylrb__ted += f"""    ensure_column_unboxed(T, arr_list_{fqjs__qpw}, i, arr_ind_{fqjs__qpw})
"""
            iylrb__ted += f"""    out_arr_{fqjs__qpw} = bodo.gatherv(arr_list_{fqjs__qpw}[i], allgather, warn_if_rep, root)
"""
            iylrb__ted += (
                f'    out_arr_list_{fqjs__qpw}[i] = out_arr_{fqjs__qpw}\n')
            iylrb__ted += (
                f'  T2 = set_table_block(T2, out_arr_list_{fqjs__qpw}, {fqjs__qpw})\n'
                )
        iylrb__ted += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        iylrb__ted += f'  T2 = set_table_len(T2, length)\n'
        iylrb__ted += f'  return T2\n'
        lpjsy__pivc = {}
        exec(iylrb__ted, djaeh__pisou, lpjsy__pivc)
        trc__ijjeg = lpjsy__pivc['impl_table']
        return trc__ijjeg
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        rrl__xxr = len(data.columns)
        if rrl__xxr == 0:
            huhs__yiqv = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                xullz__adovm = bodo.gatherv(index, allgather, warn_if_rep, root
                    )
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    xullz__adovm, huhs__yiqv)
            return impl
        yzwu__jpvy = ', '.join(f'g_data_{i}' for i in range(rrl__xxr))
        iylrb__ted = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            wox__aus = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            yzwu__jpvy = 'T2'
            iylrb__ted += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            iylrb__ted += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(rrl__xxr):
                iylrb__ted += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                iylrb__ted += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        iylrb__ted += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        iylrb__ted += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        iylrb__ted += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(yzwu__jpvy))
        lpjsy__pivc = {}
        djaeh__pisou = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(iylrb__ted, djaeh__pisou, lpjsy__pivc)
        yrf__eqoqc = lpjsy__pivc['impl_df']
        return yrf__eqoqc
    if isinstance(data, ArrayItemArrayType):
        zvyu__pyfe = np.int32(numba_to_c_type(types.int32))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            dngu__aqiy = bodo.libs.array_item_arr_ext.get_offsets(data)
            aegal__qbuxu = bodo.libs.array_item_arr_ext.get_data(data)
            aegal__qbuxu = aegal__qbuxu[:dngu__aqiy[-1]]
            ccsbz__ykezm = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            kded__iahk = len(data)
            gpzhu__mlldc = np.empty(kded__iahk, np.uint32)
            jci__dni = kded__iahk + 7 >> 3
            for i in range(kded__iahk):
                gpzhu__mlldc[i] = dngu__aqiy[i + 1] - dngu__aqiy[i]
            recv_counts = gather_scalar(np.int32(kded__iahk), allgather,
                root=root)
            uewv__paj = recv_counts.sum()
            kmju__gyj = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            lwk__vbxj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kmju__gyj = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for plrxn__nvrjr in range(len(recv_counts)):
                    recv_counts_nulls[plrxn__nvrjr] = recv_counts[plrxn__nvrjr
                        ] + 7 >> 3
                lwk__vbxj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            rhju__oalru = np.empty(uewv__paj + 1, np.uint32)
            jzkv__qoqdo = bodo.gatherv(aegal__qbuxu, allgather, warn_if_rep,
                root)
            alv__hzaop = np.empty(uewv__paj + 7 >> 3, np.uint8)
            c_gatherv(gpzhu__mlldc.ctypes, np.int32(kded__iahk),
                rhju__oalru.ctypes, recv_counts.ctypes, kmju__gyj.ctypes,
                zvyu__pyfe, allgather, np.int32(root))
            c_gatherv(ccsbz__ykezm.ctypes, np.int32(jci__dni),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, lwk__vbxj.
                ctypes, ggk__bhopf, allgather, np.int32(root))
            dummy_use(data)
            sohu__cbpc = np.empty(uewv__paj + 1, np.uint64)
            convert_len_arr_to_offset(rhju__oalru.ctypes, sohu__cbpc.ctypes,
                uewv__paj)
            copy_gathered_null_bytes(alv__hzaop.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                uewv__paj, jzkv__qoqdo, sohu__cbpc, alv__hzaop)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ncj__uurfs = data.names
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vfc__wjia = bodo.libs.struct_arr_ext.get_data(data)
            wqvp__cbhtu = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            ukjdt__cyq = bodo.gatherv(vfc__wjia, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            kded__iahk = len(data)
            jci__dni = kded__iahk + 7 >> 3
            recv_counts = gather_scalar(np.int32(kded__iahk), allgather,
                root=root)
            uewv__paj = recv_counts.sum()
            pudvy__jfd = np.empty(uewv__paj + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            lwk__vbxj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                lwk__vbxj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(wqvp__cbhtu.ctypes, np.int32(jci__dni),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, lwk__vbxj.
                ctypes, ggk__bhopf, allgather, np.int32(root))
            copy_gathered_null_bytes(pudvy__jfd.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(ukjdt__cyq,
                pudvy__jfd, ncj__uurfs)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            eod__rmhw = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(eod__rmhw)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            eod__rmhw = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(eod__rmhw)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            eod__rmhw = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(eod__rmhw)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            eod__rmhw = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            ubpil__irwls = bodo.gatherv(data.indices, allgather,
                warn_if_rep, root)
            uoouo__egh = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            hbu__yfnr = gather_scalar(data.shape[0], allgather, root=root)
            ccx__mdyd = hbu__yfnr.sum()
            rrl__xxr = bodo.libs.distributed_api.dist_reduce(data.shape[1],
                np.int32(Reduce_Type.Max.value))
            pgm__wvooa = np.empty(ccx__mdyd + 1, np.int64)
            ubpil__irwls = ubpil__irwls.astype(np.int64)
            pgm__wvooa[0] = 0
            wmkn__owt = 1
            mzgk__bzvaq = 0
            for xdllo__npqsz in hbu__yfnr:
                for tto__ytafb in range(xdllo__npqsz):
                    rigip__kmuhj = uoouo__egh[mzgk__bzvaq + 1] - uoouo__egh[
                        mzgk__bzvaq]
                    pgm__wvooa[wmkn__owt] = pgm__wvooa[wmkn__owt - 1
                        ] + rigip__kmuhj
                    wmkn__owt += 1
                    mzgk__bzvaq += 1
                mzgk__bzvaq += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(eod__rmhw,
                ubpil__irwls, pgm__wvooa, (ccx__mdyd, rrl__xxr))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        iylrb__ted = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        iylrb__ted += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo}, lpjsy__pivc)
        jctei__tzlj = lpjsy__pivc['impl_tuple']
        return jctei__tzlj
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    try:
        import bodosql
        from bodosql.context_ext import BodoSQLContextType
    except ImportError as kkhej__kur:
        BodoSQLContextType = None
    if BodoSQLContextType is not None and isinstance(data, BodoSQLContextType):
        iylrb__ted = f"""def impl_bodosql_context(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        gcy__dsw = ', '.join([f"'{qzpub__pxtaq}'" for qzpub__pxtaq in data.
            names])
        fdg__bxinv = ', '.join([
            f'bodo.gatherv(data.dataframes[{i}], allgather, warn_if_rep, root)'
             for i in range(len(data.dataframes))])
        iylrb__ted += f"""  return bodosql.context_ext.init_sql_context(({gcy__dsw}, ), ({fdg__bxinv}, ), data.catalog)
"""
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo, 'bodosql': bodosql}, lpjsy__pivc)
        srjl__lwch = lpjsy__pivc['impl_bodosql_context']
        return srjl__lwch
    try:
        import bodosql
        from bodosql import TablePathType
    except ImportError as kkhej__kur:
        TablePathType = None
    if TablePathType is not None and isinstance(data, TablePathType):
        iylrb__ted = f"""def impl_table_path(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        iylrb__ted += f'  return data\n'
        lpjsy__pivc = {}
        exec(iylrb__ted, {}, lpjsy__pivc)
        ruv__ixggu = lpjsy__pivc['impl_table_path']
        return ruv__ixggu
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    iylrb__ted = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    iylrb__ted += '    if random:\n'
    iylrb__ted += '        if random_seed is None:\n'
    iylrb__ted += '            random = 1\n'
    iylrb__ted += '        else:\n'
    iylrb__ted += '            random = 2\n'
    iylrb__ted += '    if random_seed is None:\n'
    iylrb__ted += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mvan__fzyb = data
        rrl__xxr = len(mvan__fzyb.columns)
        for i in range(rrl__xxr):
            iylrb__ted += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        iylrb__ted += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        yzwu__jpvy = ', '.join(f'data_{i}' for i in range(rrl__xxr))
        iylrb__ted += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(kxe__ntkei) for
            kxe__ntkei in range(rrl__xxr))))
        iylrb__ted += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        iylrb__ted += '    if dests is None:\n'
        iylrb__ted += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        iylrb__ted += '    else:\n'
        iylrb__ted += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for aim__unmvz in range(rrl__xxr):
            iylrb__ted += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(aim__unmvz))
        iylrb__ted += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(rrl__xxr))
        iylrb__ted += '    delete_table(out_table)\n'
        iylrb__ted += '    if parallel:\n'
        iylrb__ted += '        delete_table(table_total)\n'
        yzwu__jpvy = ', '.join('out_arr_{}'.format(i) for i in range(rrl__xxr))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        iylrb__ted += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(yzwu__jpvy, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        iylrb__ted += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        iylrb__ted += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        iylrb__ted += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        iylrb__ted += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        iylrb__ted += '    if dests is None:\n'
        iylrb__ted += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        iylrb__ted += '    else:\n'
        iylrb__ted += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        iylrb__ted += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        iylrb__ted += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        iylrb__ted += '    delete_table(out_table)\n'
        iylrb__ted += '    if parallel:\n'
        iylrb__ted += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        iylrb__ted += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        iylrb__ted += '    if not parallel:\n'
        iylrb__ted += '        return data\n'
        iylrb__ted += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        iylrb__ted += '    if dests is None:\n'
        iylrb__ted += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        iylrb__ted += '    elif bodo.get_rank() not in dests:\n'
        iylrb__ted += '        dim0_local_size = 0\n'
        iylrb__ted += '    else:\n'
        iylrb__ted += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        iylrb__ted += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        iylrb__ted += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        iylrb__ted += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        iylrb__ted += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        iylrb__ted += '    if dests is None:\n'
        iylrb__ted += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        iylrb__ted += '    else:\n'
        iylrb__ted += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        iylrb__ted += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        iylrb__ted += '    delete_table(out_table)\n'
        iylrb__ted += '    if parallel:\n'
        iylrb__ted += '        delete_table(table_total)\n'
        iylrb__ted += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    lpjsy__pivc = {}
    djaeh__pisou = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        djaeh__pisou.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(mvan__fzyb.columns)})
    exec(iylrb__ted, djaeh__pisou, lpjsy__pivc)
    impl = lpjsy__pivc['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    iylrb__ted = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        iylrb__ted += '    if seed is None:\n'
        iylrb__ted += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        iylrb__ted += '    np.random.seed(seed)\n'
        iylrb__ted += '    if not parallel:\n'
        iylrb__ted += '        data = data.copy()\n'
        iylrb__ted += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            iylrb__ted += '        data = data[:n_samples]\n'
        iylrb__ted += '        return data\n'
        iylrb__ted += '    else:\n'
        iylrb__ted += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        iylrb__ted += '        permutation = np.arange(dim0_global_size)\n'
        iylrb__ted += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            iylrb__ted += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            iylrb__ted += '        n_samples = dim0_global_size\n'
        iylrb__ted += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        iylrb__ted += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        iylrb__ted += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        iylrb__ted += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        iylrb__ted += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        iylrb__ted += '        return output\n'
    else:
        iylrb__ted += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            iylrb__ted += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            iylrb__ted += '    output = output[:local_n_samples]\n'
        iylrb__ted += '    return output\n'
    lpjsy__pivc = {}
    exec(iylrb__ted, {'np': np, 'bodo': bodo}, lpjsy__pivc)
    impl = lpjsy__pivc['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    jsp__wvsfe = np.empty(sendcounts_nulls.sum(), np.uint8)
    ifcui__ufb = 0
    euatz__nizu = 0
    for iajva__iplb in range(len(sendcounts)):
        yhg__ufl = sendcounts[iajva__iplb]
        jci__dni = sendcounts_nulls[iajva__iplb]
        uso__yzolc = jsp__wvsfe[ifcui__ufb:ifcui__ufb + jci__dni]
        for tfeh__uhu in range(yhg__ufl):
            set_bit_to_arr(uso__yzolc, tfeh__uhu, get_bit_bitmap(
                null_bitmap_ptr, euatz__nizu))
            euatz__nizu += 1
        ifcui__ufb += jci__dni
    return jsp__wvsfe


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    qsnjq__ecodr = MPI.COMM_WORLD
    data = qsnjq__ecodr.bcast(data, root)
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
    cux__gnnel = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    chdrq__pww = (0,) * cux__gnnel

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        uzn__ljv = np.ascontiguousarray(data)
        fno__jvx = data.ctypes
        tdx__gcgp = chdrq__pww
        if rank == MPI_ROOT:
            tdx__gcgp = uzn__ljv.shape
        tdx__gcgp = bcast_tuple(tdx__gcgp)
        pcpjm__vzrs = get_tuple_prod(tdx__gcgp[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            tdx__gcgp[0])
        send_counts *= pcpjm__vzrs
        kded__iahk = send_counts[rank]
        xkcj__abamw = np.empty(kded__iahk, dtype)
        kmju__gyj = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(fno__jvx, send_counts.ctypes, kmju__gyj.ctypes,
            xkcj__abamw.ctypes, np.int32(kded__iahk), np.int32(typ_val))
        return xkcj__abamw.reshape((-1,) + tdx__gcgp[1:])
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
        wcrn__iftpf = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], wcrn__iftpf)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        qzpub__pxtaq = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=qzpub__pxtaq)
        bmsu__ndx = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(bmsu__ndx)
        return pd.Index(arr, name=qzpub__pxtaq)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        qzpub__pxtaq = _get_name_value_for_type(dtype.name_typ)
        ncj__uurfs = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        dlqx__fkxr = tuple(get_value_for_type(t) for t in dtype.array_types)
        dlqx__fkxr = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in dlqx__fkxr)
        val = pd.MultiIndex.from_arrays(dlqx__fkxr, names=ncj__uurfs)
        val.name = qzpub__pxtaq
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        qzpub__pxtaq = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=qzpub__pxtaq)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dlqx__fkxr = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({qzpub__pxtaq: arr for qzpub__pxtaq, arr in zip
            (dtype.columns, dlqx__fkxr)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        bmsu__ndx = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(bmsu__ndx[0], bmsu__ndx
            [0])])
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
        zvyu__pyfe = np.int32(numba_to_c_type(types.int32))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            imlem__hdjxh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            imlem__hdjxh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        iylrb__ted = f"""def impl(
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
            recv_arr = {imlem__hdjxh}(n_loc, n_loc_char)

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
        lpjsy__pivc = dict()
        exec(iylrb__ted, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            zvyu__pyfe, 'char_typ_enum': ggk__bhopf, 'decode_if_dict_array':
            decode_if_dict_array}, lpjsy__pivc)
        impl = lpjsy__pivc['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        zvyu__pyfe = np.int32(numba_to_c_type(types.int32))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            bgbiu__umg = bodo.libs.array_item_arr_ext.get_offsets(data)
            duj__nugia = bodo.libs.array_item_arr_ext.get_data(data)
            duj__nugia = duj__nugia[:bgbiu__umg[-1]]
            xlf__tuw = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            kvj__flei = bcast_scalar(len(data))
            hqd__gsa = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                hqd__gsa[i] = bgbiu__umg[i + 1] - bgbiu__umg[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                kvj__flei)
            kmju__gyj = bodo.ir.join.calc_disp(send_counts)
            folhm__cpkk = np.empty(n_pes, np.int32)
            if rank == 0:
                jcu__xbu = 0
                for i in range(n_pes):
                    ndq__hkldl = 0
                    for tto__ytafb in range(send_counts[i]):
                        ndq__hkldl += hqd__gsa[jcu__xbu]
                        jcu__xbu += 1
                    folhm__cpkk[i] = ndq__hkldl
            bcast(folhm__cpkk)
            nvfm__vaty = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                nvfm__vaty[i] = send_counts[i] + 7 >> 3
            lwk__vbxj = bodo.ir.join.calc_disp(nvfm__vaty)
            kded__iahk = send_counts[rank]
            uglv__qmo = np.empty(kded__iahk + 1, np_offset_type)
            imwu__hzwn = bodo.libs.distributed_api.scatterv_impl(duj__nugia,
                folhm__cpkk)
            khfwa__uum = kded__iahk + 7 >> 3
            npogc__izv = np.empty(khfwa__uum, np.uint8)
            kcph__biw = np.empty(kded__iahk, np.uint32)
            c_scatterv(hqd__gsa.ctypes, send_counts.ctypes, kmju__gyj.
                ctypes, kcph__biw.ctypes, np.int32(kded__iahk), zvyu__pyfe)
            convert_len_arr_to_offset(kcph__biw.ctypes, uglv__qmo.ctypes,
                kded__iahk)
            czv__sbis = get_scatter_null_bytes_buff(xlf__tuw.ctypes,
                send_counts, nvfm__vaty)
            c_scatterv(czv__sbis.ctypes, nvfm__vaty.ctypes, lwk__vbxj.
                ctypes, npogc__izv.ctypes, np.int32(khfwa__uum), ggk__bhopf)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                kded__iahk, imwu__hzwn, uglv__qmo, npogc__izv)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            ktmkb__aaq = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            ktmkb__aaq = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            ktmkb__aaq = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            ktmkb__aaq = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            uzn__ljv = data._data
            wqvp__cbhtu = data._null_bitmap
            asv__ibx = len(uzn__ljv)
            gypak__hcyi = _scatterv_np(uzn__ljv, send_counts)
            kvj__flei = bcast_scalar(asv__ibx)
            xwnk__hot = len(gypak__hcyi) + 7 >> 3
            rto__ucgi = np.empty(xwnk__hot, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                kvj__flei)
            nvfm__vaty = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                nvfm__vaty[i] = send_counts[i] + 7 >> 3
            lwk__vbxj = bodo.ir.join.calc_disp(nvfm__vaty)
            czv__sbis = get_scatter_null_bytes_buff(wqvp__cbhtu.ctypes,
                send_counts, nvfm__vaty)
            c_scatterv(czv__sbis.ctypes, nvfm__vaty.ctypes, lwk__vbxj.
                ctypes, rto__ucgi.ctypes, np.int32(xwnk__hot), ggk__bhopf)
            return ktmkb__aaq(gypak__hcyi, rto__ucgi)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            bael__yjkzd = bodo.libs.distributed_api.scatterv_impl(data.
                _left, send_counts)
            tli__zagep = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(bael__yjkzd,
                tli__zagep)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            vffxg__ibumq = data._start
            fhn__mokm = data._stop
            peyb__inixc = data._step
            qzpub__pxtaq = data._name
            qzpub__pxtaq = bcast_scalar(qzpub__pxtaq)
            vffxg__ibumq = bcast_scalar(vffxg__ibumq)
            fhn__mokm = bcast_scalar(fhn__mokm)
            peyb__inixc = bcast_scalar(peyb__inixc)
            fhi__ecw = bodo.libs.array_kernels.calc_nitems(vffxg__ibumq,
                fhn__mokm, peyb__inixc)
            chunk_start = bodo.libs.distributed_api.get_start(fhi__ecw,
                n_pes, rank)
            iqge__pwhzt = bodo.libs.distributed_api.get_node_portion(fhi__ecw,
                n_pes, rank)
            nrtxy__ekym = vffxg__ibumq + peyb__inixc * chunk_start
            eky__hkhrz = vffxg__ibumq + peyb__inixc * (chunk_start +
                iqge__pwhzt)
            eky__hkhrz = min(eky__hkhrz, fhn__mokm)
            return bodo.hiframes.pd_index_ext.init_range_index(nrtxy__ekym,
                eky__hkhrz, peyb__inixc, qzpub__pxtaq)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        gqc__hibq = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            uzn__ljv = data._data
            qzpub__pxtaq = data._name
            qzpub__pxtaq = bcast_scalar(qzpub__pxtaq)
            arr = bodo.libs.distributed_api.scatterv_impl(uzn__ljv, send_counts
                )
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                qzpub__pxtaq, gqc__hibq)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            uzn__ljv = data._data
            qzpub__pxtaq = data._name
            qzpub__pxtaq = bcast_scalar(qzpub__pxtaq)
            arr = bodo.libs.distributed_api.scatterv_impl(uzn__ljv, send_counts
                )
            return bodo.utils.conversion.index_from_array(arr, qzpub__pxtaq)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            eod__rmhw = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            qzpub__pxtaq = bcast_scalar(data._name)
            ncj__uurfs = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(eod__rmhw,
                ncj__uurfs, qzpub__pxtaq)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qzpub__pxtaq = bodo.hiframes.pd_series_ext.get_series_name(data)
            mvu__optmh = bcast_scalar(qzpub__pxtaq)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            etmp__sxt = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                etmp__sxt, mvu__optmh)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        rrl__xxr = len(data.columns)
        gthry__dxqn = ColNamesMetaType(data.columns)
        iylrb__ted = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        if data.is_table_format:
            iylrb__ted += (
                '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            iylrb__ted += """  g_table = bodo.libs.distributed_api.scatterv_impl(table, send_counts)
"""
            yzwu__jpvy = 'g_table'
        else:
            for i in range(rrl__xxr):
                iylrb__ted += f"""  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
                iylrb__ted += f"""  g_data_{i} = bodo.libs.distributed_api.scatterv_impl(data_{i}, send_counts)
"""
            yzwu__jpvy = ', '.join(f'g_data_{i}' for i in range(rrl__xxr))
        iylrb__ted += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        iylrb__ted += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        iylrb__ted += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({yzwu__jpvy},), g_index, __col_name_meta_scaterv_impl)
"""
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            gthry__dxqn}, lpjsy__pivc)
        yrf__eqoqc = lpjsy__pivc['impl_df']
        return yrf__eqoqc
    if isinstance(data, bodo.TableType):
        iylrb__ted = (
            'def impl_table(data, send_counts=None, warn_if_dist=True):\n')
        iylrb__ted += '  T = data\n'
        iylrb__ted += '  T2 = init_table(T, False)\n'
        iylrb__ted += '  l = 0\n'
        djaeh__pisou = {}
        for fqjs__qpw in data.type_to_blk.values():
            djaeh__pisou[f'arr_inds_{fqjs__qpw}'] = np.array(data.
                block_to_arr_ind[fqjs__qpw], dtype=np.int64)
            iylrb__ted += (
                f'  arr_list_{fqjs__qpw} = get_table_block(T, {fqjs__qpw})\n')
            iylrb__ted += f"""  out_arr_list_{fqjs__qpw} = alloc_list_like(arr_list_{fqjs__qpw}, len(arr_list_{fqjs__qpw}), False)
"""
            iylrb__ted += f'  for i in range(len(arr_list_{fqjs__qpw})):\n'
            iylrb__ted += (
                f'    arr_ind_{fqjs__qpw} = arr_inds_{fqjs__qpw}[i]\n')
            iylrb__ted += f"""    ensure_column_unboxed(T, arr_list_{fqjs__qpw}, i, arr_ind_{fqjs__qpw})
"""
            iylrb__ted += f"""    out_arr_{fqjs__qpw} = bodo.libs.distributed_api.scatterv_impl(arr_list_{fqjs__qpw}[i], send_counts)
"""
            iylrb__ted += (
                f'    out_arr_list_{fqjs__qpw}[i] = out_arr_{fqjs__qpw}\n')
            iylrb__ted += f'    l = len(out_arr_{fqjs__qpw})\n'
            iylrb__ted += (
                f'  T2 = set_table_block(T2, out_arr_list_{fqjs__qpw}, {fqjs__qpw})\n'
                )
        iylrb__ted += f'  T2 = set_table_len(T2, l)\n'
        iylrb__ted += f'  return T2\n'
        djaeh__pisou.update({'bodo': bodo, 'init_table': bodo.hiframes.
            table.init_table, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like})
        lpjsy__pivc = {}
        exec(iylrb__ted, djaeh__pisou, lpjsy__pivc)
        return lpjsy__pivc['impl_table']
    if data == bodo.dict_str_arr_type:

        def impl_dict_arr(data, send_counts=None, warn_if_dist=True):
            if bodo.get_rank() == 0:
                eopbx__exs = data._data
                bodo.libs.distributed_api.bcast_scalar(len(eopbx__exs))
                bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.libs.
                    str_arr_ext.num_total_chars(eopbx__exs)))
            else:
                srnw__vpx = bodo.libs.distributed_api.bcast_scalar(0)
                aymxk__trf = bodo.libs.distributed_api.bcast_scalar(0)
                eopbx__exs = bodo.libs.str_arr_ext.pre_alloc_string_array(
                    srnw__vpx, aymxk__trf)
            bodo.libs.distributed_api.bcast(eopbx__exs)
            hxy__jpwk = bodo.libs.distributed_api.scatterv_impl(data.
                _indices, send_counts)
            return bodo.libs.dict_arr_ext.init_dict_arr(eopbx__exs,
                hxy__jpwk, True)
        return impl_dict_arr
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            khyyu__sgl = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                khyyu__sgl, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        iylrb__ted = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        iylrb__ted += '  return ({}{})\n'.format(', '.join(
            f'bodo.libs.distributed_api.scatterv_impl(data[{i}], send_counts)'
             for i in range(len(data))), ',' if len(data) > 0 else '')
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo}, lpjsy__pivc)
        jctei__tzlj = lpjsy__pivc['impl_tuple']
        return jctei__tzlj
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
        jhatd__kadn = np.int32(numba_to_c_type(offset_type))
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            kded__iahk = len(data)
            dmk__lwrcw = num_total_chars(data)
            assert kded__iahk < INT_MAX
            assert dmk__lwrcw < INT_MAX
            woa__ihlg = get_offset_ptr(data)
            fno__jvx = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            jci__dni = kded__iahk + 7 >> 3
            c_bcast(woa__ihlg, np.int32(kded__iahk + 1), jhatd__kadn, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(fno__jvx, np.int32(dmk__lwrcw), ggk__bhopf, np.array([-
                1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(jci__dni), ggk__bhopf, np.
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
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                tzrrc__akkzh = 0
                usqzx__muhx = np.empty(0, np.uint8).ctypes
            else:
                usqzx__muhx, tzrrc__akkzh = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            tzrrc__akkzh = bodo.libs.distributed_api.bcast_scalar(tzrrc__akkzh,
                root)
            if rank != root:
                xlrx__zhzf = np.empty(tzrrc__akkzh + 1, np.uint8)
                xlrx__zhzf[tzrrc__akkzh] = 0
                usqzx__muhx = xlrx__zhzf.ctypes
            c_bcast(usqzx__muhx, np.int32(tzrrc__akkzh), ggk__bhopf, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(usqzx__muhx, tzrrc__akkzh)
        return impl_str
    typ_val = numba_to_c_type(val)
    iylrb__ted = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    lpjsy__pivc = {}
    exec(iylrb__ted, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, lpjsy__pivc)
    xgpod__ywibm = lpjsy__pivc['bcast_scalar_impl']
    return xgpod__ywibm


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    azl__vgcj = len(val)
    iylrb__ted = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    iylrb__ted += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(azl__vgcj)),
        ',' if azl__vgcj else '')
    lpjsy__pivc = {}
    exec(iylrb__ted, {'bcast_scalar': bcast_scalar}, lpjsy__pivc)
    ndto__hqaj = lpjsy__pivc['bcast_tuple_impl']
    return ndto__hqaj


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            kded__iahk = bcast_scalar(len(arr), root)
            tcbn__iogmo = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(kded__iahk, tcbn__iogmo)
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
            nrtxy__ekym = max(arr_start, slice_index.start) - arr_start
            eky__hkhrz = max(slice_index.stop - arr_start, 0)
            return slice(nrtxy__ekym, eky__hkhrz)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            vffxg__ibumq = slice_index.start
            peyb__inixc = slice_index.step
            see__darbq = (0 if peyb__inixc == 1 or vffxg__ibumq > arr_start
                 else abs(peyb__inixc - arr_start % peyb__inixc) % peyb__inixc)
            nrtxy__ekym = max(arr_start, slice_index.start
                ) - arr_start + see__darbq
            eky__hkhrz = max(slice_index.stop - arr_start, 0)
            return slice(nrtxy__ekym, eky__hkhrz, peyb__inixc)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        nyq__bulwg = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[nyq__bulwg])
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
        utvj__bcq = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        ggk__bhopf = np.int32(numba_to_c_type(types.uint8))
        pvzn__snw = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            tngh__sra = np.int32(10)
            tag = np.int32(11)
            bpc__loc = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                aegal__qbuxu = arr._data
                wceb__whe = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    aegal__qbuxu, ind)
                guw__tqgp = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    aegal__qbuxu, ind + 1)
                length = guw__tqgp - wceb__whe
                rhk__uagqq = aegal__qbuxu[ind]
                bpc__loc[0] = length
                isend(bpc__loc, np.int32(1), root, tngh__sra, True)
                isend(rhk__uagqq, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(pvzn__snw,
                utvj__bcq, 0, 1)
            srnw__vpx = 0
            if rank == root:
                srnw__vpx = recv(np.int64, ANY_SOURCE, tngh__sra)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    pvzn__snw, utvj__bcq, srnw__vpx, 1)
                fno__jvx = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(fno__jvx, np.int32(srnw__vpx), ggk__bhopf, ANY_SOURCE,
                    tag)
            dummy_use(bpc__loc)
            srnw__vpx = bcast_scalar(srnw__vpx)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    pvzn__snw, utvj__bcq, srnw__vpx, 1)
            fno__jvx = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(fno__jvx, np.int32(srnw__vpx), ggk__bhopf, np.array([-1
                ]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, srnw__vpx)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        ssyc__imyja = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, ssyc__imyja)
            if arr_start <= ind < arr_start + len(arr):
                khyyu__sgl = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = khyyu__sgl[ind - arr_start]
                send_arr = np.full(1, data, ssyc__imyja)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = ssyc__imyja(-1)
            if rank == root:
                val = recv(ssyc__imyja, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            vyy__hnsqw = arr.dtype.categories[max(val, 0)]
            return vyy__hnsqw
        return cat_getitem_impl
    xmsvg__bztus = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, xmsvg__bztus)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, xmsvg__bztus)[0]
        if rank == root:
            val = recv(xmsvg__bztus, ANY_SOURCE, tag)
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
    ojn__fyy = get_type_enum(out_data)
    assert typ_enum == ojn__fyy
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
    iylrb__ted = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        iylrb__ted += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    iylrb__ted += '  return\n'
    lpjsy__pivc = {}
    exec(iylrb__ted, {'alltoallv': alltoallv}, lpjsy__pivc)
    uqxnx__yrhp = lpjsy__pivc['f']
    return uqxnx__yrhp


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    vffxg__ibumq = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return vffxg__ibumq, count


@numba.njit
def get_start(total_size, pes, rank):
    fds__bshdg = total_size % pes
    vgtgr__bxgeu = (total_size - fds__bshdg) // pes
    return rank * vgtgr__bxgeu + min(rank, fds__bshdg)


@numba.njit
def get_end(total_size, pes, rank):
    fds__bshdg = total_size % pes
    vgtgr__bxgeu = (total_size - fds__bshdg) // pes
    return (rank + 1) * vgtgr__bxgeu + min(rank + 1, fds__bshdg)


@numba.njit
def get_node_portion(total_size, pes, rank):
    fds__bshdg = total_size % pes
    vgtgr__bxgeu = (total_size - fds__bshdg) // pes
    if rank < fds__bshdg:
        return vgtgr__bxgeu + 1
    else:
        return vgtgr__bxgeu


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    bdtm__jzxtu = in_arr.dtype(0)
    eklt__trduw = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        ndq__hkldl = bdtm__jzxtu
        for ylnib__vjik in np.nditer(in_arr):
            ndq__hkldl += ylnib__vjik.item()
        vkebi__ozgv = dist_exscan(ndq__hkldl, eklt__trduw)
        for i in range(in_arr.size):
            vkebi__ozgv += in_arr[i]
            out_arr[i] = vkebi__ozgv
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    nzm__bqpt = in_arr.dtype(1)
    eklt__trduw = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        ndq__hkldl = nzm__bqpt
        for ylnib__vjik in np.nditer(in_arr):
            ndq__hkldl *= ylnib__vjik.item()
        vkebi__ozgv = dist_exscan(ndq__hkldl, eklt__trduw)
        if get_rank() == 0:
            vkebi__ozgv = nzm__bqpt
        for i in range(in_arr.size):
            vkebi__ozgv *= in_arr[i]
            out_arr[i] = vkebi__ozgv
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        nzm__bqpt = np.finfo(in_arr.dtype(1).dtype).max
    else:
        nzm__bqpt = np.iinfo(in_arr.dtype(1).dtype).max
    eklt__trduw = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        ndq__hkldl = nzm__bqpt
        for ylnib__vjik in np.nditer(in_arr):
            ndq__hkldl = min(ndq__hkldl, ylnib__vjik.item())
        vkebi__ozgv = dist_exscan(ndq__hkldl, eklt__trduw)
        if get_rank() == 0:
            vkebi__ozgv = nzm__bqpt
        for i in range(in_arr.size):
            vkebi__ozgv = min(vkebi__ozgv, in_arr[i])
            out_arr[i] = vkebi__ozgv
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        nzm__bqpt = np.finfo(in_arr.dtype(1).dtype).min
    else:
        nzm__bqpt = np.iinfo(in_arr.dtype(1).dtype).min
    nzm__bqpt = in_arr.dtype(1)
    eklt__trduw = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        ndq__hkldl = nzm__bqpt
        for ylnib__vjik in np.nditer(in_arr):
            ndq__hkldl = max(ndq__hkldl, ylnib__vjik.item())
        vkebi__ozgv = dist_exscan(ndq__hkldl, eklt__trduw)
        if get_rank() == 0:
            vkebi__ozgv = nzm__bqpt
        for i in range(in_arr.size):
            vkebi__ozgv = max(vkebi__ozgv, in_arr[i])
            out_arr[i] = vkebi__ozgv
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    fboqa__ooeoe = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), fboqa__ooeoe)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    hjpmk__uxvs = args[0]
    if equiv_set.has_shape(hjpmk__uxvs):
        return ArrayAnalysis.AnalyzeResult(shape=hjpmk__uxvs, pre=[])
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
    ukqy__piq = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for i,
        gegjg__cnjb in enumerate(args) if is_array_typ(gegjg__cnjb) or
        isinstance(gegjg__cnjb, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    iylrb__ted = f"""def impl(*args):
    if {ukqy__piq} or bodo.get_rank() == 0:
        print(*args)"""
    lpjsy__pivc = {}
    exec(iylrb__ted, globals(), lpjsy__pivc)
    impl = lpjsy__pivc['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        xmu__ttho = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        iylrb__ted = 'def f(req, cond=True):\n'
        iylrb__ted += f'  return {xmu__ttho}\n'
        lpjsy__pivc = {}
        exec(iylrb__ted, {'_wait': _wait}, lpjsy__pivc)
        impl = lpjsy__pivc['f']
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
        fds__bshdg = 1
        for a in t:
            fds__bshdg *= a
        return fds__bshdg
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    icbw__ipox = np.ascontiguousarray(in_arr)
    xop__cru = get_tuple_prod(icbw__ipox.shape[1:])
    bulk__dkzr = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        omg__qfwgv = np.array(dest_ranks, dtype=np.int32)
    else:
        omg__qfwgv = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, icbw__ipox.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * bulk__dkzr, dtype_size * xop__cru, len(
        omg__qfwgv), omg__qfwgv.ctypes)
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
    rvibb__chv = np.ascontiguousarray(rhs)
    ytd__ppw = get_tuple_prod(rvibb__chv.shape[1:])
    tihl__yvbqc = dtype_size * ytd__ppw
    permutation_array_index(lhs.ctypes, lhs_len, tihl__yvbqc, rvibb__chv.
        ctypes, rvibb__chv.shape[0], p.ctypes, p_len, n_samples)
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
        iylrb__ted = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, lpjsy__pivc)
        xgpod__ywibm = lpjsy__pivc['bcast_scalar_impl']
        return xgpod__ywibm
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        rrl__xxr = len(data.columns)
        yzwu__jpvy = ', '.join('g_data_{}'.format(i) for i in range(rrl__xxr))
        atzr__eavde = ColNamesMetaType(data.columns)
        iylrb__ted = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(rrl__xxr):
            iylrb__ted += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            iylrb__ted += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        iylrb__ted += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        iylrb__ted += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        iylrb__ted += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(yzwu__jpvy))
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            atzr__eavde}, lpjsy__pivc)
        yrf__eqoqc = lpjsy__pivc['impl_df']
        return yrf__eqoqc
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            vffxg__ibumq = data._start
            fhn__mokm = data._stop
            peyb__inixc = data._step
            qzpub__pxtaq = data._name
            qzpub__pxtaq = bcast_scalar(qzpub__pxtaq, root)
            vffxg__ibumq = bcast_scalar(vffxg__ibumq, root)
            fhn__mokm = bcast_scalar(fhn__mokm, root)
            peyb__inixc = bcast_scalar(peyb__inixc, root)
            fhi__ecw = bodo.libs.array_kernels.calc_nitems(vffxg__ibumq,
                fhn__mokm, peyb__inixc)
            chunk_start = bodo.libs.distributed_api.get_start(fhi__ecw,
                n_pes, rank)
            iqge__pwhzt = bodo.libs.distributed_api.get_node_portion(fhi__ecw,
                n_pes, rank)
            nrtxy__ekym = vffxg__ibumq + peyb__inixc * chunk_start
            eky__hkhrz = vffxg__ibumq + peyb__inixc * (chunk_start +
                iqge__pwhzt)
            eky__hkhrz = min(eky__hkhrz, fhn__mokm)
            return bodo.hiframes.pd_index_ext.init_range_index(nrtxy__ekym,
                eky__hkhrz, peyb__inixc, qzpub__pxtaq)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            uzn__ljv = data._data
            qzpub__pxtaq = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(uzn__ljv,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, qzpub__pxtaq)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qzpub__pxtaq = bodo.hiframes.pd_series_ext.get_series_name(data)
            mvu__optmh = bodo.libs.distributed_api.bcast_comm_impl(qzpub__pxtaq
                , comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            etmp__sxt = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                etmp__sxt, mvu__optmh)
        return impl_series
    if isinstance(data, types.BaseTuple):
        iylrb__ted = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        iylrb__ted += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        lpjsy__pivc = {}
        exec(iylrb__ted, {'bcast_comm_impl': bcast_comm_impl}, lpjsy__pivc)
        jctei__tzlj = lpjsy__pivc['impl_tuple']
        return jctei__tzlj
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    cux__gnnel = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    chdrq__pww = (0,) * cux__gnnel

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        uzn__ljv = np.ascontiguousarray(data)
        fno__jvx = data.ctypes
        tdx__gcgp = chdrq__pww
        if rank == root:
            tdx__gcgp = uzn__ljv.shape
        tdx__gcgp = bcast_tuple(tdx__gcgp, root)
        pcpjm__vzrs = get_tuple_prod(tdx__gcgp[1:])
        send_counts = tdx__gcgp[0] * pcpjm__vzrs
        xkcj__abamw = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(fno__jvx, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(xkcj__abamw.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return xkcj__abamw.reshape((-1,) + tdx__gcgp[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        qsnjq__ecodr = MPI.COMM_WORLD
        kueg__udfvw = MPI.Get_processor_name()
        wawg__axyf = qsnjq__ecodr.allgather(kueg__udfvw)
        node_ranks = defaultdict(list)
        for i, eoty__chluy in enumerate(wawg__axyf):
            node_ranks[eoty__chluy].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    qsnjq__ecodr = MPI.COMM_WORLD
    lsf__frc = qsnjq__ecodr.Get_group()
    dtzqw__fzwag = lsf__frc.Incl(comm_ranks)
    gyt__gjzn = qsnjq__ecodr.Create_group(dtzqw__fzwag)
    return gyt__gjzn


def get_nodes_first_ranks():
    eocac__jinpt = get_host_ranks()
    return np.array([nuy__tfu[0] for nuy__tfu in eocac__jinpt.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
