from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.bodosql_array_kernel_utils import *


def acos(arr):
    return


def acosh(arr):
    return


def asin(arr):
    return


def asinh(arr):
    return


def atan(arr):
    return


def atanh(arr):
    return


def atan2(arr0, arr1):
    return


def cos(arr):
    return


def cosh(arr):
    return


def sin(arr):
    return


def sinh(arr):
    return


def tan(arr):
    return


def tanh(arr):
    return


def radians(arr):
    return


def degrees(arr):
    return


def acos_util(arr):
    return


def acosh_util(arr):
    return


def asin_util(arr):
    return


def asinh_util(arr):
    return


def atan_util(arr):
    return


def atanh_util(arr):
    return


def atan2_util(arr0, arr1):
    return


def cos_util(arr):
    return


def cosh_util(arr):
    return


def sin_util(arr):
    return


def sinh_util(arr):
    return


def tan_util(arr):
    return


def tanh_util(arr):
    return


def radians_util(arr):
    return


def degrees_util(arr):
    return


funcs_utils_names = (acos, acos_util, 'ACOS'), (acosh, acosh_util, 'ACOSH'), (
    asin, asin_util, 'ASIN'), (asinh, asinh_util, 'ASINH'), (atan,
    atan_util, 'ATAN'), (atanh, atanh_util, 'ATANH'), (atan2, atan2_util,
    'ATAN2'), (cos, cos_util, 'COS'), (cosh, cosh_util, 'COSH'), (sin,
    sin_util, 'SIN'), (sinh, sinh_util, 'SINH'), (tan, tan_util, 'TAN'), (tanh,
    tanh_util, 'TANH'), (radians, radians_util, 'RADIANS'), (degrees,
    degrees_util, 'DEGREES')
double_arg_funcs = 'ATAN2',


def create_trig_func_overload(func_name):
    if func_name not in double_arg_funcs:
        func_name = func_name.lower()

        def overload_func(arr):
            if isinstance(arr, types.optional):
                return unopt_argument(
                    f'bodo.libs.bodosql_array_kernels.{func_name}', ['arr'], 0)
            syv__wqsb = 'def impl(arr):\n'
            syv__wqsb += (
                f'  return bodo.libs.bodosql_array_kernels.{func_name}_util(arr)'
                )
            edq__vhcvy = {}
            exec(syv__wqsb, {'bodo': bodo}, edq__vhcvy)
            return edq__vhcvy['impl']
    else:
        func_name = func_name.lower()

        def overload_func(arr0, arr1):
            args = [arr0, arr1]
            for xjqvj__vswn in range(2):
                if isinstance(args[xjqvj__vswn], types.optional):
                    return unopt_argument(
                        f'bodo.libs.bodosql_array_kernels.{func_name}', [
                        'arr0', 'arr1'], xjqvj__vswn)
            syv__wqsb = 'def impl(arr0, arr1):\n'
            syv__wqsb += (
                f'  return bodo.libs.bodosql_array_kernels.{func_name}_util(arr0, arr1)'
                )
            edq__vhcvy = {}
            exec(syv__wqsb, {'bodo': bodo}, edq__vhcvy)
            return edq__vhcvy['impl']
    return overload_func


def create_trig_util_overload(func_name):
    if func_name not in double_arg_funcs:

        def overload_trig_util(arr):
            verify_int_float_arg(arr, func_name, 'arr')
            wcmw__hew = ['arr']
            nrbk__ykxo = [arr]
            obxoz__apjt = [True]
            bwxzr__bwyb = ''
            if func_name == 'ACOS':
                bwxzr__bwyb += 'res[i] = np.arccos(arg0)'
            elif func_name == 'ACOSH':
                bwxzr__bwyb += 'res[i] = np.arccosh(arg0)'
            elif func_name == 'ASIN':
                bwxzr__bwyb += 'res[i] = np.arcsin(arg0)'
            elif func_name == 'ASINH':
                bwxzr__bwyb += 'res[i] = np.arcsinh(arg0)'
            elif func_name == 'ATAN':
                bwxzr__bwyb += 'res[i] = np.arctan(arg0)'
            elif func_name == 'ATANH':
                bwxzr__bwyb += 'res[i] = np.arctanh(arg0)'
            elif func_name == 'COS':
                bwxzr__bwyb += 'res[i] = np.cos(arg0)'
            elif func_name == 'COSH':
                bwxzr__bwyb += 'res[i] = np.cosh(arg0)'
            elif func_name == 'SIN':
                bwxzr__bwyb += 'res[i] = np.sin(arg0)'
            elif func_name == 'SINH':
                bwxzr__bwyb += 'res[i] = np.sinh(arg0)'
            elif func_name == 'TAN':
                bwxzr__bwyb += 'res[i] = np.tan(arg0)'
            elif func_name == 'TANH':
                bwxzr__bwyb += 'res[i] = np.tanh(arg0)'
            elif func_name == 'RADIANS':
                bwxzr__bwyb += 'res[i] = np.radians(arg0)'
            elif func_name == 'DEGREES':
                bwxzr__bwyb += 'res[i] = np.degrees(arg0)'
            else:
                raise ValueError(f'Unknown function name: {func_name}')
            gsf__vqjjl = types.Array(bodo.float64, 1, 'C')
            return gen_vectorized(wcmw__hew, nrbk__ykxo, obxoz__apjt,
                bwxzr__bwyb, gsf__vqjjl)
    else:

        def overload_trig_util(arr0, arr1):
            verify_int_float_arg(arr0, func_name, 'arr0')
            verify_int_float_arg(arr1, func_name, 'arr1')
            wcmw__hew = ['arr0', 'arr1']
            nrbk__ykxo = [arr0, arr1]
            obxoz__apjt = [True, True]
            bwxzr__bwyb = ''
            if func_name == 'ATAN2':
                bwxzr__bwyb += 'res[i] = np.arctan2(arg0, arg1)\n'
            else:
                raise ValueError(f'Unknown function name: {func_name}')
            gsf__vqjjl = types.Array(bodo.float64, 1, 'C')
            return gen_vectorized(wcmw__hew, nrbk__ykxo, obxoz__apjt,
                bwxzr__bwyb, gsf__vqjjl)
    return overload_trig_util


def _install_trig_overload(funcs_utils_names):
    for unj__iyc, ovmz__ydwfi, func_name in funcs_utils_names:
        tre__lagrj = create_trig_func_overload(func_name)
        overload(unj__iyc)(tre__lagrj)
        cwtpc__gvmrw = create_trig_util_overload(func_name)
        overload(ovmz__ydwfi)(cwtpc__gvmrw)


_install_trig_overload(funcs_utils_names)
