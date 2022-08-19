"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.time_ext import TimeArrayType
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, parse_dtype, raise_bodo_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        rfv__eysd = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({rfv__eysd})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    qibi__dqu = 'def impl(df):\n'
    if df.has_runtime_cols:
        qibi__dqu += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        mhq__cqpbs = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        qibi__dqu += f'  return {mhq__cqpbs}'
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    caq__mnj = len(df.columns)
    cfzzp__svpsb = set(i for i in range(caq__mnj) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in cfzzp__svpsb else '') for i in
        range(caq__mnj))
    qibi__dqu = 'def f(df):\n'.format()
    qibi__dqu += '    return np.stack(({},), 1)\n'.format(data_args)
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'np': np}, luqre__neevz)
    lua__kqa = luqre__neevz['f']
    return lua__kqa


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    vpuf__akvhz = {'dtype': dtype, 'na_value': na_value}
    cznlq__bjf = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            ydukt__sngku = bodo.hiframes.table.compute_num_runtime_columns(t)
            return ydukt__sngku * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            ydukt__sngku = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), ydukt__sngku
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    qibi__dqu = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    mddu__jxelz = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    qibi__dqu += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{mddu__jxelz}), {index}, None)
"""
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        return dtype.name
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.astype()')
    vpuf__akvhz = {'copy': copy, 'errors': errors}
    cznlq__bjf = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    if df.is_table_format:
        extra_globals = {}
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        lvem__ysunt = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        jkni__tumrz = _bodo_object_typeref.instance_type
        assert isinstance(jkni__tumrz, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in jkni__tumrz.column_index:
                    idx = jkni__tumrz.column_index[name]
                    arr_typ = jkni__tumrz.data[idx]
                else:
                    arr_typ = df.data[i]
                lvem__ysunt.append(arr_typ)
        else:
            extra_globals = {}
            ygpcw__immf = {}
            for i, name in enumerate(jkni__tumrz.columns):
                arr_typ = jkni__tumrz.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    llpa__ttyfl = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    llpa__ttyfl = boolean_dtype
                else:
                    llpa__ttyfl = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = llpa__ttyfl
                ygpcw__immf[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {ygpcw__immf[weamh__ikbe]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if weamh__ikbe in ygpcw__immf else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, weamh__ikbe in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        pgg__zdmc = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            pgg__zdmc = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in pgg__zdmc.items()}
            for i, name in enumerate(df.columns):
                if name in pgg__zdmc:
                    arr_typ = pgg__zdmc[name]
                else:
                    arr_typ = df.data[i]
                lvem__ysunt.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(pgg__zdmc[weamh__ikbe])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if weamh__ikbe in pgg__zdmc else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, weamh__ikbe in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        lvem__ysunt = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        prq__sth = bodo.TableType(tuple(lvem__ysunt))
        extra_globals['out_table_typ'] = prq__sth
        data_args = (
            'bodo.utils.table_utils.table_astype(table, out_table_typ, copy, _bodo_nan_to_str)'
            )
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    header = 'def impl(df, deep=True):\n'
    extra_globals = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ciyi__laiwi = types.none
        extra_globals = {'output_arr_typ': ciyi__laiwi}
        if is_overload_false(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if deep else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        pejxo__marp = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                pejxo__marp.append(arr + '.copy()')
            elif is_overload_false(deep):
                pejxo__marp.append(arr)
            else:
                pejxo__marp.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(pejxo__marp)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    vpuf__akvhz = {'index': index, 'level': level, 'errors': errors}
    cznlq__bjf = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        fbrg__olp = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        fbrg__olp = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    uociw__hpl = tuple([fbrg__olp.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    ttvkk__goluh = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ttvkk__goluh = df.copy(columns=uociw__hpl)
        ciyi__laiwi = types.none
        extra_globals = {'output_arr_typ': ciyi__laiwi}
        if is_overload_false(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if copy else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        pejxo__marp = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                pejxo__marp.append(arr + '.copy()')
            elif is_overload_false(copy):
                pejxo__marp.append(arr)
            else:
                pejxo__marp.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(pejxo__marp)
    return _gen_init_df(header, uociw__hpl, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    ghi__ymkm = not is_overload_none(items)
    eghl__ach = not is_overload_none(like)
    quo__tde = not is_overload_none(regex)
    lrtsv__bfxrl = ghi__ymkm ^ eghl__ach ^ quo__tde
    syxf__tqakh = not (ghi__ymkm or eghl__ach or quo__tde)
    if syxf__tqakh:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not lrtsv__bfxrl:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        iyn__cve = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        iyn__cve = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert iyn__cve in {0, 1}
    qibi__dqu = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if iyn__cve == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if iyn__cve == 1:
        rmm__voywv = []
        iyctl__sqa = []
        twx__klszv = []
        if ghi__ymkm:
            if is_overload_constant_list(items):
                mspse__usnad = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if eghl__ach:
            if is_overload_constant_str(like):
                eyoww__dhuui = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if quo__tde:
            if is_overload_constant_str(regex):
                wwz__bmhz = get_overload_const_str(regex)
                yxely__tzs = re.compile(wwz__bmhz)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, weamh__ikbe in enumerate(df.columns):
            if not is_overload_none(items
                ) and weamh__ikbe in mspse__usnad or not is_overload_none(like
                ) and eyoww__dhuui in str(weamh__ikbe) or not is_overload_none(
                regex) and yxely__tzs.search(str(weamh__ikbe)):
                iyctl__sqa.append(weamh__ikbe)
                twx__klszv.append(i)
        for i in twx__klszv:
            var_name = f'data_{i}'
            rmm__voywv.append(var_name)
            qibi__dqu += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(rmm__voywv)
        return _gen_init_df(qibi__dqu, iyctl__sqa, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ttvkk__goluh = None
    if df.is_table_format:
        ciyi__laiwi = types.Array(types.bool_, 1, 'C')
        ttvkk__goluh = DataFrameType(tuple([ciyi__laiwi] * len(df.data)),
            df.index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': ciyi__laiwi}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    yfqcb__dcy = is_overload_none(include)
    gvhr__kdk = is_overload_none(exclude)
    ajcgv__pgdd = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if yfqcb__dcy and gvhr__kdk:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not yfqcb__dcy:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            rxn__ewidk = [dtype_to_array_type(parse_dtype(elem, ajcgv__pgdd
                )) for elem in include]
        elif is_legal_input(include):
            rxn__ewidk = [dtype_to_array_type(parse_dtype(include,
                ajcgv__pgdd))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        rxn__ewidk = get_nullable_and_non_nullable_types(rxn__ewidk)
        pum__jekmk = tuple(weamh__ikbe for i, weamh__ikbe in enumerate(df.
            columns) if df.data[i] in rxn__ewidk)
    else:
        pum__jekmk = df.columns
    if not gvhr__kdk:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            zksnq__oxad = [dtype_to_array_type(parse_dtype(elem,
                ajcgv__pgdd)) for elem in exclude]
        elif is_legal_input(exclude):
            zksnq__oxad = [dtype_to_array_type(parse_dtype(exclude,
                ajcgv__pgdd))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        zksnq__oxad = get_nullable_and_non_nullable_types(zksnq__oxad)
        pum__jekmk = tuple(weamh__ikbe for weamh__ikbe in pum__jekmk if df.
            data[df.column_index[weamh__ikbe]] not in zksnq__oxad)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[weamh__ikbe]})'
         for weamh__ikbe in pum__jekmk)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, pum__jekmk, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ttvkk__goluh = None
    if df.is_table_format:
        ciyi__laiwi = types.Array(types.bool_, 1, 'C')
        ttvkk__goluh = DataFrameType(tuple([ciyi__laiwi] * len(df.data)),
            df.index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': ciyi__laiwi}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'~bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


def overload_dataframe_head(df, n=5):
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[:n]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[m:]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    eoec__pidhi = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in eoec__pidhi:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.first()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    eoec__pidhi = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in eoec__pidhi:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.last()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.isin()')
    qibi__dqu = 'def impl(df, values):\n'
    qsiep__kkpa = {}
    rliks__zkj = False
    if isinstance(values, DataFrameType):
        rliks__zkj = True
        for i, weamh__ikbe in enumerate(df.columns):
            if weamh__ikbe in values.column_index:
                djbkz__wtmxm = 'val{}'.format(i)
                qibi__dqu += f"""  {djbkz__wtmxm} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[weamh__ikbe]})
