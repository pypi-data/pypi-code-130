"""
Implements string array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
from numba.core import types
from numba.extending import overload, register_jitable
import bodo
from bodo.libs.bodosql_array_kernel_utils import *


@numba.generated_jit(nopython=True)
def char(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.char_util',
            ['arr'], 0)

    def impl(arr):
        return char_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_no_max(s, t):
    args = [s, t]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_no_max', ['s',
                't'], djl__dvjs)

    def impl(s, t):
        return editdistance_no_max_util(s, t)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_with_max(s, t, maxDistance):
    args = [s, t, maxDistance]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_with_max', [
                's', 't', 'maxDistance'], djl__dvjs)

    def impl(s, t, maxDistance):
        return editdistance_with_max_util(s, t, maxDistance)
    return impl


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], djl__dvjs)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def initcap(arr, delim):
    args = [arr, delim]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.initcap',
                ['arr', 'delim'], djl__dvjs)

    def impl(arr, delim):
        return initcap_util(arr, delim)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], djl__dvjs)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], djl__dvjs)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], djl__dvjs)

    def impl(arr, length, padstr):
        return lpad_util(arr, length, padstr)
    return impl


@numba.generated_jit(nopython=True)
def ord_ascii(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.ord_ascii_util',
            ['arr'], 0)

    def impl(arr):
        return ord_ascii_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def repeat(arr, repeats):
    args = [arr, repeats]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], djl__dvjs)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], djl__dvjs)

    def impl(arr, to_replace, replace_with):
        return replace_util(arr, to_replace, replace_with)
    return impl


@numba.generated_jit(nopython=True)
def reverse(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.reverse_util',
            ['arr'], 0)

    def impl(arr):
        return reverse_util(arr)
    return impl


def right(arr, n_chars):
    return


@overload(right)
def overload_right(arr, n_chars):
    args = [arr, n_chars]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], djl__dvjs)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], djl__dvjs)

    def impl(arr, length, padstr):
        return rpad_util(arr, length, padstr)
    return impl


@numba.generated_jit(nopython=True)
def space(n_chars):
    if isinstance(n_chars, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.space_util',
            ['n_chars'], 0)

    def impl(n_chars):
        return space_util(n_chars)
    return impl


@numba.generated_jit(nopython=True)
def split_part(source, delim, part):
    args = [source, delim, part]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.split_part',
                ['source', 'delim', 'part'], djl__dvjs)

    def impl(source, delim, part):
        return split_part_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def strcmp(arr0, arr1):
    args = [arr0, arr1]
    for djl__dvjs in range(2):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], djl__dvjs)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def strtok(source, delim, part):
    args = [source, delim, part]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strtok',
                ['source', 'delim', 'part'], djl__dvjs)

    def impl(source, delim, part):
        return strtok_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], djl__dvjs)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], djl__dvjs)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def translate(arr, source, target):
    args = [arr, source, target]
    for djl__dvjs in range(3):
        if isinstance(args[djl__dvjs], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.translate',
                ['arr', 'source', 'target'], djl__dvjs)

    def impl(arr, source, target):
        return translate_util(arr, source, target)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    zcg__pvdyg = ['arr']
    hkjw__obnu = [arr]
    eae__woh = [True]
    oala__xbj = 'if 0 <= arg0 <= 127:\n'
    oala__xbj += '   res[i] = chr(arg0)\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   bodo.libs.array_kernels.setna(res, i)\n'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def initcap_util(arr, delim):
    verify_string_arg(arr, 'INITCAP', 'arr')
    verify_string_arg(delim, 'INITCAP', 'delim')
    zcg__pvdyg = ['arr', 'delim']
    hkjw__obnu = [arr, delim]
    eae__woh = [True] * 2
    oala__xbj = 'capitalized = arg0[:1].upper()\n'
    oala__xbj += 'for j in range(1, len(arg0)):\n'
    oala__xbj += '   if arg0[j-1] in arg1:\n'
    oala__xbj += '      capitalized += arg0[j].upper()\n'
    oala__xbj += '   else:\n'
    oala__xbj += '      capitalized += arg0[j].lower()\n'
    oala__xbj += 'res[i] = capitalized'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    zcg__pvdyg = ['arr', 'target']
    hkjw__obnu = [arr, target]
    eae__woh = [True] * 2
    oala__xbj = 'res[i] = arg0.find(arg1) + 1'
    hoxk__aath = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@register_jitable
def min_edit_distance(s, t):
    if len(s) > len(t):
        s, t = t, s
    ylh__yfpil, ylqs__abcop = len(s), len(t)
    ejtw__ljbp, ixotj__sxv = 1, 0
    arr = np.zeros((2, ylh__yfpil + 1), dtype=np.uint32)
    arr[0, :] = np.arange(ylh__yfpil + 1)
    for djl__dvjs in range(1, ylqs__abcop + 1):
        arr[ejtw__ljbp, 0] = djl__dvjs
        for xlfzp__swud in range(1, ylh__yfpil + 1):
            if s[xlfzp__swud - 1] == t[djl__dvjs - 1]:
                arr[ejtw__ljbp, xlfzp__swud] = arr[ixotj__sxv, xlfzp__swud - 1]
            else:
                arr[ejtw__ljbp, xlfzp__swud] = 1 + min(arr[ejtw__ljbp, 
                    xlfzp__swud - 1], arr[ixotj__sxv, xlfzp__swud], arr[
                    ixotj__sxv, xlfzp__swud - 1])
        ejtw__ljbp, ixotj__sxv = ixotj__sxv, ejtw__ljbp
    return arr[ylqs__abcop % 2, ylh__yfpil]


@register_jitable
def min_edit_distance_with_max(s, t, maxDistance):
    if maxDistance < 0:
        return 0
    if len(s) > len(t):
        s, t = t, s
    ylh__yfpil, ylqs__abcop = len(s), len(t)
    if ylh__yfpil <= maxDistance and ylqs__abcop <= maxDistance:
        return min_edit_distance(s, t)
    ejtw__ljbp, ixotj__sxv = 1, 0
    arr = np.zeros((2, ylh__yfpil + 1), dtype=np.uint32)
    arr[0, :] = np.arange(ylh__yfpil + 1)
    for djl__dvjs in range(1, ylqs__abcop + 1):
        arr[ejtw__ljbp, 0] = djl__dvjs
        for xlfzp__swud in range(1, ylh__yfpil + 1):
            if s[xlfzp__swud - 1] == t[djl__dvjs - 1]:
                arr[ejtw__ljbp, xlfzp__swud] = arr[ixotj__sxv, xlfzp__swud - 1]
            else:
                arr[ejtw__ljbp, xlfzp__swud] = 1 + min(arr[ejtw__ljbp, 
                    xlfzp__swud - 1], arr[ixotj__sxv, xlfzp__swud], arr[
                    ixotj__sxv, xlfzp__swud - 1])
        if (arr[ejtw__ljbp] >= maxDistance).all():
            return maxDistance
        ejtw__ljbp, ixotj__sxv = ixotj__sxv, ejtw__ljbp
    return min(arr[ylqs__abcop % 2, ylh__yfpil], maxDistance)


@numba.generated_jit(nopython=True)
def editdistance_no_max_util(s, t):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    zcg__pvdyg = ['s', 't']
    hkjw__obnu = [s, t]
    eae__woh = [True] * 2
    oala__xbj = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance(arg0, arg1)'
        )
    hoxk__aath = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def editdistance_with_max_util(s, t, maxDistance):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    verify_int_arg(maxDistance, 'editdistance_no_max', 't')
    zcg__pvdyg = ['s', 't', 'maxDistance']
    hkjw__obnu = [s, t, maxDistance]
    eae__woh = [True] * 3
    oala__xbj = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance_with_max(arg0, arg1, arg2)'
        )
    hoxk__aath = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    zcg__pvdyg = ['arr', 'places']
    hkjw__obnu = [arr, places]
    eae__woh = [True] * 2
    oala__xbj = 'prec = max(arg1, 0)\n'
    oala__xbj += "res[i] = format(arg0, f',.{prec}f')"
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        krcv__vuxh = verify_string_binary_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        pzio__fixiu = "''" if krcv__vuxh else "b''"
        zcg__pvdyg = ['arr', 'n_chars']
        hkjw__obnu = [arr, n_chars]
        eae__woh = [True] * 2
        oala__xbj = 'if arg1 <= 0:\n'
        oala__xbj += f'   res[i] = {pzio__fixiu}\n'
        oala__xbj += 'else:\n'
        if func_name == 'LEFT':
            oala__xbj += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            oala__xbj += '   res[i] = arg0[-arg1:]'
        hoxk__aath = (bodo.string_array_type if krcv__vuxh else bodo.
            binary_array_type)
        return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
            hoxk__aath)
    return overload_left_right_util


def _install_left_right_overload():
    for ndyq__jeca, func_name in zip((left_util, right_util), ('LEFT', 'RIGHT')
        ):
        jfdk__hlmus = create_left_right_util_overload(func_name)
        overload(ndyq__jeca)(jfdk__hlmus)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        wxgq__egx = verify_string_binary_arg(pad_string, func_name,
            'pad_string')
        krcv__vuxh = verify_string_binary_arg(arr, func_name, 'arr')
        if krcv__vuxh != wxgq__egx:
            raise bodo.utils.typing.BodoError(
                'Pad string and arr must be the same type!')
        hoxk__aath = (bodo.string_array_type if krcv__vuxh else bodo.
            binary_array_type)
        verify_int_arg(length, func_name, 'length')
        verify_string_binary_arg(pad_string, func_name,
            f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            oyp__shewy = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            oyp__shewy = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        zcg__pvdyg = ['arr', 'length', 'pad_string']
        hkjw__obnu = [arr, length, pad_string]
        eae__woh = [True] * 3
        pzio__fixiu = "''" if krcv__vuxh else "b''"
        oala__xbj = f"""                if arg1 <= 0:
                    res[i] = {pzio__fixiu}
                elif len(arg2) == 0:
                    res[i] = arg0
                elif len(arg0) >= arg1:
                    res[i] = arg0[:arg1]
                else:
                    quotient = (arg1 - len(arg0)) // len(arg2)
                    remainder = (arg1 - len(arg0)) % len(arg2)
                    res[i] = {oyp__shewy}"""
        return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
            hoxk__aath)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for ndyq__jeca, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')):
        jfdk__hlmus = create_lpad_rpad_util_overload(func_name)
        overload(ndyq__jeca)(jfdk__hlmus)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    zcg__pvdyg = ['arr']
    hkjw__obnu = [arr]
    eae__woh = [True]
    oala__xbj = 'if len(arg0) == 0:\n'
    oala__xbj += '   bodo.libs.array_kernels.setna(res, i)\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   res[i] = ord(arg0[0])'
    hoxk__aath = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    zcg__pvdyg = ['arr', 'repeats']
    hkjw__obnu = [arr, repeats]
    eae__woh = [True] * 2
    oala__xbj = 'if arg1 <= 0:\n'
    oala__xbj += "   res[i] = ''\n"
    oala__xbj += 'else:\n'
    oala__xbj += '   res[i] = arg0 * arg1'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    zcg__pvdyg = ['arr', 'to_replace', 'replace_with']
    hkjw__obnu = [arr, to_replace, replace_with]
    eae__woh = [True] * 3
    oala__xbj = "if arg1 == '':\n"
    oala__xbj += '   res[i] = arg0\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   res[i] = arg0.replace(arg1, arg2)'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    krcv__vuxh = verify_string_binary_arg(arr, 'REVERSE', 'arr')
    zcg__pvdyg = ['arr']
    hkjw__obnu = [arr]
    eae__woh = [True]
    oala__xbj = 'res[i] = arg0[::-1]'
    hoxk__aath = bodo.string_array_type
    hoxk__aath = (bodo.string_array_type if krcv__vuxh else bodo.
        binary_array_type)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    zcg__pvdyg = ['n_chars']
    hkjw__obnu = [n_chars]
    eae__woh = [True]
    oala__xbj = 'if arg0 <= 0:\n'
    oala__xbj += "   res[i] = ''\n"
    oala__xbj += 'else:\n'
    oala__xbj += "   res[i] = ' ' * arg0"
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def split_part_util(source, delim, part):
    verify_string_arg(source, 'SPLIT_PART', 'source')
    verify_string_arg(delim, 'SPLIT_PART', 'delim')
    verify_int_arg(part, 'SPLIT_PART', 'part')
    zcg__pvdyg = ['source', 'delim', 'part']
    hkjw__obnu = [source, delim, part]
    eae__woh = [True] * 3
    oala__xbj = "tokens = arg0.split(arg1) if arg1 != '' else [arg0]\n"
    oala__xbj += 'if abs(arg2) > len(tokens):\n'
    oala__xbj += "    res[i] = ''\n"
    oala__xbj += 'else:\n'
    oala__xbj += '    res[i] = tokens[arg2 if arg2 <= 0 else arg2-1]\n'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    zcg__pvdyg = ['arr0', 'arr1']
    hkjw__obnu = [arr0, arr1]
    eae__woh = [True] * 2
    oala__xbj = 'if arg0 < arg1:\n'
    oala__xbj += '   res[i] = -1\n'
    oala__xbj += 'elif arg0 > arg1:\n'
    oala__xbj += '   res[i] = 1\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   res[i] = 0\n'
    hoxk__aath = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def strtok_util(source, delim, part):
    verify_string_arg(source, 'STRTOK', 'source')
    verify_string_arg(delim, 'STRTOK', 'delim')
    verify_int_arg(part, 'STRTOK', 'part')
    zcg__pvdyg = ['source', 'delim', 'part']
    hkjw__obnu = [source, delim, part]
    eae__woh = [True] * 3
    oala__xbj = "if (arg0 == '' and arg1 == '') or arg2 <= 0:\n"
    oala__xbj += '   bodo.libs.array_kernels.setna(res, i)\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   tokens = []\n'
    oala__xbj += "   buffer = ''\n"
    oala__xbj += '   for j in range(len(arg0)):\n'
    oala__xbj += '      if arg0[j] in arg1:\n'
    oala__xbj += "         if buffer != '':"
    oala__xbj += '            tokens.append(buffer)\n'
    oala__xbj += "         buffer = ''\n"
    oala__xbj += '      else:\n'
    oala__xbj += '         buffer += arg0[j]\n'
    oala__xbj += "   if buffer != '':\n"
    oala__xbj += '      tokens.append(buffer)\n'
    oala__xbj += '   if arg2 > len(tokens):\n'
    oala__xbj += '      bodo.libs.array_kernels.setna(res, i)\n'
    oala__xbj += '   else:\n'
    oala__xbj += '      res[i] = tokens[arg2-1]\n'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    krcv__vuxh = verify_string_binary_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    hoxk__aath = (bodo.string_array_type if krcv__vuxh else bodo.
        binary_array_type)
    zcg__pvdyg = ['arr', 'start', 'length']
    hkjw__obnu = [arr, start, length]
    eae__woh = [True] * 3
    oala__xbj = 'if arg2 <= 0:\n'
    oala__xbj += "   res[i] = ''\n" if krcv__vuxh else "   res[i] = b''\n"
    oala__xbj += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    oala__xbj += '   res[i] = arg0[arg1:]\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   if arg1 > 0: arg1 -= 1\n'
    oala__xbj += '   res[i] = arg0[arg1:arg1+arg2]\n'
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    zcg__pvdyg = ['arr', 'delimiter', 'occurrences']
    hkjw__obnu = [arr, delimiter, occurrences]
    eae__woh = [True] * 3
    oala__xbj = "if arg1 == '' or arg2 == 0:\n"
    oala__xbj += "   res[i] = ''\n"
    oala__xbj += 'elif arg2 >= 0:\n'
    oala__xbj += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    oala__xbj += 'else:\n'
    oala__xbj += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)


@numba.generated_jit(nopython=True)
def translate_util(arr, source, target):
    verify_string_arg(arr, 'translate', 'arr')
    verify_string_arg(source, 'translate', 'source')
    verify_string_arg(target, 'translate', 'target')
    zcg__pvdyg = ['arr', 'source', 'target']
    hkjw__obnu = [arr, source, target]
    eae__woh = [True] * 3
    oala__xbj = "translated = ''\n"
    oala__xbj += 'for char in arg0:\n'
    oala__xbj += '   index = arg1.find(char)\n'
    oala__xbj += '   if index == -1:\n'
    oala__xbj += '      translated += char\n'
    oala__xbj += '   elif index < len(arg2):\n'
    oala__xbj += '      translated += arg2[index]\n'
    oala__xbj += 'res[i] = translated'
    hoxk__aath = bodo.string_array_type
    return gen_vectorized(zcg__pvdyg, hkjw__obnu, eae__woh, oala__xbj,
        hoxk__aath)
