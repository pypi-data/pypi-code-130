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
        ikfus__lkp = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(ikfus__lkp)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        btjz__xpk = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, btjz__xpk)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        qli__ckhw, = args
        inecy__jwzf = signature.return_type
        yrffu__ygau = cgutils.create_struct_proxy(inecy__jwzf)(context, builder
            )
        yrffu__ygau.obj = qli__ckhw
        context.nrt.incref(builder, signature.args[0], qli__ckhw)
        return yrffu__ygau._getvalue()
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(uflr__dqeig)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(uflr__dqeig, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(uflr__dqeig,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(uflr__dqeig, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    tph__unjz = S_str.stype.data
    if (tph__unjz != string_array_split_view_type and not is_str_arr_type(
        tph__unjz)) and not isinstance(tph__unjz, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(tph__unjz, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(uflr__dqeig, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_get_array_impl
    if tph__unjz == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(uflr__dqeig)
            shvpc__mhbkh = 0
            for ofid__yrb in numba.parfors.parfor.internal_prange(n):
                khsph__rzymt, khsph__rzymt, xpgie__lwcvs = (
                    get_split_view_index(uflr__dqeig, ofid__yrb, i))
                shvpc__mhbkh += xpgie__lwcvs
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, shvpc__mhbkh)
            for cdxyz__erv in numba.parfors.parfor.internal_prange(n):
                jix__isoua, lmzot__ylfd, xpgie__lwcvs = get_split_view_index(
                    uflr__dqeig, cdxyz__erv, i)
                if jix__isoua == 0:
                    bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
                    rrnzc__nnc = get_split_view_data_ptr(uflr__dqeig, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        cdxyz__erv)
                    rrnzc__nnc = get_split_view_data_ptr(uflr__dqeig,
                        lmzot__ylfd)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    cdxyz__erv, rrnzc__nnc, xpgie__lwcvs)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(uflr__dqeig, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(uflr__dqeig)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(uflr__dqeig, cdxyz__erv
                ) or not len(uflr__dqeig[cdxyz__erv]) > i >= -len(uflr__dqeig
                [cdxyz__erv]):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            else:
                out_arr[cdxyz__erv] = uflr__dqeig[cdxyz__erv][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    tph__unjz = S_str.stype.data
    if (tph__unjz != string_array_split_view_type and tph__unjz !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        tph__unjz)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(orlyw__wabzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            else:
                veyt__nlz = orlyw__wabzg[cdxyz__erv]
                out_arr[cdxyz__erv] = sep.join(veyt__nlz)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(uflr__dqeig, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            enam__ubkr = re.compile(pat, flags)
            xxa__sxwaf = len(uflr__dqeig)
            out_arr = pre_alloc_string_array(xxa__sxwaf, -1)
            for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
                if bodo.libs.array_kernels.isna(uflr__dqeig, cdxyz__erv):
                    out_arr[cdxyz__erv] = ''
                    bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
                    continue
                out_arr[cdxyz__erv] = enam__ubkr.sub(repl, uflr__dqeig[
                    cdxyz__erv])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(uflr__dqeig)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(xxa__sxwaf, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(uflr__dqeig, cdxyz__erv):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
                continue
            out_arr[cdxyz__erv] = uflr__dqeig[cdxyz__erv].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
    yjgzv__qmjtb = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(zos__htvm in pat) for zos__htvm in yjgzv__qmjtb])
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
    jcfim__fkq = re.IGNORECASE.value
    tuij__qhn = 'def impl(\n'
    tuij__qhn += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    tuij__qhn += '):\n'
    tuij__qhn += '  S = S_str._obj\n'
    tuij__qhn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    tuij__qhn += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    tuij__qhn += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tuij__qhn += '  l = len(arr)\n'
    tuij__qhn += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                tuij__qhn += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                tuij__qhn += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            tuij__qhn += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        tuij__qhn += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        tuij__qhn += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            tuij__qhn += '  upper_pat = pat.upper()\n'
        tuij__qhn += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        tuij__qhn += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        tuij__qhn += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        tuij__qhn += '      else: \n'
        if is_overload_true(case):
            tuij__qhn += '          out_arr[i] = pat in arr[i]\n'
        else:
            tuij__qhn += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    tuij__qhn += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    sikl__byme = {}
    exec(tuij__qhn, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': jcfim__fkq, 'get_search_regex':
        get_search_regex}, sikl__byme)
    impl = sikl__byme['impl']
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
    jcfim__fkq = re.IGNORECASE.value
    tuij__qhn = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    tuij__qhn += '        S = S_str._obj\n'
    tuij__qhn += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tuij__qhn += '        l = len(arr)\n'
    tuij__qhn += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tuij__qhn += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        tuij__qhn += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        tuij__qhn += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        tuij__qhn += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        tuij__qhn += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    tuij__qhn += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    sikl__byme = {}
    exec(tuij__qhn, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': jcfim__fkq, 'get_search_regex':
        get_search_regex}, sikl__byme)
    impl = sikl__byme['impl']
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
    tuij__qhn = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    tuij__qhn += '  S = S_str._obj\n'
    tuij__qhn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    tuij__qhn += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    tuij__qhn += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tuij__qhn += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        tuij__qhn += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})\n'
            )
    if S_str.stype.data == bodo.dict_str_arr_type and all(wvig__cmr == bodo
        .dict_str_arr_type for wvig__cmr in others.data):
        hivw__ybijd = ', '.join(f'data{i}' for i in range(len(others.columns)))
        tuij__qhn += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {hivw__ybijd}), sep)\n'
            )
    else:
        lcus__wmkd = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        tuij__qhn += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        tuij__qhn += '  numba.parfors.parfor.init_prange()\n'
        tuij__qhn += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        tuij__qhn += f'      if {lcus__wmkd}:\n'
        tuij__qhn += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        tuij__qhn += '          continue\n'
        xkqmz__lbldu = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range
            (len(others.columns))])
        dzkxj__bsrg = "''" if is_overload_none(sep) else 'sep'
        tuij__qhn += (
            f'      out_arr[i] = {dzkxj__bsrg}.join([{xkqmz__lbldu}])\n')
    tuij__qhn += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    sikl__byme = {}
    exec(tuij__qhn, {'bodo': bodo, 'numba': numba}, sikl__byme)
    impl = sikl__byme['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(uflr__dqeig, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        enam__ubkr = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xxa__sxwaf, np.int64)
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(enam__ubkr, orlyw__wabzg[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(uflr__dqeig, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xxa__sxwaf, np.int64)
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(uflr__dqeig, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xxa__sxwaf, np.int64)
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_index(uflr__dqeig, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_index_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xxa__sxwaf, np.int64)
        numba.parfors.parfor.init_prange()
        kuu__oasz = False
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].find(sub, start, end)
                if out_arr[i] == -1:
                    kuu__oasz = True
        yamag__ldiom = 'substring not found' if kuu__oasz else ''
        synchronize_error_njit('ValueError', yamag__ldiom)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rindex(uflr__dqeig, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_rindex_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xxa__sxwaf, np.int64)
        numba.parfors.parfor.init_prange()
        kuu__oasz = False
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].rindex(sub, start, end)
                if out_arr[i] == -1:
                    kuu__oasz = True
        yamag__ldiom = 'substring not found' if kuu__oasz else ''
        synchronize_error_njit('ValueError', yamag__ldiom)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            else:
                if stop is not None:
                    pza__oubi = orlyw__wabzg[cdxyz__erv][stop:]
                else:
                    pza__oubi = ''
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv][:start
                    ] + repl + pza__oubi
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
                ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
                ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(uflr__dqeig,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    ehlrz__kresh, ikfus__lkp)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            xxa__sxwaf = len(orlyw__wabzg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf,
                -1)
            for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
                if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                    bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
                else:
                    out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return impl
    elif is_overload_constant_list(repeats):
        lyi__ydhqf = get_overload_const_list(repeats)
        xwly__avky = all([isinstance(hsmlr__zzpgr, int) for hsmlr__zzpgr in
            lyi__ydhqf])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        xwly__avky = True
    else:
        xwly__avky = False
    if xwly__avky:

        def impl(S_str, repeats):
            S = S_str._obj
            orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            yuy__gxabp = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            xxa__sxwaf = len(orlyw__wabzg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf,
                -1)
            for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
                if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                    bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
                else:
                    out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv
                        ] * yuy__gxabp[cdxyz__erv]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    tuij__qhn = f"""def dict_impl(S_str, width, fillchar=' '):
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
    sikl__byme = {}
    ryvii__wtwg = {'bodo': bodo, 'numba': numba}
    exec(tuij__qhn, ryvii__wtwg, sikl__byme)
    impl = sikl__byme['impl']
    fksus__sjoxn = sikl__byme['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return fksus__sjoxn
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for ujs__vyy in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(ujs__vyy)
        overload_method(SeriesStrMethodType, ujs__vyy, inline='always',
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(uflr__dqeig,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(uflr__dqeig,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(uflr__dqeig,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            elif side == 'left':
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(uflr__dqeig, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            else:
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(uflr__dqeig, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xxa__sxwaf, -1)
        for cdxyz__erv in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, cdxyz__erv):
                out_arr[cdxyz__erv] = ''
                bodo.libs.array_kernels.setna(out_arr, cdxyz__erv)
            else:
                out_arr[cdxyz__erv] = orlyw__wabzg[cdxyz__erv][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(uflr__dqeig,
                pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xxa__sxwaf)
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
            ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
            ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(uflr__dqeig, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ehlrz__kresh, ikfus__lkp)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        orlyw__wabzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ikfus__lkp = bodo.hiframes.pd_series_ext.get_series_name(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xxa__sxwaf = len(orlyw__wabzg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xxa__sxwaf)
        for i in numba.parfors.parfor.internal_prange(xxa__sxwaf):
            if bodo.libs.array_kernels.isna(orlyw__wabzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = orlyw__wabzg[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            ehlrz__kresh, ikfus__lkp)
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
    folpb__jiid, regex = _get_column_names_from_regex(pat, flags, 'extract')
    ppj__bwv = len(folpb__jiid)
    if S_str.stype.data == bodo.dict_str_arr_type:
        tuij__qhn = 'def impl(S_str, pat, flags=0, expand=True):\n'
        tuij__qhn += '  S = S_str._obj\n'
        tuij__qhn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        tuij__qhn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tuij__qhn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tuij__qhn += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {ppj__bwv})
"""
        for i in range(ppj__bwv):
            tuij__qhn += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        tuij__qhn = 'def impl(S_str, pat, flags=0, expand=True):\n'
        tuij__qhn += '  regex = re.compile(pat, flags=flags)\n'
        tuij__qhn += '  S = S_str._obj\n'
        tuij__qhn += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tuij__qhn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tuij__qhn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tuij__qhn += '  numba.parfors.parfor.init_prange()\n'
        tuij__qhn += '  n = len(str_arr)\n'
        for i in range(ppj__bwv):
            tuij__qhn += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        tuij__qhn += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        tuij__qhn += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(ppj__bwv):
            tuij__qhn += "          out_arr_{}[j] = ''\n".format(i)
            tuij__qhn += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        tuij__qhn += '      else:\n'
        tuij__qhn += '          m = regex.search(str_arr[j])\n'
        tuij__qhn += '          if m:\n'
        tuij__qhn += '            g = m.groups()\n'
        for i in range(ppj__bwv):
            tuij__qhn += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        tuij__qhn += '          else:\n'
        for i in range(ppj__bwv):
            tuij__qhn += "            out_arr_{}[j] = ''\n".format(i)
            tuij__qhn += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        ikfus__lkp = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        tuij__qhn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(ikfus__lkp))
        sikl__byme = {}
        exec(tuij__qhn, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, sikl__byme)
        impl = sikl__byme['impl']
        return impl
    obp__chav = ', '.join('out_arr_{}'.format(i) for i in range(ppj__bwv))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(tuij__qhn, folpb__jiid,
        obp__chav, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    folpb__jiid, khsph__rzymt = _get_column_names_from_regex(pat, flags,
        'extractall')
    ppj__bwv = len(folpb__jiid)
    xuvo__yim = isinstance(S_str.stype.index, StringIndexType)
    llb__mdid = ppj__bwv > 1
    ejp__zaoe = '_multi' if llb__mdid else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        tuij__qhn = 'def impl(S_str, pat, flags=0):\n'
        tuij__qhn += '  S = S_str._obj\n'
        tuij__qhn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        tuij__qhn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tuij__qhn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tuij__qhn += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        tuij__qhn += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        tuij__qhn += '  regex = re.compile(pat, flags=flags)\n'
        tuij__qhn += '  out_ind_arr, out_match_arr, out_arr_list = '
        tuij__qhn += f'bodo.libs.dict_arr_ext.str_extractall{ejp__zaoe}(\n'
        tuij__qhn += f'arr, regex, {ppj__bwv}, index_arr)\n'
        for i in range(ppj__bwv):
            tuij__qhn += f'  out_arr_{i} = out_arr_list[{i}]\n'
        tuij__qhn += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        tuij__qhn += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        tuij__qhn = 'def impl(S_str, pat, flags=0):\n'
        tuij__qhn += '  regex = re.compile(pat, flags=flags)\n'
        tuij__qhn += '  S = S_str._obj\n'
        tuij__qhn += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tuij__qhn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tuij__qhn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tuij__qhn += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        tuij__qhn += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        tuij__qhn += '  numba.parfors.parfor.init_prange()\n'
        tuij__qhn += '  n = len(str_arr)\n'
        tuij__qhn += '  out_n_l = [0]\n'
        for i in range(ppj__bwv):
            tuij__qhn += '  num_chars_{} = 0\n'.format(i)
        if xuvo__yim:
            tuij__qhn += '  index_num_chars = 0\n'
        tuij__qhn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if xuvo__yim:
            tuij__qhn += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        tuij__qhn += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        tuij__qhn += '          continue\n'
        tuij__qhn += '      m = regex.findall(str_arr[i])\n'
        tuij__qhn += '      out_n_l[0] += len(m)\n'
        for i in range(ppj__bwv):
            tuij__qhn += '      l_{} = 0\n'.format(i)
        tuij__qhn += '      for s in m:\n'
        for i in range(ppj__bwv):
            tuij__qhn += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if ppj__bwv > 1 else '')
        for i in range(ppj__bwv):
            tuij__qhn += '      num_chars_{0} += l_{0}\n'.format(i)
        tuij__qhn += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(ppj__bwv):
            tuij__qhn += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if xuvo__yim:
            tuij__qhn += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            tuij__qhn += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        tuij__qhn += '  out_match_arr = np.empty(out_n, np.int64)\n'
        tuij__qhn += '  out_ind = 0\n'
        tuij__qhn += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        tuij__qhn += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        tuij__qhn += '          continue\n'
        tuij__qhn += '      m = regex.findall(str_arr[j])\n'
        tuij__qhn += '      for k, s in enumerate(m):\n'
        for i in range(ppj__bwv):
            tuij__qhn += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if ppj__bwv > 1 else ''))
        tuij__qhn += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        tuij__qhn += (
            '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
            )
        tuij__qhn += '        out_ind += 1\n'
        tuij__qhn += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        tuij__qhn += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    obp__chav = ', '.join('out_arr_{}'.format(i) for i in range(ppj__bwv))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(tuij__qhn, folpb__jiid,
        obp__chav, 'out_index', extra_globals={'get_utf8_size':
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
    bcvep__ibsow = dict(zip(regex.groupindex.values(), regex.groupindex.keys())
        )
    folpb__jiid = [bcvep__ibsow.get(1 + i, i) for i in range(regex.groups)]
    return folpb__jiid, regex


def create_str2str_methods_overload(func_name):
    gvoet__xdzjv = func_name in ['lstrip', 'rstrip', 'strip']
    tuij__qhn = f"""def f({'S_str, to_strip=None' if gvoet__xdzjv else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if gvoet__xdzjv else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if gvoet__xdzjv else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    tuij__qhn += f"""def _dict_impl({'S_str, to_strip=None' if gvoet__xdzjv else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if gvoet__xdzjv else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    sikl__byme = {}
    exec(tuij__qhn, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, sikl__byme)
    lma__nanz = sikl__byme['f']
    bstfe__gwzf = sikl__byme['_dict_impl']
    if gvoet__xdzjv:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return bstfe__gwzf
            return lma__nanz
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return bstfe__gwzf
            return lma__nanz
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    tuij__qhn = 'def dict_impl(S_str):\n'
    tuij__qhn += '    S = S_str._obj\n'
    tuij__qhn += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    tuij__qhn += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tuij__qhn += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tuij__qhn += f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n'
    tuij__qhn += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tuij__qhn += 'def impl(S_str):\n'
    tuij__qhn += '    S = S_str._obj\n'
    tuij__qhn += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tuij__qhn += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tuij__qhn += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    tuij__qhn += '    numba.parfors.parfor.init_prange()\n'
    tuij__qhn += '    l = len(str_arr)\n'
    tuij__qhn += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    tuij__qhn += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    tuij__qhn += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    tuij__qhn += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    tuij__qhn += '        else:\n'
    tuij__qhn += '            out_arr[i] = np.bool_(str_arr[i].{}())\n'.format(
        func_name)
    tuij__qhn += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    tuij__qhn += '      out_arr,index, name)\n'
    sikl__byme = {}
    exec(tuij__qhn, {'bodo': bodo, 'numba': numba, 'np': np}, sikl__byme)
    impl = sikl__byme['impl']
    fksus__sjoxn = sikl__byme['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return fksus__sjoxn
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for vqsno__jxnbo in bodo.hiframes.pd_series_ext.str2str_methods:
        kyxv__xtpy = create_str2str_methods_overload(vqsno__jxnbo)
        overload_method(SeriesStrMethodType, vqsno__jxnbo, inline='always',
            no_unliteral=True)(kyxv__xtpy)


def _install_str2bool_methods():
    for vqsno__jxnbo in bodo.hiframes.pd_series_ext.str2bool_methods:
        kyxv__xtpy = create_str2bool_methods_overload(vqsno__jxnbo)
        overload_method(SeriesStrMethodType, vqsno__jxnbo, inline='always',
            no_unliteral=True)(kyxv__xtpy)


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
        ikfus__lkp = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(ikfus__lkp)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        btjz__xpk = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, btjz__xpk)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        qli__ckhw, = args
        duey__hhrgs = signature.return_type
        ude__gpl = cgutils.create_struct_proxy(duey__hhrgs)(context, builder)
        ude__gpl.obj = qli__ckhw
        context.nrt.incref(builder, signature.args[0], qli__ckhw)
        return ude__gpl._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        uflr__dqeig = bodo.hiframes.pd_series_ext.get_series_data(S)
        ehlrz__kresh = bodo.hiframes.pd_series_ext.get_series_index(S)
        ikfus__lkp = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(uflr__dqeig),
            ehlrz__kresh, ikfus__lkp)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for agsep__wmhkz in unsupported_cat_attrs:
        uludk__hsb = 'Series.cat.' + agsep__wmhkz
        overload_attribute(SeriesCatMethodType, agsep__wmhkz)(
            create_unsupported_overload(uludk__hsb))
    for ufc__hsonj in unsupported_cat_methods:
        uludk__hsb = 'Series.cat.' + ufc__hsonj
        overload_method(SeriesCatMethodType, ufc__hsonj)(
            create_unsupported_overload(uludk__hsb))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for ufc__hsonj in unsupported_str_methods:
        uludk__hsb = 'Series.str.' + ufc__hsonj
        overload_method(SeriesStrMethodType, ufc__hsonj)(
            create_unsupported_overload(uludk__hsb))


_install_strseries_unsupported()
