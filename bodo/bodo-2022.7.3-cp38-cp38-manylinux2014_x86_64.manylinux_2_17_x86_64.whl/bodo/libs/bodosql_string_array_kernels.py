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
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_no_max', ['s',
                't'], aptwk__pey)

    def impl(s, t):
        return editdistance_no_max_util(s, t)
    return impl


@numba.generated_jit(nopython=True)
def editdistance_with_max(s, t, maxDistance):
    args = [s, t, maxDistance]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.editdistance_with_max', [
                's', 't', 'maxDistance'], aptwk__pey)

    def impl(s, t, maxDistance):
        return editdistance_with_max_util(s, t, maxDistance)
    return impl


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], aptwk__pey)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def initcap(arr, delim):
    args = [arr, delim]
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.initcap',
                ['arr', 'delim'], aptwk__pey)

    def impl(arr, delim):
        return initcap_util(arr, delim)
    return impl


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], aptwk__pey)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


def left(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], aptwk__pey)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


def lpad(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], aptwk__pey)

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
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], aptwk__pey)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], aptwk__pey)

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
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], aptwk__pey)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def rpad(arr, length, padstr):
    return


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], aptwk__pey)

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
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.split_part',
                ['source', 'delim', 'part'], aptwk__pey)

    def impl(source, delim, part):
        return split_part_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def strcmp(arr0, arr1):
    args = [arr0, arr1]
    for aptwk__pey in range(2):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], aptwk__pey)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def strtok(source, delim, part):
    args = [source, delim, part]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strtok',
                ['source', 'delim', 'part'], aptwk__pey)

    def impl(source, delim, part):
        return strtok_util(source, delim, part)
    return impl


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], aptwk__pey)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], aptwk__pey)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def translate(arr, source, target):
    args = [arr, source, target]
    for aptwk__pey in range(3):
        if isinstance(args[aptwk__pey], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.translate',
                ['arr', 'source', 'target'], aptwk__pey)

    def impl(arr, source, target):
        return translate_util(arr, source, target)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    nvl__jhmx = ['arr']
    nxhur__xakws = [arr]
    qdwn__ivan = [True]
    mtqjc__illid = 'if 0 <= arg0 <= 127:\n'
    mtqjc__illid += '   res[i] = chr(arg0)\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   bodo.libs.array_kernels.setna(res, i)\n'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def initcap_util(arr, delim):
    verify_string_arg(arr, 'INITCAP', 'arr')
    verify_string_arg(delim, 'INITCAP', 'delim')
    nvl__jhmx = ['arr', 'delim']
    nxhur__xakws = [arr, delim]
    qdwn__ivan = [True] * 2
    mtqjc__illid = 'capitalized = arg0[:1].upper()\n'
    mtqjc__illid += 'for j in range(1, len(arg0)):\n'
    mtqjc__illid += '   if arg0[j-1] in arg1:\n'
    mtqjc__illid += '      capitalized += arg0[j].upper()\n'
    mtqjc__illid += '   else:\n'
    mtqjc__illid += '      capitalized += arg0[j].lower()\n'
    mtqjc__illid += 'res[i] = capitalized'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    nvl__jhmx = ['arr', 'target']
    nxhur__xakws = [arr, target]
    qdwn__ivan = [True] * 2
    mtqjc__illid = 'res[i] = arg0.find(arg1) + 1'
    iygh__dxj = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@register_jitable
def min_edit_distance(s, t):
    if len(s) > len(t):
        s, t = t, s
    duh__rintk, dknps__cno = len(s), len(t)
    twqe__elvri, ypplz__qhu = 1, 0
    arr = np.zeros((2, duh__rintk + 1), dtype=np.uint32)
    arr[0, :] = np.arange(duh__rintk + 1)
    for aptwk__pey in range(1, dknps__cno + 1):
        arr[twqe__elvri, 0] = aptwk__pey
        for ydxi__igyw in range(1, duh__rintk + 1):
            if s[ydxi__igyw - 1] == t[aptwk__pey - 1]:
                arr[twqe__elvri, ydxi__igyw] = arr[ypplz__qhu, ydxi__igyw - 1]
            else:
                arr[twqe__elvri, ydxi__igyw] = 1 + min(arr[twqe__elvri, 
                    ydxi__igyw - 1], arr[ypplz__qhu, ydxi__igyw], arr[
                    ypplz__qhu, ydxi__igyw - 1])
        twqe__elvri, ypplz__qhu = ypplz__qhu, twqe__elvri
    return arr[dknps__cno % 2, duh__rintk]


