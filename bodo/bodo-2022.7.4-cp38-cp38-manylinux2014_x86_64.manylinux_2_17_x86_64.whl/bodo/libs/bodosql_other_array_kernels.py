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
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.booland',
                ['A', 'B'], hnb__qjun)

    def impl(A, B):
        return booland_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolor(A, B):
    args = [A, B]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolor',
                ['A', 'B'], hnb__qjun)

    def impl(A, B):
        return boolor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolxor(A, B):
    args = [A, B]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolxor',
                ['A', 'B'], hnb__qjun)

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
    for hnb__qjun in range(3):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], hnb__qjun)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def equal_null(A, B):
    args = [A, B]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.equal_null',
                ['A', 'B'], hnb__qjun)

    def impl(A, B):
        return equal_null_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def booland_util(A, B):
    verify_int_float_arg(A, 'BOOLAND', 'A')
    verify_int_float_arg(B, 'BOOLAND', 'B')
    psn__zti = ['A', 'B']
    osn__cdvwl = [A, B]
    rlt__sbl = [False] * 2
    if A == bodo.none:
        rlt__sbl = [False, True]
        mtwpu__cdt = 'if arg1 != 0:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = False\n'
    elif B == bodo.none:
        rlt__sbl = [True, False]
        mtwpu__cdt = 'if arg0 != 0:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = False\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            mtwpu__cdt = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += 'else:\n'
            mtwpu__cdt += '   res[i] = (arg0 != 0) and (arg1 != 0)'
        else:
            mtwpu__cdt = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += 'else:\n'
            mtwpu__cdt += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        mtwpu__cdt = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    else:
        mtwpu__cdt = 'res[i] = (arg0 != 0) and (arg1 != 0)'
    ssw__rcqro = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def boolor_util(A, B):
    verify_int_float_arg(A, 'BOOLOR', 'A')
    verify_int_float_arg(B, 'BOOLOR', 'B')
    psn__zti = ['A', 'B']
    osn__cdvwl = [A, B]
    rlt__sbl = [False] * 2
    if A == bodo.none:
        rlt__sbl = [False, True]
        mtwpu__cdt = 'if arg1 == 0:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = True\n'
    elif B == bodo.none:
        rlt__sbl = [True, False]
        mtwpu__cdt = 'if arg0 == 0:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = True\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            mtwpu__cdt = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            mtwpu__cdt += '   res[i] = True\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            mtwpu__cdt += '   res[i] = True\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += 'else:\n'
            mtwpu__cdt += '   res[i] = (arg0 != 0) or (arg1 != 0)'
        else:
            mtwpu__cdt = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            mtwpu__cdt += '   res[i] = True\n'
            mtwpu__cdt += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += 'else:\n'
            mtwpu__cdt += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        mtwpu__cdt = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        mtwpu__cdt += '   res[i] = True\n'
        mtwpu__cdt += (
            'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    else:
        mtwpu__cdt = 'res[i] = (arg0 != 0) or (arg1 != 0)'
    ssw__rcqro = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def boolxor_util(A, B):
    verify_int_float_arg(A, 'BOOLXOR', 'A')
    verify_int_float_arg(B, 'BOOLXOR', 'B')
    psn__zti = ['A', 'B']
    osn__cdvwl = [A, B]
    rlt__sbl = [True] * 2
    mtwpu__cdt = 'res[i] = (arg0 == 0) != (arg1 == 0)'
    ssw__rcqro = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def boolnot_util(A):
    verify_int_float_arg(A, 'BOOLNOT', 'A')
    psn__zti = ['A']
    osn__cdvwl = [A]
    rlt__sbl = [True]
    mtwpu__cdt = 'res[i] = arg0 == 0'
    ssw__rcqro = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], hnb__qjun)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def regr_valx(y, x):
    args = [y, x]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valx',
                ['y', 'x'], hnb__qjun)

    def impl(y, x):
        return regr_valx_util(y, x)
    return impl


