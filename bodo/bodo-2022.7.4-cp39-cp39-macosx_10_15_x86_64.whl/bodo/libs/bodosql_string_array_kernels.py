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
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_no_max', ['s',
                't'], gfbmq__fbtc)

    def impl(s, t):
        return editdistance_no_max_util(s, t)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_with_max(s, t, maxDistance):
    args = [s, t, maxDistance]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_with_max', [
                's', 't', 'maxDistance'], gfbmq__fbtc)

    def impl(s, t, maxDistance):
        return editdistance_with_max_util(s, t, maxDistance)
    return impl


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], gfbmq__fbtc)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def initcap(arr, delim):
    args = [arr, delim]
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.initcap',
                ['arr', 'delim'], gfbmq__fbtc)

    def impl(arr, delim):
        return initcap_util(arr, delim)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], gfbmq__fbtc)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], gfbmq__fbtc)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], gfbmq__fbtc)

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
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], gfbmq__fbtc)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], gfbmq__fbtc)

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
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], gfbmq__fbtc)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], gfbmq__fbtc)

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
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.split_part',
                ['source', 'delim', 'part'], gfbmq__fbtc)

    def impl(source, delim, part):
        return split_part_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def strcmp(arr0, arr1):
    args = [arr0, arr1]
    for gfbmq__fbtc in range(2):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], gfbmq__fbtc)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def strtok(source, delim, part):
    args = [source, delim, part]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strtok',
                ['source', 'delim', 'part'], gfbmq__fbtc)

    def impl(source, delim, part):
        return strtok_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], gfbmq__fbtc)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], gfbmq__fbtc)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def translate(arr, source, target):
    args = [arr, source, target]
    for gfbmq__fbtc in range(3):
        if isinstance(args[gfbmq__fbtc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.translate',
                ['arr', 'source', 'target'], gfbmq__fbtc)

    def impl(arr, source, target):
        return translate_util(arr, source, target)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    djvlw__qwoe = ['arr']
    kfpin__jeno = [arr]
    zygu__ganav = [True]
    pmehq__dpa = 'if 0 <= arg0 <= 127:\n'
    pmehq__dpa += '   res[i] = chr(arg0)\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   bodo.libs.array_kernels.setna(res, i)\n'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def initcap_util(arr, delim):
    verify_string_arg(arr, 'INITCAP', 'arr')
    verify_string_arg(delim, 'INITCAP', 'delim')
    djvlw__qwoe = ['arr', 'delim']
    kfpin__jeno = [arr, delim]
    zygu__ganav = [True] * 2
    pmehq__dpa = 'capitalized = arg0[:1].upper()\n'
    pmehq__dpa += 'for j in range(1, len(arg0)):\n'
    pmehq__dpa += '   if arg0[j-1] in arg1:\n'
    pmehq__dpa += '      capitalized += arg0[j].upper()\n'
    pmehq__dpa += '   else:\n'
    pmehq__dpa += '      capitalized += arg0[j].lower()\n'
    pmehq__dpa += 'res[i] = capitalized'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    djvlw__qwoe = ['arr', 'target']
    kfpin__jeno = [arr, target]
    zygu__ganav = [True] * 2
    pmehq__dpa = 'res[i] = arg0.find(arg1) + 1'
    ughjx__oxww = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@register_jitable
def min_edit_distance(s, t):
    if len(s) > len(t):
        s, t = t, s
    zji__okau, zzdau__nuhwa = len(s), len(t)
    lyfy__tdvow, ujl__vyws = 1, 0
    arr = np.zeros((2, zji__okau + 1), dtype=np.uint32)
    arr[0, :] = np.arange(zji__okau + 1)
    for gfbmq__fbtc in range(1, zzdau__nuhwa + 1):
        arr[lyfy__tdvow, 0] = gfbmq__fbtc
        for nlt__vaz in range(1, zji__okau + 1):
            if s[nlt__vaz - 1] == t[gfbmq__fbtc - 1]:
                arr[lyfy__tdvow, nlt__vaz] = arr[ujl__vyws, nlt__vaz - 1]
            else:
                arr[lyfy__tdvow, nlt__vaz] = 1 + min(arr[lyfy__tdvow, 
                    nlt__vaz - 1], arr[ujl__vyws, nlt__vaz], arr[ujl__vyws,
                    nlt__vaz - 1])
        lyfy__tdvow, ujl__vyws = ujl__vyws, lyfy__tdvow
    return arr[zzdau__nuhwa % 2, zji__okau]


@register_jitable
def min_edit_distance_with_max(s, t, maxDistance):
    if maxDistance < 0:
        return 0
    if len(s) > len(t):
        s, t = t, s
    zji__okau, zzdau__nuhwa = len(s), len(t)
    if zji__okau <= maxDistance and zzdau__nuhwa <= maxDistance:
        return min_edit_distance(s, t)
    lyfy__tdvow, ujl__vyws = 1, 0
    arr = np.zeros((2, zji__okau + 1), dtype=np.uint32)
    arr[0, :] = np.arange(zji__okau + 1)
    for gfbmq__fbtc in range(1, zzdau__nuhwa + 1):
        arr[lyfy__tdvow, 0] = gfbmq__fbtc
        for nlt__vaz in range(1, zji__okau + 1):
            if s[nlt__vaz - 1] == t[gfbmq__fbtc - 1]:
                arr[lyfy__tdvow, nlt__vaz] = arr[ujl__vyws, nlt__vaz - 1]
            else:
                arr[lyfy__tdvow, nlt__vaz] = 1 + min(arr[lyfy__tdvow, 
                    nlt__vaz - 1], arr[ujl__vyws, nlt__vaz], arr[ujl__vyws,
                    nlt__vaz - 1])
        if (arr[lyfy__tdvow] >= maxDistance).all():
            return maxDistance
        lyfy__tdvow, ujl__vyws = ujl__vyws, lyfy__tdvow
    return min(arr[zzdau__nuhwa % 2, zji__okau], maxDistance)


@numba.generated_jit(nopython=True)
def editdistance_no_max_util(s, t):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    djvlw__qwoe = ['s', 't']
    kfpin__jeno = [s, t]
    zygu__ganav = [True] * 2
    pmehq__dpa = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance(arg0, arg1)'
        )
    ughjx__oxww = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def editdistance_with_max_util(s, t, maxDistance):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    verify_int_arg(maxDistance, 'editdistance_no_max', 't')
    djvlw__qwoe = ['s', 't', 'maxDistance']
    kfpin__jeno = [s, t, maxDistance]
    zygu__ganav = [True] * 3
    pmehq__dpa = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance_with_max(arg0, arg1, arg2)'
        )
    ughjx__oxww = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    djvlw__qwoe = ['arr', 'places']
    kfpin__jeno = [arr, places]
    zygu__ganav = [True] * 2
    pmehq__dpa = 'prec = max(arg1, 0)\n'
    pmehq__dpa += "res[i] = format(arg0, f',.{prec}f')"
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        iomc__ztogm = verify_string_binary_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        sdu__kdrcm = "''" if iomc__ztogm else "b''"
        djvlw__qwoe = ['arr', 'n_chars']
        kfpin__jeno = [arr, n_chars]
        zygu__ganav = [True] * 2
        pmehq__dpa = 'if arg1 <= 0:\n'
        pmehq__dpa += f'   res[i] = {sdu__kdrcm}\n'
        pmehq__dpa += 'else:\n'
        if func_name == 'LEFT':
            pmehq__dpa += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            pmehq__dpa += '   res[i] = arg0[-arg1:]'
        ughjx__oxww = (bodo.string_array_type if iomc__ztogm else bodo.
            binary_array_type)
        return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav,
            pmehq__dpa, ughjx__oxww)
    return overload_left_right_util


