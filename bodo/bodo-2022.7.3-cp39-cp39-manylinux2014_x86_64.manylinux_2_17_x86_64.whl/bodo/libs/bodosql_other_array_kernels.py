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
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.booland',
                ['A', 'B'], jtyv__ejc)

    def impl(A, B):
        return booland_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolor(A, B):
    args = [A, B]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolor',
                ['A', 'B'], jtyv__ejc)

    def impl(A, B):
        return boolor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def boolxor(A, B):
    args = [A, B]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.boolxor',
                ['A', 'B'], jtyv__ejc)

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
    for jtyv__ejc in range(3):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], jtyv__ejc)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def equal_null(A, B):
    args = [A, B]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.equal_null',
                ['A', 'B'], jtyv__ejc)

    def impl(A, B):
        return equal_null_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def booland_util(A, B):
    verify_int_float_arg(A, 'BOOLAND', 'A')
    verify_int_float_arg(B, 'BOOLAND', 'B')
    fmzif__nrw = ['A', 'B']
    hoqpb__gwnru = [A, B]
    abs__urmzq = [False] * 2
    if A == bodo.none:
        abs__urmzq = [False, True]
        rgab__aimek = 'if arg1 != 0:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = False\n'
    elif B == bodo.none:
        abs__urmzq = [True, False]
        rgab__aimek = 'if arg0 != 0:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = False\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rgab__aimek = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += 'else:\n'
            rgab__aimek += '   res[i] = (arg0 != 0) and (arg1 != 0)'
        else:
            rgab__aimek = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += 'else:\n'
            rgab__aimek += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        rgab__aimek = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = (arg0 != 0) and (arg1 != 0)'
    else:
        rgab__aimek = 'res[i] = (arg0 != 0) and (arg1 != 0)'
    bmnmc__uskgh = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def boolor_util(A, B):
    verify_int_float_arg(A, 'BOOLOR', 'A')
    verify_int_float_arg(B, 'BOOLOR', 'B')
    fmzif__nrw = ['A', 'B']
    hoqpb__gwnru = [A, B]
    abs__urmzq = [False] * 2
    if A == bodo.none:
        abs__urmzq = [False, True]
        rgab__aimek = 'if arg1 == 0:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = True\n'
    elif B == bodo.none:
        abs__urmzq = [True, False]
        rgab__aimek = 'if arg0 == 0:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = True\n'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rgab__aimek = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rgab__aimek += '   res[i] = True\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n')
            rgab__aimek += '   res[i] = True\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += 'else:\n'
            rgab__aimek += '   res[i] = (arg0 != 0) or (arg1 != 0)'
        else:
            rgab__aimek = (
                'if bodo.libs.array_kernels.isna(A, i) and arg1 != 0:\n')
            rgab__aimek += '   res[i] = True\n'
            rgab__aimek += (
                'elif bodo.libs.array_kernels.isna(A, i) and arg1 == 0:\n')
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += 'else:\n'
            rgab__aimek += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    elif bodo.utils.utils.is_array_typ(B, True):
        rgab__aimek = 'if bodo.libs.array_kernels.isna(B, i) and arg0 != 0:\n'
        rgab__aimek += '   res[i] = True\n'
        rgab__aimek += (
            'elif bodo.libs.array_kernels.isna(B, i) and arg0 == 0:\n')
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   res[i] = (arg0 != 0) or (arg1 != 0)'
    else:
        rgab__aimek = 'res[i] = (arg0 != 0) or (arg1 != 0)'
    bmnmc__uskgh = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def boolxor_util(A, B):
    verify_int_float_arg(A, 'BOOLXOR', 'A')
    verify_int_float_arg(B, 'BOOLXOR', 'B')
    fmzif__nrw = ['A', 'B']
    hoqpb__gwnru = [A, B]
    abs__urmzq = [True] * 2
    rgab__aimek = 'res[i] = (arg0 == 0) != (arg1 == 0)'
    bmnmc__uskgh = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def boolnot_util(A):
    verify_int_float_arg(A, 'BOOLNOT', 'A')
    fmzif__nrw = ['A']
    hoqpb__gwnru = [A]
    abs__urmzq = [True]
    rgab__aimek = 'res[i] = arg0 == 0'
    bmnmc__uskgh = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], jtyv__ejc)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def regr_valx(y, x):
    args = [y, x]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valx',
                ['y', 'x'], jtyv__ejc)

    def impl(y, x):
        return regr_valx_util(y, x)
    return impl


