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
        awbvj__rljvd = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({awbvj__rljvd})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    npeo__tsstf = 'def impl(df):\n'
    if df.has_runtime_cols:
        npeo__tsstf += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        qjgi__mdlf = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        npeo__tsstf += f'  return {qjgi__mdlf}'
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
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
    elmy__bgfm = len(df.columns)
    qvwr__yluxx = set(i for i in range(elmy__bgfm) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in qvwr__yluxx else '') for i in
        range(elmy__bgfm))
    npeo__tsstf = 'def f(df):\n'.format()
    npeo__tsstf += '    return np.stack(({},), 1)\n'.format(data_args)
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'np': np}, psrrd__hwtf)
    cqbon__wtxgq = psrrd__hwtf['f']
    return cqbon__wtxgq


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
    yyf__smtks = {'dtype': dtype, 'na_value': na_value}
    crwv__xwvdl = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', yyf__smtks, crwv__xwvdl,
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
            bxk__bcjns = bodo.hiframes.table.compute_num_runtime_columns(t)
            return bxk__bcjns * len(t)
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
            bxk__bcjns = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), bxk__bcjns
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    npeo__tsstf = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    lkose__fcp = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    npeo__tsstf += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{lkose__fcp}), {index}, None)
"""
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
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
    yyf__smtks = {'copy': copy, 'errors': errors}
    crwv__xwvdl = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', yyf__smtks, crwv__xwvdl,
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
        dbc__gmk = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        ejpgy__youl = _bodo_object_typeref.instance_type
        assert isinstance(ejpgy__youl, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in ejpgy__youl.column_index:
                    idx = ejpgy__youl.column_index[name]
                    arr_typ = ejpgy__youl.data[idx]
                else:
                    arr_typ = df.data[i]
                dbc__gmk.append(arr_typ)
        else:
            extra_globals = {}
            zxn__bvero = {}
            for i, name in enumerate(ejpgy__youl.columns):
                arr_typ = ejpgy__youl.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    qfd__jobhy = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    qfd__jobhy = boolean_dtype
                else:
                    qfd__jobhy = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = qfd__jobhy
                zxn__bvero[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {zxn__bvero[zde__hzky]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if zde__hzky in zxn__bvero else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, zde__hzky in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        jko__yrg = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            jko__yrg = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in jko__yrg.items()}
            for i, name in enumerate(df.columns):
                if name in jko__yrg:
                    arr_typ = jko__yrg[name]
                else:
                    arr_typ = df.data[i]
                dbc__gmk.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(jko__yrg[zde__hzky])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if zde__hzky in jko__yrg else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, zde__hzky in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        dbc__gmk = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        eyojr__yhl = bodo.TableType(tuple(dbc__gmk))
        extra_globals['out_table_typ'] = eyojr__yhl
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
        oscgj__vlde = types.none
        extra_globals = {'output_arr_typ': oscgj__vlde}
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
        cqj__ngv = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                cqj__ngv.append(arr + '.copy()')
            elif is_overload_false(deep):
                cqj__ngv.append(arr)
            else:
                cqj__ngv.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(cqj__ngv)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    yyf__smtks = {'index': index, 'level': level, 'errors': errors}
    crwv__xwvdl = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', yyf__smtks, crwv__xwvdl,
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
        jqli__pkj = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        jqli__pkj = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    ktad__cpu = tuple([jqli__pkj.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    nrpwc__zugp = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        nrpwc__zugp = df.copy(columns=ktad__cpu)
        oscgj__vlde = types.none
        extra_globals = {'output_arr_typ': oscgj__vlde}
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
        cqj__ngv = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                cqj__ngv.append(arr + '.copy()')
            elif is_overload_false(copy):
                cqj__ngv.append(arr)
            else:
                cqj__ngv.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(cqj__ngv)
    return _gen_init_df(header, ktad__cpu, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    ajq__hnv = not is_overload_none(items)
    qat__tcu = not is_overload_none(like)
    crkc__pppt = not is_overload_none(regex)
    ody__wahuy = ajq__hnv ^ qat__tcu ^ crkc__pppt
    pqslz__cre = not (ajq__hnv or qat__tcu or crkc__pppt)
    if pqslz__cre:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not ody__wahuy:
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
        cyltd__bnltr = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        cyltd__bnltr = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert cyltd__bnltr in {0, 1}
    npeo__tsstf = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if cyltd__bnltr == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if cyltd__bnltr == 1:
        yup__ezs = []
        jrtzb__myme = []
        eztsx__agqr = []
        if ajq__hnv:
            if is_overload_constant_list(items):
                noe__lxj = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if qat__tcu:
            if is_overload_constant_str(like):
                mnhmc__wjqq = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if crkc__pppt:
            if is_overload_constant_str(regex):
                mly__gmlbv = get_overload_const_str(regex)
                mte__tuqs = re.compile(mly__gmlbv)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, zde__hzky in enumerate(df.columns):
            if not is_overload_none(items
                ) and zde__hzky in noe__lxj or not is_overload_none(like
                ) and mnhmc__wjqq in str(zde__hzky) or not is_overload_none(
                regex) and mte__tuqs.search(str(zde__hzky)):
                jrtzb__myme.append(zde__hzky)
                eztsx__agqr.append(i)
        for i in eztsx__agqr:
            var_name = f'data_{i}'
            yup__ezs.append(var_name)
            npeo__tsstf += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(yup__ezs)
        return _gen_init_df(npeo__tsstf, jrtzb__myme, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    nrpwc__zugp = None
    if df.is_table_format:
        oscgj__vlde = types.Array(types.bool_, 1, 'C')
        nrpwc__zugp = DataFrameType(tuple([oscgj__vlde] * len(df.data)), df
            .index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': oscgj__vlde}
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
    nmsq__rop = is_overload_none(include)
    zjycj__itez = is_overload_none(exclude)
    llw__rvry = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if nmsq__rop and zjycj__itez:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not nmsq__rop:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            qmn__enqwk = [dtype_to_array_type(parse_dtype(elem, llw__rvry)) for
                elem in include]
        elif is_legal_input(include):
            qmn__enqwk = [dtype_to_array_type(parse_dtype(include, llw__rvry))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        qmn__enqwk = get_nullable_and_non_nullable_types(qmn__enqwk)
        ilsr__boh = tuple(zde__hzky for i, zde__hzky in enumerate(df.
            columns) if df.data[i] in qmn__enqwk)
    else:
        ilsr__boh = df.columns
    if not zjycj__itez:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            zuphi__epm = [dtype_to_array_type(parse_dtype(elem, llw__rvry)) for
                elem in exclude]
        elif is_legal_input(exclude):
            zuphi__epm = [dtype_to_array_type(parse_dtype(exclude, llw__rvry))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        zuphi__epm = get_nullable_and_non_nullable_types(zuphi__epm)
        ilsr__boh = tuple(zde__hzky for zde__hzky in ilsr__boh if df.data[
            df.column_index[zde__hzky]] not in zuphi__epm)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[zde__hzky]})'
         for zde__hzky in ilsr__boh)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, ilsr__boh, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    nrpwc__zugp = None
    if df.is_table_format:
        oscgj__vlde = types.Array(types.bool_, 1, 'C')
        nrpwc__zugp = DataFrameType(tuple([oscgj__vlde] * len(df.data)), df
            .index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': oscgj__vlde}
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
    mla__gzrdq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in mla__gzrdq:
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
    mla__gzrdq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in mla__gzrdq:
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
    npeo__tsstf = 'def impl(df, values):\n'
    qxayf__uproy = {}
    fqai__nunbc = False
    if isinstance(values, DataFrameType):
        fqai__nunbc = True
        for i, zde__hzky in enumerate(df.columns):
            if zde__hzky in values.column_index:
                khrq__joy = 'val{}'.format(i)
                npeo__tsstf += f"""  {khrq__joy} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[zde__hzky]})
