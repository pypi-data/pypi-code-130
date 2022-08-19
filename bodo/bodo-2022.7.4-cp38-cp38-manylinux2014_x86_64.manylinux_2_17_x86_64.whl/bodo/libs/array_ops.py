"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils import tracing
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero, is_str_arr_type


def array_op_any(arr, skipna=True):
    pass


@overload(array_op_any)
def overload_array_op_any(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        qtw__ltv = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        qtw__ltv = False
    elif A == bodo.string_array_type:
        qtw__ltv = ''
    elif A == bodo.binary_array_type:
        qtw__ltv = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qvfwv__hjvq):
                if A[qvfwv__hjvq] != qtw__ltv:
                    gwbmf__zwda += 1
        return gwbmf__zwda != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        qtw__ltv = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        qtw__ltv = False
    elif A == bodo.string_array_type:
        qtw__ltv = ''
    elif A == bodo.binary_array_type:
        qtw__ltv = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qvfwv__hjvq):
                if A[qvfwv__hjvq] == qtw__ltv:
                    gwbmf__zwda += 1
        return gwbmf__zwda == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    vpyfr__nqt = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(vpyfr__nqt.ctypes,
        arr, parallel, skipna)
    return vpyfr__nqt[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yfni__peckp = len(arr)
        nua__cez = np.empty(yfni__peckp, np.bool_)
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(yfni__peckp):
            nua__cez[qvfwv__hjvq] = bodo.libs.array_kernels.isna(arr,
                qvfwv__hjvq)
        return nua__cez
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
            ouro__lfq = 0
            if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                ouro__lfq = 1
            gwbmf__zwda += ouro__lfq
        vpyfr__nqt = gwbmf__zwda
        return vpyfr__nqt
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    tuzkf__firsd = array_op_count(arr)
    lxuu__poe = array_op_min(arr)
    orgp__zbtge = array_op_max(arr)
    strk__fwz = array_op_mean(arr)
    lxcp__uyhs = array_op_std(arr)
    ddn__zzw = array_op_quantile(arr, 0.25)
    xqpid__rigih = array_op_quantile(arr, 0.5)
    yjq__vkrld = array_op_quantile(arr, 0.75)
    return (tuzkf__firsd, strk__fwz, lxcp__uyhs, lxuu__poe, ddn__zzw,
        xqpid__rigih, yjq__vkrld, orgp__zbtge)


def array_op_describe_dt_impl(arr):
    tuzkf__firsd = array_op_count(arr)
    lxuu__poe = array_op_min(arr)
    orgp__zbtge = array_op_max(arr)
    strk__fwz = array_op_mean(arr)
    ddn__zzw = array_op_quantile(arr, 0.25)
    xqpid__rigih = array_op_quantile(arr, 0.5)
    yjq__vkrld = array_op_quantile(arr, 0.75)
    return (tuzkf__firsd, strk__fwz, lxuu__poe, ddn__zzw, xqpid__rigih,
        yjq__vkrld, orgp__zbtge)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


@generated_jit(nopython=True)
def array_op_nbytes(arr):
    return array_op_nbytes_impl


def array_op_nbytes_impl(arr):
    return arr.nbytes


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = numba.cpython.builtins.get_type_max_value(np.int64)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qvfwv__hjvq]))
                    ouro__lfq = 1
                cqiu__hcyp = min(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(cqiu__hcyp,
                gwbmf__zwda)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = numba.cpython.builtins.get_type_max_value(np.int64)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qvfwv__hjvq])
                    ouro__lfq = 1
                cqiu__hcyp = min(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            return bodo.hiframes.pd_index_ext._dti_val_finalize(cqiu__hcyp,
                gwbmf__zwda)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            blf__tttw = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = numba.cpython.builtins.get_type_max_value(np.int64)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(
                blf__tttw)):
                epqy__kcww = blf__tttw[qvfwv__hjvq]
                if epqy__kcww == -1:
                    continue
                cqiu__hcyp = min(cqiu__hcyp, epqy__kcww)
                gwbmf__zwda += 1
            vpyfr__nqt = bodo.hiframes.series_kernels._box_cat_val(cqiu__hcyp,
                arr.dtype, gwbmf__zwda)
            return vpyfr__nqt
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = bodo.hiframes.series_kernels._get_date_max_value()
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = arr[qvfwv__hjvq]
                    ouro__lfq = 1
                cqiu__hcyp = min(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            vpyfr__nqt = bodo.hiframes.series_kernels._sum_handle_nan(
                cqiu__hcyp, gwbmf__zwda)
            return vpyfr__nqt
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        cqiu__hcyp = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
            czqv__jaq = cqiu__hcyp
            ouro__lfq = 0
            if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                czqv__jaq = arr[qvfwv__hjvq]
                ouro__lfq = 1
            cqiu__hcyp = min(cqiu__hcyp, czqv__jaq)
            gwbmf__zwda += ouro__lfq
        vpyfr__nqt = bodo.hiframes.series_kernels._sum_handle_nan(cqiu__hcyp,
            gwbmf__zwda)
        return vpyfr__nqt
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = numba.cpython.builtins.get_type_min_value(np.int64)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qvfwv__hjvq]))
                    ouro__lfq = 1
                cqiu__hcyp = max(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(cqiu__hcyp,
                gwbmf__zwda)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = numba.cpython.builtins.get_type_min_value(np.int64)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qvfwv__hjvq])
                    ouro__lfq = 1
                cqiu__hcyp = max(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            return bodo.hiframes.pd_index_ext._dti_val_finalize(cqiu__hcyp,
                gwbmf__zwda)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            blf__tttw = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = -1
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(
                blf__tttw)):
                cqiu__hcyp = max(cqiu__hcyp, blf__tttw[qvfwv__hjvq])
            vpyfr__nqt = bodo.hiframes.series_kernels._box_cat_val(cqiu__hcyp,
                arr.dtype, 1)
            return vpyfr__nqt
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = bodo.hiframes.series_kernels._get_date_min_value()
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = cqiu__hcyp
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = arr[qvfwv__hjvq]
                    ouro__lfq = 1
                cqiu__hcyp = max(cqiu__hcyp, czqv__jaq)
                gwbmf__zwda += ouro__lfq
            vpyfr__nqt = bodo.hiframes.series_kernels._sum_handle_nan(
                cqiu__hcyp, gwbmf__zwda)
            return vpyfr__nqt
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        cqiu__hcyp = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
            czqv__jaq = cqiu__hcyp
            ouro__lfq = 0
            if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                czqv__jaq = arr[qvfwv__hjvq]
                ouro__lfq = 1
            cqiu__hcyp = max(cqiu__hcyp, czqv__jaq)
            gwbmf__zwda += ouro__lfq
        vpyfr__nqt = bodo.hiframes.series_kernels._sum_handle_nan(cqiu__hcyp,
            gwbmf__zwda)
        return vpyfr__nqt
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    pejhs__mad = types.float64
    cevib__xeh = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        pejhs__mad = types.float32
        cevib__xeh = types.float32
    tflsf__tzl = pejhs__mad(0)
    mjhu__wtgkg = cevib__xeh(0)
    drslu__cforf = cevib__xeh(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        cqiu__hcyp = tflsf__tzl
        gwbmf__zwda = mjhu__wtgkg
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
            czqv__jaq = tflsf__tzl
            ouro__lfq = mjhu__wtgkg
            if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                czqv__jaq = arr[qvfwv__hjvq]
                ouro__lfq = drslu__cforf
            cqiu__hcyp += czqv__jaq
            gwbmf__zwda += ouro__lfq
        vpyfr__nqt = bodo.hiframes.series_kernels._mean_handle_nan(cqiu__hcyp,
            gwbmf__zwda)
        return vpyfr__nqt
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        oqb__wrte = 0.0
        nzfrt__kpn = 0.0
        gwbmf__zwda = 0
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
            czqv__jaq = 0.0
            ouro__lfq = 0
            if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq
                ) or not skipna:
                czqv__jaq = arr[qvfwv__hjvq]
                ouro__lfq = 1
            oqb__wrte += czqv__jaq
            nzfrt__kpn += czqv__jaq * czqv__jaq
            gwbmf__zwda += ouro__lfq
        vpyfr__nqt = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            oqb__wrte, nzfrt__kpn, gwbmf__zwda, ddof)
        return vpyfr__nqt
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                nua__cez = np.empty(len(q), np.int64)
                for qvfwv__hjvq in range(len(q)):
                    ujri__hlfi = np.float64(q[qvfwv__hjvq])
                    nua__cez[qvfwv__hjvq] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), ujri__hlfi)
                return nua__cez.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            nua__cez = np.empty(len(q), np.float64)
            for qvfwv__hjvq in range(len(q)):
                ujri__hlfi = np.float64(q[qvfwv__hjvq])
                nua__cez[qvfwv__hjvq] = bodo.libs.array_kernels.quantile(arr,
                    ujri__hlfi)
            return nua__cez
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        jvi__kslsr = types.intp
    elif arr.dtype == types.bool_:
        jvi__kslsr = np.int64
    else:
        jvi__kslsr = arr.dtype
    jdsa__bper = jvi__kslsr(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = jdsa__bper
            yfni__peckp = len(arr)
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(yfni__peckp
                ):
                czqv__jaq = jdsa__bper
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq
                    ) or not skipna:
                    czqv__jaq = arr[qvfwv__hjvq]
                    ouro__lfq = 1
                cqiu__hcyp += czqv__jaq
                gwbmf__zwda += ouro__lfq
            vpyfr__nqt = bodo.hiframes.series_kernels._var_handle_mincount(
                cqiu__hcyp, gwbmf__zwda, min_count)
            return vpyfr__nqt
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = jdsa__bper
            yfni__peckp = len(arr)
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(yfni__peckp
                ):
                czqv__jaq = jdsa__bper
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = arr[qvfwv__hjvq]
                cqiu__hcyp += czqv__jaq
            return cqiu__hcyp
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    yuix__ixkqo = arr.dtype(1)
    if arr.dtype == types.bool_:
        yuix__ixkqo = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = yuix__ixkqo
            gwbmf__zwda = 0
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = yuix__ixkqo
                ouro__lfq = 0
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq
                    ) or not skipna:
                    czqv__jaq = arr[qvfwv__hjvq]
                    ouro__lfq = 1
                gwbmf__zwda += ouro__lfq
                cqiu__hcyp *= czqv__jaq
            vpyfr__nqt = bodo.hiframes.series_kernels._var_handle_mincount(
                cqiu__hcyp, gwbmf__zwda, min_count)
            return vpyfr__nqt
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            cqiu__hcyp = yuix__ixkqo
            for qvfwv__hjvq in numba.parfors.parfor.internal_prange(len(arr)):
                czqv__jaq = yuix__ixkqo
                if not bodo.libs.array_kernels.isna(arr, qvfwv__hjvq):
                    czqv__jaq = arr[qvfwv__hjvq]
                cqiu__hcyp *= czqv__jaq
            return cqiu__hcyp
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        qvfwv__hjvq = bodo.libs.array_kernels._nan_argmax(arr)
        return index[qvfwv__hjvq]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        qvfwv__hjvq = bodo.libs.array_kernels._nan_argmin(arr)
        return index[qvfwv__hjvq]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            kdi__yte = {}
            for pdn__esg in values:
                kdi__yte[bodo.utils.conversion.box_if_dt64(pdn__esg)] = 0
            return kdi__yte
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        yfni__peckp = len(arr)
        nua__cez = np.empty(yfni__peckp, np.bool_)
        for qvfwv__hjvq in numba.parfors.parfor.internal_prange(yfni__peckp):
            nua__cez[qvfwv__hjvq] = bodo.utils.conversion.box_if_dt64(arr[
                qvfwv__hjvq]) in values
        return nua__cez
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    zcgi__jamuc = len(in_arr_tup) != 1
    iqw__yqdbg = list(in_arr_tup.types)
    foi__obwhb = 'def impl(in_arr_tup):\n'
    foi__obwhb += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    foi__obwhb += '  n = len(in_arr_tup[0])\n'
    if zcgi__jamuc:
        qfd__vcuue = ', '.join([f'in_arr_tup[{qvfwv__hjvq}][unused]' for
            qvfwv__hjvq in range(len(in_arr_tup))])
        qmsbh__iftm = ', '.join(['False' for him__rcazy in range(len(
            in_arr_tup))])
        foi__obwhb += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({qfd__vcuue},), ({qmsbh__iftm},)): 0 for unused in range(0)}}
