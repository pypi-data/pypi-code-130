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
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitand',
                ['A', 'B'], wefu__duv)

    def impl(A, B):
        return bitand_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitleftshift(A, B):
    args = [A, B]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitleftshift', ['A', 'B'],
                wefu__duv)

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
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitor',
                ['A', 'B'], wefu__duv)

    def impl(A, B):
        return bitor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitrightshift(A, B):
    args = [A, B]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitrightshift', ['A', 'B'],
                wefu__duv)

    def impl(A, B):
        return bitrightshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitxor(A, B):
    args = [A, B]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitxor',
                ['A', 'B'], wefu__duv)

    def impl(A, B):
        return bitxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for wefu__duv in range(3):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], wefu__duv)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def getbit(A, B):
    args = [A, B]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.getbit',
                ['A', 'B'], wefu__duv)

    def impl(A, B):
        return getbit_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    args = [lat1, lon1, lat2, lon2]
    for wefu__duv in range(4):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.haversine',
                ['lat1', 'lon1', 'lat2', 'lon2'], wefu__duv)

    def impl(lat1, lon1, lat2, lon2):
        return haversine_util(lat1, lon1, lat2, lon2)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], wefu__duv)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for wefu__duv in range(2):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], wefu__duv)

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
    for wefu__duv in range(4):
        if isinstance(args[wefu__duv], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.width_bucket', ['arr',
                'min_val', 'max_val', 'num_buckets'], wefu__duv)

    def impl(arr, min_val, max_val, num_buckets):
        return width_bucket_util(arr, min_val, max_val, num_buckets)
    return impl