"""
                qxayf__uproy[zde__hzky] = khrq__joy
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        qxayf__uproy = {zde__hzky: 'values' for zde__hzky in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        khrq__joy = 'data{}'.format(i)
        npeo__tsstf += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(khrq__joy, i))
        data.append(khrq__joy)
    cvu__pbpji = ['out{}'.format(i) for i in range(len(df.columns))]
    rfrrr__uca = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    oyzab__wck = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    msmmt__cfkz = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, ktu__kqvj) in enumerate(zip(df.columns, data)):
        if cname in qxayf__uproy:
            fbho__kjzax = qxayf__uproy[cname]
            if fqai__nunbc:
                npeo__tsstf += rfrrr__uca.format(ktu__kqvj, fbho__kjzax,
                    cvu__pbpji[i])
            else:
                npeo__tsstf += oyzab__wck.format(ktu__kqvj, fbho__kjzax,
                    cvu__pbpji[i])
        else:
            npeo__tsstf += msmmt__cfkz.format(cvu__pbpji[i])
    return _gen_init_df(npeo__tsstf, df.columns, ','.join(cvu__pbpji))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    elmy__bgfm = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(elmy__bgfm))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    nki__cydg = [zde__hzky for zde__hzky, unaon__pvjd in zip(df.columns, df
        .data) if bodo.utils.typing._is_pandas_numeric_dtype(unaon__pvjd.dtype)
        ]
    assert len(nki__cydg) != 0
    tlk__xjlr = ''
    if not any(unaon__pvjd == types.float64 for unaon__pvjd in df.data):
        tlk__xjlr = '.astype(np.float64)'
    ltqye__bjirs = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[zde__hzky], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[zde__hzky]], IntegerArrayType) or
        df.data[df.column_index[zde__hzky]] == boolean_array else '') for
        zde__hzky in nki__cydg)
    jlpx__bvw = 'np.stack(({},), 1){}'.format(ltqye__bjirs, tlk__xjlr)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(nki__cydg)))
    index = f'{generate_col_to_index_func_text(nki__cydg)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(jlpx__bvw)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, nki__cydg, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    kta__qhaj = dict(ddof=ddof)
    fok__iva = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    fbs__mcvqx = '1' if is_overload_none(min_periods) else 'min_periods'
    nki__cydg = [zde__hzky for zde__hzky, unaon__pvjd in zip(df.columns, df
        .data) if bodo.utils.typing._is_pandas_numeric_dtype(unaon__pvjd.dtype)
        ]
    if len(nki__cydg) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    tlk__xjlr = ''
    if not any(unaon__pvjd == types.float64 for unaon__pvjd in df.data):
        tlk__xjlr = '.astype(np.float64)'
    ltqye__bjirs = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[zde__hzky], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[zde__hzky]], IntegerArrayType) or
        df.data[df.column_index[zde__hzky]] == boolean_array else '') for
        zde__hzky in nki__cydg)
    jlpx__bvw = 'np.stack(({},), 1){}'.format(ltqye__bjirs, tlk__xjlr)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(nki__cydg)))
    index = f'pd.Index({nki__cydg})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(jlpx__bvw)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        fbs__mcvqx)
    return _gen_init_df(header, nki__cydg, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    kta__qhaj = dict(axis=axis, level=level, numeric_only=numeric_only)
    fok__iva = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    npeo__tsstf = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    npeo__tsstf += '  data = np.array([{}])\n'.format(data_args)
    qjgi__mdlf = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    npeo__tsstf += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {qjgi__mdlf})\n'
        )
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'np': np}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    kta__qhaj = dict(axis=axis)
    fok__iva = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    npeo__tsstf = 'def impl(df, axis=0, dropna=True):\n'
    npeo__tsstf += '  data = np.asarray(({},))\n'.format(data_args)
    qjgi__mdlf = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    npeo__tsstf += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {qjgi__mdlf})\n'
        )
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'np': np}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fok__iva = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fok__iva = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fok__iva = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fok__iva = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fok__iva = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    kta__qhaj = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fok__iva = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    kta__qhaj = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fok__iva = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    kta__qhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fok__iva = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    kta__qhaj = dict(numeric_only=numeric_only, interpolation=interpolation)
    fok__iva = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    kta__qhaj = dict(axis=axis, skipna=skipna)
    fok__iva = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for dqsbz__ykwar in df.data:
        if not (bodo.utils.utils.is_np_array_typ(dqsbz__ykwar) and (
            dqsbz__ykwar.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(dqsbz__ykwar.dtype, (types.Number, types.Boolean))) or
            isinstance(dqsbz__ykwar, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or dqsbz__ykwar in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {dqsbz__ykwar} not supported.'
                )
        if isinstance(dqsbz__ykwar, bodo.CategoricalArrayType
            ) and not dqsbz__ykwar.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    kta__qhaj = dict(axis=axis, skipna=skipna)
    fok__iva = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for dqsbz__ykwar in df.data:
        if not (bodo.utils.utils.is_np_array_typ(dqsbz__ykwar) and (
            dqsbz__ykwar.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(dqsbz__ykwar.dtype, (types.Number, types.Boolean))) or
            isinstance(dqsbz__ykwar, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or dqsbz__ykwar in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {dqsbz__ykwar} not supported.'
                )
        if isinstance(dqsbz__ykwar, bodo.CategoricalArrayType
            ) and not dqsbz__ykwar.dtype.ordered:
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
        nki__cydg = tuple(zde__hzky for zde__hzky, unaon__pvjd in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (unaon__pvjd.dtype))
        out_colnames = nki__cydg
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            bmwrc__gxm = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[zde__hzky]].dtype) for zde__hzky in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(bmwrc__gxm, []))
    except NotImplementedError as pyb__rqomp:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ntp__zvu = ''
    if func_name in ('sum', 'prod'):
        ntp__zvu = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    npeo__tsstf = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ntp__zvu))
    if func_name == 'quantile':
        npeo__tsstf = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        npeo__tsstf = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        npeo__tsstf += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        npeo__tsstf += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    dae__xpejs = ''
    if func_name in ('min', 'max'):
        dae__xpejs = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        dae__xpejs = ', dtype=np.float32'
    cku__tlosh = f'bodo.libs.array_ops.array_op_{func_name}'
    ubq__quwa = ''
    if func_name in ['sum', 'prod']:
        ubq__quwa = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        ubq__quwa = 'index'
    elif func_name == 'quantile':
        ubq__quwa = 'q'
    elif func_name in ['std', 'var']:
        ubq__quwa = 'True, ddof'
    elif func_name == 'median':
        ubq__quwa = 'True'
    data_args = ', '.join(
        f'{cku__tlosh}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[zde__hzky]}), {ubq__quwa})'
         for zde__hzky in out_colnames)
    npeo__tsstf = ''
    if func_name in ('idxmax', 'idxmin'):
        npeo__tsstf += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        npeo__tsstf += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        npeo__tsstf += '  data = np.asarray(({},){})\n'.format(data_args,
            dae__xpejs)
    npeo__tsstf += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return npeo__tsstf


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    crbp__zsd = [df_type.column_index[zde__hzky] for zde__hzky in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in crbp__zsd)
    ewrd__oygg = '\n        '.join(f'row[{i}] = arr_{crbp__zsd[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    uxbnl__gpwv = f'len(arr_{crbp__zsd[0]})'
    niga__ozxj = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in niga__ozxj:
        gukla__sert = niga__ozxj[func_name]
        olmla__tts = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        npeo__tsstf = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {uxbnl__gpwv}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{olmla__tts})
    for i in numba.parfors.parfor.internal_prange(n):
        {ewrd__oygg}
        A[i] = {gukla__sert}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return npeo__tsstf
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    kta__qhaj = dict(fill_method=fill_method, limit=limit, freq=freq)
    fok__iva = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', kta__qhaj, fok__iva,
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
    kta__qhaj = dict(axis=axis, skipna=skipna)
    fok__iva = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', kta__qhaj, fok__iva,
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
    kta__qhaj = dict(skipna=skipna)
    fok__iva = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', kta__qhaj, fok__iva,
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
    kta__qhaj = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fok__iva = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    nki__cydg = [zde__hzky for zde__hzky, unaon__pvjd in zip(df.columns, df
        .data) if _is_describe_type(unaon__pvjd)]
    if len(nki__cydg) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    lwfk__xsm = sum(df.data[df.column_index[zde__hzky]].dtype == bodo.
        datetime64ns for zde__hzky in nki__cydg)

    def _get_describe(col_ind):
        ssj__jxx = df.data[col_ind].dtype == bodo.datetime64ns
        if lwfk__xsm and lwfk__xsm != len(nki__cydg):
            if ssj__jxx:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for zde__hzky in nki__cydg:
        col_ind = df.column_index[zde__hzky]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[zde__hzky]) for
        zde__hzky in nki__cydg)
    wai__bocf = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if lwfk__xsm == len(nki__cydg):
        wai__bocf = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif lwfk__xsm:
        wai__bocf = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({wai__bocf})'
    return _gen_init_df(header, nki__cydg, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    kta__qhaj = dict(axis=axis, convert=convert, is_copy=is_copy)
    fok__iva = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', kta__qhaj, fok__iva,
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
    kta__qhaj = dict(freq=freq, axis=axis, fill_value=fill_value)
    fok__iva = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for lzp__tbv in df.data:
        if not is_supported_shift_array_type(lzp__tbv):
            raise BodoError(
                f'Dataframe.shift() column input type {lzp__tbv.dtype} not supported yet.'
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
    kta__qhaj = dict(axis=axis)
    fok__iva = dict(axis=0)
    check_unsupported_args('DataFrame.diff', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for lzp__tbv in df.data:
        if not (isinstance(lzp__tbv, types.Array) and (isinstance(lzp__tbv.
            dtype, types.Number) or lzp__tbv.dtype == bodo.datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {lzp__tbv.dtype} not supported.'
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
    ywh__goou = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(ywh__goou)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        jai__sstwx = get_overload_const_list(column)
    else:
        jai__sstwx = [get_literal_value(column)]
    khmz__gtcy = [df.column_index[zde__hzky] for zde__hzky in jai__sstwx]
    for i in khmz__gtcy:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{khmz__gtcy[0]})\n'
        )
    for i in range(n):
        if i in khmz__gtcy:
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
    yyf__smtks = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    crwv__xwvdl = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', yyf__smtks, crwv__xwvdl,
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
    columns = tuple(zde__hzky for zde__hzky in df.columns if zde__hzky !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    yyf__smtks = {'inplace': inplace}
    crwv__xwvdl = {'inplace': False}
    check_unsupported_args('query', yyf__smtks, crwv__xwvdl, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        kerya__kwgj = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[kerya__kwgj]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    yyf__smtks = {'subset': subset, 'keep': keep}
    crwv__xwvdl = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', yyf__smtks, crwv__xwvdl,
        package_name='pandas', module_name='DataFrame')
    elmy__bgfm = len(df.columns)
    npeo__tsstf = "def impl(df, subset=None, keep='first'):\n"
    for i in range(elmy__bgfm):
        npeo__tsstf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    lkepr__lspv = ', '.join(f'data_{i}' for i in range(elmy__bgfm))
    lkepr__lspv += ',' if elmy__bgfm == 1 else ''
    npeo__tsstf += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({lkepr__lspv}))\n'
        )
    npeo__tsstf += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    npeo__tsstf += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    yyf__smtks = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    crwv__xwvdl = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    lfs__puj = []
    if is_overload_constant_list(subset):
        lfs__puj = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        lfs__puj = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        lfs__puj = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    exul__glq = []
    for col_name in lfs__puj:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        exul__glq.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', yyf__smtks,
        crwv__xwvdl, package_name='pandas', module_name='DataFrame')
    lsm__hvhol = []
    if exul__glq:
        for xsul__wyck in exul__glq:
            if isinstance(df.data[xsul__wyck], bodo.MapArrayType):
                lsm__hvhol.append(df.columns[xsul__wyck])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                lsm__hvhol.append(col_name)
    if lsm__hvhol:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {lsm__hvhol} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    elmy__bgfm = len(df.columns)
    lysk__fpj = ['data_{}'.format(i) for i in exul__glq]
    pnbax__cudht = ['data_{}'.format(i) for i in range(elmy__bgfm) if i not in
        exul__glq]
    if lysk__fpj:
        dgg__zhxae = len(lysk__fpj)
    else:
        dgg__zhxae = elmy__bgfm
    sdzb__wbuj = ', '.join(lysk__fpj + pnbax__cudht)
    data_args = ', '.join('data_{}'.format(i) for i in range(elmy__bgfm))
    npeo__tsstf = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(elmy__bgfm):
        npeo__tsstf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    npeo__tsstf += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(sdzb__wbuj, index, dgg__zhxae))
    npeo__tsstf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(npeo__tsstf, df.columns, data_args, 'index')


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
            nasjr__bvy = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                nasjr__bvy = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                nasjr__bvy = lambda i: f'other[:,{i}]'
        elmy__bgfm = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {nasjr__bvy(i)})'
             for i in range(elmy__bgfm))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        isd__dhqoh = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(isd__dhqoh
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    kta__qhaj = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    fok__iva = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', kta__qhaj, fok__iva,
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
    elmy__bgfm = len(df.columns)
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
        for i in range(elmy__bgfm):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(elmy__bgfm):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(elmy__bgfm):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    gwyc__gddmn = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    npeo__tsstf = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    psrrd__hwtf = {}
    qdy__ajup = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': gwyc__gddmn}
    qdy__ajup.update(extra_globals)
    exec(npeo__tsstf, qdy__ajup, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        gvhxy__lxzg = pd.Index(lhs.columns)
        nfcc__zsqp = pd.Index(rhs.columns)
        ersy__ryimb, duk__lqgd, nyzze__ogiut = gvhxy__lxzg.join(nfcc__zsqp,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(ersy__ryimb), duk__lqgd, nyzze__ogiut
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        waw__reej = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        zobqd__lstf = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, waw__reej)
        check_runtime_cols_unsupported(rhs, waw__reej)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                ersy__ryimb, duk__lqgd, nyzze__ogiut = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {imvm__zcnc}) {waw__reej}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {ouw__dbaz})'
                     if imvm__zcnc != -1 and ouw__dbaz != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for imvm__zcnc, ouw__dbaz in zip(duk__lqgd, nyzze__ogiut))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, ersy__ryimb, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            eih__xcxra = []
            hlmin__tmt = []
            if op in zobqd__lstf:
                for i, sjc__kth in enumerate(lhs.data):
                    if is_common_scalar_dtype([sjc__kth.dtype, rhs]):
                        eih__xcxra.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {waw__reej} rhs'
                            )
                    else:
                        aljqc__hnqtl = f'arr{i}'
                        hlmin__tmt.append(aljqc__hnqtl)
                        eih__xcxra.append(aljqc__hnqtl)
                data_args = ', '.join(eih__xcxra)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {waw__reej} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(hlmin__tmt) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {aljqc__hnqtl} = np.empty(n, dtype=np.bool_)\n' for
                    aljqc__hnqtl in hlmin__tmt)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(aljqc__hnqtl,
                    op == operator.ne) for aljqc__hnqtl in hlmin__tmt)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            eih__xcxra = []
            hlmin__tmt = []
            if op in zobqd__lstf:
                for i, sjc__kth in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, sjc__kth.dtype]):
                        eih__xcxra.append(
                            f'lhs {waw__reej} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        aljqc__hnqtl = f'arr{i}'
                        hlmin__tmt.append(aljqc__hnqtl)
                        eih__xcxra.append(aljqc__hnqtl)
                data_args = ', '.join(eih__xcxra)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, waw__reej) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(hlmin__tmt) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(aljqc__hnqtl) for aljqc__hnqtl in hlmin__tmt)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(aljqc__hnqtl,
                    op == operator.ne) for aljqc__hnqtl in hlmin__tmt)
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
        isd__dhqoh = create_binary_op_overload(op)
        overload(op)(isd__dhqoh)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        waw__reej = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, waw__reej)
        check_runtime_cols_unsupported(right, waw__reej)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                ersy__ryimb, _, nyzze__ogiut = _get_binop_columns(left,
                    right, True)
                npeo__tsstf = 'def impl(left, right):\n'
                for i, ouw__dbaz in enumerate(nyzze__ogiut):
                    if ouw__dbaz == -1:
                        npeo__tsstf += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    npeo__tsstf += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    npeo__tsstf += f"""  df_arr{i} {waw__reej} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {ouw__dbaz})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    ersy__ryimb)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(npeo__tsstf, ersy__ryimb, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            npeo__tsstf = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                npeo__tsstf += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                npeo__tsstf += '  df_arr{0} {1} right\n'.format(i, waw__reej)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(npeo__tsstf, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        isd__dhqoh = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(isd__dhqoh)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            waw__reej = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, waw__reej)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, waw__reej) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        isd__dhqoh = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(isd__dhqoh)


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
            fio__wbxe = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                fio__wbxe[i] = bodo.libs.array_kernels.isna(obj, i)
            return fio__wbxe
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
            fio__wbxe = np.empty(n, np.bool_)
            for i in range(n):
                fio__wbxe[i] = pd.isna(obj[i])
            return fio__wbxe
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
    yyf__smtks = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    crwv__xwvdl = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', yyf__smtks, crwv__xwvdl, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    jvb__fdwjd = str(expr_node)
    return jvb__fdwjd.startswith('left.') or jvb__fdwjd.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    wni__dhhf = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (wni__dhhf,))
    jjlm__kyozr = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        bcvrs__yrgju = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        qbs__yyyu = {('NOT_NA', jjlm__kyozr(sjc__kth)): sjc__kth for
            sjc__kth in null_set}
        tzv__mttx, _, _ = _parse_query_expr(bcvrs__yrgju, env, [], [], None,
            join_cleaned_cols=qbs__yyyu)
        gvkk__lhv = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            mfr__hip = pd.core.computation.ops.BinOp('&', tzv__mttx, expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = gvkk__lhv
        return mfr__hip

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                tof__lryhw = set()
                jgykx__hlnq = set()
                tsjfe__mkxpt = _insert_NA_cond_body(expr_node.lhs, tof__lryhw)
                qjgv__zmitn = _insert_NA_cond_body(expr_node.rhs, jgykx__hlnq)
                xjg__tkbxf = tof__lryhw.intersection(jgykx__hlnq)
                tof__lryhw.difference_update(xjg__tkbxf)
                jgykx__hlnq.difference_update(xjg__tkbxf)
                null_set.update(xjg__tkbxf)
                expr_node.lhs = append_null_checks(tsjfe__mkxpt, tof__lryhw)
                expr_node.rhs = append_null_checks(qjgv__zmitn, jgykx__hlnq)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            qgyi__mjp = expr_node.name
            rmaii__xprzu, col_name = qgyi__mjp.split('.')
            if rmaii__xprzu == 'left':
                ckww__zkabc = left_columns
                data = left_data
            else:
                ckww__zkabc = right_columns
                data = right_data
            pklo__fbghq = data[ckww__zkabc.index(col_name)]
            if bodo.utils.typing.is_nullable(pklo__fbghq):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    wydtc__rrviu = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        acta__mdyy = str(expr_node.lhs)
        okuu__pdrdm = str(expr_node.rhs)
        if acta__mdyy.startswith('left.') and okuu__pdrdm.startswith('left.'
            ) or acta__mdyy.startswith('right.') and okuu__pdrdm.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [acta__mdyy.split('.')[1]]
        right_on = [okuu__pdrdm.split('.')[1]]
        if acta__mdyy.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        vea__hpfit, wqa__nunwb, osxjc__ryp = _extract_equal_conds(expr_node.lhs
            )
        bljbg__ihw, uha__tcgz, vcvfq__jvaa = _extract_equal_conds(expr_node.rhs
            )
        left_on = vea__hpfit + bljbg__ihw
        right_on = wqa__nunwb + uha__tcgz
        if osxjc__ryp is None:
            return left_on, right_on, vcvfq__jvaa
        if vcvfq__jvaa is None:
            return left_on, right_on, osxjc__ryp
        expr_node.lhs = osxjc__ryp
        expr_node.rhs = vcvfq__jvaa
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    wni__dhhf = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (wni__dhhf,))
    jqli__pkj = dict()
    jjlm__kyozr = pd.core.computation.parsing.clean_column_name
    for name, zyozo__eeyb in (('left', left_columns), ('right', right_columns)
        ):
        for sjc__kth in zyozo__eeyb:
            hqa__ekbu = jjlm__kyozr(sjc__kth)
            qswox__ybb = name, hqa__ekbu
            if qswox__ybb in jqli__pkj:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{sjc__kth}' and '{jqli__pkj[hqa__ekbu]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            jqli__pkj[qswox__ybb] = sjc__kth
    hkx__gtry, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=jqli__pkj)
    left_on, right_on, seaqd__actwl = _extract_equal_conds(hkx__gtry.terms)
    return left_on, right_on, _insert_NA_cond(seaqd__actwl, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    kta__qhaj = dict(sort=sort, copy=copy, validate=validate)
    fok__iva = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    ttv__iocl = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    fpo__ndcvo = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in ttv__iocl and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, ujmvd__tirj = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if ujmvd__tirj is None:
                    fpo__ndcvo = ''
                else:
                    fpo__ndcvo = str(ujmvd__tirj)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ttv__iocl
        right_keys = ttv__iocl
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
    tto__iljrq = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        jtdgf__bwu = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        jtdgf__bwu = list(get_overload_const_list(suffixes))
    suffix_x = jtdgf__bwu[0]
    suffix_y = jtdgf__bwu[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    npeo__tsstf = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    npeo__tsstf += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    npeo__tsstf += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    npeo__tsstf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, tto__iljrq, fpo__ndcvo))
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    _impl = psrrd__hwtf['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType)
    enw__epu = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    euigf__hjld = {get_overload_const_str(walfa__pciu) for walfa__pciu in (
        left_on, right_on, on) if is_overload_constant_str(walfa__pciu)}
    for df in (left, right):
        for i, sjc__kth in enumerate(df.data):
            if not isinstance(sjc__kth, valid_dataframe_column_types
                ) and sjc__kth not in enw__epu:
                raise BodoError(
                    f'{name_func}(): use of column with {type(sjc__kth)} in merge unsupported'
                    )
            if df.columns[i] in euigf__hjld and isinstance(sjc__kth,
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
        jtdgf__bwu = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        jtdgf__bwu = list(get_overload_const_list(suffixes))
    if len(jtdgf__bwu) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    ttv__iocl = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        ltr__prdke = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            ltr__prdke = on_str not in ttv__iocl and ('left.' in on_str or 
                'right.' in on_str)
        if len(ttv__iocl) == 0 and not ltr__prdke:
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
    qrl__mxprn = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            hqf__jdxcj = left.index
            hsc__ents = isinstance(hqf__jdxcj, StringIndexType)
            jglfu__nor = right.index
            qjjhn__ztedx = isinstance(jglfu__nor, StringIndexType)
        elif is_overload_true(left_index):
            hqf__jdxcj = left.index
            hsc__ents = isinstance(hqf__jdxcj, StringIndexType)
            jglfu__nor = right.data[right.columns.index(right_keys[0])]
            qjjhn__ztedx = jglfu__nor.dtype == string_type
        elif is_overload_true(right_index):
            hqf__jdxcj = left.data[left.columns.index(left_keys[0])]
            hsc__ents = hqf__jdxcj.dtype == string_type
            jglfu__nor = right.index
            qjjhn__ztedx = isinstance(jglfu__nor, StringIndexType)
        if hsc__ents and qjjhn__ztedx:
            return
        hqf__jdxcj = hqf__jdxcj.dtype
        jglfu__nor = jglfu__nor.dtype
        try:
            hucrp__oagul = qrl__mxprn.resolve_function_type(operator.eq, (
                hqf__jdxcj, jglfu__nor), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=hqf__jdxcj, rk_dtype=jglfu__nor))
    else:
        for gdflr__qgl, runzp__kgd in zip(left_keys, right_keys):
            hqf__jdxcj = left.data[left.columns.index(gdflr__qgl)].dtype
            rxtbh__imj = left.data[left.columns.index(gdflr__qgl)]
            jglfu__nor = right.data[right.columns.index(runzp__kgd)].dtype
            xage__uzl = right.data[right.columns.index(runzp__kgd)]
            if rxtbh__imj == xage__uzl:
                continue
            ryqae__tton = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=gdflr__qgl, lk_dtype=hqf__jdxcj, rk=runzp__kgd,
                rk_dtype=jglfu__nor))
            lcws__cow = hqf__jdxcj == string_type
            ezqgl__xttow = jglfu__nor == string_type
            if lcws__cow ^ ezqgl__xttow:
                raise_bodo_error(ryqae__tton)
            try:
                hucrp__oagul = qrl__mxprn.resolve_function_type(operator.eq,
                    (hqf__jdxcj, jglfu__nor), {})
            except:
                raise_bodo_error(ryqae__tton)