@register_jitable
def min_edit_distance_with_max(s, t, maxDistance):
    if maxDistance < 0:
        return 0
    if len(s) > len(t):
        s, t = t, s
    duh__rintk, dknps__cno = len(s), len(t)
    if duh__rintk <= maxDistance and dknps__cno <= maxDistance:
        return min_edit_distance(s, t)
    twqe__elvri, ypplz__qhu = 1, 0
    arr = np.zeros((2, duh__rintk + 1), dtype=np.uint32)
    arr[0, :] = np.arange(duh__rintk + 1)
    for aptwk__pey in range(1, dknps__cno + 1):
        arr[twqe__elvri, 0] = aptwk__pey
        for ydxi__igyw in range(1, duh__rintk + 1):
            if s[ydxi__igyw - 1] == t[aptwk__pey - 1]:
                arr[twqe__elvri, ydxi__igyw] = arr[ypplz__qhu, ydxi__igyw - 1]
            else:
                arr[twqe__elvri, ydxi__igyw] = 1 + min(arr[twqe__elvri, 
                    ydxi__igyw - 1], arr[ypplz__qhu, ydxi__igyw], arr[
                    ypplz__qhu, ydxi__igyw - 1])
        if (arr[twqe__elvri] >= maxDistance).all():
            return maxDistance
        twqe__elvri, ypplz__qhu = ypplz__qhu, twqe__elvri
    return min(arr[dknps__cno % 2, duh__rintk], maxDistance)


@numba.generated_jit(nopython=True)
def editdistance_no_max_util(s, t):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    nvl__jhmx = ['s', 't']
    nxhur__xakws = [s, t]
    qdwn__ivan = [True] * 2
    mtqjc__illid = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance(arg0, arg1)'
        )
    iygh__dxj = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def editdistance_with_max_util(s, t, maxDistance):
    verify_string_arg(s, 'editdistance_no_max', 's')
    verify_string_arg(t, 'editdistance_no_max', 't')
    verify_int_arg(maxDistance, 'editdistance_no_max', 't')
    nvl__jhmx = ['s', 't', 'maxDistance']
    nxhur__xakws = [s, t, maxDistance]
    qdwn__ivan = [True] * 3
    mtqjc__illid = (
        'res[i] = bodo.libs.bodosql_array_kernels.min_edit_distance_with_max(arg0, arg1, arg2)'
        )
    iygh__dxj = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    nvl__jhmx = ['arr', 'places']
    nxhur__xakws = [arr, places]
    qdwn__ivan = [True] * 2
    mtqjc__illid = 'prec = max(arg1, 0)\n'
    mtqjc__illid += "res[i] = format(arg0, f',.{prec}f')"
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        qjgxm__jkq = verify_string_binary_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        vsmlk__wolv = "''" if qjgxm__jkq else "b''"
        nvl__jhmx = ['arr', 'n_chars']
        nxhur__xakws = [arr, n_chars]
        qdwn__ivan = [True] * 2
        mtqjc__illid = 'if arg1 <= 0:\n'
        mtqjc__illid += f'   res[i] = {vsmlk__wolv}\n'
        mtqjc__illid += 'else:\n'
        if func_name == 'LEFT':
            mtqjc__illid += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            mtqjc__illid += '   res[i] = arg0[-arg1:]'
        iygh__dxj = (bodo.string_array_type if qjgxm__jkq else bodo.
            binary_array_type)
        return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan,
            mtqjc__illid, iygh__dxj)
    return overload_left_right_util


def _install_left_right_overload():
    for uwgeg__qjqny, func_name in zip((left_util, right_util), ('LEFT',
        'RIGHT')):
        yelkz__hroaf = create_left_right_util_overload(func_name)
        overload(uwgeg__qjqny)(yelkz__hroaf)


