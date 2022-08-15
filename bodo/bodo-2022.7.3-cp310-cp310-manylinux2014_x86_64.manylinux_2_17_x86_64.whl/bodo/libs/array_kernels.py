"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import DictionaryArrayType, init_dict_arr
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType, alloc_int_array
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)
max_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Max.value)
min_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Min.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._indices._null_bitmap, i) or bodo.libs.array_kernels.isna(arr.
            _data, arr._indices[i])
    if isinstance(arr, DatetimeArrayType):
        return lambda arr, i: np.isnat(arr._data[i])
    assert isinstance(arr, types.Array), f'Invalid array type in isna(): {arr}'
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        pdxsc__rufo = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = pdxsc__rufo
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        pdxsc__rufo = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = pdxsc__rufo
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, ind, int_nan_const=0: bodo.libs.array_kernels.setna(
            arr._indices, ind)
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            dslfe__hoq = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            dslfe__hoq[ind + 1] = dslfe__hoq[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            dslfe__hoq = bodo.libs.array_item_arr_ext.get_offsets(arr)
            dslfe__hoq[ind + 1] = dslfe__hoq[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    qxuf__qvjau = arr_tup.count
    qedfb__krttz = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(qxuf__qvjau):
        qedfb__krttz += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    qedfb__krttz += '  return\n'
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'setna': setna}, sgwo__cqqdn)
    impl = sgwo__cqqdn['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        taiam__ubpbs = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(taiam__ubpbs.start, taiam__ubpbs.stop, taiam__ubpbs.step
            ):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        kgvw__sml = 'n'
        arzus__iuq = 'n_pes'
        ajtpt__rkmyr = 'min_op'
    else:
        kgvw__sml = 'n-1, -1, -1'
        arzus__iuq = '-1'
        ajtpt__rkmyr = 'max_op'
    qedfb__krttz = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {arzus__iuq}
    for i in range({kgvw__sml}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {ajtpt__rkmyr}))
        if possible_valid_rank != {arzus__iuq}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, sgwo__cqqdn)
    impl = sgwo__cqqdn['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    pvrf__ftia = array_to_info(arr)
    _median_series_computation(res, pvrf__ftia, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pvrf__ftia)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    pvrf__ftia = array_to_info(arr)
    _autocorr_series_computation(res, pvrf__ftia, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pvrf__ftia)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    pvrf__ftia = array_to_info(arr)
    _compute_series_monotonicity(res, pvrf__ftia, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pvrf__ftia)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    bohog__jrr = res[0] > 0.5
    return bohog__jrr


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        didai__hbmiy = '-'
        lzxzg__ghj = 'index_arr[0] > threshhold_date'
        kgvw__sml = '1, n+1'
        nbp__qes = 'index_arr[-i] <= threshhold_date'
        sfa__ibz = 'i - 1'
    else:
        didai__hbmiy = '+'
        lzxzg__ghj = 'index_arr[-1] < threshhold_date'
        kgvw__sml = 'n'
        nbp__qes = 'index_arr[i] >= threshhold_date'
        sfa__ibz = 'i'
    qedfb__krttz = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        qedfb__krttz += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        qedfb__krttz += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            qedfb__krttz += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            qedfb__krttz += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            qedfb__krttz += '    else:\n'
            qedfb__krttz += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            qedfb__krttz += (
                f'    threshhold_date = initial_date {didai__hbmiy} date_offset\n'
                )
    else:
        qedfb__krttz += (
            f'  threshhold_date = initial_date {didai__hbmiy} offset\n')
    qedfb__krttz += '  local_valid = 0\n'
    qedfb__krttz += f'  n = len(index_arr)\n'
    qedfb__krttz += f'  if n:\n'
    qedfb__krttz += f'    if {lzxzg__ghj}:\n'
    qedfb__krttz += '      loc_valid = n\n'
    qedfb__krttz += '    else:\n'
    qedfb__krttz += f'      for i in range({kgvw__sml}):\n'
    qedfb__krttz += f'        if {nbp__qes}:\n'
    qedfb__krttz += f'          loc_valid = {sfa__ibz}\n'
    qedfb__krttz += '          break\n'
    qedfb__krttz += '  if is_parallel:\n'
    qedfb__krttz += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    qedfb__krttz += '    return total_valid\n'
    qedfb__krttz += '  else:\n'
    qedfb__krttz += '    return loc_valid\n'
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, sgwo__cqqdn)
    return sgwo__cqqdn['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    bjoy__ocxrk = numba_to_c_type(sig.args[0].dtype)
    btvoh__iasx = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), bjoy__ocxrk))
    cho__ibyvy = args[0]
    eirij__ozgur = sig.args[0]
    if isinstance(eirij__ozgur, (IntegerArrayType, BooleanArrayType)):
        cho__ibyvy = cgutils.create_struct_proxy(eirij__ozgur)(context,
            builder, cho__ibyvy).data
        eirij__ozgur = types.Array(eirij__ozgur.dtype, 1, 'C')
    assert eirij__ozgur.ndim == 1
    arr = make_array(eirij__ozgur)(context, builder, cho__ibyvy)
    zjc__nlec = builder.extract_value(arr.shape, 0)
    kuvf__xkn = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zjc__nlec, args[1], builder.load(btvoh__iasx)]
    rxe__bpazj = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    yij__qdqla = lir.FunctionType(lir.DoubleType(), rxe__bpazj)
    iqvwq__swdk = cgutils.get_or_insert_function(builder.module, yij__qdqla,
        name='quantile_sequential')
    lqhr__szn = builder.call(iqvwq__swdk, kuvf__xkn)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return lqhr__szn


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    bjoy__ocxrk = numba_to_c_type(sig.args[0].dtype)
    btvoh__iasx = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), bjoy__ocxrk))
    cho__ibyvy = args[0]
    eirij__ozgur = sig.args[0]
    if isinstance(eirij__ozgur, (IntegerArrayType, BooleanArrayType)):
        cho__ibyvy = cgutils.create_struct_proxy(eirij__ozgur)(context,
            builder, cho__ibyvy).data
        eirij__ozgur = types.Array(eirij__ozgur.dtype, 1, 'C')
    assert eirij__ozgur.ndim == 1
    arr = make_array(eirij__ozgur)(context, builder, cho__ibyvy)
    zjc__nlec = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        bqq__hko = args[2]
    else:
        bqq__hko = zjc__nlec
    kuvf__xkn = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        zjc__nlec, bqq__hko, args[1], builder.load(btvoh__iasx)]
    rxe__bpazj = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    yij__qdqla = lir.FunctionType(lir.DoubleType(), rxe__bpazj)
    iqvwq__swdk = cgutils.get_or_insert_function(builder.module, yij__qdqla,
        name='quantile_parallel')
    lqhr__szn = builder.call(iqvwq__swdk, kuvf__xkn)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return lqhr__szn


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        mwig__kvh = np.nonzero(pd.isna(arr))[0]
        ujl__lhue = arr[1:] != arr[:-1]
        ujl__lhue[pd.isna(ujl__lhue)] = False
        vaop__lpk = ujl__lhue.astype(np.bool_)
        ecbdz__xdk = np.concatenate((np.array([True]), vaop__lpk))
        if mwig__kvh.size:
            ktca__bidkg, wbaxv__brd = mwig__kvh[0], mwig__kvh[1:]
            ecbdz__xdk[ktca__bidkg] = True
            if wbaxv__brd.size:
                ecbdz__xdk[wbaxv__brd] = False
                if wbaxv__brd[-1] + 1 < ecbdz__xdk.size:
                    ecbdz__xdk[wbaxv__brd[-1] + 1] = True
            elif ktca__bidkg + 1 < ecbdz__xdk.size:
                ecbdz__xdk[ktca__bidkg + 1] = True
        return ecbdz__xdk
    return impl


def rank(arr, method='average', na_option='keep', ascending=True, pct=False):
    return arr