def validate_keys(keys, df):
    sbs__eqgml = set(keys).difference(set(df.columns))
    if len(sbs__eqgml) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in sbs__eqgml:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {sbs__eqgml} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    kta__qhaj = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fok__iva = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', kta__qhaj, fok__iva,
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
    npeo__tsstf = "def _impl(left, other, on=None, how='left',\n"
    npeo__tsstf += "    lsuffix='', rsuffix='', sort=False):\n"
    npeo__tsstf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    _impl = psrrd__hwtf['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        pem__aikhs = get_overload_const_list(on)
        validate_keys(pem__aikhs, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    ttv__iocl = tuple(set(left.columns) & set(other.columns))
    if len(ttv__iocl) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=ttv__iocl))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    rvwa__idx = set(left_keys) & set(right_keys)
    ppb__jpvz = set(left_columns) & set(right_columns)
    wqu__opdb = ppb__jpvz - rvwa__idx
    acs__pakc = set(left_columns) - ppb__jpvz
    awbex__tkyqk = set(right_columns) - ppb__jpvz
    jlarz__smo = {}

    def insertOutColumn(col_name):
        if col_name in jlarz__smo:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        jlarz__smo[col_name] = 0
    for oxm__rvx in rvwa__idx:
        insertOutColumn(oxm__rvx)
    for oxm__rvx in wqu__opdb:
        fixae__ihe = str(oxm__rvx) + suffix_x
        big__kwul = str(oxm__rvx) + suffix_y
        insertOutColumn(fixae__ihe)
        insertOutColumn(big__kwul)
    for oxm__rvx in acs__pakc:
        insertOutColumn(oxm__rvx)
    for oxm__rvx in awbex__tkyqk:
        insertOutColumn(oxm__rvx)
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
    ttv__iocl = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ttv__iocl
        right_keys = ttv__iocl
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
        jtdgf__bwu = suffixes
    if is_overload_constant_list(suffixes):
        jtdgf__bwu = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        jtdgf__bwu = suffixes.value
    suffix_x = jtdgf__bwu[0]
    suffix_y = jtdgf__bwu[1]
    npeo__tsstf = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    npeo__tsstf += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    npeo__tsstf += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    npeo__tsstf += "    allow_exact_matches=True, direction='backward'):\n"
    npeo__tsstf += '  suffix_x = suffixes[0]\n'
    npeo__tsstf += '  suffix_y = suffixes[1]\n'
    npeo__tsstf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo}, psrrd__hwtf)
    _impl = psrrd__hwtf['_impl']
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
    kta__qhaj = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    upnw__iqmms = dict(sort=False, group_keys=True, squeeze=False, observed
        =True)
    check_unsupported_args('Dataframe.groupby', kta__qhaj, upnw__iqmms,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    uao__mcc = func_name == 'DataFrame.pivot_table'
    if uao__mcc:
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
    mau__nrw = get_literal_value(columns)
    if isinstance(mau__nrw, (list, tuple)):
        if len(mau__nrw) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {mau__nrw}"
                )
        mau__nrw = mau__nrw[0]
    if mau__nrw not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {mau__nrw} not found in DataFrame {df}."
            )
    uqrcv__bvu = df.column_index[mau__nrw]
    if is_overload_none(index):
        bcarf__crf = []
        seols__dwhf = []
    else:
        seols__dwhf = get_literal_value(index)
        if not isinstance(seols__dwhf, (list, tuple)):
            seols__dwhf = [seols__dwhf]
        bcarf__crf = []
        for index in seols__dwhf:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            bcarf__crf.append(df.column_index[index])
    if not (all(isinstance(zde__hzky, int) for zde__hzky in seols__dwhf) or
        all(isinstance(zde__hzky, str) for zde__hzky in seols__dwhf)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        rql__tkj = []
        yizcs__dea = []
        zkxym__nkhi = bcarf__crf + [uqrcv__bvu]
        for i, zde__hzky in enumerate(df.columns):
            if i not in zkxym__nkhi:
                rql__tkj.append(i)
                yizcs__dea.append(zde__hzky)
    else:
        yizcs__dea = get_literal_value(values)
        if not isinstance(yizcs__dea, (list, tuple)):
            yizcs__dea = [yizcs__dea]
        rql__tkj = []
        for val in yizcs__dea:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            rql__tkj.append(df.column_index[val])
    zalv__bauc = set(rql__tkj) | set(bcarf__crf) | {uqrcv__bvu}
    if len(zalv__bauc) != len(rql__tkj) + len(bcarf__crf) + 1:
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
    if len(bcarf__crf) == 0:
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
        for kog__ehcap in bcarf__crf:
            index_column = df.data[kog__ehcap]
            check_valid_index_typ(index_column)
    qao__aqa = df.data[uqrcv__bvu]
    if isinstance(qao__aqa, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(qao__aqa, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for kum__nuiv in rql__tkj:
        djh__qkr = df.data[kum__nuiv]
        if isinstance(djh__qkr, (bodo.ArrayItemArrayType, bodo.MapArrayType,
            bodo.StructArrayType, bodo.TupleArrayType)
            ) or djh__qkr == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return seols__dwhf, mau__nrw, yizcs__dea, bcarf__crf, uqrcv__bvu, rql__tkj


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (seols__dwhf, mau__nrw, yizcs__dea, kog__ehcap, uqrcv__bvu, vky__ktvj) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(seols__dwhf) == 0:
        if is_overload_none(data.index.name_typ):
            tabds__jvo = None,
        else:
            tabds__jvo = get_literal_value(data.index.name_typ),
    else:
        tabds__jvo = tuple(seols__dwhf)
    seols__dwhf = ColNamesMetaType(tabds__jvo)
    yizcs__dea = ColNamesMetaType(tuple(yizcs__dea))
    mau__nrw = ColNamesMetaType((mau__nrw,))
    npeo__tsstf = 'def impl(data, index=None, columns=None, values=None):\n'
    npeo__tsstf += "    ev = tracing.Event('df.pivot')\n"
    npeo__tsstf += f'    pivot_values = data.iloc[:, {uqrcv__bvu}].unique()\n'
    npeo__tsstf += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(kog__ehcap) == 0:
        npeo__tsstf += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        npeo__tsstf += '        (\n'
        for hrxb__vhk in kog__ehcap:
            npeo__tsstf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {hrxb__vhk}),
"""
        npeo__tsstf += '        ),\n'
    npeo__tsstf += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {uqrcv__bvu}),),
"""
    npeo__tsstf += '        (\n'
    for kum__nuiv in vky__ktvj:
        npeo__tsstf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {kum__nuiv}),
"""
    npeo__tsstf += '        ),\n'
    npeo__tsstf += '        pivot_values,\n'
    npeo__tsstf += '        index_lit,\n'
    npeo__tsstf += '        columns_lit,\n'
    npeo__tsstf += '        values_lit,\n'
    npeo__tsstf += '    )\n'
    npeo__tsstf += '    ev.finalize()\n'
    npeo__tsstf += '    return result\n'
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'index_lit': seols__dwhf,
        'columns_lit': mau__nrw, 'values_lit': yizcs__dea, 'tracing':
        tracing}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
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
    kta__qhaj = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    fok__iva = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (seols__dwhf, mau__nrw, yizcs__dea, kog__ehcap, uqrcv__bvu, vky__ktvj) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    hbzpc__iqf = seols__dwhf
    seols__dwhf = ColNamesMetaType(tuple(seols__dwhf))
    yizcs__dea = ColNamesMetaType(tuple(yizcs__dea))
    jxe__pjqfg = mau__nrw
    mau__nrw = ColNamesMetaType((mau__nrw,))
    npeo__tsstf = 'def impl(\n'
    npeo__tsstf += '    data,\n'
    npeo__tsstf += '    values=None,\n'
    npeo__tsstf += '    index=None,\n'
    npeo__tsstf += '    columns=None,\n'
    npeo__tsstf += '    aggfunc="mean",\n'
    npeo__tsstf += '    fill_value=None,\n'
    npeo__tsstf += '    margins=False,\n'
    npeo__tsstf += '    dropna=True,\n'
    npeo__tsstf += '    margins_name="All",\n'
    npeo__tsstf += '    observed=False,\n'
    npeo__tsstf += '    sort=True,\n'
    npeo__tsstf += '    _pivot_values=None,\n'
    npeo__tsstf += '):\n'
    npeo__tsstf += "    ev = tracing.Event('df.pivot_table')\n"
    bgzc__brrhs = kog__ehcap + [uqrcv__bvu] + vky__ktvj
    npeo__tsstf += f'    data = data.iloc[:, {bgzc__brrhs}]\n'
    xiup__tliu = hbzpc__iqf + [jxe__pjqfg]
    if not is_overload_none(_pivot_values):
        wuy__xda = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(wuy__xda)
        npeo__tsstf += '    pivot_values = _pivot_values_arr\n'
        npeo__tsstf += (
            f'    data = data[data.iloc[:, {len(kog__ehcap)}].isin(pivot_values)]\n'
            )
        if all(isinstance(zde__hzky, str) for zde__hzky in wuy__xda):
            ybhuc__xfkt = pd.array(wuy__xda, 'string')
        elif all(isinstance(zde__hzky, int) for zde__hzky in wuy__xda):
            ybhuc__xfkt = np.array(wuy__xda, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        ybhuc__xfkt = None
    gpui__bktrr = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    nkhfa__mravz = len(xiup__tliu) if gpui__bktrr else len(hbzpc__iqf)
    npeo__tsstf += f"""    data = data.groupby({xiup__tliu!r}, as_index=False, _bodo_num_shuffle_keys={nkhfa__mravz}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        npeo__tsstf += (
            f'    pivot_values = data.iloc[:, {len(kog__ehcap)}].unique()\n')
    npeo__tsstf += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    npeo__tsstf += '        (\n'
    for i in range(0, len(kog__ehcap)):
        npeo__tsstf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    npeo__tsstf += '        ),\n'
    npeo__tsstf += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(kog__ehcap)}),),
