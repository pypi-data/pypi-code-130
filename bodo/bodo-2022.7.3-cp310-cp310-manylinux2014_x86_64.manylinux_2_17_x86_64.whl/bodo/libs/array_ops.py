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
        wlj__teg = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        wlj__teg = False
    elif A == bodo.string_array_type:
        wlj__teg = ''
    elif A == bodo.binary_array_type:
        wlj__teg = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, tdsl__telzj):
                if A[tdsl__telzj] != wlj__teg:
                    xsfbq__ejhm += 1
        return xsfbq__ejhm != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        wlj__teg = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        wlj__teg = False
    elif A == bodo.string_array_type:
        wlj__teg = ''
    elif A == bodo.binary_array_type:
        wlj__teg = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, tdsl__telzj):
                if A[tdsl__telzj] == wlj__teg:
                    xsfbq__ejhm += 1
        return xsfbq__ejhm == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    fveq__jbv = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(fveq__jbv.ctypes, arr,
        parallel, skipna)
    return fveq__jbv[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        sqxk__acgv = len(arr)
        lhnba__kdjt = np.empty(sqxk__acgv, np.bool_)
        for tdsl__telzj in numba.parfors.parfor.internal_prange(sqxk__acgv):
            lhnba__kdjt[tdsl__telzj] = bodo.libs.array_kernels.isna(arr,
                tdsl__telzj)
        return lhnba__kdjt
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
            zmcsm__qfyy = 0
            if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                zmcsm__qfyy = 1
            xsfbq__ejhm += zmcsm__qfyy
        fveq__jbv = xsfbq__ejhm
        return fveq__jbv
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    uickn__glf = array_op_count(arr)
    ppiec__wtcrg = array_op_min(arr)
    hqjyt__hdr = array_op_max(arr)
    aah__wxuya = array_op_mean(arr)
    nydis__nvjnt = array_op_std(arr)
    jkz__scj = array_op_quantile(arr, 0.25)
    hian__nftd = array_op_quantile(arr, 0.5)
    ljoq__tja = array_op_quantile(arr, 0.75)
    return (uickn__glf, aah__wxuya, nydis__nvjnt, ppiec__wtcrg, jkz__scj,
        hian__nftd, ljoq__tja, hqjyt__hdr)


def array_op_describe_dt_impl(arr):
    uickn__glf = array_op_count(arr)
    ppiec__wtcrg = array_op_min(arr)
    hqjyt__hdr = array_op_max(arr)
    aah__wxuya = array_op_mean(arr)
    jkz__scj = array_op_quantile(arr, 0.25)
    hian__nftd = array_op_quantile(arr, 0.5)
    ljoq__tja = array_op_quantile(arr, 0.75)
    return (uickn__glf, aah__wxuya, ppiec__wtcrg, jkz__scj, hian__nftd,
        ljoq__tja, hqjyt__hdr)


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
            nryo__hew = numba.cpython.builtins.get_type_max_value(np.int64)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[tdsl__telzj]))
                    zmcsm__qfyy = 1
                nryo__hew = min(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(nryo__hew,
                xsfbq__ejhm)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            nryo__hew = numba.cpython.builtins.get_type_max_value(np.int64)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[tdsl__telzj]))
                    zmcsm__qfyy = 1
                nryo__hew = min(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            return bodo.hiframes.pd_index_ext._dti_val_finalize(nryo__hew,
                xsfbq__ejhm)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            vyvml__xvexh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nryo__hew = numba.cpython.builtins.get_type_max_value(np.int64)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(
                vyvml__xvexh)):
                hpkur__oopvx = vyvml__xvexh[tdsl__telzj]
                if hpkur__oopvx == -1:
                    continue
                nryo__hew = min(nryo__hew, hpkur__oopvx)
                xsfbq__ejhm += 1
            fveq__jbv = bodo.hiframes.series_kernels._box_cat_val(nryo__hew,
                arr.dtype, xsfbq__ejhm)
            return fveq__jbv
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            nryo__hew = bodo.hiframes.series_kernels._get_date_max_value()
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = arr[tdsl__telzj]
                    zmcsm__qfyy = 1
                nryo__hew = min(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            fveq__jbv = bodo.hiframes.series_kernels._sum_handle_nan(nryo__hew,
                xsfbq__ejhm)
            return fveq__jbv
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nryo__hew = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
            wuiy__swpuv = nryo__hew
            zmcsm__qfyy = 0
            if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                wuiy__swpuv = arr[tdsl__telzj]
                zmcsm__qfyy = 1
            nryo__hew = min(nryo__hew, wuiy__swpuv)
            xsfbq__ejhm += zmcsm__qfyy
        fveq__jbv = bodo.hiframes.series_kernels._sum_handle_nan(nryo__hew,
            xsfbq__ejhm)
        return fveq__jbv
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            nryo__hew = numba.cpython.builtins.get_type_min_value(np.int64)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[tdsl__telzj]))
                    zmcsm__qfyy = 1
                nryo__hew = max(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(nryo__hew,
                xsfbq__ejhm)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            nryo__hew = numba.cpython.builtins.get_type_min_value(np.int64)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[tdsl__telzj]))
                    zmcsm__qfyy = 1
                nryo__hew = max(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            return bodo.hiframes.pd_index_ext._dti_val_finalize(nryo__hew,
                xsfbq__ejhm)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            vyvml__xvexh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nryo__hew = -1
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(
                vyvml__xvexh)):
                nryo__hew = max(nryo__hew, vyvml__xvexh[tdsl__telzj])
            fveq__jbv = bodo.hiframes.series_kernels._box_cat_val(nryo__hew,
                arr.dtype, 1)
            return fveq__jbv
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            nryo__hew = bodo.hiframes.series_kernels._get_date_min_value()
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = nryo__hew
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = arr[tdsl__telzj]
                    zmcsm__qfyy = 1
                nryo__hew = max(nryo__hew, wuiy__swpuv)
                xsfbq__ejhm += zmcsm__qfyy
            fveq__jbv = bodo.hiframes.series_kernels._sum_handle_nan(nryo__hew,
                xsfbq__ejhm)
            return fveq__jbv
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nryo__hew = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
            wuiy__swpuv = nryo__hew
            zmcsm__qfyy = 0
            if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                wuiy__swpuv = arr[tdsl__telzj]
                zmcsm__qfyy = 1
            nryo__hew = max(nryo__hew, wuiy__swpuv)
            xsfbq__ejhm += zmcsm__qfyy
        fveq__jbv = bodo.hiframes.series_kernels._sum_handle_nan(nryo__hew,
            xsfbq__ejhm)
        return fveq__jbv
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
    zakuf__bafin = types.float64
    ebyt__utul = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        zakuf__bafin = types.float32
        ebyt__utul = types.float32
    igw__tpug = zakuf__bafin(0)
    wvr__zpw = ebyt__utul(0)
    kxzww__ehdwh = ebyt__utul(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nryo__hew = igw__tpug
        xsfbq__ejhm = wvr__zpw
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
            wuiy__swpuv = igw__tpug
            zmcsm__qfyy = wvr__zpw
            if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                wuiy__swpuv = arr[tdsl__telzj]
                zmcsm__qfyy = kxzww__ehdwh
            nryo__hew += wuiy__swpuv
            xsfbq__ejhm += zmcsm__qfyy
        fveq__jbv = bodo.hiframes.series_kernels._mean_handle_nan(nryo__hew,
            xsfbq__ejhm)
        return fveq__jbv
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        noe__ilfsw = 0.0
        pdg__rxqh = 0.0
        xsfbq__ejhm = 0
        for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
            wuiy__swpuv = 0.0
            zmcsm__qfyy = 0
            if not bodo.libs.array_kernels.isna(arr, tdsl__telzj
                ) or not skipna:
                wuiy__swpuv = arr[tdsl__telzj]
                zmcsm__qfyy = 1
            noe__ilfsw += wuiy__swpuv
            pdg__rxqh += wuiy__swpuv * wuiy__swpuv
            xsfbq__ejhm += zmcsm__qfyy
        fveq__jbv = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            noe__ilfsw, pdg__rxqh, xsfbq__ejhm, ddof)
        return fveq__jbv
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
                lhnba__kdjt = np.empty(len(q), np.int64)
                for tdsl__telzj in range(len(q)):
                    mws__akuq = np.float64(q[tdsl__telzj])
                    lhnba__kdjt[tdsl__telzj
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), mws__akuq)
                return lhnba__kdjt.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            lhnba__kdjt = np.empty(len(q), np.float64)
            for tdsl__telzj in range(len(q)):
                mws__akuq = np.float64(q[tdsl__telzj])
                lhnba__kdjt[tdsl__telzj] = bodo.libs.array_kernels.quantile(arr
                    , mws__akuq)
            return lhnba__kdjt
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
        ydgit__stu = types.intp
    elif arr.dtype == types.bool_:
        ydgit__stu = np.int64
    else:
        ydgit__stu = arr.dtype
    hnl__xjjw = ydgit__stu(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nryo__hew = hnl__xjjw
            sqxk__acgv = len(arr)
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(sqxk__acgv
                ):
                wuiy__swpuv = hnl__xjjw
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj
                    ) or not skipna:
                    wuiy__swpuv = arr[tdsl__telzj]
                    zmcsm__qfyy = 1
                nryo__hew += wuiy__swpuv
                xsfbq__ejhm += zmcsm__qfyy
            fveq__jbv = bodo.hiframes.series_kernels._var_handle_mincount(
                nryo__hew, xsfbq__ejhm, min_count)
            return fveq__jbv
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nryo__hew = hnl__xjjw
            sqxk__acgv = len(arr)
            for tdsl__telzj in numba.parfors.parfor.internal_prange(sqxk__acgv
                ):
                wuiy__swpuv = hnl__xjjw
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = arr[tdsl__telzj]
                nryo__hew += wuiy__swpuv
            return nryo__hew
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    mro__zgw = arr.dtype(1)
    if arr.dtype == types.bool_:
        mro__zgw = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nryo__hew = mro__zgw
            xsfbq__ejhm = 0
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = mro__zgw
                zmcsm__qfyy = 0
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj
                    ) or not skipna:
                    wuiy__swpuv = arr[tdsl__telzj]
                    zmcsm__qfyy = 1
                xsfbq__ejhm += zmcsm__qfyy
                nryo__hew *= wuiy__swpuv
            fveq__jbv = bodo.hiframes.series_kernels._var_handle_mincount(
                nryo__hew, xsfbq__ejhm, min_count)
            return fveq__jbv
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nryo__hew = mro__zgw
            for tdsl__telzj in numba.parfors.parfor.internal_prange(len(arr)):
                wuiy__swpuv = mro__zgw
                if not bodo.libs.array_kernels.isna(arr, tdsl__telzj):
                    wuiy__swpuv = arr[tdsl__telzj]
                nryo__hew *= wuiy__swpuv
            return nryo__hew
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        tdsl__telzj = bodo.libs.array_kernels._nan_argmax(arr)
        return index[tdsl__telzj]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        tdsl__telzj = bodo.libs.array_kernels._nan_argmin(arr)
        return index[tdsl__telzj]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            lhs__veem = {}
            for lrbdj__wst in values:
                lhs__veem[bodo.utils.conversion.box_if_dt64(lrbdj__wst)] = 0
            return lhs__veem
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
        sqxk__acgv = len(arr)
        lhnba__kdjt = np.empty(sqxk__acgv, np.bool_)
        for tdsl__telzj in numba.parfors.parfor.internal_prange(sqxk__acgv):
            lhnba__kdjt[tdsl__telzj] = bodo.utils.conversion.box_if_dt64(arr
                [tdsl__telzj]) in values
        return lhnba__kdjt
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    qurwu__egfy = len(in_arr_tup) != 1
    qfv__nqbl = list(in_arr_tup.types)
    vpokn__jdncy = 'def impl(in_arr_tup):\n'
    vpokn__jdncy += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    vpokn__jdncy += '  n = len(in_arr_tup[0])\n'
    if qurwu__egfy:
        dpvrt__yrmvt = ', '.join([f'in_arr_tup[{tdsl__telzj}][unused]' for
            tdsl__telzj in range(len(in_arr_tup))])
        xolkq__uqxkn = ', '.join(['False' for mij__oei in range(len(
            in_arr_tup))])
        vpokn__jdncy += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({dpvrt__yrmvt},), ({xolkq__uqxkn},)): 0 for unused in range(0)}}