@numba.generated_jit(nopython=True)
def bitand_util(A, B):
    verify_int_arg(A, 'bitand', 'A')
    verify_int_arg(B, 'bitand', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = arg0 & arg1'
    kyer__lvo = get_common_broadcasted_type([A, B], 'bitand')
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def bitleftshift_util(A, B):
    verify_int_arg(A, 'bitleftshift', 'A')
    verify_int_arg(B, 'bitleftshift', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = arg0 << arg1'
    kyer__lvo = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def bitnot_util(A):
    verify_int_arg(A, 'bitnot', 'A')
    hyh__hzok = ['A']
    zctms__figj = [A]
    mtb__vqovy = [True]
    krr__alhn = 'res[i] = ~arg0'
    if A == bodo.none:
        kyer__lvo = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            gyzhc__qdglj = A.dtype
        else:
            gyzhc__qdglj = A
        kyer__lvo = bodo.libs.int_arr_ext.IntegerArrayType(gyzhc__qdglj)
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def bitor_util(A, B):
    verify_int_arg(A, 'bitor', 'A')
    verify_int_arg(B, 'bitor', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = arg0 | arg1'
    kyer__lvo = get_common_broadcasted_type([A, B], 'bitor')
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def bitrightshift_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    if A == bodo.none:
        gyzhc__qdglj = kyer__lvo = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            gyzhc__qdglj = A.dtype
        else:
            gyzhc__qdglj = A
        kyer__lvo = bodo.libs.int_arr_ext.IntegerArrayType(gyzhc__qdglj)
    krr__alhn = f'res[i] = arg0 >> arg1\n'
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def bitxor_util(A, B):
    verify_int_arg(A, 'bitxor', 'A')
    verify_int_arg(B, 'bitxor', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = arg0 ^ arg1'
    kyer__lvo = get_common_broadcasted_type([A, B], 'bitxor')
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    hyh__hzok = ['arr', 'old_base', 'new_base']
    zctms__figj = [arr, old_base, new_base]
    mtb__vqovy = [True] * 3
    krr__alhn = 'old_val = int(arg0, arg1)\n'
    krr__alhn += 'if arg2 == 2:\n'
    krr__alhn += "   res[i] = format(old_val, 'b')\n"
    krr__alhn += 'elif arg2 == 8:\n'
    krr__alhn += "   res[i] = format(old_val, 'o')\n"
    krr__alhn += 'elif arg2 == 10:\n'
    krr__alhn += "   res[i] = format(old_val, 'd')\n"
    krr__alhn += 'elif arg2 == 16:\n'
    krr__alhn += "   res[i] = format(old_val, 'x')\n"
    krr__alhn += 'else:\n'
    krr__alhn += '   bodo.libs.array_kernels.setna(res, i)\n'
    kyer__lvo = bodo.string_array_type
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def getbit_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    hyh__hzok = ['A', 'B']
    zctms__figj = [A, B]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = (arg0 >> arg1) & 1'
    kyer__lvo = bodo.libs.int_arr_ext.IntegerArrayType(types.uint8)
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def haversine_util(lat1, lon1, lat2, lon2):
    verify_int_float_arg(lat1, 'HAVERSINE', 'lat1')
    verify_int_float_arg(lon1, 'HAVERSINE', 'lon1')
    verify_int_float_arg(lat2, 'HAVERSINE', 'lat2')
    verify_int_float_arg(lon2, 'HAVERSINE', 'lon2')
    hyh__hzok = ['lat1', 'lon1', 'lat2', 'lon2']
    zctms__figj = [lat1, lon1, lat2, lon2]
    oindm__nuhno = [True] * 4
    krr__alhn = (
        'arg0, arg1, arg2, arg3 = map(np.radians, (arg0, arg1, arg2, arg3))\n')
    xbkzc__lwg = '(arg2 - arg0) * 0.5'
    joluv__xzrxu = '(arg3 - arg1) * 0.5'
    kjcy__diwt = (
        f'np.square(np.sin({xbkzc__lwg})) + (np.cos(arg0) * np.cos(arg2) * np.square(np.sin({joluv__xzrxu})))'
        )
    krr__alhn += f'res[i] = 12742.0 * np.arcsin(np.sqrt({kjcy__diwt}))\n'
    kyer__lvo = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(hyh__hzok, zctms__figj, oindm__nuhno, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    hyh__hzok = ['arr', 'divisor']
    zctms__figj = [arr, divisor]
    oindm__nuhno = [True] * 2
    krr__alhn = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    kyer__lvo = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(hyh__hzok, zctms__figj, oindm__nuhno, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    hyh__hzok = ['arr', 'base']
    zctms__figj = [arr, base]
    mtb__vqovy = [True] * 2
    krr__alhn = 'res[i] = np.log(arg0) / np.log(arg1)'
    kyer__lvo = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    hyh__hzok = ['arr']
    zctms__figj = [arr]
    mtb__vqovy = [True]
    if arr == bodo.none:
        gyzhc__qdglj = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        gyzhc__qdglj = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        gyzhc__qdglj = arr.data.dtype
    else:
        gyzhc__qdglj = arr
    krr__alhn = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(gyzhc__qdglj, 'res[i] = -arg0')
    gyzhc__qdglj = {types.uint8: types.int16, types.uint16: types.int32,
        types.uint32: types.int64, types.uint64: types.int64}.get(gyzhc__qdglj,
        gyzhc__qdglj)
    kyer__lvo = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(gyzhc__qdglj))
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


@numba.generated_jit(nopython=True)
def width_bucket_util(arr, min_val, max_val, num_buckets):
    verify_int_float_arg(arr, 'WIDTH_BUCKET', 'arr')
    verify_int_float_arg(min_val, 'WIDTH_BUCKET', 'min_val')
    verify_int_float_arg(max_val, 'WIDTH_BUCKET', 'max_val')
    verify_int_arg(num_buckets, 'WIDTH_BUCKET', 'num_buckets')
    hyh__hzok = ['arr', 'min_val', 'max_val', 'num_buckets']
    zctms__figj = [arr, min_val, max_val, num_buckets]
    mtb__vqovy = [True] * 4
    krr__alhn = (
        "if arg1 >= arg2: raise ValueError('min_val must be less than max_val')\n"
        )
    krr__alhn += (
        "if arg3 <= 0: raise ValueError('num_buckets must be a positive integer')\n"
        )
    krr__alhn += (
        'res[i] = min(max(-1.0, math.floor((arg0 - arg1) / ((arg2 - arg1) / arg3))), arg3) + 1.0'
        )
    kyer__lvo = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(hyh__hzok, zctms__figj, mtb__vqovy, krr__alhn,
        kyer__lvo)


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
    vnjh__pvem = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        vnjh__pvem += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        vnjh__pvem += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        vnjh__pvem += '  for arr in arr_tup:\n'
        vnjh__pvem += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        vnjh__pvem += '    obs = obs | next_obs \n'
        vnjh__pvem += '  dense = obs.cumsum()\n'
        if method == 'dense':
            vnjh__pvem += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            vnjh__pvem += '    dense,\n'
            vnjh__pvem += '    new_dtype=np.float64,\n'
            vnjh__pvem += '    copy=True,\n'
            vnjh__pvem += '    nan_to_str=False,\n'
            vnjh__pvem += '    from_series=True,\n'
            vnjh__pvem += '  )\n'
        else:
            vnjh__pvem += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            vnjh__pvem += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                vnjh__pvem += '  ret = count_float[dense]\n'
            elif method == 'min':
                vnjh__pvem += '  ret = count_float[dense - 1] + 1\n'
            else:
                vnjh__pvem += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            vnjh__pvem += '  div_val = np.max(ret)\n'
        else:
            vnjh__pvem += '  div_val = arr.size\n'
        vnjh__pvem += '  for i in range(len(ret)):\n'
        vnjh__pvem += '    ret[i] = ret[i] / div_val\n'
    vnjh__pvem += '  return ret\n'
    xmv__irvf = {}
    exec(vnjh__pvem, {'np': np, 'pd': pd, 'bodo': bodo}, xmv__irvf)
    return xmv__irvf['impl']
