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
        ykx__kohgb = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ykx__kohgb = False
    elif A == bodo.string_array_type:
        ykx__kohgb = ''
    elif A == bodo.binary_array_type:
        ykx__kohgb = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, lqce__scm):
                if A[lqce__scm] != ykx__kohgb:
                    fcyln__esc += 1
        return fcyln__esc != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        ykx__kohgb = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ykx__kohgb = False
    elif A == bodo.string_array_type:
        ykx__kohgb = ''
    elif A == bodo.binary_array_type:
        ykx__kohgb = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, lqce__scm):
                if A[lqce__scm] == ykx__kohgb:
                    fcyln__esc += 1
        return fcyln__esc == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    fif__mnhj = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(fif__mnhj.ctypes, arr,
        parallel, skipna)
    return fif__mnhj[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        rqg__wpvm = len(arr)
        fmp__gxps = np.empty(rqg__wpvm, np.bool_)
        for lqce__scm in numba.parfors.parfor.internal_prange(rqg__wpvm):
            fmp__gxps[lqce__scm] = bodo.libs.array_kernels.isna(arr, lqce__scm)
        return fmp__gxps
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
            iakxt__iwa = 0
            if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                iakxt__iwa = 1
            fcyln__esc += iakxt__iwa
        fif__mnhj = fcyln__esc
        return fif__mnhj
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    zzdv__pioua = array_op_count(arr)
    pivml__erg = array_op_min(arr)
    vlyjw__tnx = array_op_max(arr)
    lss__urz = array_op_mean(arr)
    jvs__kczh = array_op_std(arr)
    wpd__ashne = array_op_quantile(arr, 0.25)
    fzyof__bhh = array_op_quantile(arr, 0.5)
    kmbyl__fmcjo = array_op_quantile(arr, 0.75)
    return (zzdv__pioua, lss__urz, jvs__kczh, pivml__erg, wpd__ashne,
        fzyof__bhh, kmbyl__fmcjo, vlyjw__tnx)


def array_op_describe_dt_impl(arr):
    zzdv__pioua = array_op_count(arr)
    pivml__erg = array_op_min(arr)
    vlyjw__tnx = array_op_max(arr)
    lss__urz = array_op_mean(arr)
    wpd__ashne = array_op_quantile(arr, 0.25)
    fzyof__bhh = array_op_quantile(arr, 0.5)
    kmbyl__fmcjo = array_op_quantile(arr, 0.75)
    return (zzdv__pioua, lss__urz, pivml__erg, wpd__ashne, fzyof__bhh,
        kmbyl__fmcjo, vlyjw__tnx)


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
            xzql__ocbl = numba.cpython.builtins.get_type_max_value(np.int64)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[lqce__scm]))
                    iakxt__iwa = 1
                xzql__ocbl = min(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xzql__ocbl,
                fcyln__esc)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = numba.cpython.builtins.get_type_max_value(np.int64)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[lqce__scm])
                    iakxt__iwa = 1
                xzql__ocbl = min(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xzql__ocbl,
                fcyln__esc)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            qif__bpvo = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xzql__ocbl = numba.cpython.builtins.get_type_max_value(np.int64)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(
                qif__bpvo)):
                jhonw__muzsx = qif__bpvo[lqce__scm]
                if jhonw__muzsx == -1:
                    continue
                xzql__ocbl = min(xzql__ocbl, jhonw__muzsx)
                fcyln__esc += 1
            fif__mnhj = bodo.hiframes.series_kernels._box_cat_val(xzql__ocbl,
                arr.dtype, fcyln__esc)
            return fif__mnhj
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = bodo.hiframes.series_kernels._get_date_max_value()
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = arr[lqce__scm]
                    iakxt__iwa = 1
                xzql__ocbl = min(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            fif__mnhj = bodo.hiframes.series_kernels._sum_handle_nan(xzql__ocbl
                , fcyln__esc)
            return fif__mnhj
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xzql__ocbl = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
            nqc__hov = xzql__ocbl
            iakxt__iwa = 0
            if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                nqc__hov = arr[lqce__scm]
                iakxt__iwa = 1
            xzql__ocbl = min(xzql__ocbl, nqc__hov)
            fcyln__esc += iakxt__iwa
        fif__mnhj = bodo.hiframes.series_kernels._sum_handle_nan(xzql__ocbl,
            fcyln__esc)
        return fif__mnhj
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = numba.cpython.builtins.get_type_min_value(np.int64)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[lqce__scm]))
                    iakxt__iwa = 1
                xzql__ocbl = max(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xzql__ocbl,
                fcyln__esc)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = numba.cpython.builtins.get_type_min_value(np.int64)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[lqce__scm])
                    iakxt__iwa = 1
                xzql__ocbl = max(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xzql__ocbl,
                fcyln__esc)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            qif__bpvo = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xzql__ocbl = -1
            for lqce__scm in numba.parfors.parfor.internal_prange(len(
                qif__bpvo)):
                xzql__ocbl = max(xzql__ocbl, qif__bpvo[lqce__scm])
            fif__mnhj = bodo.hiframes.series_kernels._box_cat_val(xzql__ocbl,
                arr.dtype, 1)
            return fif__mnhj
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = bodo.hiframes.series_kernels._get_date_min_value()
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = xzql__ocbl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = arr[lqce__scm]
                    iakxt__iwa = 1
                xzql__ocbl = max(xzql__ocbl, nqc__hov)
                fcyln__esc += iakxt__iwa
            fif__mnhj = bodo.hiframes.series_kernels._sum_handle_nan(xzql__ocbl
                , fcyln__esc)
            return fif__mnhj
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xzql__ocbl = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
            nqc__hov = xzql__ocbl
            iakxt__iwa = 0
            if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                nqc__hov = arr[lqce__scm]
                iakxt__iwa = 1
            xzql__ocbl = max(xzql__ocbl, nqc__hov)
            fcyln__esc += iakxt__iwa
        fif__mnhj = bodo.hiframes.series_kernels._sum_handle_nan(xzql__ocbl,
            fcyln__esc)
        return fif__mnhj
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
    rbqac__qoq = types.float64
    fdik__ehy = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        rbqac__qoq = types.float32
        fdik__ehy = types.float32
    nxxqa__rqov = rbqac__qoq(0)
    supc__tnxtr = fdik__ehy(0)
    qftt__sjkp = fdik__ehy(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xzql__ocbl = nxxqa__rqov
        fcyln__esc = supc__tnxtr
        for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
            nqc__hov = nxxqa__rqov
            iakxt__iwa = supc__tnxtr
            if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                nqc__hov = arr[lqce__scm]
                iakxt__iwa = qftt__sjkp
            xzql__ocbl += nqc__hov
            fcyln__esc += iakxt__iwa
        fif__mnhj = bodo.hiframes.series_kernels._mean_handle_nan(xzql__ocbl,
            fcyln__esc)
        return fif__mnhj
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        rki__oyuge = 0.0
        lhk__nrri = 0.0
        fcyln__esc = 0
        for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
            nqc__hov = 0.0
            iakxt__iwa = 0
            if not bodo.libs.array_kernels.isna(arr, lqce__scm) or not skipna:
                nqc__hov = arr[lqce__scm]
                iakxt__iwa = 1
            rki__oyuge += nqc__hov
            lhk__nrri += nqc__hov * nqc__hov
            fcyln__esc += iakxt__iwa
        fif__mnhj = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            rki__oyuge, lhk__nrri, fcyln__esc, ddof)
        return fif__mnhj
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
                fmp__gxps = np.empty(len(q), np.int64)
                for lqce__scm in range(len(q)):
                    vrmo__qfmt = np.float64(q[lqce__scm])
                    fmp__gxps[lqce__scm] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), vrmo__qfmt)
                return fmp__gxps.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            fmp__gxps = np.empty(len(q), np.float64)
            for lqce__scm in range(len(q)):
                vrmo__qfmt = np.float64(q[lqce__scm])
                fmp__gxps[lqce__scm] = bodo.libs.array_kernels.quantile(arr,
                    vrmo__qfmt)
            return fmp__gxps
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
        zsik__dcu = types.intp
    elif arr.dtype == types.bool_:
        zsik__dcu = np.int64
    else:
        zsik__dcu = arr.dtype
    ylcp__lypo = zsik__dcu(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = ylcp__lypo
            rqg__wpvm = len(arr)
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(rqg__wpvm):
                nqc__hov = ylcp__lypo
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm
                    ) or not skipna:
                    nqc__hov = arr[lqce__scm]
                    iakxt__iwa = 1
                xzql__ocbl += nqc__hov
                fcyln__esc += iakxt__iwa
            fif__mnhj = bodo.hiframes.series_kernels._var_handle_mincount(
                xzql__ocbl, fcyln__esc, min_count)
            return fif__mnhj
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = ylcp__lypo
            rqg__wpvm = len(arr)
            for lqce__scm in numba.parfors.parfor.internal_prange(rqg__wpvm):
                nqc__hov = ylcp__lypo
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = arr[lqce__scm]
                xzql__ocbl += nqc__hov
            return xzql__ocbl
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    nnwc__qibl = arr.dtype(1)
    if arr.dtype == types.bool_:
        nnwc__qibl = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = nnwc__qibl
            fcyln__esc = 0
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = nnwc__qibl
                iakxt__iwa = 0
                if not bodo.libs.array_kernels.isna(arr, lqce__scm
                    ) or not skipna:
                    nqc__hov = arr[lqce__scm]
                    iakxt__iwa = 1
                fcyln__esc += iakxt__iwa
                xzql__ocbl *= nqc__hov
            fif__mnhj = bodo.hiframes.series_kernels._var_handle_mincount(
                xzql__ocbl, fcyln__esc, min_count)
            return fif__mnhj
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xzql__ocbl = nnwc__qibl
            for lqce__scm in numba.parfors.parfor.internal_prange(len(arr)):
                nqc__hov = nnwc__qibl
                if not bodo.libs.array_kernels.isna(arr, lqce__scm):
                    nqc__hov = arr[lqce__scm]
                xzql__ocbl *= nqc__hov
            return xzql__ocbl
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        lqce__scm = bodo.libs.array_kernels._nan_argmax(arr)
        return index[lqce__scm]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        lqce__scm = bodo.libs.array_kernels._nan_argmin(arr)
        return index[lqce__scm]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            mqg__rdx = {}
            for spii__datdi in values:
                mqg__rdx[bodo.utils.conversion.box_if_dt64(spii__datdi)] = 0
            return mqg__rdx
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
        rqg__wpvm = len(arr)
        fmp__gxps = np.empty(rqg__wpvm, np.bool_)
        for lqce__scm in numba.parfors.parfor.internal_prange(rqg__wpvm):
            fmp__gxps[lqce__scm] = bodo.utils.conversion.box_if_dt64(arr[
                lqce__scm]) in values
        return fmp__gxps
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    wgw__rcu = len(in_arr_tup) != 1
    uekrs__huys = list(in_arr_tup.types)
    srqqg__iiiel = 'def impl(in_arr_tup):\n'
    srqqg__iiiel += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    srqqg__iiiel += '  n = len(in_arr_tup[0])\n'
    if wgw__rcu:
        hyv__rxd = ', '.join([f'in_arr_tup[{lqce__scm}][unused]' for
            lqce__scm in range(len(in_arr_tup))])
        isfob__devg = ', '.join(['False' for amf__xzqkz in range(len(
            in_arr_tup))])
        srqqg__iiiel += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({hyv__rxd},), ({isfob__devg},)): 0 for unused in range(0)}}
