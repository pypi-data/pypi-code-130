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
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitand',
                ['A', 'B'], btg__ggjnr)

    def impl(A, B):
        return bitand_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitleftshift(A, B):
    args = [A, B]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitleftshift', ['A', 'B'],
                btg__ggjnr)

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
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitor',
                ['A', 'B'], btg__ggjnr)

    def impl(A, B):
        return bitor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitrightshift(A, B):
    args = [A, B]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitrightshift', ['A', 'B'],
                btg__ggjnr)

    def impl(A, B):
        return bitrightshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitxor(A, B):
    args = [A, B]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitxor',
                ['A', 'B'], btg__ggjnr)

    def impl(A, B):
        return bitxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for btg__ggjnr in range(3):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], btg__ggjnr)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def getbit(A, B):
    args = [A, B]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.getbit',
                ['A', 'B'], btg__ggjnr)

    def impl(A, B):
        return getbit_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    args = [lat1, lon1, lat2, lon2]
    for btg__ggjnr in range(4):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.haversine',
                ['lat1', 'lon1', 'lat2', 'lon2'], btg__ggjnr)

    def impl(lat1, lon1, lat2, lon2):
        return haversine_util(lat1, lon1, lat2, lon2)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], btg__ggjnr)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for btg__ggjnr in range(2):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], btg__ggjnr)

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
def width_bucket(arr, min_val, max_val, num_buckets):
    args = [arr, min_val, max_val, num_buckets]
    for btg__ggjnr in range(4):
        if isinstance(args[btg__ggjnr], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.width_bucket', ['arr',
                'min_val', 'max_val', 'num_buckets'], btg__ggjnr)

    def impl(arr, min_val, max_val, num_buckets):
        return width_bucket_util(arr, min_val, max_val, num_buckets)
    return impl