@numba.generated_jit(nopython=True)
def regr_valy(y, x):
    args = [y, x]
    for jtyv__ejc in range(2):
        if isinstance(args[jtyv__ejc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.regr_valy',
                ['y', 'x'], jtyv__ejc)

    def impl(y, x):
        return regr_valx(x, y)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    fmzif__nrw = ['arr', 'ifbranch', 'elsebranch']
    hoqpb__gwnru = [arr, ifbranch, elsebranch]
    abs__urmzq = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        rgab__aimek = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        rgab__aimek = 'if arg0:\n'
    else:
        rgab__aimek = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            rgab__aimek += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            rgab__aimek += '      bodo.libs.array_kernels.setna(res, i)\n'
            rgab__aimek += '   else:\n'
            rgab__aimek += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            rgab__aimek += '   res[i] = arg1\n'
        rgab__aimek += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        rgab__aimek += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        rgab__aimek += '      bodo.libs.array_kernels.setna(res, i)\n'
        rgab__aimek += '   else:\n'
        rgab__aimek += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        rgab__aimek += '   res[i] = arg2\n'
    bmnmc__uskgh = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def equal_null_util(A, B):
    get_common_broadcasted_type([A, B], 'EQUAL_NULL')
    fmzif__nrw = ['A', 'B']
    hoqpb__gwnru = [A, B]
    abs__urmzq = [False] * 2
    if A == bodo.none:
        if B == bodo.none:
            rgab__aimek = 'res[i] = True'
        elif bodo.utils.utils.is_array_typ(B, True):
            rgab__aimek = 'res[i] = bodo.libs.array_kernels.isna(B, i)'
        else:
            rgab__aimek = 'res[i] = False'
    elif B == bodo.none:
        if bodo.utils.utils.is_array_typ(A, True):
            rgab__aimek = 'res[i] = bodo.libs.array_kernels.isna(A, i)'
        else:
            rgab__aimek = 'res[i] = False'
    elif bodo.utils.utils.is_array_typ(A, True):
        if bodo.utils.utils.is_array_typ(B, True):
            rgab__aimek = """if bodo.libs.array_kernels.isna(A, i) and bodo.libs.array_kernels.isna(B, i):
"""
            rgab__aimek += '   res[i] = True\n'
            rgab__aimek += """elif bodo.libs.array_kernels.isna(A, i) or bodo.libs.array_kernels.isna(B, i):
"""
            rgab__aimek += '   res[i] = False\n'
            rgab__aimek += 'else:\n'
            rgab__aimek += '   res[i] = arg0 == arg1'
        else:
            rgab__aimek = (
                'res[i] = (not bodo.libs.array_kernels.isna(A, i)) and arg0 == arg1'
                )
    elif bodo.utils.utils.is_array_typ(B, True):
        rgab__aimek = (
            'res[i] = (not bodo.libs.array_kernels.isna(B, i)) and arg0 == arg1'
            )
    else:
        rgab__aimek = 'res[i] = arg0 == arg1'
    bmnmc__uskgh = bodo.libs.bool_arr_ext.boolean_array
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    fmzif__nrw = ['arr0', 'arr1']
    hoqpb__gwnru = [arr0, arr1]
    abs__urmzq = [True, False]
    if arr1 == bodo.none:
        rgab__aimek = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        rgab__aimek = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        rgab__aimek += '   res[i] = arg0\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        rgab__aimek = 'if arg0 != arg1:\n'
        rgab__aimek += '   res[i] = arg0\n'
        rgab__aimek += 'else:\n'
        rgab__aimek += '   bodo.libs.array_kernels.setna(res, i)'
    bmnmc__uskgh = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, abs__urmzq, rgab__aimek,
        bmnmc__uskgh)


@numba.generated_jit(nopython=True)
def regr_valx_util(y, x):
    verify_int_float_arg(y, 'regr_valx', 'y')
    verify_int_float_arg(x, 'regr_valx', 'x')
    fmzif__nrw = ['y', 'x']
    hoqpb__gwnru = [y, x]
    lpl__qcz = [True] * 2
    rgab__aimek = 'res[i] = arg1'
    bmnmc__uskgh = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(fmzif__nrw, hoqpb__gwnru, lpl__qcz, rgab__aimek,
        bmnmc__uskgh)
