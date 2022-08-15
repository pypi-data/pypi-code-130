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
            ljhzv__hiu = bodo.hiframes.pd_series_ext.get_series_data(s)
            lphkf__vzfl = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                ljhzv__hiu)
            return lphkf__vzfl
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
            evhiq__hxig = list()
            for rvx__xjpc in range(len(S)):
                evhiq__hxig.append(S.iat[rvx__xjpc])
            return evhiq__hxig
        return impl_float

    def impl(S):
        evhiq__hxig = list()
        for rvx__xjpc in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, rvx__xjpc):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            evhiq__hxig.append(S.iat[rvx__xjpc])
        return evhiq__hxig
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    bwegc__pzzoq = dict(dtype=dtype, copy=copy, na_value=na_value)
    oxdv__teuw = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    bwegc__pzzoq = dict(name=name, inplace=inplace)
    oxdv__teuw = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', bwegc__pzzoq, oxdv__teuw,
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
        dgy__isv = ', '.join(['index_arrs[{}]'.format(rvx__xjpc) for
            rvx__xjpc in range(S.index.nlevels)])
    else:
        dgy__isv = '    bodo.utils.conversion.index_to_array(index)\n'
    omh__qdka = 'index' if 'index' != series_name else 'level_0'
    uxs__wab = get_index_names(S.index, 'Series.reset_index()', omh__qdka)
    columns = [name for name in uxs__wab]
    columns.append(series_name)
    fbkdt__abvf = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    fbkdt__abvf += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    fbkdt__abvf += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        fbkdt__abvf += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    fbkdt__abvf += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    fbkdt__abvf += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({dgy__isv}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    grqh__fjvs = {}
    exec(fbkdt__abvf, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, grqh__fjvs)
    tfq__ghpn = grqh__fjvs['_impl']
    return tfq__ghpn


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
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
        iyr__peyci = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[rvx__xjpc]):
                bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
            else:
                iyr__peyci[rvx__xjpc] = np.round(arr[rvx__xjpc], decimals)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    oxdv__teuw = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', bwegc__pzzoq, oxdv__teuw,
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
        enrq__dpwm = bodo.hiframes.pd_series_ext.get_series_data(S)
        hxx__ugabe = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        mbsd__ocav = 0
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(enrq__dpwm)):
            kflw__img = 0
            uxmhl__huuvs = bodo.libs.array_kernels.isna(enrq__dpwm, rvx__xjpc)
            zwm__zsf = bodo.libs.array_kernels.isna(hxx__ugabe, rvx__xjpc)
            if uxmhl__huuvs and not zwm__zsf or not uxmhl__huuvs and zwm__zsf:
                kflw__img = 1
            elif not uxmhl__huuvs:
                if enrq__dpwm[rvx__xjpc] != hxx__ugabe[rvx__xjpc]:
                    kflw__img = 1
            mbsd__ocav += kflw__img
        return mbsd__ocav == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    bwegc__pzzoq = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    oxdv__teuw = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    bwegc__pzzoq = dict(level=level)
    oxdv__teuw = dict(level=None)
    check_unsupported_args('Series.mad', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    ewvs__dslro = types.float64
    idydl__dldsu = types.float64
    if S.dtype == types.float32:
        ewvs__dslro = types.float32
        idydl__dldsu = types.float32
    oxuns__kdh = ewvs__dslro(0)
    chq__wrvr = idydl__dldsu(0)
    kqun__ptmox = idydl__dldsu(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        beaq__pjmq = oxuns__kdh
        mbsd__ocav = chq__wrvr
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(A)):
            kflw__img = oxuns__kdh
            jben__nkgdd = chq__wrvr
            if not bodo.libs.array_kernels.isna(A, rvx__xjpc) or not skipna:
                kflw__img = A[rvx__xjpc]
                jben__nkgdd = kqun__ptmox
            beaq__pjmq += kflw__img
            mbsd__ocav += jben__nkgdd
        wwkh__rdgb = bodo.hiframes.series_kernels._mean_handle_nan(beaq__pjmq,
            mbsd__ocav)
        hkhl__zwnc = oxuns__kdh
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(A)):
            kflw__img = oxuns__kdh
            if not bodo.libs.array_kernels.isna(A, rvx__xjpc) or not skipna:
                kflw__img = abs(A[rvx__xjpc] - wwkh__rdgb)
            hkhl__zwnc += kflw__img
        fgi__bckjf = bodo.hiframes.series_kernels._mean_handle_nan(hkhl__zwnc,
            mbsd__ocav)
        return fgi__bckjf
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    bwegc__pzzoq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', bwegc__pzzoq, oxdv__teuw,
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
        xnl__osct = 0
        lgmc__boxg = 0
        mbsd__ocav = 0
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(A)):
            kflw__img = 0
            jben__nkgdd = 0
            if not bodo.libs.array_kernels.isna(A, rvx__xjpc) or not skipna:
                kflw__img = A[rvx__xjpc]
                jben__nkgdd = 1
            xnl__osct += kflw__img
            lgmc__boxg += kflw__img * kflw__img
            mbsd__ocav += jben__nkgdd
        oryar__dfjbh = (bodo.hiframes.series_kernels.
            _compute_var_nan_count_ddof(xnl__osct, lgmc__boxg, mbsd__ocav,
            ddof))
        bij__ubxrf = bodo.hiframes.series_kernels._sem_handle_nan(oryar__dfjbh,
            mbsd__ocav)
        return bij__ubxrf
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', bwegc__pzzoq, oxdv__teuw,
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
        xnl__osct = 0.0
        lgmc__boxg = 0.0
        tqwop__ncdi = 0.0
        atcke__wqy = 0.0
        mbsd__ocav = 0
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(A)):
            kflw__img = 0.0
            jben__nkgdd = 0
            if not bodo.libs.array_kernels.isna(A, rvx__xjpc) or not skipna:
                kflw__img = np.float64(A[rvx__xjpc])
                jben__nkgdd = 1
            xnl__osct += kflw__img
            lgmc__boxg += kflw__img ** 2
            tqwop__ncdi += kflw__img ** 3
            atcke__wqy += kflw__img ** 4
            mbsd__ocav += jben__nkgdd
        oryar__dfjbh = bodo.hiframes.series_kernels.compute_kurt(xnl__osct,
            lgmc__boxg, tqwop__ncdi, atcke__wqy, mbsd__ocav)
        return oryar__dfjbh
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', bwegc__pzzoq, oxdv__teuw,
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
        xnl__osct = 0.0
        lgmc__boxg = 0.0
        tqwop__ncdi = 0.0
        mbsd__ocav = 0
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(A)):
            kflw__img = 0.0
            jben__nkgdd = 0
            if not bodo.libs.array_kernels.isna(A, rvx__xjpc) or not skipna:
                kflw__img = np.float64(A[rvx__xjpc])
                jben__nkgdd = 1
            xnl__osct += kflw__img
            lgmc__boxg += kflw__img ** 2
            tqwop__ncdi += kflw__img ** 3
            mbsd__ocav += jben__nkgdd
        oryar__dfjbh = bodo.hiframes.series_kernels.compute_skew(xnl__osct,
            lgmc__boxg, tqwop__ncdi, mbsd__ocav)
        return oryar__dfjbh
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', bwegc__pzzoq, oxdv__teuw,
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
        enrq__dpwm = bodo.hiframes.pd_series_ext.get_series_data(S)
        hxx__ugabe = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        xugup__hcb = 0
        for rvx__xjpc in numba.parfors.parfor.internal_prange(len(enrq__dpwm)):
            xbc__fcvn = enrq__dpwm[rvx__xjpc]
            olqe__wow = hxx__ugabe[rvx__xjpc]
            xugup__hcb += xbc__fcvn * olqe__wow
        return xugup__hcb
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    bwegc__pzzoq = dict(skipna=skipna)
    oxdv__teuw = dict(skipna=True)
    check_unsupported_args('Series.cumsum', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(skipna=skipna)
    oxdv__teuw = dict(skipna=True)
    check_unsupported_args('Series.cumprod', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(skipna=skipna)
    oxdv__teuw = dict(skipna=True)
    check_unsupported_args('Series.cummin', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(skipna=skipna)
    oxdv__teuw = dict(skipna=True)
    check_unsupported_args('Series.cummax', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    oxdv__teuw = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        uze__iek = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, uze__iek, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    bwegc__pzzoq = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    oxdv__teuw = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(level=level)
    oxdv__teuw = dict(level=None)
    check_unsupported_args('Series.count', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    bwegc__pzzoq = dict(method=method, min_periods=min_periods)
    oxdv__teuw = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        wbb__plud = S.sum()
        hkiu__kaxis = other.sum()
        a = n * (S * other).sum() - wbb__plud * hkiu__kaxis
        dbicj__zct = n * (S ** 2).sum() - wbb__plud ** 2
        cqd__kmhln = n * (other ** 2).sum() - hkiu__kaxis ** 2
        return a / np.sqrt(dbicj__zct * cqd__kmhln)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    bwegc__pzzoq = dict(min_periods=min_periods)
    oxdv__teuw = dict(min_periods=None)
    check_unsupported_args('Series.cov', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        wbb__plud = S.mean()
        hkiu__kaxis = other.mean()
        kutj__tcnxn = ((S - wbb__plud) * (other - hkiu__kaxis)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(kutj__tcnxn, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            ebkm__kcx = np.sign(sum_val)
            return np.inf * ebkm__kcx
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    bwegc__pzzoq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(axis=axis, skipna=skipna)
    oxdv__teuw = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(axis=axis, skipna=skipna)
    oxdv__teuw = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', bwegc__pzzoq, oxdv__teuw,
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
    bwegc__pzzoq = dict(level=level, numeric_only=numeric_only)
    oxdv__teuw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', bwegc__pzzoq, oxdv__teuw,
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
        ecvgf__oxd = arr[:n]
        ypxi__sox = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(ecvgf__oxd,
            ypxi__sox, name)
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
        mgle__ikgcd = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ecvgf__oxd = arr[mgle__ikgcd:]
        ypxi__sox = index[mgle__ikgcd:]
        return bodo.hiframes.pd_series_ext.init_series(ecvgf__oxd,
            ypxi__sox, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    qenx__snrhq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in qenx__snrhq:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            cuj__qhz = index[0]
            qkf__resf = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, cuj__qhz,
                False))
        else:
            qkf__resf = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ecvgf__oxd = arr[:qkf__resf]
        ypxi__sox = index[:qkf__resf]
        return bodo.hiframes.pd_series_ext.init_series(ecvgf__oxd,
            ypxi__sox, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    qenx__snrhq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in qenx__snrhq:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            denb__yggwc = index[-1]
            qkf__resf = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                denb__yggwc, True))
        else:
            qkf__resf = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ecvgf__oxd = arr[len(arr) - qkf__resf:]
        ypxi__sox = index[len(arr) - qkf__resf:]
        return bodo.hiframes.pd_series_ext.init_series(ecvgf__oxd,
            ypxi__sox, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yazub__tjlsp = bodo.utils.conversion.index_to_array(index)
        lxouy__aqoyb, ycsir__cks = (bodo.libs.array_kernels.
            first_last_valid_index(arr, yazub__tjlsp))
        return ycsir__cks if lxouy__aqoyb else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yazub__tjlsp = bodo.utils.conversion.index_to_array(index)
        lxouy__aqoyb, ycsir__cks = (bodo.libs.array_kernels.
            first_last_valid_index(arr, yazub__tjlsp, False))
        return ycsir__cks if lxouy__aqoyb else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    bwegc__pzzoq = dict(keep=keep)
    oxdv__teuw = dict(keep='first')
    check_unsupported_args('Series.nlargest', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yazub__tjlsp = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci, pkrxr__vvh = bodo.libs.array_kernels.nlargest(arr,
            yazub__tjlsp, n, True, bodo.hiframes.series_kernels.gt_f)
        aikjj__rvwt = bodo.utils.conversion.convert_to_index(pkrxr__vvh)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    bwegc__pzzoq = dict(keep=keep)
    oxdv__teuw = dict(keep='first')
    check_unsupported_args('Series.nsmallest', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yazub__tjlsp = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci, pkrxr__vvh = bodo.libs.array_kernels.nlargest(arr,
            yazub__tjlsp, n, False, bodo.hiframes.series_kernels.lt_f)
        aikjj__rvwt = bodo.utils.conversion.convert_to_index(pkrxr__vvh)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
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
    bwegc__pzzoq = dict(errors=errors)
    oxdv__teuw = dict(errors='raise')
    check_unsupported_args('Series.astype', bwegc__pzzoq, oxdv__teuw,
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
        iyr__peyci = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    bwegc__pzzoq = dict(axis=axis, is_copy=is_copy)
    oxdv__teuw = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        hcbnn__uus = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[hcbnn__uus],
            index[hcbnn__uus], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    bwegc__pzzoq = dict(axis=axis, kind=kind, order=order)
    oxdv__teuw = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        efi__qyu = S.notna().values
        if not efi__qyu.all():
            iyr__peyci = np.full(n, -1, np.int64)
            iyr__peyci[efi__qyu] = argsort(arr[efi__qyu])
        else:
            iyr__peyci = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    bwegc__pzzoq = dict(axis=axis, numeric_only=numeric_only)
    oxdv__teuw = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', bwegc__pzzoq, oxdv__teuw,
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
        iyr__peyci = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    bwegc__pzzoq = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    oxdv__teuw = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    cnjkt__zkn = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        tce__nkey = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, cnjkt__zkn)
        frob__kzjqm = tce__nkey.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        iyr__peyci = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            frob__kzjqm, 0)
        aikjj__rvwt = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            frob__kzjqm)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    bwegc__pzzoq = dict(axis=axis, inplace=inplace, kind=kind, ignore_index
        =ignore_index, key=key)
    oxdv__teuw = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    pacfa__wck = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        tce__nkey = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, pacfa__wck)
        frob__kzjqm = tce__nkey.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        iyr__peyci = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            frob__kzjqm, 0)
        aikjj__rvwt = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            frob__kzjqm)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    mtw__lzp = is_overload_true(is_nullable)
    fbkdt__abvf = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    fbkdt__abvf += '  numba.parfors.parfor.init_prange()\n'
    fbkdt__abvf += '  n = len(arr)\n'
    if mtw__lzp:
        fbkdt__abvf += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        fbkdt__abvf += '  out_arr = np.empty(n, np.int64)\n'
    fbkdt__abvf += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    fbkdt__abvf += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if mtw__lzp:
        fbkdt__abvf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        fbkdt__abvf += '      out_arr[i] = -1\n'
    fbkdt__abvf += '      continue\n'
    fbkdt__abvf += '    val = arr[i]\n'
    fbkdt__abvf += '    if include_lowest and val == bins[0]:\n'
    fbkdt__abvf += '      ind = 1\n'
    fbkdt__abvf += '    else:\n'
    fbkdt__abvf += '      ind = np.searchsorted(bins, val)\n'
    fbkdt__abvf += '    if ind == 0 or ind == len(bins):\n'
    if mtw__lzp:
        fbkdt__abvf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        fbkdt__abvf += '      out_arr[i] = -1\n'
    fbkdt__abvf += '    else:\n'
    fbkdt__abvf += '      out_arr[i] = ind - 1\n'
    fbkdt__abvf += '  return out_arr\n'
    grqh__fjvs = {}
    exec(fbkdt__abvf, {'bodo': bodo, 'np': np, 'numba': numba}, grqh__fjvs)
    impl = grqh__fjvs['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        xffam__diby, cqnad__gvmnd = np.divmod(x, 1)
        if xffam__diby == 0:
            hmoq__qmxk = -int(np.floor(np.log10(abs(cqnad__gvmnd)))
                ) - 1 + precision
        else:
            hmoq__qmxk = precision
        return np.around(x, hmoq__qmxk)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        qgy__ptmp = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(qgy__ptmp)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        ofuuj__eajy = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            mej__hvrk = bins.copy()
            if right and include_lowest:
                mej__hvrk[0] = mej__hvrk[0] - ofuuj__eajy
            cwv__gxcta = bodo.libs.interval_arr_ext.init_interval_array(
                mej__hvrk[:-1], mej__hvrk[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(cwv__gxcta,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        mej__hvrk = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            mej__hvrk[0] = mej__hvrk[0] - 10.0 ** -precision
        cwv__gxcta = bodo.libs.interval_arr_ext.init_interval_array(mej__hvrk
            [:-1], mej__hvrk[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(cwv__gxcta, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        ckrbt__vula = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        cgz__sdd = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        iyr__peyci = np.zeros(nbins, np.int64)
        for rvx__xjpc in range(len(ckrbt__vula)):
            iyr__peyci[cgz__sdd[rvx__xjpc]] = ckrbt__vula[rvx__xjpc]
        return iyr__peyci
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
            rlcw__ney = (max_val - min_val) * 0.001
            if right:
                bins[0] -= rlcw__ney
            else:
                bins[-1] += rlcw__ney
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    bwegc__pzzoq = dict(dropna=dropna)
    oxdv__teuw = dict(dropna=True)
    check_unsupported_args('Series.value_counts', bwegc__pzzoq, oxdv__teuw,
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
    lpd__qnap = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    fbkdt__abvf = 'def impl(\n'
    fbkdt__abvf += '    S,\n'
    fbkdt__abvf += '    normalize=False,\n'
    fbkdt__abvf += '    sort=True,\n'
    fbkdt__abvf += '    ascending=False,\n'
    fbkdt__abvf += '    bins=None,\n'
    fbkdt__abvf += '    dropna=True,\n'
    fbkdt__abvf += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    fbkdt__abvf += '):\n'
    fbkdt__abvf += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    fbkdt__abvf += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    fbkdt__abvf += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if lpd__qnap:
        fbkdt__abvf += '    right = True\n'
        fbkdt__abvf += _gen_bins_handling(bins, S.dtype)
        fbkdt__abvf += '    arr = get_bin_inds(bins, arr)\n'
    fbkdt__abvf += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    fbkdt__abvf += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    fbkdt__abvf += '    )\n'
    fbkdt__abvf += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if lpd__qnap:
        fbkdt__abvf += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        fbkdt__abvf += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        fbkdt__abvf += '    index = get_bin_labels(bins)\n'
    else:
        fbkdt__abvf += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        fbkdt__abvf += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        fbkdt__abvf += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        fbkdt__abvf += '    )\n'
        fbkdt__abvf += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    fbkdt__abvf += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        fbkdt__abvf += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        aandh__bszci = 'len(S)' if lpd__qnap else 'count_arr.sum()'
        fbkdt__abvf += f'    res = res / float({aandh__bszci})\n'
    fbkdt__abvf += '    return res\n'
    grqh__fjvs = {}
    exec(fbkdt__abvf, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, grqh__fjvs)
    impl = grqh__fjvs['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    fbkdt__abvf = ''
    if isinstance(bins, types.Integer):
        fbkdt__abvf += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        fbkdt__abvf += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            fbkdt__abvf += '    min_val = min_val.value\n'
            fbkdt__abvf += '    max_val = max_val.value\n'
        fbkdt__abvf += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            fbkdt__abvf += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        fbkdt__abvf += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return fbkdt__abvf


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    bwegc__pzzoq = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    oxdv__teuw = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    fbkdt__abvf = 'def impl(\n'
    fbkdt__abvf += '    x,\n'
    fbkdt__abvf += '    bins,\n'
    fbkdt__abvf += '    right=True,\n'
    fbkdt__abvf += '    labels=None,\n'
    fbkdt__abvf += '    retbins=False,\n'
    fbkdt__abvf += '    precision=3,\n'
    fbkdt__abvf += '    include_lowest=False,\n'
    fbkdt__abvf += "    duplicates='raise',\n"
    fbkdt__abvf += '    ordered=True\n'
    fbkdt__abvf += '):\n'
    if isinstance(x, SeriesType):
        fbkdt__abvf += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        fbkdt__abvf += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        fbkdt__abvf += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        fbkdt__abvf += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    fbkdt__abvf += _gen_bins_handling(bins, x.dtype)
    fbkdt__abvf += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    fbkdt__abvf += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    fbkdt__abvf += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    fbkdt__abvf += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        fbkdt__abvf += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        fbkdt__abvf += '    return res\n'
    else:
        fbkdt__abvf += '    return out_arr\n'
    grqh__fjvs = {}
    exec(fbkdt__abvf, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, grqh__fjvs)
    impl = grqh__fjvs['impl']
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
    bwegc__pzzoq = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    oxdv__teuw = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        ohtip__oax = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, ohtip__oax)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    bwegc__pzzoq = dict(axis=axis, sort=sort, group_keys=group_keys,
        squeeze=squeeze, observed=observed, dropna=dropna)
    oxdv__teuw = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', bwegc__pzzoq, oxdv__teuw,
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
        rah__gvyux = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            rupz__xgexs = bodo.utils.conversion.coerce_to_array(index)
            tce__nkey = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                rupz__xgexs, arr), index, rah__gvyux)
            return tce__nkey.groupby(' ')['']
        return impl_index
    zvwvs__ryx = by
    if isinstance(by, SeriesType):
        zvwvs__ryx = by.data
    if isinstance(zvwvs__ryx, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    msbpn__lswmh = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        rupz__xgexs = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        tce__nkey = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            rupz__xgexs, arr), index, msbpn__lswmh)
        return tce__nkey.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    bwegc__pzzoq = dict(verify_integrity=verify_integrity)
    oxdv__teuw = dict(verify_integrity=False)
    check_unsupported_args('Series.append', bwegc__pzzoq, oxdv__teuw,
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
            skm__mqtt = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            iyr__peyci = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(iyr__peyci, A, skm__mqtt, False)
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    bwegc__pzzoq = dict(interpolation=interpolation)
    oxdv__teuw = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            iyr__peyci = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
        ksmj__pojb = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(ksmj__pojb, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    bwegc__pzzoq = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    oxdv__teuw = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', bwegc__pzzoq, oxdv__teuw,
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
        dzi__kssh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        dzi__kssh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    fbkdt__abvf = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {dzi__kssh}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    eybgv__bsl = dict()
    exec(fbkdt__abvf, {'bodo': bodo, 'numba': numba}, eybgv__bsl)
    jhjxk__nrgg = eybgv__bsl['impl']
    return jhjxk__nrgg


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        dzi__kssh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        dzi__kssh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    fbkdt__abvf = 'def impl(S,\n'
    fbkdt__abvf += '     value=None,\n'
    fbkdt__abvf += '    method=None,\n'
    fbkdt__abvf += '    axis=None,\n'
    fbkdt__abvf += '    inplace=False,\n'
    fbkdt__abvf += '    limit=None,\n'
    fbkdt__abvf += '   downcast=None,\n'
    fbkdt__abvf += '):\n'
    fbkdt__abvf += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    fbkdt__abvf += '    n = len(in_arr)\n'
    fbkdt__abvf += f'    out_arr = {dzi__kssh}(n, -1)\n'
    fbkdt__abvf += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    fbkdt__abvf += '        s = in_arr[j]\n'
    fbkdt__abvf += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    fbkdt__abvf += '            s = value\n'
    fbkdt__abvf += '        out_arr[j] = s\n'
    fbkdt__abvf += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    eybgv__bsl = dict()
    exec(fbkdt__abvf, {'bodo': bodo, 'numba': numba}, eybgv__bsl)
    jhjxk__nrgg = eybgv__bsl['impl']
    return jhjxk__nrgg


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
    hrub__vsanp = bodo.hiframes.pd_series_ext.get_series_data(value)
    for rvx__xjpc in numba.parfors.parfor.internal_prange(len(oosm__tmik)):
        s = oosm__tmik[rvx__xjpc]
        if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc
            ) and not bodo.libs.array_kernels.isna(hrub__vsanp, rvx__xjpc):
            s = hrub__vsanp[rvx__xjpc]
        oosm__tmik[rvx__xjpc] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
    for rvx__xjpc in numba.parfors.parfor.internal_prange(len(oosm__tmik)):
        s = oosm__tmik[rvx__xjpc]
        if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc):
            s = value
        oosm__tmik[rvx__xjpc] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    hrub__vsanp = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(oosm__tmik)
    iyr__peyci = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for uajj__kis in numba.parfors.parfor.internal_prange(n):
        s = oosm__tmik[uajj__kis]
        if bodo.libs.array_kernels.isna(oosm__tmik, uajj__kis
            ) and not bodo.libs.array_kernels.isna(hrub__vsanp, uajj__kis):
            s = hrub__vsanp[uajj__kis]
        iyr__peyci[uajj__kis] = s
        if bodo.libs.array_kernels.isna(oosm__tmik, uajj__kis
            ) and bodo.libs.array_kernels.isna(hrub__vsanp, uajj__kis):
            bodo.libs.array_kernels.setna(iyr__peyci, uajj__kis)
    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    hrub__vsanp = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(oosm__tmik)
    iyr__peyci = bodo.utils.utils.alloc_type(n, oosm__tmik.dtype, (-1,))
    for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
        s = oosm__tmik[rvx__xjpc]
        if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc
            ) and not bodo.libs.array_kernels.isna(hrub__vsanp, rvx__xjpc):
            s = hrub__vsanp[rvx__xjpc]
        iyr__peyci[rvx__xjpc] = s
    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    bwegc__pzzoq = dict(limit=limit, downcast=downcast)
    oxdv__teuw = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', bwegc__pzzoq, oxdv__teuw,
        package_name='pandas', module_name='Series')
    gjlt__vtxz = not is_overload_none(value)
    vmycb__dvvs = not is_overload_none(method)
    if gjlt__vtxz and vmycb__dvvs:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not gjlt__vtxz and not vmycb__dvvs:
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
    if vmycb__dvvs:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        jyz__jwpwn = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(jyz__jwpwn)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(jyz__jwpwn)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    tib__omfdq = element_type(S.data)
    xspqi__jbut = None
    if gjlt__vtxz:
        xspqi__jbut = element_type(types.unliteral(value))
    if xspqi__jbut and not can_replace(tib__omfdq, xspqi__jbut):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {xspqi__jbut} with series type {tib__omfdq}'
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
        jps__jkllv = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hrub__vsanp = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(oosm__tmik)
                iyr__peyci = bodo.utils.utils.alloc_type(n, jps__jkllv, (-1,))
                for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc
                        ) and bodo.libs.array_kernels.isna(hrub__vsanp,
                        rvx__xjpc):
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                        continue
                    if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc):
                        iyr__peyci[rvx__xjpc
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            hrub__vsanp[rvx__xjpc])
                        continue
                    iyr__peyci[rvx__xjpc
                        ] = bodo.utils.conversion.unbox_if_timestamp(oosm__tmik
                        [rvx__xjpc])
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return fillna_series_impl
        if vmycb__dvvs:
            dimpg__awmr = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(tib__omfdq, (types.Integer, types.Float)
                ) and tib__omfdq not in dimpg__awmr:
                raise BodoError(
                    f"Series.fillna(): series of type {tib__omfdq} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                iyr__peyci = bodo.libs.array_kernels.ffill_bfill_arr(oosm__tmik
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(oosm__tmik)
            iyr__peyci = bodo.utils.utils.alloc_type(n, jps__jkllv, (-1,))
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(oosm__tmik[
                    rvx__xjpc])
                if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc):
                    s = value
                iyr__peyci[rvx__xjpc] = s
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        vxird__fzpr = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        bwegc__pzzoq = dict(limit=limit, downcast=downcast)
        oxdv__teuw = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', bwegc__pzzoq,
            oxdv__teuw, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        tib__omfdq = element_type(S.data)
        dimpg__awmr = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(tib__omfdq, (types.Integer, types.Float)
            ) and tib__omfdq not in dimpg__awmr:
            raise BodoError(
                f'Series.{overload_name}(): series of type {tib__omfdq} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            iyr__peyci = bodo.libs.array_kernels.ffill_bfill_arr(oosm__tmik,
                vxird__fzpr)
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        cszha__yqz = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            cszha__yqz)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        beo__dvf = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(beo__dvf)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        beo__dvf = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(beo__dvf)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        beo__dvf = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(beo__dvf)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    bwegc__pzzoq = dict(inplace=inplace, limit=limit, regex=regex, method=
        method)
    nthjx__znbft = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', bwegc__pzzoq, nthjx__znbft,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    tib__omfdq = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        fzbb__wpxet = element_type(to_replace.key_type)
        xspqi__jbut = element_type(to_replace.value_type)
    else:
        fzbb__wpxet = element_type(to_replace)
        xspqi__jbut = element_type(value)
    uavq__wqj = None
    if tib__omfdq != types.unliteral(fzbb__wpxet):
        if bodo.utils.typing.equality_always_false(tib__omfdq, types.
            unliteral(fzbb__wpxet)
            ) or not bodo.utils.typing.types_equality_exists(tib__omfdq,
            fzbb__wpxet):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(tib__omfdq, (types.Float, types.Integer)
            ) or tib__omfdq == np.bool_:
            uavq__wqj = tib__omfdq
    if not can_replace(tib__omfdq, types.unliteral(xspqi__jbut)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    bffb__ilnxr = to_str_arr_if_dict_array(S.data)
    if isinstance(bffb__ilnxr, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(oosm__tmik.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(oosm__tmik)
        iyr__peyci = bodo.utils.utils.alloc_type(n, bffb__ilnxr, (-1,))
        iybxv__ssv = build_replace_dict(to_replace, value, uavq__wqj)
        for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(oosm__tmik, rvx__xjpc):
                bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                continue
            s = oosm__tmik[rvx__xjpc]
            if s in iybxv__ssv:
                s = iybxv__ssv[s]
            iyr__peyci[rvx__xjpc] = s
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    zhjzx__cwqsj = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    aav__ukvae = is_iterable_type(to_replace)
    idca__atfnv = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    qof__taxub = is_iterable_type(value)
    if zhjzx__cwqsj and idca__atfnv:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                iybxv__ssv = {}
                iybxv__ssv[key_dtype_conv(to_replace)] = value
                return iybxv__ssv
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            iybxv__ssv = {}
            iybxv__ssv[to_replace] = value
            return iybxv__ssv
        return impl
    if aav__ukvae and idca__atfnv:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                iybxv__ssv = {}
                for wlcws__edqtx in to_replace:
                    iybxv__ssv[key_dtype_conv(wlcws__edqtx)] = value
                return iybxv__ssv
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            iybxv__ssv = {}
            for wlcws__edqtx in to_replace:
                iybxv__ssv[wlcws__edqtx] = value
            return iybxv__ssv
        return impl
    if aav__ukvae and qof__taxub:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                iybxv__ssv = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for rvx__xjpc in range(len(to_replace)):
                    iybxv__ssv[key_dtype_conv(to_replace[rvx__xjpc])] = value[
                        rvx__xjpc]
                return iybxv__ssv
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            iybxv__ssv = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for rvx__xjpc in range(len(to_replace)):
                iybxv__ssv[to_replace[rvx__xjpc]] = value[rvx__xjpc]
            return iybxv__ssv
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
            iyr__peyci = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    bwegc__pzzoq = dict(ignore_index=ignore_index)
    uiqu__orco = dict(ignore_index=False)
    check_unsupported_args('Series.explode', bwegc__pzzoq, uiqu__orco,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yazub__tjlsp = bodo.utils.conversion.index_to_array(index)
        iyr__peyci, rab__lfjdm = bodo.libs.array_kernels.explode(arr,
            yazub__tjlsp)
        aikjj__rvwt = bodo.utils.conversion.index_from_array(rab__lfjdm)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
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
            vnlw__pydsl = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                vnlw__pydsl[rvx__xjpc] = np.argmax(a[rvx__xjpc])
            return vnlw__pydsl
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            yje__xgqfh = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                yje__xgqfh[rvx__xjpc] = np.argmin(a[rvx__xjpc])
            return yje__xgqfh
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
    bwegc__pzzoq = dict(axis=axis, inplace=inplace, how=how)
    ptjji__lfzh = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', bwegc__pzzoq, ptjji__lfzh,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            efi__qyu = S.notna().values
            yazub__tjlsp = bodo.utils.conversion.extract_index_array(S)
            aikjj__rvwt = bodo.utils.conversion.convert_to_index(yazub__tjlsp
                [efi__qyu])
            iyr__peyci = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(oosm__tmik))
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                aikjj__rvwt, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            yazub__tjlsp = bodo.utils.conversion.extract_index_array(S)
            efi__qyu = S.notna().values
            aikjj__rvwt = bodo.utils.conversion.convert_to_index(yazub__tjlsp
                [efi__qyu])
            iyr__peyci = oosm__tmik[efi__qyu]
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                aikjj__rvwt, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    bwegc__pzzoq = dict(freq=freq, axis=axis, fill_value=fill_value)
    oxdv__teuw = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', bwegc__pzzoq, oxdv__teuw,
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
        iyr__peyci = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    bwegc__pzzoq = dict(fill_method=fill_method, limit=limit, freq=freq)
    oxdv__teuw = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', bwegc__pzzoq, oxdv__teuw,
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
        iyr__peyci = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
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
            pgoc__fccg = 'None'
        else:
            pgoc__fccg = 'other'
        fbkdt__abvf = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            fbkdt__abvf += '  cond = ~cond\n'
        fbkdt__abvf += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        fbkdt__abvf += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        fbkdt__abvf += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        fbkdt__abvf += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {pgoc__fccg})
"""
        fbkdt__abvf += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        grqh__fjvs = {}
        exec(fbkdt__abvf, {'bodo': bodo, 'np': np}, grqh__fjvs)
        impl = grqh__fjvs['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        cszha__yqz = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(cszha__yqz)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    bwegc__pzzoq = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    oxdv__teuw = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', bwegc__pzzoq, oxdv__teuw,
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
    evdg__hkkl = is_overload_constant_nan(other)
    if not (is_default or evdg__hkkl or is_scalar_type(other) or isinstance
        (other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
        isinstance(other, SeriesType) and (isinstance(arr, types.Array) or 
        arr.dtype in [bodo.string_type, bodo.bytes_type]) or 
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
            amwju__otyig = arr.dtype.elem_type
        else:
            amwju__otyig = arr.dtype
        if is_iterable_type(other):
            tjq__jwuqc = other.dtype
        elif evdg__hkkl:
            tjq__jwuqc = types.float64
        else:
            tjq__jwuqc = types.unliteral(other)
        if not evdg__hkkl and not is_common_scalar_dtype([amwju__otyig,
            tjq__jwuqc]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        bwegc__pzzoq = dict(level=level, axis=axis)
        oxdv__teuw = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__),
            bwegc__pzzoq, oxdv__teuw, package_name='pandas', module_name=
            'Series')
        aje__wwg = other == string_type or is_overload_constant_str(other)
        lphos__rre = is_iterable_type(other) and other.dtype == string_type
        slmdt__haxva = S.dtype == string_type and (op == operator.add and (
            aje__wwg or lphos__rre) or op == operator.mul and isinstance(
            other, types.Integer))
        mnf__rzf = S.dtype == bodo.timedelta64ns
        stl__nfyv = S.dtype == bodo.datetime64ns
        hhybu__hjme = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        ofiot__siub = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        epw__gnc = mnf__rzf and (hhybu__hjme or ofiot__siub
            ) or stl__nfyv and hhybu__hjme
        epw__gnc = epw__gnc and op == operator.add
        if not (isinstance(S.dtype, types.Number) or slmdt__haxva or epw__gnc):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        roadk__txmmp = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            bffb__ilnxr = roadk__txmmp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and bffb__ilnxr == types.Array(types.bool_, 1, 'C'):
                bffb__ilnxr = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                iyr__peyci = bodo.utils.utils.alloc_type(n, bffb__ilnxr, (-1,))
                for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                    wfedq__wjs = bodo.libs.array_kernels.isna(arr, rvx__xjpc)
                    if wfedq__wjs:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc
                                )
                        else:
                            iyr__peyci[rvx__xjpc] = op(fill_value, other)
                    else:
                        iyr__peyci[rvx__xjpc] = op(arr[rvx__xjpc], other)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        bffb__ilnxr = roadk__txmmp.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and bffb__ilnxr == types.Array(
            types.bool_, 1, 'C'):
            bffb__ilnxr = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zux__hnqd = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            iyr__peyci = bodo.utils.utils.alloc_type(n, bffb__ilnxr, (-1,))
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                wfedq__wjs = bodo.libs.array_kernels.isna(arr, rvx__xjpc)
                wpngt__dgd = bodo.libs.array_kernels.isna(zux__hnqd, rvx__xjpc)
                if wfedq__wjs and wpngt__dgd:
                    bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                elif wfedq__wjs:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                    else:
                        iyr__peyci[rvx__xjpc] = op(fill_value, zux__hnqd[
                            rvx__xjpc])
                elif wpngt__dgd:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                    else:
                        iyr__peyci[rvx__xjpc] = op(arr[rvx__xjpc], fill_value)
                else:
                    iyr__peyci[rvx__xjpc] = op(arr[rvx__xjpc], zux__hnqd[
                        rvx__xjpc])
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
        roadk__txmmp = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            bffb__ilnxr = roadk__txmmp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and bffb__ilnxr == types.Array(types.bool_, 1, 'C'):
                bffb__ilnxr = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                iyr__peyci = bodo.utils.utils.alloc_type(n, bffb__ilnxr, None)
                for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                    wfedq__wjs = bodo.libs.array_kernels.isna(arr, rvx__xjpc)
                    if wfedq__wjs:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc
                                )
                        else:
                            iyr__peyci[rvx__xjpc] = op(other, fill_value)
                    else:
                        iyr__peyci[rvx__xjpc] = op(other, arr[rvx__xjpc])
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        bffb__ilnxr = roadk__txmmp.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and bffb__ilnxr == types.Array(
            types.bool_, 1, 'C'):
            bffb__ilnxr = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zux__hnqd = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            iyr__peyci = bodo.utils.utils.alloc_type(n, bffb__ilnxr, None)
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                wfedq__wjs = bodo.libs.array_kernels.isna(arr, rvx__xjpc)
                wpngt__dgd = bodo.libs.array_kernels.isna(zux__hnqd, rvx__xjpc)
                iyr__peyci[rvx__xjpc] = op(zux__hnqd[rvx__xjpc], arr[rvx__xjpc]
                    )
                if wfedq__wjs and wpngt__dgd:
                    bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                elif wfedq__wjs:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                    else:
                        iyr__peyci[rvx__xjpc] = op(zux__hnqd[rvx__xjpc],
                            fill_value)
                elif wpngt__dgd:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                    else:
                        iyr__peyci[rvx__xjpc] = op(fill_value, arr[rvx__xjpc])
                else:
                    iyr__peyci[rvx__xjpc] = op(zux__hnqd[rvx__xjpc], arr[
                        rvx__xjpc])
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
    for op, ims__qwdg in explicit_binop_funcs_two_ways.items():
        for name in ims__qwdg:
            cszha__yqz = create_explicit_binary_op_overload(op)
            sae__xkh = create_explicit_binary_reverse_op_overload(op)
            mzc__yihxx = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(cszha__yqz)
            overload_method(SeriesType, mzc__yihxx, no_unliteral=True)(sae__xkh
                )
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        cszha__yqz = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(cszha__yqz)
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
                huqj__khy = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                iyr__peyci = dt64_arr_sub(arr, huqj__khy)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
                iyr__peyci = np.empty(n, np.dtype('datetime64[ns]'))
                for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, rvx__xjpc):
                        bodo.libs.array_kernels.setna(iyr__peyci, rvx__xjpc)
                        continue
                    ivy__diuex = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[rvx__xjpc]))
                    ilr__yha = op(ivy__diuex, rhs)
                    iyr__peyci[rvx__xjpc
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ilr__yha.value)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
                    huqj__khy = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    iyr__peyci = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(huqj__khy))
                    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                huqj__khy = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                iyr__peyci = op(arr, huqj__khy)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    kfpqu__zig = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    iyr__peyci = op(bodo.utils.conversion.
                        unbox_if_timestamp(kfpqu__zig), arr)
                    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kfpqu__zig = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                iyr__peyci = op(kfpqu__zig, arr)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        cszha__yqz = create_binary_op_overload(op)
        overload(op)(cszha__yqz)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    dnceu__xvh = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, dnceu__xvh)
        for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, rvx__xjpc
                ) or bodo.libs.array_kernels.isna(arg2, rvx__xjpc):
                bodo.libs.array_kernels.setna(S, rvx__xjpc)
                continue
            S[rvx__xjpc
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                rvx__xjpc]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[rvx__xjpc]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                zux__hnqd = bodo.utils.conversion.get_array_if_series_or_index(
                    other)
                op(arr, zux__hnqd)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        cszha__yqz = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(cszha__yqz)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                iyr__peyci = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        cszha__yqz = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(cszha__yqz)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    iyr__peyci = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
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
                    zux__hnqd = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    iyr__peyci = ufunc(arr, zux__hnqd)
                    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    zux__hnqd = bodo.hiframes.pd_series_ext.get_series_data(S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    iyr__peyci = ufunc(arr, zux__hnqd)
                    return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        cszha__yqz = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(cszha__yqz)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        yfnts__fax = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        ljhzv__hiu = np.arange(n),
        bodo.libs.timsort.sort(yfnts__fax, 0, n, ljhzv__hiu)
        return ljhzv__hiu[0]
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
        qftf__pmtb = get_overload_const_str(downcast)
        if qftf__pmtb in ('integer', 'signed'):
            out_dtype = types.int64
        elif qftf__pmtb == 'unsigned':
            out_dtype = types.uint64
        else:
            assert qftf__pmtb == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            oosm__tmik = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            iyr__peyci = pd.to_numeric(oosm__tmik, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            snzzz__kcpj = np.empty(n, np.float64)
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, rvx__xjpc):
                    bodo.libs.array_kernels.setna(snzzz__kcpj, rvx__xjpc)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(snzzz__kcpj,
                        rvx__xjpc, arg_a, rvx__xjpc)
            return snzzz__kcpj
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            snzzz__kcpj = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, rvx__xjpc):
                    bodo.libs.array_kernels.setna(snzzz__kcpj, rvx__xjpc)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(snzzz__kcpj,
                        rvx__xjpc, arg_a, rvx__xjpc)
            return snzzz__kcpj
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        vnl__xtk = if_series_to_array_type(args[0])
        if isinstance(vnl__xtk, types.Array) and isinstance(vnl__xtk.dtype,
            types.Integer):
            vnl__xtk = types.Array(types.float64, 1, 'C')
        return vnl__xtk(*args)


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
    fik__rhwwg = bodo.utils.utils.is_array_typ(x, True)
    eiyvb__act = bodo.utils.utils.is_array_typ(y, True)
    fbkdt__abvf = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        fbkdt__abvf += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if fik__rhwwg and not bodo.utils.utils.is_array_typ(x, False):
        fbkdt__abvf += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if eiyvb__act and not bodo.utils.utils.is_array_typ(y, False):
        fbkdt__abvf += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    fbkdt__abvf += '  n = len(condition)\n'
    fhe__efz = x.dtype if fik__rhwwg else types.unliteral(x)
    ocjn__suhqo = y.dtype if eiyvb__act else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        fhe__efz = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        ocjn__suhqo = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    ttni__oxyg = get_data(x)
    paym__iex = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(ljhzv__hiu) for
        ljhzv__hiu in [ttni__oxyg, paym__iex])
    if paym__iex == types.none:
        if isinstance(fhe__efz, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif ttni__oxyg == paym__iex and not is_nullable:
        out_dtype = dtype_to_array_type(fhe__efz)
    elif fhe__efz == string_type or ocjn__suhqo == string_type:
        out_dtype = bodo.string_array_type
    elif ttni__oxyg == bytes_type or (fik__rhwwg and fhe__efz == bytes_type
        ) and (paym__iex == bytes_type or eiyvb__act and ocjn__suhqo ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(fhe__efz, bodo.PDCategoricalDtype):
        out_dtype = None
    elif fhe__efz in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(fhe__efz, 1, 'C')
    elif ocjn__suhqo in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(ocjn__suhqo, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(fhe__efz), numba.np.numpy_support.
            as_dtype(ocjn__suhqo)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(fhe__efz, bodo.PDCategoricalDtype):
        vkqc__tfyla = 'x'
    else:
        vkqc__tfyla = 'out_dtype'
    fbkdt__abvf += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {vkqc__tfyla}, (-1,))\n')
    if isinstance(fhe__efz, bodo.PDCategoricalDtype):
        fbkdt__abvf += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        fbkdt__abvf += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    fbkdt__abvf += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    fbkdt__abvf += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if fik__rhwwg:
        fbkdt__abvf += '      if bodo.libs.array_kernels.isna(x, j):\n'
        fbkdt__abvf += '        setna(out_arr, j)\n'
        fbkdt__abvf += '        continue\n'
    if isinstance(fhe__efz, bodo.PDCategoricalDtype):
        fbkdt__abvf += '      out_codes[j] = x_codes[j]\n'
    else:
        fbkdt__abvf += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if fik__rhwwg else 'x'))
    fbkdt__abvf += '    else:\n'
    if eiyvb__act:
        fbkdt__abvf += '      if bodo.libs.array_kernels.isna(y, j):\n'
        fbkdt__abvf += '        setna(out_arr, j)\n'
        fbkdt__abvf += '        continue\n'
    if paym__iex == types.none:
        if isinstance(fhe__efz, bodo.PDCategoricalDtype):
            fbkdt__abvf += '      out_codes[j] = -1\n'
        else:
            fbkdt__abvf += '      setna(out_arr, j)\n'
    else:
        fbkdt__abvf += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if eiyvb__act else 'y'))
    fbkdt__abvf += '  return out_arr\n'
    grqh__fjvs = {}
    exec(fbkdt__abvf, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, grqh__fjvs)
    tfq__ghpn = grqh__fjvs['_impl']
    return tfq__ghpn


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
        enjb__ardqx = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(enjb__ardqx, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(enjb__ardqx):
            abng__hbmhw = enjb__ardqx.data.dtype
        else:
            abng__hbmhw = enjb__ardqx.dtype
        if isinstance(abng__hbmhw, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        doiol__pcdb = enjb__ardqx
    else:
        gqv__bel = []
        for enjb__ardqx in choicelist:
            if not bodo.utils.utils.is_array_typ(enjb__ardqx, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(enjb__ardqx):
                abng__hbmhw = enjb__ardqx.data.dtype
            else:
                abng__hbmhw = enjb__ardqx.dtype
            if isinstance(abng__hbmhw, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            gqv__bel.append(abng__hbmhw)
        if not is_common_scalar_dtype(gqv__bel):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        doiol__pcdb = choicelist[0]
    if is_series_type(doiol__pcdb):
        doiol__pcdb = doiol__pcdb.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, doiol__pcdb.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(doiol__pcdb, types.Array) or isinstance(doiol__pcdb,
        BooleanArrayType) or isinstance(doiol__pcdb, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(doiol__pcdb, False) and doiol__pcdb.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {doiol__pcdb} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    dswn__ajydj = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        uhmoe__bvvrn = choicelist.dtype
    else:
        qqirh__hljmy = False
        gqv__bel = []
        for enjb__ardqx in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                enjb__ardqx, 'numpy.select()')
            if is_nullable_type(enjb__ardqx):
                qqirh__hljmy = True
            if is_series_type(enjb__ardqx):
                abng__hbmhw = enjb__ardqx.data.dtype
            else:
                abng__hbmhw = enjb__ardqx.dtype
            if isinstance(abng__hbmhw, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            gqv__bel.append(abng__hbmhw)
        rkis__mlf, rczun__gegy = get_common_scalar_dtype(gqv__bel)
        if not rczun__gegy:
            raise BodoError('Internal error in overload_np_select')
        rnrs__vxj = dtype_to_array_type(rkis__mlf)
        if qqirh__hljmy:
            rnrs__vxj = to_nullable_type(rnrs__vxj)
        uhmoe__bvvrn = rnrs__vxj
    if isinstance(uhmoe__bvvrn, SeriesType):
        uhmoe__bvvrn = uhmoe__bvvrn.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        fyco__ipfaf = True
    else:
        fyco__ipfaf = False
    todqi__poyjm = False
    rauu__ybxzj = False
    if fyco__ipfaf:
        if isinstance(uhmoe__bvvrn.dtype, types.Number):
            pass
        elif uhmoe__bvvrn.dtype == types.bool_:
            rauu__ybxzj = True
        else:
            todqi__poyjm = True
            uhmoe__bvvrn = to_nullable_type(uhmoe__bvvrn)
    elif default == types.none or is_overload_constant_nan(default):
        todqi__poyjm = True
        uhmoe__bvvrn = to_nullable_type(uhmoe__bvvrn)
    fbkdt__abvf = 'def np_select_impl(condlist, choicelist, default=0):\n'
    fbkdt__abvf += '  if len(condlist) != len(choicelist):\n'
    fbkdt__abvf += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    fbkdt__abvf += '  output_len = len(choicelist[0])\n'
    fbkdt__abvf += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    fbkdt__abvf += '  for i in range(output_len):\n'
    if todqi__poyjm:
        fbkdt__abvf += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif rauu__ybxzj:
        fbkdt__abvf += '    out[i] = False\n'
    else:
        fbkdt__abvf += '    out[i] = default\n'
    if dswn__ajydj:
        fbkdt__abvf += '  for i in range(len(condlist) - 1, -1, -1):\n'
        fbkdt__abvf += '    cond = condlist[i]\n'
        fbkdt__abvf += '    choice = choicelist[i]\n'
        fbkdt__abvf += '    out = np.where(cond, choice, out)\n'
    else:
        for rvx__xjpc in range(len(choicelist) - 1, -1, -1):
            fbkdt__abvf += f'  cond = condlist[{rvx__xjpc}]\n'
            fbkdt__abvf += f'  choice = choicelist[{rvx__xjpc}]\n'
            fbkdt__abvf += f'  out = np.where(cond, choice, out)\n'
    fbkdt__abvf += '  return out'
    grqh__fjvs = dict()
    exec(fbkdt__abvf, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': uhmoe__bvvrn}, grqh__fjvs)
    impl = grqh__fjvs['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        iyr__peyci = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    bwegc__pzzoq = dict(subset=subset, keep=keep, inplace=inplace)
    oxdv__teuw = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', bwegc__pzzoq,
        oxdv__teuw, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        ccto__bnf = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (ccto__bnf,), yazub__tjlsp = bodo.libs.array_kernels.drop_duplicates((
            ccto__bnf,), index, 1)
        index = bodo.utils.conversion.index_from_array(yazub__tjlsp)
        return bodo.hiframes.pd_series_ext.init_series(ccto__bnf, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    kyg__gpddo = element_type(S.data)
    if not is_common_scalar_dtype([kyg__gpddo, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([kyg__gpddo, right]):
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
        iyr__peyci = np.empty(n, np.bool_)
        for rvx__xjpc in numba.parfors.parfor.internal_prange(n):
            kflw__img = bodo.utils.conversion.box_if_dt64(arr[rvx__xjpc])
            if inclusive == 'both':
                iyr__peyci[rvx__xjpc
                    ] = kflw__img <= right and kflw__img >= left
            else:
                iyr__peyci[rvx__xjpc] = kflw__img < right and kflw__img > left
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    bwegc__pzzoq = dict(axis=axis)
    oxdv__teuw = dict(axis=None)
    check_unsupported_args('Series.repeat', bwegc__pzzoq, oxdv__teuw,
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
            yazub__tjlsp = bodo.utils.conversion.index_to_array(index)
            iyr__peyci = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            rab__lfjdm = bodo.libs.array_kernels.repeat_kernel(yazub__tjlsp,
                repeats)
            aikjj__rvwt = bodo.utils.conversion.index_from_array(rab__lfjdm)
            return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
                aikjj__rvwt, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yazub__tjlsp = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        iyr__peyci = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        rab__lfjdm = bodo.libs.array_kernels.repeat_kernel(yazub__tjlsp,
            repeats)
        aikjj__rvwt = bodo.utils.conversion.index_from_array(rab__lfjdm)
        return bodo.hiframes.pd_series_ext.init_series(iyr__peyci,
            aikjj__rvwt, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        ljhzv__hiu = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(ljhzv__hiu)
        oik__izm = {}
        for rvx__xjpc in range(n):
            kflw__img = bodo.utils.conversion.box_if_dt64(ljhzv__hiu[rvx__xjpc]
                )
            oik__izm[index[rvx__xjpc]] = kflw__img
        return oik__izm
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    jyz__jwpwn = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            yong__vjp = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(jyz__jwpwn)
    elif is_literal_type(name):
        yong__vjp = get_literal_value(name)
    else:
        raise_bodo_error(jyz__jwpwn)
    yong__vjp = 0 if yong__vjp is None else yong__vjp
    pnh__mwtb = ColNamesMetaType((yong__vjp,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            pnh__mwtb)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