"""
        foi__obwhb += '  map_vector = np.empty(n, np.int64)\n'
        for qvfwv__hjvq, xby__hezuz in enumerate(iqw__yqdbg):
            foi__obwhb += f'  in_lst_{qvfwv__hjvq} = []\n'
            if is_str_arr_type(xby__hezuz):
                foi__obwhb += f'  total_len_{qvfwv__hjvq} = 0\n'
            foi__obwhb += f'  null_in_lst_{qvfwv__hjvq} = []\n'
        foi__obwhb += '  for i in range(n):\n'
        oly__kwg = ', '.join([f'in_arr_tup[{qvfwv__hjvq}][i]' for
            qvfwv__hjvq in range(len(iqw__yqdbg))])
        abtsu__aggra = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{qvfwv__hjvq}], i)' for
            qvfwv__hjvq in range(len(iqw__yqdbg))])
        foi__obwhb += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({oly__kwg},), ({abtsu__aggra},))
"""
        foi__obwhb += '    if data_val not in arr_map:\n'
        foi__obwhb += '      set_val = len(arr_map)\n'
        foi__obwhb += '      values_tup = data_val._data\n'
        foi__obwhb += '      nulls_tup = data_val._null_values\n'
        for qvfwv__hjvq, xby__hezuz in enumerate(iqw__yqdbg):
            foi__obwhb += (
                f'      in_lst_{qvfwv__hjvq}.append(values_tup[{qvfwv__hjvq}])\n'
                )
            foi__obwhb += (
                f'      null_in_lst_{qvfwv__hjvq}.append(nulls_tup[{qvfwv__hjvq}])\n'
                )
            if is_str_arr_type(xby__hezuz):
                foi__obwhb += f"""      total_len_{qvfwv__hjvq}  += nulls_tup[{qvfwv__hjvq}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{qvfwv__hjvq}], i)
"""
        foi__obwhb += '      arr_map[data_val] = len(arr_map)\n'
        foi__obwhb += '    else:\n'
        foi__obwhb += '      set_val = arr_map[data_val]\n'
        foi__obwhb += '    map_vector[i] = set_val\n'
        foi__obwhb += '  n_rows = len(arr_map)\n'
        for qvfwv__hjvq, xby__hezuz in enumerate(iqw__yqdbg):
            if is_str_arr_type(xby__hezuz):
                foi__obwhb += f"""  out_arr_{qvfwv__hjvq} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{qvfwv__hjvq})
"""
            else:
                foi__obwhb += f"""  out_arr_{qvfwv__hjvq} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{qvfwv__hjvq}], (-1,))
"""
        foi__obwhb += '  for j in range(len(arr_map)):\n'
        for qvfwv__hjvq in range(len(iqw__yqdbg)):
            foi__obwhb += f'    if null_in_lst_{qvfwv__hjvq}[j]:\n'
            foi__obwhb += (
                f'      bodo.libs.array_kernels.setna(out_arr_{qvfwv__hjvq}, j)\n'
                )
            foi__obwhb += '    else:\n'
            foi__obwhb += (
                f'      out_arr_{qvfwv__hjvq}[j] = in_lst_{qvfwv__hjvq}[j]\n')
        kgxms__rndwd = ', '.join([f'out_arr_{qvfwv__hjvq}' for qvfwv__hjvq in
            range(len(iqw__yqdbg))])
        foi__obwhb += "  ev.add_attribute('n_map_entries', n_rows)\n"
        foi__obwhb += '  ev.finalize()\n'
        foi__obwhb += f'  return ({kgxms__rndwd},), map_vector\n'
    else:
        foi__obwhb += '  in_arr = in_arr_tup[0]\n'
        foi__obwhb += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        foi__obwhb += '  map_vector = np.empty(n, np.int64)\n'
        foi__obwhb += '  is_na = 0\n'
        foi__obwhb += '  in_lst = []\n'
        foi__obwhb += '  na_idxs = []\n'
        if is_str_arr_type(iqw__yqdbg[0]):
            foi__obwhb += '  total_len = 0\n'
        foi__obwhb += '  for i in range(n):\n'
        foi__obwhb += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        foi__obwhb += '      is_na = 1\n'
        foi__obwhb += '      # Always put NA in the last location.\n'
        foi__obwhb += '      # We use -1 as a placeholder\n'
        foi__obwhb += '      set_val = -1\n'
        foi__obwhb += '      na_idxs.append(i)\n'
        foi__obwhb += '    else:\n'
        foi__obwhb += '      data_val = in_arr[i]\n'
        foi__obwhb += '      if data_val not in arr_map:\n'
        foi__obwhb += '        set_val = len(arr_map)\n'
        foi__obwhb += '        in_lst.append(data_val)\n'
        if is_str_arr_type(iqw__yqdbg[0]):
            foi__obwhb += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        foi__obwhb += '        arr_map[data_val] = len(arr_map)\n'
        foi__obwhb += '      else:\n'
        foi__obwhb += '        set_val = arr_map[data_val]\n'
        foi__obwhb += '    map_vector[i] = set_val\n'
        foi__obwhb += '  map_vector[na_idxs] = len(arr_map)\n'
        foi__obwhb += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(iqw__yqdbg[0]):
            foi__obwhb += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            foi__obwhb += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        foi__obwhb += '  for j in range(len(arr_map)):\n'
        foi__obwhb += '    out_arr[j] = in_lst[j]\n'
        foi__obwhb += '  if is_na:\n'
        foi__obwhb += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        foi__obwhb += "  ev.add_attribute('n_map_entries', n_rows)\n"
        foi__obwhb += '  ev.finalize()\n'
        foi__obwhb += f'  return (out_arr,), map_vector\n'
    ypib__zuam = {}
    exec(foi__obwhb, {'bodo': bodo, 'np': np, 'tracing': tracing}, ypib__zuam)
    impl = ypib__zuam['impl']
    return impl
