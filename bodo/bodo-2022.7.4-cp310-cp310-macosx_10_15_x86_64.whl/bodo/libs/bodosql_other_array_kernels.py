"""
Implements miscellaneous array kernels that are specific to BodoSQL
"""
import numba
from numba.core import types
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import raise_bodo_error


@numba.generated_jit(nopython=True)
def booland(A, B):
    args = [A, B]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.booland',
                ['A', 'B'], sdld__xevj)

    def impl(A, B):
        return booland_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolor(A, B):
    args = [A, B]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolor',
                ['A', 'B'], sdld__xevj)

    def impl(A, B):
        return boolor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolxor(A, B):
    args = [A, B]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolxor',
                ['A', 'B'], sdld__xevj)

    def impl(A, B):
        return boolxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolnot(A):
    if isinstance(A, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.boolnot_util',
            ['A'], 0)

    def impl(A):
        return boolnot_util(A)
    return impl


@numba.generated_jit(nopython=True)
def cond(arr, ifbranch, elsebranch):
    args = [arr, ifbranch, elsebranch]
    for sdld__xevj in range(3):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], sdld__xevj)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def equal_null(A, B):
    args = [A, B]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.equal_null',
                ['A', 'B'], sdld__xevj)

    def impl(A, B):
        return equal_null_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def booland_util(A, B):
    verify_int_float_arg(A, 'BOOLAND', 'A')
    verify_int_float_arg(B, 'BOOLAND', 'B')
    vwu__sbf = ['A', 'B']
    aaxn__dwawb = [A, B]
    jky__hpqs = [False] * 2
    if A == bodo.none:
        jky__hpqs = [False, True]
        nvyoa__xwg = 'if arg1 != 0:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = False\n'
    elif B == bodo.none:
        jky__hpqs = [True, False]
        nvyoa__xwg = 'if arg0 != 0:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = False\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            nvyoa__xwg = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += 'else:\n'
            nvyoa__xwg += '   res[i] = (arg0 != 0) and (arg1 != 0)'
        else:
            nvyoa__xwg = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += 'else:\n'
            nvyoa__xwg += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        nvyoa__xwg = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    else:
        nvyoa__xwg = 'res[i] = (arg0 != 0) and (arg1 != 0)'
    mkun__hhb = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def boolor_util(A, B):
    verify_int_float_arg(A, 'BOOLOR', 'A')
    verify_int_float_arg(B, 'BOOLOR', 'B')
    vwu__sbf = ['A', 'B']
    aaxn__dwawb = [A, B]
    jky__hpqs = [False] * 2
    if A == bodo.none:
        jky__hpqs = [False, True]
        nvyoa__xwg = 'if arg1 == 0:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = True\n'
    elif B == bodo.none:
        jky__hpqs = [True, False]
        nvyoa__xwg = 'if arg0 == 0:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = True\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            nvyoa__xwg = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            nvyoa__xwg += '   res[i] = True\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            nvyoa__xwg += '   res[i] = True\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += 'else:\n'
            nvyoa__xwg += '   res[i] = (arg0 != 0) or (arg1 != 0)'
        else:
            nvyoa__xwg = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            nvyoa__xwg += '   res[i] = True\n'
            nvyoa__xwg += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += 'else:\n'
            nvyoa__xwg += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        nvyoa__xwg = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        nvyoa__xwg += '   res[i] = True\n'
        nvyoa__xwg += (
            'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    else:
        nvyoa__xwg = 'res[i] = (arg0 != 0) or (arg1 != 0)'
    mkun__hhb = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def boolxor_util(A, B):
    verify_int_float_arg(A, 'BOOLXOR', 'A')
    verify_int_float_arg(B, 'BOOLXOR', 'B')
    vwu__sbf = ['A', 'B']
    aaxn__dwawb = [A, B]
    jky__hpqs = [True] * 2
    nvyoa__xwg = 'res[i] = (arg0 == 0) != (arg1 == 0)'
    mkun__hhb = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def boolnot_util(A):
    verify_int_float_arg(A, 'BOOLNOT', 'A')
    vwu__sbf = ['A']
    aaxn__dwawb = [A]
    jky__hpqs = [True]
    nvyoa__xwg = 'res[i] = arg0 == 0'
    mkun__hhb = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], sdld__xevj)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def regr_valx(y, x):
    args = [y, x]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valx',
                ['y', 'x'], sdld__xevj)

    def impl(y, x):
        return regr_valx_util(y, x)
    return impl