"""
    npeo__tsstf += '        (\n'
    for i in range(len(kog__ehcap) + 1, len(vky__ktvj) + len(kog__ehcap) + 1):
        npeo__tsstf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    npeo__tsstf += '        ),\n'
    npeo__tsstf += '        pivot_values,\n'
    npeo__tsstf += '        index_lit,\n'
    npeo__tsstf += '        columns_lit,\n'
    npeo__tsstf += '        values_lit,\n'
    npeo__tsstf += '        check_duplicates=False,\n'
    npeo__tsstf += f'        is_already_shuffled={not gpui__bktrr},\n'
    npeo__tsstf += '        _constant_pivot_values=_constant_pivot_values,\n'
    npeo__tsstf += '    )\n'
    npeo__tsstf += '    ev.finalize()\n'
    npeo__tsstf += '    return result\n'
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'numba': numba, 'index_lit':
        seols__dwhf, 'columns_lit': mau__nrw, 'values_lit': yizcs__dea,
        '_pivot_values_arr': ybhuc__xfkt, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    kta__qhaj = dict(col_level=col_level, ignore_index=ignore_index)
    fok__iva = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', kta__qhaj, fok__iva,
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
    tpshv__jksb = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(tpshv__jksb, (list, tuple)):
        tpshv__jksb = [tpshv__jksb]
    for zde__hzky in tpshv__jksb:
        if zde__hzky not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {zde__hzky} not found in {frame}."
                )
    jbjs__ddw = [frame.column_index[i] for i in tpshv__jksb]
    if is_overload_none(value_vars):
        mxdv__prtk = []
        enxaw__grp = []
        for i, zde__hzky in enumerate(frame.columns):
            if i not in jbjs__ddw:
                mxdv__prtk.append(i)
                enxaw__grp.append(zde__hzky)
    else:
        enxaw__grp = get_literal_value(value_vars)
        if not isinstance(enxaw__grp, (list, tuple)):
            enxaw__grp = [enxaw__grp]
        enxaw__grp = [v for v in enxaw__grp if v not in tpshv__jksb]
        if not enxaw__grp:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        mxdv__prtk = []
        for val in enxaw__grp:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            mxdv__prtk.append(frame.column_index[val])
    for zde__hzky in enxaw__grp:
        if zde__hzky not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {zde__hzky} not found in {frame}."
                )
    if not (all(isinstance(zde__hzky, int) for zde__hzky in enxaw__grp) or
        all(isinstance(zde__hzky, str) for zde__hzky in enxaw__grp)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    vdp__prevb = frame.data[mxdv__prtk[0]]
    irbd__mlr = [frame.data[i].dtype for i in mxdv__prtk]
    mxdv__prtk = np.array(mxdv__prtk, dtype=np.int64)
    jbjs__ddw = np.array(jbjs__ddw, dtype=np.int64)
    _, dgb__fxx = bodo.utils.typing.get_common_scalar_dtype(irbd__mlr)
    if not dgb__fxx:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': enxaw__grp, 'val_type': vdp__prevb}
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
    if frame.is_table_format and all(v == vdp__prevb.dtype for v in irbd__mlr):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            mxdv__prtk))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(enxaw__grp) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {mxdv__prtk[0]})
"""
    else:
        mfht__iqtl = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in mxdv__prtk)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({mfht__iqtl},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in jbjs__ddw:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(enxaw__grp)})\n'
            )
    seslg__tuu = ', '.join(f'out_id{i}' for i in jbjs__ddw) + (', ' if len(
        jbjs__ddw) > 0 else '')
    data_args = seslg__tuu + 'var_col, val_col'
    columns = tuple(tpshv__jksb + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(enxaw__grp)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    kta__qhaj = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fok__iva = dict(values=None, rownames=None, colnames=None, aggfunc=None,
        margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', kta__qhaj, fok__iva,
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
    kta__qhaj = dict(ignore_index=ignore_index, key=key)
    fok__iva = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', kta__qhaj, fok__iva,
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
    wrhs__wyb = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        wrhs__wyb.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        mcfn__gln = [get_overload_const_tuple(by)]
    else:
        mcfn__gln = get_overload_const_list(by)
    mcfn__gln = set((k, '') if (k, '') in wrhs__wyb else k for k in mcfn__gln)
    if len(mcfn__gln.difference(wrhs__wyb)) > 0:
        yaiz__hvksm = list(set(get_overload_const_list(by)).difference(
            wrhs__wyb))
        raise_bodo_error(f'sort_values(): invalid keys {yaiz__hvksm} for by.')
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
        hkjw__yxr = get_overload_const_list(na_position)
        for na_position in hkjw__yxr:
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
    kta__qhaj = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fok__iva = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', kta__qhaj, fok__iva,
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
    npeo__tsstf = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    elmy__bgfm = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(elmy__bgfm))
    for i in range(elmy__bgfm):
        npeo__tsstf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(npeo__tsstf, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    kta__qhaj = dict(limit=limit, downcast=downcast)
    fok__iva = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', kta__qhaj, fok__iva,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    tnqme__gutwm = not is_overload_none(value)
    hwpsi__epaqv = not is_overload_none(method)
    if tnqme__gutwm and hwpsi__epaqv:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not tnqme__gutwm and not hwpsi__epaqv:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if tnqme__gutwm:
        poc__sdc = 'value=value'
    else:
        poc__sdc = 'method=method'
    data_args = [(f"df['{zde__hzky}'].fillna({poc__sdc}, inplace=inplace)" if
        isinstance(zde__hzky, str) else
        f'df[{zde__hzky}].fillna({poc__sdc}, inplace=inplace)') for
        zde__hzky in df.columns]
    npeo__tsstf = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        npeo__tsstf += '  ' + '  \n'.join(data_args) + '\n'
        psrrd__hwtf = {}
        exec(npeo__tsstf, {}, psrrd__hwtf)
        impl = psrrd__hwtf['impl']
        return impl
    else:
        return _gen_init_df(npeo__tsstf, df.columns, ', '.join(unaon__pvjd +
            '.values' for unaon__pvjd in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    kta__qhaj = dict(col_level=col_level, col_fill=col_fill)
    fok__iva = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', kta__qhaj, fok__iva,
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
    npeo__tsstf = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    npeo__tsstf += (
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
        cnzbs__knv = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            cnzbs__knv)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            npeo__tsstf += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            yqe__jrggs = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = yqe__jrggs + data_args
        else:
            adx__jaz = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [adx__jaz] + data_args
    return _gen_init_df(npeo__tsstf, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    caa__ddvrn = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and caa__ddvrn == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(caa__ddvrn))


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
        xdya__rlakp = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        lgf__cjd = get_overload_const_list(subset)
        xdya__rlakp = []
        for ecarn__ljn in lgf__cjd:
            if ecarn__ljn not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{ecarn__ljn}' not in data frame columns {df}"
                    )
            xdya__rlakp.append(df.column_index[ecarn__ljn])
    elmy__bgfm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(elmy__bgfm))
    npeo__tsstf = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(elmy__bgfm):
        npeo__tsstf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    npeo__tsstf += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in xdya__rlakp)))
    npeo__tsstf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(npeo__tsstf, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    kta__qhaj = dict(index=index, level=level, errors=errors)
    fok__iva = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', kta__qhaj, fok__iva,
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
            gvf__wgjj = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            gvf__wgjj = get_overload_const_list(labels)
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
            gvf__wgjj = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            gvf__wgjj = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for zde__hzky in gvf__wgjj:
        if zde__hzky not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(zde__hzky, df.columns))
    if len(set(gvf__wgjj)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    ktad__cpu = tuple(zde__hzky for zde__hzky in df.columns if zde__hzky not in
        gvf__wgjj)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[zde__hzky], '.copy()' if not inplace else ''
        ) for zde__hzky in ktad__cpu)
    npeo__tsstf = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    npeo__tsstf += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(npeo__tsstf, ktad__cpu, data_args, index)


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
    kta__qhaj = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    advr__hti = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', kta__qhaj, advr__hti,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    elmy__bgfm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(elmy__bgfm))
    hzv__svtb = ', '.join('rhs_data_{}'.format(i) for i in range(elmy__bgfm))
    npeo__tsstf = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    npeo__tsstf += '  if (frac == 1 or n == len(df)) and not replace:\n'
    npeo__tsstf += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(elmy__bgfm):
        npeo__tsstf += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    npeo__tsstf += '  if frac is None:\n'
    npeo__tsstf += '    frac_d = -1.0\n'
    npeo__tsstf += '  else:\n'
    npeo__tsstf += '    frac_d = frac\n'
    npeo__tsstf += '  if n is None:\n'
    npeo__tsstf += '    n_i = 0\n'
    npeo__tsstf += '  else:\n'
    npeo__tsstf += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    npeo__tsstf += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({hzv__svtb},), {index}, n_i, frac_d, replace)