"""
                qsiep__kkpa[weamh__ikbe] = djbkz__wtmxm
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        qsiep__kkpa = {weamh__ikbe: 'values' for weamh__ikbe in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        djbkz__wtmxm = 'data{}'.format(i)
        qibi__dqu += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(djbkz__wtmxm, i))
        data.append(djbkz__wtmxm)
    twa__uwy = ['out{}'.format(i) for i in range(len(df.columns))]
    gsy__ibe = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    jhdt__fcrd = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    wkb__nkiu = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, khvy__rtrjm) in enumerate(zip(df.columns, data)):
        if cname in qsiep__kkpa:
            kij__sxqmu = qsiep__kkpa[cname]
            if rliks__zkj:
                qibi__dqu += gsy__ibe.format(khvy__rtrjm, kij__sxqmu,
                    twa__uwy[i])
            else:
                qibi__dqu += jhdt__fcrd.format(khvy__rtrjm, kij__sxqmu,
                    twa__uwy[i])
        else:
            qibi__dqu += wkb__nkiu.format(twa__uwy[i])
    return _gen_init_df(qibi__dqu, df.columns, ','.join(twa__uwy))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    caq__mnj = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(caq__mnj))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    rdopl__ias = [weamh__ikbe for weamh__ikbe, jumcm__vxlao in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        jumcm__vxlao.dtype)]
    assert len(rdopl__ias) != 0
    jfzji__dgfm = ''
    if not any(jumcm__vxlao == types.float64 for jumcm__vxlao in df.data):
        jfzji__dgfm = '.astype(np.float64)'
    jxd__jfap = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[weamh__ikbe], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[weamh__ikbe]], IntegerArrayType) or
        df.data[df.column_index[weamh__ikbe]] == boolean_array else '') for
        weamh__ikbe in rdopl__ias)
    zcp__wcz = 'np.stack(({},), 1){}'.format(jxd__jfap, jfzji__dgfm)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(rdopl__ias))
        )
    index = f'{generate_col_to_index_func_text(rdopl__ias)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(zcp__wcz)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, rdopl__ias, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    pqd__kxs = dict(ddof=ddof)
    fmnf__zkpt = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    koezv__yqvk = '1' if is_overload_none(min_periods) else 'min_periods'
    rdopl__ias = [weamh__ikbe for weamh__ikbe, jumcm__vxlao in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        jumcm__vxlao.dtype)]
    if len(rdopl__ias) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    jfzji__dgfm = ''
    if not any(jumcm__vxlao == types.float64 for jumcm__vxlao in df.data):
        jfzji__dgfm = '.astype(np.float64)'
    jxd__jfap = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[weamh__ikbe], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[weamh__ikbe]], IntegerArrayType) or
        df.data[df.column_index[weamh__ikbe]] == boolean_array else '') for
        weamh__ikbe in rdopl__ias)
    zcp__wcz = 'np.stack(({},), 1){}'.format(jxd__jfap, jfzji__dgfm)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(rdopl__ias))
        )
    index = f'pd.Index({rdopl__ias})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(zcp__wcz)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        koezv__yqvk)
    return _gen_init_df(header, rdopl__ias, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    pqd__kxs = dict(axis=axis, level=level, numeric_only=numeric_only)
    fmnf__zkpt = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    qibi__dqu = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    qibi__dqu += '  data = np.array([{}])\n'.format(data_args)
    mhq__cqpbs = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    qibi__dqu += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {mhq__cqpbs})\n'
        )
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'np': np}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    pqd__kxs = dict(axis=axis)
    fmnf__zkpt = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    qibi__dqu = 'def impl(df, axis=0, dropna=True):\n'
    qibi__dqu += '  data = np.asarray(({},))\n'.format(data_args)
    mhq__cqpbs = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    qibi__dqu += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {mhq__cqpbs})\n'
        )
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'np': np}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    pqd__kxs = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    pqd__kxs = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    pqd__kxs = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fmnf__zkpt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    pqd__kxs = dict(numeric_only=numeric_only, interpolation=interpolation)
    fmnf__zkpt = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    pqd__kxs = dict(axis=axis, skipna=skipna)
    fmnf__zkpt = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for wnekh__jecd in df.data:
        if not (bodo.utils.utils.is_np_array_typ(wnekh__jecd) and (
            wnekh__jecd.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(wnekh__jecd.dtype, (types.Number, types.Boolean))) or
            isinstance(wnekh__jecd, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or wnekh__jecd in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {wnekh__jecd} not supported.'
                )
        if isinstance(wnekh__jecd, bodo.CategoricalArrayType
            ) and not wnekh__jecd.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    pqd__kxs = dict(axis=axis, skipna=skipna)
    fmnf__zkpt = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for wnekh__jecd in df.data:
        if not (bodo.utils.utils.is_np_array_typ(wnekh__jecd) and (
            wnekh__jecd.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(wnekh__jecd.dtype, (types.Number, types.Boolean))) or
            isinstance(wnekh__jecd, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or wnekh__jecd in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {wnekh__jecd} not supported.'
                )
        if isinstance(wnekh__jecd, bodo.CategoricalArrayType
            ) and not wnekh__jecd.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        rdopl__ias = tuple(weamh__ikbe for weamh__ikbe, jumcm__vxlao in zip
            (df.columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(jumcm__vxlao.dtype))
        out_colnames = rdopl__ias
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            apsv__velch = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[weamh__ikbe]].dtype) for weamh__ikbe in
                out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(apsv__velch, []))
    except NotImplementedError as zai__kqff:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    esu__chxyg = ''
    if func_name in ('sum', 'prod'):
        esu__chxyg = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    qibi__dqu = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, esu__chxyg))
    if func_name == 'quantile':
        qibi__dqu = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        qibi__dqu = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        qibi__dqu += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        qibi__dqu += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    kqi__drkou = ''
    if func_name in ('min', 'max'):
        kqi__drkou = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        kqi__drkou = ', dtype=np.float32'
    ayq__zuoz = f'bodo.libs.array_ops.array_op_{func_name}'
    lqo__adoeg = ''
    if func_name in ['sum', 'prod']:
        lqo__adoeg = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        lqo__adoeg = 'index'
    elif func_name == 'quantile':
        lqo__adoeg = 'q'
    elif func_name in ['std', 'var']:
        lqo__adoeg = 'True, ddof'
    elif func_name == 'median':
        lqo__adoeg = 'True'
    data_args = ', '.join(
        f'{ayq__zuoz}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[weamh__ikbe]}), {lqo__adoeg})'
         for weamh__ikbe in out_colnames)
    qibi__dqu = ''
    if func_name in ('idxmax', 'idxmin'):
        qibi__dqu += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        qibi__dqu += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        qibi__dqu += '  data = np.asarray(({},){})\n'.format(data_args,
            kqi__drkou)
    qibi__dqu += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return qibi__dqu


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    kmoj__qprzq = [df_type.column_index[weamh__ikbe] for weamh__ikbe in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in kmoj__qprzq)
    nxfa__lwsp = '\n        '.join(f'row[{i}] = arr_{kmoj__qprzq[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    gral__pqg = f'len(arr_{kmoj__qprzq[0]})'
    dxfyn__nafiv = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in dxfyn__nafiv:
        vstwe__bem = dxfyn__nafiv[func_name]
        ngzv__icg = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        qibi__dqu = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {gral__pqg}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{ngzv__icg})
    for i in numba.parfors.parfor.internal_prange(n):
        {nxfa__lwsp}
        A[i] = {vstwe__bem}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return qibi__dqu
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    pqd__kxs = dict(fill_method=fill_method, limit=limit, freq=freq)
    fmnf__zkpt = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.pct_change()')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    pqd__kxs = dict(axis=axis, skipna=skipna)
    fmnf__zkpt = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumprod()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    pqd__kxs = dict(skipna=skipna)
    fmnf__zkpt = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumsum()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    pqd__kxs = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fmnf__zkpt = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    rdopl__ias = [weamh__ikbe for weamh__ikbe, jumcm__vxlao in zip(df.
        columns, df.data) if _is_describe_type(jumcm__vxlao)]
    if len(rdopl__ias) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    npco__dfth = sum(df.data[df.column_index[weamh__ikbe]].dtype == bodo.
        datetime64ns for weamh__ikbe in rdopl__ias)

    def _get_describe(col_ind):
        xzs__apc = df.data[col_ind].dtype == bodo.datetime64ns
        if npco__dfth and npco__dfth != len(rdopl__ias):
            if xzs__apc:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for weamh__ikbe in rdopl__ias:
        col_ind = df.column_index[weamh__ikbe]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[weamh__ikbe]) for
        weamh__ikbe in rdopl__ias)
    nixao__vruwh = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if npco__dfth == len(rdopl__ias):
        nixao__vruwh = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif npco__dfth:
        nixao__vruwh = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({nixao__vruwh})'
    return _gen_init_df(header, rdopl__ias, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    pqd__kxs = dict(axis=axis, convert=convert, is_copy=is_copy)
    fmnf__zkpt = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    pqd__kxs = dict(freq=freq, axis=axis, fill_value=fill_value)
    fmnf__zkpt = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for dpbmn__rrtp in df.data:
        if not is_supported_shift_array_type(dpbmn__rrtp):
            raise BodoError(
                f'Dataframe.shift() column input type {dpbmn__rrtp.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    pqd__kxs = dict(axis=axis)
    fmnf__zkpt = dict(axis=0)
    check_unsupported_args('DataFrame.diff', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for dpbmn__rrtp in df.data:
        if not (isinstance(dpbmn__rrtp, types.Array) and (isinstance(
            dpbmn__rrtp.dtype, types.Number) or dpbmn__rrtp.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {dpbmn__rrtp.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.explode()')
    ees__zmu = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(ees__zmu)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        fber__ctykk = get_overload_const_list(column)
    else:
        fber__ctykk = [get_literal_value(column)]
    abuqf__pjx = [df.column_index[weamh__ikbe] for weamh__ikbe in fber__ctykk]
    for i in abuqf__pjx:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{abuqf__pjx[0]})\n'
        )
    for i in range(n):
        if i in abuqf__pjx:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    vpuf__akvhz = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    cznlq__bjf = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    columns = tuple(weamh__ikbe for weamh__ikbe in df.columns if 
        weamh__ikbe != col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    vpuf__akvhz = {'inplace': inplace}
    cznlq__bjf = {'inplace': False}
    check_unsupported_args('query', vpuf__akvhz, cznlq__bjf, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        wcsv__nno = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[wcsv__nno]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    vpuf__akvhz = {'subset': subset, 'keep': keep}
    cznlq__bjf = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')
    caq__mnj = len(df.columns)
    qibi__dqu = "def impl(df, subset=None, keep='first'):\n"
    for i in range(caq__mnj):
        qibi__dqu += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    lfgm__sivke = ', '.join(f'data_{i}' for i in range(caq__mnj))
    lfgm__sivke += ',' if caq__mnj == 1 else ''
    qibi__dqu += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({lfgm__sivke}))\n'
        )
    qibi__dqu += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    qibi__dqu += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    vpuf__akvhz = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    cznlq__bjf = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    ftov__jmekq = []
    if is_overload_constant_list(subset):
        ftov__jmekq = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        ftov__jmekq = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        ftov__jmekq = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    uguey__qkz = []
    for col_name in ftov__jmekq:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        uguey__qkz.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', vpuf__akvhz,
        cznlq__bjf, package_name='pandas', module_name='DataFrame')
    lmbj__lvmy = []
    if uguey__qkz:
        for zlrl__heypp in uguey__qkz:
            if isinstance(df.data[zlrl__heypp], bodo.MapArrayType):
                lmbj__lvmy.append(df.columns[zlrl__heypp])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                lmbj__lvmy.append(col_name)
    if lmbj__lvmy:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {lmbj__lvmy} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    caq__mnj = len(df.columns)
    sel__xwjz = ['data_{}'.format(i) for i in uguey__qkz]
    cfiid__uwmmc = ['data_{}'.format(i) for i in range(caq__mnj) if i not in
        uguey__qkz]
    if sel__xwjz:
        ezyir__zkt = len(sel__xwjz)
    else:
        ezyir__zkt = caq__mnj
    ejehr__dcx = ', '.join(sel__xwjz + cfiid__uwmmc)
    data_args = ', '.join('data_{}'.format(i) for i in range(caq__mnj))
    qibi__dqu = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(caq__mnj):
        qibi__dqu += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    qibi__dqu += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(ejehr__dcx, index, ezyir__zkt))
    qibi__dqu += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(qibi__dqu, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
            f'DataFrame.{func_name}()')
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):

                def cond_str(i, gen_all_false):
                    if df.columns[i] in cond.column_index:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {cond.column_index[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            pxd__gza = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                pxd__gza = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                pxd__gza = lambda i: f'other[:,{i}]'
        caq__mnj = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {pxd__gza(i)})'
             for i in range(caq__mnj))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        vkguh__zpes = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(
            vkguh__zpes)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    pqd__kxs = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    fmnf__zkpt = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    caq__mnj = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        for i in range(caq__mnj):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(caq__mnj):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(caq__mnj):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    cte__dvmi = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    qibi__dqu = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    luqre__neevz = {}
    pdxq__gym = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': cte__dvmi}
    pdxq__gym.update(extra_globals)
    exec(qibi__dqu, pdxq__gym, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        xdkcd__eabij = pd.Index(lhs.columns)
        aphap__ysmk = pd.Index(rhs.columns)
        anhj__rch, ggjs__ckw, svdr__nqxv = xdkcd__eabij.join(aphap__ysmk,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(anhj__rch), ggjs__ckw, svdr__nqxv
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        awdg__ors = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        confd__xzp = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, awdg__ors)
        check_runtime_cols_unsupported(rhs, awdg__ors)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                anhj__rch, ggjs__ckw, svdr__nqxv = _get_binop_columns(lhs, rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {oblba__bxda}) {awdg__ors}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {jkhg__iquq})'
                     if oblba__bxda != -1 and jkhg__iquq != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for oblba__bxda, jkhg__iquq in zip(ggjs__ckw, svdr__nqxv))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, anhj__rch, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            jwxqa__xifqg = []
            yju__qmv = []
            if op in confd__xzp:
                for i, utbvf__rqc in enumerate(lhs.data):
                    if is_common_scalar_dtype([utbvf__rqc.dtype, rhs]):
                        jwxqa__xifqg.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {awdg__ors} rhs'
                            )
                    else:
                        dnuq__zpz = f'arr{i}'
                        yju__qmv.append(dnuq__zpz)
                        jwxqa__xifqg.append(dnuq__zpz)
                data_args = ', '.join(jwxqa__xifqg)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {awdg__ors} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(yju__qmv) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {dnuq__zpz} = np.empty(n, dtype=np.bool_)\n' for
                    dnuq__zpz in yju__qmv)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(dnuq__zpz, op ==
                    operator.ne) for dnuq__zpz in yju__qmv)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            jwxqa__xifqg = []
            yju__qmv = []
            if op in confd__xzp:
                for i, utbvf__rqc in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, utbvf__rqc.dtype]):
                        jwxqa__xifqg.append(
                            f'lhs {awdg__ors} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        dnuq__zpz = f'arr{i}'
                        yju__qmv.append(dnuq__zpz)
                        jwxqa__xifqg.append(dnuq__zpz)
                data_args = ', '.join(jwxqa__xifqg)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, awdg__ors) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(yju__qmv) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(dnuq__zpz) for dnuq__zpz in yju__qmv)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(dnuq__zpz, op ==
                    operator.ne) for dnuq__zpz in yju__qmv)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        vkguh__zpes = create_binary_op_overload(op)
        overload(op)(vkguh__zpes)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        awdg__ors = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, awdg__ors)
        check_runtime_cols_unsupported(right, awdg__ors)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                anhj__rch, _, svdr__nqxv = _get_binop_columns(left, right, True
                    )
                qibi__dqu = 'def impl(left, right):\n'
                for i, jkhg__iquq in enumerate(svdr__nqxv):
                    if jkhg__iquq == -1:
                        qibi__dqu += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    qibi__dqu += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    qibi__dqu += f"""  df_arr{i} {awdg__ors} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {jkhg__iquq})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    anhj__rch)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(qibi__dqu, anhj__rch, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            qibi__dqu = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                qibi__dqu += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                qibi__dqu += '  df_arr{0} {1} right\n'.format(i, awdg__ors)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(qibi__dqu, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        vkguh__zpes = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(vkguh__zpes)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            awdg__ors = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, awdg__ors)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, awdg__ors) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        vkguh__zpes = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(vkguh__zpes)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            kff__lfev = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                kff__lfev[i] = bodo.libs.array_kernels.isna(obj, i)
            return kff__lfev
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            kff__lfev = np.empty(n, np.bool_)
            for i in range(n):
                kff__lfev[i] = pd.isna(obj[i])
            return kff__lfev
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if isinstance(obj, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, (DataFrameType, SeriesType)):
        return lambda obj: obj.notna()
    if isinstance(obj, (types.List, types.UniTuple)) or is_array_typ(obj,
        include_index_series=True):
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    vpuf__akvhz = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    cznlq__bjf = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', vpuf__akvhz, cznlq__bjf, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    neukz__jtb = str(expr_node)
    return neukz__jtb.startswith('left.') or neukz__jtb.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    fbkym__hax = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (fbkym__hax,))
    gqo__okw = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        ocjc__smrr = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        zvs__vop = {('NOT_NA', gqo__okw(utbvf__rqc)): utbvf__rqc for
            utbvf__rqc in null_set}
        azp__api, _, _ = _parse_query_expr(ocjc__smrr, env, [], [], None,
            join_cleaned_cols=zvs__vop)
        ymo__japd = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            fdytv__onee = pd.core.computation.ops.BinOp('&', azp__api,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = ymo__japd
        return fdytv__onee

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                ccf__dghvj = set()
                rdr__asepa = set()
                brst__qvnj = _insert_NA_cond_body(expr_node.lhs, ccf__dghvj)
                lhb__jljf = _insert_NA_cond_body(expr_node.rhs, rdr__asepa)
                vaz__jesl = ccf__dghvj.intersection(rdr__asepa)
                ccf__dghvj.difference_update(vaz__jesl)
                rdr__asepa.difference_update(vaz__jesl)
                null_set.update(vaz__jesl)
                expr_node.lhs = append_null_checks(brst__qvnj, ccf__dghvj)
                expr_node.rhs = append_null_checks(lhb__jljf, rdr__asepa)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            qdex__bom = expr_node.name
            iryaw__uznvh, col_name = qdex__bom.split('.')
            if iryaw__uznvh == 'left':
                hugn__doid = left_columns
                data = left_data
            else:
                hugn__doid = right_columns
                data = right_data
            btzhs__safwp = data[hugn__doid.index(col_name)]
            if bodo.utils.typing.is_nullable(btzhs__safwp):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    vpjqa__xust = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        tlck__vxkn = str(expr_node.lhs)
        fnu__pql = str(expr_node.rhs)
        if tlck__vxkn.startswith('left.') and fnu__pql.startswith('left.'
            ) or tlck__vxkn.startswith('right.') and fnu__pql.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [tlck__vxkn.split('.')[1]]
        right_on = [fnu__pql.split('.')[1]]
        if tlck__vxkn.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        fzwu__xea, qkdc__iqivz, ztwq__keol = _extract_equal_conds(expr_node.lhs
            )
        ibaw__xwke, sela__yxofs, nikpe__sgsa = _extract_equal_conds(expr_node
            .rhs)
        left_on = fzwu__xea + ibaw__xwke
        right_on = qkdc__iqivz + sela__yxofs
        if ztwq__keol is None:
            return left_on, right_on, nikpe__sgsa
        if nikpe__sgsa is None:
            return left_on, right_on, ztwq__keol
        expr_node.lhs = ztwq__keol
        expr_node.rhs = nikpe__sgsa
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    fbkym__hax = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (fbkym__hax,))
    fbrg__olp = dict()
    gqo__okw = pd.core.computation.parsing.clean_column_name
    for name, uoix__tzsj in (('left', left_columns), ('right', right_columns)):
        for utbvf__rqc in uoix__tzsj:
            bjk__ypfk = gqo__okw(utbvf__rqc)
            gzko__dqwjh = name, bjk__ypfk
            if gzko__dqwjh in fbrg__olp:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{utbvf__rqc}' and '{fbrg__olp[bjk__ypfk]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            fbrg__olp[gzko__dqwjh] = utbvf__rqc
    woqp__rxzsd, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=fbrg__olp)
    left_on, right_on, imet__twsus = _extract_equal_conds(woqp__rxzsd.terms)
    return left_on, right_on, _insert_NA_cond(imet__twsus, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    pqd__kxs = dict(sort=sort, copy=copy, validate=validate)
    fmnf__zkpt = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    ejtb__zqurs = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    pbd__nimb = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in ejtb__zqurs and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, dhrg__nggdt = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if dhrg__nggdt is None:
                    pbd__nimb = ''
                else:
                    pbd__nimb = str(dhrg__nggdt)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ejtb__zqurs
        right_keys = ejtb__zqurs
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    soc__oqnf = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        ypuha__acip = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ypuha__acip = list(get_overload_const_list(suffixes))
    suffix_x = ypuha__acip[0]
    suffix_y = ypuha__acip[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    qibi__dqu = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    qibi__dqu += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    qibi__dqu += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    qibi__dqu += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, soc__oqnf, pbd__nimb))
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    _impl = luqre__neevz['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType, TimeArrayType)
    rrhvh__nbnu = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    cjg__arvjb = {get_overload_const_str(xygxc__zcpgp) for xygxc__zcpgp in
        (left_on, right_on, on) if is_overload_constant_str(xygxc__zcpgp)}
    for df in (left, right):
        for i, utbvf__rqc in enumerate(df.data):
            if not isinstance(utbvf__rqc, valid_dataframe_column_types
                ) and utbvf__rqc not in rrhvh__nbnu:
                raise BodoError(
                    f'{name_func}(): use of column with {type(utbvf__rqc)} in merge unsupported'
                    )
            if df.columns[i] in cjg__arvjb and isinstance(utbvf__rqc,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        ypuha__acip = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ypuha__acip = list(get_overload_const_list(suffixes))
    if len(ypuha__acip) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    ejtb__zqurs = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        anfpf__ahkn = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            anfpf__ahkn = on_str not in ejtb__zqurs and ('left.' in on_str or
                'right.' in on_str)
        if len(ejtb__zqurs) == 0 and not anfpf__ahkn:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    nymb__fcda = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            swqj__idgyg = left.index
            tdsug__xiqx = isinstance(swqj__idgyg, StringIndexType)
            ovv__twuc = right.index
            vwa__vagnv = isinstance(ovv__twuc, StringIndexType)
        elif is_overload_true(left_index):
            swqj__idgyg = left.index
            tdsug__xiqx = isinstance(swqj__idgyg, StringIndexType)
            ovv__twuc = right.data[right.columns.index(right_keys[0])]
            vwa__vagnv = ovv__twuc.dtype == string_type
        elif is_overload_true(right_index):
            swqj__idgyg = left.data[left.columns.index(left_keys[0])]
            tdsug__xiqx = swqj__idgyg.dtype == string_type
            ovv__twuc = right.index
            vwa__vagnv = isinstance(ovv__twuc, StringIndexType)
        if tdsug__xiqx and vwa__vagnv:
            return
        swqj__idgyg = swqj__idgyg.dtype
        ovv__twuc = ovv__twuc.dtype
        try:
            ttp__rpf = nymb__fcda.resolve_function_type(operator.eq, (
                swqj__idgyg, ovv__twuc), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=swqj__idgyg, rk_dtype=ovv__twuc))
    else:
        for riuen__www, qwnk__rbzf in zip(left_keys, right_keys):
            swqj__idgyg = left.data[left.columns.index(riuen__www)].dtype
            jwsil__tup = left.data[left.columns.index(riuen__www)]
            ovv__twuc = right.data[right.columns.index(qwnk__rbzf)].dtype
            gdon__fzxwk = right.data[right.columns.index(qwnk__rbzf)]
            if jwsil__tup == gdon__fzxwk:
                continue
            nnkvn__wlh = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=riuen__www, lk_dtype=swqj__idgyg, rk=qwnk__rbzf,
                rk_dtype=ovv__twuc))
            gdwis__fxa = swqj__idgyg == string_type
            pba__fwixm = ovv__twuc == string_type
            if gdwis__fxa ^ pba__fwixm:
                raise_bodo_error(nnkvn__wlh)
            try:
                ttp__rpf = nymb__fcda.resolve_function_type(operator.eq, (
                    swqj__idgyg, ovv__twuc), {})
            except:
                raise_bodo_error(nnkvn__wlh)