"""
        vpokn__jdncy += '  map_vector = np.empty(n, np.int64)\n'
        for tdsl__telzj, xqjz__anjq in enumerate(qfv__nqbl):
            vpokn__jdncy += f'  in_lst_{tdsl__telzj} = []\n'
            if is_str_arr_type(xqjz__anjq):
                vpokn__jdncy += f'  total_len_{tdsl__telzj} = 0\n'
            vpokn__jdncy += f'  null_in_lst_{tdsl__telzj} = []\n'
        vpokn__jdncy += '  for i in range(n):\n'
        zjo__ztf = ', '.join([f'in_arr_tup[{tdsl__telzj}][i]' for
            tdsl__telzj in range(len(qfv__nqbl))])
        fph__ryu = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{tdsl__telzj}], i)' for
            tdsl__telzj in range(len(qfv__nqbl))])
        vpokn__jdncy += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({zjo__ztf},), ({fph__ryu},))
"""
        vpokn__jdncy += '    if data_val not in arr_map:\n'
        vpokn__jdncy += '      set_val = len(arr_map)\n'
        vpokn__jdncy += '      values_tup = data_val._data\n'
        vpokn__jdncy += '      nulls_tup = data_val._null_values\n'
        for tdsl__telzj, xqjz__anjq in enumerate(qfv__nqbl):
            vpokn__jdncy += (
                f'      in_lst_{tdsl__telzj}.append(values_tup[{tdsl__telzj}])\n'
                )
            vpokn__jdncy += (
                f'      null_in_lst_{tdsl__telzj}.append(nulls_tup[{tdsl__telzj}])\n'
                )
            if is_str_arr_type(xqjz__anjq):
                vpokn__jdncy += f"""      total_len_{tdsl__telzj}  += nulls_tup[{tdsl__telzj}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{tdsl__telzj}], i)
"""
        vpokn__jdncy += '      arr_map[data_val] = len(arr_map)\n'
        vpokn__jdncy += '    else:\n'
        vpokn__jdncy += '      set_val = arr_map[data_val]\n'
        vpokn__jdncy += '    map_vector[i] = set_val\n'
        vpokn__jdncy += '  n_rows = len(arr_map)\n'
        for tdsl__telzj, xqjz__anjq in enumerate(qfv__nqbl):
            if is_str_arr_type(xqjz__anjq):
                vpokn__jdncy += f"""  out_arr_{tdsl__telzj} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{tdsl__telzj})
"""
            else:
                vpokn__jdncy += f"""  out_arr_{tdsl__telzj} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{tdsl__telzj}], (-1,))
"""
        vpokn__jdncy += '  for j in range(len(arr_map)):\n'
        for tdsl__telzj in range(len(qfv__nqbl)):
            vpokn__jdncy += f'    if null_in_lst_{tdsl__telzj}[j]:\n'
            vpokn__jdncy += (
                f'      bodo.libs.array_kernels.setna(out_arr_{tdsl__telzj}, j)\n'
                )
            vpokn__jdncy += '    else:\n'
            vpokn__jdncy += (
                f'      out_arr_{tdsl__telzj}[j] = in_lst_{tdsl__telzj}[j]\n')
        qblq__yro = ', '.join([f'out_arr_{tdsl__telzj}' for tdsl__telzj in
            range(len(qfv__nqbl))])
        vpokn__jdncy += "  ev.add_attribute('n_map_entries', n_rows)\n"
        vpokn__jdncy += '  ev.finalize()\n'
        vpokn__jdncy += f'  return ({qblq__yro},), map_vector\n'
    else:
        vpokn__jdncy += '  in_arr = in_arr_tup[0]\n'
        vpokn__jdncy += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        vpokn__jdncy += '  map_vector = np.empty(n, np.int64)\n'
        vpokn__jdncy += '  is_na = 0\n'
        vpokn__jdncy += '  in_lst = []\n'
        vpokn__jdncy += '  na_idxs = []\n'
        if is_str_arr_type(qfv__nqbl[0]):
            vpokn__jdncy += '  total_len = 0\n'
        vpokn__jdncy += '  for i in range(n):\n'
        vpokn__jdncy += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        vpokn__jdncy += '      is_na = 1\n'
        vpokn__jdncy += '      # Always put NA in the last location.\n'
        vpokn__jdncy += '      # We use -1 as a placeholder\n'
        vpokn__jdncy += '      set_val = -1\n'
        vpokn__jdncy += '      na_idxs.append(i)\n'
        vpokn__jdncy += '    else:\n'
        vpokn__jdncy += '      data_val = in_arr[i]\n'
        vpokn__jdncy += '      if data_val not in arr_map:\n'
        vpokn__jdncy += '        set_val = len(arr_map)\n'
        vpokn__jdncy += '        in_lst.append(data_val)\n'
        if is_str_arr_type(qfv__nqbl[0]):
            vpokn__jdncy += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        vpokn__jdncy += '        arr_map[data_val] = len(arr_map)\n'
        vpokn__jdncy += '      else:\n'
        vpokn__jdncy += '        set_val = arr_map[data_val]\n'
        vpokn__jdncy += '    map_vector[i] = set_val\n'
        vpokn__jdncy += '  map_vector[na_idxs] = len(arr_map)\n'
        vpokn__jdncy += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(qfv__nqbl[0]):
            vpokn__jdncy += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            vpokn__jdncy += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        vpokn__jdncy += '  for j in range(len(arr_map)):\n'
        vpokn__jdncy += '    out_arr[j] = in_lst[j]\n'
        vpokn__jdncy += '  if is_na:\n'
        vpokn__jdncy += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        vpokn__jdncy += "  ev.add_attribute('n_map_entries', n_rows)\n"
        vpokn__jdncy += '  ev.finalize()\n'
        vpokn__jdncy += f'  return (out_arr,), map_vector\n'
    ipb__xigs = {}
    exec(vpokn__jdncy, {'bodo': bodo, 'np': np, 'tracing': tracing}, ipb__xigs)
    impl = ipb__xigs['impl']
    return impl