"""
    npeo__tsstf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(npeo__tsstf, df.
        columns, data_args, 'index')


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
    yyf__smtks = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    crwv__xwvdl = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', yyf__smtks, crwv__xwvdl,
        package_name='pandas', module_name='DataFrame')
    bjwem__ephr = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            zch__snc = bjwem__ephr + '\n'
            zch__snc += 'Index: 0 entries\n'
            zch__snc += 'Empty DataFrame'
            print(zch__snc)
        return _info_impl
    else:
        npeo__tsstf = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        npeo__tsstf += '    ncols = df.shape[1]\n'
        npeo__tsstf += f'    lines = "{bjwem__ephr}\\n"\n'
        npeo__tsstf += f'    lines += "{df.index}: "\n'
        npeo__tsstf += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            npeo__tsstf += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            npeo__tsstf += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            npeo__tsstf += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        npeo__tsstf += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        npeo__tsstf += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        npeo__tsstf += '    column_width = max(space, 7)\n'
        npeo__tsstf += '    column= "Column"\n'
        npeo__tsstf += '    underl= "------"\n'
        npeo__tsstf += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        npeo__tsstf += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        npeo__tsstf += '    mem_size = 0\n'
        npeo__tsstf += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        npeo__tsstf += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        npeo__tsstf += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        ziio__ydfu = dict()
        for i in range(len(df.columns)):
            npeo__tsstf += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            whnp__azt = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                whnp__azt = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                til__lnwmy = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                whnp__azt = f'{til__lnwmy[:-7]}'
            npeo__tsstf += f'    col_dtype[{i}] = "{whnp__azt}"\n'
            if whnp__azt in ziio__ydfu:
                ziio__ydfu[whnp__azt] += 1
            else:
                ziio__ydfu[whnp__azt] = 1
            npeo__tsstf += f'    col_name[{i}] = "{df.columns[i]}"\n'
            npeo__tsstf += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        npeo__tsstf += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        npeo__tsstf += '    for i in column_info:\n'
        npeo__tsstf += "        lines += f'{i}\\n'\n"
        rys__ijys = ', '.join(f'{k}({ziio__ydfu[k]})' for k in sorted(
            ziio__ydfu))
        npeo__tsstf += f"    lines += 'dtypes: {rys__ijys}\\n'\n"
        npeo__tsstf += '    mem_size += df.index.nbytes\n'
        npeo__tsstf += '    total_size = _sizeof_fmt(mem_size)\n'
        npeo__tsstf += "    lines += f'memory usage: {total_size}'\n"
        npeo__tsstf += '    print(lines)\n'
        psrrd__hwtf = {}
        exec(npeo__tsstf, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, psrrd__hwtf)
        _info_impl = psrrd__hwtf['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    npeo__tsstf = 'def impl(df, index=True, deep=False):\n'
    jokqe__qehv = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    hkvc__pijh = is_overload_true(index)
    columns = df.columns
    if hkvc__pijh:
        columns = ('Index',) + columns
    if len(columns) == 0:
        kaj__ivd = ()
    elif all(isinstance(zde__hzky, int) for zde__hzky in columns):
        kaj__ivd = np.array(columns, 'int64')
    elif all(isinstance(zde__hzky, str) for zde__hzky in columns):
        kaj__ivd = pd.array(columns, 'string')
    else:
        kaj__ivd = columns
    if df.is_table_format and len(df.columns) > 0:
        xcz__yaq = int(hkvc__pijh)
        bxk__bcjns = len(columns)
        npeo__tsstf += f'  nbytes_arr = np.empty({bxk__bcjns}, np.int64)\n'
        npeo__tsstf += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        npeo__tsstf += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {xcz__yaq})
"""
        if hkvc__pijh:
            npeo__tsstf += f'  nbytes_arr[0] = {jokqe__qehv}\n'
        npeo__tsstf += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if hkvc__pijh:
            data = f'{jokqe__qehv},{data}'
        else:
            lkose__fcp = ',' if len(columns) == 1 else ''
            data = f'{data}{lkose__fcp}'
        npeo__tsstf += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        kaj__ivd}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
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
    knlgv__qjf = 'read_excel_df{}'.format(next_label())
    setattr(types, knlgv__qjf, df_type)
    lytdv__iuyh = False
    if is_overload_constant_list(parse_dates):
        lytdv__iuyh = get_overload_const_list(parse_dates)
    ianb__cgmu = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    npeo__tsstf = f"""
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
    with numba.objmode(df="{knlgv__qjf}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{ianb__cgmu}}},
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
            parse_dates={lytdv__iuyh},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    psrrd__hwtf = {}
    exec(npeo__tsstf, globals(), psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as pyb__rqomp:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    npeo__tsstf = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    npeo__tsstf += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    npeo__tsstf += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        npeo__tsstf += '   fig, ax = plt.subplots()\n'
    else:
        npeo__tsstf += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        npeo__tsstf += '   fig.set_figwidth(figsize[0])\n'
        npeo__tsstf += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        npeo__tsstf += '   xlabel = x\n'
    npeo__tsstf += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        npeo__tsstf += '   ylabel = y\n'
    else:
        npeo__tsstf += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        npeo__tsstf += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        npeo__tsstf += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    npeo__tsstf += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            npeo__tsstf += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            fecnz__fgrh = get_overload_const_str(x)
            tiu__fgni = df.columns.index(fecnz__fgrh)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if tiu__fgni != i:
                        npeo__tsstf += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            npeo__tsstf += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        npeo__tsstf += '   ax.scatter(df[x], df[y], s=20)\n'
        npeo__tsstf += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        npeo__tsstf += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        npeo__tsstf += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        npeo__tsstf += '   ax.legend()\n'
    npeo__tsstf += '   return ax\n'
    psrrd__hwtf = {}
    exec(npeo__tsstf, {'bodo': bodo, 'plt': plt}, psrrd__hwtf)
    impl = psrrd__hwtf['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for rmb__lzt in df_typ.data:
        if not (isinstance(rmb__lzt, IntegerArrayType) or isinstance(
            rmb__lzt.dtype, types.Number) or rmb__lzt.dtype in (bodo.
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
        yjmtc__fiuql = args[0]
        zfzal__pfo = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        zmnu__cbd = yjmtc__fiuql
        check_runtime_cols_unsupported(yjmtc__fiuql, 'set_df_col()')
        if isinstance(yjmtc__fiuql, DataFrameType):
            index = yjmtc__fiuql.index
            if len(yjmtc__fiuql.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(yjmtc__fiuql.columns) == 0:
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
            if zfzal__pfo in yjmtc__fiuql.columns:
                ktad__cpu = yjmtc__fiuql.columns
                vosgo__vui = yjmtc__fiuql.columns.index(zfzal__pfo)
                ygks__fddb = list(yjmtc__fiuql.data)
                ygks__fddb[vosgo__vui] = val
                ygks__fddb = tuple(ygks__fddb)
            else:
                ktad__cpu = yjmtc__fiuql.columns + (zfzal__pfo,)
                ygks__fddb = yjmtc__fiuql.data + (val,)
            zmnu__cbd = DataFrameType(ygks__fddb, index, ktad__cpu,
                yjmtc__fiuql.dist, yjmtc__fiuql.is_table_format)
        return zmnu__cbd(*args)


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
        lxu__ifwsv = args[0]
        assert isinstance(lxu__ifwsv, DataFrameType) and len(lxu__ifwsv.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        jcap__ouz = args[2]
        assert len(col_names_to_replace) == len(jcap__ouz
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(lxu__ifwsv.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in lxu__ifwsv.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(lxu__ifwsv,
            '__bodosql_replace_columns_dummy()')
        index = lxu__ifwsv.index
        ktad__cpu = lxu__ifwsv.columns
        ygks__fddb = list(lxu__ifwsv.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            skfbi__fevoi = jcap__ouz[i]
            assert isinstance(skfbi__fevoi, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(skfbi__fevoi, SeriesType):
                skfbi__fevoi = skfbi__fevoi.data
            xsul__wyck = lxu__ifwsv.column_index[col_name]
            ygks__fddb[xsul__wyck] = skfbi__fevoi
        ygks__fddb = tuple(ygks__fddb)
        zmnu__cbd = DataFrameType(ygks__fddb, index, ktad__cpu, lxu__ifwsv.
            dist, lxu__ifwsv.is_table_format)
        return zmnu__cbd(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    jban__rgcir = {}

    def _rewrite_membership_op(self, node, left, right):
        ciqw__rqn = node.op
        op = self.visit(ciqw__rqn)
        return op, ciqw__rqn, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    nqmth__smci = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in nqmth__smci:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in nqmth__smci:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        zvyv__spnm = node.attr
        value = node.value
        hvnvc__ednu = pd.core.computation.ops.LOCAL_TAG
        if zvyv__spnm in ('str', 'dt'):
            try:
                vkq__tnfwr = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as ajb__xzvg:
                col_name = ajb__xzvg.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            vkq__tnfwr = str(self.visit(value))
        qswox__ybb = vkq__tnfwr, zvyv__spnm
        if qswox__ybb in join_cleaned_cols:
            zvyv__spnm = join_cleaned_cols[qswox__ybb]
        name = vkq__tnfwr + '.' + zvyv__spnm
        if name.startswith(hvnvc__ednu):
            name = name[len(hvnvc__ednu):]
        if zvyv__spnm in ('str', 'dt'):
            jex__pya = columns[cleaned_columns.index(vkq__tnfwr)]
            jban__rgcir[jex__pya] = vkq__tnfwr
            self.env.scope[name] = 0
            return self.term_type(hvnvc__ednu + name, self.env)
        nqmth__smci.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in nqmth__smci:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        hwpe__cflb = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        zfzal__pfo = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(hwpe__cflb), zfzal__pfo))

    def op__str__(self):
        aoj__nrvf = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            okmz__vqgp)) for okmz__vqgp in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(aoj__nrvf)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(aoj__nrvf)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(aoj__nrvf))
    psh__bgo = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    xxf__jbrpd = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    qdz__xjotz = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    lvcg__dfzb = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    thoh__elfsd = pd.core.computation.ops.Term.__str__
    fyb__nhcw = pd.core.computation.ops.MathCall.__str__
    lezo__dqzem = pd.core.computation.ops.Op.__str__
    gvkk__lhv = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        hkx__gtry = pd.core.computation.expr.Expr(expr, env=env)
        tduy__fun = str(hkx__gtry)
    except pd.core.computation.ops.UndefinedVariableError as ajb__xzvg:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == ajb__xzvg.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {ajb__xzvg}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            psh__bgo)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            xxf__jbrpd)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = qdz__xjotz
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lvcg__dfzb
        pd.core.computation.ops.Term.__str__ = thoh__elfsd
        pd.core.computation.ops.MathCall.__str__ = fyb__nhcw
        pd.core.computation.ops.Op.__str__ = lezo__dqzem
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            gvkk__lhv)
    rxi__qcjp = pd.core.computation.parsing.clean_column_name
    jban__rgcir.update({zde__hzky: rxi__qcjp(zde__hzky) for zde__hzky in
        columns if rxi__qcjp(zde__hzky) in hkx__gtry.names})
    return hkx__gtry, tduy__fun, jban__rgcir


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        cnrr__mavnn = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(cnrr__mavnn))
        qyw__equq = namedtuple('Pandas', col_names)
        atn__uzoiw = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], qyw__equq)
        super(DataFrameTupleIterator, self).__init__(name, atn__uzoiw)

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
        swem__wcomh = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        swem__wcomh = [types.Array(types.int64, 1, 'C')] + swem__wcomh
        bbjfc__ftey = DataFrameTupleIterator(col_names, swem__wcomh)
        return bbjfc__ftey(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        boirb__cqzd = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            boirb__cqzd)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    tgzjv__onm = args[len(args) // 2:]
    pwq__ttqh = sig.args[len(sig.args) // 2:]
    zpa__dsmzd = context.make_helper(builder, sig.return_type)
    oaym__vscy = context.get_constant(types.intp, 0)
    wvmm__cnmpn = cgutils.alloca_once_value(builder, oaym__vscy)
    zpa__dsmzd.index = wvmm__cnmpn
    for i, arr in enumerate(tgzjv__onm):
        setattr(zpa__dsmzd, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(tgzjv__onm, pwq__ttqh):
        context.nrt.incref(builder, arr_typ, arr)
    res = zpa__dsmzd._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    vflx__rbruk, = sig.args
    gdqlp__myv, = args
    zpa__dsmzd = context.make_helper(builder, vflx__rbruk, value=gdqlp__myv)
    bkxt__cem = signature(types.intp, vflx__rbruk.array_types[1])
    mtta__rtk = context.compile_internal(builder, lambda a: len(a),
        bkxt__cem, [zpa__dsmzd.array0])
    index = builder.load(zpa__dsmzd.index)
    axexq__qevm = builder.icmp_signed('<', index, mtta__rtk)
    result.set_valid(axexq__qevm)
    with builder.if_then(axexq__qevm):
        values = [index]
        for i, arr_typ in enumerate(vflx__rbruk.array_types[1:]):
            dhglf__iql = getattr(zpa__dsmzd, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                iaaqa__yxl = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    iaaqa__yxl, [dhglf__iql, index])
            else:
                iaaqa__yxl = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    iaaqa__yxl, [dhglf__iql, index])
            values.append(val)
        value = context.make_tuple(builder, vflx__rbruk.yield_type, values)
        result.yield_(value)
        pqt__jmu = cgutils.increment_index(builder, index)
        builder.store(pqt__jmu, zpa__dsmzd.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    rkku__fwlq = ir.Assign(rhs, lhs, expr.loc)
    fpj__ibbp = lhs
    gjz__uka = []
    olt__hvjeg = []
    flyp__xnk = typ.count
    for i in range(flyp__xnk):
        oblb__iszc = ir.Var(fpj__ibbp.scope, mk_unique_var('{}_size{}'.
            format(fpj__ibbp.name, i)), fpj__ibbp.loc)
        alxld__xth = ir.Expr.static_getitem(lhs, i, None, fpj__ibbp.loc)
        self.calltypes[alxld__xth] = None
        gjz__uka.append(ir.Assign(alxld__xth, oblb__iszc, fpj__ibbp.loc))
        self._define(equiv_set, oblb__iszc, types.intp, alxld__xth)
        olt__hvjeg.append(oblb__iszc)
    xjqx__ozq = tuple(olt__hvjeg)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        xjqx__ozq, pre=[rkku__fwlq] + gjz__uka)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