@numba.generated_jit(nopython=True)
def regr_valy(y, x):
    args = [y, x]
    for hnb__qjun in range(2):
        if isinstance(args[hnb__qjun], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valy',
                ['y', 'x'], hnb__qjun)

    def impl(y, x):
        return regr_valx(x, y)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    psn__zti = ['arr', 'ifbranch', 'elsebranch']
    osn__cdvwl = [arr, ifbranch, elsebranch]
    rlt__sbl = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        mtwpu__cdt = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        mtwpu__cdt = 'if arg0:\n'
    else:
        mtwpu__cdt = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            mtwpu__cdt += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            mtwpu__cdt += '      bodo.libs.array_kernels.setna(res, i)\n'
            mtwpu__cdt += '   else:\n'
            mtwpu__cdt += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            mtwpu__cdt += '   res[i] = arg1\n'
        mtwpu__cdt += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        mtwpu__cdt += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        mtwpu__cdt += '      bodo.libs.array_kernels.setna(res, i)\n'
        mtwpu__cdt += '   else:\n'
        mtwpu__cdt += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        mtwpu__cdt += '   res[i] = arg2\n'
    ssw__rcqro = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def equal_null_util(A, B):
    get_common_broadcasted_type([A, B], 'EQUAL_NULL')
    psn__zti = ['A', 'B']
    osn__cdvwl = [A, B]
    rlt__sbl = [False] * 2
    if A == bodo.none:
        if B == bodo.none:
            mtwpu__cdt = 'res[i] = True'
        elif bodo.utils.utils.is_array_typ(B, True):
            mtwpu__cdt = 'res[i] = bodo.libs.array_kernels.isna(B, i)'
        else:
            mtwpu__cdt = 'res[i] = False'
    elif B == bodo.none:
        if bodo.utils.utils.is_array_typ(A, True):
            mtwpu__cdt = 'res[i] = bodo.libs.array_kernels.isna(A, i)'
        else:
            mtwpu__cdt = 'res[i] = False'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            mtwpu__cdt = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            mtwpu__cdt += '   res[i] = True\n'
            mtwpu__cdt += """elif bodo.libs.array_kernels.isna(A, i) or bodo.libs.array_kernels.isna(B, i):
"""
            mtwpu__cdt += '   res[i] = False\n'
            mtwpu__cdt += 'else:\n'
            mtwpu__cdt += '   res[i] = arg0 == arg1'
        else:
            mtwpu__cdt = (
                'res[i] = (not bodo.libs.array_kernels.isna(A, i)) and arg0 == arg1'
                )
    elif bodo.utils.utils.is_array_typ(B, True):
        mtwpu__cdt = (
            'res[i] = (not bodo.libs.array_kernels.isna(B, i)) and arg0 == arg1'
            )
    else:
        mtwpu__cdt = 'res[i] = arg0 == arg1'
    ssw__rcqro = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    psn__zti = ['arr0', 'arr1']
    osn__cdvwl = [arr0, arr1]
    rlt__sbl = [True, False]
    if arr1 == bodo.none:
        mtwpu__cdt = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        mtwpu__cdt = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        mtwpu__cdt += '   res[i] = arg0\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        mtwpu__cdt = 'if arg0 != arg1:\n'
        mtwpu__cdt += '   res[i] = arg0\n'
        mtwpu__cdt += 'else:\n'
        mtwpu__cdt += '   bodo.libs.array_kernels.setna(res, i)'
    ssw__rcqro = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(psn__zti, osn__cdvwl, rlt__sbl, mtwpu__cdt,
        ssw__rcqro)


@numba.generated_jit(nopython=True)
def regr_valx_util(y, x):
    verify_int_float_arg(y, 'regr_valx', 'y')
    verify_int_float_arg(x, 'regr_valx', 'x')
    psn__zti = ['y', 'x']
    osn__cdvwl = [y, x]
    uwo__nhcjr = [True] * 2
    mtwpu__cdt = 'res[i] = arg1'
    ssw__rcqro = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(psn__zti, osn__cdvwl, uwo__nhcjr, mtwpu__cdt,
        ssw__rcqro)