"""
        srqqg__iiiel += '  map_vector = np.empty(n, np.int64)\n'
        for lqce__scm, vcn__ull in enumerate(uekrs__huys):
            srqqg__iiiel += f'  in_lst_{lqce__scm} = []\n'
            if is_str_arr_type(vcn__ull):
                srqqg__iiiel += f'  total_len_{lqce__scm} = 0\n'
            srqqg__iiiel += f'  null_in_lst_{lqce__scm} = []\n'
        srqqg__iiiel += '  for i in range(n):\n'
        fteot__snni = ', '.join([f'in_arr_tup[{lqce__scm}][i]' for
            lqce__scm in range(len(uekrs__huys))])
        die__uwmd = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{lqce__scm}], i)' for
            lqce__scm in range(len(uekrs__huys))])
        srqqg__iiiel += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({fteot__snni},), ({die__uwmd},))
"""
        srqqg__iiiel += '    if data_val not in arr_map:\n'
        srqqg__iiiel += '      set_val = len(arr_map)\n'
        srqqg__iiiel += '      values_tup = data_val._data\n'
        srqqg__iiiel += '      nulls_tup = data_val._null_values\n'
        for lqce__scm, vcn__ull in enumerate(uekrs__huys):
            srqqg__iiiel += (
                f'      in_lst_{lqce__scm}.append(values_tup[{lqce__scm}])\n')
            srqqg__iiiel += (
                f'      null_in_lst_{lqce__scm}.append(nulls_tup[{lqce__scm}])\n'
                )
            if is_str_arr_type(vcn__ull):
                srqqg__iiiel += f"""      total_len_{lqce__scm}  += nulls_tup[{lqce__scm}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{lqce__scm}], i)
"""
        srqqg__iiiel += '      arr_map[data_val] = len(arr_map)\n'
        srqqg__iiiel += '    else:\n'
        srqqg__iiiel += '      set_val = arr_map[data_val]\n'
        srqqg__iiiel += '    map_vector[i] = set_val\n'
        srqqg__iiiel += '  n_rows = len(arr_map)\n'
        for lqce__scm, vcn__ull in enumerate(uekrs__huys):
            if is_str_arr_type(vcn__ull):
                srqqg__iiiel += f"""  out_arr_{lqce__scm} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{lqce__scm})
"""
            else:
                srqqg__iiiel += f"""  out_arr_{lqce__scm} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{lqce__scm}], (-1,))
"""
        srqqg__iiiel += '  for j in range(len(arr_map)):\n'
        for lqce__scm in range(len(uekrs__huys)):
            srqqg__iiiel += f'    if null_in_lst_{lqce__scm}[j]:\n'
            srqqg__iiiel += (
                f'      bodo.libs.array_kernels.setna(out_arr_{lqce__scm}, j)\n'
                )
            srqqg__iiiel += '    else:\n'
            srqqg__iiiel += (
                f'      out_arr_{lqce__scm}[j] = in_lst_{lqce__scm}[j]\n')
        lnb__osief = ', '.join([f'out_arr_{lqce__scm}' for lqce__scm in
            range(len(uekrs__huys))])
        srqqg__iiiel += "  ev.add_attribute('n_map_entries', n_rows)\n"
        srqqg__iiiel += '  ev.finalize()\n'
        srqqg__iiiel += f'  return ({lnb__osief},), map_vector\n'
    else:
        srqqg__iiiel += '  in_arr = in_arr_tup[0]\n'
        srqqg__iiiel += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        srqqg__iiiel += '  map_vector = np.empty(n, np.int64)\n'
        srqqg__iiiel += '  is_na = 0\n'
        srqqg__iiiel += '  in_lst = []\n'
        srqqg__iiiel += '  na_idxs = []\n'
        if is_str_arr_type(uekrs__huys[0]):
            srqqg__iiiel += '  total_len = 0\n'
        srqqg__iiiel += '  for i in range(n):\n'
        srqqg__iiiel += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        srqqg__iiiel += '      is_na = 1\n'
        srqqg__iiiel += '      # Always put NA in the last location.\n'
        srqqg__iiiel += '      # We use -1 as a placeholder\n'
        srqqg__iiiel += '      set_val = -1\n'
        srqqg__iiiel += '      na_idxs.append(i)\n'
        srqqg__iiiel += '    else:\n'
        srqqg__iiiel += '      data_val = in_arr[i]\n'
        srqqg__iiiel += '      if data_val not in arr_map:\n'
        srqqg__iiiel += '        set_val = len(arr_map)\n'
        srqqg__iiiel += '        in_lst.append(data_val)\n'
        if is_str_arr_type(uekrs__huys[0]):
            srqqg__iiiel += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        srqqg__iiiel += '        arr_map[data_val] = len(arr_map)\n'
        srqqg__iiiel += '      else:\n'
        srqqg__iiiel += '        set_val = arr_map[data_val]\n'
        srqqg__iiiel += '    map_vector[i] = set_val\n'
        srqqg__iiiel += '  map_vector[na_idxs] = len(arr_map)\n'
        srqqg__iiiel += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(uekrs__huys[0]):
            srqqg__iiiel += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            srqqg__iiiel += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        srqqg__iiiel += '  for j in range(len(arr_map)):\n'
        srqqg__iiiel += '    out_arr[j] = in_lst[j]\n'
        srqqg__iiiel += '  if is_na:\n'
        srqqg__iiiel += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        srqqg__iiiel += "  ev.add_attribute('n_map_entries', n_rows)\n"
        srqqg__iiiel += '  ev.finalize()\n'
        srqqg__iiiel += f'  return (out_arr,), map_vector\n'
    xujx__ittv = {}
    exec(srqqg__iiiel, {'bodo': bodo, 'np': np, 'tracing': tracing}, xujx__ittv
        )
    impl = xujx__ittv['impl']
    return impl
