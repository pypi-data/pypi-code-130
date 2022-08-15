"""
Implements datetime array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
from numba.core import types
import bodo
from bodo.libs.bodosql_array_kernel_utils import *


@numba.generated_jit(nopython=True)
def dayname(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.dayname_util',
            ['arr'], 0)

    def impl(arr):
        return dayname_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def day_timestamp(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.day_timestamp_util', ['arr'], 0)

    def impl(arr):
        return day_timestamp_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def int_to_days(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.int_to_days_util', ['arr'], 0)

    def impl(arr):
        return int_to_days_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def last_day(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.last_day_util',
            ['arr'], 0)

    def impl(arr):
        return last_day_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def makedate(year, day):
    args = [year, day]
    for vqq__ladu in range(2):
        if isinstance(args[vqq__ladu], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.makedate',
                ['year', 'day'], vqq__ladu)

    def impl(year, day):
        return makedate_util(year, day)
    return impl


@numba.generated_jit(nopython=True)
def monthname(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.monthname_util',
            ['arr'], 0)

    def impl(arr):
        return monthname_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def month_diff(arr0, arr1):
    args = [arr0, arr1]
    for vqq__ladu in range(2):
        if isinstance(args[vqq__ladu], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.month_diff',
                ['arr0', 'arr1'], vqq__ladu)

    def impl(arr0, arr1):
        return month_diff_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def second_timestamp(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.second_timestamp_util', ['arr'], 0
            )

    def impl(arr):
        return second_timestamp_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def weekday(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.weekday_util',
            ['arr'], 0)

    def impl(arr):
        return weekday_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def yearofweekiso(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.yearofweekiso_util', ['arr'], 0)

    def impl(arr):
        return yearofweekiso_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def dayname_util(arr):
    verify_datetime_arg(arr, 'DAYNAME', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = 'res[i] = pd.Timestamp(arg0).day_name()'
    lcalm__fuiqx = bodo.string_array_type
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def day_timestamp_util(arr):
    verify_int_arg(arr, 'day_timestamp', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='D'))"
        )
    lcalm__fuiqx = np.dtype('datetime64[ns]')
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def int_to_days_util(arr):
    verify_int_arg(arr, 'int_to_days', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timedelta(days=arg0))'
        )
    lcalm__fuiqx = np.dtype('timedelta64[ns]')
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def last_day_util(arr):
    verify_datetime_arg(arr, 'LAST_DAY', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0) + pd.tseries.offsets.MonthEnd(n=0, normalize=True))'
        )
    lcalm__fuiqx = np.dtype('datetime64[ns]')
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def makedate_util(year, day):
    verify_int_arg(year, 'MAKEDATE', 'year')
    verify_int_arg(day, 'MAKEDATE', 'day')
    efftg__undn = ['year', 'day']
    hxfuf__wcrt = [year, day]
    laqoy__rpx = [True] * 2
    hndk__qzsaw = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(year=arg0, month=1, day=1) + pd.Timedelta(days=arg1-1))'
        )
    lcalm__fuiqx = np.dtype('datetime64[ns]')
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def monthname_util(arr):
    verify_datetime_arg(arr, 'MONTHNAME', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = 'res[i] = pd.Timestamp(arg0).month_name()'
    lcalm__fuiqx = bodo.string_array_type
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def month_diff_util(arr0, arr1):
    verify_datetime_arg(arr0, 'month_diff', 'arr0')
    verify_datetime_arg(arr1, 'month_diff', 'arr1')
    efftg__undn = ['arr0', 'arr1']
    hxfuf__wcrt = [arr0, arr1]
    laqoy__rpx = [True] * 2
    hndk__qzsaw = 'A0 = bodo.utils.conversion.box_if_dt64(arg0)\n'
    hndk__qzsaw += 'A1 = bodo.utils.conversion.box_if_dt64(arg1)\n'
    hndk__qzsaw += 'delta = 12 * (A0.year - A1.year) + (A0.month - A1.month)\n'
    hndk__qzsaw += (
        'remainder = ((A0 - pd.DateOffset(months=delta)) - A1).value\n')
    hndk__qzsaw += 'if delta > 0 and remainder < 0:\n'
    hndk__qzsaw += '   res[i] = -(delta - 1)\n'
    hndk__qzsaw += 'elif delta < 0 and remainder > 0:\n'
    hndk__qzsaw += '   res[i] = -(delta + 1)\n'
    hndk__qzsaw += 'else:\n'
    hndk__qzsaw += '   res[i] = -delta'
    lcalm__fuiqx = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def second_timestamp_util(arr):
    verify_int_arg(arr, 'second_timestamp', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='s'))"
        )
    lcalm__fuiqx = np.dtype('datetime64[ns]')
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def weekday_util(arr):
    verify_datetime_arg(arr, 'WEEKDAY', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = 'dt = pd.Timestamp(arg0)\n'
    hndk__qzsaw += (
        'res[i] = bodo.hiframes.pd_timestamp_ext.get_day_of_week(dt.year, dt.month, dt.day)'
        )
    lcalm__fuiqx = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)


@numba.generated_jit(nopython=True)
def yearofweekiso_util(arr):
    verify_datetime_arg(arr, 'YEAROFWEEKISO', 'arr')
    efftg__undn = ['arr']
    hxfuf__wcrt = [arr]
    laqoy__rpx = [True]
    hndk__qzsaw = 'dt = pd.Timestamp(arg0)\n'
    hndk__qzsaw += 'res[i] = dt.isocalendar()[0]'
    lcalm__fuiqx = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(efftg__undn, hxfuf__wcrt, laqoy__rpx, hndk__qzsaw,
        lcalm__fuiqx)