def validate_keys(keys, df):
    ggr__lmw = set(keys).difference(set(df.columns))
    if len(ggr__lmw) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in ggr__lmw:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {ggr__lmw} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    pqd__kxs = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fmnf__zkpt = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    qibi__dqu = "def _impl(left, other, on=None, how='left',\n"
    qibi__dqu += "    lsuffix='', rsuffix='', sort=False):\n"
    qibi__dqu += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    _impl = luqre__neevz['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        avbx__wrgyu = get_overload_const_list(on)
        validate_keys(avbx__wrgyu, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    ejtb__zqurs = tuple(set(left.columns) & set(other.columns))
    if len(ejtb__zqurs) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=ejtb__zqurs))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    zcwph__lyybc = set(left_keys) & set(right_keys)
    xmir__aiku = set(left_columns) & set(right_columns)
    iljkp__njgk = xmir__aiku - zcwph__lyybc
    swkvx__fmn = set(left_columns) - xmir__aiku
    dskq__ilmmy = set(right_columns) - xmir__aiku
    yvv__ogww = {}

    def insertOutColumn(col_name):
        if col_name in yvv__ogww:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        yvv__ogww[col_name] = 0
    for zur__albf in zcwph__lyybc:
        insertOutColumn(zur__albf)
    for zur__albf in iljkp__njgk:
        tzfya__azffj = str(zur__albf) + suffix_x
        rsdo__ory = str(zur__albf) + suffix_y
        insertOutColumn(tzfya__azffj)
        insertOutColumn(rsdo__ory)
    for zur__albf in swkvx__fmn:
        insertOutColumn(zur__albf)
    for zur__albf in dskq__ilmmy:
        insertOutColumn(zur__albf)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    raise BodoError('pandas.merge_asof() not support yet')
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    ejtb__zqurs = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ejtb__zqurs
        right_keys = ejtb__zqurs
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        ypuha__acip = suffixes
    if is_overload_constant_list(suffixes):
        ypuha__acip = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        ypuha__acip = suffixes.value
    suffix_x = ypuha__acip[0]
    suffix_y = ypuha__acip[1]
    qibi__dqu = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    qibi__dqu += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    qibi__dqu += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    qibi__dqu += "    allow_exact_matches=True, direction='backward'):\n"
    qibi__dqu += '  suffix_x = suffixes[0]\n'
    qibi__dqu += '  suffix_y = suffixes[1]\n'
    qibi__dqu += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo}, luqre__neevz)
    _impl = luqre__neevz['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True, _bodo_num_shuffle_keys=-1):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna, _bodo_num_shuffle_keys)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True,
        _bodo_num_shuffle_keys=-1):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna, _bodo_num_shuffle_keys)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna, _num_shuffle_keys):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_bodo_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_bodo_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_bodo_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_bodo_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    if not is_overload_constant_int(_num_shuffle_keys):
        raise_bodo_error(
            f"groupby(): '_num_shuffle_keys' parameter must be a constant integer, not {_num_shuffle_keys}."
            )
    pqd__kxs = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    ntlc__hdinp = dict(sort=False, group_keys=True, squeeze=False, observed
        =True)
    check_unsupported_args('Dataframe.groupby', pqd__kxs, ntlc__hdinp,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    vxs__wvhl = func_name == 'DataFrame.pivot_table'
    if vxs__wvhl:
        if is_overload_none(index) or not is_literal_type(index):
            raise_bodo_error(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise_bodo_error(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise_bodo_error(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise_bodo_error(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    dfloi__hoxv = get_literal_value(columns)
    if isinstance(dfloi__hoxv, (list, tuple)):
        if len(dfloi__hoxv) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {dfloi__hoxv}"
                )
        dfloi__hoxv = dfloi__hoxv[0]
    if dfloi__hoxv not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {dfloi__hoxv} not found in DataFrame {df}."
            )
    wngzk__kul = df.column_index[dfloi__hoxv]
    if is_overload_none(index):
        oldk__vyvn = []
        fykrs__hhs = []
    else:
        fykrs__hhs = get_literal_value(index)
        if not isinstance(fykrs__hhs, (list, tuple)):
            fykrs__hhs = [fykrs__hhs]
        oldk__vyvn = []
        for index in fykrs__hhs:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            oldk__vyvn.append(df.column_index[index])
    if not (all(isinstance(weamh__ikbe, int) for weamh__ikbe in fykrs__hhs) or
        all(isinstance(weamh__ikbe, str) for weamh__ikbe in fykrs__hhs)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        ezx__ihm = []
        mvy__agaph = []
        hpao__xombo = oldk__vyvn + [wngzk__kul]
        for i, weamh__ikbe in enumerate(df.columns):
            if i not in hpao__xombo:
                ezx__ihm.append(i)
                mvy__agaph.append(weamh__ikbe)
    else:
        mvy__agaph = get_literal_value(values)
        if not isinstance(mvy__agaph, (list, tuple)):
            mvy__agaph = [mvy__agaph]
        ezx__ihm = []
        for val in mvy__agaph:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            ezx__ihm.append(df.column_index[val])
    ixy__xzplf = set(ezx__ihm) | set(oldk__vyvn) | {wngzk__kul}
    if len(ixy__xzplf) != len(ezx__ihm) + len(oldk__vyvn) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(oldk__vyvn) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for gkmtv__bnrau in oldk__vyvn:
            index_column = df.data[gkmtv__bnrau]
            check_valid_index_typ(index_column)
    yzm__auiz = df.data[wngzk__kul]
    if isinstance(yzm__auiz, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(yzm__auiz, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for apti__uhxi in ezx__ihm:
        zob__oiv = df.data[apti__uhxi]
        if isinstance(zob__oiv, (bodo.ArrayItemArrayType, bodo.MapArrayType,
            bodo.StructArrayType, bodo.TupleArrayType)
            ) or zob__oiv == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (fykrs__hhs, dfloi__hoxv, mvy__agaph, oldk__vyvn, wngzk__kul,
        ezx__ihm)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (fykrs__hhs, dfloi__hoxv, mvy__agaph, gkmtv__bnrau, wngzk__kul, zqlj__ouum
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(fykrs__hhs) == 0:
        if is_overload_none(data.index.name_typ):
            gzfk__eop = None,
        else:
            gzfk__eop = get_literal_value(data.index.name_typ),
    else:
        gzfk__eop = tuple(fykrs__hhs)
    fykrs__hhs = ColNamesMetaType(gzfk__eop)
    mvy__agaph = ColNamesMetaType(tuple(mvy__agaph))
    dfloi__hoxv = ColNamesMetaType((dfloi__hoxv,))
    qibi__dqu = 'def impl(data, index=None, columns=None, values=None):\n'
    qibi__dqu += "    ev = tracing.Event('df.pivot')\n"
    qibi__dqu += f'    pivot_values = data.iloc[:, {wngzk__kul}].unique()\n'
    qibi__dqu += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(gkmtv__bnrau) == 0:
        qibi__dqu += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        qibi__dqu += '        (\n'
        for qljf__wqtbq in gkmtv__bnrau:
            qibi__dqu += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {qljf__wqtbq}),
"""
        qibi__dqu += '        ),\n'
    qibi__dqu += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {wngzk__kul}),),
"""
    qibi__dqu += '        (\n'
    for apti__uhxi in zqlj__ouum:
        qibi__dqu += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {apti__uhxi}),
"""
    qibi__dqu += '        ),\n'
    qibi__dqu += '        pivot_values,\n'
    qibi__dqu += '        index_lit,\n'
    qibi__dqu += '        columns_lit,\n'
    qibi__dqu += '        values_lit,\n'
    qibi__dqu += '    )\n'
    qibi__dqu += '    ev.finalize()\n'
    qibi__dqu += '    return result\n'
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'index_lit': fykrs__hhs, 'columns_lit':
        dfloi__hoxv, 'values_lit': mvy__agaph, 'tracing': tracing},
        luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot_table()')
    pqd__kxs = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    fmnf__zkpt = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (fykrs__hhs, dfloi__hoxv, mvy__agaph, gkmtv__bnrau, wngzk__kul, zqlj__ouum
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    ovgy__uax = fykrs__hhs
    fykrs__hhs = ColNamesMetaType(tuple(fykrs__hhs))
    mvy__agaph = ColNamesMetaType(tuple(mvy__agaph))
    ypepa__coffn = dfloi__hoxv
    dfloi__hoxv = ColNamesMetaType((dfloi__hoxv,))
    qibi__dqu = 'def impl(\n'
    qibi__dqu += '    data,\n'
    qibi__dqu += '    values=None,\n'
    qibi__dqu += '    index=None,\n'
    qibi__dqu += '    columns=None,\n'
    qibi__dqu += '    aggfunc="mean",\n'
    qibi__dqu += '    fill_value=None,\n'
    qibi__dqu += '    margins=False,\n'
    qibi__dqu += '    dropna=True,\n'
    qibi__dqu += '    margins_name="All",\n'
    qibi__dqu += '    observed=False,\n'
    qibi__dqu += '    sort=True,\n'
    qibi__dqu += '    _pivot_values=None,\n'
    qibi__dqu += '):\n'
    qibi__dqu += "    ev = tracing.Event('df.pivot_table')\n"
    mpn__ywv = gkmtv__bnrau + [wngzk__kul] + zqlj__ouum
    qibi__dqu += f'    data = data.iloc[:, {mpn__ywv}]\n'
    uufog__uhrwi = ovgy__uax + [ypepa__coffn]
    if not is_overload_none(_pivot_values):
        ntbs__mcznq = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(ntbs__mcznq)
        qibi__dqu += '    pivot_values = _pivot_values_arr\n'
        qibi__dqu += (
            f'    data = data[data.iloc[:, {len(gkmtv__bnrau)}].isin(pivot_values)]\n'
            )
        if all(isinstance(weamh__ikbe, str) for weamh__ikbe in ntbs__mcznq):
            aixr__xnlu = pd.array(ntbs__mcznq, 'string')
        elif all(isinstance(weamh__ikbe, int) for weamh__ikbe in ntbs__mcznq):
            aixr__xnlu = np.array(ntbs__mcznq, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        aixr__xnlu = None
    luqqm__ldy = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    ermdk__jzof = len(uufog__uhrwi) if luqqm__ldy else len(ovgy__uax)
    qibi__dqu += f"""    data = data.groupby({uufog__uhrwi!r}, as_index=False, _bodo_num_shuffle_keys={ermdk__jzof}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        qibi__dqu += (
            f'    pivot_values = data.iloc[:, {len(gkmtv__bnrau)}].unique()\n')
    qibi__dqu += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    qibi__dqu += '        (\n'
    for i in range(0, len(gkmtv__bnrau)):
        qibi__dqu += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    qibi__dqu += '        ),\n'
    qibi__dqu += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(gkmtv__bnrau)}),),
"""
    qibi__dqu += '        (\n'
    for i in range(len(gkmtv__bnrau) + 1, len(zqlj__ouum) + len(
        gkmtv__bnrau) + 1):
        qibi__dqu += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    qibi__dqu += '        ),\n'
    qibi__dqu += '        pivot_values,\n'
    qibi__dqu += '        index_lit,\n'
    qibi__dqu += '        columns_lit,\n'
    qibi__dqu += '        values_lit,\n'
    qibi__dqu += '        check_duplicates=False,\n'
    qibi__dqu += f'        is_already_shuffled={not luqqm__ldy},\n'
    qibi__dqu += '        _constant_pivot_values=_constant_pivot_values,\n'
    qibi__dqu += '    )\n'
    qibi__dqu += '    ev.finalize()\n'
    qibi__dqu += '    return result\n'
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'numba': numba, 'index_lit': fykrs__hhs,
        'columns_lit': dfloi__hoxv, 'values_lit': mvy__agaph,
        '_pivot_values_arr': aixr__xnlu, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    pqd__kxs = dict(col_level=col_level, ignore_index=ignore_index)
    fmnf__zkpt = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(frame, DataFrameType):
        raise BodoError("pandas.melt(): 'frame' argument must be a DataFrame.")
    if not is_overload_none(id_vars) and not is_literal_type(id_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'id_vars', if specified, must be a literal.")
    if not is_overload_none(value_vars) and not is_literal_type(value_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'value_vars', if specified, must be a literal.")
    if not is_overload_none(var_name) and not (is_literal_type(var_name) and
        (is_scalar_type(var_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'var_name', if specified, must be a literal.")
    if value_name != 'value' and not (is_literal_type(value_name) and (
        is_scalar_type(value_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'value_name', if specified, must be a literal.")
    var_name = get_literal_value(var_name) if not is_overload_none(var_name
        ) else 'variable'
    value_name = get_literal_value(value_name
        ) if value_name != 'value' else 'value'
    utw__zlyi = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(utw__zlyi, (list, tuple)):
        utw__zlyi = [utw__zlyi]
    for weamh__ikbe in utw__zlyi:
        if weamh__ikbe not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {weamh__ikbe} not found in {frame}."
                )
    ibvk__ovett = [frame.column_index[i] for i in utw__zlyi]
    if is_overload_none(value_vars):
        myik__aexoc = []
        puw__awrk = []
        for i, weamh__ikbe in enumerate(frame.columns):
            if i not in ibvk__ovett:
                myik__aexoc.append(i)
                puw__awrk.append(weamh__ikbe)
    else:
        puw__awrk = get_literal_value(value_vars)
        if not isinstance(puw__awrk, (list, tuple)):
            puw__awrk = [puw__awrk]
        puw__awrk = [v for v in puw__awrk if v not in utw__zlyi]
        if not puw__awrk:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        myik__aexoc = []
        for val in puw__awrk:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            myik__aexoc.append(frame.column_index[val])
    for weamh__ikbe in puw__awrk:
        if weamh__ikbe not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {weamh__ikbe} not found in {frame}."
                )
    if not (all(isinstance(weamh__ikbe, int) for weamh__ikbe in puw__awrk) or
        all(isinstance(weamh__ikbe, str) for weamh__ikbe in puw__awrk)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    gpry__wzobf = frame.data[myik__aexoc[0]]
    fjna__nzd = [frame.data[i].dtype for i in myik__aexoc]
    myik__aexoc = np.array(myik__aexoc, dtype=np.int64)
    ibvk__ovett = np.array(ibvk__ovett, dtype=np.int64)
    _, ehw__rjztz = bodo.utils.typing.get_common_scalar_dtype(fjna__nzd)
    if not ehw__rjztz:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': puw__awrk, 'val_type': gpry__wzobf}
    header = 'def impl(\n'
    header += '  frame,\n'
    header += '  id_vars=None,\n'
    header += '  value_vars=None,\n'
    header += '  var_name=None,\n'
    header += "  value_name='value',\n"
    header += '  col_level=None,\n'
    header += '  ignore_index=True,\n'
    header += '):\n'
    header += (
        '  dummy_id = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, 0)\n'
        )
    if frame.is_table_format and all(v == gpry__wzobf.dtype for v in fjna__nzd
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            myik__aexoc))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(puw__awrk) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {myik__aexoc[0]})
"""
    else:
        vha__doow = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in myik__aexoc)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({vha__doow},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in ibvk__ovett:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(puw__awrk)})\n'
            )
    qvtap__hzq = ', '.join(f'out_id{i}' for i in ibvk__ovett) + (', ' if 
        len(ibvk__ovett) > 0 else '')
    data_args = qvtap__hzq + 'var_col, val_col'
    columns = tuple(utw__zlyi + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(puw__awrk)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    pqd__kxs = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fmnf__zkpt = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(index,
        'pandas.crosstab()')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    pqd__kxs = dict(ignore_index=ignore_index, key=key)
    fmnf__zkpt = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_bodo_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    ydab__xjufl = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        ydab__xjufl.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        ivhk__vwk = [get_overload_const_tuple(by)]
    else:
        ivhk__vwk = get_overload_const_list(by)
    ivhk__vwk = set((k, '') if (k, '') in ydab__xjufl else k for k in ivhk__vwk
        )
    if len(ivhk__vwk.difference(ydab__xjufl)) > 0:
        sumj__cuqu = list(set(get_overload_const_list(by)).difference(
            ydab__xjufl))
        raise_bodo_error(f'sort_values(): invalid keys {sumj__cuqu} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        hsm__zofj = get_overload_const_list(na_position)
        for na_position in hsm__zofj:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_bodo_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    pqd__kxs = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fmnf__zkpt = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'rank', inline='always', no_unliteral=True)
def overload_dataframe_rank(df, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    qibi__dqu = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    caq__mnj = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(caq__mnj))
    for i in range(caq__mnj):
        qibi__dqu += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(qibi__dqu, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    pqd__kxs = dict(limit=limit, downcast=downcast)
    fmnf__zkpt = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    fpn__mjiqt = not is_overload_none(value)
    nmbpc__mca = not is_overload_none(method)
    if fpn__mjiqt and nmbpc__mca:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not fpn__mjiqt and not nmbpc__mca:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if fpn__mjiqt:
        jjru__rie = 'value=value'
    else:
        jjru__rie = 'method=method'
    data_args = [(
        f"df['{weamh__ikbe}'].fillna({jjru__rie}, inplace=inplace)" if
        isinstance(weamh__ikbe, str) else
        f'df[{weamh__ikbe}].fillna({jjru__rie}, inplace=inplace)') for
        weamh__ikbe in df.columns]
    qibi__dqu = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        qibi__dqu += '  ' + '  \n'.join(data_args) + '\n'
        luqre__neevz = {}
        exec(qibi__dqu, {}, luqre__neevz)
        impl = luqre__neevz['impl']
        return impl
    else:
        return _gen_init_df(qibi__dqu, df.columns, ', '.join(jumcm__vxlao +
            '.values' for jumcm__vxlao in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    pqd__kxs = dict(col_level=col_level, col_fill=col_fill)
    fmnf__zkpt = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    qibi__dqu = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    qibi__dqu += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        dae__xya = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            dae__xya)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            qibi__dqu += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            mkn__uwahl = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = mkn__uwahl + data_args
        else:
            clxh__lep = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [clxh__lep] + data_args
    return _gen_init_df(qibi__dqu, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    uqh__gttm = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and uqh__gttm == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(uqh__gttm))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        mjjve__pdhqs = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        tfel__wjk = get_overload_const_list(subset)
        mjjve__pdhqs = []
        for yaa__waoh in tfel__wjk:
            if yaa__waoh not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{yaa__waoh}' not in data frame columns {df}"
                    )
            mjjve__pdhqs.append(df.column_index[yaa__waoh])
    caq__mnj = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(caq__mnj))
    qibi__dqu = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(caq__mnj):
        qibi__dqu += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    qibi__dqu += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in mjjve__pdhqs)))
    qibi__dqu += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(qibi__dqu, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    pqd__kxs = dict(index=index, level=level, errors=errors)
    fmnf__zkpt = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', pqd__kxs, fmnf__zkpt,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            anhru__ydrbg = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            anhru__ydrbg = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            anhru__ydrbg = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            anhru__ydrbg = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for weamh__ikbe in anhru__ydrbg:
        if weamh__ikbe not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(weamh__ikbe, df.columns))
    if len(set(anhru__ydrbg)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    uociw__hpl = tuple(weamh__ikbe for weamh__ikbe in df.columns if 
        weamh__ikbe not in anhru__ydrbg)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[weamh__ikbe], '.copy()' if not inplace else
        '') for weamh__ikbe in uociw__hpl)
    qibi__dqu = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    qibi__dqu += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(qibi__dqu, uociw__hpl, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sample()')
    pqd__kxs = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    ibv__uqdib = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', pqd__kxs, ibv__uqdib,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    caq__mnj = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(caq__mnj))
    npqsz__cvtqv = ', '.join('rhs_data_{}'.format(i) for i in range(caq__mnj))
    qibi__dqu = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    qibi__dqu += '  if (frac == 1 or n == len(df)) and not replace:\n'
    qibi__dqu += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(caq__mnj):
        qibi__dqu += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    qibi__dqu += '  if frac is None:\n'
    qibi__dqu += '    frac_d = -1.0\n'
    qibi__dqu += '  else:\n'
    qibi__dqu += '    frac_d = frac\n'
    qibi__dqu += '  if n is None:\n'
    qibi__dqu += '    n_i = 0\n'
    qibi__dqu += '  else:\n'
    qibi__dqu += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    qibi__dqu += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({npqsz__cvtqv},), {index}, n_i, frac_d, replace)