@numba.generated_jit(nopython=True)
def bitand_util(A, B):
    verify_int_arg(A, 'bitand', 'A')
    verify_int_arg(B, 'bitand', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = arg0 & arg1'
    kabd__ncti = get_common_broadcasted_type([A, B], 'bitand')
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def bitleftshift_util(A, B):
    verify_int_arg(A, 'bitleftshift', 'A')
    verify_int_arg(B, 'bitleftshift', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = arg0 << arg1'
    kabd__ncti = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def bitnot_util(A):
    verify_int_arg(A, 'bitnot', 'A')
    owk__rdq = ['A']
    fore__lsyq = [A]
    dvp__yvg = [True]
    olcn__wxv = 'res[i] = ~arg0'
    if A == bodo.none:
        kabd__ncti = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            hblo__tirsv = A.dtype
        else:
            hblo__tirsv = A
        kabd__ncti = bodo.libs.int_arr_ext.IntegerArrayType(hblo__tirsv)
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def bitor_util(A, B):
    verify_int_arg(A, 'bitor', 'A')
    verify_int_arg(B, 'bitor', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = arg0 | arg1'
    kabd__ncti = get_common_broadcasted_type([A, B], 'bitor')
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def bitrightshift_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    if A == bodo.none:
        hblo__tirsv = kabd__ncti = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            hblo__tirsv = A.dtype
        else:
            hblo__tirsv = A
        kabd__ncti = bodo.libs.int_arr_ext.IntegerArrayType(hblo__tirsv)
    olcn__wxv = f'res[i] = arg0 >> arg1\n'
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def bitxor_util(A, B):
    verify_int_arg(A, 'bitxor', 'A')
    verify_int_arg(B, 'bitxor', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = arg0 ^ arg1'
    kabd__ncti = get_common_broadcasted_type([A, B], 'bitxor')
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    owk__rdq = ['arr', 'old_base', 'new_base']
    fore__lsyq = [arr, old_base, new_base]
    dvp__yvg = [True] * 3
    olcn__wxv = 'old_val = int(arg0, arg1)\n'
    olcn__wxv += 'if arg2 == 2:\n'
    olcn__wxv += "   res[i] = format(old_val, 'b')\n"
    olcn__wxv += 'elif arg2 == 8:\n'
    olcn__wxv += "   res[i] = format(old_val, 'o')\n"
    olcn__wxv += 'elif arg2 == 10:\n'
    olcn__wxv += "   res[i] = format(old_val, 'd')\n"
    olcn__wxv += 'elif arg2 == 16:\n'
    olcn__wxv += "   res[i] = format(old_val, 'x')\n"
    olcn__wxv += 'else:\n'
    olcn__wxv += '   bodo.libs.array_kernels.setna(res, i)\n'
    kabd__ncti = bodo.string_array_type
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def getbit_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    owk__rdq = ['A', 'B']
    fore__lsyq = [A, B]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = (arg0 >> arg1) & 1'
    kabd__ncti = bodo.libs.int_arr_ext.IntegerArrayType(types.uint8)
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def haversine_util(lat1, lon1, lat2, lon2):
    verify_int_float_arg(lat1, 'HAVERSINE', 'lat1')
    verify_int_float_arg(lon1, 'HAVERSINE', 'lon1')
    verify_int_float_arg(lat2, 'HAVERSINE', 'lat2')
    verify_int_float_arg(lon2, 'HAVERSINE', 'lon2')
    owk__rdq = ['lat1', 'lon1', 'lat2', 'lon2']
    fore__lsyq = [lat1, lon1, lat2, lon2]
    wquhw__yocjt = [True] * 4
    olcn__wxv = (
        'arg0, arg1, arg2, arg3 = map(np.radians, (arg0, arg1, arg2, arg3))\n')
    qvk__jyjp = '(arg2 - arg0) * 0.5'
    wpfob__vyfjk = '(arg3 - arg1) * 0.5'
    uuyh__zdc = (
        f'np.square(np.sin({qvk__jyjp})) + (np.cos(arg0) * np.cos(arg2) * np.square(np.sin({wpfob__vyfjk})))'
        )
    olcn__wxv += f'res[i] = 12742.0 * np.arcsin(np.sqrt({uuyh__zdc}))\n'
    kabd__ncti = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(owk__rdq, fore__lsyq, wquhw__yocjt, olcn__wxv,
        kabd__ncti)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    owk__rdq = ['arr', 'divisor']
    fore__lsyq = [arr, divisor]
    wquhw__yocjt = [True] * 2
    olcn__wxv = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    kabd__ncti = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(owk__rdq, fore__lsyq, wquhw__yocjt, olcn__wxv,
        kabd__ncti)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    owk__rdq = ['arr', 'base']
    fore__lsyq = [arr, base]
    dvp__yvg = [True] * 2
    olcn__wxv = 'res[i] = np.log(arg0) / np.log(arg1)'
    kabd__ncti = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    owk__rdq = ['arr']
    fore__lsyq = [arr]
    dvp__yvg = [True]
    if arr == bodo.none:
        hblo__tirsv = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        hblo__tirsv = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        hblo__tirsv = arr.data.dtype
    else:
        hblo__tirsv = arr
    olcn__wxv = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(hblo__tirsv, 'res[i] = -arg0')
    hblo__tirsv = {types.uint8: types.int16, types.uint16: types.int32,
        types.uint32: types.int64, types.uint64: types.int64}.get(hblo__tirsv,
        hblo__tirsv)
    kabd__ncti = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(hblo__tirsv))
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


@numba.generated_jit(nopython=True)
def width_bucket_util(arr, min_val, max_val, num_buckets):
    verify_int_float_arg(arr, 'WIDTH_BUCKET', 'arr')
    verify_int_float_arg(min_val, 'WIDTH_BUCKET', 'min_val')
    verify_int_float_arg(max_val, 'WIDTH_BUCKET', 'max_val')
    verify_int_arg(num_buckets, 'WIDTH_BUCKET', 'num_buckets')
    owk__rdq = ['arr', 'min_val', 'max_val', 'num_buckets']
    fore__lsyq = [arr, min_val, max_val, num_buckets]
    dvp__yvg = [True] * 4
    olcn__wxv = (
        "if arg1 >= arg2: raise ValueError('min_val must be less than max_val')\n"
        )
    olcn__wxv += (
        "if arg3 <= 0: raise ValueError('num_buckets must be a positive integer')\n"
        )
    olcn__wxv += (
        'res[i] = min(max(-1.0, math.floor((arg0 - arg1) / ((arg2 - arg1) / arg3))), arg3) + 1.0'
        )
    kabd__ncti = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(owk__rdq, fore__lsyq, dvp__yvg, olcn__wxv, kabd__ncti
        )


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
    ehj__gmg = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        ehj__gmg += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        ehj__gmg += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        ehj__gmg += '  for arr in arr_tup:\n'
        ehj__gmg += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        ehj__gmg += '    obs = obs | next_obs \n'
        ehj__gmg += '  dense = obs.cumsum()\n'
        if method == 'dense':
            ehj__gmg += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            ehj__gmg += '    dense,\n'
            ehj__gmg += '    new_dtype=np.float64,\n'
            ehj__gmg += '    copy=True,\n'
            ehj__gmg += '    nan_to_str=False,\n'
            ehj__gmg += '    from_series=True,\n'
            ehj__gmg += '  )\n'
        else:
            ehj__gmg += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            ehj__gmg += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                ehj__gmg += '  ret = count_float[dense]\n'
            elif method == 'min':
                ehj__gmg += '  ret = count_float[dense - 1] + 1\n'
            else:
                ehj__gmg += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            ehj__gmg += '  div_val = np.max(ret)\n'
        else:
            ehj__gmg += '  div_val = arr.size\n'
        ehj__gmg += '  for i in range(len(ret)):\n'
        ehj__gmg += '    ret[i] = ret[i] / div_val\n'
    ehj__gmg += '  return ret\n'
    bhxnc__zgt = {}
    exec(ehj__gmg, {'np': np, 'pd': pd, 'bodo': bodo}, bhxnc__zgt)
    return bhxnc__zgt['impl']