@numba.generated_jit(nopython=True)
def regr_valy(y, x):
    args = [y, x]
    for sdld__xevj in range(2):
        if isinstance(args[sdld__xevj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valy',
                ['y', 'x'], sdld__xevj)

    def impl(y, x):
        return regr_valx(x, y)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    vwu__sbf = ['arr', 'ifbranch', 'elsebranch']
    aaxn__dwawb = [arr, ifbranch, elsebranch]
    jky__hpqs = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        nvyoa__xwg = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        nvyoa__xwg = 'if arg0:\n'
    else:
        nvyoa__xwg = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            nvyoa__xwg += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            nvyoa__xwg += '      bodo.libs.array_kernels.setna(res, i)\n'
            nvyoa__xwg += '   else:\n'
            nvyoa__xwg += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            nvyoa__xwg += '   res[i] = arg1\n'
        nvyoa__xwg += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        nvyoa__xwg += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        nvyoa__xwg += '      bodo.libs.array_kernels.setna(res, i)\n'
        nvyoa__xwg += '   else:\n'
        nvyoa__xwg += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        nvyoa__xwg += '   res[i] = arg2\n'
    mkun__hhb = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def equal_null_util(A, B):
    get_common_broadcasted_type([A, B], 'EQUAL_NULL')
    vwu__sbf = ['A', 'B']
    aaxn__dwawb = [A, B]
    jky__hpqs = [False] * 2
    if A == bodo.none:
        if B == bodo.none:
            nvyoa__xwg = 'res[i] = True'
        elif bodo.utils.utils.is_array_typ(B, True):
            nvyoa__xwg = 'res[i] = bodo.libs.array_kernels.isna(B, i)'
        else:
            nvyoa__xwg = 'res[i] = False'
    elif B == bodo.none:
        if bodo.utils.utils.is_array_typ(A, True):
            nvyoa__xwg = 'res[i] = bodo.libs.array_kernels.isna(A, i)'
        else:
            nvyoa__xwg = 'res[i] = False'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            nvyoa__xwg = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            nvyoa__xwg += '   res[i] = True\n'
            nvyoa__xwg += """elif bodo.libs.array_kernels.isna(A, i) or bodo.libs.array_kernels.isna(B, i):
"""
            nvyoa__xwg += '   res[i] = False\n'
            nvyoa__xwg += 'else:\n'
            nvyoa__xwg += '   res[i] = arg0 == arg1'
        else:
            nvyoa__xwg = (
                'res[i] = (not bodo.libs.array_kernels.isna(A, i)) and arg0 == arg1'
                )
    elif bodo.utils.utils.is_array_typ(B, True):
        nvyoa__xwg = (
            'res[i] = (not bodo.libs.array_kernels.isna(B, i)) and arg0 == arg1'
            )
    else:
        nvyoa__xwg = 'res[i] = arg0 == arg1'
    mkun__hhb = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    vwu__sbf = ['arr0', 'arr1']
    aaxn__dwawb = [arr0, arr1]
    jky__hpqs = [True, False]
    if arr1 == bodo.none:
        nvyoa__xwg = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        nvyoa__xwg = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        nvyoa__xwg += '   res[i] = arg0\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        nvyoa__xwg = 'if arg0 != arg1:\n'
        nvyoa__xwg += '   res[i] = arg0\n'
        nvyoa__xwg += 'else:\n'
        nvyoa__xwg += '   bodo.libs.array_kernels.setna(res, i)'
    mkun__hhb = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(vwu__sbf, aaxn__dwawb, jky__hpqs, nvyoa__xwg,
        mkun__hhb)


@numba.generated_jit(nopython=True)
def regr_valx_util(y, x):
    verify_int_float_arg(y, 'regr_valx', 'y')
    verify_int_float_arg(x, 'regr_valx', 'x')
    vwu__sbf = ['y', 'x']
    aaxn__dwawb = [y, x]
    onfj__bel = [True] * 2
    nvyoa__xwg = 'res[i] = arg1'
    mkun__hhb = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(vwu__sbf, aaxn__dwawb, onfj__bel, nvyoa__xwg,
        mkun__hhb)
