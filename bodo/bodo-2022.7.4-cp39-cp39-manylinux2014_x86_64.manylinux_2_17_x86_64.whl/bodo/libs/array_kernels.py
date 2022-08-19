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
from bodo.hiframes.time_ext import TimeArrayType
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
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_bin_arr_type, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
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
    if isinstance(arr, (IntegerArrayType, DecimalArrayType, TimeArrayType)
        ) or arr in (boolean_array, datetime_date_array_type,
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
        eysqg__ktnfm = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = eysqg__ktnfm
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        eysqg__ktnfm = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = eysqg__ktnfm
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
            pam__lmju = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            pam__lmju[ind + 1] = pam__lmju[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            pam__lmju = bodo.libs.array_item_arr_ext.get_offsets(arr)
            pam__lmju[ind + 1] = pam__lmju[ind]
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
    mooga__bho = arr_tup.count
    swz__vjxa = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(mooga__bho):
        swz__vjxa += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    swz__vjxa += '  return\n'
    zqp__amul = {}
    exec(swz__vjxa, {'setna': setna}, zqp__amul)
    impl = zqp__amul['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        uyqu__bkws = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(uyqu__bkws.start, uyqu__bkws.stop, uyqu__bkws.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        rwmew__nqi = 'n'
        nzy__ckoi = 'n_pes'
        ypbn__lma = 'min_op'
    else:
        rwmew__nqi = 'n-1, -1, -1'
        nzy__ckoi = '-1'
        ypbn__lma = 'max_op'
    swz__vjxa = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {nzy__ckoi}
    for i in range({rwmew__nqi}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {ypbn__lma}))
        if possible_valid_rank != {nzy__ckoi}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    zqp__amul = {}
    exec(swz__vjxa, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op': max_op,
        'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.box_if_dt64},
        zqp__amul)
    impl = zqp__amul['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    ald__piteu = array_to_info(arr)
    _median_series_computation(res, ald__piteu, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ald__piteu)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    ald__piteu = array_to_info(arr)
    _autocorr_series_computation(res, ald__piteu, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ald__piteu)


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
    ald__piteu = array_to_info(arr)
    _compute_series_monotonicity(res, ald__piteu, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ald__piteu)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    gyw__hjzki = res[0] > 0.5
    return gyw__hjzki


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        xwbo__vkhkc = '-'
        wzpit__twlof = 'index_arr[0] > threshhold_date'
        rwmew__nqi = '1, n+1'
        odg__eky = 'index_arr[-i] <= threshhold_date'
        femf__dcu = 'i - 1'
    else:
        xwbo__vkhkc = '+'
        wzpit__twlof = 'index_arr[-1] < threshhold_date'
        rwmew__nqi = 'n'
        odg__eky = 'index_arr[i] >= threshhold_date'
        femf__dcu = 'i'
    swz__vjxa = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        swz__vjxa += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        swz__vjxa += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            swz__vjxa += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            swz__vjxa += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            swz__vjxa += '    else:\n'
            swz__vjxa += '      threshhold_date = initial_date + date_offset\n'
        else:
            swz__vjxa += (
                f'    threshhold_date = initial_date {xwbo__vkhkc} date_offset\n'
                )
    else:
        swz__vjxa += f'  threshhold_date = initial_date {xwbo__vkhkc} offset\n'
    swz__vjxa += '  local_valid = 0\n'
    swz__vjxa += f'  n = len(index_arr)\n'
    swz__vjxa += f'  if n:\n'
    swz__vjxa += f'    if {wzpit__twlof}:\n'
    swz__vjxa += '      loc_valid = n\n'
    swz__vjxa += '    else:\n'
    swz__vjxa += f'      for i in range({rwmew__nqi}):\n'
    swz__vjxa += f'        if {odg__eky}:\n'
    swz__vjxa += f'          loc_valid = {femf__dcu}\n'
    swz__vjxa += '          break\n'
    swz__vjxa += '  if is_parallel:\n'
    swz__vjxa += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    swz__vjxa += '    return total_valid\n'
    swz__vjxa += '  else:\n'
    swz__vjxa += '    return loc_valid\n'
    zqp__amul = {}
    exec(swz__vjxa, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, zqp__amul)
    return zqp__amul['impl']


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
    unwlg__ajb = numba_to_c_type(sig.args[0].dtype)
    sutia__vkay = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), unwlg__ajb))
    lxcyp__frp = args[0]
    cpjwd__few = sig.args[0]
    if isinstance(cpjwd__few, (IntegerArrayType, BooleanArrayType)):
        lxcyp__frp = cgutils.create_struct_proxy(cpjwd__few)(context,
            builder, lxcyp__frp).data
        cpjwd__few = types.Array(cpjwd__few.dtype, 1, 'C')
    assert cpjwd__few.ndim == 1
    arr = make_array(cpjwd__few)(context, builder, lxcyp__frp)
    rcsd__zmg = builder.extract_value(arr.shape, 0)
    epbfp__itl = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        rcsd__zmg, args[1], builder.load(sutia__vkay)]
    yqev__ujb = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    vjb__dvf = lir.FunctionType(lir.DoubleType(), yqev__ujb)
    xzo__wpu = cgutils.get_or_insert_function(builder.module, vjb__dvf,
        name='quantile_sequential')
    jqub__jcnsm = builder.call(xzo__wpu, epbfp__itl)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return jqub__jcnsm


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    unwlg__ajb = numba_to_c_type(sig.args[0].dtype)
    sutia__vkay = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), unwlg__ajb))
    lxcyp__frp = args[0]
    cpjwd__few = sig.args[0]
    if isinstance(cpjwd__few, (IntegerArrayType, BooleanArrayType)):
        lxcyp__frp = cgutils.create_struct_proxy(cpjwd__few)(context,
            builder, lxcyp__frp).data
        cpjwd__few = types.Array(cpjwd__few.dtype, 1, 'C')
    assert cpjwd__few.ndim == 1
    arr = make_array(cpjwd__few)(context, builder, lxcyp__frp)
    rcsd__zmg = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        omo__qeisj = args[2]
    else:
        omo__qeisj = rcsd__zmg
    epbfp__itl = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        rcsd__zmg, omo__qeisj, args[1], builder.load(sutia__vkay)]
    yqev__ujb = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    vjb__dvf = lir.FunctionType(lir.DoubleType(), yqev__ujb)
    xzo__wpu = cgutils.get_or_insert_function(builder.module, vjb__dvf,
        name='quantile_parallel')
    jqub__jcnsm = builder.call(xzo__wpu, epbfp__itl)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return jqub__jcnsm


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        nzo__vuj = np.nonzero(pd.isna(arr))[0]
        slvlu__awrq = arr[1:] != arr[:-1]
        slvlu__awrq[pd.isna(slvlu__awrq)] = False
        tpjol__nwb = slvlu__awrq.astype(np.bool_)
        dmaq__pxr = np.concatenate((np.array([True]), tpjol__nwb))
        if nzo__vuj.size:
            mvc__hng, egq__res = nzo__vuj[0], nzo__vuj[1:]
            dmaq__pxr[mvc__hng] = True
            if egq__res.size:
                dmaq__pxr[egq__res] = False
                if egq__res[-1] + 1 < dmaq__pxr.size:
                    dmaq__pxr[egq__res[-1] + 1] = True
            elif mvc__hng + 1 < dmaq__pxr.size:
                dmaq__pxr[mvc__hng + 1] = True
        return dmaq__pxr
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
    swz__vjxa = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    swz__vjxa += '  na_idxs = pd.isna(arr)\n'
    swz__vjxa += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    swz__vjxa += '  nas = sum(na_idxs)\n'
    if not ascending:
        swz__vjxa += '  if nas and nas < (sorter.size - 1):\n'
        swz__vjxa += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        swz__vjxa += '  else:\n'
        swz__vjxa += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        swz__vjxa += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    swz__vjxa += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    swz__vjxa += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        swz__vjxa += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        swz__vjxa += '    inv,\n'
        swz__vjxa += '    new_dtype=np.float64,\n'
        swz__vjxa += '    copy=True,\n'
        swz__vjxa += '    nan_to_str=False,\n'
        swz__vjxa += '    from_series=True,\n'
        swz__vjxa += '    ) + 1\n'
    else:
        swz__vjxa += '  arr = arr[sorter]\n'
        swz__vjxa += '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n'
        swz__vjxa += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            swz__vjxa += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            swz__vjxa += '    dense,\n'
            swz__vjxa += '    new_dtype=np.float64,\n'
            swz__vjxa += '    copy=True,\n'
            swz__vjxa += '    nan_to_str=False,\n'
            swz__vjxa += '    from_series=True,\n'
            swz__vjxa += '  )\n'
        else:
            swz__vjxa += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            swz__vjxa += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                swz__vjxa += '  ret = count_float[dense]\n'
            elif method == 'min':
                swz__vjxa += '  ret = count_float[dense - 1] + 1\n'
            else:
                swz__vjxa += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                swz__vjxa += '  ret[na_idxs] = -1\n'
            swz__vjxa += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            swz__vjxa += '  div_val = arr.size - nas\n'
        else:
            swz__vjxa += '  div_val = arr.size\n'
        swz__vjxa += '  for i in range(len(ret)):\n'
        swz__vjxa += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        swz__vjxa += '  ret[na_idxs] = np.nan\n'
    swz__vjxa += '  return ret\n'
    zqp__amul = {}
    exec(swz__vjxa, {'np': np, 'pd': pd, 'bodo': bodo}, zqp__amul)
    return zqp__amul['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    gou__nneb = start
    xynuz__nphe = 2 * start + 1
    ljctg__notq = 2 * start + 2
    if xynuz__nphe < n and not cmp_f(arr[xynuz__nphe], arr[gou__nneb]):
        gou__nneb = xynuz__nphe
    if ljctg__notq < n and not cmp_f(arr[ljctg__notq], arr[gou__nneb]):
        gou__nneb = ljctg__notq
    if gou__nneb != start:
        arr[start], arr[gou__nneb] = arr[gou__nneb], arr[start]
        ind_arr[start], ind_arr[gou__nneb] = ind_arr[gou__nneb], ind_arr[start]
        min_heapify(arr, ind_arr, n, gou__nneb, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        belut__mdn = np.empty(k, A.dtype)
        sjlxm__pcjeb = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                belut__mdn[ind] = A[i]
                sjlxm__pcjeb[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            belut__mdn = belut__mdn[:ind]
            sjlxm__pcjeb = sjlxm__pcjeb[:ind]
        return belut__mdn, sjlxm__pcjeb, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        xhud__buzzc = np.sort(A)
        zbfm__wodw = index_arr[np.argsort(A)]
        hjlp__ekh = pd.Series(xhud__buzzc).notna().values
        xhud__buzzc = xhud__buzzc[hjlp__ekh]
        zbfm__wodw = zbfm__wodw[hjlp__ekh]
        if is_largest:
            xhud__buzzc = xhud__buzzc[::-1]
            zbfm__wodw = zbfm__wodw[::-1]
        return np.ascontiguousarray(xhud__buzzc), np.ascontiguousarray(
            zbfm__wodw)
    belut__mdn, sjlxm__pcjeb, start = select_k_nonan(A, index_arr, m, k)
    sjlxm__pcjeb = sjlxm__pcjeb[belut__mdn.argsort()]
    belut__mdn.sort()
    if not is_largest:
        belut__mdn = np.ascontiguousarray(belut__mdn[::-1])
        sjlxm__pcjeb = np.ascontiguousarray(sjlxm__pcjeb[::-1])
    for i in range(start, m):
        if cmp_f(A[i], belut__mdn[0]):
            belut__mdn[0] = A[i]
            sjlxm__pcjeb[0] = index_arr[i]
            min_heapify(belut__mdn, sjlxm__pcjeb, k, 0, cmp_f)
    sjlxm__pcjeb = sjlxm__pcjeb[belut__mdn.argsort()]
    belut__mdn.sort()
    if is_largest:
        belut__mdn = belut__mdn[::-1]
        sjlxm__pcjeb = sjlxm__pcjeb[::-1]
    return np.ascontiguousarray(belut__mdn), np.ascontiguousarray(sjlxm__pcjeb)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    pijqa__eilix = bodo.libs.distributed_api.get_rank()
    wfca__muat, wzvf__cfqie = nlargest(A, I, k, is_largest, cmp_f)
    zgg__xze = bodo.libs.distributed_api.gatherv(wfca__muat)
    ldtb__mwv = bodo.libs.distributed_api.gatherv(wzvf__cfqie)
    if pijqa__eilix == MPI_ROOT:
        res, gni__xomf = nlargest(zgg__xze, ldtb__mwv, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        gni__xomf = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(gni__xomf)
    return res, gni__xomf


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    fzl__dsrg, yidcg__kzqhi = mat.shape
    fmr__nwy = np.empty((yidcg__kzqhi, yidcg__kzqhi), dtype=np.float64)
    for ovgkc__vhlh in range(yidcg__kzqhi):
        for twl__wbja in range(ovgkc__vhlh + 1):
            bzjil__hazy = 0
            fym__olvw = yoiz__iboe = vqomm__iaktt = lslwe__avpep = 0.0
            for i in range(fzl__dsrg):
                if np.isfinite(mat[i, ovgkc__vhlh]) and np.isfinite(mat[i,
                    twl__wbja]):
                    omsz__twgqb = mat[i, ovgkc__vhlh]
                    pvatq__mkdms = mat[i, twl__wbja]
                    bzjil__hazy += 1
                    vqomm__iaktt += omsz__twgqb
                    lslwe__avpep += pvatq__mkdms
            if parallel:
                bzjil__hazy = bodo.libs.distributed_api.dist_reduce(bzjil__hazy
                    , sum_op)
                vqomm__iaktt = bodo.libs.distributed_api.dist_reduce(
                    vqomm__iaktt, sum_op)
                lslwe__avpep = bodo.libs.distributed_api.dist_reduce(
                    lslwe__avpep, sum_op)
            if bzjil__hazy < minpv:
                fmr__nwy[ovgkc__vhlh, twl__wbja] = fmr__nwy[twl__wbja,
                    ovgkc__vhlh] = np.nan
            else:
                wwzw__kjbo = vqomm__iaktt / bzjil__hazy
                oyjdf__krkd = lslwe__avpep / bzjil__hazy
                vqomm__iaktt = 0.0
                for i in range(fzl__dsrg):
                    if np.isfinite(mat[i, ovgkc__vhlh]) and np.isfinite(mat
                        [i, twl__wbja]):
                        omsz__twgqb = mat[i, ovgkc__vhlh] - wwzw__kjbo
                        pvatq__mkdms = mat[i, twl__wbja] - oyjdf__krkd
                        vqomm__iaktt += omsz__twgqb * pvatq__mkdms
                        fym__olvw += omsz__twgqb * omsz__twgqb
                        yoiz__iboe += pvatq__mkdms * pvatq__mkdms
                if parallel:
                    vqomm__iaktt = bodo.libs.distributed_api.dist_reduce(
                        vqomm__iaktt, sum_op)
                    fym__olvw = bodo.libs.distributed_api.dist_reduce(fym__olvw
                        , sum_op)
                    yoiz__iboe = bodo.libs.distributed_api.dist_reduce(
                        yoiz__iboe, sum_op)
                puau__vace = bzjil__hazy - 1.0 if cov else sqrt(fym__olvw *
                    yoiz__iboe)
                if puau__vace != 0.0:
                    fmr__nwy[ovgkc__vhlh, twl__wbja] = fmr__nwy[twl__wbja,
                        ovgkc__vhlh] = vqomm__iaktt / puau__vace
                else:
                    fmr__nwy[ovgkc__vhlh, twl__wbja] = fmr__nwy[twl__wbja,
                        ovgkc__vhlh] = np.nan
    return fmr__nwy


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    itnbk__ffvhd = n != 1
    swz__vjxa = 'def impl(data, parallel=False):\n'
    swz__vjxa += '  if parallel:\n'
    opjw__jbs = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    swz__vjxa += f'    cpp_table = arr_info_list_to_table([{opjw__jbs}])\n'
    swz__vjxa += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    eex__ihj = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    swz__vjxa += f'    data = ({eex__ihj},)\n'
    swz__vjxa += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    swz__vjxa += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    swz__vjxa += '    bodo.libs.array.delete_table(cpp_table)\n'
    swz__vjxa += '  n = len(data[0])\n'
    swz__vjxa += '  out = np.empty(n, np.bool_)\n'
    swz__vjxa += '  uniqs = dict()\n'
    if itnbk__ffvhd:
        swz__vjxa += '  for i in range(n):\n'
        seahn__row = ', '.join(f'data[{i}][i]' for i in range(n))
        hgy__muv = ',  '.join(f'bodo.libs.array_kernels.isna(data[{i}], i)' for
            i in range(n))
        swz__vjxa += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({seahn__row},), ({hgy__muv},))
"""
        swz__vjxa += '    if val in uniqs:\n'
        swz__vjxa += '      out[i] = True\n'
        swz__vjxa += '    else:\n'
        swz__vjxa += '      out[i] = False\n'
        swz__vjxa += '      uniqs[val] = 0\n'
    else:
        swz__vjxa += '  data = data[0]\n'
        swz__vjxa += '  hasna = False\n'
        swz__vjxa += '  for i in range(n):\n'
        swz__vjxa += '    if bodo.libs.array_kernels.isna(data, i):\n'
        swz__vjxa += '      out[i] = hasna\n'
        swz__vjxa += '      hasna = True\n'
        swz__vjxa += '    else:\n'
        swz__vjxa += '      val = data[i]\n'
        swz__vjxa += '      if val in uniqs:\n'
        swz__vjxa += '        out[i] = True\n'
        swz__vjxa += '      else:\n'
        swz__vjxa += '        out[i] = False\n'
        swz__vjxa += '        uniqs[val] = 0\n'
    swz__vjxa += '  if parallel:\n'
    swz__vjxa += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    swz__vjxa += '  return out\n'
    zqp__amul = {}
    exec(swz__vjxa, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, zqp__amul)
    impl = zqp__amul['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    mooga__bho = len(data)
    swz__vjxa = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    swz__vjxa += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        mooga__bho)))
    swz__vjxa += '  table_total = arr_info_list_to_table(info_list_total)\n'
    swz__vjxa += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(mooga__bho))
    for yssr__kwsd in range(mooga__bho):
        swz__vjxa += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(yssr__kwsd, yssr__kwsd, yssr__kwsd))
    swz__vjxa += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(mooga__bho))
    swz__vjxa += '  delete_table(out_table)\n'
    swz__vjxa += '  delete_table(table_total)\n'
    swz__vjxa += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(mooga__bho)))
    zqp__amul = {}
    exec(swz__vjxa, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, zqp__amul)
    impl = zqp__amul['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    mooga__bho = len(data)
    swz__vjxa = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    swz__vjxa += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        mooga__bho)))
    swz__vjxa += '  table_total = arr_info_list_to_table(info_list_total)\n'
    swz__vjxa += '  keep_i = 0\n'
    swz__vjxa += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for yssr__kwsd in range(mooga__bho):
        swz__vjxa += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(yssr__kwsd, yssr__kwsd, yssr__kwsd))
    swz__vjxa += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(mooga__bho))
    swz__vjxa += '  delete_table(out_table)\n'
    swz__vjxa += '  delete_table(table_total)\n'
    swz__vjxa += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(mooga__bho)))
    zqp__amul = {}
    exec(swz__vjxa, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zqp__amul)
    impl = zqp__amul['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        uxw__tpxnp = [array_to_info(data_arr)]
        evqhw__ilp = arr_info_list_to_table(uxw__tpxnp)
        hzwwa__nweti = 0
        wgo__jfv = drop_duplicates_table(evqhw__ilp, parallel, 1,
            hzwwa__nweti, False, True)
        elie__annq = info_to_array(info_from_table(wgo__jfv, 0), data_arr)
        delete_table(wgo__jfv)
        delete_table(evqhw__ilp)
        return elie__annq
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    eifym__ajz = len(data.types)
    msyb__lfxjq = [('out' + str(i)) for i in range(eifym__ajz)]
    sqi__oofem = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    rjxq__cft = ['isna(data[{}], i)'.format(i) for i in sqi__oofem]
    lblx__uufg = 'not ({})'.format(' or '.join(rjxq__cft))
    if not is_overload_none(thresh):
        lblx__uufg = '(({}) <= ({}) - thresh)'.format(' + '.join(rjxq__cft),
            eifym__ajz - 1)
    elif how == 'all':
        lblx__uufg = 'not ({})'.format(' and '.join(rjxq__cft))
    swz__vjxa = 'def _dropna_imp(data, how, thresh, subset):\n'
    swz__vjxa += '  old_len = len(data[0])\n'
    swz__vjxa += '  new_len = 0\n'
    swz__vjxa += '  for i in range(old_len):\n'
    swz__vjxa += '    if {}:\n'.format(lblx__uufg)
    swz__vjxa += '      new_len += 1\n'
    for i, out in enumerate(msyb__lfxjq):
        if isinstance(data[i], bodo.CategoricalArrayType):
            swz__vjxa += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            swz__vjxa += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    swz__vjxa += '  curr_ind = 0\n'
    swz__vjxa += '  for i in range(old_len):\n'
    swz__vjxa += '    if {}:\n'.format(lblx__uufg)
    for i in range(eifym__ajz):
        swz__vjxa += '      if isna(data[{}], i):\n'.format(i)
        swz__vjxa += '        setna({}, curr_ind)\n'.format(msyb__lfxjq[i])
        swz__vjxa += '      else:\n'
        swz__vjxa += '        {}[curr_ind] = data[{}][i]\n'.format(msyb__lfxjq
            [i], i)
    swz__vjxa += '      curr_ind += 1\n'
    swz__vjxa += '  return {}\n'.format(', '.join(msyb__lfxjq))
    zqp__amul = {}
    dheff__bjeey = {'t{}'.format(i): mady__yqyd for i, mady__yqyd in
        enumerate(data.types)}
    dheff__bjeey.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(swz__vjxa, dheff__bjeey, zqp__amul)
    cnyzh__xbay = zqp__amul['_dropna_imp']
    return cnyzh__xbay


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        cpjwd__few = arr.dtype
        eaq__ndi = cpjwd__few.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            crnkj__zsao = init_nested_counts(eaq__ndi)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                crnkj__zsao = add_nested_counts(crnkj__zsao, val[ind])
            elie__annq = bodo.utils.utils.alloc_type(n, cpjwd__few, crnkj__zsao
                )
            for hpdgr__vzhz in range(n):
                if bodo.libs.array_kernels.isna(arr, hpdgr__vzhz):
                    setna(elie__annq, hpdgr__vzhz)
                    continue
                val = arr[hpdgr__vzhz]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(elie__annq, hpdgr__vzhz)
                    continue
                elie__annq[hpdgr__vzhz] = val[ind]
            return elie__annq
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    xsbw__rjtih = _to_readonly(arr_types.types[0])
    return all(isinstance(mady__yqyd, CategoricalArrayType) and 
        _to_readonly(mady__yqyd) == xsbw__rjtih for mady__yqyd in arr_types
        .types)


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
        cdmx__raka = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            xpvf__wtyhu = 0
            wbk__pjef = []
            for A in arr_list:
                zgy__fbznh = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                wbk__pjef.append(bodo.libs.array_item_arr_ext.get_data(A))
                xpvf__wtyhu += zgy__fbznh
            easl__dwovl = np.empty(xpvf__wtyhu + 1, offset_type)
            mnbxg__bxpf = bodo.libs.array_kernels.concat(wbk__pjef)
            jrw__wqo = np.empty(xpvf__wtyhu + 7 >> 3, np.uint8)
            hraw__xhns = 0
            euxwl__nzh = 0
            for A in arr_list:
                vazmf__inzjn = bodo.libs.array_item_arr_ext.get_offsets(A)
                uivs__jaela = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                zgy__fbznh = len(A)
                xxnfy__ppbro = vazmf__inzjn[zgy__fbznh]
                for i in range(zgy__fbznh):
                    easl__dwovl[i + hraw__xhns] = vazmf__inzjn[i] + euxwl__nzh
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        uivs__jaela, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jrw__wqo, i +
                        hraw__xhns, zal__ukjf)
                hraw__xhns += zgy__fbznh
                euxwl__nzh += xxnfy__ppbro
            easl__dwovl[hraw__xhns] = euxwl__nzh
            elie__annq = bodo.libs.array_item_arr_ext.init_array_item_array(
                xpvf__wtyhu, mnbxg__bxpf, easl__dwovl, jrw__wqo)
            return elie__annq
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        ffc__devyf = arr_list.dtype.names
        swz__vjxa = 'def struct_array_concat_impl(arr_list):\n'
        swz__vjxa += f'    n_all = 0\n'
        for i in range(len(ffc__devyf)):
            swz__vjxa += f'    concat_list{i} = []\n'
        swz__vjxa += '    for A in arr_list:\n'
        swz__vjxa += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(ffc__devyf)):
            swz__vjxa += f'        concat_list{i}.append(data_tuple[{i}])\n'
        swz__vjxa += '        n_all += len(A)\n'
        swz__vjxa += '    n_bytes = (n_all + 7) >> 3\n'
        swz__vjxa += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        swz__vjxa += '    curr_bit = 0\n'
        swz__vjxa += '    for A in arr_list:\n'
        swz__vjxa += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        swz__vjxa += '        for j in range(len(A)):\n'
        swz__vjxa += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        swz__vjxa += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        swz__vjxa += '            curr_bit += 1\n'
        swz__vjxa += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        byc__skoq = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(ffc__devyf))])
        swz__vjxa += f'        ({byc__skoq},),\n'
        swz__vjxa += '        new_mask,\n'
        swz__vjxa += f'        {ffc__devyf},\n'
        swz__vjxa += '    )\n'
        zqp__amul = {}
        exec(swz__vjxa, {'bodo': bodo, 'np': np}, zqp__amul)
        return zqp__amul['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            sutqb__izyk = 0
            for A in arr_list:
                sutqb__izyk += len(A)
            rdndu__wzily = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(sutqb__izyk))
            qea__mpzl = 0
            for A in arr_list:
                for i in range(len(A)):
                    rdndu__wzily._data[i + qea__mpzl] = A._data[i]
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(rdndu__wzily.
                        _null_bitmap, i + qea__mpzl, zal__ukjf)
                qea__mpzl += len(A)
            return rdndu__wzily
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            sutqb__izyk = 0
            for A in arr_list:
                sutqb__izyk += len(A)
            rdndu__wzily = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(sutqb__izyk))
            qea__mpzl = 0
            for A in arr_list:
                for i in range(len(A)):
                    rdndu__wzily._days_data[i + qea__mpzl] = A._days_data[i]
                    rdndu__wzily._seconds_data[i + qea__mpzl
                        ] = A._seconds_data[i]
                    rdndu__wzily._microseconds_data[i + qea__mpzl
                        ] = A._microseconds_data[i]
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(rdndu__wzily.
                        _null_bitmap, i + qea__mpzl, zal__ukjf)
                qea__mpzl += len(A)
            return rdndu__wzily
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        xub__cvane = arr_list.dtype.precision
        gza__kmp = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            sutqb__izyk = 0
            for A in arr_list:
                sutqb__izyk += len(A)
            rdndu__wzily = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                sutqb__izyk, xub__cvane, gza__kmp)
            qea__mpzl = 0
            for A in arr_list:
                for i in range(len(A)):
                    rdndu__wzily._data[i + qea__mpzl] = A._data[i]
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(rdndu__wzily.
                        _null_bitmap, i + qea__mpzl, zal__ukjf)
                qea__mpzl += len(A)
            return rdndu__wzily
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        mady__yqyd) for mady__yqyd in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            mpuqm__vgtm = arr_list.types[0]
        else:
            mpuqm__vgtm = arr_list.dtype
        mpuqm__vgtm = to_str_arr_if_dict_array(mpuqm__vgtm)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            okfg__kwqqj = 0
            ugv__puqf = 0
            for A in arr_list:
                arr = A
                okfg__kwqqj += len(arr)
                ugv__puqf += bodo.libs.str_arr_ext.num_total_chars(arr)
            elie__annq = bodo.utils.utils.alloc_type(okfg__kwqqj,
                mpuqm__vgtm, (ugv__puqf,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(elie__annq, -1)
            yqgct__ufg = 0
            mjbxw__xofbe = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(elie__annq,
                    arr, yqgct__ufg, mjbxw__xofbe)
                yqgct__ufg += len(arr)
                mjbxw__xofbe += bodo.libs.str_arr_ext.num_total_chars(arr)
            return elie__annq
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(mady__yqyd.dtype, types.Integer) for
        mady__yqyd in arr_list.types) and any(isinstance(mady__yqyd,
        IntegerArrayType) for mady__yqyd in arr_list.types):

        def impl_int_arr_list(arr_list):
            jrib__jopf = convert_to_nullable_tup(arr_list)
            wqyt__cow = []
            ggy__hmz = 0
            for A in jrib__jopf:
                wqyt__cow.append(A._data)
                ggy__hmz += len(A)
            mnbxg__bxpf = bodo.libs.array_kernels.concat(wqyt__cow)
            djg__erj = ggy__hmz + 7 >> 3
            yxlai__afbut = np.empty(djg__erj, np.uint8)
            yhex__owdy = 0
            for A in jrib__jopf:
                ext__hlyou = A._null_bitmap
                for hpdgr__vzhz in range(len(A)):
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ext__hlyou, hpdgr__vzhz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yxlai__afbut,
                        yhex__owdy, zal__ukjf)
                    yhex__owdy += 1
            return bodo.libs.int_arr_ext.init_integer_array(mnbxg__bxpf,
                yxlai__afbut)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(mady__yqyd.dtype == types.bool_ for mady__yqyd in
        arr_list.types) and any(mady__yqyd == boolean_array for mady__yqyd in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            jrib__jopf = convert_to_nullable_tup(arr_list)
            wqyt__cow = []
            ggy__hmz = 0
            for A in jrib__jopf:
                wqyt__cow.append(A._data)
                ggy__hmz += len(A)
            mnbxg__bxpf = bodo.libs.array_kernels.concat(wqyt__cow)
            djg__erj = ggy__hmz + 7 >> 3
            yxlai__afbut = np.empty(djg__erj, np.uint8)
            yhex__owdy = 0
            for A in jrib__jopf:
                ext__hlyou = A._null_bitmap
                for hpdgr__vzhz in range(len(A)):
                    zal__ukjf = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ext__hlyou, hpdgr__vzhz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yxlai__afbut,
                        yhex__owdy, zal__ukjf)
                    yhex__owdy += 1
            return bodo.libs.bool_arr_ext.init_bool_array(mnbxg__bxpf,
                yxlai__afbut)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            atiwv__yps = []
            for A in arr_list:
                atiwv__yps.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                atiwv__yps), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        jmf__ixuz = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        swz__vjxa = 'def impl(arr_list):\n'
        swz__vjxa += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({jmf__ixuz},)), arr_list[0].dtype)
"""
        ftyxm__vcvh = {}
        exec(swz__vjxa, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, ftyxm__vcvh)
        return ftyxm__vcvh['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            ggy__hmz = 0
            for A in arr_list:
                ggy__hmz += len(A)
            elie__annq = np.empty(ggy__hmz, dtype)
            lri__qyluk = 0
            for A in arr_list:
                n = len(A)
                elie__annq[lri__qyluk:lri__qyluk + n] = A
                lri__qyluk += n
            return elie__annq
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(mady__yqyd,
        (types.Array, IntegerArrayType)) and isinstance(mady__yqyd.dtype,
        types.Integer) for mady__yqyd in arr_list.types) and any(isinstance
        (mady__yqyd, types.Array) and isinstance(mady__yqyd.dtype, types.
        Float) for mady__yqyd in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            mcrv__cmvk = []
            for A in arr_list:
                mcrv__cmvk.append(A._data)
            uioc__kzsw = bodo.libs.array_kernels.concat(mcrv__cmvk)
            fmr__nwy = bodo.libs.map_arr_ext.init_map_arr(uioc__kzsw)
            return fmr__nwy
        return impl_map_arr_list
    for tguq__abs in arr_list:
        if not isinstance(tguq__abs, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(mady__yqyd.astype(np.float64) for mady__yqyd in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    mooga__bho = len(arr_tup.types)
    swz__vjxa = 'def f(arr_tup):\n'
    swz__vjxa += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        mooga__bho)), ',' if mooga__bho == 1 else '')
    zqp__amul = {}
    exec(swz__vjxa, {'np': np}, zqp__amul)
    teg__ctp = zqp__amul['f']
    return teg__ctp


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    mooga__bho = len(arr_tup.types)
    unag__ldapm = find_common_np_dtype(arr_tup.types)
    eaq__ndi = None
    uap__eor = ''
    if isinstance(unag__ldapm, types.Integer):
        eaq__ndi = bodo.libs.int_arr_ext.IntDtype(unag__ldapm)
        uap__eor = '.astype(out_dtype, False)'
    swz__vjxa = 'def f(arr_tup):\n'
    swz__vjxa += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, uap__eor) for i in range(mooga__bho)), ',' if mooga__bho ==
        1 else '')
    zqp__amul = {}
    exec(swz__vjxa, {'bodo': bodo, 'out_dtype': eaq__ndi}, zqp__amul)
    qsw__titui = zqp__amul['f']
    return qsw__titui


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, shsuf__vusw = build_set_seen_na(A)
        return len(s) + int(not dropna and shsuf__vusw)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        tzwaw__txbg = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        krttt__wcgw = len(tzwaw__txbg)
        return bodo.libs.distributed_api.dist_reduce(krttt__wcgw, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([smll__hcej for smll__hcej in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        vhfzd__isibu = np.finfo(A.dtype(1).dtype).max
    else:
        vhfzd__isibu = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        elie__annq = np.empty(n, A.dtype)
        yerdj__trhn = vhfzd__isibu
        for i in range(n):
            yerdj__trhn = min(yerdj__trhn, A[i])
            elie__annq[i] = yerdj__trhn
        return elie__annq
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        vhfzd__isibu = np.finfo(A.dtype(1).dtype).min
    else:
        vhfzd__isibu = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        elie__annq = np.empty(n, A.dtype)
        yerdj__trhn = vhfzd__isibu
        for i in range(n):
            yerdj__trhn = max(yerdj__trhn, A[i])
            elie__annq[i] = yerdj__trhn
        return elie__annq
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        iakp__rphi = arr_info_list_to_table([array_to_info(A)])
        qak__pluej = 1
        hzwwa__nweti = 0
        wgo__jfv = drop_duplicates_table(iakp__rphi, parallel, qak__pluej,
            hzwwa__nweti, dropna, True)
        elie__annq = info_to_array(info_from_table(wgo__jfv, 0), A)
        delete_table(iakp__rphi)
        delete_table(wgo__jfv)
        return elie__annq
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    cdmx__raka = bodo.utils.typing.to_nullable_type(arr.dtype)
    rwup__cwg = index_arr
    zhnpy__enpzp = rwup__cwg.dtype

    def impl(arr, index_arr):
        n = len(arr)
        crnkj__zsao = init_nested_counts(cdmx__raka)
        mryn__qslm = init_nested_counts(zhnpy__enpzp)
        for i in range(n):
            hrouz__oefh = index_arr[i]
            if isna(arr, i):
                crnkj__zsao = (crnkj__zsao[0] + 1,) + crnkj__zsao[1:]
                mryn__qslm = add_nested_counts(mryn__qslm, hrouz__oefh)
                continue
            wavat__pttm = arr[i]
            if len(wavat__pttm) == 0:
                crnkj__zsao = (crnkj__zsao[0] + 1,) + crnkj__zsao[1:]
                mryn__qslm = add_nested_counts(mryn__qslm, hrouz__oefh)
                continue
            crnkj__zsao = add_nested_counts(crnkj__zsao, wavat__pttm)
            for qsl__jgwkk in range(len(wavat__pttm)):
                mryn__qslm = add_nested_counts(mryn__qslm, hrouz__oefh)
        elie__annq = bodo.utils.utils.alloc_type(crnkj__zsao[0], cdmx__raka,
            crnkj__zsao[1:])
        fpgx__rwz = bodo.utils.utils.alloc_type(crnkj__zsao[0], rwup__cwg,
            mryn__qslm)
        euxwl__nzh = 0
        for i in range(n):
            if isna(arr, i):
                setna(elie__annq, euxwl__nzh)
                fpgx__rwz[euxwl__nzh] = index_arr[i]
                euxwl__nzh += 1
                continue
            wavat__pttm = arr[i]
            xxnfy__ppbro = len(wavat__pttm)
            if xxnfy__ppbro == 0:
                setna(elie__annq, euxwl__nzh)
                fpgx__rwz[euxwl__nzh] = index_arr[i]
                euxwl__nzh += 1
                continue
            elie__annq[euxwl__nzh:euxwl__nzh + xxnfy__ppbro] = wavat__pttm
            fpgx__rwz[euxwl__nzh:euxwl__nzh + xxnfy__ppbro] = index_arr[i]
            euxwl__nzh += xxnfy__ppbro
        return elie__annq, fpgx__rwz
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    cdmx__raka = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        crnkj__zsao = init_nested_counts(cdmx__raka)
        for i in range(n):
            if isna(arr, i):
                crnkj__zsao = (crnkj__zsao[0] + 1,) + crnkj__zsao[1:]
                xmnf__kvbzy = 1
            else:
                wavat__pttm = arr[i]
                uhbgx__lmci = len(wavat__pttm)
                if uhbgx__lmci == 0:
                    crnkj__zsao = (crnkj__zsao[0] + 1,) + crnkj__zsao[1:]
                    xmnf__kvbzy = 1
                    continue
                else:
                    crnkj__zsao = add_nested_counts(crnkj__zsao, wavat__pttm)
                    xmnf__kvbzy = uhbgx__lmci
            if counts[i] != xmnf__kvbzy:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        elie__annq = bodo.utils.utils.alloc_type(crnkj__zsao[0], cdmx__raka,
            crnkj__zsao[1:])
        euxwl__nzh = 0
        for i in range(n):
            if isna(arr, i):
                setna(elie__annq, euxwl__nzh)
                euxwl__nzh += 1
                continue
            wavat__pttm = arr[i]
            xxnfy__ppbro = len(wavat__pttm)
            if xxnfy__ppbro == 0:
                setna(elie__annq, euxwl__nzh)
                euxwl__nzh += 1
                continue
            elie__annq[euxwl__nzh:euxwl__nzh + xxnfy__ppbro] = wavat__pttm
            euxwl__nzh += xxnfy__ppbro
        return elie__annq
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(xjoog__twss) for xjoog__twss in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one or is_bin_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        lucyg__ywk = 'np.empty(n, np.int64)'
        dejn__dyssz = 'out_arr[i] = 1'
        zrg__mqn = 'max(len(arr[i]), 1)'
    else:
        lucyg__ywk = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        dejn__dyssz = 'bodo.libs.array_kernels.setna(out_arr, i)'
        zrg__mqn = 'len(arr[i])'
    swz__vjxa = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {lucyg__ywk}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {dejn__dyssz}
        else:
            out_arr[i] = {zrg__mqn}
    return out_arr
    """
    zqp__amul = {}
    exec(swz__vjxa, {'bodo': bodo, 'numba': numba, 'np': np}, zqp__amul)
    impl = zqp__amul['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    rwup__cwg = index_arr
    zhnpy__enpzp = rwup__cwg.dtype

    def impl(arr, pat, n, index_arr):
        adop__iuuz = pat is not None and len(pat) > 1
        if adop__iuuz:
            uphmr__dhxl = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        tejj__hul = len(arr)
        okfg__kwqqj = 0
        ugv__puqf = 0
        mryn__qslm = init_nested_counts(zhnpy__enpzp)
        for i in range(tejj__hul):
            hrouz__oefh = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                okfg__kwqqj += 1
                mryn__qslm = add_nested_counts(mryn__qslm, hrouz__oefh)
                continue
            if adop__iuuz:
                coelq__tnz = uphmr__dhxl.split(arr[i], maxsplit=n)
            else:
                coelq__tnz = arr[i].split(pat, n)
            okfg__kwqqj += len(coelq__tnz)
            for s in coelq__tnz:
                mryn__qslm = add_nested_counts(mryn__qslm, hrouz__oefh)
                ugv__puqf += bodo.libs.str_arr_ext.get_utf8_size(s)
        elie__annq = bodo.libs.str_arr_ext.pre_alloc_string_array(okfg__kwqqj,
            ugv__puqf)
        fpgx__rwz = bodo.utils.utils.alloc_type(okfg__kwqqj, rwup__cwg,
            mryn__qslm)
        was__ynxmf = 0
        for hpdgr__vzhz in range(tejj__hul):
            if isna(arr, hpdgr__vzhz):
                elie__annq[was__ynxmf] = ''
                bodo.libs.array_kernels.setna(elie__annq, was__ynxmf)
                fpgx__rwz[was__ynxmf] = index_arr[hpdgr__vzhz]
                was__ynxmf += 1
                continue
            if adop__iuuz:
                coelq__tnz = uphmr__dhxl.split(arr[hpdgr__vzhz], maxsplit=n)
            else:
                coelq__tnz = arr[hpdgr__vzhz].split(pat, n)
            skfn__eor = len(coelq__tnz)
            elie__annq[was__ynxmf:was__ynxmf + skfn__eor] = coelq__tnz
            fpgx__rwz[was__ynxmf:was__ynxmf + skfn__eor] = index_arr[
                hpdgr__vzhz]
            was__ynxmf += skfn__eor
        return elie__annq, fpgx__rwz
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
            elie__annq = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                elie__annq[i] = np.nan
            return elie__annq
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            vaz__saf = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            xla__alyn = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(xla__alyn, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(vaz__saf, xla__alyn,
                True)
        return impl_dict
    ett__ccdz = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        elie__annq = bodo.utils.utils.alloc_type(n, ett__ccdz, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(elie__annq, i)
        return elie__annq
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
    vnksd__eox = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            elie__annq = bodo.utils.utils.alloc_type(new_len, vnksd__eox)
            bodo.libs.str_arr_ext.str_copy_ptr(elie__annq.ctypes, 0, A.
                ctypes, old_size)
            return elie__annq
        return impl_char

    def impl(A, old_size, new_len):
        elie__annq = bodo.utils.utils.alloc_type(new_len, vnksd__eox, (-1,))
        elie__annq[:old_size] = A[:old_size]
        return elie__annq
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    caccc__bmrtv = math.ceil((stop - start) / step)
    return int(max(caccc__bmrtv, 0))


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
    if any(isinstance(smll__hcej, types.Complex) for smll__hcej in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            intu__dqt = (stop - start) / step
            caccc__bmrtv = math.ceil(intu__dqt.real)
            ttov__kme = math.ceil(intu__dqt.imag)
            vjm__ysju = int(max(min(ttov__kme, caccc__bmrtv), 0))
            arr = np.empty(vjm__ysju, dtype)
            for i in numba.parfors.parfor.internal_prange(vjm__ysju):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            vjm__ysju = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(vjm__ysju, dtype)
            for i in numba.parfors.parfor.internal_prange(vjm__ysju):
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
        mwu__fem = arr,
        if not inplace:
            mwu__fem = arr.copy(),
        uut__efj = bodo.libs.str_arr_ext.to_list_if_immutable_arr(mwu__fem)
        cgq__ofgs = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(uut__efj, 0, n, cgq__ofgs)
        if not ascending:
            bodo.libs.timsort.reverseRange(uut__efj, 0, n, cgq__ofgs)
        bodo.libs.str_arr_ext.cp_str_list_to_array(mwu__fem, uut__efj)
        return mwu__fem[0]
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
        fmr__nwy = []
        for i in range(n):
            if A[i]:
                fmr__nwy.append(i + offset)
        return np.array(fmr__nwy, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    vnksd__eox = element_type(A)
    if vnksd__eox == types.unicode_type:
        null_value = '""'
    elif vnksd__eox == types.bool_:
        null_value = 'False'
    elif vnksd__eox == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif vnksd__eox == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    was__ynxmf = 'i'
    ozyg__egi = False
    ofyve__klhpc = get_overload_const_str(method)
    if ofyve__klhpc in ('ffill', 'pad'):
        wlpe__xojpc = 'n'
        send_right = True
    elif ofyve__klhpc in ('backfill', 'bfill'):
        wlpe__xojpc = 'n-1, -1, -1'
        send_right = False
        if vnksd__eox == types.unicode_type:
            was__ynxmf = '(n - 1) - i'
            ozyg__egi = True
    swz__vjxa = 'def impl(A, method, parallel=False):\n'
    swz__vjxa += '  A = decode_if_dict_array(A)\n'
    swz__vjxa += '  has_last_value = False\n'
    swz__vjxa += f'  last_value = {null_value}\n'
    swz__vjxa += '  if parallel:\n'
    swz__vjxa += '    rank = bodo.libs.distributed_api.get_rank()\n'
    swz__vjxa += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    swz__vjxa += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    swz__vjxa += '  n = len(A)\n'
    swz__vjxa += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    swz__vjxa += f'  for i in range({wlpe__xojpc}):\n'
    swz__vjxa += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    swz__vjxa += (
        f'      bodo.libs.array_kernels.setna(out_arr, {was__ynxmf})\n')
    swz__vjxa += '      continue\n'
    swz__vjxa += '    s = A[i]\n'
    swz__vjxa += '    if bodo.libs.array_kernels.isna(A, i):\n'
    swz__vjxa += '      s = last_value\n'
    swz__vjxa += f'    out_arr[{was__ynxmf}] = s\n'
    swz__vjxa += '    last_value = s\n'
    swz__vjxa += '    has_last_value = True\n'
    if ozyg__egi:
        swz__vjxa += '  return out_arr[::-1]\n'
    else:
        swz__vjxa += '  return out_arr\n'
    pliy__arxgh = {}
    exec(swz__vjxa, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, pliy__arxgh)
    impl = pliy__arxgh['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        hdpfj__gsdnu = 0
        ttcsn__ftp = n_pes - 1
        eotc__mqxul = np.int32(rank + 1)
        pdi__jrsi = np.int32(rank - 1)
        ytf__cjv = len(in_arr) - 1
        rdb__xxbfx = -1
        gnyvk__egrji = -1
    else:
        hdpfj__gsdnu = n_pes - 1
        ttcsn__ftp = 0
        eotc__mqxul = np.int32(rank - 1)
        pdi__jrsi = np.int32(rank + 1)
        ytf__cjv = 0
        rdb__xxbfx = len(in_arr)
        gnyvk__egrji = 1
    nwkdq__xqdg = np.int32(bodo.hiframes.rolling.comm_border_tag)
    edwh__dlq = np.empty(1, dtype=np.bool_)
    gjvt__lhmk = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    gso__crqz = np.empty(1, dtype=np.bool_)
    jruc__wcre = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    xgk__duyev = False
    ldrh__arkc = null_value
    for i in range(ytf__cjv, rdb__xxbfx, gnyvk__egrji):
        if not isna(in_arr, i):
            xgk__duyev = True
            ldrh__arkc = in_arr[i]
            break
    if rank != hdpfj__gsdnu:
        bksg__goq = bodo.libs.distributed_api.irecv(edwh__dlq, 1, pdi__jrsi,
            nwkdq__xqdg, True)
        bodo.libs.distributed_api.wait(bksg__goq, True)
        ktfo__eptkh = bodo.libs.distributed_api.irecv(gjvt__lhmk, 1,
            pdi__jrsi, nwkdq__xqdg, True)
        bodo.libs.distributed_api.wait(ktfo__eptkh, True)
        cvk__nuan = edwh__dlq[0]
        sfyhk__odacn = gjvt__lhmk[0]
    else:
        cvk__nuan = False
        sfyhk__odacn = null_value
    if xgk__duyev:
        gso__crqz[0] = xgk__duyev
        jruc__wcre[0] = ldrh__arkc
    else:
        gso__crqz[0] = cvk__nuan
        jruc__wcre[0] = sfyhk__odacn
    if rank != ttcsn__ftp:
        zqpgm__nhrs = bodo.libs.distributed_api.isend(gso__crqz, 1,
            eotc__mqxul, nwkdq__xqdg, True)
        mrvk__xjuxt = bodo.libs.distributed_api.isend(jruc__wcre, 1,
            eotc__mqxul, nwkdq__xqdg, True)
    return cvk__nuan, sfyhk__odacn


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    cfreh__ewxaf = {'axis': axis, 'kind': kind, 'order': order}
    nwpd__odxzz = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', cfreh__ewxaf, nwpd__odxzz, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    vnksd__eox = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):
        if A == bodo.dict_str_arr_type:

            def impl_dict_int(A, repeats):
                data_arr = A._data.copy()
                ulhmb__ohf = A._indices
                tejj__hul = len(ulhmb__ohf)
                uqoik__gggfm = alloc_int_array(tejj__hul * repeats, np.int32)
                for i in range(tejj__hul):
                    was__ynxmf = i * repeats
                    if bodo.libs.array_kernels.isna(ulhmb__ohf, i):
                        for hpdgr__vzhz in range(repeats):
                            bodo.libs.array_kernels.setna(uqoik__gggfm, 
                                was__ynxmf + hpdgr__vzhz)
                    else:
                        uqoik__gggfm[was__ynxmf:was__ynxmf + repeats
                            ] = ulhmb__ohf[i]
                return init_dict_arr(data_arr, uqoik__gggfm, A.
                    _has_global_dictionary)
            return impl_dict_int

        def impl_int(A, repeats):
            tejj__hul = len(A)
            elie__annq = bodo.utils.utils.alloc_type(tejj__hul * repeats,
                vnksd__eox, (-1,))
            for i in range(tejj__hul):
                was__ynxmf = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for hpdgr__vzhz in range(repeats):
                        bodo.libs.array_kernels.setna(elie__annq, 
                            was__ynxmf + hpdgr__vzhz)
                else:
                    elie__annq[was__ynxmf:was__ynxmf + repeats] = A[i]
            return elie__annq
        return impl_int
    if A == bodo.dict_str_arr_type:

        def impl_dict_arr(A, repeats):
            data_arr = A._data.copy()
            ulhmb__ohf = A._indices
            tejj__hul = len(ulhmb__ohf)
            uqoik__gggfm = alloc_int_array(repeats.sum(), np.int32)
            was__ynxmf = 0
            for i in range(tejj__hul):
                xztts__cchg = repeats[i]
                if xztts__cchg < 0:
                    raise ValueError('repeats may not contain negative values.'
                        )
                if bodo.libs.array_kernels.isna(ulhmb__ohf, i):
                    for hpdgr__vzhz in range(xztts__cchg):
                        bodo.libs.array_kernels.setna(uqoik__gggfm, 
                            was__ynxmf + hpdgr__vzhz)
                else:
                    uqoik__gggfm[was__ynxmf:was__ynxmf + xztts__cchg
                        ] = ulhmb__ohf[i]
                was__ynxmf += xztts__cchg
            return init_dict_arr(data_arr, uqoik__gggfm, A.
                _has_global_dictionary)
        return impl_dict_arr

    def impl_arr(A, repeats):
        tejj__hul = len(A)
        elie__annq = bodo.utils.utils.alloc_type(repeats.sum(), vnksd__eox,
            (-1,))
        was__ynxmf = 0
        for i in range(tejj__hul):
            xztts__cchg = repeats[i]
            if xztts__cchg < 0:
                raise ValueError('repeats may not contain negative values.')
            if bodo.libs.array_kernels.isna(A, i):
                for hpdgr__vzhz in range(xztts__cchg):
                    bodo.libs.array_kernels.setna(elie__annq, was__ynxmf +
                        hpdgr__vzhz)
            else:
                elie__annq[was__ynxmf:was__ynxmf + xztts__cchg] = A[i]
            was__ynxmf += xztts__cchg
        return elie__annq
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
        qiqjg__gzxvf = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(qiqjg__gzxvf, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        wosdn__iabb = bodo.libs.array_kernels.concat([A1, A2])
        bncu__uhav = bodo.libs.array_kernels.unique(wosdn__iabb)
        return pd.Series(bncu__uhav).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    cfreh__ewxaf = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    nwpd__odxzz = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', cfreh__ewxaf, nwpd__odxzz, 'numpy'
        )
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        vpgx__dfna = bodo.libs.array_kernels.unique(A1)
        xvi__npc = bodo.libs.array_kernels.unique(A2)
        wosdn__iabb = bodo.libs.array_kernels.concat([vpgx__dfna, xvi__npc])
        cpyn__qwoy = pd.Series(wosdn__iabb).sort_values().values
        return slice_array_intersect1d(cpyn__qwoy)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    hjlp__ekh = arr[1:] == arr[:-1]
    return arr[:-1][hjlp__ekh]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    nwkdq__xqdg = np.int32(bodo.hiframes.rolling.comm_border_tag)
    tjnns__npqtd = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        zdwd__mfkcs = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), nwkdq__xqdg, True)
        bodo.libs.distributed_api.wait(zdwd__mfkcs, True)
    if rank == n_pes - 1:
        return None
    else:
        cyvc__zdo = bodo.libs.distributed_api.irecv(tjnns__npqtd, 1, np.
            int32(rank + 1), nwkdq__xqdg, True)
        bodo.libs.distributed_api.wait(cyvc__zdo, True)
        return tjnns__npqtd[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    hjlp__ekh = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            hjlp__ekh[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        iqiri__tcz = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == iqiri__tcz:
            hjlp__ekh[n - 1] = True
    return hjlp__ekh


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    cfreh__ewxaf = {'assume_unique': assume_unique}
    nwpd__odxzz = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', cfreh__ewxaf, nwpd__odxzz, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        vpgx__dfna = bodo.libs.array_kernels.unique(A1)
        xvi__npc = bodo.libs.array_kernels.unique(A2)
        hjlp__ekh = calculate_mask_setdiff1d(vpgx__dfna, xvi__npc)
        return pd.Series(vpgx__dfna[hjlp__ekh]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    hjlp__ekh = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        hjlp__ekh &= A1 != A2[i]
    return hjlp__ekh


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    cfreh__ewxaf = {'retstep': retstep, 'axis': axis}
    nwpd__odxzz = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', cfreh__ewxaf, nwpd__odxzz, 'numpy')
    qmf__xdyrj = False
    if is_overload_none(dtype):
        vnksd__eox = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            qmf__xdyrj = True
        vnksd__eox = numba.np.numpy_support.as_dtype(dtype).type
    if qmf__xdyrj:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            isslu__uvj = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            elie__annq = np.empty(num, vnksd__eox)
            for i in numba.parfors.parfor.internal_prange(num):
                elie__annq[i] = vnksd__eox(np.floor(start + i * isslu__uvj))
            return elie__annq
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            isslu__uvj = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            elie__annq = np.empty(num, vnksd__eox)
            for i in numba.parfors.parfor.internal_prange(num):
                elie__annq[i] = vnksd__eox(start + i * isslu__uvj)
            return elie__annq
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
        mooga__bho = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mooga__bho += A[i] == val
        return mooga__bho > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    cfreh__ewxaf = {'axis': axis, 'out': out, 'keepdims': keepdims}
    nwpd__odxzz = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', cfreh__ewxaf, nwpd__odxzz, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        mooga__bho = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mooga__bho += int(bool(A[i]))
        return mooga__bho > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    cfreh__ewxaf = {'axis': axis, 'out': out, 'keepdims': keepdims}
    nwpd__odxzz = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', cfreh__ewxaf, nwpd__odxzz, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        mooga__bho = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                mooga__bho += int(bool(A[i]))
        return mooga__bho == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    cfreh__ewxaf = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    nwpd__odxzz = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', cfreh__ewxaf, nwpd__odxzz, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        ikyxq__spbp = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            elie__annq = np.empty(n, ikyxq__spbp)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(elie__annq, i)
                    continue
                elie__annq[i] = np_cbrt_scalar(A[i], ikyxq__spbp)
            return elie__annq
        return impl_arr
    ikyxq__spbp = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, ikyxq__spbp)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    fcupf__yjvf = x < 0
    if fcupf__yjvf:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if fcupf__yjvf:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    wbvv__egfk = isinstance(tup, (types.BaseTuple, types.List))
    fgdl__hneie = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for tguq__abs in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tguq__abs
                , 'numpy.hstack()')
            wbvv__egfk = wbvv__egfk and bodo.utils.utils.is_array_typ(tguq__abs
                , False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        wbvv__egfk = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif fgdl__hneie:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        vwp__ypzdr = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for tguq__abs in vwp__ypzdr.types:
            fgdl__hneie = fgdl__hneie and bodo.utils.utils.is_array_typ(
                tguq__abs, False)
    if not (wbvv__egfk or fgdl__hneie):
        return
    if fgdl__hneie:

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
    cfreh__ewxaf = {'check_valid': check_valid, 'tol': tol}
    nwpd__odxzz = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', cfreh__ewxaf,
        nwpd__odxzz, 'numpy')
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
        fzl__dsrg = mean.shape[0]
        onefx__oab = size, fzl__dsrg
        tfcn__xyrx = np.random.standard_normal(onefx__oab)
        cov = cov.astype(np.float64)
        buoxy__bktih, s, eln__afl = np.linalg.svd(cov)
        res = np.dot(tfcn__xyrx, np.sqrt(s).reshape(fzl__dsrg, 1) * eln__afl)
        eejl__tmr = res + mean
        return eejl__tmr
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
            nzy__ckoi = bodo.hiframes.series_kernels._get_type_max_value(arr)
            clh__hmyq = typing.builtins.IndexValue(-1, nzy__ckoi)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                wok__xhnqt = typing.builtins.IndexValue(i, arr[i])
                clh__hmyq = min(clh__hmyq, wok__xhnqt)
            return clh__hmyq.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        syuoc__lup = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            ljg__uwcov = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nzy__ckoi = syuoc__lup(len(arr.dtype.categories) + 1)
            clh__hmyq = typing.builtins.IndexValue(-1, nzy__ckoi)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                wok__xhnqt = typing.builtins.IndexValue(i, ljg__uwcov[i])
                clh__hmyq = min(clh__hmyq, wok__xhnqt)
            return clh__hmyq.index
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
            nzy__ckoi = bodo.hiframes.series_kernels._get_type_min_value(arr)
            clh__hmyq = typing.builtins.IndexValue(-1, nzy__ckoi)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                wok__xhnqt = typing.builtins.IndexValue(i, arr[i])
                clh__hmyq = max(clh__hmyq, wok__xhnqt)
            return clh__hmyq.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        syuoc__lup = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            ljg__uwcov = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nzy__ckoi = syuoc__lup(-1)
            clh__hmyq = typing.builtins.IndexValue(-1, nzy__ckoi)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                wok__xhnqt = typing.builtins.IndexValue(i, ljg__uwcov[i])
                clh__hmyq = max(clh__hmyq, wok__xhnqt)
            return clh__hmyq.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