@overload(rank, no_unliteral=True, inline='always')
def overload_rank(arr, method='average', na_option='keep', ascending=True,
    pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_str(na_option):
        raise_bodo_error(
            "Series.rank(): 'na_option' argument must be a constant string")
    na_option = get_overload_const_str(na_option)
    if not is_overload_constant_bool(ascending):
        raise_bodo_error(
            "Series.rank(): 'ascending' argument must be a constant boolean")
    ascending = get_overload_const_bool(ascending)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    if method == 'first' and not ascending:
        raise BodoError(
            "Series.rank(): method='first' with ascending=False is currently unsupported."
            )
    qedfb__krttz = """def impl(arr, method='average', na_option='keep', ascending=True, pct=False):
"""
    qedfb__krttz += '  na_idxs = pd.isna(arr)\n'
    qedfb__krttz += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    qedfb__krttz += '  nas = sum(na_idxs)\n'
    if not ascending:
        qedfb__krttz += '  if nas and nas < (sorter.size - 1):\n'
        qedfb__krttz += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        qedfb__krttz += '  else:\n'
        qedfb__krttz += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        qedfb__krttz += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    qedfb__krttz += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    qedfb__krttz += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        qedfb__krttz += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        qedfb__krttz += '    inv,\n'
        qedfb__krttz += '    new_dtype=np.float64,\n'
        qedfb__krttz += '    copy=True,\n'
        qedfb__krttz += '    nan_to_str=False,\n'
        qedfb__krttz += '    from_series=True,\n'
        qedfb__krttz += '    ) + 1\n'
    else:
        qedfb__krttz += '  arr = arr[sorter]\n'
        qedfb__krttz += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        qedfb__krttz += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            qedfb__krttz += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            qedfb__krttz += '    dense,\n'
            qedfb__krttz += '    new_dtype=np.float64,\n'
            qedfb__krttz += '    copy=True,\n'
            qedfb__krttz += '    nan_to_str=False,\n'
            qedfb__krttz += '    from_series=True,\n'
            qedfb__krttz += '  )\n'
        else:
            qedfb__krttz += """  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))
"""
            qedfb__krttz += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                qedfb__krttz += '  ret = count_float[dense]\n'
            elif method == 'min':
                qedfb__krttz += '  ret = count_float[dense - 1] + 1\n'
            else:
                qedfb__krttz += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                qedfb__krttz += '  ret[na_idxs] = -1\n'
            qedfb__krttz += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            qedfb__krttz += '  div_val = arr.size - nas\n'
        else:
            qedfb__krttz += '  div_val = arr.size\n'
        qedfb__krttz += '  for i in range(len(ret)):\n'
        qedfb__krttz += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        qedfb__krttz += '  ret[na_idxs] = np.nan\n'
    qedfb__krttz += '  return ret\n'
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'np': np, 'pd': pd, 'bodo': bodo}, sgwo__cqqdn)
    return sgwo__cqqdn['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    rdop__tdpw = start
    lpze__jquh = 2 * start + 1
    twsl__svovs = 2 * start + 2
    if lpze__jquh < n and not cmp_f(arr[lpze__jquh], arr[rdop__tdpw]):
        rdop__tdpw = lpze__jquh
    if twsl__svovs < n and not cmp_f(arr[twsl__svovs], arr[rdop__tdpw]):
        rdop__tdpw = twsl__svovs
    if rdop__tdpw != start:
        arr[start], arr[rdop__tdpw] = arr[rdop__tdpw], arr[start]
        ind_arr[start], ind_arr[rdop__tdpw] = ind_arr[rdop__tdpw], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, rdop__tdpw, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        tll__vcgj = np.empty(k, A.dtype)
        bumzh__wmkau = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                tll__vcgj[ind] = A[i]
                bumzh__wmkau[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            tll__vcgj = tll__vcgj[:ind]
            bumzh__wmkau = bumzh__wmkau[:ind]
        return tll__vcgj, bumzh__wmkau, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        lrba__mzt = np.sort(A)
        uagf__otmum = index_arr[np.argsort(A)]
        ptn__vepcx = pd.Series(lrba__mzt).notna().values
        lrba__mzt = lrba__mzt[ptn__vepcx]
        uagf__otmum = uagf__otmum[ptn__vepcx]
        if is_largest:
            lrba__mzt = lrba__mzt[::-1]
            uagf__otmum = uagf__otmum[::-1]
        return np.ascontiguousarray(lrba__mzt), np.ascontiguousarray(
            uagf__otmum)
    tll__vcgj, bumzh__wmkau, start = select_k_nonan(A, index_arr, m, k)
    bumzh__wmkau = bumzh__wmkau[tll__vcgj.argsort()]
    tll__vcgj.sort()
    if not is_largest:
        tll__vcgj = np.ascontiguousarray(tll__vcgj[::-1])
        bumzh__wmkau = np.ascontiguousarray(bumzh__wmkau[::-1])
    for i in range(start, m):
        if cmp_f(A[i], tll__vcgj[0]):
            tll__vcgj[0] = A[i]
            bumzh__wmkau[0] = index_arr[i]
            min_heapify(tll__vcgj, bumzh__wmkau, k, 0, cmp_f)
    bumzh__wmkau = bumzh__wmkau[tll__vcgj.argsort()]
    tll__vcgj.sort()
    if is_largest:
        tll__vcgj = tll__vcgj[::-1]
        bumzh__wmkau = bumzh__wmkau[::-1]
    return np.ascontiguousarray(tll__vcgj), np.ascontiguousarray(bumzh__wmkau)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    kvwbn__tbz = bodo.libs.distributed_api.get_rank()
    cyrg__idddn, ythbe__fcov = nlargest(A, I, k, is_largest, cmp_f)
    vhtv__ioj = bodo.libs.distributed_api.gatherv(cyrg__idddn)
    lza__odjwt = bodo.libs.distributed_api.gatherv(ythbe__fcov)
    if kvwbn__tbz == MPI_ROOT:
        res, pdf__aezi = nlargest(vhtv__ioj, lza__odjwt, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        pdf__aezi = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(pdf__aezi)
    return res, pdf__aezi


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    cqrrt__omgak, qqsnt__dlwrk = mat.shape
    cmbbd__ijwkb = np.empty((qqsnt__dlwrk, qqsnt__dlwrk), dtype=np.float64)
    for jukeb__ekamd in range(qqsnt__dlwrk):
        for qkk__xeiy in range(jukeb__ekamd + 1):
            bwxf__dzl = 0
            ammda__pqxmq = sfma__ktczx = rveas__qdiu = ykda__qmwvv = 0.0
            for i in range(cqrrt__omgak):
                if np.isfinite(mat[i, jukeb__ekamd]) and np.isfinite(mat[i,
                    qkk__xeiy]):
                    odu__svgre = mat[i, jukeb__ekamd]
                    ezbyb__zsh = mat[i, qkk__xeiy]
                    bwxf__dzl += 1
                    rveas__qdiu += odu__svgre
                    ykda__qmwvv += ezbyb__zsh
            if parallel:
                bwxf__dzl = bodo.libs.distributed_api.dist_reduce(bwxf__dzl,
                    sum_op)
                rveas__qdiu = bodo.libs.distributed_api.dist_reduce(rveas__qdiu
                    , sum_op)
                ykda__qmwvv = bodo.libs.distributed_api.dist_reduce(ykda__qmwvv
                    , sum_op)
            if bwxf__dzl < minpv:
                cmbbd__ijwkb[jukeb__ekamd, qkk__xeiy] = cmbbd__ijwkb[
                    qkk__xeiy, jukeb__ekamd] = np.nan
            else:
                qock__wxzrk = rveas__qdiu / bwxf__dzl
                geytv__xbu = ykda__qmwvv / bwxf__dzl
                rveas__qdiu = 0.0
                for i in range(cqrrt__omgak):
                    if np.isfinite(mat[i, jukeb__ekamd]) and np.isfinite(mat
                        [i, qkk__xeiy]):
                        odu__svgre = mat[i, jukeb__ekamd] - qock__wxzrk
                        ezbyb__zsh = mat[i, qkk__xeiy] - geytv__xbu
                        rveas__qdiu += odu__svgre * ezbyb__zsh
                        ammda__pqxmq += odu__svgre * odu__svgre
                        sfma__ktczx += ezbyb__zsh * ezbyb__zsh
                if parallel:
                    rveas__qdiu = bodo.libs.distributed_api.dist_reduce(
                        rveas__qdiu, sum_op)
                    ammda__pqxmq = bodo.libs.distributed_api.dist_reduce(
                        ammda__pqxmq, sum_op)
                    sfma__ktczx = bodo.libs.distributed_api.dist_reduce(
                        sfma__ktczx, sum_op)
                vqm__vizue = bwxf__dzl - 1.0 if cov else sqrt(ammda__pqxmq *
                    sfma__ktczx)
                if vqm__vizue != 0.0:
                    cmbbd__ijwkb[jukeb__ekamd, qkk__xeiy] = cmbbd__ijwkb[
                        qkk__xeiy, jukeb__ekamd] = rveas__qdiu / vqm__vizue
                else:
                    cmbbd__ijwkb[jukeb__ekamd, qkk__xeiy] = cmbbd__ijwkb[
                        qkk__xeiy, jukeb__ekamd] = np.nan
    return cmbbd__ijwkb


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    tto__rxy = n != 1
    qedfb__krttz = 'def impl(data, parallel=False):\n'
    qedfb__krttz += '  if parallel:\n'
    pafoq__kkskb = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    qedfb__krttz += (
        f'    cpp_table = arr_info_list_to_table([{pafoq__kkskb}])\n')
    qedfb__krttz += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    nhykr__fvev = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    qedfb__krttz += f'    data = ({nhykr__fvev},)\n'
    qedfb__krttz += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    qedfb__krttz += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    qedfb__krttz += '    bodo.libs.array.delete_table(cpp_table)\n'
    qedfb__krttz += '  n = len(data[0])\n'
    qedfb__krttz += '  out = np.empty(n, np.bool_)\n'
    qedfb__krttz += '  uniqs = dict()\n'
    if tto__rxy:
        qedfb__krttz += '  for i in range(n):\n'
        oer__wui = ', '.join(f'data[{i}][i]' for i in range(n))
        oojgt__vql = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        qedfb__krttz += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({oer__wui},), ({oojgt__vql},))
"""
        qedfb__krttz += '    if val in uniqs:\n'
        qedfb__krttz += '      out[i] = True\n'
        qedfb__krttz += '    else:\n'
        qedfb__krttz += '      out[i] = False\n'
        qedfb__krttz += '      uniqs[val] = 0\n'
    else:
        qedfb__krttz += '  data = data[0]\n'
        qedfb__krttz += '  hasna = False\n'
        qedfb__krttz += '  for i in range(n):\n'
        qedfb__krttz += '    if bodo.libs.array_kernels.isna(data, i):\n'
        qedfb__krttz += '      out[i] = hasna\n'
        qedfb__krttz += '      hasna = True\n'
        qedfb__krttz += '    else:\n'
        qedfb__krttz += '      val = data[i]\n'
        qedfb__krttz += '      if val in uniqs:\n'
        qedfb__krttz += '        out[i] = True\n'
        qedfb__krttz += '      else:\n'
        qedfb__krttz += '        out[i] = False\n'
        qedfb__krttz += '        uniqs[val] = 0\n'
    qedfb__krttz += '  if parallel:\n'
    qedfb__krttz += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    qedfb__krttz += '  return out\n'
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        sgwo__cqqdn)
    impl = sgwo__cqqdn['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    qxuf__qvjau = len(data)
    qedfb__krttz = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    qedfb__krttz += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (qxuf__qvjau))))
    qedfb__krttz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    qedfb__krttz += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(qxuf__qvjau))
    for fht__pxdda in range(qxuf__qvjau):
        qedfb__krttz += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(fht__pxdda, fht__pxdda, fht__pxdda))
    qedfb__krttz += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(qxuf__qvjau))
    qedfb__krttz += '  delete_table(out_table)\n'
    qedfb__krttz += '  delete_table(table_total)\n'
    qedfb__krttz += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(qxuf__qvjau)))
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, sgwo__cqqdn)
    impl = sgwo__cqqdn['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    qxuf__qvjau = len(data)
    qedfb__krttz = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    qedfb__krttz += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (qxuf__qvjau))))
    qedfb__krttz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    qedfb__krttz += '  keep_i = 0\n'
    qedfb__krttz += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for fht__pxdda in range(qxuf__qvjau):
        qedfb__krttz += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(fht__pxdda, fht__pxdda, fht__pxdda))
    qedfb__krttz += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(qxuf__qvjau))
    qedfb__krttz += '  delete_table(out_table)\n'
    qedfb__krttz += '  delete_table(table_total)\n'
    qedfb__krttz += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(qxuf__qvjau)))
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, sgwo__cqqdn)
    impl = sgwo__cqqdn['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        wbaj__lcm = [array_to_info(data_arr)]
        cjv__voe = arr_info_list_to_table(wbaj__lcm)
        yopl__xsf = 0
        vugzb__rsed = drop_duplicates_table(cjv__voe, parallel, 1,
            yopl__xsf, False, True)
        hbuye__npr = info_to_array(info_from_table(vugzb__rsed, 0), data_arr)
        delete_table(vugzb__rsed)
        delete_table(cjv__voe)
        return hbuye__npr
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    rnkzj__ecaw = len(data.types)
    roeng__kpzmr = [('out' + str(i)) for i in range(rnkzj__ecaw)]
    gwpn__vkr = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    lceo__olv = ['isna(data[{}], i)'.format(i) for i in gwpn__vkr]
    pwq__vnkft = 'not ({})'.format(' or '.join(lceo__olv))
    if not is_overload_none(thresh):
        pwq__vnkft = '(({}) <= ({}) - thresh)'.format(' + '.join(lceo__olv),
            rnkzj__ecaw - 1)
    elif how == 'all':
        pwq__vnkft = 'not ({})'.format(' and '.join(lceo__olv))
    qedfb__krttz = 'def _dropna_imp(data, how, thresh, subset):\n'
    qedfb__krttz += '  old_len = len(data[0])\n'
    qedfb__krttz += '  new_len = 0\n'
    qedfb__krttz += '  for i in range(old_len):\n'
    qedfb__krttz += '    if {}:\n'.format(pwq__vnkft)
    qedfb__krttz += '      new_len += 1\n'
    for i, out in enumerate(roeng__kpzmr):
        if isinstance(data[i], bodo.CategoricalArrayType):
            qedfb__krttz += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            qedfb__krttz += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    qedfb__krttz += '  curr_ind = 0\n'
    qedfb__krttz += '  for i in range(old_len):\n'
    qedfb__krttz += '    if {}:\n'.format(pwq__vnkft)
    for i in range(rnkzj__ecaw):
        qedfb__krttz += '      if isna(data[{}], i):\n'.format(i)
        qedfb__krttz += '        setna({}, curr_ind)\n'.format(roeng__kpzmr[i])
        qedfb__krttz += '      else:\n'
        qedfb__krttz += '        {}[curr_ind] = data[{}][i]\n'.format(
            roeng__kpzmr[i], i)
    qedfb__krttz += '      curr_ind += 1\n'
    qedfb__krttz += '  return {}\n'.format(', '.join(roeng__kpzmr))
    sgwo__cqqdn = {}
    hlrs__qdoe = {'t{}'.format(i): dslku__vkpgy for i, dslku__vkpgy in
        enumerate(data.types)}
    hlrs__qdoe.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(qedfb__krttz, hlrs__qdoe, sgwo__cqqdn)
    nlvxn__aiil = sgwo__cqqdn['_dropna_imp']
    return nlvxn__aiil


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        eirij__ozgur = arr.dtype
        mkkb__oqx = eirij__ozgur.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            aww__ifem = init_nested_counts(mkkb__oqx)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                aww__ifem = add_nested_counts(aww__ifem, val[ind])
            hbuye__npr = bodo.utils.utils.alloc_type(n, eirij__ozgur, aww__ifem
                )
            for irzj__emu in range(n):
                if bodo.libs.array_kernels.isna(arr, irzj__emu):
                    setna(hbuye__npr, irzj__emu)
                    continue
                val = arr[irzj__emu]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(hbuye__npr, irzj__emu)
                    continue
                hbuye__npr[irzj__emu] = val[ind]
            return hbuye__npr
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    mtr__rkbyh = _to_readonly(arr_types.types[0])
    return all(isinstance(dslku__vkpgy, CategoricalArrayType) and 
        _to_readonly(dslku__vkpgy) == mtr__rkbyh for dslku__vkpgy in
        arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arr_list.
        dtype, 'bodo.concat()')
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        lgs__gutm = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            ifftk__gjgjt = 0
            dzo__kcc = []
            for A in arr_list:
                vimug__dlsfw = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                dzo__kcc.append(bodo.libs.array_item_arr_ext.get_data(A))
                ifftk__gjgjt += vimug__dlsfw
            bwrjg__uqdsl = np.empty(ifftk__gjgjt + 1, offset_type)
            ebcj__npqy = bodo.libs.array_kernels.concat(dzo__kcc)
            lsx__esn = np.empty(ifftk__gjgjt + 7 >> 3, np.uint8)
            eix__cjm = 0
            pibh__zplmv = 0
            for A in arr_list:
                bji__oeaq = bodo.libs.array_item_arr_ext.get_offsets(A)
                agvfn__kpufi = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                vimug__dlsfw = len(A)
                yffv__yxww = bji__oeaq[vimug__dlsfw]
                for i in range(vimug__dlsfw):
                    bwrjg__uqdsl[i + eix__cjm] = bji__oeaq[i] + pibh__zplmv
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        agvfn__kpufi, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lsx__esn, i +
                        eix__cjm, zqlcp__sfzg)
                eix__cjm += vimug__dlsfw
                pibh__zplmv += yffv__yxww
            bwrjg__uqdsl[eix__cjm] = pibh__zplmv
            hbuye__npr = bodo.libs.array_item_arr_ext.init_array_item_array(
                ifftk__gjgjt, ebcj__npqy, bwrjg__uqdsl, lsx__esn)
            return hbuye__npr
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        wxwn__bbi = arr_list.dtype.names
        qedfb__krttz = 'def struct_array_concat_impl(arr_list):\n'
        qedfb__krttz += f'    n_all = 0\n'
        for i in range(len(wxwn__bbi)):
            qedfb__krttz += f'    concat_list{i} = []\n'
        qedfb__krttz += '    for A in arr_list:\n'
        qedfb__krttz += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(wxwn__bbi)):
            qedfb__krttz += f'        concat_list{i}.append(data_tuple[{i}])\n'
        qedfb__krttz += '        n_all += len(A)\n'
        qedfb__krttz += '    n_bytes = (n_all + 7) >> 3\n'
        qedfb__krttz += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        qedfb__krttz += '    curr_bit = 0\n'
        qedfb__krttz += '    for A in arr_list:\n'
        qedfb__krttz += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        qedfb__krttz += '        for j in range(len(A)):\n'
        qedfb__krttz += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        qedfb__krttz += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        qedfb__krttz += '            curr_bit += 1\n'
        qedfb__krttz += (
            '    return bodo.libs.struct_arr_ext.init_struct_arr(\n')
        nwx__mod = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(wxwn__bbi))])
        qedfb__krttz += f'        ({nwx__mod},),\n'
        qedfb__krttz += '        new_mask,\n'
        qedfb__krttz += f'        {wxwn__bbi},\n'
        qedfb__krttz += '    )\n'
        sgwo__cqqdn = {}
        exec(qedfb__krttz, {'bodo': bodo, 'np': np}, sgwo__cqqdn)
        return sgwo__cqqdn['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            agqpb__zkb = 0
            for A in arr_list:
                agqpb__zkb += len(A)
            syce__gfkz = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(agqpb__zkb))
            hjmsf__ucl = 0
            for A in arr_list:
                for i in range(len(A)):
                    syce__gfkz._data[i + hjmsf__ucl] = A._data[i]
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(syce__gfkz.
                        _null_bitmap, i + hjmsf__ucl, zqlcp__sfzg)
                hjmsf__ucl += len(A)
            return syce__gfkz
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            agqpb__zkb = 0
            for A in arr_list:
                agqpb__zkb += len(A)
            syce__gfkz = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(agqpb__zkb))
            hjmsf__ucl = 0
            for A in arr_list:
                for i in range(len(A)):
                    syce__gfkz._days_data[i + hjmsf__ucl] = A._days_data[i]
                    syce__gfkz._seconds_data[i + hjmsf__ucl] = A._seconds_data[
                        i]
                    syce__gfkz._microseconds_data[i + hjmsf__ucl
                        ] = A._microseconds_data[i]
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(syce__gfkz.
                        _null_bitmap, i + hjmsf__ucl, zqlcp__sfzg)
                hjmsf__ucl += len(A)
            return syce__gfkz
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        xvk__ufh = arr_list.dtype.precision
        jql__cflpw = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            agqpb__zkb = 0
            for A in arr_list:
                agqpb__zkb += len(A)
            syce__gfkz = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                agqpb__zkb, xvk__ufh, jql__cflpw)
            hjmsf__ucl = 0
            for A in arr_list:
                for i in range(len(A)):
                    syce__gfkz._data[i + hjmsf__ucl] = A._data[i]
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(syce__gfkz.
                        _null_bitmap, i + hjmsf__ucl, zqlcp__sfzg)
                hjmsf__ucl += len(A)
            return syce__gfkz
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        dslku__vkpgy) for dslku__vkpgy in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            dbqkt__xnq = arr_list.types[0]
        else:
            dbqkt__xnq = arr_list.dtype
        dbqkt__xnq = to_str_arr_if_dict_array(dbqkt__xnq)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            bit__ses = 0
            mqoq__fqnxs = 0
            for A in arr_list:
                arr = A
                bit__ses += len(arr)
                mqoq__fqnxs += bodo.libs.str_arr_ext.num_total_chars(arr)
            hbuye__npr = bodo.utils.utils.alloc_type(bit__ses, dbqkt__xnq,
                (mqoq__fqnxs,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(hbuye__npr, -1)
            bjh__vnwcj = 0
            iqdxa__hqy = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(hbuye__npr,
                    arr, bjh__vnwcj, iqdxa__hqy)
                bjh__vnwcj += len(arr)
                iqdxa__hqy += bodo.libs.str_arr_ext.num_total_chars(arr)
            return hbuye__npr
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(dslku__vkpgy.dtype, types.Integer) for
        dslku__vkpgy in arr_list.types) and any(isinstance(dslku__vkpgy,
        IntegerArrayType) for dslku__vkpgy in arr_list.types):

        def impl_int_arr_list(arr_list):
            phucj__mlrh = convert_to_nullable_tup(arr_list)
            diuzf__kmz = []
            yqmn__xrzds = 0
            for A in phucj__mlrh:
                diuzf__kmz.append(A._data)
                yqmn__xrzds += len(A)
            ebcj__npqy = bodo.libs.array_kernels.concat(diuzf__kmz)
            qddeh__yqrxz = yqmn__xrzds + 7 >> 3
            coz__nps = np.empty(qddeh__yqrxz, np.uint8)
            jndqw__nnxl = 0
            for A in phucj__mlrh:
                hbdwb__dcq = A._null_bitmap
                for irzj__emu in range(len(A)):
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        hbdwb__dcq, irzj__emu)
                    bodo.libs.int_arr_ext.set_bit_to_arr(coz__nps,
                        jndqw__nnxl, zqlcp__sfzg)
                    jndqw__nnxl += 1
            return bodo.libs.int_arr_ext.init_integer_array(ebcj__npqy,
                coz__nps)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(dslku__vkpgy.dtype == types.bool_ for
        dslku__vkpgy in arr_list.types) and any(dslku__vkpgy ==
        boolean_array for dslku__vkpgy in arr_list.types):

        def impl_bool_arr_list(arr_list):
            phucj__mlrh = convert_to_nullable_tup(arr_list)
            diuzf__kmz = []
            yqmn__xrzds = 0
            for A in phucj__mlrh:
                diuzf__kmz.append(A._data)
                yqmn__xrzds += len(A)
            ebcj__npqy = bodo.libs.array_kernels.concat(diuzf__kmz)
            qddeh__yqrxz = yqmn__xrzds + 7 >> 3
            coz__nps = np.empty(qddeh__yqrxz, np.uint8)
            jndqw__nnxl = 0
            for A in phucj__mlrh:
                hbdwb__dcq = A._null_bitmap
                for irzj__emu in range(len(A)):
                    zqlcp__sfzg = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        hbdwb__dcq, irzj__emu)
                    bodo.libs.int_arr_ext.set_bit_to_arr(coz__nps,
                        jndqw__nnxl, zqlcp__sfzg)
                    jndqw__nnxl += 1
            return bodo.libs.bool_arr_ext.init_bool_array(ebcj__npqy, coz__nps)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            qea__zfkve = []
            for A in arr_list:
                qea__zfkve.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                qea__zfkve), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        wwltz__obvop = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        qedfb__krttz = 'def impl(arr_list):\n'
        qedfb__krttz += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({wwltz__obvop},)), arr_list[0].dtype)
"""
        juf__dnwqw = {}
        exec(qedfb__krttz, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, juf__dnwqw)
        return juf__dnwqw['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            yqmn__xrzds = 0
            for A in arr_list:
                yqmn__xrzds += len(A)
            hbuye__npr = np.empty(yqmn__xrzds, dtype)
            hiyc__rkvt = 0
            for A in arr_list:
                n = len(A)
                hbuye__npr[hiyc__rkvt:hiyc__rkvt + n] = A
                hiyc__rkvt += n
            return hbuye__npr
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(
        dslku__vkpgy, (types.Array, IntegerArrayType)) and isinstance(
        dslku__vkpgy.dtype, types.Integer) for dslku__vkpgy in arr_list.types
        ) and any(isinstance(dslku__vkpgy, types.Array) and isinstance(
        dslku__vkpgy.dtype, types.Float) for dslku__vkpgy in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            xpnz__kusy = []
            for A in arr_list:
                xpnz__kusy.append(A._data)
            ogl__led = bodo.libs.array_kernels.concat(xpnz__kusy)
            cmbbd__ijwkb = bodo.libs.map_arr_ext.init_map_arr(ogl__led)
            return cmbbd__ijwkb
        return impl_map_arr_list
    for jchj__ifr in arr_list:
        if not isinstance(jchj__ifr, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(dslku__vkpgy.astype(np.float64) for dslku__vkpgy in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    qxuf__qvjau = len(arr_tup.types)
    qedfb__krttz = 'def f(arr_tup):\n'
    qedfb__krttz += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        qxuf__qvjau)), ',' if qxuf__qvjau == 1 else '')
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'np': np}, sgwo__cqqdn)
    juy__pbbg = sgwo__cqqdn['f']
    return juy__pbbg


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    qxuf__qvjau = len(arr_tup.types)
    dso__wtjpy = find_common_np_dtype(arr_tup.types)
    mkkb__oqx = None
    octt__vgm = ''
    if isinstance(dso__wtjpy, types.Integer):
        mkkb__oqx = bodo.libs.int_arr_ext.IntDtype(dso__wtjpy)
        octt__vgm = '.astype(out_dtype, False)'
    qedfb__krttz = 'def f(arr_tup):\n'
    qedfb__krttz += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, octt__vgm) for i in range(qxuf__qvjau)), ',' if 
        qxuf__qvjau == 1 else '')
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'bodo': bodo, 'out_dtype': mkkb__oqx}, sgwo__cqqdn)
    rtj__cxeko = sgwo__cqqdn['f']
    return rtj__cxeko


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, zyj__xst = build_set_seen_na(A)
        return len(s) + int(not dropna and zyj__xst)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        vic__lat = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        bqj__vsivk = len(vic__lat)
        return bodo.libs.distributed_api.dist_reduce(bqj__vsivk, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([kitlc__zwom for kitlc__zwom in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        cxob__ryu = np.finfo(A.dtype(1).dtype).max
    else:
        cxob__ryu = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        hbuye__npr = np.empty(n, A.dtype)
        zoea__dcmu = cxob__ryu
        for i in range(n):
            zoea__dcmu = min(zoea__dcmu, A[i])
            hbuye__npr[i] = zoea__dcmu
        return hbuye__npr
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        cxob__ryu = np.finfo(A.dtype(1).dtype).min
    else:
        cxob__ryu = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        hbuye__npr = np.empty(n, A.dtype)
        zoea__dcmu = cxob__ryu
        for i in range(n):
            zoea__dcmu = max(zoea__dcmu, A[i])
            hbuye__npr[i] = zoea__dcmu
        return hbuye__npr
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        zpq__qxuvj = arr_info_list_to_table([array_to_info(A)])
        ked__orm = 1
        yopl__xsf = 0
        vugzb__rsed = drop_duplicates_table(zpq__qxuvj, parallel, ked__orm,
            yopl__xsf, dropna, True)
        hbuye__npr = info_to_array(info_from_table(vugzb__rsed, 0), A)
        delete_table(zpq__qxuvj)
        delete_table(vugzb__rsed)
        return hbuye__npr
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    lgs__gutm = bodo.utils.typing.to_nullable_type(arr.dtype)
    bjv__mruy = index_arr
    ogbsu__vjdy = bjv__mruy.dtype

    def impl(arr, index_arr):
        n = len(arr)
        aww__ifem = init_nested_counts(lgs__gutm)
        vjwjq__vpk = init_nested_counts(ogbsu__vjdy)
        for i in range(n):
            veh__ycxe = index_arr[i]
            if isna(arr, i):
                aww__ifem = (aww__ifem[0] + 1,) + aww__ifem[1:]
                vjwjq__vpk = add_nested_counts(vjwjq__vpk, veh__ycxe)
                continue
            lkwc__ppk = arr[i]
            if len(lkwc__ppk) == 0:
                aww__ifem = (aww__ifem[0] + 1,) + aww__ifem[1:]
                vjwjq__vpk = add_nested_counts(vjwjq__vpk, veh__ycxe)
                continue
            aww__ifem = add_nested_counts(aww__ifem, lkwc__ppk)
            for ovnz__ypsis in range(len(lkwc__ppk)):
                vjwjq__vpk = add_nested_counts(vjwjq__vpk, veh__ycxe)
        hbuye__npr = bodo.utils.utils.alloc_type(aww__ifem[0], lgs__gutm,
            aww__ifem[1:])
        nxn__pnwe = bodo.utils.utils.alloc_type(aww__ifem[0], bjv__mruy,
            vjwjq__vpk)
        pibh__zplmv = 0
        for i in range(n):
            if isna(arr, i):
                setna(hbuye__npr, pibh__zplmv)
                nxn__pnwe[pibh__zplmv] = index_arr[i]
                pibh__zplmv += 1
                continue
            lkwc__ppk = arr[i]
            yffv__yxww = len(lkwc__ppk)
            if yffv__yxww == 0:
                setna(hbuye__npr, pibh__zplmv)
                nxn__pnwe[pibh__zplmv] = index_arr[i]
                pibh__zplmv += 1
                continue
            hbuye__npr[pibh__zplmv:pibh__zplmv + yffv__yxww] = lkwc__ppk
            nxn__pnwe[pibh__zplmv:pibh__zplmv + yffv__yxww] = index_arr[i]
            pibh__zplmv += yffv__yxww
        return hbuye__npr, nxn__pnwe
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    lgs__gutm = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        aww__ifem = init_nested_counts(lgs__gutm)
        for i in range(n):
            if isna(arr, i):
                aww__ifem = (aww__ifem[0] + 1,) + aww__ifem[1:]
                gqfu__ruicj = 1
            else:
                lkwc__ppk = arr[i]
                hubgv__mwbj = len(lkwc__ppk)
                if hubgv__mwbj == 0:
                    aww__ifem = (aww__ifem[0] + 1,) + aww__ifem[1:]
                    gqfu__ruicj = 1
                    continue
                else:
                    aww__ifem = add_nested_counts(aww__ifem, lkwc__ppk)
                    gqfu__ruicj = hubgv__mwbj
            if counts[i] != gqfu__ruicj:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        hbuye__npr = bodo.utils.utils.alloc_type(aww__ifem[0], lgs__gutm,
            aww__ifem[1:])
        pibh__zplmv = 0
        for i in range(n):
            if isna(arr, i):
                setna(hbuye__npr, pibh__zplmv)
                pibh__zplmv += 1
                continue
            lkwc__ppk = arr[i]
            yffv__yxww = len(lkwc__ppk)
            if yffv__yxww == 0:
                setna(hbuye__npr, pibh__zplmv)
                pibh__zplmv += 1
                continue
            hbuye__npr[pibh__zplmv:pibh__zplmv + yffv__yxww] = lkwc__ppk
            pibh__zplmv += yffv__yxww
        return hbuye__npr
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(dihut__xxju) for dihut__xxju in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        iga__zdpx = 'np.empty(n, np.int64)'
        tea__usfim = 'out_arr[i] = 1'
        xru__kbsrh = 'max(len(arr[i]), 1)'
    else:
        iga__zdpx = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        tea__usfim = 'bodo.libs.array_kernels.setna(out_arr, i)'
        xru__kbsrh = 'len(arr[i])'
    qedfb__krttz = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {iga__zdpx}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {tea__usfim}
        else:
            out_arr[i] = {xru__kbsrh}
    return out_arr
    """
    sgwo__cqqdn = {}
    exec(qedfb__krttz, {'bodo': bodo, 'numba': numba, 'np': np}, sgwo__cqqdn)
    impl = sgwo__cqqdn['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    bjv__mruy = index_arr
    ogbsu__vjdy = bjv__mruy.dtype

    def impl(arr, pat, n, index_arr):
        fllu__lfej = pat is not None and len(pat) > 1
        if fllu__lfej:
            ficch__trna = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        kuuov__ibwmw = len(arr)
        bit__ses = 0
        mqoq__fqnxs = 0
        vjwjq__vpk = init_nested_counts(ogbsu__vjdy)
        for i in range(kuuov__ibwmw):
            veh__ycxe = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                bit__ses += 1
                vjwjq__vpk = add_nested_counts(vjwjq__vpk, veh__ycxe)
                continue
            if fllu__lfej:
                oqp__xle = ficch__trna.split(arr[i], maxsplit=n)
            else:
                oqp__xle = arr[i].split(pat, n)
            bit__ses += len(oqp__xle)
            for s in oqp__xle:
                vjwjq__vpk = add_nested_counts(vjwjq__vpk, veh__ycxe)
                mqoq__fqnxs += bodo.libs.str_arr_ext.get_utf8_size(s)
        hbuye__npr = bodo.libs.str_arr_ext.pre_alloc_string_array(bit__ses,
            mqoq__fqnxs)
        nxn__pnwe = bodo.utils.utils.alloc_type(bit__ses, bjv__mruy, vjwjq__vpk
            )
        okems__xrlr = 0
        for irzj__emu in range(kuuov__ibwmw):
            if isna(arr, irzj__emu):
                hbuye__npr[okems__xrlr] = ''
                bodo.libs.array_kernels.setna(hbuye__npr, okems__xrlr)
                nxn__pnwe[okems__xrlr] = index_arr[irzj__emu]
                okems__xrlr += 1
                continue
            if fllu__lfej:
                oqp__xle = ficch__trna.split(arr[irzj__emu], maxsplit=n)
            else:
                oqp__xle = arr[irzj__emu].split(pat, n)
            dzv__cybbs = len(oqp__xle)
            hbuye__npr[okems__xrlr:okems__xrlr + dzv__cybbs] = oqp__xle
            nxn__pnwe[okems__xrlr:okems__xrlr + dzv__cybbs] = index_arr[
                irzj__emu]
            okems__xrlr += dzv__cybbs
        return hbuye__npr, nxn__pnwe
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr, use_dict_arr=False):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if not isinstance(arr, IntegerArrayType) and isinstance(dtype, (types.
        Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr, use_dict_arr=False):
            numba.parfors.parfor.init_prange()
            hbuye__npr = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hbuye__npr[i] = np.nan
            return hbuye__npr
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            osojd__iyc = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            vdjkg__csrzk = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(vdjkg__csrzk, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(osojd__iyc,
                vdjkg__csrzk, True)
        return impl_dict
    qiuf__nwqi = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        hbuye__npr = bodo.utils.utils.alloc_type(n, qiuf__nwqi, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(hbuye__npr, i)
        return hbuye__npr
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.resize_and_copy()')
    fnk__hmc = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            hbuye__npr = bodo.utils.utils.alloc_type(new_len, fnk__hmc)
            bodo.libs.str_arr_ext.str_copy_ptr(hbuye__npr.ctypes, 0, A.
                ctypes, old_size)
            return hbuye__npr
        return impl_char

    def impl(A, old_size, new_len):
        hbuye__npr = bodo.utils.utils.alloc_type(new_len, fnk__hmc, (-1,))
        hbuye__npr[:old_size] = A[:old_size]
        return hbuye__npr
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    pahr__wiw = math.ceil((stop - start) / step)
    return int(max(pahr__wiw, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(kitlc__zwom, types.Complex) for kitlc__zwom in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            xlkeu__cbzw = (stop - start) / step
            pahr__wiw = math.ceil(xlkeu__cbzw.real)
            lhfmi__bwnpi = math.ceil(xlkeu__cbzw.imag)
            smwmf__oaphe = int(max(min(lhfmi__bwnpi, pahr__wiw), 0))
            arr = np.empty(smwmf__oaphe, dtype)
            for i in numba.parfors.parfor.internal_prange(smwmf__oaphe):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            smwmf__oaphe = bodo.libs.array_kernels.calc_nitems(start, stop,
                step)
            arr = np.empty(smwmf__oaphe, dtype)
            for i in numba.parfors.parfor.internal_prange(smwmf__oaphe):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        nwqr__fmf = arr,
        if not inplace:
            nwqr__fmf = arr.copy(),
        efaxp__eds = bodo.libs.str_arr_ext.to_list_if_immutable_arr(nwqr__fmf)
        ely__dhp = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(efaxp__eds, 0, n, ely__dhp)
        if not ascending:
            bodo.libs.timsort.reverseRange(efaxp__eds, 0, n, ely__dhp)
        bodo.libs.str_arr_ext.cp_str_list_to_array(nwqr__fmf, efaxp__eds)
        return nwqr__fmf[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.nonzero()')
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        cmbbd__ijwkb = []
        for i in range(n):
            if A[i]:
                cmbbd__ijwkb.append(i + offset)
        return np.array(cmbbd__ijwkb, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    fnk__hmc = element_type(A)
    if fnk__hmc == types.unicode_type:
        null_value = '""'
    elif fnk__hmc == types.bool_:
        null_value = 'False'
    elif fnk__hmc == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif fnk__hmc == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    okems__xrlr = 'i'
    crzi__url = False
    cknp__hhb = get_overload_const_str(method)
    if cknp__hhb in ('ffill', 'pad'):
        tgq__qglud = 'n'
        send_right = True
    elif cknp__hhb in ('backfill', 'bfill'):
        tgq__qglud = 'n-1, -1, -1'
        send_right = False
        if fnk__hmc == types.unicode_type:
            okems__xrlr = '(n - 1) - i'
            crzi__url = True
    qedfb__krttz = 'def impl(A, method, parallel=False):\n'
    qedfb__krttz += '  A = decode_if_dict_array(A)\n'
    qedfb__krttz += '  has_last_value = False\n'
    qedfb__krttz += f'  last_value = {null_value}\n'
    qedfb__krttz += '  if parallel:\n'
    qedfb__krttz += '    rank = bodo.libs.distributed_api.get_rank()\n'
    qedfb__krttz += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    qedfb__krttz += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    qedfb__krttz += '  n = len(A)\n'
    qedfb__krttz += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    qedfb__krttz += f'  for i in range({tgq__qglud}):\n'
    qedfb__krttz += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    qedfb__krttz += (
        f'      bodo.libs.array_kernels.setna(out_arr, {okems__xrlr})\n')
    qedfb__krttz += '      continue\n'
    qedfb__krttz += '    s = A[i]\n'
    qedfb__krttz += '    if bodo.libs.array_kernels.isna(A, i):\n'
    qedfb__krttz += '      s = last_value\n'
    qedfb__krttz += f'    out_arr[{okems__xrlr}] = s\n'
    qedfb__krttz += '    last_value = s\n'
    qedfb__krttz += '    has_last_value = True\n'
    if crzi__url:
        qedfb__krttz += '  return out_arr[::-1]\n'
    else:
        qedfb__krttz += '  return out_arr\n'
    ohqpl__luvn = {}
    exec(qedfb__krttz, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, ohqpl__luvn)
    impl = ohqpl__luvn['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        zstu__iuy = 0
        exvm__ivjtr = n_pes - 1
        tecy__jlrkt = np.int32(rank + 1)
        kkmr__qff = np.int32(rank - 1)
        gfj__ong = len(in_arr) - 1
        ehkey__usqx = -1
        fij__swv = -1
    else:
        zstu__iuy = n_pes - 1
        exvm__ivjtr = 0
        tecy__jlrkt = np.int32(rank - 1)
        kkmr__qff = np.int32(rank + 1)
        gfj__ong = 0
        ehkey__usqx = len(in_arr)
        fij__swv = 1
    cckuf__cst = np.int32(bodo.hiframes.rolling.comm_border_tag)
    ace__fvlo = np.empty(1, dtype=np.bool_)
    tdhbl__hfih = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    uumr__eul = np.empty(1, dtype=np.bool_)
    jct__kmdn = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    htnqg__bnaj = False
    tszc__kgon = null_value
    for i in range(gfj__ong, ehkey__usqx, fij__swv):
        if not isna(in_arr, i):
            htnqg__bnaj = True
            tszc__kgon = in_arr[i]
            break
    if rank != zstu__iuy:
        ewv__svpqi = bodo.libs.distributed_api.irecv(ace__fvlo, 1,
            kkmr__qff, cckuf__cst, True)
        bodo.libs.distributed_api.wait(ewv__svpqi, True)
        qlela__tmwu = bodo.libs.distributed_api.irecv(tdhbl__hfih, 1,
            kkmr__qff, cckuf__cst, True)
        bodo.libs.distributed_api.wait(qlela__tmwu, True)
        lze__pxyai = ace__fvlo[0]
        whcdi__dpfn = tdhbl__hfih[0]
    else:
        lze__pxyai = False
        whcdi__dpfn = null_value
    if htnqg__bnaj:
        uumr__eul[0] = htnqg__bnaj
        jct__kmdn[0] = tszc__kgon
    else:
        uumr__eul[0] = lze__pxyai
        jct__kmdn[0] = whcdi__dpfn
    if rank != exvm__ivjtr:
        oumy__djkj = bodo.libs.distributed_api.isend(uumr__eul, 1,
            tecy__jlrkt, cckuf__cst, True)
        qtpso__lvisw = bodo.libs.distributed_api.isend(jct__kmdn, 1,
            tecy__jlrkt, cckuf__cst, True)
    return lze__pxyai, whcdi__dpfn


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    yzs__avpk = {'axis': axis, 'kind': kind, 'order': order}
    xqig__rga = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', yzs__avpk, xqig__rga, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    fnk__hmc = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):
        if A == bodo.dict_str_arr_type:

            def impl_dict_int(A, repeats):
                data_arr = A._data.copy()
                wol__rqpz = A._indices
                kuuov__ibwmw = len(wol__rqpz)
                ufwi__huni = alloc_int_array(kuuov__ibwmw * repeats, np.int32)
                for i in range(kuuov__ibwmw):
                    okems__xrlr = i * repeats
                    if bodo.libs.array_kernels.isna(wol__rqpz, i):
                        for irzj__emu in range(repeats):
                            bodo.libs.array_kernels.setna(ufwi__huni, 
                                okems__xrlr + irzj__emu)
                    else:
                        ufwi__huni[okems__xrlr:okems__xrlr + repeats
                            ] = wol__rqpz[i]
                return init_dict_arr(data_arr, ufwi__huni, A.
                    _has_global_dictionary)
            return impl_dict_int

        def impl_int(A, repeats):
            kuuov__ibwmw = len(A)
            hbuye__npr = bodo.utils.utils.alloc_type(kuuov__ibwmw * repeats,
                fnk__hmc, (-1,))
            for i in range(kuuov__ibwmw):
                okems__xrlr = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for irzj__emu in range(repeats):
                        bodo.libs.array_kernels.setna(hbuye__npr, 
                            okems__xrlr + irzj__emu)
                else:
                    hbuye__npr[okems__xrlr:okems__xrlr + repeats] = A[i]
            return hbuye__npr
        return impl_int
    if A == bodo.dict_str_arr_type:

        def impl_dict_arr(A, repeats):
            data_arr = A._data.copy()
            wol__rqpz = A._indices
            kuuov__ibwmw = len(wol__rqpz)
            ufwi__huni = alloc_int_array(repeats.sum(), np.int32)
            okems__xrlr = 0
            for i in range(kuuov__ibwmw):
                atnfe__crm = repeats[i]
                if atnfe__crm < 0:
                    raise ValueError('repeats may not contain negative values.'
                        )
                if bodo.libs.array_kernels.isna(wol__rqpz, i):
                    for irzj__emu in range(atnfe__crm):
                        bodo.libs.array_kernels.setna(ufwi__huni, 
                            okems__xrlr + irzj__emu)
                else:
                    ufwi__huni[okems__xrlr:okems__xrlr + atnfe__crm
                        ] = wol__rqpz[i]
                okems__xrlr += atnfe__crm
            return init_dict_arr(data_arr, ufwi__huni, A._has_global_dictionary
                )
        return impl_dict_arr

    def impl_arr(A, repeats):
        kuuov__ibwmw = len(A)
        hbuye__npr = bodo.utils.utils.alloc_type(repeats.sum(), fnk__hmc, (-1,)
            )
        okems__xrlr = 0
        for i in range(kuuov__ibwmw):
            atnfe__crm = repeats[i]
            if atnfe__crm < 0:
                raise ValueError('repeats may not contain negative values.')
            if bodo.libs.array_kernels.isna(A, i):
                for irzj__emu in range(atnfe__crm):
                    bodo.libs.array_kernels.setna(hbuye__npr, okems__xrlr +
                        irzj__emu)
            else:
                hbuye__npr[okems__xrlr:okems__xrlr + atnfe__crm] = A[i]
            okems__xrlr += atnfe__crm
        return hbuye__npr
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@numba.generated_jit
def repeat_like(A, dist_like_arr):
    if not bodo.utils.utils.is_array_typ(A, False
        ) or not bodo.utils.utils.is_array_typ(dist_like_arr, False):
        raise BodoError('Both A and dist_like_arr must be array-like.')

    def impl(A, dist_like_arr):
        return bodo.libs.array_kernels.repeat_kernel(A, len(dist_like_arr))
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        phw__hvljp = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(phw__hvljp, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        tvk__daje = bodo.libs.array_kernels.concat([A1, A2])
        axzc__egbje = bodo.libs.array_kernels.unique(tvk__daje)
        return pd.Series(axzc__egbje).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    yzs__avpk = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    xqig__rga = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', yzs__avpk, xqig__rga, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        trf__krcn = bodo.libs.array_kernels.unique(A1)
        zejsc__lecus = bodo.libs.array_kernels.unique(A2)
        tvk__daje = bodo.libs.array_kernels.concat([trf__krcn, zejsc__lecus])
        xjee__yheyd = pd.Series(tvk__daje).sort_values().values
        return slice_array_intersect1d(xjee__yheyd)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    ptn__vepcx = arr[1:] == arr[:-1]
    return arr[:-1][ptn__vepcx]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    cckuf__cst = np.int32(bodo.hiframes.rolling.comm_border_tag)
    yxh__stgr = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        tarp__jiv = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), cckuf__cst, True)
        bodo.libs.distributed_api.wait(tarp__jiv, True)
    if rank == n_pes - 1:
        return None
    else:
        aidjh__obrtk = bodo.libs.distributed_api.irecv(yxh__stgr, 1, np.
            int32(rank + 1), cckuf__cst, True)
        bodo.libs.distributed_api.wait(aidjh__obrtk, True)
        return yxh__stgr[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    ptn__vepcx = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            ptn__vepcx[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        nts__qhy = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == nts__qhy:
            ptn__vepcx[n - 1] = True
    return ptn__vepcx


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    yzs__avpk = {'assume_unique': assume_unique}
    xqig__rga = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', yzs__avpk, xqig__rga, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        trf__krcn = bodo.libs.array_kernels.unique(A1)
        zejsc__lecus = bodo.libs.array_kernels.unique(A2)
        ptn__vepcx = calculate_mask_setdiff1d(trf__krcn, zejsc__lecus)
        return pd.Series(trf__krcn[ptn__vepcx]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    ptn__vepcx = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        ptn__vepcx &= A1 != A2[i]
    return ptn__vepcx


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    yzs__avpk = {'retstep': retstep, 'axis': axis}
    xqig__rga = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', yzs__avpk, xqig__rga, 'numpy')
    nfsh__bxo = False
    if is_overload_none(dtype):
        fnk__hmc = np.promote_types(np.promote_types(numba.np.numpy_support
            .as_dtype(start), numba.np.numpy_support.as_dtype(stop)), numba
            .np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            nfsh__bxo = True
        fnk__hmc = numba.np.numpy_support.as_dtype(dtype).type
    if nfsh__bxo:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            pkdf__pycf = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hbuye__npr = np.empty(num, fnk__hmc)
            for i in numba.parfors.parfor.internal_prange(num):
                hbuye__npr[i] = fnk__hmc(np.floor(start + i * pkdf__pycf))
            return hbuye__npr
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            pkdf__pycf = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hbuye__npr = np.empty(num, fnk__hmc)
            for i in numba.parfors.parfor.internal_prange(num):
                hbuye__npr[i] = fnk__hmc(start + i * pkdf__pycf)
            return hbuye__npr
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'np.contains()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        qxuf__qvjau = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                qxuf__qvjau += A[i] == val
        return qxuf__qvjau > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    yzs__avpk = {'axis': axis, 'out': out, 'keepdims': keepdims}
    xqig__rga = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', yzs__avpk, xqig__rga, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        qxuf__qvjau = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                qxuf__qvjau += int(bool(A[i]))
        return qxuf__qvjau > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    yzs__avpk = {'axis': axis, 'out': out, 'keepdims': keepdims}
    xqig__rga = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', yzs__avpk, xqig__rga, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        qxuf__qvjau = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                qxuf__qvjau += int(bool(A[i]))
        return qxuf__qvjau == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    yzs__avpk = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    xqig__rga = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', yzs__avpk, xqig__rga, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        npo__touj = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            hbuye__npr = np.empty(n, npo__touj)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(hbuye__npr, i)
                    continue
                hbuye__npr[i] = np_cbrt_scalar(A[i], npo__touj)
            return hbuye__npr
        return impl_arr
    npo__touj = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, npo__touj)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    dcr__ectqf = x < 0
    if dcr__ectqf:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if dcr__ectqf:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    zcfxp__btpr = isinstance(tup, (types.BaseTuple, types.List))
    phj__bbp = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for jchj__ifr in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(jchj__ifr
                , 'numpy.hstack()')
            zcfxp__btpr = zcfxp__btpr and bodo.utils.utils.is_array_typ(
                jchj__ifr, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        zcfxp__btpr = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif phj__bbp:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        lzmn__asao = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for jchj__ifr in lzmn__asao.types:
            phj__bbp = phj__bbp and bodo.utils.utils.is_array_typ(jchj__ifr,
                False)
    if not (zcfxp__btpr or phj__bbp):
        return
    if phj__bbp:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    yzs__avpk = {'check_valid': check_valid, 'tol': tol}
    xqig__rga = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', yzs__avpk,
        xqig__rga, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        cqrrt__omgak = mean.shape[0]
        jhqhk__gbcd = size, cqrrt__omgak
        zxriq__vij = np.random.standard_normal(jhqhk__gbcd)
        cov = cov.astype(np.float64)
        shwcq__fbfxm, s, mczb__kmmab = np.linalg.svd(cov)
        res = np.dot(zxriq__vij, np.sqrt(s).reshape(cqrrt__omgak, 1) *
            mczb__kmmab)
        cfqe__ajz = res + mean
        return cfqe__ajz
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            arzus__iuq = bodo.hiframes.series_kernels._get_type_max_value(arr)
            tkjqm__qyvmo = typing.builtins.IndexValue(-1, arzus__iuq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                luvuu__uxgo = typing.builtins.IndexValue(i, arr[i])
                tkjqm__qyvmo = min(tkjqm__qyvmo, luvuu__uxgo)
            return tkjqm__qyvmo.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        xvy__kkykj = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            dvwdk__ibvn = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            arzus__iuq = xvy__kkykj(len(arr.dtype.categories) + 1)
            tkjqm__qyvmo = typing.builtins.IndexValue(-1, arzus__iuq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                luvuu__uxgo = typing.builtins.IndexValue(i, dvwdk__ibvn[i])
                tkjqm__qyvmo = min(tkjqm__qyvmo, luvuu__uxgo)
            return tkjqm__qyvmo.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            arzus__iuq = bodo.hiframes.series_kernels._get_type_min_value(arr)
            tkjqm__qyvmo = typing.builtins.IndexValue(-1, arzus__iuq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                luvuu__uxgo = typing.builtins.IndexValue(i, arr[i])
                tkjqm__qyvmo = max(tkjqm__qyvmo, luvuu__uxgo)
            return tkjqm__qyvmo.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        xvy__kkykj = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            dvwdk__ibvn = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            arzus__iuq = xvy__kkykj(-1)
            tkjqm__qyvmo = typing.builtins.IndexValue(-1, arzus__iuq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                luvuu__uxgo = typing.builtins.IndexValue(i, dvwdk__ibvn[i])
                tkjqm__qyvmo = max(tkjqm__qyvmo, luvuu__uxgo)
            return tkjqm__qyvmo.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
