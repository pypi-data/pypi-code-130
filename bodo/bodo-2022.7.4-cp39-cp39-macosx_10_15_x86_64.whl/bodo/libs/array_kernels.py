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
        zpa__dbjy = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = zpa__dbjy
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        zpa__dbjy = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = zpa__dbjy
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
            wyh__rvdqf = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            wyh__rvdqf[ind + 1] = wyh__rvdqf[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            wyh__rvdqf = bodo.libs.array_item_arr_ext.get_offsets(arr)
            wyh__rvdqf[ind + 1] = wyh__rvdqf[ind]
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
    nju__xyhz = arr_tup.count
    fypgw__pfbyn = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(nju__xyhz):
        fypgw__pfbyn += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    fypgw__pfbyn += '  return\n'
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'setna': setna}, nix__nvjh)
    impl = nix__nvjh['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        shai__qnsxd = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(shai__qnsxd.start, shai__qnsxd.stop, shai__qnsxd.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        phni__nvf = 'n'
        yhzcg__glp = 'n_pes'
        mwb__dtm = 'min_op'
    else:
        phni__nvf = 'n-1, -1, -1'
        yhzcg__glp = '-1'
        mwb__dtm = 'max_op'
    fypgw__pfbyn = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {yhzcg__glp}
    for i in range({phni__nvf}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {mwb__dtm}))
        if possible_valid_rank != {yhzcg__glp}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, nix__nvjh)
    impl = nix__nvjh['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    tvlc__nkxl = array_to_info(arr)
    _median_series_computation(res, tvlc__nkxl, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(tvlc__nkxl)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    tvlc__nkxl = array_to_info(arr)
    _autocorr_series_computation(res, tvlc__nkxl, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(tvlc__nkxl)


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
    tvlc__nkxl = array_to_info(arr)
    _compute_series_monotonicity(res, tvlc__nkxl, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(tvlc__nkxl)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    ewqf__rof = res[0] > 0.5
    return ewqf__rof


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        enka__nvsa = '-'
        beb__hrbnl = 'index_arr[0] > threshhold_date'
        phni__nvf = '1, n+1'
        lyed__yitr = 'index_arr[-i] <= threshhold_date'
        fch__vxk = 'i - 1'
    else:
        enka__nvsa = '+'
        beb__hrbnl = 'index_arr[-1] < threshhold_date'
        phni__nvf = 'n'
        lyed__yitr = 'index_arr[i] >= threshhold_date'
        fch__vxk = 'i'
    fypgw__pfbyn = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        fypgw__pfbyn += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        fypgw__pfbyn += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            fypgw__pfbyn += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            fypgw__pfbyn += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            fypgw__pfbyn += '    else:\n'
            fypgw__pfbyn += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            fypgw__pfbyn += (
                f'    threshhold_date = initial_date {enka__nvsa} date_offset\n'
                )
    else:
        fypgw__pfbyn += (
            f'  threshhold_date = initial_date {enka__nvsa} offset\n')
    fypgw__pfbyn += '  local_valid = 0\n'
    fypgw__pfbyn += f'  n = len(index_arr)\n'
    fypgw__pfbyn += f'  if n:\n'
    fypgw__pfbyn += f'    if {beb__hrbnl}:\n'
    fypgw__pfbyn += '      loc_valid = n\n'
    fypgw__pfbyn += '    else:\n'
    fypgw__pfbyn += f'      for i in range({phni__nvf}):\n'
    fypgw__pfbyn += f'        if {lyed__yitr}:\n'
    fypgw__pfbyn += f'          loc_valid = {fch__vxk}\n'
    fypgw__pfbyn += '          break\n'
    fypgw__pfbyn += '  if is_parallel:\n'
    fypgw__pfbyn += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    fypgw__pfbyn += '    return total_valid\n'
    fypgw__pfbyn += '  else:\n'
    fypgw__pfbyn += '    return loc_valid\n'
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, nix__nvjh)
    return nix__nvjh['impl']


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
    vjnx__ahui = numba_to_c_type(sig.args[0].dtype)
    qehu__djx = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), vjnx__ahui))
    jvet__htwh = args[0]
    yzhah__dtbpz = sig.args[0]
    if isinstance(yzhah__dtbpz, (IntegerArrayType, BooleanArrayType)):
        jvet__htwh = cgutils.create_struct_proxy(yzhah__dtbpz)(context,
            builder, jvet__htwh).data
        yzhah__dtbpz = types.Array(yzhah__dtbpz.dtype, 1, 'C')
    assert yzhah__dtbpz.ndim == 1
    arr = make_array(yzhah__dtbpz)(context, builder, jvet__htwh)
    vzvxz__qzop = builder.extract_value(arr.shape, 0)
    lvw__prji = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        vzvxz__qzop, args[1], builder.load(qehu__djx)]
    srd__bmego = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    kloga__btrui = lir.FunctionType(lir.DoubleType(), srd__bmego)
    ypk__uapke = cgutils.get_or_insert_function(builder.module,
        kloga__btrui, name='quantile_sequential')
    eotap__ggtm = builder.call(ypk__uapke, lvw__prji)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return eotap__ggtm


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    vjnx__ahui = numba_to_c_type(sig.args[0].dtype)
    qehu__djx = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), vjnx__ahui))
    jvet__htwh = args[0]
    yzhah__dtbpz = sig.args[0]
    if isinstance(yzhah__dtbpz, (IntegerArrayType, BooleanArrayType)):
        jvet__htwh = cgutils.create_struct_proxy(yzhah__dtbpz)(context,
            builder, jvet__htwh).data
        yzhah__dtbpz = types.Array(yzhah__dtbpz.dtype, 1, 'C')
    assert yzhah__dtbpz.ndim == 1
    arr = make_array(yzhah__dtbpz)(context, builder, jvet__htwh)
    vzvxz__qzop = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        dsxj__qpcf = args[2]
    else:
        dsxj__qpcf = vzvxz__qzop
    lvw__prji = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        vzvxz__qzop, dsxj__qpcf, args[1], builder.load(qehu__djx)]
    srd__bmego = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    kloga__btrui = lir.FunctionType(lir.DoubleType(), srd__bmego)
    ypk__uapke = cgutils.get_or_insert_function(builder.module,
        kloga__btrui, name='quantile_parallel')
    eotap__ggtm = builder.call(ypk__uapke, lvw__prji)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return eotap__ggtm


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        zjr__jociw = np.nonzero(pd.isna(arr))[0]
        zwsv__vjllc = arr[1:] != arr[:-1]
        zwsv__vjllc[pd.isna(zwsv__vjllc)] = False
        uduwz__mejq = zwsv__vjllc.astype(np.bool_)
        hutpa__rasp = np.concatenate((np.array([True]), uduwz__mejq))
        if zjr__jociw.size:
            ywft__tny, xtbx__luik = zjr__jociw[0], zjr__jociw[1:]
            hutpa__rasp[ywft__tny] = True
            if xtbx__luik.size:
                hutpa__rasp[xtbx__luik] = False
                if xtbx__luik[-1] + 1 < hutpa__rasp.size:
                    hutpa__rasp[xtbx__luik[-1] + 1] = True
            elif ywft__tny + 1 < hutpa__rasp.size:
                hutpa__rasp[ywft__tny + 1] = True
        return hutpa__rasp
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
    fypgw__pfbyn = """def impl(arr, method='average', na_option='keep', ascending=True, pct=False):
"""
    fypgw__pfbyn += '  na_idxs = pd.isna(arr)\n'
    fypgw__pfbyn += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    fypgw__pfbyn += '  nas = sum(na_idxs)\n'
    if not ascending:
        fypgw__pfbyn += '  if nas and nas < (sorter.size - 1):\n'
        fypgw__pfbyn += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        fypgw__pfbyn += '  else:\n'
        fypgw__pfbyn += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        fypgw__pfbyn += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    fypgw__pfbyn += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    fypgw__pfbyn += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        fypgw__pfbyn += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        fypgw__pfbyn += '    inv,\n'
        fypgw__pfbyn += '    new_dtype=np.float64,\n'
        fypgw__pfbyn += '    copy=True,\n'
        fypgw__pfbyn += '    nan_to_str=False,\n'
        fypgw__pfbyn += '    from_series=True,\n'
        fypgw__pfbyn += '    ) + 1\n'
    else:
        fypgw__pfbyn += '  arr = arr[sorter]\n'
        fypgw__pfbyn += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        fypgw__pfbyn += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            fypgw__pfbyn += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            fypgw__pfbyn += '    dense,\n'
            fypgw__pfbyn += '    new_dtype=np.float64,\n'
            fypgw__pfbyn += '    copy=True,\n'
            fypgw__pfbyn += '    nan_to_str=False,\n'
            fypgw__pfbyn += '    from_series=True,\n'
            fypgw__pfbyn += '  )\n'
        else:
            fypgw__pfbyn += """  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))
"""
            fypgw__pfbyn += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                fypgw__pfbyn += '  ret = count_float[dense]\n'
            elif method == 'min':
                fypgw__pfbyn += '  ret = count_float[dense - 1] + 1\n'
            else:
                fypgw__pfbyn += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                fypgw__pfbyn += '  ret[na_idxs] = -1\n'
            fypgw__pfbyn += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            fypgw__pfbyn += '  div_val = arr.size - nas\n'
        else:
            fypgw__pfbyn += '  div_val = arr.size\n'
        fypgw__pfbyn += '  for i in range(len(ret)):\n'
        fypgw__pfbyn += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        fypgw__pfbyn += '  ret[na_idxs] = np.nan\n'
    fypgw__pfbyn += '  return ret\n'
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'np': np, 'pd': pd, 'bodo': bodo}, nix__nvjh)
    return nix__nvjh['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    pcrb__goovt = start
    pebnm__elkok = 2 * start + 1
    ixvih__dpt = 2 * start + 2
    if pebnm__elkok < n and not cmp_f(arr[pebnm__elkok], arr[pcrb__goovt]):
        pcrb__goovt = pebnm__elkok
    if ixvih__dpt < n and not cmp_f(arr[ixvih__dpt], arr[pcrb__goovt]):
        pcrb__goovt = ixvih__dpt
    if pcrb__goovt != start:
        arr[start], arr[pcrb__goovt] = arr[pcrb__goovt], arr[start]
        ind_arr[start], ind_arr[pcrb__goovt] = ind_arr[pcrb__goovt], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, pcrb__goovt, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        xre__qbf = np.empty(k, A.dtype)
        rchu__xhli = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                xre__qbf[ind] = A[i]
                rchu__xhli[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            xre__qbf = xre__qbf[:ind]
            rchu__xhli = rchu__xhli[:ind]
        return xre__qbf, rchu__xhli, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        xiax__beknd = np.sort(A)
        jbkzf__gwg = index_arr[np.argsort(A)]
        wabfz__ykgh = pd.Series(xiax__beknd).notna().values
        xiax__beknd = xiax__beknd[wabfz__ykgh]
        jbkzf__gwg = jbkzf__gwg[wabfz__ykgh]
        if is_largest:
            xiax__beknd = xiax__beknd[::-1]
            jbkzf__gwg = jbkzf__gwg[::-1]
        return np.ascontiguousarray(xiax__beknd), np.ascontiguousarray(
            jbkzf__gwg)
    xre__qbf, rchu__xhli, start = select_k_nonan(A, index_arr, m, k)
    rchu__xhli = rchu__xhli[xre__qbf.argsort()]
    xre__qbf.sort()
    if not is_largest:
        xre__qbf = np.ascontiguousarray(xre__qbf[::-1])
        rchu__xhli = np.ascontiguousarray(rchu__xhli[::-1])
    for i in range(start, m):
        if cmp_f(A[i], xre__qbf[0]):
            xre__qbf[0] = A[i]
            rchu__xhli[0] = index_arr[i]
            min_heapify(xre__qbf, rchu__xhli, k, 0, cmp_f)
    rchu__xhli = rchu__xhli[xre__qbf.argsort()]
    xre__qbf.sort()
    if is_largest:
        xre__qbf = xre__qbf[::-1]
        rchu__xhli = rchu__xhli[::-1]
    return np.ascontiguousarray(xre__qbf), np.ascontiguousarray(rchu__xhli)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    ioniy__hjpdh = bodo.libs.distributed_api.get_rank()
    ihqu__dxuu, qfcqx__agbwu = nlargest(A, I, k, is_largest, cmp_f)
    atb__wzw = bodo.libs.distributed_api.gatherv(ihqu__dxuu)
    vftdi__uxb = bodo.libs.distributed_api.gatherv(qfcqx__agbwu)
    if ioniy__hjpdh == MPI_ROOT:
        res, ojzcy__iquzj = nlargest(atb__wzw, vftdi__uxb, k, is_largest, cmp_f
            )
    else:
        res = np.empty(k, A.dtype)
        ojzcy__iquzj = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(ojzcy__iquzj)
    return res, ojzcy__iquzj


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    pvtvg__guiz, efw__qnsa = mat.shape
    zti__trule = np.empty((efw__qnsa, efw__qnsa), dtype=np.float64)
    for usdig__srv in range(efw__qnsa):
        for zqx__brouo in range(usdig__srv + 1):
            uuklr__ohlqt = 0
            scyh__hjyt = gmd__fjr = jsng__qlgrg = jnv__lru = 0.0
            for i in range(pvtvg__guiz):
                if np.isfinite(mat[i, usdig__srv]) and np.isfinite(mat[i,
                    zqx__brouo]):
                    bjqu__dkvos = mat[i, usdig__srv]
                    yylf__sth = mat[i, zqx__brouo]
                    uuklr__ohlqt += 1
                    jsng__qlgrg += bjqu__dkvos
                    jnv__lru += yylf__sth
            if parallel:
                uuklr__ohlqt = bodo.libs.distributed_api.dist_reduce(
                    uuklr__ohlqt, sum_op)
                jsng__qlgrg = bodo.libs.distributed_api.dist_reduce(jsng__qlgrg
                    , sum_op)
                jnv__lru = bodo.libs.distributed_api.dist_reduce(jnv__lru,
                    sum_op)
            if uuklr__ohlqt < minpv:
                zti__trule[usdig__srv, zqx__brouo] = zti__trule[zqx__brouo,
                    usdig__srv] = np.nan
            else:
                lml__ynpd = jsng__qlgrg / uuklr__ohlqt
                qjabw__vgf = jnv__lru / uuklr__ohlqt
                jsng__qlgrg = 0.0
                for i in range(pvtvg__guiz):
                    if np.isfinite(mat[i, usdig__srv]) and np.isfinite(mat[
                        i, zqx__brouo]):
                        bjqu__dkvos = mat[i, usdig__srv] - lml__ynpd
                        yylf__sth = mat[i, zqx__brouo] - qjabw__vgf
                        jsng__qlgrg += bjqu__dkvos * yylf__sth
                        scyh__hjyt += bjqu__dkvos * bjqu__dkvos
                        gmd__fjr += yylf__sth * yylf__sth
                if parallel:
                    jsng__qlgrg = bodo.libs.distributed_api.dist_reduce(
                        jsng__qlgrg, sum_op)
                    scyh__hjyt = bodo.libs.distributed_api.dist_reduce(
                        scyh__hjyt, sum_op)
                    gmd__fjr = bodo.libs.distributed_api.dist_reduce(gmd__fjr,
                        sum_op)
                ngjy__fmzl = uuklr__ohlqt - 1.0 if cov else sqrt(scyh__hjyt *
                    gmd__fjr)
                if ngjy__fmzl != 0.0:
                    zti__trule[usdig__srv, zqx__brouo] = zti__trule[
                        zqx__brouo, usdig__srv] = jsng__qlgrg / ngjy__fmzl
                else:
                    zti__trule[usdig__srv, zqx__brouo] = zti__trule[
                        zqx__brouo, usdig__srv] = np.nan
    return zti__trule


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    ztnzs__uywf = n != 1
    fypgw__pfbyn = 'def impl(data, parallel=False):\n'
    fypgw__pfbyn += '  if parallel:\n'
    uya__poa = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    fypgw__pfbyn += f'    cpp_table = arr_info_list_to_table([{uya__poa}])\n'
    fypgw__pfbyn += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    abnej__ueck = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    fypgw__pfbyn += f'    data = ({abnej__ueck},)\n'
    fypgw__pfbyn += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    fypgw__pfbyn += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    fypgw__pfbyn += '    bodo.libs.array.delete_table(cpp_table)\n'
    fypgw__pfbyn += '  n = len(data[0])\n'
    fypgw__pfbyn += '  out = np.empty(n, np.bool_)\n'
    fypgw__pfbyn += '  uniqs = dict()\n'
    if ztnzs__uywf:
        fypgw__pfbyn += '  for i in range(n):\n'
        eljn__hphv = ', '.join(f'data[{i}][i]' for i in range(n))
        tdtft__wuobp = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        fypgw__pfbyn += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({eljn__hphv},), ({tdtft__wuobp},))
"""
        fypgw__pfbyn += '    if val in uniqs:\n'
        fypgw__pfbyn += '      out[i] = True\n'
        fypgw__pfbyn += '    else:\n'
        fypgw__pfbyn += '      out[i] = False\n'
        fypgw__pfbyn += '      uniqs[val] = 0\n'
    else:
        fypgw__pfbyn += '  data = data[0]\n'
        fypgw__pfbyn += '  hasna = False\n'
        fypgw__pfbyn += '  for i in range(n):\n'
        fypgw__pfbyn += '    if bodo.libs.array_kernels.isna(data, i):\n'
        fypgw__pfbyn += '      out[i] = hasna\n'
        fypgw__pfbyn += '      hasna = True\n'
        fypgw__pfbyn += '    else:\n'
        fypgw__pfbyn += '      val = data[i]\n'
        fypgw__pfbyn += '      if val in uniqs:\n'
        fypgw__pfbyn += '        out[i] = True\n'
        fypgw__pfbyn += '      else:\n'
        fypgw__pfbyn += '        out[i] = False\n'
        fypgw__pfbyn += '        uniqs[val] = 0\n'
    fypgw__pfbyn += '  if parallel:\n'
    fypgw__pfbyn += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    fypgw__pfbyn += '  return out\n'
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        nix__nvjh)
    impl = nix__nvjh['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    nju__xyhz = len(data)
    fypgw__pfbyn = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    fypgw__pfbyn += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (nju__xyhz))))
    fypgw__pfbyn += '  table_total = arr_info_list_to_table(info_list_total)\n'
    fypgw__pfbyn += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(nju__xyhz))
    for sohkd__mzr in range(nju__xyhz):
        fypgw__pfbyn += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(sohkd__mzr, sohkd__mzr, sohkd__mzr))
    fypgw__pfbyn += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(nju__xyhz))
    fypgw__pfbyn += '  delete_table(out_table)\n'
    fypgw__pfbyn += '  delete_table(table_total)\n'
    fypgw__pfbyn += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(nju__xyhz)))
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, nix__nvjh)
    impl = nix__nvjh['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    nju__xyhz = len(data)
    fypgw__pfbyn = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    fypgw__pfbyn += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (nju__xyhz))))
    fypgw__pfbyn += '  table_total = arr_info_list_to_table(info_list_total)\n'
    fypgw__pfbyn += '  keep_i = 0\n'
    fypgw__pfbyn += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for sohkd__mzr in range(nju__xyhz):
        fypgw__pfbyn += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(sohkd__mzr, sohkd__mzr, sohkd__mzr))
    fypgw__pfbyn += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(nju__xyhz))
    fypgw__pfbyn += '  delete_table(out_table)\n'
    fypgw__pfbyn += '  delete_table(table_total)\n'
    fypgw__pfbyn += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(nju__xyhz)))
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, nix__nvjh)
    impl = nix__nvjh['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        dmj__lefsu = [array_to_info(data_arr)]
        iqe__fykp = arr_info_list_to_table(dmj__lefsu)
        scg__xkx = 0
        jcb__ufldy = drop_duplicates_table(iqe__fykp, parallel, 1, scg__xkx,
            False, True)
        kyi__azy = info_to_array(info_from_table(jcb__ufldy, 0), data_arr)
        delete_table(jcb__ufldy)
        delete_table(iqe__fykp)
        return kyi__azy
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    ultpu__lvgli = len(data.types)
    ova__pkljh = [('out' + str(i)) for i in range(ultpu__lvgli)]
    ycyr__enrz = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    yrt__tvt = ['isna(data[{}], i)'.format(i) for i in ycyr__enrz]
    hnv__okqt = 'not ({})'.format(' or '.join(yrt__tvt))
    if not is_overload_none(thresh):
        hnv__okqt = '(({}) <= ({}) - thresh)'.format(' + '.join(yrt__tvt), 
            ultpu__lvgli - 1)
    elif how == 'all':
        hnv__okqt = 'not ({})'.format(' and '.join(yrt__tvt))
    fypgw__pfbyn = 'def _dropna_imp(data, how, thresh, subset):\n'
    fypgw__pfbyn += '  old_len = len(data[0])\n'
    fypgw__pfbyn += '  new_len = 0\n'
    fypgw__pfbyn += '  for i in range(old_len):\n'
    fypgw__pfbyn += '    if {}:\n'.format(hnv__okqt)
    fypgw__pfbyn += '      new_len += 1\n'
    for i, out in enumerate(ova__pkljh):
        if isinstance(data[i], bodo.CategoricalArrayType):
            fypgw__pfbyn += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            fypgw__pfbyn += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    fypgw__pfbyn += '  curr_ind = 0\n'
    fypgw__pfbyn += '  for i in range(old_len):\n'
    fypgw__pfbyn += '    if {}:\n'.format(hnv__okqt)
    for i in range(ultpu__lvgli):
        fypgw__pfbyn += '      if isna(data[{}], i):\n'.format(i)
        fypgw__pfbyn += '        setna({}, curr_ind)\n'.format(ova__pkljh[i])
        fypgw__pfbyn += '      else:\n'
        fypgw__pfbyn += '        {}[curr_ind] = data[{}][i]\n'.format(
            ova__pkljh[i], i)
    fypgw__pfbyn += '      curr_ind += 1\n'
    fypgw__pfbyn += '  return {}\n'.format(', '.join(ova__pkljh))
    nix__nvjh = {}
    qwc__czs = {'t{}'.format(i): lwl__jpesw for i, lwl__jpesw in enumerate(
        data.types)}
    qwc__czs.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(fypgw__pfbyn, qwc__czs, nix__nvjh)
    bcx__pdy = nix__nvjh['_dropna_imp']
    return bcx__pdy


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        yzhah__dtbpz = arr.dtype
        teqa__qkft = yzhah__dtbpz.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            tyqc__mjwwe = init_nested_counts(teqa__qkft)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                tyqc__mjwwe = add_nested_counts(tyqc__mjwwe, val[ind])
            kyi__azy = bodo.utils.utils.alloc_type(n, yzhah__dtbpz, tyqc__mjwwe
                )
            for umdmz__irlp in range(n):
                if bodo.libs.array_kernels.isna(arr, umdmz__irlp):
                    setna(kyi__azy, umdmz__irlp)
                    continue
                val = arr[umdmz__irlp]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(kyi__azy, umdmz__irlp)
                    continue
                kyi__azy[umdmz__irlp] = val[ind]
            return kyi__azy
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    tuppm__hlyr = _to_readonly(arr_types.types[0])
    return all(isinstance(lwl__jpesw, CategoricalArrayType) and 
        _to_readonly(lwl__jpesw) == tuppm__hlyr for lwl__jpesw in arr_types
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
        bkhnh__ilnph = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            ful__bzh = 0
            nkd__oab = []
            for A in arr_list:
                zgfz__cfpqg = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                nkd__oab.append(bodo.libs.array_item_arr_ext.get_data(A))
                ful__bzh += zgfz__cfpqg
            hdjy__wrj = np.empty(ful__bzh + 1, offset_type)
            ojgg__yqx = bodo.libs.array_kernels.concat(nkd__oab)
            otpd__drpn = np.empty(ful__bzh + 7 >> 3, np.uint8)
            pem__bdifq = 0
            phqks__nskc = 0
            for A in arr_list:
                kcqe__jabv = bodo.libs.array_item_arr_ext.get_offsets(A)
                qng__eqi = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                zgfz__cfpqg = len(A)
                ubiw__btdiw = kcqe__jabv[zgfz__cfpqg]
                for i in range(zgfz__cfpqg):
                    hdjy__wrj[i + pem__bdifq] = kcqe__jabv[i] + phqks__nskc
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        qng__eqi, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(otpd__drpn, i +
                        pem__bdifq, bnn__icq)
                pem__bdifq += zgfz__cfpqg
                phqks__nskc += ubiw__btdiw
            hdjy__wrj[pem__bdifq] = phqks__nskc
            kyi__azy = bodo.libs.array_item_arr_ext.init_array_item_array(
                ful__bzh, ojgg__yqx, hdjy__wrj, otpd__drpn)
            return kyi__azy
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        wnl__oah = arr_list.dtype.names
        fypgw__pfbyn = 'def struct_array_concat_impl(arr_list):\n'
        fypgw__pfbyn += f'    n_all = 0\n'
        for i in range(len(wnl__oah)):
            fypgw__pfbyn += f'    concat_list{i} = []\n'
        fypgw__pfbyn += '    for A in arr_list:\n'
        fypgw__pfbyn += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(wnl__oah)):
            fypgw__pfbyn += f'        concat_list{i}.append(data_tuple[{i}])\n'
        fypgw__pfbyn += '        n_all += len(A)\n'
        fypgw__pfbyn += '    n_bytes = (n_all + 7) >> 3\n'
        fypgw__pfbyn += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        fypgw__pfbyn += '    curr_bit = 0\n'
        fypgw__pfbyn += '    for A in arr_list:\n'
        fypgw__pfbyn += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        fypgw__pfbyn += '        for j in range(len(A)):\n'
        fypgw__pfbyn += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        fypgw__pfbyn += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        fypgw__pfbyn += '            curr_bit += 1\n'
        fypgw__pfbyn += (
            '    return bodo.libs.struct_arr_ext.init_struct_arr(\n')
        kkpy__nhisr = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(wnl__oah))])
        fypgw__pfbyn += f'        ({kkpy__nhisr},),\n'
        fypgw__pfbyn += '        new_mask,\n'
        fypgw__pfbyn += f'        {wnl__oah},\n'
        fypgw__pfbyn += '    )\n'
        nix__nvjh = {}
        exec(fypgw__pfbyn, {'bodo': bodo, 'np': np}, nix__nvjh)
        return nix__nvjh['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            ttz__mnr = 0
            for A in arr_list:
                ttz__mnr += len(A)
            sayn__fjt = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(ttz__mnr))
            enoq__nxpz = 0
            for A in arr_list:
                for i in range(len(A)):
                    sayn__fjt._data[i + enoq__nxpz] = A._data[i]
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sayn__fjt.
                        _null_bitmap, i + enoq__nxpz, bnn__icq)
                enoq__nxpz += len(A)
            return sayn__fjt
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            ttz__mnr = 0
            for A in arr_list:
                ttz__mnr += len(A)
            sayn__fjt = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(ttz__mnr))
            enoq__nxpz = 0
            for A in arr_list:
                for i in range(len(A)):
                    sayn__fjt._days_data[i + enoq__nxpz] = A._days_data[i]
                    sayn__fjt._seconds_data[i + enoq__nxpz] = A._seconds_data[i
                        ]
                    sayn__fjt._microseconds_data[i + enoq__nxpz
                        ] = A._microseconds_data[i]
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sayn__fjt.
                        _null_bitmap, i + enoq__nxpz, bnn__icq)
                enoq__nxpz += len(A)
            return sayn__fjt
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        azj__kyr = arr_list.dtype.precision
        fdyr__eykaf = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            ttz__mnr = 0
            for A in arr_list:
                ttz__mnr += len(A)
            sayn__fjt = bodo.libs.decimal_arr_ext.alloc_decimal_array(ttz__mnr,
                azj__kyr, fdyr__eykaf)
            enoq__nxpz = 0
            for A in arr_list:
                for i in range(len(A)):
                    sayn__fjt._data[i + enoq__nxpz] = A._data[i]
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sayn__fjt.
                        _null_bitmap, i + enoq__nxpz, bnn__icq)
                enoq__nxpz += len(A)
            return sayn__fjt
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        lwl__jpesw) for lwl__jpesw in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            wss__mgndb = arr_list.types[0]
        else:
            wss__mgndb = arr_list.dtype
        wss__mgndb = to_str_arr_if_dict_array(wss__mgndb)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            blsby__oixon = 0
            saiki__phwn = 0
            for A in arr_list:
                arr = A
                blsby__oixon += len(arr)
                saiki__phwn += bodo.libs.str_arr_ext.num_total_chars(arr)
            kyi__azy = bodo.utils.utils.alloc_type(blsby__oixon, wss__mgndb,
                (saiki__phwn,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(kyi__azy, -1)
            dycev__fmc = 0
            hwel__vndr = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(kyi__azy, arr,
                    dycev__fmc, hwel__vndr)
                dycev__fmc += len(arr)
                hwel__vndr += bodo.libs.str_arr_ext.num_total_chars(arr)
            return kyi__azy
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(lwl__jpesw.dtype, types.Integer) for
        lwl__jpesw in arr_list.types) and any(isinstance(lwl__jpesw,
        IntegerArrayType) for lwl__jpesw in arr_list.types):

        def impl_int_arr_list(arr_list):
            vrul__upvsa = convert_to_nullable_tup(arr_list)
            txpt__phgcf = []
            fjaa__locp = 0
            for A in vrul__upvsa:
                txpt__phgcf.append(A._data)
                fjaa__locp += len(A)
            ojgg__yqx = bodo.libs.array_kernels.concat(txpt__phgcf)
            zxa__fpd = fjaa__locp + 7 >> 3
            yiri__axj = np.empty(zxa__fpd, np.uint8)
            gyb__xjqzt = 0
            for A in vrul__upvsa:
                jucg__itm = A._null_bitmap
                for umdmz__irlp in range(len(A)):
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        jucg__itm, umdmz__irlp)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yiri__axj,
                        gyb__xjqzt, bnn__icq)
                    gyb__xjqzt += 1
            return bodo.libs.int_arr_ext.init_integer_array(ojgg__yqx,
                yiri__axj)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(lwl__jpesw.dtype == types.bool_ for lwl__jpesw in
        arr_list.types) and any(lwl__jpesw == boolean_array for lwl__jpesw in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            vrul__upvsa = convert_to_nullable_tup(arr_list)
            txpt__phgcf = []
            fjaa__locp = 0
            for A in vrul__upvsa:
                txpt__phgcf.append(A._data)
                fjaa__locp += len(A)
            ojgg__yqx = bodo.libs.array_kernels.concat(txpt__phgcf)
            zxa__fpd = fjaa__locp + 7 >> 3
            yiri__axj = np.empty(zxa__fpd, np.uint8)
            gyb__xjqzt = 0
            for A in vrul__upvsa:
                jucg__itm = A._null_bitmap
                for umdmz__irlp in range(len(A)):
                    bnn__icq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        jucg__itm, umdmz__irlp)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yiri__axj,
                        gyb__xjqzt, bnn__icq)
                    gyb__xjqzt += 1
            return bodo.libs.bool_arr_ext.init_bool_array(ojgg__yqx, yiri__axj)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            into__rlji = []
            for A in arr_list:
                into__rlji.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                into__rlji), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        ipap__mfd = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        fypgw__pfbyn = 'def impl(arr_list):\n'
        fypgw__pfbyn += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({ipap__mfd},)), arr_list[0].dtype)
"""
        hipck__rky = {}
        exec(fypgw__pfbyn, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, hipck__rky)
        return hipck__rky['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            fjaa__locp = 0
            for A in arr_list:
                fjaa__locp += len(A)
            kyi__azy = np.empty(fjaa__locp, dtype)
            nwp__vdtc = 0
            for A in arr_list:
                n = len(A)
                kyi__azy[nwp__vdtc:nwp__vdtc + n] = A
                nwp__vdtc += n
            return kyi__azy
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(lwl__jpesw,
        (types.Array, IntegerArrayType)) and isinstance(lwl__jpesw.dtype,
        types.Integer) for lwl__jpesw in arr_list.types) and any(isinstance
        (lwl__jpesw, types.Array) and isinstance(lwl__jpesw.dtype, types.
        Float) for lwl__jpesw in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            glyo__uefe = []
            for A in arr_list:
                glyo__uefe.append(A._data)
            jmozn__gcq = bodo.libs.array_kernels.concat(glyo__uefe)
            zti__trule = bodo.libs.map_arr_ext.init_map_arr(jmozn__gcq)
            return zti__trule
        return impl_map_arr_list
    for gnca__vknc in arr_list:
        if not isinstance(gnca__vknc, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(lwl__jpesw.astype(np.float64) for lwl__jpesw in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    nju__xyhz = len(arr_tup.types)
    fypgw__pfbyn = 'def f(arr_tup):\n'
    fypgw__pfbyn += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(nju__xyhz
        )), ',' if nju__xyhz == 1 else '')
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'np': np}, nix__nvjh)
    efxl__pusq = nix__nvjh['f']
    return efxl__pusq


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    nju__xyhz = len(arr_tup.types)
    pambw__jfwdm = find_common_np_dtype(arr_tup.types)
    teqa__qkft = None
    knluw__ctj = ''
    if isinstance(pambw__jfwdm, types.Integer):
        teqa__qkft = bodo.libs.int_arr_ext.IntDtype(pambw__jfwdm)
        knluw__ctj = '.astype(out_dtype, False)'
    fypgw__pfbyn = 'def f(arr_tup):\n'
    fypgw__pfbyn += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, knluw__ctj) for i in range(nju__xyhz)), ',' if nju__xyhz ==
        1 else '')
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'bodo': bodo, 'out_dtype': teqa__qkft}, nix__nvjh)
    mjen__btun = nix__nvjh['f']
    return mjen__btun


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, fhiw__gui = build_set_seen_na(A)
        return len(s) + int(not dropna and fhiw__gui)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        yfn__avleq = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        wjfsj__ptyr = len(yfn__avleq)
        return bodo.libs.distributed_api.dist_reduce(wjfsj__ptyr, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([qfok__nub for qfok__nub in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        omvy__myf = np.finfo(A.dtype(1).dtype).max
    else:
        omvy__myf = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        kyi__azy = np.empty(n, A.dtype)
        anyam__jmk = omvy__myf
        for i in range(n):
            anyam__jmk = min(anyam__jmk, A[i])
            kyi__azy[i] = anyam__jmk
        return kyi__azy
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        omvy__myf = np.finfo(A.dtype(1).dtype).min
    else:
        omvy__myf = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        kyi__azy = np.empty(n, A.dtype)
        anyam__jmk = omvy__myf
        for i in range(n):
            anyam__jmk = max(anyam__jmk, A[i])
            kyi__azy[i] = anyam__jmk
        return kyi__azy
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        ohodt__nnc = arr_info_list_to_table([array_to_info(A)])
        pphxy__eejft = 1
        scg__xkx = 0
        jcb__ufldy = drop_duplicates_table(ohodt__nnc, parallel,
            pphxy__eejft, scg__xkx, dropna, True)
        kyi__azy = info_to_array(info_from_table(jcb__ufldy, 0), A)
        delete_table(ohodt__nnc)
        delete_table(jcb__ufldy)
        return kyi__azy
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    bkhnh__ilnph = bodo.utils.typing.to_nullable_type(arr.dtype)
    eruzf__hma = index_arr
    xvbp__vuf = eruzf__hma.dtype

    def impl(arr, index_arr):
        n = len(arr)
        tyqc__mjwwe = init_nested_counts(bkhnh__ilnph)
        xnw__zau = init_nested_counts(xvbp__vuf)
        for i in range(n):
            sgka__wovf = index_arr[i]
            if isna(arr, i):
                tyqc__mjwwe = (tyqc__mjwwe[0] + 1,) + tyqc__mjwwe[1:]
                xnw__zau = add_nested_counts(xnw__zau, sgka__wovf)
                continue
            caucz__rhhpy = arr[i]
            if len(caucz__rhhpy) == 0:
                tyqc__mjwwe = (tyqc__mjwwe[0] + 1,) + tyqc__mjwwe[1:]
                xnw__zau = add_nested_counts(xnw__zau, sgka__wovf)
                continue
            tyqc__mjwwe = add_nested_counts(tyqc__mjwwe, caucz__rhhpy)
            for uuyni__feyhf in range(len(caucz__rhhpy)):
                xnw__zau = add_nested_counts(xnw__zau, sgka__wovf)
        kyi__azy = bodo.utils.utils.alloc_type(tyqc__mjwwe[0], bkhnh__ilnph,
            tyqc__mjwwe[1:])
        welje__mgfac = bodo.utils.utils.alloc_type(tyqc__mjwwe[0],
            eruzf__hma, xnw__zau)
        phqks__nskc = 0
        for i in range(n):
            if isna(arr, i):
                setna(kyi__azy, phqks__nskc)
                welje__mgfac[phqks__nskc] = index_arr[i]
                phqks__nskc += 1
                continue
            caucz__rhhpy = arr[i]
            ubiw__btdiw = len(caucz__rhhpy)
            if ubiw__btdiw == 0:
                setna(kyi__azy, phqks__nskc)
                welje__mgfac[phqks__nskc] = index_arr[i]
                phqks__nskc += 1
                continue
            kyi__azy[phqks__nskc:phqks__nskc + ubiw__btdiw] = caucz__rhhpy
            welje__mgfac[phqks__nskc:phqks__nskc + ubiw__btdiw] = index_arr[i]
            phqks__nskc += ubiw__btdiw
        return kyi__azy, welje__mgfac
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    bkhnh__ilnph = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        tyqc__mjwwe = init_nested_counts(bkhnh__ilnph)
        for i in range(n):
            if isna(arr, i):
                tyqc__mjwwe = (tyqc__mjwwe[0] + 1,) + tyqc__mjwwe[1:]
                bre__ucjyt = 1
            else:
                caucz__rhhpy = arr[i]
                gvak__wndi = len(caucz__rhhpy)
                if gvak__wndi == 0:
                    tyqc__mjwwe = (tyqc__mjwwe[0] + 1,) + tyqc__mjwwe[1:]
                    bre__ucjyt = 1
                    continue
                else:
                    tyqc__mjwwe = add_nested_counts(tyqc__mjwwe, caucz__rhhpy)
                    bre__ucjyt = gvak__wndi
            if counts[i] != bre__ucjyt:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        kyi__azy = bodo.utils.utils.alloc_type(tyqc__mjwwe[0], bkhnh__ilnph,
            tyqc__mjwwe[1:])
        phqks__nskc = 0
        for i in range(n):
            if isna(arr, i):
                setna(kyi__azy, phqks__nskc)
                phqks__nskc += 1
                continue
            caucz__rhhpy = arr[i]
            ubiw__btdiw = len(caucz__rhhpy)
            if ubiw__btdiw == 0:
                setna(kyi__azy, phqks__nskc)
                phqks__nskc += 1
                continue
            kyi__azy[phqks__nskc:phqks__nskc + ubiw__btdiw] = caucz__rhhpy
            phqks__nskc += ubiw__btdiw
        return kyi__azy
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(zahv__chjnv) for zahv__chjnv in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one or is_bin_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        bjw__voi = 'np.empty(n, np.int64)'
        pqsj__yoqic = 'out_arr[i] = 1'
        ktj__auimb = 'max(len(arr[i]), 1)'
    else:
        bjw__voi = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        pqsj__yoqic = 'bodo.libs.array_kernels.setna(out_arr, i)'
        ktj__auimb = 'len(arr[i])'
    fypgw__pfbyn = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {bjw__voi}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {pqsj__yoqic}
        else:
            out_arr[i] = {ktj__auimb}
    return out_arr
    """
    nix__nvjh = {}
    exec(fypgw__pfbyn, {'bodo': bodo, 'numba': numba, 'np': np}, nix__nvjh)
    impl = nix__nvjh['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    eruzf__hma = index_arr
    xvbp__vuf = eruzf__hma.dtype

    def impl(arr, pat, n, index_arr):
        cke__mgzb = pat is not None and len(pat) > 1
        if cke__mgzb:
            runpv__hzu = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        ksxj__zzwt = len(arr)
        blsby__oixon = 0
        saiki__phwn = 0
        xnw__zau = init_nested_counts(xvbp__vuf)
        for i in range(ksxj__zzwt):
            sgka__wovf = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                blsby__oixon += 1
                xnw__zau = add_nested_counts(xnw__zau, sgka__wovf)
                continue
            if cke__mgzb:
                cxte__rqau = runpv__hzu.split(arr[i], maxsplit=n)
            else:
                cxte__rqau = arr[i].split(pat, n)
            blsby__oixon += len(cxte__rqau)
            for s in cxte__rqau:
                xnw__zau = add_nested_counts(xnw__zau, sgka__wovf)
                saiki__phwn += bodo.libs.str_arr_ext.get_utf8_size(s)
        kyi__azy = bodo.libs.str_arr_ext.pre_alloc_string_array(blsby__oixon,
            saiki__phwn)
        welje__mgfac = bodo.utils.utils.alloc_type(blsby__oixon, eruzf__hma,
            xnw__zau)
        zsncg__tekek = 0
        for umdmz__irlp in range(ksxj__zzwt):
            if isna(arr, umdmz__irlp):
                kyi__azy[zsncg__tekek] = ''
                bodo.libs.array_kernels.setna(kyi__azy, zsncg__tekek)
                welje__mgfac[zsncg__tekek] = index_arr[umdmz__irlp]
                zsncg__tekek += 1
                continue
            if cke__mgzb:
                cxte__rqau = runpv__hzu.split(arr[umdmz__irlp], maxsplit=n)
            else:
                cxte__rqau = arr[umdmz__irlp].split(pat, n)
            kah__fyz = len(cxte__rqau)
            kyi__azy[zsncg__tekek:zsncg__tekek + kah__fyz] = cxte__rqau
            welje__mgfac[zsncg__tekek:zsncg__tekek + kah__fyz] = index_arr[
                umdmz__irlp]
            zsncg__tekek += kah__fyz
        return kyi__azy, welje__mgfac
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
            kyi__azy = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                kyi__azy[i] = np.nan
            return kyi__azy
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            mzco__ysk = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            regvb__tqenq = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(regvb__tqenq, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(mzco__ysk,
                regvb__tqenq, True)
        return impl_dict
    wbys__lek = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        kyi__azy = bodo.utils.utils.alloc_type(n, wbys__lek, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(kyi__azy, i)
        return kyi__azy
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
    fuw__ghes = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            kyi__azy = bodo.utils.utils.alloc_type(new_len, fuw__ghes)
            bodo.libs.str_arr_ext.str_copy_ptr(kyi__azy.ctypes, 0, A.ctypes,
                old_size)
            return kyi__azy
        return impl_char

    def impl(A, old_size, new_len):
        kyi__azy = bodo.utils.utils.alloc_type(new_len, fuw__ghes, (-1,))
        kyi__azy[:old_size] = A[:old_size]
        return kyi__azy
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    nfke__kwan = math.ceil((stop - start) / step)
    return int(max(nfke__kwan, 0))


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
    if any(isinstance(qfok__nub, types.Complex) for qfok__nub in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            pbsxt__wdsk = (stop - start) / step
            nfke__kwan = math.ceil(pbsxt__wdsk.real)
            zsuly__ticb = math.ceil(pbsxt__wdsk.imag)
            pzw__ouxrb = int(max(min(zsuly__ticb, nfke__kwan), 0))
            arr = np.empty(pzw__ouxrb, dtype)
            for i in numba.parfors.parfor.internal_prange(pzw__ouxrb):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            pzw__ouxrb = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(pzw__ouxrb, dtype)
            for i in numba.parfors.parfor.internal_prange(pzw__ouxrb):
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
        jetp__heqz = arr,
        if not inplace:
            jetp__heqz = arr.copy(),
        xora__cqs = bodo.libs.str_arr_ext.to_list_if_immutable_arr(jetp__heqz)
        ydh__vnpu = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(xora__cqs, 0, n, ydh__vnpu)
        if not ascending:
            bodo.libs.timsort.reverseRange(xora__cqs, 0, n, ydh__vnpu)
        bodo.libs.str_arr_ext.cp_str_list_to_array(jetp__heqz, xora__cqs)
        return jetp__heqz[0]
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
        zti__trule = []
        for i in range(n):
            if A[i]:
                zti__trule.append(i + offset)
        return np.array(zti__trule, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    fuw__ghes = element_type(A)
    if fuw__ghes == types.unicode_type:
        null_value = '""'
    elif fuw__ghes == types.bool_:
        null_value = 'False'
    elif fuw__ghes == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif fuw__ghes == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    zsncg__tekek = 'i'
    pjrw__jwh = False
    liqww__znzc = get_overload_const_str(method)
    if liqww__znzc in ('ffill', 'pad'):
        mnhw__zrtjo = 'n'
        send_right = True
    elif liqww__znzc in ('backfill', 'bfill'):
        mnhw__zrtjo = 'n-1, -1, -1'
        send_right = False
        if fuw__ghes == types.unicode_type:
            zsncg__tekek = '(n - 1) - i'
            pjrw__jwh = True
    fypgw__pfbyn = 'def impl(A, method, parallel=False):\n'
    fypgw__pfbyn += '  A = decode_if_dict_array(A)\n'
    fypgw__pfbyn += '  has_last_value = False\n'
    fypgw__pfbyn += f'  last_value = {null_value}\n'
    fypgw__pfbyn += '  if parallel:\n'
    fypgw__pfbyn += '    rank = bodo.libs.distributed_api.get_rank()\n'
    fypgw__pfbyn += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    fypgw__pfbyn += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    fypgw__pfbyn += '  n = len(A)\n'
    fypgw__pfbyn += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    fypgw__pfbyn += f'  for i in range({mnhw__zrtjo}):\n'
    fypgw__pfbyn += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    fypgw__pfbyn += (
        f'      bodo.libs.array_kernels.setna(out_arr, {zsncg__tekek})\n')
    fypgw__pfbyn += '      continue\n'
    fypgw__pfbyn += '    s = A[i]\n'
    fypgw__pfbyn += '    if bodo.libs.array_kernels.isna(A, i):\n'
    fypgw__pfbyn += '      s = last_value\n'
    fypgw__pfbyn += f'    out_arr[{zsncg__tekek}] = s\n'
    fypgw__pfbyn += '    last_value = s\n'
    fypgw__pfbyn += '    has_last_value = True\n'
    if pjrw__jwh:
        fypgw__pfbyn += '  return out_arr[::-1]\n'
    else:
        fypgw__pfbyn += '  return out_arr\n'
    hrq__rhee = {}
    exec(fypgw__pfbyn, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, hrq__rhee)
    impl = hrq__rhee['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        amam__bzwth = 0
        pyc__iul = n_pes - 1
        mkjoa__vity = np.int32(rank + 1)
        vae__xqkg = np.int32(rank - 1)
        omyxx__lyw = len(in_arr) - 1
        ibmx__ycbst = -1
        nqy__sqqn = -1
    else:
        amam__bzwth = n_pes - 1
        pyc__iul = 0
        mkjoa__vity = np.int32(rank - 1)
        vae__xqkg = np.int32(rank + 1)
        omyxx__lyw = 0
        ibmx__ycbst = len(in_arr)
        nqy__sqqn = 1
    gfnm__dchg = np.int32(bodo.hiframes.rolling.comm_border_tag)
    cgu__hxiyo = np.empty(1, dtype=np.bool_)
    ehq__akha = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    jogd__ecrx = np.empty(1, dtype=np.bool_)
    pzwy__mpw = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    wzaxs__yizgy = False
    vyt__bxofy = null_value
    for i in range(omyxx__lyw, ibmx__ycbst, nqy__sqqn):
        if not isna(in_arr, i):
            wzaxs__yizgy = True
            vyt__bxofy = in_arr[i]
            break
    if rank != amam__bzwth:
        efqfq__ayjc = bodo.libs.distributed_api.irecv(cgu__hxiyo, 1,
            vae__xqkg, gfnm__dchg, True)
        bodo.libs.distributed_api.wait(efqfq__ayjc, True)
        vuoqa__epsa = bodo.libs.distributed_api.irecv(ehq__akha, 1,
            vae__xqkg, gfnm__dchg, True)
        bodo.libs.distributed_api.wait(vuoqa__epsa, True)
        fvl__pkcdx = cgu__hxiyo[0]
        jllci__snmk = ehq__akha[0]
    else:
        fvl__pkcdx = False
        jllci__snmk = null_value
    if wzaxs__yizgy:
        jogd__ecrx[0] = wzaxs__yizgy
        pzwy__mpw[0] = vyt__bxofy
    else:
        jogd__ecrx[0] = fvl__pkcdx
        pzwy__mpw[0] = jllci__snmk
    if rank != pyc__iul:
        binyv__pip = bodo.libs.distributed_api.isend(jogd__ecrx, 1,
            mkjoa__vity, gfnm__dchg, True)
        xdwtl__ijpxl = bodo.libs.distributed_api.isend(pzwy__mpw, 1,
            mkjoa__vity, gfnm__dchg, True)
    return fvl__pkcdx, jllci__snmk


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    tlty__pvs = {'axis': axis, 'kind': kind, 'order': order}
    tfb__rmqve = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', tlty__pvs, tfb__rmqve, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    fuw__ghes = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):
        if A == bodo.dict_str_arr_type:

            def impl_dict_int(A, repeats):
                data_arr = A._data.copy()
                rpe__qbn = A._indices
                ksxj__zzwt = len(rpe__qbn)
                ysiyg__yxgc = alloc_int_array(ksxj__zzwt * repeats, np.int32)
                for i in range(ksxj__zzwt):
                    zsncg__tekek = i * repeats
                    if bodo.libs.array_kernels.isna(rpe__qbn, i):
                        for umdmz__irlp in range(repeats):
                            bodo.libs.array_kernels.setna(ysiyg__yxgc, 
                                zsncg__tekek + umdmz__irlp)
                    else:
                        ysiyg__yxgc[zsncg__tekek:zsncg__tekek + repeats
                            ] = rpe__qbn[i]
                return init_dict_arr(data_arr, ysiyg__yxgc, A.
                    _has_global_dictionary)
            return impl_dict_int

        def impl_int(A, repeats):
            ksxj__zzwt = len(A)
            kyi__azy = bodo.utils.utils.alloc_type(ksxj__zzwt * repeats,
                fuw__ghes, (-1,))
            for i in range(ksxj__zzwt):
                zsncg__tekek = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for umdmz__irlp in range(repeats):
                        bodo.libs.array_kernels.setna(kyi__azy, 
                            zsncg__tekek + umdmz__irlp)
                else:
                    kyi__azy[zsncg__tekek:zsncg__tekek + repeats] = A[i]
            return kyi__azy
        return impl_int
    if A == bodo.dict_str_arr_type:

        def impl_dict_arr(A, repeats):
            data_arr = A._data.copy()
            rpe__qbn = A._indices
            ksxj__zzwt = len(rpe__qbn)
            ysiyg__yxgc = alloc_int_array(repeats.sum(), np.int32)
            zsncg__tekek = 0
            for i in range(ksxj__zzwt):
                gjz__yck = repeats[i]
                if gjz__yck < 0:
                    raise ValueError('repeats may not contain negative values.'
                        )
                if bodo.libs.array_kernels.isna(rpe__qbn, i):
                    for umdmz__irlp in range(gjz__yck):
                        bodo.libs.array_kernels.setna(ysiyg__yxgc, 
                            zsncg__tekek + umdmz__irlp)
                else:
                    ysiyg__yxgc[zsncg__tekek:zsncg__tekek + gjz__yck
                        ] = rpe__qbn[i]
                zsncg__tekek += gjz__yck
            return init_dict_arr(data_arr, ysiyg__yxgc, A.
                _has_global_dictionary)
        return impl_dict_arr

    def impl_arr(A, repeats):
        ksxj__zzwt = len(A)
        kyi__azy = bodo.utils.utils.alloc_type(repeats.sum(), fuw__ghes, (-1,))
        zsncg__tekek = 0
        for i in range(ksxj__zzwt):
            gjz__yck = repeats[i]
            if gjz__yck < 0:
                raise ValueError('repeats may not contain negative values.')
            if bodo.libs.array_kernels.isna(A, i):
                for umdmz__irlp in range(gjz__yck):
                    bodo.libs.array_kernels.setna(kyi__azy, zsncg__tekek +
                        umdmz__irlp)
            else:
                kyi__azy[zsncg__tekek:zsncg__tekek + gjz__yck] = A[i]
            zsncg__tekek += gjz__yck
        return kyi__azy
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
        qpry__duhi = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(qpry__duhi, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        pgn__skh = bodo.libs.array_kernels.concat([A1, A2])
        trle__ger = bodo.libs.array_kernels.unique(pgn__skh)
        return pd.Series(trle__ger).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    tlty__pvs = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    tfb__rmqve = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', tlty__pvs, tfb__rmqve, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        bulq__drb = bodo.libs.array_kernels.unique(A1)
        jvaoa__awd = bodo.libs.array_kernels.unique(A2)
        pgn__skh = bodo.libs.array_kernels.concat([bulq__drb, jvaoa__awd])
        kkqdk__vbbeh = pd.Series(pgn__skh).sort_values().values
        return slice_array_intersect1d(kkqdk__vbbeh)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    wabfz__ykgh = arr[1:] == arr[:-1]
    return arr[:-1][wabfz__ykgh]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    gfnm__dchg = np.int32(bodo.hiframes.rolling.comm_border_tag)
    lagfj__xqp = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        hely__rvhxf = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), gfnm__dchg, True)
        bodo.libs.distributed_api.wait(hely__rvhxf, True)
    if rank == n_pes - 1:
        return None
    else:
        kqjpn__vrh = bodo.libs.distributed_api.irecv(lagfj__xqp, 1, np.
            int32(rank + 1), gfnm__dchg, True)
        bodo.libs.distributed_api.wait(kqjpn__vrh, True)
        return lagfj__xqp[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    wabfz__ykgh = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            wabfz__ykgh[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        uklnx__bmfcv = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == uklnx__bmfcv:
            wabfz__ykgh[n - 1] = True
    return wabfz__ykgh


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    tlty__pvs = {'assume_unique': assume_unique}
    tfb__rmqve = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', tlty__pvs, tfb__rmqve, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        bulq__drb = bodo.libs.array_kernels.unique(A1)
        jvaoa__awd = bodo.libs.array_kernels.unique(A2)
        wabfz__ykgh = calculate_mask_setdiff1d(bulq__drb, jvaoa__awd)
        return pd.Series(bulq__drb[wabfz__ykgh]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    wabfz__ykgh = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        wabfz__ykgh &= A1 != A2[i]
    return wabfz__ykgh


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    tlty__pvs = {'retstep': retstep, 'axis': axis}
    tfb__rmqve = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', tlty__pvs, tfb__rmqve, 'numpy')
    cttt__wkep = False
    if is_overload_none(dtype):
        fuw__ghes = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            cttt__wkep = True
        fuw__ghes = numba.np.numpy_support.as_dtype(dtype).type
    if cttt__wkep:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            gxbla__kmy = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            kyi__azy = np.empty(num, fuw__ghes)
            for i in numba.parfors.parfor.internal_prange(num):
                kyi__azy[i] = fuw__ghes(np.floor(start + i * gxbla__kmy))
            return kyi__azy
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            gxbla__kmy = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            kyi__azy = np.empty(num, fuw__ghes)
            for i in numba.parfors.parfor.internal_prange(num):
                kyi__azy[i] = fuw__ghes(start + i * gxbla__kmy)
            return kyi__azy
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
        nju__xyhz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                nju__xyhz += A[i] == val
        return nju__xyhz > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    tlty__pvs = {'axis': axis, 'out': out, 'keepdims': keepdims}
    tfb__rmqve = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', tlty__pvs, tfb__rmqve, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        nju__xyhz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                nju__xyhz += int(bool(A[i]))
        return nju__xyhz > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    tlty__pvs = {'axis': axis, 'out': out, 'keepdims': keepdims}
    tfb__rmqve = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', tlty__pvs, tfb__rmqve, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        nju__xyhz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                nju__xyhz += int(bool(A[i]))
        return nju__xyhz == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    tlty__pvs = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    tfb__rmqve = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', tlty__pvs, tfb__rmqve, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        qpw__gvk = np.promote_types(numba.np.numpy_support.as_dtype(A.dtype
            ), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            kyi__azy = np.empty(n, qpw__gvk)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(kyi__azy, i)
                    continue
                kyi__azy[i] = np_cbrt_scalar(A[i], qpw__gvk)
            return kyi__azy
        return impl_arr
    qpw__gvk = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, qpw__gvk)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    soqe__dhed = x < 0
    if soqe__dhed:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if soqe__dhed:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    opq__gdh = isinstance(tup, (types.BaseTuple, types.List))
    ubw__xikh = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for gnca__vknc in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                gnca__vknc, 'numpy.hstack()')
            opq__gdh = opq__gdh and bodo.utils.utils.is_array_typ(gnca__vknc,
                False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        opq__gdh = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif ubw__xikh:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        gvcog__rqgi = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for gnca__vknc in gvcog__rqgi.types:
            ubw__xikh = ubw__xikh and bodo.utils.utils.is_array_typ(gnca__vknc,
                False)
    if not (opq__gdh or ubw__xikh):
        return
    if ubw__xikh:

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
    tlty__pvs = {'check_valid': check_valid, 'tol': tol}
    tfb__rmqve = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', tlty__pvs,
        tfb__rmqve, 'numpy')
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
        pvtvg__guiz = mean.shape[0]
        weav__umh = size, pvtvg__guiz
        tnlk__zslrc = np.random.standard_normal(weav__umh)
        cov = cov.astype(np.float64)
        dhnmt__unp, s, hhytz__emql = np.linalg.svd(cov)
        res = np.dot(tnlk__zslrc, np.sqrt(s).reshape(pvtvg__guiz, 1) *
            hhytz__emql)
        dzca__xzobe = res + mean
        return dzca__xzobe
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
            yhzcg__glp = bodo.hiframes.series_kernels._get_type_max_value(arr)
            jyx__apto = typing.builtins.IndexValue(-1, yhzcg__glp)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pone__vnn = typing.builtins.IndexValue(i, arr[i])
                jyx__apto = min(jyx__apto, pone__vnn)
            return jyx__apto.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tolm__caax = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            zgxif__hrm = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yhzcg__glp = tolm__caax(len(arr.dtype.categories) + 1)
            jyx__apto = typing.builtins.IndexValue(-1, yhzcg__glp)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pone__vnn = typing.builtins.IndexValue(i, zgxif__hrm[i])
                jyx__apto = min(jyx__apto, pone__vnn)
            return jyx__apto.index
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
            yhzcg__glp = bodo.hiframes.series_kernels._get_type_min_value(arr)
            jyx__apto = typing.builtins.IndexValue(-1, yhzcg__glp)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pone__vnn = typing.builtins.IndexValue(i, arr[i])
                jyx__apto = max(jyx__apto, pone__vnn)
            return jyx__apto.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tolm__caax = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            zgxif__hrm = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yhzcg__glp = tolm__caax(-1)
            jyx__apto = typing.builtins.IndexValue(-1, yhzcg__glp)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pone__vnn = typing.builtins.IndexValue(i, zgxif__hrm[i])
                jyx__apto = max(jyx__apto, pone__vnn)
            return jyx__apto.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
