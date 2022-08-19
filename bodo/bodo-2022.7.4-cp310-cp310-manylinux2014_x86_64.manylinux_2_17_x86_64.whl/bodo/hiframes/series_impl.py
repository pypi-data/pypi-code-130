"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.transform import is_var_size_item_array_type
from bodo.utils.typing import BodoError, ColNamesMetaType, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_index_names, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, is_str_arr_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    if isinstance(s.data, bodo.DatetimeArrayType):

        def impl(s):
            qqxke__aib = bodo.hiframes.pd_series_ext.get_series_data(s)
            kvyb__fwl = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                qqxke__aib)
            return kvyb__fwl
        return impl
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s, 'Series.dtype'
        )
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s,
        'Series.dtypes')
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.tolist()')
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            iqk__tdwif = list()
            for esrx__pocec in range(len(S)):
                iqk__tdwif.append(S.iat[esrx__pocec])
            return iqk__tdwif
        return impl_float

    def impl(S):
        iqk__tdwif = list()
        for esrx__pocec in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, esrx__pocec):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            iqk__tdwif.append(S.iat[esrx__pocec])
        return iqk__tdwif
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    tdgp__xgctv = dict(dtype=dtype, copy=copy, na_value=na_value)
    tblfm__uxja = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    tdgp__xgctv = dict(name=name, inplace=inplace)
    tblfm__uxja = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ubd__oiau = ', '.join(['index_arrs[{}]'.format(esrx__pocec) for
            esrx__pocec in range(S.index.nlevels)])
    else:
        ubd__oiau = '    bodo.utils.conversion.index_to_array(index)\n'
    yhd__spe = 'index' if 'index' != series_name else 'level_0'
    bsm__zjvu = get_index_names(S.index, 'Series.reset_index()', yhd__spe)
    columns = [name for name in bsm__zjvu]
    columns.append(series_name)
    qiej__jwzbk = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    qiej__jwzbk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    qiej__jwzbk += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        qiej__jwzbk += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    qiej__jwzbk += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    qiej__jwzbk += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ubd__oiau}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    nfuj__iayh = {}
    exec(qiej__jwzbk, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, nfuj__iayh)
    jlqg__ooc = nfuj__iayh['_impl']
    return jlqg__ooc


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.round()')

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        wtt__bxvcp = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for esrx__pocec in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[esrx__pocec]):
                bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
            else:
                wtt__bxvcp[esrx__pocec] = np.round(arr[esrx__pocec], decimals)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sum()'
        )

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.product()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    tdgp__xgctv = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    tblfm__uxja = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.any()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.equals()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.equals()')
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        muj__ckc = bodo.hiframes.pd_series_ext.get_series_data(S)
        wwlno__xths = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        cul__iqyr = 0
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(muj__ckc)):
            kpwby__afh = 0
            jxb__wym = bodo.libs.array_kernels.isna(muj__ckc, esrx__pocec)
            qrvof__osbyc = bodo.libs.array_kernels.isna(wwlno__xths,
                esrx__pocec)
            if jxb__wym and not qrvof__osbyc or not jxb__wym and qrvof__osbyc:
                kpwby__afh = 1
            elif not jxb__wym:
                if muj__ckc[esrx__pocec] != wwlno__xths[esrx__pocec]:
                    kpwby__afh = 1
            cul__iqyr += kpwby__afh
        return cul__iqyr == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    tdgp__xgctv = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    tblfm__uxja = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    tdgp__xgctv = dict(level=level)
    tblfm__uxja = dict(level=None)
    check_unsupported_args('Series.mad', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    wch__gigps = types.float64
    dct__omnvn = types.float64
    if S.dtype == types.float32:
        wch__gigps = types.float32
        dct__omnvn = types.float32
    hhm__qcjaw = wch__gigps(0)
    nceb__dwx = dct__omnvn(0)
    mpllq__xgagi = dct__omnvn(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ddz__aabx = hhm__qcjaw
        cul__iqyr = nceb__dwx
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(A)):
            kpwby__afh = hhm__qcjaw
            vad__rmqvg = nceb__dwx
            if not bodo.libs.array_kernels.isna(A, esrx__pocec) or not skipna:
                kpwby__afh = A[esrx__pocec]
                vad__rmqvg = mpllq__xgagi
            ddz__aabx += kpwby__afh
            cul__iqyr += vad__rmqvg
        zpxn__azifl = bodo.hiframes.series_kernels._mean_handle_nan(ddz__aabx,
            cul__iqyr)
        efov__fwmnw = hhm__qcjaw
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(A)):
            kpwby__afh = hhm__qcjaw
            if not bodo.libs.array_kernels.isna(A, esrx__pocec) or not skipna:
                kpwby__afh = abs(A[esrx__pocec] - zpxn__azifl)
            efov__fwmnw += kpwby__afh
        pbrs__tlezx = bodo.hiframes.series_kernels._mean_handle_nan(efov__fwmnw
            , cul__iqyr)
        return pbrs__tlezx
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    tdgp__xgctv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.mean()')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sem()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        xczr__djepw = 0
        iyh__cvb = 0
        cul__iqyr = 0
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(A)):
            kpwby__afh = 0
            vad__rmqvg = 0
            if not bodo.libs.array_kernels.isna(A, esrx__pocec) or not skipna:
                kpwby__afh = A[esrx__pocec]
                vad__rmqvg = 1
            xczr__djepw += kpwby__afh
            iyh__cvb += kpwby__afh * kpwby__afh
            cul__iqyr += vad__rmqvg
        jdhr__mphr = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            xczr__djepw, iyh__cvb, cul__iqyr, ddof)
        mchow__zba = bodo.hiframes.series_kernels._sem_handle_nan(jdhr__mphr,
            cul__iqyr)
        return mchow__zba
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.kurtosis()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        xczr__djepw = 0.0
        iyh__cvb = 0.0
        wxy__bzvx = 0.0
        cpe__ffvro = 0.0
        cul__iqyr = 0
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(A)):
            kpwby__afh = 0.0
            vad__rmqvg = 0
            if not bodo.libs.array_kernels.isna(A, esrx__pocec) or not skipna:
                kpwby__afh = np.float64(A[esrx__pocec])
                vad__rmqvg = 1
            xczr__djepw += kpwby__afh
            iyh__cvb += kpwby__afh ** 2
            wxy__bzvx += kpwby__afh ** 3
            cpe__ffvro += kpwby__afh ** 4
            cul__iqyr += vad__rmqvg
        jdhr__mphr = bodo.hiframes.series_kernels.compute_kurt(xczr__djepw,
            iyh__cvb, wxy__bzvx, cpe__ffvro, cul__iqyr)
        return jdhr__mphr
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.skew()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        xczr__djepw = 0.0
        iyh__cvb = 0.0
        wxy__bzvx = 0.0
        cul__iqyr = 0
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(A)):
            kpwby__afh = 0.0
            vad__rmqvg = 0
            if not bodo.libs.array_kernels.isna(A, esrx__pocec) or not skipna:
                kpwby__afh = np.float64(A[esrx__pocec])
                vad__rmqvg = 1
            xczr__djepw += kpwby__afh
            iyh__cvb += kpwby__afh ** 2
            wxy__bzvx += kpwby__afh ** 3
            cul__iqyr += vad__rmqvg
        jdhr__mphr = bodo.hiframes.series_kernels.compute_skew(xczr__djepw,
            iyh__cvb, wxy__bzvx, cul__iqyr)
        return jdhr__mphr
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.var()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.std()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.dot()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.dot()')

    def impl(S, other):
        muj__ckc = bodo.hiframes.pd_series_ext.get_series_data(S)
        wwlno__xths = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        zyc__dbhf = 0
        for esrx__pocec in numba.parfors.parfor.internal_prange(len(muj__ckc)):
            scq__sacz = muj__ckc[esrx__pocec]
            ijdpl__mjok = wwlno__xths[esrx__pocec]
            zyc__dbhf += scq__sacz * ijdpl__mjok
        return zyc__dbhf
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    tdgp__xgctv = dict(skipna=skipna)
    tblfm__uxja = dict(skipna=True)
    check_unsupported_args('Series.cumsum', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumsum()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    tdgp__xgctv = dict(skipna=skipna)
    tblfm__uxja = dict(skipna=True)
    check_unsupported_args('Series.cumprod', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumprod()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    tdgp__xgctv = dict(skipna=skipna)
    tblfm__uxja = dict(skipna=True)
    check_unsupported_args('Series.cummin', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummin()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    tdgp__xgctv = dict(skipna=skipna)
    tblfm__uxja = dict(skipna=True)
    check_unsupported_args('Series.cummax', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummax()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    tdgp__xgctv = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    tblfm__uxja = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        gvto__ntlqu = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, gvto__ntlqu, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    tdgp__xgctv = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    tblfm__uxja = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.abs()'
        )

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    tdgp__xgctv = dict(level=level)
    tblfm__uxja = dict(level=None)
    check_unsupported_args('Series.count', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    tdgp__xgctv = dict(method=method, min_periods=min_periods)
    tblfm__uxja = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        xhe__viky = S.sum()
        qqz__lpa = other.sum()
        a = n * (S * other).sum() - xhe__viky * qqz__lpa
        uykca__cniq = n * (S ** 2).sum() - xhe__viky ** 2
        haqwc__yqyk = n * (other ** 2).sum() - qqz__lpa ** 2
        return a / np.sqrt(uykca__cniq * haqwc__yqyk)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    tdgp__xgctv = dict(min_periods=min_periods)
    tblfm__uxja = dict(min_periods=None)
    check_unsupported_args('Series.cov', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        xhe__viky = S.mean()
        qqz__lpa = other.mean()
        prld__znm = ((S - xhe__viky) * (other - qqz__lpa)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(prld__znm, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            avh__iuo = np.sign(sum_val)
            return np.inf * avh__iuo
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    tdgp__xgctv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.min()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    tdgp__xgctv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.max()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    tdgp__xgctv = dict(axis=axis, skipna=skipna)
    tblfm__uxja = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmin()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    tdgp__xgctv = dict(axis=axis, skipna=skipna)
    tblfm__uxja = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmax()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_increasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_decreasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    tdgp__xgctv = dict(level=level, numeric_only=numeric_only)
    tblfm__uxja = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qno__tpf = arr[:n]
        hbatz__okj = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(qno__tpf, hbatz__okj,
            name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        mbnb__bbwk = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qno__tpf = arr[mbnb__bbwk:]
        hbatz__okj = index[mbnb__bbwk:]
        return bodo.hiframes.pd_series_ext.init_series(qno__tpf, hbatz__okj,
            name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    ecf__mtoit = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ecf__mtoit:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            eltji__peg = index[0]
            aoj__ajxff = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                eltji__peg, False))
        else:
            aoj__ajxff = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qno__tpf = arr[:aoj__ajxff]
        hbatz__okj = index[:aoj__ajxff]
        return bodo.hiframes.pd_series_ext.init_series(qno__tpf, hbatz__okj,
            name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    ecf__mtoit = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ecf__mtoit:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            adxf__kxqk = index[-1]
            aoj__ajxff = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                adxf__kxqk, True))
        else:
            aoj__ajxff = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qno__tpf = arr[len(arr) - aoj__ajxff:]
        hbatz__okj = index[len(arr) - aoj__ajxff:]
        return bodo.hiframes.pd_series_ext.init_series(qno__tpf, hbatz__okj,
            name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        fpl__lzzt = bodo.utils.conversion.index_to_array(index)
        mjtj__suxm, fyt__devr = bodo.libs.array_kernels.first_last_valid_index(
            arr, fpl__lzzt)
        return fyt__devr if mjtj__suxm else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        fpl__lzzt = bodo.utils.conversion.index_to_array(index)
        mjtj__suxm, fyt__devr = bodo.libs.array_kernels.first_last_valid_index(
            arr, fpl__lzzt, False)
        return fyt__devr if mjtj__suxm else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    tdgp__xgctv = dict(keep=keep)
    tblfm__uxja = dict(keep='first')
    check_unsupported_args('Series.nlargest', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        fpl__lzzt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp, vavjv__abs = bodo.libs.array_kernels.nlargest(arr,
            fpl__lzzt, n, True, bodo.hiframes.series_kernels.gt_f)
        ijxbn__fbr = bodo.utils.conversion.convert_to_index(vavjv__abs)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    tdgp__xgctv = dict(keep=keep)
    tblfm__uxja = dict(keep='first')
    check_unsupported_args('Series.nsmallest', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        fpl__lzzt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp, vavjv__abs = bodo.libs.array_kernels.nlargest(arr,
            fpl__lzzt, n, False, bodo.hiframes.series_kernels.lt_f)
        ijxbn__fbr = bodo.utils.conversion.convert_to_index(vavjv__abs)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
@overload_method(HeterogeneousSeriesType, 'astype', inline='always',
    no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    tdgp__xgctv = dict(errors=errors)
    tblfm__uxja = dict(errors='raise')
    check_unsupported_args('Series.astype', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.astype()')

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    tdgp__xgctv = dict(axis=axis, is_copy=is_copy)
    tblfm__uxja = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        din__khovi = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[din__khovi],
            index[din__khovi], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    tdgp__xgctv = dict(axis=axis, kind=kind, order=order)
    tblfm__uxja = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bctnn__dcfqu = S.notna().values
        if not bctnn__dcfqu.all():
            wtt__bxvcp = np.full(n, -1, np.int64)
            wtt__bxvcp[bctnn__dcfqu] = argsort(arr[bctnn__dcfqu])
        else:
            wtt__bxvcp = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    tdgp__xgctv = dict(axis=axis, numeric_only=numeric_only)
    tblfm__uxja = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_str(method):
        raise BodoError(
            "Series.rank(): 'method' argument must be a constant string")
    if not is_overload_constant_str(na_option):
        raise BodoError(
            "Series.rank(): 'na_option' argument must be a constant string")

    def impl(S, axis=0, method='average', numeric_only=None, na_option=
        'keep', ascending=True, pct=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    tdgp__xgctv = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    tblfm__uxja = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    kdbfe__hzfyj = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ynn__rlc = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, kdbfe__hzfyj)
        pqh__ghsop = ynn__rlc.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        wtt__bxvcp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            pqh__ghsop, 0)
        ijxbn__fbr = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            pqh__ghsop)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    tdgp__xgctv = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    tblfm__uxja = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    xebo__biyn = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ynn__rlc = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, xebo__biyn)
        pqh__ghsop = ynn__rlc.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        wtt__bxvcp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            pqh__ghsop, 0)
        ijxbn__fbr = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            pqh__ghsop)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    brb__mfze = is_overload_true(is_nullable)
    qiej__jwzbk = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    qiej__jwzbk += '  numba.parfors.parfor.init_prange()\n'
    qiej__jwzbk += '  n = len(arr)\n'
    if brb__mfze:
        qiej__jwzbk += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        qiej__jwzbk += '  out_arr = np.empty(n, np.int64)\n'
    qiej__jwzbk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    qiej__jwzbk += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if brb__mfze:
        qiej__jwzbk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        qiej__jwzbk += '      out_arr[i] = -1\n'
    qiej__jwzbk += '      continue\n'
    qiej__jwzbk += '    val = arr[i]\n'
    qiej__jwzbk += '    if include_lowest and val == bins[0]:\n'
    qiej__jwzbk += '      ind = 1\n'
    qiej__jwzbk += '    else:\n'
    qiej__jwzbk += '      ind = np.searchsorted(bins, val)\n'
    qiej__jwzbk += '    if ind == 0 or ind == len(bins):\n'
    if brb__mfze:
        qiej__jwzbk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        qiej__jwzbk += '      out_arr[i] = -1\n'
    qiej__jwzbk += '    else:\n'
    qiej__jwzbk += '      out_arr[i] = ind - 1\n'
    qiej__jwzbk += '  return out_arr\n'
    nfuj__iayh = {}
    exec(qiej__jwzbk, {'bodo': bodo, 'np': np, 'numba': numba}, nfuj__iayh)
    impl = nfuj__iayh['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        soqo__uctz, iocd__etlk = np.divmod(x, 1)
        if soqo__uctz == 0:
            ftr__zue = -int(np.floor(np.log10(abs(iocd__etlk)))
                ) - 1 + precision
        else:
            ftr__zue = precision
        return np.around(x, ftr__zue)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        omw__kfg = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(omw__kfg)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        rhkiu__vxws = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            rrpv__dtp = bins.copy()
            if right and include_lowest:
                rrpv__dtp[0] = rrpv__dtp[0] - rhkiu__vxws
            szzon__zjg = bodo.libs.interval_arr_ext.init_interval_array(
                rrpv__dtp[:-1], rrpv__dtp[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(szzon__zjg,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        rrpv__dtp = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            rrpv__dtp[0] = rrpv__dtp[0] - 10.0 ** -precision
        szzon__zjg = bodo.libs.interval_arr_ext.init_interval_array(rrpv__dtp
            [:-1], rrpv__dtp[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(szzon__zjg, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        erj__ohh = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        cde__uscv = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        wtt__bxvcp = np.zeros(nbins, np.int64)
        for esrx__pocec in range(len(erj__ohh)):
            wtt__bxvcp[cde__uscv[esrx__pocec]] = erj__ohh[esrx__pocec]
        return wtt__bxvcp
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            ffryo__sdiu = (max_val - min_val) * 0.001
            if right:
                bins[0] -= ffryo__sdiu
            else:
                bins[-1] += ffryo__sdiu
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    tdgp__xgctv = dict(dropna=dropna)
    tblfm__uxja = dict(dropna=True)
    check_unsupported_args('Series.value_counts', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    xgtao__gwtox = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    qiej__jwzbk = 'def impl(\n'
    qiej__jwzbk += '    S,\n'
    qiej__jwzbk += '    normalize=False,\n'
    qiej__jwzbk += '    sort=True,\n'
    qiej__jwzbk += '    ascending=False,\n'
    qiej__jwzbk += '    bins=None,\n'
    qiej__jwzbk += '    dropna=True,\n'
    qiej__jwzbk += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    qiej__jwzbk += '):\n'
    qiej__jwzbk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    qiej__jwzbk += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    qiej__jwzbk += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if xgtao__gwtox:
        qiej__jwzbk += '    right = True\n'
        qiej__jwzbk += _gen_bins_handling(bins, S.dtype)
        qiej__jwzbk += '    arr = get_bin_inds(bins, arr)\n'
    qiej__jwzbk += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    qiej__jwzbk += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    qiej__jwzbk += '    )\n'
    qiej__jwzbk += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if xgtao__gwtox:
        qiej__jwzbk += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        qiej__jwzbk += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        qiej__jwzbk += '    index = get_bin_labels(bins)\n'
    else:
        qiej__jwzbk += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        qiej__jwzbk += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        qiej__jwzbk += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        qiej__jwzbk += '    )\n'
        qiej__jwzbk += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    qiej__jwzbk += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        qiej__jwzbk += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        ecq__qmaj = 'len(S)' if xgtao__gwtox else 'count_arr.sum()'
        qiej__jwzbk += f'    res = res / float({ecq__qmaj})\n'
    qiej__jwzbk += '    return res\n'
    nfuj__iayh = {}
    exec(qiej__jwzbk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, nfuj__iayh)
    impl = nfuj__iayh['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    qiej__jwzbk = ''
    if isinstance(bins, types.Integer):
        qiej__jwzbk += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        qiej__jwzbk += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            qiej__jwzbk += '    min_val = min_val.value\n'
            qiej__jwzbk += '    max_val = max_val.value\n'
        qiej__jwzbk += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            qiej__jwzbk += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        qiej__jwzbk += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return qiej__jwzbk


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    tdgp__xgctv = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    tblfm__uxja = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    qiej__jwzbk = 'def impl(\n'
    qiej__jwzbk += '    x,\n'
    qiej__jwzbk += '    bins,\n'
    qiej__jwzbk += '    right=True,\n'
    qiej__jwzbk += '    labels=None,\n'
    qiej__jwzbk += '    retbins=False,\n'
    qiej__jwzbk += '    precision=3,\n'
    qiej__jwzbk += '    include_lowest=False,\n'
    qiej__jwzbk += "    duplicates='raise',\n"
    qiej__jwzbk += '    ordered=True\n'
    qiej__jwzbk += '):\n'
    if isinstance(x, SeriesType):
        qiej__jwzbk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        qiej__jwzbk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        qiej__jwzbk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        qiej__jwzbk += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    qiej__jwzbk += _gen_bins_handling(bins, x.dtype)
    qiej__jwzbk += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    qiej__jwzbk += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    qiej__jwzbk += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    qiej__jwzbk += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        qiej__jwzbk += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        qiej__jwzbk += '    return res\n'
    else:
        qiej__jwzbk += '    return out_arr\n'
    nfuj__iayh = {}
    exec(qiej__jwzbk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, nfuj__iayh)
    impl = nfuj__iayh['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.unique, inline='always', no_unliteral=True)
def overload_unique(values):
    if not is_series_type(values) and not (bodo.utils.utils.is_array_typ(
        values, False) and values.ndim == 1):
        raise BodoError(
            "pd.unique(): 'values' must be either a Series or a 1-d array")
    if is_series_type(values):

        def impl(values):
            arr = bodo.hiframes.pd_series_ext.get_series_data(values)
            return bodo.allgatherv(bodo.libs.array_kernels.unique(arr), False)
        return impl
    else:
        return lambda values: bodo.allgatherv(bodo.libs.array_kernels.
            unique(values), False)


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    tdgp__xgctv = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    tblfm__uxja = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        les__ats = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, les__ats)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    tdgp__xgctv = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    tblfm__uxja = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )
        ksr__cbaa = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            kdtzt__txk = bodo.utils.conversion.coerce_to_array(index)
            ynn__rlc = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                kdtzt__txk, arr), index, ksr__cbaa)
            return ynn__rlc.groupby(' ')['']
        return impl_index
    zkis__oazvf = by
    if isinstance(by, SeriesType):
        zkis__oazvf = by.data
    if isinstance(zkis__oazvf, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    xeaks__ogkov = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        kdtzt__txk = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ynn__rlc = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            kdtzt__txk, arr), index, xeaks__ogkov)
        return ynn__rlc.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    tdgp__xgctv = dict(verify_integrity=verify_integrity)
    tblfm__uxja = dict(verify_integrity=False)
    check_unsupported_args('Series.append', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_append,
        'Series.append()')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.isin()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(values,
        'Series.isin()')
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            zomn__nsqow = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            wtt__bxvcp = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(wtt__bxvcp, A, zomn__nsqow, False)
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    tdgp__xgctv = dict(interpolation=interpolation)
    tblfm__uxja = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            wtt__bxvcp = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        scju__nop = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(scju__nop, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    tdgp__xgctv = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    tblfm__uxja = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.describe()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        cjqk__zaef = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        cjqk__zaef = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    qiej__jwzbk = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {cjqk__zaef}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    uql__jcst = dict()
    exec(qiej__jwzbk, {'bodo': bodo, 'numba': numba}, uql__jcst)
    equzr__qan = uql__jcst['impl']
    return equzr__qan


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        cjqk__zaef = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        cjqk__zaef = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    qiej__jwzbk = 'def impl(S,\n'
    qiej__jwzbk += '     value=None,\n'
    qiej__jwzbk += '    method=None,\n'
    qiej__jwzbk += '    axis=None,\n'
    qiej__jwzbk += '    inplace=False,\n'
    qiej__jwzbk += '    limit=None,\n'
    qiej__jwzbk += '   downcast=None,\n'
    qiej__jwzbk += '):\n'
    qiej__jwzbk += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    qiej__jwzbk += '    n = len(in_arr)\n'
    qiej__jwzbk += f'    out_arr = {cjqk__zaef}(n, -1)\n'
    qiej__jwzbk += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    qiej__jwzbk += '        s = in_arr[j]\n'
    qiej__jwzbk += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    qiej__jwzbk += '            s = value\n'
    qiej__jwzbk += '        out_arr[j] = s\n'
    qiej__jwzbk += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    uql__jcst = dict()
    exec(qiej__jwzbk, {'bodo': bodo, 'numba': numba}, uql__jcst)
    equzr__qan = uql__jcst['impl']
    return equzr__qan


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
    inuj__fzccd = bodo.hiframes.pd_series_ext.get_series_data(value)
    for esrx__pocec in numba.parfors.parfor.internal_prange(len(bxc__pdz)):
        s = bxc__pdz[esrx__pocec]
        if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec
            ) and not bodo.libs.array_kernels.isna(inuj__fzccd, esrx__pocec):
            s = inuj__fzccd[esrx__pocec]
        bxc__pdz[esrx__pocec] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
    for esrx__pocec in numba.parfors.parfor.internal_prange(len(bxc__pdz)):
        s = bxc__pdz[esrx__pocec]
        if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec):
            s = value
        bxc__pdz[esrx__pocec] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    inuj__fzccd = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(bxc__pdz)
    wtt__bxvcp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for zasvr__pgrhg in numba.parfors.parfor.internal_prange(n):
        s = bxc__pdz[zasvr__pgrhg]
        if bodo.libs.array_kernels.isna(bxc__pdz, zasvr__pgrhg
            ) and not bodo.libs.array_kernels.isna(inuj__fzccd, zasvr__pgrhg):
            s = inuj__fzccd[zasvr__pgrhg]
        wtt__bxvcp[zasvr__pgrhg] = s
        if bodo.libs.array_kernels.isna(bxc__pdz, zasvr__pgrhg
            ) and bodo.libs.array_kernels.isna(inuj__fzccd, zasvr__pgrhg):
            bodo.libs.array_kernels.setna(wtt__bxvcp, zasvr__pgrhg)
    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    inuj__fzccd = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(bxc__pdz)
    wtt__bxvcp = bodo.utils.utils.alloc_type(n, bxc__pdz.dtype, (-1,))
    for esrx__pocec in numba.parfors.parfor.internal_prange(n):
        s = bxc__pdz[esrx__pocec]
        if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec
            ) and not bodo.libs.array_kernels.isna(inuj__fzccd, esrx__pocec):
            s = inuj__fzccd[esrx__pocec]
        wtt__bxvcp[esrx__pocec] = s
    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    tdgp__xgctv = dict(limit=limit, downcast=downcast)
    tblfm__uxja = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    too__iazec = not is_overload_none(value)
    lypwa__flmhc = not is_overload_none(method)
    if too__iazec and lypwa__flmhc:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not too__iazec and not lypwa__flmhc:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if lypwa__flmhc:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        sfp__ynhm = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(sfp__ynhm)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(sfp__ynhm)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    domo__mcvx = element_type(S.data)
    atgg__ljmwg = None
    if too__iazec:
        atgg__ljmwg = element_type(types.unliteral(value))
    if atgg__ljmwg and not can_replace(domo__mcvx, atgg__ljmwg):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {atgg__ljmwg} with series type {domo__mcvx}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if S.data == bodo.dict_str_arr_type:
                raise_bodo_error(
                    "Series.fillna(): 'inplace' not supported for dictionary-encoded string arrays yet."
                    )
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        bnid__sof = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                inuj__fzccd = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(bxc__pdz)
                wtt__bxvcp = bodo.utils.utils.alloc_type(n, bnid__sof, (-1,))
                for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec
                        ) and bodo.libs.array_kernels.isna(inuj__fzccd,
                        esrx__pocec):
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                        continue
                    if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec):
                        wtt__bxvcp[esrx__pocec
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            inuj__fzccd[esrx__pocec])
                        continue
                    wtt__bxvcp[esrx__pocec
                        ] = bodo.utils.conversion.unbox_if_timestamp(bxc__pdz
                        [esrx__pocec])
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return fillna_series_impl
        if lypwa__flmhc:
            dqkb__xfi = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(domo__mcvx, (types.Integer, types.Float)
                ) and domo__mcvx not in dqkb__xfi:
                raise BodoError(
                    f"Series.fillna(): series of type {domo__mcvx} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wtt__bxvcp = bodo.libs.array_kernels.ffill_bfill_arr(bxc__pdz,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(bxc__pdz)
            wtt__bxvcp = bodo.utils.utils.alloc_type(n, bnid__sof, (-1,))
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(bxc__pdz[
                    esrx__pocec])
                if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec):
                    s = value
                wtt__bxvcp[esrx__pocec] = s
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        nin__cfkq = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        tdgp__xgctv = dict(limit=limit, downcast=downcast)
        tblfm__uxja = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', tdgp__xgctv,
            tblfm__uxja, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        domo__mcvx = element_type(S.data)
        dqkb__xfi = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(domo__mcvx, (types.Integer, types.Float)
            ) and domo__mcvx not in dqkb__xfi:
            raise BodoError(
                f'Series.{overload_name}(): series of type {domo__mcvx} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wtt__bxvcp = bodo.libs.array_kernels.ffill_bfill_arr(bxc__pdz,
                nin__cfkq)
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        pqf__xes = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(pqf__xes)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        wmn__wfum = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(wmn__wfum)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        wmn__wfum = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(wmn__wfum)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        wmn__wfum = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(wmn__wfum)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    tdgp__xgctv = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    kvftr__thw = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', tdgp__xgctv, kvftr__thw,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    domo__mcvx = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        uwku__cddj = element_type(to_replace.key_type)
        atgg__ljmwg = element_type(to_replace.value_type)
    else:
        uwku__cddj = element_type(to_replace)
        atgg__ljmwg = element_type(value)
    lszjd__qpbn = None
    if domo__mcvx != types.unliteral(uwku__cddj):
        if bodo.utils.typing.equality_always_false(domo__mcvx, types.
            unliteral(uwku__cddj)
            ) or not bodo.utils.typing.types_equality_exists(domo__mcvx,
            uwku__cddj):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(domo__mcvx, (types.Float, types.Integer)
            ) or domo__mcvx == np.bool_:
            lszjd__qpbn = domo__mcvx
    if not can_replace(domo__mcvx, types.unliteral(atgg__ljmwg)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    nez__oto = to_str_arr_if_dict_array(S.data)
    if isinstance(nez__oto, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bxc__pdz.replace
                (to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(bxc__pdz)
        wtt__bxvcp = bodo.utils.utils.alloc_type(n, nez__oto, (-1,))
        kwfj__yuco = build_replace_dict(to_replace, value, lszjd__qpbn)
        for esrx__pocec in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(bxc__pdz, esrx__pocec):
                bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                continue
            s = bxc__pdz[esrx__pocec]
            if s in kwfj__yuco:
                s = kwfj__yuco[s]
            wtt__bxvcp[esrx__pocec] = s
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    cxssa__pjjg = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    vddu__rkoo = is_iterable_type(to_replace)
    smw__bel = isinstance(value, (types.Number, Decimal128Type)) or value in [
        bodo.string_type, bodo.bytes_type, types.boolean]
    uiedq__ibhtw = is_iterable_type(value)
    if cxssa__pjjg and smw__bel:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                kwfj__yuco = {}
                kwfj__yuco[key_dtype_conv(to_replace)] = value
                return kwfj__yuco
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            kwfj__yuco = {}
            kwfj__yuco[to_replace] = value
            return kwfj__yuco
        return impl
    if vddu__rkoo and smw__bel:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                kwfj__yuco = {}
                for vqu__dbh in to_replace:
                    kwfj__yuco[key_dtype_conv(vqu__dbh)] = value
                return kwfj__yuco
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            kwfj__yuco = {}
            for vqu__dbh in to_replace:
                kwfj__yuco[vqu__dbh] = value
            return kwfj__yuco
        return impl
    if vddu__rkoo and uiedq__ibhtw:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                kwfj__yuco = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for esrx__pocec in range(len(to_replace)):
                    kwfj__yuco[key_dtype_conv(to_replace[esrx__pocec])
                        ] = value[esrx__pocec]
                return kwfj__yuco
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            kwfj__yuco = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for esrx__pocec in range(len(to_replace)):
                kwfj__yuco[to_replace[esrx__pocec]] = value[esrx__pocec]
            return kwfj__yuco
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.diff()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wtt__bxvcp = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    tdgp__xgctv = dict(ignore_index=ignore_index)
    ydf__rjw = dict(ignore_index=False)
    check_unsupported_args('Series.explode', tdgp__xgctv, ydf__rjw,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fpl__lzzt = bodo.utils.conversion.index_to_array(index)
        wtt__bxvcp, yygzo__jyo = bodo.libs.array_kernels.explode(arr, fpl__lzzt
            )
        ijxbn__fbr = bodo.utils.conversion.index_from_array(yygzo__jyo)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.digitize()')
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            iynt__islux = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                iynt__islux[esrx__pocec] = np.argmax(a[esrx__pocec])
            return iynt__islux
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            fclhr__rxlw = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                fclhr__rxlw[esrx__pocec] = np.argmin(a[esrx__pocec])
            return fclhr__rxlw
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    tdgp__xgctv = dict(axis=axis, inplace=inplace, how=how)
    hdysc__cfdvq = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', tdgp__xgctv, hdysc__cfdvq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            bctnn__dcfqu = S.notna().values
            fpl__lzzt = bodo.utils.conversion.extract_index_array(S)
            ijxbn__fbr = bodo.utils.conversion.convert_to_index(fpl__lzzt[
                bctnn__dcfqu])
            wtt__bxvcp = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(bxc__pdz))
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                ijxbn__fbr, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            fpl__lzzt = bodo.utils.conversion.extract_index_array(S)
            bctnn__dcfqu = S.notna().values
            ijxbn__fbr = bodo.utils.conversion.convert_to_index(fpl__lzzt[
                bctnn__dcfqu])
            wtt__bxvcp = bxc__pdz[bctnn__dcfqu]
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                ijxbn__fbr, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    tdgp__xgctv = dict(freq=freq, axis=axis, fill_value=fill_value)
    tblfm__uxja = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.shift()')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    tdgp__xgctv = dict(fill_method=fill_method, limit=limit, freq=freq)
    tblfm__uxja = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.pct_change()')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
            f'Series.{func_name}()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            f'Series.{func_name}()')
        _validate_arguments_mask_where(f'Series.{func_name}', 'Series', S,
            cond, other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            nncai__qco = 'None'
        else:
            nncai__qco = 'other'
        qiej__jwzbk = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            qiej__jwzbk += '  cond = ~cond\n'
        qiej__jwzbk += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qiej__jwzbk += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qiej__jwzbk += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        qiej__jwzbk += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {nncai__qco})
"""
        qiej__jwzbk += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        nfuj__iayh = {}
        exec(qiej__jwzbk, {'bodo': bodo, 'np': np}, nfuj__iayh)
        impl = nfuj__iayh['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        pqf__xes = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(pqf__xes)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    tdgp__xgctv = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    tblfm__uxja = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name=module_name)
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(S, bodo.hiframes.pd_index_ext.RangeIndexType):
        arr = types.Array(types.int64, 1, 'C')
    else:
        arr = S.data
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, module_name, arr, other.data
            )
    else:
        _validate_self_other_mask_where(func_name, module_name, arr, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, module_name, arr, other,
    max_ndim=1, is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() {module_name} data with type {arr} not yet supported'
            )
    zkxet__fqcup = is_overload_constant_nan(other)
    if not (is_default or zkxet__fqcup or is_scalar_type(other) or 
        isinstance(other, types.Array) and other.ndim >= 1 and other.ndim <=
        max_ndim or isinstance(other, SeriesType) and (isinstance(arr,
        types.Array) or arr.dtype in [bodo.string_type, bodo.bytes_type]) or
        is_str_arr_type(other) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not (isinstance(other, (StringArrayType, BinaryArrayType)) or 
        other == bodo.dict_str_arr_type) and (isinstance(arr.dtype, types.
        Integer) and (bodo.utils.utils.is_array_typ(other) and isinstance(
        other.dtype, types.Integer) or is_series_type(other) and isinstance
        (other.dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(
        other) and arr.dtype == other.dtype or is_series_type(other) and 
        arr.dtype == other.dtype)) and (isinstance(arr, BooleanArrayType) or
        isinstance(arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for {module_name}."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            xkwt__wvb = arr.dtype.elem_type
        else:
            xkwt__wvb = arr.dtype
        if is_iterable_type(other):
            hitc__aswam = other.dtype
        elif zkxet__fqcup:
            hitc__aswam = types.float64
        else:
            hitc__aswam = types.unliteral(other)
        if not zkxet__fqcup and not is_common_scalar_dtype([xkwt__wvb,
            hitc__aswam]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        tdgp__xgctv = dict(level=level, axis=axis)
        tblfm__uxja = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), tdgp__xgctv,
            tblfm__uxja, package_name='pandas', module_name='Series')
        sosrn__aws = other == string_type or is_overload_constant_str(other)
        odsi__muz = is_iterable_type(other) and other.dtype == string_type
        vub__atf = S.dtype == string_type and (op == operator.add and (
            sosrn__aws or odsi__muz) or op == operator.mul and isinstance(
            other, types.Integer))
        wsrs__gyf = S.dtype == bodo.timedelta64ns
        trkx__otrz = S.dtype == bodo.datetime64ns
        ajq__zrv = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        ikmii__ohkmf = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        dlja__srbb = wsrs__gyf and (ajq__zrv or ikmii__ohkmf
            ) or trkx__otrz and ajq__zrv
        dlja__srbb = dlja__srbb and op == operator.add
        if not (isinstance(S.dtype, types.Number) or vub__atf or dlja__srbb):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        qmjha__nrcc = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            nez__oto = qmjha__nrcc.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and nez__oto == types.Array(types.bool_, 1, 'C'):
                nez__oto = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                wtt__bxvcp = bodo.utils.utils.alloc_type(n, nez__oto, (-1,))
                for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                    xeqa__vyug = bodo.libs.array_kernels.isna(arr, esrx__pocec)
                    if xeqa__vyug:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wtt__bxvcp,
                                esrx__pocec)
                        else:
                            wtt__bxvcp[esrx__pocec] = op(fill_value, other)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(arr[esrx__pocec], other)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        nez__oto = qmjha__nrcc.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and nez__oto == types.Array(
            types.bool_, 1, 'C'):
            nez__oto = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            iqm__mhcf = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wtt__bxvcp = bodo.utils.utils.alloc_type(n, nez__oto, (-1,))
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                xeqa__vyug = bodo.libs.array_kernels.isna(arr, esrx__pocec)
                tqpsa__hlzj = bodo.libs.array_kernels.isna(iqm__mhcf,
                    esrx__pocec)
                if xeqa__vyug and tqpsa__hlzj:
                    bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                elif xeqa__vyug:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(fill_value, iqm__mhcf[
                            esrx__pocec])
                elif tqpsa__hlzj:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(arr[esrx__pocec],
                            fill_value)
                else:
                    wtt__bxvcp[esrx__pocec] = op(arr[esrx__pocec],
                        iqm__mhcf[esrx__pocec])
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        qmjha__nrcc = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            nez__oto = qmjha__nrcc.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and nez__oto == types.Array(types.bool_, 1, 'C'):
                nez__oto = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                wtt__bxvcp = bodo.utils.utils.alloc_type(n, nez__oto, None)
                for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                    xeqa__vyug = bodo.libs.array_kernels.isna(arr, esrx__pocec)
                    if xeqa__vyug:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wtt__bxvcp,
                                esrx__pocec)
                        else:
                            wtt__bxvcp[esrx__pocec] = op(other, fill_value)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(other, arr[esrx__pocec])
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        nez__oto = qmjha__nrcc.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and nez__oto == types.Array(
            types.bool_, 1, 'C'):
            nez__oto = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            iqm__mhcf = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wtt__bxvcp = bodo.utils.utils.alloc_type(n, nez__oto, None)
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                xeqa__vyug = bodo.libs.array_kernels.isna(arr, esrx__pocec)
                tqpsa__hlzj = bodo.libs.array_kernels.isna(iqm__mhcf,
                    esrx__pocec)
                wtt__bxvcp[esrx__pocec] = op(iqm__mhcf[esrx__pocec], arr[
                    esrx__pocec])
                if xeqa__vyug and tqpsa__hlzj:
                    bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                elif xeqa__vyug:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(iqm__mhcf[esrx__pocec],
                            fill_value)
                elif tqpsa__hlzj:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                    else:
                        wtt__bxvcp[esrx__pocec] = op(fill_value, arr[
                            esrx__pocec])
                else:
                    wtt__bxvcp[esrx__pocec] = op(iqm__mhcf[esrx__pocec],
                        arr[esrx__pocec])
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, jsl__oao in explicit_binop_funcs_two_ways.items():
        for name in jsl__oao:
            pqf__xes = create_explicit_binary_op_overload(op)
            jyjz__zbaex = create_explicit_binary_reverse_op_overload(op)
            sdy__syoz = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(pqf__xes)
            overload_method(SeriesType, sdy__syoz, no_unliteral=True)(
                jyjz__zbaex)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        pqf__xes = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(pqf__xes)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lucw__tjnx = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wtt__bxvcp = dt64_arr_sub(arr, lucw__tjnx)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                wtt__bxvcp = np.empty(n, np.dtype('datetime64[ns]'))
                for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, esrx__pocec):
                        bodo.libs.array_kernels.setna(wtt__bxvcp, esrx__pocec)
                        continue
                    wnky__wpjsq = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[esrx__pocec]))
                    frlq__rkdyl = op(wnky__wpjsq, rhs)
                    wtt__bxvcp[esrx__pocec
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        frlq__rkdyl.value)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    lucw__tjnx = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    wtt__bxvcp = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(lucw__tjnx))
                    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lucw__tjnx = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wtt__bxvcp = op(arr, lucw__tjnx)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    nyz__xtna = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    wtt__bxvcp = op(bodo.utils.conversion.
                        unbox_if_timestamp(nyz__xtna), arr)
                    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nyz__xtna = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                wtt__bxvcp = op(nyz__xtna, arr)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        pqf__xes = create_binary_op_overload(op)
        overload(op)(pqf__xes)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    gpp__awrja = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, gpp__awrja)
        for esrx__pocec in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, esrx__pocec
                ) or bodo.libs.array_kernels.isna(arg2, esrx__pocec):
                bodo.libs.array_kernels.setna(S, esrx__pocec)
                continue
            S[esrx__pocec
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                esrx__pocec]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[esrx__pocec]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                iqm__mhcf = bodo.utils.conversion.get_array_if_series_or_index(
                    other)
                op(arr, iqm__mhcf)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        pqf__xes = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(pqf__xes)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wtt__bxvcp = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        pqf__xes = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(pqf__xes)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    wtt__bxvcp = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    iqm__mhcf = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    wtt__bxvcp = ufunc(arr, iqm__mhcf)
                    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    iqm__mhcf = bodo.hiframes.pd_series_ext.get_series_data(S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    wtt__bxvcp = ufunc(arr, iqm__mhcf)
                    return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        pqf__xes = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(pqf__xes)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        dnv__sij = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        qqxke__aib = np.arange(n),
        bodo.libs.timsort.sort(dnv__sij, 0, n, qqxke__aib)
        return qqxke__aib[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        jpgw__uuyo = get_overload_const_str(downcast)
        if jpgw__uuyo in ('integer', 'signed'):
            out_dtype = types.int64
        elif jpgw__uuyo == 'unsigned':
            out_dtype = types.uint64
        else:
            assert jpgw__uuyo == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            bxc__pdz = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            wtt__bxvcp = pd.to_numeric(bxc__pdz, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            aes__pgb = np.empty(n, np.float64)
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, esrx__pocec):
                    bodo.libs.array_kernels.setna(aes__pgb, esrx__pocec)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(aes__pgb,
                        esrx__pocec, arg_a, esrx__pocec)
            return aes__pgb
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            aes__pgb = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for esrx__pocec in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, esrx__pocec):
                    bodo.libs.array_kernels.setna(aes__pgb, esrx__pocec)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(aes__pgb,
                        esrx__pocec, arg_a, esrx__pocec)
            return aes__pgb
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        fiyky__vkvl = if_series_to_array_type(args[0])
        if isinstance(fiyky__vkvl, types.Array) and isinstance(fiyky__vkvl.
            dtype, types.Integer):
            fiyky__vkvl = types.Array(types.float64, 1, 'C')
        return fiyky__vkvl(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(y,
        'numpy.where()')
    yxrhd__wfvnh = bodo.utils.utils.is_array_typ(x, True)
    jqx__hpk = bodo.utils.utils.is_array_typ(y, True)
    qiej__jwzbk = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        qiej__jwzbk += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if yxrhd__wfvnh and not bodo.utils.utils.is_array_typ(x, False):
        qiej__jwzbk += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if jqx__hpk and not bodo.utils.utils.is_array_typ(y, False):
        qiej__jwzbk += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    qiej__jwzbk += '  n = len(condition)\n'
    gkoc__eogkx = x.dtype if yxrhd__wfvnh else types.unliteral(x)
    rqf__gfcol = y.dtype if jqx__hpk else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        gkoc__eogkx = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        rqf__gfcol = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    ncy__dxcm = get_data(x)
    wlw__mbbc = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(qqxke__aib) for
        qqxke__aib in [ncy__dxcm, wlw__mbbc])
    if wlw__mbbc == types.none:
        if isinstance(gkoc__eogkx, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif ncy__dxcm == wlw__mbbc and not is_nullable:
        out_dtype = dtype_to_array_type(gkoc__eogkx)
    elif gkoc__eogkx == string_type or rqf__gfcol == string_type:
        out_dtype = bodo.string_array_type
    elif ncy__dxcm == bytes_type or (yxrhd__wfvnh and gkoc__eogkx == bytes_type
        ) and (wlw__mbbc == bytes_type or jqx__hpk and rqf__gfcol == bytes_type
        ):
        out_dtype = binary_array_type
    elif isinstance(gkoc__eogkx, bodo.PDCategoricalDtype):
        out_dtype = None
    elif gkoc__eogkx in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(gkoc__eogkx, 1, 'C')
    elif rqf__gfcol in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(rqf__gfcol, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(gkoc__eogkx), numba.np.numpy_support.
            as_dtype(rqf__gfcol)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(gkoc__eogkx, bodo.PDCategoricalDtype):
        qqnfe__sdmv = 'x'
    else:
        qqnfe__sdmv = 'out_dtype'
    qiej__jwzbk += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {qqnfe__sdmv}, (-1,))\n')
    if isinstance(gkoc__eogkx, bodo.PDCategoricalDtype):
        qiej__jwzbk += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        qiej__jwzbk += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    qiej__jwzbk += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    qiej__jwzbk += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if yxrhd__wfvnh:
        qiej__jwzbk += '      if bodo.libs.array_kernels.isna(x, j):\n'
        qiej__jwzbk += '        setna(out_arr, j)\n'
        qiej__jwzbk += '        continue\n'
    if isinstance(gkoc__eogkx, bodo.PDCategoricalDtype):
        qiej__jwzbk += '      out_codes[j] = x_codes[j]\n'
    else:
        qiej__jwzbk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if yxrhd__wfvnh else 'x'))
    qiej__jwzbk += '    else:\n'
    if jqx__hpk:
        qiej__jwzbk += '      if bodo.libs.array_kernels.isna(y, j):\n'
        qiej__jwzbk += '        setna(out_arr, j)\n'
        qiej__jwzbk += '        continue\n'
    if wlw__mbbc == types.none:
        if isinstance(gkoc__eogkx, bodo.PDCategoricalDtype):
            qiej__jwzbk += '      out_codes[j] = -1\n'
        else:
            qiej__jwzbk += '      setna(out_arr, j)\n'
    else:
        qiej__jwzbk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if jqx__hpk else 'y'))
    qiej__jwzbk += '  return out_arr\n'
    nfuj__iayh = {}
    exec(qiej__jwzbk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, nfuj__iayh)
    jlqg__ooc = nfuj__iayh['_impl']
    return jlqg__ooc


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        hhhr__nrx = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(hhhr__nrx, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(hhhr__nrx):
            ukte__mtdf = hhhr__nrx.data.dtype
        else:
            ukte__mtdf = hhhr__nrx.dtype
        if isinstance(ukte__mtdf, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        neaf__rimlb = hhhr__nrx
    else:
        pyxv__fasid = []
        for hhhr__nrx in choicelist:
            if not bodo.utils.utils.is_array_typ(hhhr__nrx, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(hhhr__nrx):
                ukte__mtdf = hhhr__nrx.data.dtype
            else:
                ukte__mtdf = hhhr__nrx.dtype
            if isinstance(ukte__mtdf, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            pyxv__fasid.append(ukte__mtdf)
        if not is_common_scalar_dtype(pyxv__fasid):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        neaf__rimlb = choicelist[0]
    if is_series_type(neaf__rimlb):
        neaf__rimlb = neaf__rimlb.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, neaf__rimlb.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(neaf__rimlb, types.Array) or isinstance(neaf__rimlb,
        BooleanArrayType) or isinstance(neaf__rimlb, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(neaf__rimlb, False) and neaf__rimlb.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {neaf__rimlb} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    wps__qrf = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        apt__tlvu = choicelist.dtype
    else:
        uuio__dkkr = False
        pyxv__fasid = []
        for hhhr__nrx in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(hhhr__nrx
                , 'numpy.select()')
            if is_nullable_type(hhhr__nrx):
                uuio__dkkr = True
            if is_series_type(hhhr__nrx):
                ukte__mtdf = hhhr__nrx.data.dtype
            else:
                ukte__mtdf = hhhr__nrx.dtype
            if isinstance(ukte__mtdf, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            pyxv__fasid.append(ukte__mtdf)
        xtob__vsnkz, vzo__ecsh = get_common_scalar_dtype(pyxv__fasid)
        if not vzo__ecsh:
            raise BodoError('Internal error in overload_np_select')
        zhq__vexsk = dtype_to_array_type(xtob__vsnkz)
        if uuio__dkkr:
            zhq__vexsk = to_nullable_type(zhq__vexsk)
        apt__tlvu = zhq__vexsk
    if isinstance(apt__tlvu, SeriesType):
        apt__tlvu = apt__tlvu.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        rae__lvqio = True
    else:
        rae__lvqio = False
    meecc__llu = False
    aiudy__swjd = False
    if rae__lvqio:
        if isinstance(apt__tlvu.dtype, types.Number):
            pass
        elif apt__tlvu.dtype == types.bool_:
            aiudy__swjd = True
        else:
            meecc__llu = True
            apt__tlvu = to_nullable_type(apt__tlvu)
    elif default == types.none or is_overload_constant_nan(default):
        meecc__llu = True
        apt__tlvu = to_nullable_type(apt__tlvu)
    qiej__jwzbk = 'def np_select_impl(condlist, choicelist, default=0):\n'
    qiej__jwzbk += '  if len(condlist) != len(choicelist):\n'
    qiej__jwzbk += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    qiej__jwzbk += '  output_len = len(choicelist[0])\n'
    qiej__jwzbk += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    qiej__jwzbk += '  for i in range(output_len):\n'
    if meecc__llu:
        qiej__jwzbk += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif aiudy__swjd:
        qiej__jwzbk += '    out[i] = False\n'
    else:
        qiej__jwzbk += '    out[i] = default\n'
    if wps__qrf:
        qiej__jwzbk += '  for i in range(len(condlist) - 1, -1, -1):\n'
        qiej__jwzbk += '    cond = condlist[i]\n'
        qiej__jwzbk += '    choice = choicelist[i]\n'
        qiej__jwzbk += '    out = np.where(cond, choice, out)\n'
    else:
        for esrx__pocec in range(len(choicelist) - 1, -1, -1):
            qiej__jwzbk += f'  cond = condlist[{esrx__pocec}]\n'
            qiej__jwzbk += f'  choice = choicelist[{esrx__pocec}]\n'
            qiej__jwzbk += f'  out = np.where(cond, choice, out)\n'
    qiej__jwzbk += '  return out'
    nfuj__iayh = dict()
    exec(qiej__jwzbk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': apt__tlvu}, nfuj__iayh)
    impl = nfuj__iayh['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtt__bxvcp = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    tdgp__xgctv = dict(subset=subset, keep=keep, inplace=inplace)
    tblfm__uxja = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', tdgp__xgctv,
        tblfm__uxja, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        jem__mvv = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (jem__mvv,), fpl__lzzt = bodo.libs.array_kernels.drop_duplicates((
            jem__mvv,), index, 1)
        index = bodo.utils.conversion.index_from_array(fpl__lzzt)
        return bodo.hiframes.pd_series_ext.init_series(jem__mvv, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    gbqkb__sbivr = element_type(S.data)
    if not is_common_scalar_dtype([gbqkb__sbivr, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([gbqkb__sbivr, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        wtt__bxvcp = np.empty(n, np.bool_)
        for esrx__pocec in numba.parfors.parfor.internal_prange(n):
            kpwby__afh = bodo.utils.conversion.box_if_dt64(arr[esrx__pocec])
            if inclusive == 'both':
                wtt__bxvcp[esrx__pocec
                    ] = kpwby__afh <= right and kpwby__afh >= left
            else:
                wtt__bxvcp[esrx__pocec
                    ] = kpwby__afh < right and kpwby__afh > left
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    tdgp__xgctv = dict(axis=axis)
    tblfm__uxja = dict(axis=None)
    check_unsupported_args('Series.repeat', tdgp__xgctv, tblfm__uxja,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            fpl__lzzt = bodo.utils.conversion.index_to_array(index)
            wtt__bxvcp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            yygzo__jyo = bodo.libs.array_kernels.repeat_kernel(fpl__lzzt,
                repeats)
            ijxbn__fbr = bodo.utils.conversion.index_from_array(yygzo__jyo)
            return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
                ijxbn__fbr, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fpl__lzzt = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        wtt__bxvcp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        yygzo__jyo = bodo.libs.array_kernels.repeat_kernel(fpl__lzzt, repeats)
        ijxbn__fbr = bodo.utils.conversion.index_from_array(yygzo__jyo)
        return bodo.hiframes.pd_series_ext.init_series(wtt__bxvcp,
            ijxbn__fbr, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        qqxke__aib = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(qqxke__aib)
        fuw__pde = {}
        for esrx__pocec in range(n):
            kpwby__afh = bodo.utils.conversion.box_if_dt64(qqxke__aib[
                esrx__pocec])
            fuw__pde[index[esrx__pocec]] = kpwby__afh
        return fuw__pde
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    sfp__ynhm = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            cer__vyuq = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(sfp__ynhm)
    elif is_literal_type(name):
        cer__vyuq = get_literal_value(name)
    else:
        raise_bodo_error(sfp__ynhm)
    cer__vyuq = 0 if cer__vyuq is None else cer__vyuq
    pfnl__kayjw = ColNamesMetaType((cer__vyuq,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            pfnl__kayjw)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
