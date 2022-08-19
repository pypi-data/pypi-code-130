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
            zvuni__hmw = bodo.hiframes.pd_series_ext.get_series_data(s)
            zfb__rmnql = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                zvuni__hmw)
            return zfb__rmnql
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
            cjsj__jfc = list()
            for xgw__fcupm in range(len(S)):
                cjsj__jfc.append(S.iat[xgw__fcupm])
            return cjsj__jfc
        return impl_float

    def impl(S):
        cjsj__jfc = list()
        for xgw__fcupm in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, xgw__fcupm):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            cjsj__jfc.append(S.iat[xgw__fcupm])
        return cjsj__jfc
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    cua__cjzo = dict(dtype=dtype, copy=copy, na_value=na_value)
    uxj__ygnp = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    cua__cjzo = dict(name=name, inplace=inplace)
    uxj__ygnp = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', cua__cjzo, uxj__ygnp,
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
        lnt__zlpcu = ', '.join(['index_arrs[{}]'.format(xgw__fcupm) for
            xgw__fcupm in range(S.index.nlevels)])
    else:
        lnt__zlpcu = '    bodo.utils.conversion.index_to_array(index)\n'
    dmu__bvum = 'index' if 'index' != series_name else 'level_0'
    bgx__tvrpt = get_index_names(S.index, 'Series.reset_index()', dmu__bvum)
    columns = [name for name in bgx__tvrpt]
    columns.append(series_name)
    nblnr__zsk = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    nblnr__zsk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    nblnr__zsk += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        nblnr__zsk += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    nblnr__zsk += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    nblnr__zsk += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({lnt__zlpcu}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    ckbf__lul = {}
    exec(nblnr__zsk, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, ckbf__lul)
    tknc__mjji = ckbf__lul['_impl']
    return tknc__mjji


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
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
        wtw__wsixf = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[xgw__fcupm]):
                bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
            else:
                wtw__wsixf[xgw__fcupm] = np.round(arr[xgw__fcupm], decimals)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    uxj__ygnp = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
        hnbfg__iiszr = bodo.hiframes.pd_series_ext.get_series_data(S)
        bnime__hizkc = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        edev__hdhr = 0
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(
            hnbfg__iiszr)):
            ciqh__iuk = 0
            rnuu__yoc = bodo.libs.array_kernels.isna(hnbfg__iiszr, xgw__fcupm)
            baumr__qetuf = bodo.libs.array_kernels.isna(bnime__hizkc,
                xgw__fcupm)
            if (rnuu__yoc and not baumr__qetuf or not rnuu__yoc and
                baumr__qetuf):
                ciqh__iuk = 1
            elif not rnuu__yoc:
                if hnbfg__iiszr[xgw__fcupm] != bnime__hizkc[xgw__fcupm]:
                    ciqh__iuk = 1
            edev__hdhr += ciqh__iuk
        return edev__hdhr == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    cua__cjzo = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    uxj__ygnp = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    cua__cjzo = dict(level=level)
    uxj__ygnp = dict(level=None)
    check_unsupported_args('Series.mad', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    kxnv__blm = types.float64
    wnepr__ekt = types.float64
    if S.dtype == types.float32:
        kxnv__blm = types.float32
        wnepr__ekt = types.float32
    yfcbe__shx = kxnv__blm(0)
    ttna__frvm = wnepr__ekt(0)
    ulcus__kav = wnepr__ekt(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        vbs__ryt = yfcbe__shx
        edev__hdhr = ttna__frvm
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(A)):
            ciqh__iuk = yfcbe__shx
            uvgf__zzx = ttna__frvm
            if not bodo.libs.array_kernels.isna(A, xgw__fcupm) or not skipna:
                ciqh__iuk = A[xgw__fcupm]
                uvgf__zzx = ulcus__kav
            vbs__ryt += ciqh__iuk
            edev__hdhr += uvgf__zzx
        ezrv__ztlz = bodo.hiframes.series_kernels._mean_handle_nan(vbs__ryt,
            edev__hdhr)
        vugn__iyj = yfcbe__shx
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(A)):
            ciqh__iuk = yfcbe__shx
            if not bodo.libs.array_kernels.isna(A, xgw__fcupm) or not skipna:
                ciqh__iuk = abs(A[xgw__fcupm] - ezrv__ztlz)
            vugn__iyj += ciqh__iuk
        otkv__fwkc = bodo.hiframes.series_kernels._mean_handle_nan(vugn__iyj,
            edev__hdhr)
        return otkv__fwkc
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    cua__cjzo = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
        ooqg__bfbp = 0
        ztkgf__pppc = 0
        edev__hdhr = 0
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(A)):
            ciqh__iuk = 0
            uvgf__zzx = 0
            if not bodo.libs.array_kernels.isna(A, xgw__fcupm) or not skipna:
                ciqh__iuk = A[xgw__fcupm]
                uvgf__zzx = 1
            ooqg__bfbp += ciqh__iuk
            ztkgf__pppc += ciqh__iuk * ciqh__iuk
            edev__hdhr += uvgf__zzx
        xvnmk__list = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            ooqg__bfbp, ztkgf__pppc, edev__hdhr, ddof)
        mjvxn__eqoz = bodo.hiframes.series_kernels._sem_handle_nan(xvnmk__list,
            edev__hdhr)
        return mjvxn__eqoz
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', cua__cjzo, uxj__ygnp,
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
        ooqg__bfbp = 0.0
        ztkgf__pppc = 0.0
        vpz__qnr = 0.0
        ehapm__ywjo = 0.0
        edev__hdhr = 0
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(A)):
            ciqh__iuk = 0.0
            uvgf__zzx = 0
            if not bodo.libs.array_kernels.isna(A, xgw__fcupm) or not skipna:
                ciqh__iuk = np.float64(A[xgw__fcupm])
                uvgf__zzx = 1
            ooqg__bfbp += ciqh__iuk
            ztkgf__pppc += ciqh__iuk ** 2
            vpz__qnr += ciqh__iuk ** 3
            ehapm__ywjo += ciqh__iuk ** 4
            edev__hdhr += uvgf__zzx
        xvnmk__list = bodo.hiframes.series_kernels.compute_kurt(ooqg__bfbp,
            ztkgf__pppc, vpz__qnr, ehapm__ywjo, edev__hdhr)
        return xvnmk__list
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', cua__cjzo, uxj__ygnp,
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
        ooqg__bfbp = 0.0
        ztkgf__pppc = 0.0
        vpz__qnr = 0.0
        edev__hdhr = 0
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(A)):
            ciqh__iuk = 0.0
            uvgf__zzx = 0
            if not bodo.libs.array_kernels.isna(A, xgw__fcupm) or not skipna:
                ciqh__iuk = np.float64(A[xgw__fcupm])
                uvgf__zzx = 1
            ooqg__bfbp += ciqh__iuk
            ztkgf__pppc += ciqh__iuk ** 2
            vpz__qnr += ciqh__iuk ** 3
            edev__hdhr += uvgf__zzx
        xvnmk__list = bodo.hiframes.series_kernels.compute_skew(ooqg__bfbp,
            ztkgf__pppc, vpz__qnr, edev__hdhr)
        return xvnmk__list
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
        hnbfg__iiszr = bodo.hiframes.pd_series_ext.get_series_data(S)
        bnime__hizkc = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        zee__xtp = 0
        for xgw__fcupm in numba.parfors.parfor.internal_prange(len(
            hnbfg__iiszr)):
            toex__lgnb = hnbfg__iiszr[xgw__fcupm]
            njcd__phwsv = bnime__hizkc[xgw__fcupm]
            zee__xtp += toex__lgnb * njcd__phwsv
        return zee__xtp
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    cua__cjzo = dict(skipna=skipna)
    uxj__ygnp = dict(skipna=True)
    check_unsupported_args('Series.cumsum', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(skipna=skipna)
    uxj__ygnp = dict(skipna=True)
    check_unsupported_args('Series.cumprod', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(skipna=skipna)
    uxj__ygnp = dict(skipna=True)
    check_unsupported_args('Series.cummin', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(skipna=skipna)
    uxj__ygnp = dict(skipna=True)
    check_unsupported_args('Series.cummax', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    uxj__ygnp = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        lmh__dqys = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, lmh__dqys, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    cua__cjzo = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    uxj__ygnp = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(level=level)
    uxj__ygnp = dict(level=None)
    check_unsupported_args('Series.count', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    cua__cjzo = dict(method=method, min_periods=min_periods)
    uxj__ygnp = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        vnuk__edbgt = S.sum()
        rdbq__slxyx = other.sum()
        a = n * (S * other).sum() - vnuk__edbgt * rdbq__slxyx
        izsu__thmsa = n * (S ** 2).sum() - vnuk__edbgt ** 2
        nmnqk__hae = n * (other ** 2).sum() - rdbq__slxyx ** 2
        return a / np.sqrt(izsu__thmsa * nmnqk__hae)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    cua__cjzo = dict(min_periods=min_periods)
    uxj__ygnp = dict(min_periods=None)
    check_unsupported_args('Series.cov', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        vnuk__edbgt = S.mean()
        rdbq__slxyx = other.mean()
        wnr__thpz = ((S - vnuk__edbgt) * (other - rdbq__slxyx)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(wnr__thpz, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            untao__xalk = np.sign(sum_val)
            return np.inf * untao__xalk
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    cua__cjzo = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
    cua__cjzo = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='Series')
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
    cua__cjzo = dict(axis=axis, skipna=skipna)
    uxj__ygnp = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(axis=axis, skipna=skipna)
    uxj__ygnp = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', cua__cjzo, uxj__ygnp,
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
    cua__cjzo = dict(level=level, numeric_only=numeric_only)
    uxj__ygnp = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', cua__cjzo, uxj__ygnp,
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
        czp__bgfa = arr[:n]
        nawrl__ugfc = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(czp__bgfa,
            nawrl__ugfc, name)
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
        gojmw__nqm = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        czp__bgfa = arr[gojmw__nqm:]
        nawrl__ugfc = index[gojmw__nqm:]
        return bodo.hiframes.pd_series_ext.init_series(czp__bgfa,
            nawrl__ugfc, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    vbs__rxua = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in vbs__rxua:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            dvge__pown = index[0]
            hbxzu__xabju = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                dvge__pown, False))
        else:
            hbxzu__xabju = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        czp__bgfa = arr[:hbxzu__xabju]
        nawrl__ugfc = index[:hbxzu__xabju]
        return bodo.hiframes.pd_series_ext.init_series(czp__bgfa,
            nawrl__ugfc, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    vbs__rxua = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in vbs__rxua:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            otc__nyb = index[-1]
            hbxzu__xabju = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, otc__nyb,
                True))
        else:
            hbxzu__xabju = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        czp__bgfa = arr[len(arr) - hbxzu__xabju:]
        nawrl__ugfc = index[len(arr) - hbxzu__xabju:]
        return bodo.hiframes.pd_series_ext.init_series(czp__bgfa,
            nawrl__ugfc, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kusz__ttsb = bodo.utils.conversion.index_to_array(index)
        snf__skcki, hhydr__edh = (bodo.libs.array_kernels.
            first_last_valid_index(arr, kusz__ttsb))
        return hhydr__edh if snf__skcki else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kusz__ttsb = bodo.utils.conversion.index_to_array(index)
        snf__skcki, hhydr__edh = (bodo.libs.array_kernels.
            first_last_valid_index(arr, kusz__ttsb, False))
        return hhydr__edh if snf__skcki else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    cua__cjzo = dict(keep=keep)
    uxj__ygnp = dict(keep='first')
    check_unsupported_args('Series.nlargest', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kusz__ttsb = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf, rfey__laa = bodo.libs.array_kernels.nlargest(arr,
            kusz__ttsb, n, True, bodo.hiframes.series_kernels.gt_f)
        ajekt__ivsj = bodo.utils.conversion.convert_to_index(rfey__laa)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    cua__cjzo = dict(keep=keep)
    uxj__ygnp = dict(keep='first')
    check_unsupported_args('Series.nsmallest', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kusz__ttsb = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf, rfey__laa = bodo.libs.array_kernels.nlargest(arr,
            kusz__ttsb, n, False, bodo.hiframes.series_kernels.lt_f)
        ajekt__ivsj = bodo.utils.conversion.convert_to_index(rfey__laa)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
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
    cua__cjzo = dict(errors=errors)
    uxj__ygnp = dict(errors='raise')
    check_unsupported_args('Series.astype', cua__cjzo, uxj__ygnp,
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
        wtw__wsixf = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    cua__cjzo = dict(axis=axis, is_copy=is_copy)
    uxj__ygnp = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        zax__wybie = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[zax__wybie],
            index[zax__wybie], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    cua__cjzo = dict(axis=axis, kind=kind, order=order)
    uxj__ygnp = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dbl__cuwfe = S.notna().values
        if not dbl__cuwfe.all():
            wtw__wsixf = np.full(n, -1, np.int64)
            wtw__wsixf[dbl__cuwfe] = argsort(arr[dbl__cuwfe])
        else:
            wtw__wsixf = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    cua__cjzo = dict(axis=axis, numeric_only=numeric_only)
    uxj__ygnp = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', cua__cjzo, uxj__ygnp,
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
        wtw__wsixf = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    cua__cjzo = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    uxj__ygnp = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    aoh__krji = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gcl__dkwvf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, aoh__krji)
        uulsm__fzf = gcl__dkwvf.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        wtw__wsixf = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            uulsm__fzf, 0)
        ajekt__ivsj = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            uulsm__fzf)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    cua__cjzo = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    uxj__ygnp = dict(axis=0, inplace=False, kind='quicksort', ignore_index=
        False, key=None)
    check_unsupported_args('Series.sort_values', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    dmf__sbt = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        gcl__dkwvf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, dmf__sbt)
        uulsm__fzf = gcl__dkwvf.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        wtw__wsixf = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            uulsm__fzf, 0)
        ajekt__ivsj = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            uulsm__fzf)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    hpdrt__zmkpl = is_overload_true(is_nullable)
    nblnr__zsk = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    nblnr__zsk += '  numba.parfors.parfor.init_prange()\n'
    nblnr__zsk += '  n = len(arr)\n'
    if hpdrt__zmkpl:
        nblnr__zsk += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        nblnr__zsk += '  out_arr = np.empty(n, np.int64)\n'
    nblnr__zsk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    nblnr__zsk += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if hpdrt__zmkpl:
        nblnr__zsk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        nblnr__zsk += '      out_arr[i] = -1\n'
    nblnr__zsk += '      continue\n'
    nblnr__zsk += '    val = arr[i]\n'
    nblnr__zsk += '    if include_lowest and val == bins[0]:\n'
    nblnr__zsk += '      ind = 1\n'
    nblnr__zsk += '    else:\n'
    nblnr__zsk += '      ind = np.searchsorted(bins, val)\n'
    nblnr__zsk += '    if ind == 0 or ind == len(bins):\n'
    if hpdrt__zmkpl:
        nblnr__zsk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        nblnr__zsk += '      out_arr[i] = -1\n'
    nblnr__zsk += '    else:\n'
    nblnr__zsk += '      out_arr[i] = ind - 1\n'
    nblnr__zsk += '  return out_arr\n'
    ckbf__lul = {}
    exec(nblnr__zsk, {'bodo': bodo, 'np': np, 'numba': numba}, ckbf__lul)
    impl = ckbf__lul['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        wfz__qvp, kuie__pxq = np.divmod(x, 1)
        if wfz__qvp == 0:
            xjm__ezyq = -int(np.floor(np.log10(abs(kuie__pxq)))
                ) - 1 + precision
        else:
            xjm__ezyq = precision
        return np.around(x, xjm__ezyq)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        xtow__dryhs = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(xtow__dryhs)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        pztl__hkm = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            vusl__pjje = bins.copy()
            if right and include_lowest:
                vusl__pjje[0] = vusl__pjje[0] - pztl__hkm
            ojl__qme = bodo.libs.interval_arr_ext.init_interval_array(
                vusl__pjje[:-1], vusl__pjje[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(ojl__qme,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        vusl__pjje = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            vusl__pjje[0] = vusl__pjje[0] - 10.0 ** -precision
        ojl__qme = bodo.libs.interval_arr_ext.init_interval_array(vusl__pjje
            [:-1], vusl__pjje[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(ojl__qme, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        kbmt__jkx = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        mti__fekij = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        wtw__wsixf = np.zeros(nbins, np.int64)
        for xgw__fcupm in range(len(kbmt__jkx)):
            wtw__wsixf[mti__fekij[xgw__fcupm]] = kbmt__jkx[xgw__fcupm]
        return wtw__wsixf
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
            wjjbv__dboza = (max_val - min_val) * 0.001
            if right:
                bins[0] -= wjjbv__dboza
            else:
                bins[-1] += wjjbv__dboza
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    cua__cjzo = dict(dropna=dropna)
    uxj__ygnp = dict(dropna=True)
    check_unsupported_args('Series.value_counts', cua__cjzo, uxj__ygnp,
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
    mxi__suzz = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    nblnr__zsk = 'def impl(\n'
    nblnr__zsk += '    S,\n'
    nblnr__zsk += '    normalize=False,\n'
    nblnr__zsk += '    sort=True,\n'
    nblnr__zsk += '    ascending=False,\n'
    nblnr__zsk += '    bins=None,\n'
    nblnr__zsk += '    dropna=True,\n'
    nblnr__zsk += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    nblnr__zsk += '):\n'
    nblnr__zsk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    nblnr__zsk += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    nblnr__zsk += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if mxi__suzz:
        nblnr__zsk += '    right = True\n'
        nblnr__zsk += _gen_bins_handling(bins, S.dtype)
        nblnr__zsk += '    arr = get_bin_inds(bins, arr)\n'
    nblnr__zsk += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    nblnr__zsk += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    nblnr__zsk += '    )\n'
    nblnr__zsk += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if mxi__suzz:
        nblnr__zsk += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        nblnr__zsk += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        nblnr__zsk += '    index = get_bin_labels(bins)\n'
    else:
        nblnr__zsk += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        nblnr__zsk += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        nblnr__zsk += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        nblnr__zsk += '    )\n'
        nblnr__zsk += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    nblnr__zsk += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        nblnr__zsk += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        jvsr__avyp = 'len(S)' if mxi__suzz else 'count_arr.sum()'
        nblnr__zsk += f'    res = res / float({jvsr__avyp})\n'
    nblnr__zsk += '    return res\n'
    ckbf__lul = {}
    exec(nblnr__zsk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, ckbf__lul)
    impl = ckbf__lul['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    nblnr__zsk = ''
    if isinstance(bins, types.Integer):
        nblnr__zsk += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        nblnr__zsk += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            nblnr__zsk += '    min_val = min_val.value\n'
            nblnr__zsk += '    max_val = max_val.value\n'
        nblnr__zsk += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            nblnr__zsk += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        nblnr__zsk += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return nblnr__zsk


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    cua__cjzo = dict(right=right, labels=labels, retbins=retbins, precision
        =precision, duplicates=duplicates, ordered=ordered)
    uxj__ygnp = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', cua__cjzo, uxj__ygnp, package_name
        ='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    nblnr__zsk = 'def impl(\n'
    nblnr__zsk += '    x,\n'
    nblnr__zsk += '    bins,\n'
    nblnr__zsk += '    right=True,\n'
    nblnr__zsk += '    labels=None,\n'
    nblnr__zsk += '    retbins=False,\n'
    nblnr__zsk += '    precision=3,\n'
    nblnr__zsk += '    include_lowest=False,\n'
    nblnr__zsk += "    duplicates='raise',\n"
    nblnr__zsk += '    ordered=True\n'
    nblnr__zsk += '):\n'
    if isinstance(x, SeriesType):
        nblnr__zsk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        nblnr__zsk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        nblnr__zsk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        nblnr__zsk += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    nblnr__zsk += _gen_bins_handling(bins, x.dtype)
    nblnr__zsk += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    nblnr__zsk += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    nblnr__zsk += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    nblnr__zsk += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        nblnr__zsk += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        nblnr__zsk += '    return res\n'
    else:
        nblnr__zsk += '    return out_arr\n'
    ckbf__lul = {}
    exec(nblnr__zsk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, ckbf__lul)
    impl = ckbf__lul['impl']
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
    cua__cjzo = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    uxj__ygnp = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        gtb__pqiy = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, gtb__pqiy)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    cua__cjzo = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    uxj__ygnp = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', cua__cjzo, uxj__ygnp,
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
        mgxht__abxpg = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            qcnb__bbij = bodo.utils.conversion.coerce_to_array(index)
            gcl__dkwvf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                qcnb__bbij, arr), index, mgxht__abxpg)
            return gcl__dkwvf.groupby(' ')['']
        return impl_index
    hzh__zslr = by
    if isinstance(by, SeriesType):
        hzh__zslr = by.data
    if isinstance(hzh__zslr, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    whw__tyqw = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        qcnb__bbij = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        gcl__dkwvf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            qcnb__bbij, arr), index, whw__tyqw)
        return gcl__dkwvf.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    cua__cjzo = dict(verify_integrity=verify_integrity)
    uxj__ygnp = dict(verify_integrity=False)
    check_unsupported_args('Series.append', cua__cjzo, uxj__ygnp,
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
            yrwz__hnzdf = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            wtw__wsixf = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(wtw__wsixf, A, yrwz__hnzdf, False)
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    cua__cjzo = dict(interpolation=interpolation)
    uxj__ygnp = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            wtw__wsixf = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
        rgqu__lanh = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(rgqu__lanh, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    cua__cjzo = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    uxj__ygnp = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', cua__cjzo, uxj__ygnp,
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
        fsy__xyr = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fsy__xyr = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    nblnr__zsk = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {fsy__xyr}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    vvzqz__tfvk = dict()
    exec(nblnr__zsk, {'bodo': bodo, 'numba': numba}, vvzqz__tfvk)
    grxn__dqg = vvzqz__tfvk['impl']
    return grxn__dqg


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        fsy__xyr = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fsy__xyr = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    nblnr__zsk = 'def impl(S,\n'
    nblnr__zsk += '     value=None,\n'
    nblnr__zsk += '    method=None,\n'
    nblnr__zsk += '    axis=None,\n'
    nblnr__zsk += '    inplace=False,\n'
    nblnr__zsk += '    limit=None,\n'
    nblnr__zsk += '   downcast=None,\n'
    nblnr__zsk += '):\n'
    nblnr__zsk += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    nblnr__zsk += '    n = len(in_arr)\n'
    nblnr__zsk += f'    out_arr = {fsy__xyr}(n, -1)\n'
    nblnr__zsk += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    nblnr__zsk += '        s = in_arr[j]\n'
    nblnr__zsk += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    nblnr__zsk += '            s = value\n'
    nblnr__zsk += '        out_arr[j] = s\n'
    nblnr__zsk += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    vvzqz__tfvk = dict()
    exec(nblnr__zsk, {'bodo': bodo, 'numba': numba}, vvzqz__tfvk)
    grxn__dqg = vvzqz__tfvk['impl']
    return grxn__dqg


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
    fkahq__parvz = bodo.hiframes.pd_series_ext.get_series_data(value)
    for xgw__fcupm in numba.parfors.parfor.internal_prange(len(nrff__ehbd)):
        s = nrff__ehbd[xgw__fcupm]
        if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm
            ) and not bodo.libs.array_kernels.isna(fkahq__parvz, xgw__fcupm):
            s = fkahq__parvz[xgw__fcupm]
        nrff__ehbd[xgw__fcupm] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
    for xgw__fcupm in numba.parfors.parfor.internal_prange(len(nrff__ehbd)):
        s = nrff__ehbd[xgw__fcupm]
        if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm):
            s = value
        nrff__ehbd[xgw__fcupm] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    fkahq__parvz = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(nrff__ehbd)
    wtw__wsixf = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for xrmju__tns in numba.parfors.parfor.internal_prange(n):
        s = nrff__ehbd[xrmju__tns]
        if bodo.libs.array_kernels.isna(nrff__ehbd, xrmju__tns
            ) and not bodo.libs.array_kernels.isna(fkahq__parvz, xrmju__tns):
            s = fkahq__parvz[xrmju__tns]
        wtw__wsixf[xrmju__tns] = s
        if bodo.libs.array_kernels.isna(nrff__ehbd, xrmju__tns
            ) and bodo.libs.array_kernels.isna(fkahq__parvz, xrmju__tns):
            bodo.libs.array_kernels.setna(wtw__wsixf, xrmju__tns)
    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    fkahq__parvz = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(nrff__ehbd)
    wtw__wsixf = bodo.utils.utils.alloc_type(n, nrff__ehbd.dtype, (-1,))
    for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
        s = nrff__ehbd[xgw__fcupm]
        if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm
            ) and not bodo.libs.array_kernels.isna(fkahq__parvz, xgw__fcupm):
            s = fkahq__parvz[xgw__fcupm]
        wtw__wsixf[xgw__fcupm] = s
    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    cua__cjzo = dict(limit=limit, downcast=downcast)
    uxj__ygnp = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')
    watfp__bmd = not is_overload_none(value)
    hjbgb__jhtvf = not is_overload_none(method)
    if watfp__bmd and hjbgb__jhtvf:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not watfp__bmd and not hjbgb__jhtvf:
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
    if hjbgb__jhtvf:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        xzh__rfvap = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(xzh__rfvap)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(xzh__rfvap)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    injxi__xci = element_type(S.data)
    hup__pzei = None
    if watfp__bmd:
        hup__pzei = element_type(types.unliteral(value))
    if hup__pzei and not can_replace(injxi__xci, hup__pzei):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {hup__pzei} with series type {injxi__xci}'
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
        slqv__zepw = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                fkahq__parvz = bodo.hiframes.pd_series_ext.get_series_data(
                    value)
                n = len(nrff__ehbd)
                wtw__wsixf = bodo.utils.utils.alloc_type(n, slqv__zepw, (-1,))
                for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm
                        ) and bodo.libs.array_kernels.isna(fkahq__parvz,
                        xgw__fcupm):
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                        continue
                    if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm):
                        wtw__wsixf[xgw__fcupm
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            fkahq__parvz[xgw__fcupm])
                        continue
                    wtw__wsixf[xgw__fcupm
                        ] = bodo.utils.conversion.unbox_if_timestamp(nrff__ehbd
                        [xgw__fcupm])
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return fillna_series_impl
        if hjbgb__jhtvf:
            tvl__fzps = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(injxi__xci, (types.Integer, types.Float)
                ) and injxi__xci not in tvl__fzps:
                raise BodoError(
                    f"Series.fillna(): series of type {injxi__xci} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wtw__wsixf = bodo.libs.array_kernels.ffill_bfill_arr(nrff__ehbd
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(nrff__ehbd)
            wtw__wsixf = bodo.utils.utils.alloc_type(n, slqv__zepw, (-1,))
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(nrff__ehbd[
                    xgw__fcupm])
                if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm):
                    s = value
                wtw__wsixf[xgw__fcupm] = s
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        xajuu__ujiji = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        cua__cjzo = dict(limit=limit, downcast=downcast)
        uxj__ygnp = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', cua__cjzo,
            uxj__ygnp, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        injxi__xci = element_type(S.data)
        tvl__fzps = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(injxi__xci, (types.Integer, types.Float)
            ) and injxi__xci not in tvl__fzps:
            raise BodoError(
                f'Series.{overload_name}(): series of type {injxi__xci} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wtw__wsixf = bodo.libs.array_kernels.ffill_bfill_arr(nrff__ehbd,
                xajuu__ujiji)
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        kfpzo__jhp = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            kfpzo__jhp)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        tmry__wlbf = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(tmry__wlbf)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        tmry__wlbf = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(tmry__wlbf)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        tmry__wlbf = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(tmry__wlbf)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    cua__cjzo = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    zbi__wyqli = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', cua__cjzo, zbi__wyqli,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    injxi__xci = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        rxfqw__wwafj = element_type(to_replace.key_type)
        hup__pzei = element_type(to_replace.value_type)
    else:
        rxfqw__wwafj = element_type(to_replace)
        hup__pzei = element_type(value)
    prmd__ghda = None
    if injxi__xci != types.unliteral(rxfqw__wwafj):
        if bodo.utils.typing.equality_always_false(injxi__xci, types.
            unliteral(rxfqw__wwafj)
            ) or not bodo.utils.typing.types_equality_exists(injxi__xci,
            rxfqw__wwafj):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(injxi__xci, (types.Float, types.Integer)
            ) or injxi__xci == np.bool_:
            prmd__ghda = injxi__xci
    if not can_replace(injxi__xci, types.unliteral(hup__pzei)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    mfd__ccyy = to_str_arr_if_dict_array(S.data)
    if isinstance(mfd__ccyy, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(nrff__ehbd.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(nrff__ehbd)
        wtw__wsixf = bodo.utils.utils.alloc_type(n, mfd__ccyy, (-1,))
        hnlmg__oge = build_replace_dict(to_replace, value, prmd__ghda)
        for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(nrff__ehbd, xgw__fcupm):
                bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                continue
            s = nrff__ehbd[xgw__fcupm]
            if s in hnlmg__oge:
                s = hnlmg__oge[s]
            wtw__wsixf[xgw__fcupm] = s
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    pjynj__bvk = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    mwko__rsfdw = is_iterable_type(to_replace)
    pfgsk__lofit = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    oruhi__dtmnp = is_iterable_type(value)
    if pjynj__bvk and pfgsk__lofit:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                hnlmg__oge = {}
                hnlmg__oge[key_dtype_conv(to_replace)] = value
                return hnlmg__oge
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            hnlmg__oge = {}
            hnlmg__oge[to_replace] = value
            return hnlmg__oge
        return impl
    if mwko__rsfdw and pfgsk__lofit:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                hnlmg__oge = {}
                for stpkq__xpei in to_replace:
                    hnlmg__oge[key_dtype_conv(stpkq__xpei)] = value
                return hnlmg__oge
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            hnlmg__oge = {}
            for stpkq__xpei in to_replace:
                hnlmg__oge[stpkq__xpei] = value
            return hnlmg__oge
        return impl
    if mwko__rsfdw and oruhi__dtmnp:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                hnlmg__oge = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for xgw__fcupm in range(len(to_replace)):
                    hnlmg__oge[key_dtype_conv(to_replace[xgw__fcupm])] = value[
                        xgw__fcupm]
                return hnlmg__oge
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            hnlmg__oge = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for xgw__fcupm in range(len(to_replace)):
                hnlmg__oge[to_replace[xgw__fcupm]] = value[xgw__fcupm]
            return hnlmg__oge
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
            wtw__wsixf = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    cua__cjzo = dict(ignore_index=ignore_index)
    myu__cxgoq = dict(ignore_index=False)
    check_unsupported_args('Series.explode', cua__cjzo, myu__cxgoq,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kusz__ttsb = bodo.utils.conversion.index_to_array(index)
        wtw__wsixf, tcvhn__nmjl = bodo.libs.array_kernels.explode(arr,
            kusz__ttsb)
        ajekt__ivsj = bodo.utils.conversion.index_from_array(tcvhn__nmjl)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
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
            mgie__gxjin = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                mgie__gxjin[xgw__fcupm] = np.argmax(a[xgw__fcupm])
            return mgie__gxjin
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            zubjx__uxts = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                zubjx__uxts[xgw__fcupm] = np.argmin(a[xgw__fcupm])
            return zubjx__uxts
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
    cua__cjzo = dict(axis=axis, inplace=inplace, how=how)
    wvcot__kfr = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', cua__cjzo, wvcot__kfr,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            dbl__cuwfe = S.notna().values
            kusz__ttsb = bodo.utils.conversion.extract_index_array(S)
            ajekt__ivsj = bodo.utils.conversion.convert_to_index(kusz__ttsb
                [dbl__cuwfe])
            wtw__wsixf = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(nrff__ehbd))
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                ajekt__ivsj, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            kusz__ttsb = bodo.utils.conversion.extract_index_array(S)
            dbl__cuwfe = S.notna().values
            ajekt__ivsj = bodo.utils.conversion.convert_to_index(kusz__ttsb
                [dbl__cuwfe])
            wtw__wsixf = nrff__ehbd[dbl__cuwfe]
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                ajekt__ivsj, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    cua__cjzo = dict(freq=freq, axis=axis, fill_value=fill_value)
    uxj__ygnp = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', cua__cjzo, uxj__ygnp,
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
        wtw__wsixf = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    cua__cjzo = dict(fill_method=fill_method, limit=limit, freq=freq)
    uxj__ygnp = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', cua__cjzo, uxj__ygnp,
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
        wtw__wsixf = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
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
            pfwhp__izif = 'None'
        else:
            pfwhp__izif = 'other'
        nblnr__zsk = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            nblnr__zsk += '  cond = ~cond\n'
        nblnr__zsk += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        nblnr__zsk += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        nblnr__zsk += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        nblnr__zsk += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {pfwhp__izif})
"""
        nblnr__zsk += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ckbf__lul = {}
        exec(nblnr__zsk, {'bodo': bodo, 'np': np}, ckbf__lul)
        impl = ckbf__lul['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        kfpzo__jhp = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(kfpzo__jhp)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    cua__cjzo = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    uxj__ygnp = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', cua__cjzo, uxj__ygnp,
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
    hytq__rvoss = is_overload_constant_nan(other)
    if not (is_default or hytq__rvoss or is_scalar_type(other) or 
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
            hvmje__yfft = arr.dtype.elem_type
        else:
            hvmje__yfft = arr.dtype
        if is_iterable_type(other):
            kmakq__zih = other.dtype
        elif hytq__rvoss:
            kmakq__zih = types.float64
        else:
            kmakq__zih = types.unliteral(other)
        if not hytq__rvoss and not is_common_scalar_dtype([hvmje__yfft,
            kmakq__zih]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        cua__cjzo = dict(level=level, axis=axis)
        uxj__ygnp = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), cua__cjzo,
            uxj__ygnp, package_name='pandas', module_name='Series')
        svq__tod = other == string_type or is_overload_constant_str(other)
        vfse__pmfp = is_iterable_type(other) and other.dtype == string_type
        hymla__wkea = S.dtype == string_type and (op == operator.add and (
            svq__tod or vfse__pmfp) or op == operator.mul and isinstance(
            other, types.Integer))
        zofum__yletg = S.dtype == bodo.timedelta64ns
        qof__rocls = S.dtype == bodo.datetime64ns
        eeoyi__dqu = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        qaa__shfv = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        oemsd__tdri = zofum__yletg and (eeoyi__dqu or qaa__shfv
            ) or qof__rocls and eeoyi__dqu
        oemsd__tdri = oemsd__tdri and op == operator.add
        if not (isinstance(S.dtype, types.Number) or hymla__wkea or oemsd__tdri
            ):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        hbx__hyw = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            mfd__ccyy = hbx__hyw.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and mfd__ccyy == types.Array(types.bool_, 1, 'C'):
                mfd__ccyy = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                wtw__wsixf = bodo.utils.utils.alloc_type(n, mfd__ccyy, (-1,))
                for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                    vld__tgh = bodo.libs.array_kernels.isna(arr, xgw__fcupm)
                    if vld__tgh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wtw__wsixf,
                                xgw__fcupm)
                        else:
                            wtw__wsixf[xgw__fcupm] = op(fill_value, other)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(arr[xgw__fcupm], other)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        mfd__ccyy = hbx__hyw.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and mfd__ccyy == types.Array(
            types.bool_, 1, 'C'):
            mfd__ccyy = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xfem__kecb = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wtw__wsixf = bodo.utils.utils.alloc_type(n, mfd__ccyy, (-1,))
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                vld__tgh = bodo.libs.array_kernels.isna(arr, xgw__fcupm)
                tdr__onio = bodo.libs.array_kernels.isna(xfem__kecb, xgw__fcupm
                    )
                if vld__tgh and tdr__onio:
                    bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                elif vld__tgh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(fill_value, xfem__kecb[
                            xgw__fcupm])
                elif tdr__onio:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(arr[xgw__fcupm], fill_value
                            )
                else:
                    wtw__wsixf[xgw__fcupm] = op(arr[xgw__fcupm], xfem__kecb
                        [xgw__fcupm])
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
        hbx__hyw = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            mfd__ccyy = hbx__hyw.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and mfd__ccyy == types.Array(types.bool_, 1, 'C'):
                mfd__ccyy = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                wtw__wsixf = bodo.utils.utils.alloc_type(n, mfd__ccyy, None)
                for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                    vld__tgh = bodo.libs.array_kernels.isna(arr, xgw__fcupm)
                    if vld__tgh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(wtw__wsixf,
                                xgw__fcupm)
                        else:
                            wtw__wsixf[xgw__fcupm] = op(other, fill_value)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(other, arr[xgw__fcupm])
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        mfd__ccyy = hbx__hyw.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and mfd__ccyy == types.Array(
            types.bool_, 1, 'C'):
            mfd__ccyy = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xfem__kecb = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            wtw__wsixf = bodo.utils.utils.alloc_type(n, mfd__ccyy, None)
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                vld__tgh = bodo.libs.array_kernels.isna(arr, xgw__fcupm)
                tdr__onio = bodo.libs.array_kernels.isna(xfem__kecb, xgw__fcupm
                    )
                wtw__wsixf[xgw__fcupm] = op(xfem__kecb[xgw__fcupm], arr[
                    xgw__fcupm])
                if vld__tgh and tdr__onio:
                    bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                elif vld__tgh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(xfem__kecb[xgw__fcupm],
                            fill_value)
                elif tdr__onio:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                    else:
                        wtw__wsixf[xgw__fcupm] = op(fill_value, arr[xgw__fcupm]
                            )
                else:
                    wtw__wsixf[xgw__fcupm] = op(xfem__kecb[xgw__fcupm], arr
                        [xgw__fcupm])
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
    for op, ivh__uci in explicit_binop_funcs_two_ways.items():
        for name in ivh__uci:
            kfpzo__jhp = create_explicit_binary_op_overload(op)
            kzl__vjaek = create_explicit_binary_reverse_op_overload(op)
            jhb__hpt = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(kfpzo__jhp)
            overload_method(SeriesType, jhb__hpt, no_unliteral=True)(kzl__vjaek
                )
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        kfpzo__jhp = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(kfpzo__jhp)
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
                wusdt__exuxn = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wtw__wsixf = dt64_arr_sub(arr, wusdt__exuxn)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
                wtw__wsixf = np.empty(n, np.dtype('datetime64[ns]'))
                for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, xgw__fcupm):
                        bodo.libs.array_kernels.setna(wtw__wsixf, xgw__fcupm)
                        continue
                    vsfo__hhis = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[xgw__fcupm]))
                    cstpo__itx = op(vsfo__hhis, rhs)
                    wtw__wsixf[xgw__fcupm
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        cstpo__itx.value)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
                    wusdt__exuxn = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    wtw__wsixf = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(wusdt__exuxn))
                    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wusdt__exuxn = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                wtw__wsixf = op(arr, wusdt__exuxn)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    crm__eovyy = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    wtw__wsixf = op(bodo.utils.conversion.
                        unbox_if_timestamp(crm__eovyy), arr)
                    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                crm__eovyy = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                wtw__wsixf = op(crm__eovyy, arr)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        kfpzo__jhp = create_binary_op_overload(op)
        overload(op)(kfpzo__jhp)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    lwcod__noou = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, lwcod__noou)
        for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, xgw__fcupm
                ) or bodo.libs.array_kernels.isna(arg2, xgw__fcupm):
                bodo.libs.array_kernels.setna(S, xgw__fcupm)
                continue
            S[xgw__fcupm
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                xgw__fcupm]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[xgw__fcupm]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                xfem__kecb = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, xfem__kecb)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        kfpzo__jhp = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(kfpzo__jhp)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                wtw__wsixf = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        kfpzo__jhp = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(kfpzo__jhp)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    wtw__wsixf = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
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
                    xfem__kecb = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    wtw__wsixf = ufunc(arr, xfem__kecb)
                    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    xfem__kecb = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    wtw__wsixf = ufunc(arr, xfem__kecb)
                    return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        kfpzo__jhp = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(kfpzo__jhp)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        vph__ofzvc = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        zvuni__hmw = np.arange(n),
        bodo.libs.timsort.sort(vph__ofzvc, 0, n, zvuni__hmw)
        return zvuni__hmw[0]
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
        cdli__pqol = get_overload_const_str(downcast)
        if cdli__pqol in ('integer', 'signed'):
            out_dtype = types.int64
        elif cdli__pqol == 'unsigned':
            out_dtype = types.uint64
        else:
            assert cdli__pqol == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            nrff__ehbd = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            wtw__wsixf = pd.to_numeric(nrff__ehbd, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            xacps__bfl = np.empty(n, np.float64)
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, xgw__fcupm):
                    bodo.libs.array_kernels.setna(xacps__bfl, xgw__fcupm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(xacps__bfl,
                        xgw__fcupm, arg_a, xgw__fcupm)
            return xacps__bfl
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            xacps__bfl = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, xgw__fcupm):
                    bodo.libs.array_kernels.setna(xacps__bfl, xgw__fcupm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(xacps__bfl,
                        xgw__fcupm, arg_a, xgw__fcupm)
            return xacps__bfl
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        ispf__tyipg = if_series_to_array_type(args[0])
        if isinstance(ispf__tyipg, types.Array) and isinstance(ispf__tyipg.
            dtype, types.Integer):
            ispf__tyipg = types.Array(types.float64, 1, 'C')
        return ispf__tyipg(*args)


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
    gaeu__bio = bodo.utils.utils.is_array_typ(x, True)
    nyn__oak = bodo.utils.utils.is_array_typ(y, True)
    nblnr__zsk = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        nblnr__zsk += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if gaeu__bio and not bodo.utils.utils.is_array_typ(x, False):
        nblnr__zsk += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if nyn__oak and not bodo.utils.utils.is_array_typ(y, False):
        nblnr__zsk += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    nblnr__zsk += '  n = len(condition)\n'
    hsu__bqyn = x.dtype if gaeu__bio else types.unliteral(x)
    pvp__flmcw = y.dtype if nyn__oak else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        hsu__bqyn = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        pvp__flmcw = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    kxjsl__jia = get_data(x)
    duqbg__cux = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(zvuni__hmw) for
        zvuni__hmw in [kxjsl__jia, duqbg__cux])
    if duqbg__cux == types.none:
        if isinstance(hsu__bqyn, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif kxjsl__jia == duqbg__cux and not is_nullable:
        out_dtype = dtype_to_array_type(hsu__bqyn)
    elif hsu__bqyn == string_type or pvp__flmcw == string_type:
        out_dtype = bodo.string_array_type
    elif kxjsl__jia == bytes_type or (gaeu__bio and hsu__bqyn == bytes_type
        ) and (duqbg__cux == bytes_type or nyn__oak and pvp__flmcw ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(hsu__bqyn, bodo.PDCategoricalDtype):
        out_dtype = None
    elif hsu__bqyn in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(hsu__bqyn, 1, 'C')
    elif pvp__flmcw in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(pvp__flmcw, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(hsu__bqyn), numba.np.numpy_support.
            as_dtype(pvp__flmcw)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(hsu__bqyn, bodo.PDCategoricalDtype):
        iyirb__zeki = 'x'
    else:
        iyirb__zeki = 'out_dtype'
    nblnr__zsk += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {iyirb__zeki}, (-1,))\n')
    if isinstance(hsu__bqyn, bodo.PDCategoricalDtype):
        nblnr__zsk += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        nblnr__zsk += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    nblnr__zsk += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    nblnr__zsk += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if gaeu__bio:
        nblnr__zsk += '      if bodo.libs.array_kernels.isna(x, j):\n'
        nblnr__zsk += '        setna(out_arr, j)\n'
        nblnr__zsk += '        continue\n'
    if isinstance(hsu__bqyn, bodo.PDCategoricalDtype):
        nblnr__zsk += '      out_codes[j] = x_codes[j]\n'
    else:
        nblnr__zsk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if gaeu__bio else 'x'))
    nblnr__zsk += '    else:\n'
    if nyn__oak:
        nblnr__zsk += '      if bodo.libs.array_kernels.isna(y, j):\n'
        nblnr__zsk += '        setna(out_arr, j)\n'
        nblnr__zsk += '        continue\n'
    if duqbg__cux == types.none:
        if isinstance(hsu__bqyn, bodo.PDCategoricalDtype):
            nblnr__zsk += '      out_codes[j] = -1\n'
        else:
            nblnr__zsk += '      setna(out_arr, j)\n'
    else:
        nblnr__zsk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if nyn__oak else 'y'))
    nblnr__zsk += '  return out_arr\n'
    ckbf__lul = {}
    exec(nblnr__zsk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, ckbf__lul)
    tknc__mjji = ckbf__lul['_impl']
    return tknc__mjji


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
        zdjn__mvna = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(zdjn__mvna, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(zdjn__mvna):
            zsb__hytb = zdjn__mvna.data.dtype
        else:
            zsb__hytb = zdjn__mvna.dtype
        if isinstance(zsb__hytb, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        yykzw__qfxx = zdjn__mvna
    else:
        mlviy__yht = []
        for zdjn__mvna in choicelist:
            if not bodo.utils.utils.is_array_typ(zdjn__mvna, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(zdjn__mvna):
                zsb__hytb = zdjn__mvna.data.dtype
            else:
                zsb__hytb = zdjn__mvna.dtype
            if isinstance(zsb__hytb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mlviy__yht.append(zsb__hytb)
        if not is_common_scalar_dtype(mlviy__yht):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        yykzw__qfxx = choicelist[0]
    if is_series_type(yykzw__qfxx):
        yykzw__qfxx = yykzw__qfxx.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, yykzw__qfxx.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(yykzw__qfxx, types.Array) or isinstance(yykzw__qfxx,
        BooleanArrayType) or isinstance(yykzw__qfxx, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(yykzw__qfxx, False) and yykzw__qfxx.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {yykzw__qfxx} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    cys__stn = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        cgpcf__tdce = choicelist.dtype
    else:
        ukyu__jxgo = False
        mlviy__yht = []
        for zdjn__mvna in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                zdjn__mvna, 'numpy.select()')
            if is_nullable_type(zdjn__mvna):
                ukyu__jxgo = True
            if is_series_type(zdjn__mvna):
                zsb__hytb = zdjn__mvna.data.dtype
            else:
                zsb__hytb = zdjn__mvna.dtype
            if isinstance(zsb__hytb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mlviy__yht.append(zsb__hytb)
        qat__gptmb, fwq__dcru = get_common_scalar_dtype(mlviy__yht)
        if not fwq__dcru:
            raise BodoError('Internal error in overload_np_select')
        mexcc__cgqz = dtype_to_array_type(qat__gptmb)
        if ukyu__jxgo:
            mexcc__cgqz = to_nullable_type(mexcc__cgqz)
        cgpcf__tdce = mexcc__cgqz
    if isinstance(cgpcf__tdce, SeriesType):
        cgpcf__tdce = cgpcf__tdce.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        joywv__lwwm = True
    else:
        joywv__lwwm = False
    ystok__jpv = False
    ahq__hlux = False
    if joywv__lwwm:
        if isinstance(cgpcf__tdce.dtype, types.Number):
            pass
        elif cgpcf__tdce.dtype == types.bool_:
            ahq__hlux = True
        else:
            ystok__jpv = True
            cgpcf__tdce = to_nullable_type(cgpcf__tdce)
    elif default == types.none or is_overload_constant_nan(default):
        ystok__jpv = True
        cgpcf__tdce = to_nullable_type(cgpcf__tdce)
    nblnr__zsk = 'def np_select_impl(condlist, choicelist, default=0):\n'
    nblnr__zsk += '  if len(condlist) != len(choicelist):\n'
    nblnr__zsk += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    nblnr__zsk += '  output_len = len(choicelist[0])\n'
    nblnr__zsk += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    nblnr__zsk += '  for i in range(output_len):\n'
    if ystok__jpv:
        nblnr__zsk += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif ahq__hlux:
        nblnr__zsk += '    out[i] = False\n'
    else:
        nblnr__zsk += '    out[i] = default\n'
    if cys__stn:
        nblnr__zsk += '  for i in range(len(condlist) - 1, -1, -1):\n'
        nblnr__zsk += '    cond = condlist[i]\n'
        nblnr__zsk += '    choice = choicelist[i]\n'
        nblnr__zsk += '    out = np.where(cond, choice, out)\n'
    else:
        for xgw__fcupm in range(len(choicelist) - 1, -1, -1):
            nblnr__zsk += f'  cond = condlist[{xgw__fcupm}]\n'
            nblnr__zsk += f'  choice = choicelist[{xgw__fcupm}]\n'
            nblnr__zsk += f'  out = np.where(cond, choice, out)\n'
    nblnr__zsk += '  return out'
    ckbf__lul = dict()
    exec(nblnr__zsk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': cgpcf__tdce}, ckbf__lul)
    impl = ckbf__lul['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtw__wsixf = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    cua__cjzo = dict(subset=subset, keep=keep, inplace=inplace)
    uxj__ygnp = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', cua__cjzo, uxj__ygnp,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        hrdof__oblh = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (hrdof__oblh,), kusz__ttsb = bodo.libs.array_kernels.drop_duplicates((
            hrdof__oblh,), index, 1)
        index = bodo.utils.conversion.index_from_array(kusz__ttsb)
        return bodo.hiframes.pd_series_ext.init_series(hrdof__oblh, index, name
            )
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    yfk__oerqj = element_type(S.data)
    if not is_common_scalar_dtype([yfk__oerqj, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([yfk__oerqj, right]):
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
        wtw__wsixf = np.empty(n, np.bool_)
        for xgw__fcupm in numba.parfors.parfor.internal_prange(n):
            ciqh__iuk = bodo.utils.conversion.box_if_dt64(arr[xgw__fcupm])
            if inclusive == 'both':
                wtw__wsixf[xgw__fcupm
                    ] = ciqh__iuk <= right and ciqh__iuk >= left
            else:
                wtw__wsixf[xgw__fcupm] = ciqh__iuk < right and ciqh__iuk > left
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    cua__cjzo = dict(axis=axis)
    uxj__ygnp = dict(axis=None)
    check_unsupported_args('Series.repeat', cua__cjzo, uxj__ygnp,
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
            kusz__ttsb = bodo.utils.conversion.index_to_array(index)
            wtw__wsixf = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            tcvhn__nmjl = bodo.libs.array_kernels.repeat_kernel(kusz__ttsb,
                repeats)
            ajekt__ivsj = bodo.utils.conversion.index_from_array(tcvhn__nmjl)
            return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
                ajekt__ivsj, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kusz__ttsb = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        wtw__wsixf = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        tcvhn__nmjl = bodo.libs.array_kernels.repeat_kernel(kusz__ttsb, repeats
            )
        ajekt__ivsj = bodo.utils.conversion.index_from_array(tcvhn__nmjl)
        return bodo.hiframes.pd_series_ext.init_series(wtw__wsixf,
            ajekt__ivsj, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        zvuni__hmw = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(zvuni__hmw)
        oep__gps = {}
        for xgw__fcupm in range(n):
            ciqh__iuk = bodo.utils.conversion.box_if_dt64(zvuni__hmw[
                xgw__fcupm])
            oep__gps[index[xgw__fcupm]] = ciqh__iuk
        return oep__gps
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    xzh__rfvap = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            nfjbe__wxvs = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(xzh__rfvap)
    elif is_literal_type(name):
        nfjbe__wxvs = get_literal_value(name)
    else:
        raise_bodo_error(xzh__rfvap)
    nfjbe__wxvs = 0 if nfjbe__wxvs is None else nfjbe__wxvs
    ywv__wbqfs = ColNamesMetaType((nfjbe__wxvs,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            ywv__wbqfs)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
