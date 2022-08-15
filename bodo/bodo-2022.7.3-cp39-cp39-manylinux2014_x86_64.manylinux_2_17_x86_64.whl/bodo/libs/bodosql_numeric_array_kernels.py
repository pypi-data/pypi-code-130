"""
Implements numerical array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, raise_bodo_error


@numba.generated_jit(nopython=True)
def bitand(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitand',
                ['A', 'B'], oku__jtf)

    def impl(A, B):
        return bitand_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitleftshift(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitleftshift', ['A', 'B'],
                oku__jtf)

    def impl(A, B):
        return bitleftshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitnot(A):
    if isinstance(A, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.bitnot_util',
            ['A'], 0)

    def impl(A):
        return bitnot_util(A)
    return impl


@numba.generated_jit(nopython=True)
def bitor(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitor',
                ['A', 'B'], oku__jtf)

    def impl(A, B):
        return bitor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitrightshift(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitrightshift', ['A', 'B'],
                oku__jtf)

    def impl(A, B):
        return bitrightshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitxor(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitxor',
                ['A', 'B'], oku__jtf)

    def impl(A, B):
        return bitxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for oku__jtf in range(3):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], oku__jtf)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def getbit(A, B):
    args = [A, B]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.getbit',
                ['A', 'B'], oku__jtf)

    def impl(A, B):
        return getbit_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    args = [lat1, lon1, lat2, lon2]
    for oku__jtf in range(4):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.haversine',
                ['lat1', 'lon1', 'lat2', 'lon2'], oku__jtf)

    def impl(lat1, lon1, lat2, lon2):
        return haversine_util(lat1, lon1, lat2, lon2)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], oku__jtf)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for oku__jtf in range(2):
        if isinstance(args[oku__jtf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], oku__jtf)

    def impl(arr, base):
        return log_util(arr, base)
    return impl


@numba.generated_jit(nopython=True)
def negate(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.negate_util',
            ['arr'], 0)

    def impl(arr):
        return negate_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def bitand_util(A, B):
    verify_int_arg(A, 'bitand', 'A')
    verify_int_arg(B, 'bitand', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = arg0 & arg1'
    wjhw__sfed = get_common_broadcasted_type([A, B], 'bitand')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def bitleftshift_util(A, B):
    verify_int_arg(A, 'bitleftshift', 'A')
    verify_int_arg(B, 'bitleftshift', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = arg0 << arg1'
    wjhw__sfed = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def bitnot_util(A):
    verify_int_arg(A, 'bitnot', 'A')
    ehvg__jrxog = ['A']
    tsgx__zfrp = [A]
    iscut__guzw = [True]
    pic__ejknl = 'res[i] = ~arg0'
    if A == bodo.none:
        wjhw__sfed = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            ohgp__tvt = A.dtype
        else:
            ohgp__tvt = A
        wjhw__sfed = bodo.libs.int_arr_ext.IntegerArrayType(ohgp__tvt)
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def bitor_util(A, B):
    verify_int_arg(A, 'bitor', 'A')
    verify_int_arg(B, 'bitor', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = arg0 | arg1'
    wjhw__sfed = get_common_broadcasted_type([A, B], 'bitor')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def bitrightshift_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    if A == bodo.none:
        ohgp__tvt = wjhw__sfed = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            ohgp__tvt = A.dtype
        else:
            ohgp__tvt = A
        wjhw__sfed = bodo.libs.int_arr_ext.IntegerArrayType(ohgp__tvt)
    pic__ejknl = f'res[i] = arg0 >> arg1\n'
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def bitxor_util(A, B):
    verify_int_arg(A, 'bitxor', 'A')
    verify_int_arg(B, 'bitxor', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = arg0 ^ arg1'
    wjhw__sfed = get_common_broadcasted_type([A, B], 'bitxor')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    ehvg__jrxog = ['arr', 'old_base', 'new_base']
    tsgx__zfrp = [arr, old_base, new_base]
    iscut__guzw = [True] * 3
    pic__ejknl = 'old_val = int(arg0, arg1)\n'
    pic__ejknl += 'if arg2 == 2:\n'
    pic__ejknl += "   res[i] = format(old_val, 'b')\n"
    pic__ejknl += 'elif arg2 == 8:\n'
    pic__ejknl += "   res[i] = format(old_val, 'o')\n"
    pic__ejknl += 'elif arg2 == 10:\n'
    pic__ejknl += "   res[i] = format(old_val, 'd')\n"
    pic__ejknl += 'elif arg2 == 16:\n'
    pic__ejknl += "   res[i] = format(old_val, 'x')\n"
    pic__ejknl += 'else:\n'
    pic__ejknl += '   bodo.libs.array_kernels.setna(res, i)\n'
    wjhw__sfed = bodo.string_array_type
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def getbit_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    ehvg__jrxog = ['A', 'B']
    tsgx__zfrp = [A, B]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = (arg0 >> arg1) & 1'
    wjhw__sfed = bodo.libs.int_arr_ext.IntegerArrayType(types.uint8)
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def haversine_util(lat1, lon1, lat2, lon2):
    verify_int_float_arg(lat1, 'HAVERSINE', 'lat1')
    verify_int_float_arg(lon1, 'HAVERSINE', 'lon1')
    verify_int_float_arg(lat2, 'HAVERSINE', 'lat2')
    verify_int_float_arg(lon2, 'HAVERSINE', 'lon2')
    ehvg__jrxog = ['lat1', 'lon1', 'lat2', 'lon2']
    tsgx__zfrp = [lat1, lon1, lat2, lon2]
    jpu__nilcs = [True] * 4
    pic__ejknl = (
        'arg0, arg1, arg2, arg3 = map(np.radians, (arg0, arg1, arg2, arg3))\n')
    pja__evvr = '(arg2 - arg0) * 0.5'
    dlxa__xkygr = '(arg3 - arg1) * 0.5'
    rrvm__fko = (
        f'np.square(np.sin({pja__evvr})) + (np.cos(arg0) * np.cos(arg2) * np.square(np.sin({dlxa__xkygr})))'
        )
    pic__ejknl += f'res[i] = 12742.0 * np.arcsin(np.sqrt({rrvm__fko}))\n'
    wjhw__sfed = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, jpu__nilcs, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    ehvg__jrxog = ['arr', 'divisor']
    tsgx__zfrp = [arr, divisor]
    jpu__nilcs = [True] * 2
    pic__ejknl = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    wjhw__sfed = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, jpu__nilcs, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    ehvg__jrxog = ['arr', 'base']
    tsgx__zfrp = [arr, base]
    iscut__guzw = [True] * 2
    pic__ejknl = 'res[i] = np.log(arg0) / np.log(arg1)'
    wjhw__sfed = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    ehvg__jrxog = ['arr']
    tsgx__zfrp = [arr]
    iscut__guzw = [True]
    if arr == bodo.none:
        ohgp__tvt = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        ohgp__tvt = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        ohgp__tvt = arr.data.dtype
    else:
        ohgp__tvt = arr
    pic__ejknl = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(ohgp__tvt, 'res[i] = -arg0')
    ohgp__tvt = {types.uint8: types.int16, types.uint16: types.int32, types
        .uint32: types.int64, types.uint64: types.int64}.get(ohgp__tvt,
        ohgp__tvt)
    wjhw__sfed = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(ohgp__tvt))
    return gen_vectorized(ehvg__jrxog, tsgx__zfrp, iscut__guzw, pic__ejknl,
        wjhw__sfed)


def rank_sql(arr_tup, method='average', pct=False):
    return


@overload(rank_sql, no_unliteral=True)
def overload_rank_sql(arr_tup, method='average', pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    raa__fplo = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        raa__fplo += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        raa__fplo += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        raa__fplo += '  for arr in arr_tup:\n'
        raa__fplo += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        raa__fplo += '    obs = obs | next_obs \n'
        raa__fplo += '  dense = obs.cumsum()\n'
        if method == 'dense':
            raa__fplo += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            raa__fplo += '    dense,\n'
            raa__fplo += '    new_dtype=np.float64,\n'
            raa__fplo += '    copy=True,\n'
            raa__fplo += '    nan_to_str=False,\n'
            raa__fplo += '    from_series=True,\n'
            raa__fplo += '  )\n'
        else:
            raa__fplo += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            raa__fplo += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                raa__fplo += '  ret = count_float[dense]\n'
            elif method == 'min':
                raa__fplo += '  ret = count_float[dense - 1] + 1\n'
            else:
                raa__fplo += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            raa__fplo += '  div_val = np.max(ret)\n'
        else:
            raa__fplo += '  div_val = arr.size\n'
        raa__fplo += '  for i in range(len(ret)):\n'
        raa__fplo += '    ret[i] = ret[i] / div_val\n'
    raa__fplo += '  return ret\n'
    pfab__qpnkf = {}
    exec(raa__fplo, {'np': np, 'pd': pd, 'bodo': bodo}, pfab__qpnkf)
    return pfab__qpnkf['impl']