_install_left_right_overload()


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        frcox__winkn = verify_string_binary_arg(pad_string, func_name,
            'pad_string')
        qjgxm__jkq = verify_string_binary_arg(arr, func_name, 'arr')
        if qjgxm__jkq != frcox__winkn:
            raise bodo.utils.typing.BodoError(
                'Pad string and arr must be the same type!')
        iygh__dxj = (bodo.string_array_type if qjgxm__jkq else bodo.
            binary_array_type)
        verify_int_arg(length, func_name, 'length')
        verify_string_binary_arg(pad_string, func_name,
            f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            iiozq__ijbha = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            iiozq__ijbha = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        nvl__jhmx = ['arr', 'length', 'pad_string']
        nxhur__xakws = [arr, length, pad_string]
        qdwn__ivan = [True] * 3
        vsmlk__wolv = "''" if qjgxm__jkq else "b''"
        mtqjc__illid = f"""                if arg1 <= 0:
                    res[i] = {vsmlk__wolv}
                elif len(arg2) == 0:
                    res[i] = arg0
                elif len(arg0) >= arg1:
                    res[i] = arg0[:arg1]
                else:
                    quotient = (arg1 - len(arg0)) // len(arg2)
                    remainder = (arg1 - len(arg0)) % len(arg2)
                    res[i] = {iiozq__ijbha}"""
        return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan,
            mtqjc__illid, iygh__dxj)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for uwgeg__qjqny, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        yelkz__hroaf = create_lpad_rpad_util_overload(func_name)
        overload(uwgeg__qjqny)(yelkz__hroaf)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    nvl__jhmx = ['arr']
    nxhur__xakws = [arr]
    qdwn__ivan = [True]
    mtqjc__illid = 'if len(arg0) == 0:\n'
    mtqjc__illid += '   bodo.libs.array_kernels.setna(res, i)\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   res[i] = ord(arg0[0])'
    iygh__dxj = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    nvl__jhmx = ['arr', 'repeats']
    nxhur__xakws = [arr, repeats]
    qdwn__ivan = [True] * 2
    mtqjc__illid = 'if arg1 <= 0:\n'
    mtqjc__illid += "   res[i] = ''\n"
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   res[i] = arg0 * arg1'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    nvl__jhmx = ['arr', 'to_replace', 'replace_with']
    nxhur__xakws = [arr, to_replace, replace_with]
    qdwn__ivan = [True] * 3
    mtqjc__illid = "if arg1 == '':\n"
    mtqjc__illid += '   res[i] = arg0\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   res[i] = arg0.replace(arg1, arg2)'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    qjgxm__jkq = verify_string_binary_arg(arr, 'REVERSE', 'arr')
    nvl__jhmx = ['arr']
    nxhur__xakws = [arr]
    qdwn__ivan = [True]
    mtqjc__illid = 'res[i] = arg0[::-1]'
    iygh__dxj = bodo.string_array_type
    iygh__dxj = (bodo.string_array_type if qjgxm__jkq else bodo.
        binary_array_type)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    nvl__jhmx = ['n_chars']
    nxhur__xakws = [n_chars]
    qdwn__ivan = [True]
    mtqjc__illid = 'if arg0 <= 0:\n'
    mtqjc__illid += "   res[i] = ''\n"
    mtqjc__illid += 'else:\n'
    mtqjc__illid += "   res[i] = ' ' * arg0"
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def split_part_util(source, delim, part):
    verify_string_arg(source, 'SPLIT_PART', 'source')
    verify_string_arg(delim, 'SPLIT_PART', 'delim')
    verify_int_arg(part, 'SPLIT_PART', 'part')
    nvl__jhmx = ['source', 'delim', 'part']
    nxhur__xakws = [source, delim, part]
    qdwn__ivan = [True] * 3
    mtqjc__illid = "tokens = arg0.split(arg1) if arg1 != '' else [arg0]\n"
    mtqjc__illid += 'if abs(arg2) > len(tokens):\n'
    mtqjc__illid += "    res[i] = ''\n"
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '    res[i] = tokens[arg2 if arg2 <= 0 else arg2-1]\n'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    nvl__jhmx = ['arr0', 'arr1']
    nxhur__xakws = [arr0, arr1]
    qdwn__ivan = [True] * 2
    mtqjc__illid = 'if arg0 < arg1:\n'
    mtqjc__illid += '   res[i] = -1\n'
    mtqjc__illid += 'elif arg0 > arg1:\n'
    mtqjc__illid += '   res[i] = 1\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   res[i] = 0\n'
    iygh__dxj = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def strtok_util(source, delim, part):
    verify_string_arg(source, 'STRTOK', 'source')
    verify_string_arg(delim, 'STRTOK', 'delim')
    verify_int_arg(part, 'STRTOK', 'part')
    nvl__jhmx = ['source', 'delim', 'part']
    nxhur__xakws = [source, delim, part]
    qdwn__ivan = [True] * 3
    mtqjc__illid = "if (arg0 == '' and arg1 == '') or arg2 <= 0:\n"
    mtqjc__illid += '   bodo.libs.array_kernels.setna(res, i)\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   tokens = []\n'
    mtqjc__illid += "   buffer = ''\n"
    mtqjc__illid += '   for j in range(len(arg0)):\n'
    mtqjc__illid += '      if arg0[j] in arg1:\n'
    mtqjc__illid += "         if buffer != '':"
    mtqjc__illid += '            tokens.append(buffer)\n'
    mtqjc__illid += "         buffer = ''\n"
    mtqjc__illid += '      else:\n'
    mtqjc__illid += '         buffer += arg0[j]\n'
    mtqjc__illid += "   if buffer != '':\n"
    mtqjc__illid += '      tokens.append(buffer)\n'
    mtqjc__illid += '   if arg2 > len(tokens):\n'
    mtqjc__illid += '      bodo.libs.array_kernels.setna(res, i)\n'
    mtqjc__illid += '   else:\n'
    mtqjc__illid += '      res[i] = tokens[arg2-1]\n'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    qjgxm__jkq = verify_string_binary_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    iygh__dxj = (bodo.string_array_type if qjgxm__jkq else bodo.
        binary_array_type)
    nvl__jhmx = ['arr', 'start', 'length']
    nxhur__xakws = [arr, start, length]
    qdwn__ivan = [True] * 3
    mtqjc__illid = 'if arg2 <= 0:\n'
    mtqjc__illid += "   res[i] = ''\n" if qjgxm__jkq else "   res[i] = b''\n"
    mtqjc__illid += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    mtqjc__illid += '   res[i] = arg0[arg1:]\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   if arg1 > 0: arg1 -= 1\n'
    mtqjc__illid += '   res[i] = arg0[arg1:arg1+arg2]\n'
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    nvl__jhmx = ['arr', 'delimiter', 'occurrences']
    nxhur__xakws = [arr, delimiter, occurrences]
    qdwn__ivan = [True] * 3
    mtqjc__illid = "if arg1 == '' or arg2 == 0:\n"
    mtqjc__illid += "   res[i] = ''\n"
    mtqjc__illid += 'elif arg2 >= 0:\n'
    mtqjc__illid += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    mtqjc__illid += 'else:\n'
    mtqjc__illid += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)


@numba.generated_jit(nopython=True)
def translate_util(arr, source, target):
    verify_string_arg(arr, 'translate', 'arr')
    verify_string_arg(source, 'translate', 'source')
    verify_string_arg(target, 'translate', 'target')
    nvl__jhmx = ['arr', 'source', 'target']
    nxhur__xakws = [arr, source, target]
    qdwn__ivan = [True] * 3
    mtqjc__illid = "translated = ''\n"
    mtqjc__illid += 'for char in arg0:\n'
    mtqjc__illid += '   index = arg1.find(char)\n'
    mtqjc__illid += '   if index == -1:\n'
    mtqjc__illid += '      translated += char\n'
    mtqjc__illid += '   elif index < len(arg2):\n'
    mtqjc__illid += '      translated += arg2[index]\n'
    mtqjc__illid += 'res[i] = translated'
    iygh__dxj = bodo.string_array_type
    return gen_vectorized(nvl__jhmx, nxhur__xakws, qdwn__ivan, mtqjc__illid,
        iygh__dxj)
