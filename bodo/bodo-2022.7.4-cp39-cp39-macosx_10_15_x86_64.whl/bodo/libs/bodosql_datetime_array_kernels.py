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
    for upzua__vps in range(2):
        if isinstance(args[upzua__vps], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.makedate',
                ['year', 'day'], upzua__vps)

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
    for upzua__vps in range(2):
        if isinstance(args[upzua__vps], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.month_diff',
                ['arr0', 'arr1'], upzua__vps)

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
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = 'res[i] = pd.Timestamp(arg0).day_name()'
    ncr__tlir = bodo.string_array_type
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def day_timestamp_util(arr):
    verify_int_arg(arr, 'day_timestamp', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='D'))"
        )
    ncr__tlir = np.dtype('datetime64[ns]')
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def int_to_days_util(arr):
    verify_int_arg(arr, 'int_to_days', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timedelta(days=arg0))'
        )
    ncr__tlir = np.dtype('timedelta64[ns]')
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def last_day_util(arr):
    verify_datetime_arg(arr, 'LAST_DAY', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0) + pd.tseries.offsets.MonthEnd(n=0, normalize=True))'
        )
    ncr__tlir = np.dtype('datetime64[ns]')
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def makedate_util(year, day):
    verify_int_arg(year, 'MAKEDATE', 'year')
    verify_int_arg(day, 'MAKEDATE', 'day')
    zob__uuze = ['year', 'day']
    rugwy__irxbn = [year, day]
    acqy__fyv = [True] * 2
    fubr__don = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(year=arg0, month=1, day=1) + pd.Timedelta(days=arg1-1))'
        )
    ncr__tlir = np.dtype('datetime64[ns]')
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def monthname_util(arr):
    verify_datetime_arg(arr, 'MONTHNAME', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = 'res[i] = pd.Timestamp(arg0).month_name()'
    ncr__tlir = bodo.string_array_type
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def month_diff_util(arr0, arr1):
    verify_datetime_arg(arr0, 'month_diff', 'arr0')
    verify_datetime_arg(arr1, 'month_diff', 'arr1')
    zob__uuze = ['arr0', 'arr1']
    rugwy__irxbn = [arr0, arr1]
    acqy__fyv = [True] * 2
    fubr__don = 'A0 = bodo.utils.conversion.box_if_dt64(arg0)\n'
    fubr__don += 'A1 = bodo.utils.conversion.box_if_dt64(arg1)\n'
    fubr__don += 'delta = 12 * (A0.year - A1.year) + (A0.month - A1.month)\n'
    fubr__don += (
        'remainder = ((A0 - pd.DateOffset(months=delta)) - A1).value\n')
    fubr__don += 'if delta > 0 and remainder < 0:\n'
    fubr__don += '   res[i] = -(delta - 1)\n'
    fubr__don += 'elif delta < 0 and remainder > 0:\n'
    fubr__don += '   res[i] = -(delta + 1)\n'
    fubr__don += 'else:\n'
    fubr__don += '   res[i] = -delta'
    ncr__tlir = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def second_timestamp_util(arr):
    verify_int_arg(arr, 'second_timestamp', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='s'))"
        )
    ncr__tlir = np.dtype('datetime64[ns]')
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def weekday_util(arr):
    verify_datetime_arg(arr, 'WEEKDAY', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = 'dt = pd.Timestamp(arg0)\n'
    fubr__don += (
        'res[i] = bodo.hiframes.pd_timestamp_ext.get_day_of_week(dt.year, dt.month, dt.day)'
        )
    ncr__tlir = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)


@numba.generated_jit(nopython=True)
def yearofweekiso_util(arr):
    verify_datetime_arg(arr, 'YEAROFWEEKISO', 'arr')
    zob__uuze = ['arr']
    rugwy__irxbn = [arr]
    acqy__fyv = [True]
    fubr__don = 'dt = pd.Timestamp(arg0)\n'
    fubr__don += 'res[i] = dt.isocalendar()[0]'
    ncr__tlir = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zob__uuze, rugwy__irxbn, acqy__fyv, fubr__don,
        ncr__tlir)