"""
    qibi__dqu += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(qibi__dqu, df.columns,
        data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    vpuf__akvhz = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    cznlq__bjf = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', vpuf__akvhz, cznlq__bjf,
        package_name='pandas', module_name='DataFrame')
    bde__mlkr = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            xofz__pgsuo = bde__mlkr + '\n'
            xofz__pgsuo += 'Index: 0 entries\n'
            xofz__pgsuo += 'Empty DataFrame'
            print(xofz__pgsuo)
        return _info_impl
    else:
        qibi__dqu = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        qibi__dqu += '    ncols = df.shape[1]\n'
        qibi__dqu += f'    lines = "{bde__mlkr}\\n"\n'
        qibi__dqu += f'    lines += "{df.index}: "\n'
        qibi__dqu += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            qibi__dqu += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            qibi__dqu += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            qibi__dqu += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        qibi__dqu += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        qibi__dqu += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        qibi__dqu += '    column_width = max(space, 7)\n'
        qibi__dqu += '    column= "Column"\n'
        qibi__dqu += '    underl= "------"\n'
        qibi__dqu += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        qibi__dqu += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        qibi__dqu += '    mem_size = 0\n'
        qibi__dqu += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        qibi__dqu += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        qibi__dqu += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        jmwz__ocsru = dict()
        for i in range(len(df.columns)):
            qibi__dqu += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            xgag__dxc = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                xgag__dxc = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                flqzc__tgdz = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                xgag__dxc = f'{flqzc__tgdz[:-7]}'
            qibi__dqu += f'    col_dtype[{i}] = "{xgag__dxc}"\n'
            if xgag__dxc in jmwz__ocsru:
                jmwz__ocsru[xgag__dxc] += 1
            else:
                jmwz__ocsru[xgag__dxc] = 1
            qibi__dqu += f'    col_name[{i}] = "{df.columns[i]}"\n'
            qibi__dqu += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        qibi__dqu += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        qibi__dqu += '    for i in column_info:\n'
        qibi__dqu += "        lines += f'{i}\\n'\n"
        mlqy__pjq = ', '.join(f'{k}({jmwz__ocsru[k]})' for k in sorted(
            jmwz__ocsru))
        qibi__dqu += f"    lines += 'dtypes: {mlqy__pjq}\\n'\n"
        qibi__dqu += '    mem_size += df.index.nbytes\n'
        qibi__dqu += '    total_size = _sizeof_fmt(mem_size)\n'
        qibi__dqu += "    lines += f'memory usage: {total_size}'\n"
        qibi__dqu += '    print(lines)\n'
        luqre__neevz = {}
        exec(qibi__dqu, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, luqre__neevz)
        _info_impl = luqre__neevz['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    qibi__dqu = 'def impl(df, index=True, deep=False):\n'
    rjc__nqq = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes'
    itxsy__qvkan = is_overload_true(index)
    columns = df.columns
    if itxsy__qvkan:
        columns = ('Index',) + columns
    if len(columns) == 0:
        zzxem__sgwu = ()
    elif all(isinstance(weamh__ikbe, int) for weamh__ikbe in columns):
        zzxem__sgwu = np.array(columns, 'int64')
    elif all(isinstance(weamh__ikbe, str) for weamh__ikbe in columns):
        zzxem__sgwu = pd.array(columns, 'string')
    else:
        zzxem__sgwu = columns
    if df.is_table_format and len(df.columns) > 0:
        hyg__xot = int(itxsy__qvkan)
        ydukt__sngku = len(columns)
        qibi__dqu += f'  nbytes_arr = np.empty({ydukt__sngku}, np.int64)\n'
        qibi__dqu += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        qibi__dqu += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {hyg__xot})
"""
        if itxsy__qvkan:
            qibi__dqu += f'  nbytes_arr[0] = {rjc__nqq}\n'
        qibi__dqu += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if itxsy__qvkan:
            data = f'{rjc__nqq},{data}'
        else:
            mddu__jxelz = ',' if len(columns) == 1 else ''
            data = f'{data}{mddu__jxelz}'
        qibi__dqu += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        zzxem__sgwu}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    qkrpk__yxop = 'read_excel_df{}'.format(next_label())
    setattr(types, qkrpk__yxop, df_type)
    ibj__tsomr = False
    if is_overload_constant_list(parse_dates):
        ibj__tsomr = get_overload_const_list(parse_dates)
    wwm__qytia = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    qibi__dqu = f"""
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{qkrpk__yxop}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{wwm__qytia}}},
            engine=engine,
            converters=converters,
            true_values=true_values,
            false_values=false_values,
            skiprows=skiprows,
            nrows=nrows,
            na_values=na_values,
            keep_default_na=keep_default_na,
            na_filter=na_filter,
            verbose=verbose,
            parse_dates={ibj__tsomr},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    luqre__neevz = {}
    exec(qibi__dqu, globals(), luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as zai__kqff:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    qibi__dqu = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    qibi__dqu += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    qibi__dqu += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        qibi__dqu += '   fig, ax = plt.subplots()\n'
    else:
        qibi__dqu += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        qibi__dqu += '   fig.set_figwidth(figsize[0])\n'
        qibi__dqu += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        qibi__dqu += '   xlabel = x\n'
    qibi__dqu += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        qibi__dqu += '   ylabel = y\n'
    else:
        qibi__dqu += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        qibi__dqu += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        qibi__dqu += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    qibi__dqu += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            qibi__dqu += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            dewb__zkpkc = get_overload_const_str(x)
            ufj__baeg = df.columns.index(dewb__zkpkc)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if ufj__baeg != i:
                        qibi__dqu += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            qibi__dqu += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        qibi__dqu += '   ax.scatter(df[x], df[y], s=20)\n'
        qibi__dqu += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        qibi__dqu += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        qibi__dqu += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        qibi__dqu += '   ax.legend()\n'
    qibi__dqu += '   return ax\n'
    luqre__neevz = {}
    exec(qibi__dqu, {'bodo': bodo, 'plt': plt}, luqre__neevz)
    impl = luqre__neevz['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for iyf__mtwpm in df_typ.data:
        if not (isinstance(iyf__mtwpm, IntegerArrayType) or isinstance(
            iyf__mtwpm.dtype, types.Number) or iyf__mtwpm.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        wntk__rnp = args[0]
        qefgy__zvatk = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        ixxf__tkx = wntk__rnp
        check_runtime_cols_unsupported(wntk__rnp, 'set_df_col()')
        if isinstance(wntk__rnp, DataFrameType):
            index = wntk__rnp.index
            if len(wntk__rnp.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(wntk__rnp.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if is_overload_constant_str(val) or val == types.unicode_type:
                val = bodo.dict_str_arr_type
            elif not is_array_typ(val):
                val = dtype_to_array_type(val)
            if qefgy__zvatk in wntk__rnp.columns:
                uociw__hpl = wntk__rnp.columns
                xbg__nfmai = wntk__rnp.columns.index(qefgy__zvatk)
                jeys__vzul = list(wntk__rnp.data)
                jeys__vzul[xbg__nfmai] = val
                jeys__vzul = tuple(jeys__vzul)
            else:
                uociw__hpl = wntk__rnp.columns + (qefgy__zvatk,)
                jeys__vzul = wntk__rnp.data + (val,)
            ixxf__tkx = DataFrameType(jeys__vzul, index, uociw__hpl,
                wntk__rnp.dist, wntk__rnp.is_table_format)
        return ixxf__tkx(*args)


SetDfColInfer.prefer_literal = True


def __bodosql_replace_columns_dummy(df, col_names_to_replace,
    cols_to_replace_with):
    for i in range(len(col_names_to_replace)):
        df[col_names_to_replace[i]] = cols_to_replace_with[i]


@infer_global(__bodosql_replace_columns_dummy)
class BodoSQLReplaceColsInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 3
        assert is_overload_constant_tuple(args[1])
        assert isinstance(args[2], types.BaseTuple)
        agv__yveg = args[0]
        assert isinstance(agv__yveg, DataFrameType) and len(agv__yveg.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        cid__ezq = args[2]
        assert len(col_names_to_replace) == len(cid__ezq
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(agv__yveg.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in agv__yveg.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(agv__yveg,
            '__bodosql_replace_columns_dummy()')
        index = agv__yveg.index
        uociw__hpl = agv__yveg.columns
        jeys__vzul = list(agv__yveg.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            tvznc__aqhny = cid__ezq[i]
            assert isinstance(tvznc__aqhny, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(tvznc__aqhny, SeriesType):
                tvznc__aqhny = tvznc__aqhny.data
            zlrl__heypp = agv__yveg.column_index[col_name]
            jeys__vzul[zlrl__heypp] = tvznc__aqhny
        jeys__vzul = tuple(jeys__vzul)
        ixxf__tkx = DataFrameType(jeys__vzul, index, uociw__hpl, agv__yveg.
            dist, agv__yveg.is_table_format)
        return ixxf__tkx(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    wjgt__yvki = {}

    def _rewrite_membership_op(self, node, left, right):
        mtrp__gjjo = node.op
        op = self.visit(mtrp__gjjo)
        return op, mtrp__gjjo, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    vwzov__knc = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in vwzov__knc:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in vwzov__knc:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        ughg__bdqp = node.attr
        value = node.value
        mkokn__alz = pd.core.computation.ops.LOCAL_TAG
        if ughg__bdqp in ('str', 'dt'):
            try:
                mxc__ewl = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as hnn__ezqn:
                col_name = hnn__ezqn.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            mxc__ewl = str(self.visit(value))
        gzko__dqwjh = mxc__ewl, ughg__bdqp
        if gzko__dqwjh in join_cleaned_cols:
            ughg__bdqp = join_cleaned_cols[gzko__dqwjh]
        name = mxc__ewl + '.' + ughg__bdqp
        if name.startswith(mkokn__alz):
            name = name[len(mkokn__alz):]
        if ughg__bdqp in ('str', 'dt'):
            lmb__dwdyh = columns[cleaned_columns.index(mxc__ewl)]
            wjgt__yvki[lmb__dwdyh] = mxc__ewl
            self.env.scope[name] = 0
            return self.term_type(mkokn__alz + name, self.env)
        vwzov__knc.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in vwzov__knc:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        ohtcd__ihhkk = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        qefgy__zvatk = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(ohtcd__ihhkk), qefgy__zvatk))

    def op__str__(self):
        cpz__ffrmn = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            pzj__yzjtn)) for pzj__yzjtn in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(cpz__ffrmn)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(cpz__ffrmn)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(cpz__ffrmn))
    qgkoq__lyx = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    pzn__znl = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    inme__ity = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    hnz__pgkn = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    swa__nkj = pd.core.computation.ops.Term.__str__
    ycfrw__kfht = pd.core.computation.ops.MathCall.__str__
    gqed__zmkw = pd.core.computation.ops.Op.__str__
    ymo__japd = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        woqp__rxzsd = pd.core.computation.expr.Expr(expr, env=env)
        fla__lwhp = str(woqp__rxzsd)
    except pd.core.computation.ops.UndefinedVariableError as hnn__ezqn:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == hnn__ezqn.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {hnn__ezqn}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            qgkoq__lyx)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            pzn__znl)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = inme__ity
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = hnz__pgkn
        pd.core.computation.ops.Term.__str__ = swa__nkj
        pd.core.computation.ops.MathCall.__str__ = ycfrw__kfht
        pd.core.computation.ops.Op.__str__ = gqed__zmkw
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            ymo__japd)
    bfqb__fbj = pd.core.computation.parsing.clean_column_name
    wjgt__yvki.update({weamh__ikbe: bfqb__fbj(weamh__ikbe) for weamh__ikbe in
        columns if bfqb__fbj(weamh__ikbe) in woqp__rxzsd.names})
    return woqp__rxzsd, fla__lwhp, wjgt__yvki


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        pdhc__sxw = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(pdhc__sxw))
        xdtwx__ntgeo = namedtuple('Pandas', col_names)
        uyukt__agiwn = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], xdtwx__ntgeo)
        super(DataFrameTupleIterator, self).__init__(name, uyukt__agiwn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        davub__ykcos = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        davub__ykcos = [types.Array(types.int64, 1, 'C')] + davub__ykcos
        xns__ssep = DataFrameTupleIterator(col_names, davub__ykcos)
        return xns__ssep(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rzf__tjcu = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            rzf__tjcu)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    sdgug__qeh = args[len(args) // 2:]
    jhx__pma = sig.args[len(sig.args) // 2:]
    fbn__cqb = context.make_helper(builder, sig.return_type)
    vkctg__qvq = context.get_constant(types.intp, 0)
    cge__fdk = cgutils.alloca_once_value(builder, vkctg__qvq)
    fbn__cqb.index = cge__fdk
    for i, arr in enumerate(sdgug__qeh):
        setattr(fbn__cqb, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(sdgug__qeh, jhx__pma):
        context.nrt.incref(builder, arr_typ, arr)
    res = fbn__cqb._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    zrtb__lbkhu, = sig.args
    nhea__fzl, = args
    fbn__cqb = context.make_helper(builder, zrtb__lbkhu, value=nhea__fzl)
    sbl__zxzz = signature(types.intp, zrtb__lbkhu.array_types[1])
    dfrm__yamu = context.compile_internal(builder, lambda a: len(a),
        sbl__zxzz, [fbn__cqb.array0])
    index = builder.load(fbn__cqb.index)
    fzy__fva = builder.icmp_signed('<', index, dfrm__yamu)
    result.set_valid(fzy__fva)
    with builder.if_then(fzy__fva):
        values = [index]
        for i, arr_typ in enumerate(zrtb__lbkhu.array_types[1:]):
            ljx__bhq = getattr(fbn__cqb, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                pzj__nedc = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    pzj__nedc, [ljx__bhq, index])
            else:
                pzj__nedc = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    pzj__nedc, [ljx__bhq, index])
            values.append(val)
        value = context.make_tuple(builder, zrtb__lbkhu.yield_type, values)
        result.yield_(value)
        anb__rcuv = cgutils.increment_index(builder, index)
        builder.store(anb__rcuv, fbn__cqb.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    upwmp__mlycj = ir.Assign(rhs, lhs, expr.loc)
    lbb__vlc = lhs
    pxxp__ptvq = []
    qwam__vxx = []
    hetuv__mgmz = typ.count
    for i in range(hetuv__mgmz):
        mcw__iptmz = ir.Var(lbb__vlc.scope, mk_unique_var('{}_size{}'.
            format(lbb__vlc.name, i)), lbb__vlc.loc)
        hcnl__bwzw = ir.Expr.static_getitem(lhs, i, None, lbb__vlc.loc)
        self.calltypes[hcnl__bwzw] = None
        pxxp__ptvq.append(ir.Assign(hcnl__bwzw, mcw__iptmz, lbb__vlc.loc))
        self._define(equiv_set, mcw__iptmz, types.intp, hcnl__bwzw)
        qwam__vxx.append(mcw__iptmz)
    ovw__qvta = tuple(qwam__vxx)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        ovw__qvta, pre=[upwmp__mlycj] + pxxp__ptvq)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
