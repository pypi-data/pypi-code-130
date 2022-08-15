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
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error
from bodo.utils.utils import synchronize_error_njit


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        uht__dxkq = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(uht__dxkq)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        jero__ipt = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, jero__ipt)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gcezz__xtl, = args
        irpk__ifj = signature.return_type
        nle__rxqkq = cgutils.create_struct_proxy(irpk__ifj)(context, builder)
        nle__rxqkq.obj = gcezz__xtl
        context.nrt.incref(builder, signature.args[0], gcezz__xtl)
        return nle__rxqkq._getvalue()
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
        string_array_split_view_type or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_len_dict_impl(S_str):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(xrqk__ggq)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(xrqk__ggq, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(xrqk__ggq,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(xrqk__ggq, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    ejev__jmi = S_str.stype.data
    if (ejev__jmi != string_array_split_view_type and not is_str_arr_type(
        ejev__jmi)) and not isinstance(ejev__jmi, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(ejev__jmi, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(xrqk__ggq, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_get_array_impl
    if ejev__jmi == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(xrqk__ggq)
            emh__kwjln = 0
            for lwksc__biehv in numba.parfors.parfor.internal_prange(n):
                yfubh__jaei, yfubh__jaei, jykqq__hur = get_split_view_index(
                    xrqk__ggq, lwksc__biehv, i)
                emh__kwjln += jykqq__hur
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, emh__kwjln)
            for vpeq__nhed in numba.parfors.parfor.internal_prange(n):
                dco__lcsqv, oemad__qwvm, jykqq__hur = get_split_view_index(
                    xrqk__ggq, vpeq__nhed, i)
                if dco__lcsqv == 0:
                    bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
                    czgvp__oyx = get_split_view_data_ptr(xrqk__ggq, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        vpeq__nhed)
                    czgvp__oyx = get_split_view_data_ptr(xrqk__ggq, oemad__qwvm
                        )
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    vpeq__nhed, czgvp__oyx, jykqq__hur)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(xrqk__ggq, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(xrqk__ggq)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(xrqk__ggq, vpeq__nhed) or not len(
                xrqk__ggq[vpeq__nhed]) > i >= -len(xrqk__ggq[vpeq__nhed]):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            else:
                out_arr[vpeq__nhed] = xrqk__ggq[vpeq__nhed][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    ejev__jmi = S_str.stype.data
    if (ejev__jmi != string_array_split_view_type and ejev__jmi !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        ejev__jmi)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(cdrcr__qhyl)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            else:
                gqih__heat = cdrcr__qhyl[vpeq__nhed]
                out_arr[vpeq__nhed] = sep.join(gqih__heat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(xrqk__ggq, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            xwro__pzrit = re.compile(pat, flags)
            lydr__lyw = len(xrqk__ggq)
            out_arr = pre_alloc_string_array(lydr__lyw, -1)
            for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
                if bodo.libs.array_kernels.isna(xrqk__ggq, vpeq__nhed):
                    out_arr[vpeq__nhed] = ''
                    bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
                    continue
                out_arr[vpeq__nhed] = xwro__pzrit.sub(repl, xrqk__ggq[
                    vpeq__nhed])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(xrqk__ggq)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(lydr__lyw, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(xrqk__ggq, vpeq__nhed):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
                continue
            out_arr[vpeq__nhed] = xrqk__ggq[vpeq__nhed].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
    ewt__tmjvx = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(gvgov__qbms in pat) for gvgov__qbms in ewt__tmjvx])
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
    valg__zhumn = re.IGNORECASE.value
    ibq__mqqi = 'def impl(\n'
    ibq__mqqi += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    ibq__mqqi += '):\n'
    ibq__mqqi += '  S = S_str._obj\n'
    ibq__mqqi += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ibq__mqqi += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ibq__mqqi += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ibq__mqqi += '  l = len(arr)\n'
    ibq__mqqi += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                ibq__mqqi += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                ibq__mqqi += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            ibq__mqqi += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        ibq__mqqi += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        ibq__mqqi += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            ibq__mqqi += '  upper_pat = pat.upper()\n'
        ibq__mqqi += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        ibq__mqqi += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        ibq__mqqi += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        ibq__mqqi += '      else: \n'
        if is_overload_true(case):
            ibq__mqqi += '          out_arr[i] = pat in arr[i]\n'
        else:
            ibq__mqqi += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    ibq__mqqi += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tym__jotp = {}
    exec(ibq__mqqi, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': valg__zhumn, 'get_search_regex':
        get_search_regex}, tym__jotp)
    impl = tym__jotp['impl']
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
    valg__zhumn = re.IGNORECASE.value
    ibq__mqqi = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    ibq__mqqi += '        S = S_str._obj\n'
    ibq__mqqi += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ibq__mqqi += '        l = len(arr)\n'
    ibq__mqqi += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ibq__mqqi += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        ibq__mqqi += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        ibq__mqqi += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        ibq__mqqi += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        ibq__mqqi += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    ibq__mqqi += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tym__jotp = {}
    exec(ibq__mqqi, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': valg__zhumn, 'get_search_regex':
        get_search_regex}, tym__jotp)
    impl = tym__jotp['impl']
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
    ibq__mqqi = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    ibq__mqqi += '  S = S_str._obj\n'
    ibq__mqqi += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ibq__mqqi += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ibq__mqqi += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ibq__mqqi += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        ibq__mqqi += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})\n'
            )
    if S_str.stype.data == bodo.dict_str_arr_type and all(ktc__leum == bodo
        .dict_str_arr_type for ktc__leum in others.data):
        ujdn__bbxfb = ', '.join(f'data{i}' for i in range(len(others.columns)))
        ibq__mqqi += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {ujdn__bbxfb}), sep)\n'
            )
    else:
        kogt__hamkt = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        ibq__mqqi += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        ibq__mqqi += '  numba.parfors.parfor.init_prange()\n'
        ibq__mqqi += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        ibq__mqqi += f'      if {kogt__hamkt}:\n'
        ibq__mqqi += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        ibq__mqqi += '          continue\n'
        zdlr__hqa = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        aqpd__qxefv = "''" if is_overload_none(sep) else 'sep'
        ibq__mqqi += f'      out_arr[i] = {aqpd__qxefv}.join([{zdlr__hqa}])\n'
    ibq__mqqi += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tym__jotp = {}
    exec(ibq__mqqi, {'bodo': bodo, 'numba': numba}, tym__jotp)
    impl = tym__jotp['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(xrqk__ggq, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        xwro__pzrit = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(lydr__lyw, np.int64)
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(xwro__pzrit, cdrcr__qhyl[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(xrqk__ggq, sub, start,
                end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(lydr__lyw, np.int64)
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(xrqk__ggq, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(lydr__lyw, np.int64)
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_index(xrqk__ggq, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_index_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(lydr__lyw, np.int64)
        numba.parfors.parfor.init_prange()
        gggw__cddxb = False
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].find(sub, start, end)
                if out_arr[i] == -1:
                    gggw__cddxb = True
        wukyd__rhu = 'substring not found' if gggw__cddxb else ''
        synchronize_error_njit('ValueError', wukyd__rhu)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rindex(xrqk__ggq, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_rindex_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(lydr__lyw, np.int64)
        numba.parfors.parfor.init_prange()
        gggw__cddxb = False
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].rindex(sub, start, end)
                if out_arr[i] == -1:
                    gggw__cddxb = True
        wukyd__rhu = 'substring not found' if gggw__cddxb else ''
        synchronize_error_njit('ValueError', wukyd__rhu)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            else:
                if stop is not None:
                    pfe__glfxh = cdrcr__qhyl[vpeq__nhed][stop:]
                else:
                    pfe__glfxh = ''
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed][:start
                    ] + repl + pfe__glfxh
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
                flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
                uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(xrqk__ggq,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    flyv__jsfe, uht__dxkq)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            lydr__lyw = len(cdrcr__qhyl)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw,
                -1)
            for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
                if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                    bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
                else:
                    out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return impl
    elif is_overload_constant_list(repeats):
        kvpdk__cfdb = get_overload_const_list(repeats)
        pqat__hpg = all([isinstance(vwbhp__ltlbn, int) for vwbhp__ltlbn in
            kvpdk__cfdb])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        pqat__hpg = True
    else:
        pqat__hpg = False
    if pqat__hpg:

        def impl(S_str, repeats):
            S = S_str._obj
            cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            eca__mjy = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            lydr__lyw = len(cdrcr__qhyl)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw,
                -1)
            for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
                if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                    bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
                else:
                    out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed] * eca__mjy[
                        vpeq__nhed]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    ibq__mqqi = f"""def dict_impl(S_str, width, fillchar=' '):
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
    tym__jotp = {}
    wlnmy__apd = {'bodo': bodo, 'numba': numba}
    exec(ibq__mqqi, wlnmy__apd, tym__jotp)
    impl = tym__jotp['impl']
    sfkc__hxa = tym__jotp['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return sfkc__hxa
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for qsue__vvs in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(qsue__vvs)
        overload_method(SeriesStrMethodType, qsue__vvs, inline='always',
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(xrqk__ggq, width,
                    fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(xrqk__ggq, width,
                    fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(xrqk__ggq,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            elif side == 'left':
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(xrqk__ggq, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            else:
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(xrqk__ggq, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(lydr__lyw, -1)
        for vpeq__nhed in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, vpeq__nhed):
                out_arr[vpeq__nhed] = ''
                bodo.libs.array_kernels.setna(out_arr, vpeq__nhed)
            else:
                out_arr[vpeq__nhed] = cdrcr__qhyl[vpeq__nhed][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(xrqk__ggq, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(lydr__lyw)
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
            flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
            uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(xrqk__ggq, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                flyv__jsfe, uht__dxkq)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        cdrcr__qhyl = bodo.hiframes.pd_series_ext.get_series_data(S)
        uht__dxkq = bodo.hiframes.pd_series_ext.get_series_name(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        lydr__lyw = len(cdrcr__qhyl)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(lydr__lyw)
        for i in numba.parfors.parfor.internal_prange(lydr__lyw):
            if bodo.libs.array_kernels.isna(cdrcr__qhyl, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = cdrcr__qhyl[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, flyv__jsfe,
            uht__dxkq)
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
    fems__cxga, regex = _get_column_names_from_regex(pat, flags, 'extract')
    nab__gth = len(fems__cxga)
    if S_str.stype.data == bodo.dict_str_arr_type:
        ibq__mqqi = 'def impl(S_str, pat, flags=0, expand=True):\n'
        ibq__mqqi += '  S = S_str._obj\n'
        ibq__mqqi += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        ibq__mqqi += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ibq__mqqi += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ibq__mqqi += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {nab__gth})
"""
        for i in range(nab__gth):
            ibq__mqqi += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        ibq__mqqi = 'def impl(S_str, pat, flags=0, expand=True):\n'
        ibq__mqqi += '  regex = re.compile(pat, flags=flags)\n'
        ibq__mqqi += '  S = S_str._obj\n'
        ibq__mqqi += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ibq__mqqi += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ibq__mqqi += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ibq__mqqi += '  numba.parfors.parfor.init_prange()\n'
        ibq__mqqi += '  n = len(str_arr)\n'
        for i in range(nab__gth):
            ibq__mqqi += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        ibq__mqqi += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        ibq__mqqi += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(nab__gth):
            ibq__mqqi += "          out_arr_{}[j] = ''\n".format(i)
            ibq__mqqi += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        ibq__mqqi += '      else:\n'
        ibq__mqqi += '          m = regex.search(str_arr[j])\n'
        ibq__mqqi += '          if m:\n'
        ibq__mqqi += '            g = m.groups()\n'
        for i in range(nab__gth):
            ibq__mqqi += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        ibq__mqqi += '          else:\n'
        for i in range(nab__gth):
            ibq__mqqi += "            out_arr_{}[j] = ''\n".format(i)
            ibq__mqqi += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        uht__dxkq = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        ibq__mqqi += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(uht__dxkq))
        tym__jotp = {}
        exec(ibq__mqqi, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, tym__jotp)
        impl = tym__jotp['impl']
        return impl
    wdps__zlmoq = ', '.join('out_arr_{}'.format(i) for i in range(nab__gth))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ibq__mqqi, fems__cxga,
        wdps__zlmoq, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    fems__cxga, yfubh__jaei = _get_column_names_from_regex(pat, flags,
        'extractall')
    nab__gth = len(fems__cxga)
    rrsq__pojxh = isinstance(S_str.stype.index, StringIndexType)
    eobff__etkrr = nab__gth > 1
    jccf__bzobu = '_multi' if eobff__etkrr else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        ibq__mqqi = 'def impl(S_str, pat, flags=0):\n'
        ibq__mqqi += '  S = S_str._obj\n'
        ibq__mqqi += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        ibq__mqqi += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ibq__mqqi += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ibq__mqqi += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        ibq__mqqi += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        ibq__mqqi += '  regex = re.compile(pat, flags=flags)\n'
        ibq__mqqi += '  out_ind_arr, out_match_arr, out_arr_list = '
        ibq__mqqi += f'bodo.libs.dict_arr_ext.str_extractall{jccf__bzobu}(\n'
        ibq__mqqi += f'arr, regex, {nab__gth}, index_arr)\n'
        for i in range(nab__gth):
            ibq__mqqi += f'  out_arr_{i} = out_arr_list[{i}]\n'
        ibq__mqqi += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        ibq__mqqi += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        ibq__mqqi = 'def impl(S_str, pat, flags=0):\n'
        ibq__mqqi += '  regex = re.compile(pat, flags=flags)\n'
        ibq__mqqi += '  S = S_str._obj\n'
        ibq__mqqi += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ibq__mqqi += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ibq__mqqi += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ibq__mqqi += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        ibq__mqqi += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        ibq__mqqi += '  numba.parfors.parfor.init_prange()\n'
        ibq__mqqi += '  n = len(str_arr)\n'
        ibq__mqqi += '  out_n_l = [0]\n'
        for i in range(nab__gth):
            ibq__mqqi += '  num_chars_{} = 0\n'.format(i)
        if rrsq__pojxh:
            ibq__mqqi += '  index_num_chars = 0\n'
        ibq__mqqi += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if rrsq__pojxh:
            ibq__mqqi += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        ibq__mqqi += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        ibq__mqqi += '          continue\n'
        ibq__mqqi += '      m = regex.findall(str_arr[i])\n'
        ibq__mqqi += '      out_n_l[0] += len(m)\n'
        for i in range(nab__gth):
            ibq__mqqi += '      l_{} = 0\n'.format(i)
        ibq__mqqi += '      for s in m:\n'
        for i in range(nab__gth):
            ibq__mqqi += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if nab__gth > 1 else '')
        for i in range(nab__gth):
            ibq__mqqi += '      num_chars_{0} += l_{0}\n'.format(i)
        ibq__mqqi += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(nab__gth):
            ibq__mqqi += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if rrsq__pojxh:
            ibq__mqqi += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            ibq__mqqi += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        ibq__mqqi += '  out_match_arr = np.empty(out_n, np.int64)\n'
        ibq__mqqi += '  out_ind = 0\n'
        ibq__mqqi += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        ibq__mqqi += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        ibq__mqqi += '          continue\n'
        ibq__mqqi += '      m = regex.findall(str_arr[j])\n'
        ibq__mqqi += '      for k, s in enumerate(m):\n'
        for i in range(nab__gth):
            ibq__mqqi += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if nab__gth > 1 else ''))
        ibq__mqqi += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        ibq__mqqi += (
            '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
            )
        ibq__mqqi += '        out_ind += 1\n'
        ibq__mqqi += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        ibq__mqqi += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    wdps__zlmoq = ', '.join('out_arr_{}'.format(i) for i in range(nab__gth))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ibq__mqqi, fems__cxga,
        wdps__zlmoq, 'out_index', extra_globals={'get_utf8_size':
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
    lvjon__wdsn = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    fems__cxga = [lvjon__wdsn.get(1 + i, i) for i in range(regex.groups)]
    return fems__cxga, regex


def create_str2str_methods_overload(func_name):
    thay__jvch = func_name in ['lstrip', 'rstrip', 'strip']
    ibq__mqqi = f"""def f({'S_str, to_strip=None' if thay__jvch else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if thay__jvch else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if thay__jvch else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    ibq__mqqi += f"""def _dict_impl({'S_str, to_strip=None' if thay__jvch else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if thay__jvch else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    tym__jotp = {}
    exec(ibq__mqqi, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, tym__jotp)
    qoaqt__remqh = tym__jotp['f']
    sfp__zpjcc = tym__jotp['_dict_impl']
    if thay__jvch:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return sfp__zpjcc
            return qoaqt__remqh
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return sfp__zpjcc
            return qoaqt__remqh
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    ibq__mqqi = 'def dict_impl(S_str):\n'
    ibq__mqqi += '    S = S_str._obj\n'
    ibq__mqqi += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ibq__mqqi += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ibq__mqqi += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ibq__mqqi += f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n'
    ibq__mqqi += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ibq__mqqi += 'def impl(S_str):\n'
    ibq__mqqi += '    S = S_str._obj\n'
    ibq__mqqi += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ibq__mqqi += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ibq__mqqi += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ibq__mqqi += '    numba.parfors.parfor.init_prange()\n'
    ibq__mqqi += '    l = len(str_arr)\n'
    ibq__mqqi += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    ibq__mqqi += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    ibq__mqqi += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    ibq__mqqi += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    ibq__mqqi += '        else:\n'
    ibq__mqqi += '            out_arr[i] = np.bool_(str_arr[i].{}())\n'.format(
        func_name)
    ibq__mqqi += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    ibq__mqqi += '      out_arr,index, name)\n'
    tym__jotp = {}
    exec(ibq__mqqi, {'bodo': bodo, 'numba': numba, 'np': np}, tym__jotp)
    impl = tym__jotp['impl']
    sfkc__hxa = tym__jotp['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return sfkc__hxa
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for mkdkn__gtuz in bodo.hiframes.pd_series_ext.str2str_methods:
        ieugb__lwn = create_str2str_methods_overload(mkdkn__gtuz)
        overload_method(SeriesStrMethodType, mkdkn__gtuz, inline='always',
            no_unliteral=True)(ieugb__lwn)


def _install_str2bool_methods():
    for mkdkn__gtuz in bodo.hiframes.pd_series_ext.str2bool_methods:
        ieugb__lwn = create_str2bool_methods_overload(mkdkn__gtuz)
        overload_method(SeriesStrMethodType, mkdkn__gtuz, inline='always',
            no_unliteral=True)(ieugb__lwn)


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
        uht__dxkq = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(uht__dxkq)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        jero__ipt = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, jero__ipt)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        gcezz__xtl, = args
        psgd__befzq = signature.return_type
        xggi__rqrxw = cgutils.create_struct_proxy(psgd__befzq)(context, builder
            )
        xggi__rqrxw.obj = gcezz__xtl
        context.nrt.incref(builder, signature.args[0], gcezz__xtl)
        return xggi__rqrxw._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        xrqk__ggq = bodo.hiframes.pd_series_ext.get_series_data(S)
        flyv__jsfe = bodo.hiframes.pd_series_ext.get_series_index(S)
        uht__dxkq = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(xrqk__ggq),
            flyv__jsfe, uht__dxkq)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for vhgp__yoo in unsupported_cat_attrs:
        zze__yso = 'Series.cat.' + vhgp__yoo
        overload_attribute(SeriesCatMethodType, vhgp__yoo)(
            create_unsupported_overload(zze__yso))
    for jtlku__sogr in unsupported_cat_methods:
        zze__yso = 'Series.cat.' + jtlku__sogr
        overload_method(SeriesCatMethodType, jtlku__sogr)(
            create_unsupported_overload(zze__yso))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for jtlku__sogr in unsupported_str_methods:
        zze__yso = 'Series.str.' + jtlku__sogr
        overload_method(SeriesStrMethodType, jtlku__sogr)(
            create_unsupported_overload(zze__yso))


_install_strseries_unsupported()
