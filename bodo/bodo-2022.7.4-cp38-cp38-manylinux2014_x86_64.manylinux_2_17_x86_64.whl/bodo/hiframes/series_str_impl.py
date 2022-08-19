"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_bin_arr_type, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error
from bodo.utils.utils import synchronize_error_njit


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        xyrc__uqrdw = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(xyrc__uqrdw)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ngjv__viqv = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, ngjv__viqv)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        pgfx__wxh, = args
        ahj__rqia = signature.return_type
        kwk__hflk = cgutils.create_struct_proxy(ahj__rqia)(context, builder)
        kwk__hflk.obj = pgfx__wxh
        context.nrt.incref(builder, signature.args[0], pgfx__wxh)
        return kwk__hflk._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not (is_str_arr_type(S.data) or S.data ==
        string_array_split_view_type or isinstance(S.data,
        ArrayItemArrayType) or is_bin_arr_type(S.data)):
        raise_bodo_error(
            'Series.str: input should be a series of string/binary or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_len_dict_impl(S_str):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(ecmrb__czcl)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(ecmrb__czcl, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n
        ) == -1 and S_str.stype.data == string_array_type:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(ecmrb__czcl,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(ecmrb__czcl, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    jjyh__tqu = S_str.stype.data
    if (jjyh__tqu != string_array_split_view_type and not is_str_arr_type(
        jjyh__tqu)) and not isinstance(jjyh__tqu, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(jjyh__tqu, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(ecmrb__czcl, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_get_array_impl
    if jjyh__tqu == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(ecmrb__czcl)
            ycm__mcjvm = 0
            for ndr__bujqq in numba.parfors.parfor.internal_prange(n):
                xkrte__aja, xkrte__aja, etdx__djko = get_split_view_index(
                    ecmrb__czcl, ndr__bujqq, i)
                ycm__mcjvm += etdx__djko
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, ycm__mcjvm)
            for xxrq__qih in numba.parfors.parfor.internal_prange(n):
                apvu__agrzy, dxqis__vxjb, etdx__djko = get_split_view_index(
                    ecmrb__czcl, xxrq__qih, i)
                if apvu__agrzy == 0:
                    bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
                    zxdb__gff = get_split_view_data_ptr(ecmrb__czcl, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr, xxrq__qih
                        )
                    zxdb__gff = get_split_view_data_ptr(ecmrb__czcl,
                        dxqis__vxjb)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    xxrq__qih, zxdb__gff, etdx__djko)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(ecmrb__czcl, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(ecmrb__czcl)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ecmrb__czcl, xxrq__qih) or not len(
                ecmrb__czcl[xxrq__qih]) > i >= -len(ecmrb__czcl[xxrq__qih]):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            else:
                out_arr[xxrq__qih] = ecmrb__czcl[xxrq__qih][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    jjyh__tqu = S_str.stype.data
    if (jjyh__tqu != string_array_split_view_type and jjyh__tqu !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        jjyh__tqu)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(man__yeln)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            else:
                qqbc__apmt = man__yeln[xxrq__qih]
                out_arr[xxrq__qih] = sep.join(qqbc__apmt)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_replace_dict_impl(S_str, pat, repl, n=-1, case=None, flags
            =0, regex=True):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(ecmrb__czcl, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            kafqx__rhz = re.compile(pat, flags)
            ivp__cme = len(ecmrb__czcl)
            out_arr = pre_alloc_string_array(ivp__cme, -1)
            for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
                if bodo.libs.array_kernels.isna(ecmrb__czcl, xxrq__qih):
                    out_arr[xxrq__qih] = ''
                    bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
                    continue
                out_arr[xxrq__qih] = kafqx__rhz.sub(repl, ecmrb__czcl[
                    xxrq__qih])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(ecmrb__czcl)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(ivp__cme, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(ecmrb__czcl, xxrq__qih):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
                continue
            out_arr[xxrq__qih] = ecmrb__czcl[xxrq__qih].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


@numba.njit
def series_match_regex(S, pat, case, flags, na):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_match(pat, case, flags, na)
    return out_arr


def is_regex_unsupported(pat):
    xgzhq__pwx = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(dph__pevh in pat) for dph__pevh in xgzhq__pwx])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    zxvmw__cdegv = re.IGNORECASE.value
    xenbt__saj = 'def impl(\n'
    xenbt__saj += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    xenbt__saj += '):\n'
    xenbt__saj += '  S = S_str._obj\n'
    xenbt__saj += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    xenbt__saj += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    xenbt__saj += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    xenbt__saj += '  l = len(arr)\n'
    xenbt__saj += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                xenbt__saj += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                xenbt__saj += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            xenbt__saj += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        xenbt__saj += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        xenbt__saj += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            xenbt__saj += '  upper_pat = pat.upper()\n'
        xenbt__saj += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        xenbt__saj += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        xenbt__saj += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        xenbt__saj += '      else: \n'
        if is_overload_true(case):
            xenbt__saj += '          out_arr[i] = pat in arr[i]\n'
        else:
            xenbt__saj += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    xenbt__saj += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wors__tgna = {}
    exec(xenbt__saj, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': zxvmw__cdegv, 'get_search_regex':
        get_search_regex}, wors__tgna)
    impl = wors__tgna['impl']
    return impl


@overload_method(SeriesStrMethodType, 'match', inline='always',
    no_unliteral=True)
def overload_str_method_match(S_str, pat, case=True, flags=0, na=np.nan):
    not_supported_arg_check('match', 'na', na, np.nan)
    str_arg_check('match', 'pat', pat)
    int_arg_check('match', 'flags', flags)
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.match(): 'case' argument should be a constant boolean")
    zxvmw__cdegv = re.IGNORECASE.value
    xenbt__saj = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    xenbt__saj += '        S = S_str._obj\n'
    xenbt__saj += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    xenbt__saj += '        l = len(arr)\n'
    xenbt__saj += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    xenbt__saj += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        xenbt__saj += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        xenbt__saj += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        xenbt__saj += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        xenbt__saj += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    xenbt__saj += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wors__tgna = {}
    exec(xenbt__saj, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': zxvmw__cdegv, 'get_search_regex':
        get_search_regex}, wors__tgna)
    impl = wors__tgna['impl']
    return impl


@overload_method(SeriesStrMethodType, 'cat', no_unliteral=True)
def overload_str_method_cat(S_str, others=None, sep=None, na_rep=None, join
    ='left'):
    if not isinstance(others, DataFrameType):
        raise_bodo_error(
            "Series.str.cat(): 'others' must be a DataFrame currently")
    if not is_overload_none(sep):
        str_arg_check('cat', 'sep', sep)
    if not is_overload_constant_str(join) or get_overload_const_str(join
        ) != 'left':
        raise_bodo_error("Series.str.cat(): 'join' not supported yet")
    xenbt__saj = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    xenbt__saj += '  S = S_str._obj\n'
    xenbt__saj += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    xenbt__saj += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    xenbt__saj += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    xenbt__saj += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        xenbt__saj += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(bpwk__ykr == bodo
        .dict_str_arr_type for bpwk__ykr in others.data):
        ewgds__artdd = ', '.join(f'data{i}' for i in range(len(others.columns))
            )
        xenbt__saj += f"""  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {ewgds__artdd}), sep)
"""
    else:
        pywf__zolu = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        xenbt__saj += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        xenbt__saj += '  numba.parfors.parfor.init_prange()\n'
        xenbt__saj += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        xenbt__saj += f'      if {pywf__zolu}:\n'
        xenbt__saj += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        xenbt__saj += '          continue\n'
        vptxf__hsdrm = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range
            (len(others.columns))])
        ltkcl__lpym = "''" if is_overload_none(sep) else 'sep'
        xenbt__saj += (
            f'      out_arr[i] = {ltkcl__lpym}.join([{vptxf__hsdrm}])\n')
    xenbt__saj += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wors__tgna = {}
    exec(xenbt__saj, {'bodo': bodo, 'numba': numba}, wors__tgna)
    impl = wors__tgna['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(ecmrb__czcl, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        kafqx__rhz = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(ivp__cme, np.int64)
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(kafqx__rhz, man__yeln[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_find_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(ecmrb__czcl, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(ivp__cme, np.int64)
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_rfind_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(ecmrb__czcl, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(ivp__cme, np.int64)
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'index', inline='always',
    no_unliteral=True)
def overload_str_method_index(S_str, sub, start=0, end=None):
    str_arg_check('index', 'sub', sub)
    int_arg_check('index', 'start', start)
    if not is_overload_none(end):
        int_arg_check('index', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_index_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_index(ecmrb__czcl, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_index_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(ivp__cme, np.int64)
        numba.parfors.parfor.init_prange()
        lgeo__aaw = False
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].find(sub, start, end)
                if out_arr[i] == -1:
                    lgeo__aaw = True
        mip__wekr = 'substring not found' if lgeo__aaw else ''
        synchronize_error_njit('ValueError', mip__wekr)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'rindex', inline='always',
    no_unliteral=True)
def overload_str_method_rindex(S_str, sub, start=0, end=None):
    str_arg_check('rindex', 'sub', sub)
    int_arg_check('rindex', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rindex', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_rindex_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rindex(ecmrb__czcl, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_rindex_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(ivp__cme, np.int64)
        numba.parfors.parfor.init_prange()
        lgeo__aaw = False
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].rindex(sub, start, end)
                if out_arr[i] == -1:
                    lgeo__aaw = True
        mip__wekr = 'substring not found' if lgeo__aaw else ''
        synchronize_error_njit('ValueError', mip__wekr)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            else:
                if stop is not None:
                    zph__gwp = man__yeln[xxrq__qih][stop:]
                else:
                    zph__gwp = ''
                out_arr[xxrq__qih] = man__yeln[xxrq__qih][:start
                    ] + repl + zph__gwp
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
                itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
                xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(ecmrb__czcl,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    itxu__fjzr, xyrc__uqrdw)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            ivp__cme = len(man__yeln)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1
                )
            for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
                if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                    bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
                else:
                    out_arr[xxrq__qih] = man__yeln[xxrq__qih] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return impl
    elif is_overload_constant_list(repeats):
        bjg__qjgel = get_overload_const_list(repeats)
        xnak__lsjh = all([isinstance(vakq__vcx, int) for vakq__vcx in
            bjg__qjgel])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        xnak__lsjh = True
    else:
        xnak__lsjh = False
    if xnak__lsjh:

        def impl(S_str, repeats):
            S = S_str._obj
            man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            fahs__iwaig = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            ivp__cme = len(man__yeln)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1
                )
            for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
                if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                    bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
                else:
                    out_arr[xxrq__qih] = man__yeln[xxrq__qih] * fahs__iwaig[
                        xxrq__qih]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    xenbt__saj = f"""def dict_impl(S_str, width, fillchar=' '):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr, width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
def impl(S_str, width, fillchar=' '):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    numba.parfors.parfor.init_prange()
    l = len(str_arr)
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
    for j in numba.parfors.parfor.internal_prange(l):
        if bodo.libs.array_kernels.isna(str_arr, j):
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}(width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    wors__tgna = {}
    hhzt__ftba = {'bodo': bodo, 'numba': numba}
    exec(xenbt__saj, hhzt__ftba, wors__tgna)
    impl = wors__tgna['impl']
    phsrs__pjyyd = wors__tgna['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return phsrs__pjyyd
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for auzno__gvw in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(auzno__gvw)
        overload_method(SeriesStrMethodType, auzno__gvw, inline='always',
            no_unliteral=True)(impl)


_install_ljust_rjust_center()


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_pad_dict_impl(S_str, width, side='left', fillchar=' '):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(ecmrb__czcl,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(ecmrb__czcl,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(ecmrb__czcl,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            elif side == 'left':
                out_arr[xxrq__qih] = man__yeln[xxrq__qih].rjust(width, fillchar
                    )
            elif side == 'right':
                out_arr[xxrq__qih] = man__yeln[xxrq__qih].ljust(width, fillchar
                    )
            elif side == 'both':
                out_arr[xxrq__qih] = man__yeln[xxrq__qih].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(ecmrb__czcl, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            else:
                out_arr[xxrq__qih] = man__yeln[xxrq__qih].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_slice_dict_impl(S_str, start=None, stop=None, step=None):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(ecmrb__czcl, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(ivp__cme, -1)
        for xxrq__qih in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, xxrq__qih):
                out_arr[xxrq__qih] = ''
                bodo.libs.array_kernels.setna(out_arr, xxrq__qih)
            else:
                out_arr[xxrq__qih] = man__yeln[xxrq__qih][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(ecmrb__czcl,
                pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ivp__cme)
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
            itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
            xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(ecmrb__czcl, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                itxu__fjzr, xyrc__uqrdw)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        man__yeln = bodo.hiframes.pd_series_ext.get_series_data(S)
        xyrc__uqrdw = bodo.hiframes.pd_series_ext.get_series_name(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        ivp__cme = len(man__yeln)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ivp__cme)
        for i in numba.parfors.parfor.internal_prange(ivp__cme):
            if bodo.libs.array_kernels.isna(man__yeln, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = man__yeln[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, itxu__fjzr,
            xyrc__uqrdw)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    bzbm__xbr, regex = _get_column_names_from_regex(pat, flags, 'extract')
    nsjen__hyki = len(bzbm__xbr)
    if S_str.stype.data == bodo.dict_str_arr_type:
        xenbt__saj = 'def impl(S_str, pat, flags=0, expand=True):\n'
        xenbt__saj += '  S = S_str._obj\n'
        xenbt__saj += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        xenbt__saj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        xenbt__saj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        xenbt__saj += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {nsjen__hyki})
"""
        for i in range(nsjen__hyki):
            xenbt__saj += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        xenbt__saj = 'def impl(S_str, pat, flags=0, expand=True):\n'
        xenbt__saj += '  regex = re.compile(pat, flags=flags)\n'
        xenbt__saj += '  S = S_str._obj\n'
        xenbt__saj += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        xenbt__saj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        xenbt__saj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        xenbt__saj += '  numba.parfors.parfor.init_prange()\n'
        xenbt__saj += '  n = len(str_arr)\n'
        for i in range(nsjen__hyki):
            xenbt__saj += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        xenbt__saj += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        xenbt__saj += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(nsjen__hyki):
            xenbt__saj += "          out_arr_{}[j] = ''\n".format(i)
            xenbt__saj += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        xenbt__saj += '      else:\n'
        xenbt__saj += '          m = regex.search(str_arr[j])\n'
        xenbt__saj += '          if m:\n'
        xenbt__saj += '            g = m.groups()\n'
        for i in range(nsjen__hyki):
            xenbt__saj += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        xenbt__saj += '          else:\n'
        for i in range(nsjen__hyki):
            xenbt__saj += "            out_arr_{}[j] = ''\n".format(i)
            xenbt__saj += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        xyrc__uqrdw = "'{}'".format(list(regex.groupindex.keys()).pop()
            ) if len(regex.groupindex.keys()) > 0 else 'name'
        xenbt__saj += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(xyrc__uqrdw))
        wors__tgna = {}
        exec(xenbt__saj, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, wors__tgna)
        impl = wors__tgna['impl']
        return impl
    zdkog__ocb = ', '.join('out_arr_{}'.format(i) for i in range(nsjen__hyki))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(xenbt__saj, bzbm__xbr,
        zdkog__ocb, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    bzbm__xbr, xkrte__aja = _get_column_names_from_regex(pat, flags,
        'extractall')
    nsjen__hyki = len(bzbm__xbr)
    hla__dun = isinstance(S_str.stype.index, StringIndexType)
    txqg__bsne = nsjen__hyki > 1
    jeez__wavf = '_multi' if txqg__bsne else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        xenbt__saj = 'def impl(S_str, pat, flags=0):\n'
        xenbt__saj += '  S = S_str._obj\n'
        xenbt__saj += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        xenbt__saj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        xenbt__saj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        xenbt__saj += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        xenbt__saj += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        xenbt__saj += '  regex = re.compile(pat, flags=flags)\n'
        xenbt__saj += '  out_ind_arr, out_match_arr, out_arr_list = '
        xenbt__saj += f'bodo.libs.dict_arr_ext.str_extractall{jeez__wavf}(\n'
        xenbt__saj += f'arr, regex, {nsjen__hyki}, index_arr)\n'
        for i in range(nsjen__hyki):
            xenbt__saj += f'  out_arr_{i} = out_arr_list[{i}]\n'
        xenbt__saj += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        xenbt__saj += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        xenbt__saj = 'def impl(S_str, pat, flags=0):\n'
        xenbt__saj += '  regex = re.compile(pat, flags=flags)\n'
        xenbt__saj += '  S = S_str._obj\n'
        xenbt__saj += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        xenbt__saj += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        xenbt__saj += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        xenbt__saj += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        xenbt__saj += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        xenbt__saj += '  numba.parfors.parfor.init_prange()\n'
        xenbt__saj += '  n = len(str_arr)\n'
        xenbt__saj += '  out_n_l = [0]\n'
        for i in range(nsjen__hyki):
            xenbt__saj += '  num_chars_{} = 0\n'.format(i)
        if hla__dun:
            xenbt__saj += '  index_num_chars = 0\n'
        xenbt__saj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if hla__dun:
            xenbt__saj += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        xenbt__saj += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        xenbt__saj += '          continue\n'
        xenbt__saj += '      m = regex.findall(str_arr[i])\n'
        xenbt__saj += '      out_n_l[0] += len(m)\n'
        for i in range(nsjen__hyki):
            xenbt__saj += '      l_{} = 0\n'.format(i)
        xenbt__saj += '      for s in m:\n'
        for i in range(nsjen__hyki):
            xenbt__saj += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if nsjen__hyki > 1 else '')
        for i in range(nsjen__hyki):
            xenbt__saj += '      num_chars_{0} += l_{0}\n'.format(i)
        xenbt__saj += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(nsjen__hyki):
            xenbt__saj += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if hla__dun:
            xenbt__saj += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            xenbt__saj += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        xenbt__saj += '  out_match_arr = np.empty(out_n, np.int64)\n'
        xenbt__saj += '  out_ind = 0\n'
        xenbt__saj += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        xenbt__saj += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        xenbt__saj += '          continue\n'
        xenbt__saj += '      m = regex.findall(str_arr[j])\n'
        xenbt__saj += '      for k, s in enumerate(m):\n'
        for i in range(nsjen__hyki):
            xenbt__saj += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if nsjen__hyki > 1 else ''))
        xenbt__saj += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        xenbt__saj += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        xenbt__saj += '        out_ind += 1\n'
        xenbt__saj += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        xenbt__saj += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    zdkog__ocb = ', '.join('out_arr_{}'.format(i) for i in range(nsjen__hyki))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(xenbt__saj, bzbm__xbr,
        zdkog__ocb, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    eow__qrx = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    bzbm__xbr = [eow__qrx.get(1 + i, i) for i in range(regex.groups)]
    return bzbm__xbr, regex


def create_str2str_methods_overload(func_name):
    zxkww__jsp = func_name in ['lstrip', 'rstrip', 'strip']
    xenbt__saj = f"""def f({'S_str, to_strip=None' if zxkww__jsp else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if zxkww__jsp else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if zxkww__jsp else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    xenbt__saj += f"""def _dict_impl({'S_str, to_strip=None' if zxkww__jsp else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if zxkww__jsp else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    wors__tgna = {}
    exec(xenbt__saj, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo
        .libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, wors__tgna)
    bib__onydw = wors__tgna['f']
    jjiw__lsu = wors__tgna['_dict_impl']
    if zxkww__jsp:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return jjiw__lsu
            return bib__onydw
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return jjiw__lsu
            return bib__onydw
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    xenbt__saj = 'def dict_impl(S_str):\n'
    xenbt__saj += '    S = S_str._obj\n'
    xenbt__saj += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    xenbt__saj += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    xenbt__saj += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    xenbt__saj += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    xenbt__saj += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    xenbt__saj += 'def impl(S_str):\n'
    xenbt__saj += '    S = S_str._obj\n'
    xenbt__saj += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    xenbt__saj += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    xenbt__saj += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    xenbt__saj += '    numba.parfors.parfor.init_prange()\n'
    xenbt__saj += '    l = len(str_arr)\n'
    xenbt__saj += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    xenbt__saj += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    xenbt__saj += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    xenbt__saj += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    xenbt__saj += '        else:\n'
    xenbt__saj += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'.
        format(func_name))
    xenbt__saj += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    xenbt__saj += '      out_arr,index, name)\n'
    wors__tgna = {}
    exec(xenbt__saj, {'bodo': bodo, 'numba': numba, 'np': np}, wors__tgna)
    impl = wors__tgna['impl']
    phsrs__pjyyd = wors__tgna['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return phsrs__pjyyd
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for phpq__uduey in bodo.hiframes.pd_series_ext.str2str_methods:
        rtju__sso = create_str2str_methods_overload(phpq__uduey)
        overload_method(SeriesStrMethodType, phpq__uduey, inline='always',
            no_unliteral=True)(rtju__sso)


def _install_str2bool_methods():
    for phpq__uduey in bodo.hiframes.pd_series_ext.str2bool_methods:
        rtju__sso = create_str2bool_methods_overload(phpq__uduey)
        overload_method(SeriesStrMethodType, phpq__uduey, inline='always',
            no_unliteral=True)(rtju__sso)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        xyrc__uqrdw = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(xyrc__uqrdw)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ngjv__viqv = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, ngjv__viqv)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        pgfx__wxh, = args
        urtjg__nuu = signature.return_type
        dtxj__zeb = cgutils.create_struct_proxy(urtjg__nuu)(context, builder)
        dtxj__zeb.obj = pgfx__wxh
        context.nrt.incref(builder, signature.args[0], pgfx__wxh)
        return dtxj__zeb._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        ecmrb__czcl = bodo.hiframes.pd_series_ext.get_series_data(S)
        itxu__fjzr = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyrc__uqrdw = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(ecmrb__czcl),
            itxu__fjzr, xyrc__uqrdw)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for htjg__tew in unsupported_cat_attrs:
        vet__gvcqn = 'Series.cat.' + htjg__tew
        overload_attribute(SeriesCatMethodType, htjg__tew)(
            create_unsupported_overload(vet__gvcqn))
    for guxhc__zrp in unsupported_cat_methods:
        vet__gvcqn = 'Series.cat.' + guxhc__zrp
        overload_method(SeriesCatMethodType, guxhc__zrp)(
            create_unsupported_overload(vet__gvcqn))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for guxhc__zrp in unsupported_str_methods:
        vet__gvcqn = 'Series.str.' + guxhc__zrp
        overload_method(SeriesStrMethodType, guxhc__zrp)(
            create_unsupported_overload(vet__gvcqn))


_install_strseries_unsupported()