def _install_left_right_overload():
    for wfsz__argfu, func_name in zip((left_util, right_util), ('LEFT',
        'RIGHT')):
        aoxmz__hwgzz = create_left_right_util_overload(func_name)
        overload(wfsz__argfu)(aoxmz__hwgzz)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        etcya__rbqw = verify_string_binary_arg(pad_string, func_name,
            'pad_string')
        iomc__ztogm = verify_string_binary_arg(arr, func_name, 'arr')
        if iomc__ztogm != etcya__rbqw:
            raise bodo.utils.typing.BodoError(
                'Pad string and arr must be the same type!')
        ughjx__oxww = (bodo.string_array_type if iomc__ztogm else bodo.
            binary_array_type)
        verify_int_arg(length, func_name, 'length')
        verify_string_binary_arg(pad_string, func_name,
            f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            lwqw__bba = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            lwqw__bba = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        djvlw__qwoe = ['arr', 'length', 'pad_string']
        kfpin__jeno = [arr, length, pad_string]
        zygu__ganav = [True] * 3
        sdu__kdrcm = "''" if iomc__ztogm else "b''"
        pmehq__dpa = f"""                if arg1 <= 0:
                    res[i] = {sdu__kdrcm}
                elif len(arg2) == 0:
                    res[i] = arg0
                elif len(arg0) >= arg1:
                    res[i] = arg0[:arg1]
                else:
                    quotient = (arg1 - len(arg0)) // len(arg2)
                    remainder = (arg1 - len(arg0)) % len(arg2)
                    res[i] = {lwqw__bba}"""
        return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav,
            pmehq__dpa, ughjx__oxww)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for wfsz__argfu, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        aoxmz__hwgzz = create_lpad_rpad_util_overload(func_name)
        overload(wfsz__argfu)(aoxmz__hwgzz)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    djvlw__qwoe = ['arr']
    kfpin__jeno = [arr]
    zygu__ganav = [True]
    pmehq__dpa = 'if len(arg0) == 0:\n'
    pmehq__dpa += '   bodo.libs.array_kernels.setna(res, i)\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   res[i] = ord(arg0[0])'
    ughjx__oxww = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    djvlw__qwoe = ['arr', 'repeats']
    kfpin__jeno = [arr, repeats]
    zygu__ganav = [True] * 2
    pmehq__dpa = 'if arg1 <= 0:\n'
    pmehq__dpa += "   res[i] = ''\n"
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   res[i] = arg0 * arg1'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    djvlw__qwoe = ['arr', 'to_replace', 'replace_with']
    kfpin__jeno = [arr, to_replace, replace_with]
    zygu__ganav = [True] * 3
    pmehq__dpa = "if arg1 == '':\n"
    pmehq__dpa += '   res[i] = arg0\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   res[i] = arg0.replace(arg1, arg2)'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    iomc__ztogm = verify_string_binary_arg(arr, 'REVERSE', 'arr')
    djvlw__qwoe = ['arr']
    kfpin__jeno = [arr]
    zygu__ganav = [True]
    pmehq__dpa = 'res[i] = arg0[::-1]'
    ughjx__oxww = bodo.string_array_type
    ughjx__oxww = (bodo.string_array_type if iomc__ztogm else bodo.
        binary_array_type)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    djvlw__qwoe = ['n_chars']
    kfpin__jeno = [n_chars]
    zygu__ganav = [True]
    pmehq__dpa = 'if arg0 <= 0:\n'
    pmehq__dpa += "   res[i] = ''\n"
    pmehq__dpa += 'else:\n'
    pmehq__dpa += "   res[i] = ' ' * arg0"
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def split_part_util(source, delim, part):
    verify_string_arg(source, 'SPLIT_PART', 'source')
    verify_string_arg(delim, 'SPLIT_PART', 'delim')
    verify_int_arg(part, 'SPLIT_PART', 'part')
    djvlw__qwoe = ['source', 'delim', 'part']
    kfpin__jeno = [source, delim, part]
    zygu__ganav = [True] * 3
    pmehq__dpa = "tokens = arg0.split(arg1) if arg1 != '' else [arg0]\n"
    pmehq__dpa += 'if abs(arg2) > len(tokens):\n'
    pmehq__dpa += "    res[i] = ''\n"
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '    res[i] = tokens[arg2 if arg2 <= 0 else arg2-1]\n'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    djvlw__qwoe = ['arr0', 'arr1']
    kfpin__jeno = [arr0, arr1]
    zygu__ganav = [True] * 2
    pmehq__dpa = 'if arg0 < arg1:\n'
    pmehq__dpa += '   res[i] = -1\n'
    pmehq__dpa += 'elif arg0 > arg1:\n'
    pmehq__dpa += '   res[i] = 1\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   res[i] = 0\n'
    ughjx__oxww = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def strtok_util(source, delim, part):
    verify_string_arg(source, 'STRTOK', 'source')
    verify_string_arg(delim, 'STRTOK', 'delim')
    verify_int_arg(part, 'STRTOK', 'part')
    djvlw__qwoe = ['source', 'delim', 'part']
    kfpin__jeno = [source, delim, part]
    zygu__ganav = [True] * 3
    pmehq__dpa = "if (arg0 == '' and arg1 == '') or arg2 <= 0:\n"
    pmehq__dpa += '   bodo.libs.array_kernels.setna(res, i)\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   tokens = []\n'
    pmehq__dpa += "   buffer = ''\n"
    pmehq__dpa += '   for j in range(len(arg0)):\n'
    pmehq__dpa += '      if arg0[j] in arg1:\n'
    pmehq__dpa += "         if buffer != '':"
    pmehq__dpa += '            tokens.append(buffer)\n'
    pmehq__dpa += "         buffer = ''\n"
    pmehq__dpa += '      else:\n'
    pmehq__dpa += '         buffer += arg0[j]\n'
    pmehq__dpa += "   if buffer != '':\n"
    pmehq__dpa += '      tokens.append(buffer)\n'
    pmehq__dpa += '   if arg2 > len(tokens):\n'
    pmehq__dpa += '      bodo.libs.array_kernels.setna(res, i)\n'
    pmehq__dpa += '   else:\n'
    pmehq__dpa += '      res[i] = tokens[arg2-1]\n'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    iomc__ztogm = verify_string_binary_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    ughjx__oxww = (bodo.string_array_type if iomc__ztogm else bodo.
        binary_array_type)
    djvlw__qwoe = ['arr', 'start', 'length']
    kfpin__jeno = [arr, start, length]
    zygu__ganav = [True] * 3
    pmehq__dpa = 'if arg2 <= 0:\n'
    pmehq__dpa += "   res[i] = ''\n" if iomc__ztogm else "   res[i] = b''\n"
    pmehq__dpa += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    pmehq__dpa += '   res[i] = arg0[arg1:]\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   if arg1 > 0: arg1 -= 1\n'
    pmehq__dpa += '   res[i] = arg0[arg1:arg1+arg2]\n'
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    djvlw__qwoe = ['arr', 'delimiter', 'occurrences']
    kfpin__jeno = [arr, delimiter, occurrences]
    zygu__ganav = [True] * 3
    pmehq__dpa = "if arg1 == '' or arg2 == 0:\n"
    pmehq__dpa += "   res[i] = ''\n"
    pmehq__dpa += 'elif arg2 >= 0:\n'
    pmehq__dpa += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    pmehq__dpa += 'else:\n'
    pmehq__dpa += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)


@numba.generated_jit(nopython=True)
def translate_util(arr, source, target):
    verify_string_arg(arr, 'translate', 'arr')
    verify_string_arg(source, 'translate', 'source')
    verify_string_arg(target, 'translate', 'target')
    djvlw__qwoe = ['arr', 'source', 'target']
    kfpin__jeno = [arr, source, target]
    zygu__ganav = [True] * 3
    pmehq__dpa = "translated = ''\n"
    pmehq__dpa += 'for char in arg0:\n'
    pmehq__dpa += '   index = arg1.find(char)\n'
    pmehq__dpa += '   if index == -1:\n'
    pmehq__dpa += '      translated += char\n'
    pmehq__dpa += '   elif index < len(arg2):\n'
    pmehq__dpa += '      translated += arg2[index]\n'
    pmehq__dpa += 'res[i] = translated'
    ughjx__oxww = bodo.string_array_type
    return gen_vectorized(djvlw__qwoe, kfpin__jeno, zygu__ganav, pmehq__dpa,
        ughjx__oxww)
