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
        qeqd__npcc = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({qeqd__npcc})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    vdpc__sjncf = 'def impl(df):\n'
    if df.has_runtime_cols:
        vdpc__sjncf += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        esso__godwd = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        vdpc__sjncf += f'  return {esso__godwd}'
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    impl = chq__mexn['impl']
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
    odif__uqy = len(df.columns)
    pko__uxmvt = set(i for i in range(odif__uqy) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in pko__uxmvt else '') for i in
        range(odif__uqy))
    vdpc__sjncf = 'def f(df):\n'.format()
    vdpc__sjncf += '    return np.stack(({},), 1)\n'.format(data_args)
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'np': np}, chq__mexn)
    olo__uey = chq__mexn['f']
    return olo__uey


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
    sctqx__xuwqq = {'dtype': dtype, 'na_value': na_value}
    baunc__biexz = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', sctqx__xuwqq, baunc__biexz,
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
            bqsh__uga = bodo.hiframes.table.compute_num_runtime_columns(t)
            return bqsh__uga * len(t)
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
            bqsh__uga = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), bqsh__uga
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    vdpc__sjncf = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    vivh__ccfi = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    vdpc__sjncf += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{vivh__ccfi}), {index}, None)
"""
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    impl = chq__mexn['impl']
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
    sctqx__xuwqq = {'copy': copy, 'errors': errors}
    baunc__biexz = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', sctqx__xuwqq, baunc__biexz,
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
        wmp__dlge = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        icrd__gkps = _bodo_object_typeref.instance_type
        assert isinstance(icrd__gkps, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in icrd__gkps.column_index:
                    idx = icrd__gkps.column_index[name]
                    arr_typ = icrd__gkps.data[idx]
                else:
                    arr_typ = df.data[i]
                wmp__dlge.append(arr_typ)
        else:
            extra_globals = {}
            wwhu__mqwet = {}
            for i, name in enumerate(icrd__gkps.columns):
                arr_typ = icrd__gkps.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    mxhai__opp = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    mxhai__opp = boolean_dtype
                else:
                    mxhai__opp = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = mxhai__opp
                wwhu__mqwet[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {wwhu__mqwet[praqx__osxms]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if praqx__osxms in wwhu__mqwet else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, praqx__osxms in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        bdrxz__fjaq = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            bdrxz__fjaq = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in bdrxz__fjaq.items()}
            for i, name in enumerate(df.columns):
                if name in bdrxz__fjaq:
                    arr_typ = bdrxz__fjaq[name]
                else:
                    arr_typ = df.data[i]
                wmp__dlge.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(bdrxz__fjaq[praqx__osxms])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if praqx__osxms in bdrxz__fjaq else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, praqx__osxms in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        wmp__dlge = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        cjl__tyven = bodo.TableType(tuple(wmp__dlge))
        extra_globals['out_table_typ'] = cjl__tyven
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
        poz__qii = types.none
        extra_globals = {'output_arr_typ': poz__qii}
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
        zwivx__kccqw = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                zwivx__kccqw.append(arr + '.copy()')
            elif is_overload_false(deep):
                zwivx__kccqw.append(arr)
            else:
                zwivx__kccqw.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(zwivx__kccqw)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    sctqx__xuwqq = {'index': index, 'level': level, 'errors': errors}
    baunc__biexz = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', sctqx__xuwqq, baunc__biexz,
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
        ycier__rzy = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ycier__rzy = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    rqlnb__myowo = tuple([ycier__rzy.get(df.columns[i], df.columns[i]) for
        i in range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    txib__stai = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        txib__stai = df.copy(columns=rqlnb__myowo)
        poz__qii = types.none
        extra_globals = {'output_arr_typ': poz__qii}
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
        zwivx__kccqw = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                zwivx__kccqw.append(arr + '.copy()')
            elif is_overload_false(copy):
                zwivx__kccqw.append(arr)
            else:
                zwivx__kccqw.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(zwivx__kccqw)
    return _gen_init_df(header, rqlnb__myowo, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    kyesi__ztomq = not is_overload_none(items)
    pgbxe__ogyv = not is_overload_none(like)
    lxqa__dmz = not is_overload_none(regex)
    ghayh__gfmyg = kyesi__ztomq ^ pgbxe__ogyv ^ lxqa__dmz
    gqtv__zmc = not (kyesi__ztomq or pgbxe__ogyv or lxqa__dmz)
    if gqtv__zmc:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not ghayh__gfmyg:
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
        amox__tkm = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        amox__tkm = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert amox__tkm in {0, 1}
    vdpc__sjncf = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if amox__tkm == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if amox__tkm == 1:
        xkb__behta = []
        gmn__xmaa = []
        tzlw__iczm = []
        if kyesi__ztomq:
            if is_overload_constant_list(items):
                wtf__rvnf = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if pgbxe__ogyv:
            if is_overload_constant_str(like):
                qvh__gudz = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if lxqa__dmz:
            if is_overload_constant_str(regex):
                hcf__spgz = get_overload_const_str(regex)
                uyz__yjl = re.compile(hcf__spgz)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, praqx__osxms in enumerate(df.columns):
            if not is_overload_none(items
                ) and praqx__osxms in wtf__rvnf or not is_overload_none(like
                ) and qvh__gudz in str(praqx__osxms) or not is_overload_none(
                regex) and uyz__yjl.search(str(praqx__osxms)):
                gmn__xmaa.append(praqx__osxms)
                tzlw__iczm.append(i)
        for i in tzlw__iczm:
            var_name = f'data_{i}'
            xkb__behta.append(var_name)
            vdpc__sjncf += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(xkb__behta)
        return _gen_init_df(vdpc__sjncf, gmn__xmaa, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    txib__stai = None
    if df.is_table_format:
        poz__qii = types.Array(types.bool_, 1, 'C')
        txib__stai = DataFrameType(tuple([poz__qii] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': poz__qii}
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
    xycjh__ojwdv = is_overload_none(include)
    mgick__gzs = is_overload_none(exclude)
    flnb__dda = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if xycjh__ojwdv and mgick__gzs:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not xycjh__ojwdv:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            mkea__pixha = [dtype_to_array_type(parse_dtype(elem, flnb__dda)
                ) for elem in include]
        elif is_legal_input(include):
            mkea__pixha = [dtype_to_array_type(parse_dtype(include, flnb__dda))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        mkea__pixha = get_nullable_and_non_nullable_types(mkea__pixha)
        bcp__nvmju = tuple(praqx__osxms for i, praqx__osxms in enumerate(df
            .columns) if df.data[i] in mkea__pixha)
    else:
        bcp__nvmju = df.columns
    if not mgick__gzs:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            bagca__ygcwg = [dtype_to_array_type(parse_dtype(elem, flnb__dda
                )) for elem in exclude]
        elif is_legal_input(exclude):
            bagca__ygcwg = [dtype_to_array_type(parse_dtype(exclude,
                flnb__dda))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        bagca__ygcwg = get_nullable_and_non_nullable_types(bagca__ygcwg)
        bcp__nvmju = tuple(praqx__osxms for praqx__osxms in bcp__nvmju if 
            df.data[df.column_index[praqx__osxms]] not in bagca__ygcwg)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[praqx__osxms]})'
         for praqx__osxms in bcp__nvmju)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, bcp__nvmju, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    txib__stai = None
    if df.is_table_format:
        poz__qii = types.Array(types.bool_, 1, 'C')
        txib__stai = DataFrameType(tuple([poz__qii] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': poz__qii}
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
    gqk__ukf = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in gqk__ukf:
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
    gqk__ukf = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in gqk__ukf:
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
    vdpc__sjncf = 'def impl(df, values):\n'
    evupv__ford = {}
    scdqw__bxkkx = False
    if isinstance(values, DataFrameType):
        scdqw__bxkkx = True
        for i, praqx__osxms in enumerate(df.columns):
            if praqx__osxms in values.column_index:
                bdal__yqrcy = 'val{}'.format(i)
                vdpc__sjncf += f"""  {bdal__yqrcy} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[praqx__osxms]})
"""
                evupv__ford[praqx__osxms] = bdal__yqrcy
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        evupv__ford = {praqx__osxms: 'values' for praqx__osxms in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        bdal__yqrcy = 'data{}'.format(i)
        vdpc__sjncf += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(bdal__yqrcy, i))
        data.append(bdal__yqrcy)
    fpa__hpy = ['out{}'.format(i) for i in range(len(df.columns))]
    roj__nyi = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    uwad__ekial = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    uwnck__ryaq = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, mlkx__yketa) in enumerate(zip(df.columns, data)):
        if cname in evupv__ford:
            oxg__ltoj = evupv__ford[cname]
            if scdqw__bxkkx:
                vdpc__sjncf += roj__nyi.format(mlkx__yketa, oxg__ltoj,
                    fpa__hpy[i])
            else:
                vdpc__sjncf += uwad__ekial.format(mlkx__yketa, oxg__ltoj,
                    fpa__hpy[i])
        else:
            vdpc__sjncf += uwnck__ryaq.format(fpa__hpy[i])
    return _gen_init_df(vdpc__sjncf, df.columns, ','.join(fpa__hpy))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    odif__uqy = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(odif__uqy))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    zvbk__xgyu = [praqx__osxms for praqx__osxms, ztak__izkgz in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        ztak__izkgz.dtype)]
    assert len(zvbk__xgyu) != 0
    rcmo__hojg = ''
    if not any(ztak__izkgz == types.float64 for ztak__izkgz in df.data):
        rcmo__hojg = '.astype(np.float64)'
    lwmjc__ytvx = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[praqx__osxms], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[praqx__osxms]], IntegerArrayType
        ) or df.data[df.column_index[praqx__osxms]] == boolean_array else
        '') for praqx__osxms in zvbk__xgyu)
    wooy__imdc = 'np.stack(({},), 1){}'.format(lwmjc__ytvx, rcmo__hojg)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(zvbk__xgyu))
        )
    index = f'{generate_col_to_index_func_text(zvbk__xgyu)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(wooy__imdc)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, zvbk__xgyu, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    vqljc__epoc = dict(ddof=ddof)
    fsw__fmi = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    ipcg__ojb = '1' if is_overload_none(min_periods) else 'min_periods'
    zvbk__xgyu = [praqx__osxms for praqx__osxms, ztak__izkgz in zip(df.
        columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype(
        ztak__izkgz.dtype)]
    if len(zvbk__xgyu) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    rcmo__hojg = ''
    if not any(ztak__izkgz == types.float64 for ztak__izkgz in df.data):
        rcmo__hojg = '.astype(np.float64)'
    lwmjc__ytvx = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[praqx__osxms], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[praqx__osxms]], IntegerArrayType
        ) or df.data[df.column_index[praqx__osxms]] == boolean_array else
        '') for praqx__osxms in zvbk__xgyu)
    wooy__imdc = 'np.stack(({},), 1){}'.format(lwmjc__ytvx, rcmo__hojg)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(zvbk__xgyu))
        )
    index = f'pd.Index({zvbk__xgyu})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(wooy__imdc)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        ipcg__ojb)
    return _gen_init_df(header, zvbk__xgyu, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    vqljc__epoc = dict(axis=axis, level=level, numeric_only=numeric_only)
    fsw__fmi = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    vdpc__sjncf = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    vdpc__sjncf += '  data = np.array([{}])\n'.format(data_args)
    esso__godwd = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    vdpc__sjncf += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {esso__godwd})\n'
        )
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'np': np}, chq__mexn)
    impl = chq__mexn['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    vqljc__epoc = dict(axis=axis)
    fsw__fmi = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    vdpc__sjncf = 'def impl(df, axis=0, dropna=True):\n'
    vdpc__sjncf += '  data = np.asarray(({},))\n'.format(data_args)
    esso__godwd = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    vdpc__sjncf += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {esso__godwd})\n'
        )
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'np': np}, chq__mexn)
    impl = chq__mexn['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    vqljc__epoc = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fsw__fmi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    vqljc__epoc = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fsw__fmi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    vqljc__epoc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fsw__fmi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    vqljc__epoc = dict(numeric_only=numeric_only, interpolation=interpolation)
    fsw__fmi = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    vqljc__epoc = dict(axis=axis, skipna=skipna)
    fsw__fmi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for mhus__cjbr in df.data:
        if not (bodo.utils.utils.is_np_array_typ(mhus__cjbr) and (
            mhus__cjbr.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(mhus__cjbr.dtype, (types.Number, types.Boolean))) or
            isinstance(mhus__cjbr, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or mhus__cjbr in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {mhus__cjbr} not supported.'
                )
        if isinstance(mhus__cjbr, bodo.CategoricalArrayType
            ) and not mhus__cjbr.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    vqljc__epoc = dict(axis=axis, skipna=skipna)
    fsw__fmi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for mhus__cjbr in df.data:
        if not (bodo.utils.utils.is_np_array_typ(mhus__cjbr) and (
            mhus__cjbr.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(mhus__cjbr.dtype, (types.Number, types.Boolean))) or
            isinstance(mhus__cjbr, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or mhus__cjbr in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {mhus__cjbr} not supported.'
                )
        if isinstance(mhus__cjbr, bodo.CategoricalArrayType
            ) and not mhus__cjbr.dtype.ordered:
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
        zvbk__xgyu = tuple(praqx__osxms for praqx__osxms, ztak__izkgz in
            zip(df.columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(ztak__izkgz.dtype))
        out_colnames = zvbk__xgyu
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            nciwz__biis = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[praqx__osxms]].dtype) for praqx__osxms in
                out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(nciwz__biis, []))
    except NotImplementedError as avqc__pavla:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    xzoak__zrlz = ''
    if func_name in ('sum', 'prod'):
        xzoak__zrlz = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    vdpc__sjncf = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, xzoak__zrlz))
    if func_name == 'quantile':
        vdpc__sjncf = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        vdpc__sjncf = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        vdpc__sjncf += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        vdpc__sjncf += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        chq__mexn)
    impl = chq__mexn['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    pod__yjvb = ''
    if func_name in ('min', 'max'):
        pod__yjvb = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        pod__yjvb = ', dtype=np.float32'
    svfc__yvrf = f'bodo.libs.array_ops.array_op_{func_name}'
    bhym__fnhl = ''
    if func_name in ['sum', 'prod']:
        bhym__fnhl = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        bhym__fnhl = 'index'
    elif func_name == 'quantile':
        bhym__fnhl = 'q'
    elif func_name in ['std', 'var']:
        bhym__fnhl = 'True, ddof'
    elif func_name == 'median':
        bhym__fnhl = 'True'
    data_args = ', '.join(
        f'{svfc__yvrf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[praqx__osxms]}), {bhym__fnhl})'
         for praqx__osxms in out_colnames)
    vdpc__sjncf = ''
    if func_name in ('idxmax', 'idxmin'):
        vdpc__sjncf += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        vdpc__sjncf += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        vdpc__sjncf += '  data = np.asarray(({},){})\n'.format(data_args,
            pod__yjvb)
    vdpc__sjncf += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return vdpc__sjncf


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    qvy__xmc = [df_type.column_index[praqx__osxms] for praqx__osxms in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in qvy__xmc)
    howsx__dbuo = '\n        '.join(f'row[{i}] = arr_{qvy__xmc[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    aktrd__lsjr = f'len(arr_{qvy__xmc[0]})'
    hnx__waaet = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in hnx__waaet:
        dqlcj__jkny = hnx__waaet[func_name]
        ubzu__qwuon = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        vdpc__sjncf = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {aktrd__lsjr}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{ubzu__qwuon})
    for i in numba.parfors.parfor.internal_prange(n):
        {howsx__dbuo}
        A[i] = {dqlcj__jkny}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return vdpc__sjncf
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    vqljc__epoc = dict(fill_method=fill_method, limit=limit, freq=freq)
    fsw__fmi = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', vqljc__epoc, fsw__fmi,
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
    vqljc__epoc = dict(axis=axis, skipna=skipna)
    fsw__fmi = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', vqljc__epoc, fsw__fmi,
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
    vqljc__epoc = dict(skipna=skipna)
    fsw__fmi = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', vqljc__epoc, fsw__fmi,
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
    vqljc__epoc = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fsw__fmi = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    zvbk__xgyu = [praqx__osxms for praqx__osxms, ztak__izkgz in zip(df.
        columns, df.data) if _is_describe_type(ztak__izkgz)]
    if len(zvbk__xgyu) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    blmrh__jfkhw = sum(df.data[df.column_index[praqx__osxms]].dtype == bodo
        .datetime64ns for praqx__osxms in zvbk__xgyu)

    def _get_describe(col_ind):
        watay__mzfi = df.data[col_ind].dtype == bodo.datetime64ns
        if blmrh__jfkhw and blmrh__jfkhw != len(zvbk__xgyu):
            if watay__mzfi:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for praqx__osxms in zvbk__xgyu:
        col_ind = df.column_index[praqx__osxms]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[praqx__osxms]) for
        praqx__osxms in zvbk__xgyu)
    jayvc__rjfe = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if blmrh__jfkhw == len(zvbk__xgyu):
        jayvc__rjfe = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif blmrh__jfkhw:
        jayvc__rjfe = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({jayvc__rjfe})'
    return _gen_init_df(header, zvbk__xgyu, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    vqljc__epoc = dict(axis=axis, convert=convert, is_copy=is_copy)
    fsw__fmi = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', vqljc__epoc, fsw__fmi,
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
    vqljc__epoc = dict(freq=freq, axis=axis, fill_value=fill_value)
    fsw__fmi = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for jqzmd__jir in df.data:
        if not is_supported_shift_array_type(jqzmd__jir):
            raise BodoError(
                f'Dataframe.shift() column input type {jqzmd__jir.dtype} not supported yet.'
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
    vqljc__epoc = dict(axis=axis)
    fsw__fmi = dict(axis=0)
    check_unsupported_args('DataFrame.diff', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for jqzmd__jir in df.data:
        if not (isinstance(jqzmd__jir, types.Array) and (isinstance(
            jqzmd__jir.dtype, types.Number) or jqzmd__jir.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {jqzmd__jir.dtype} not supported.'
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
    lcc__nzi = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(lcc__nzi)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        oxn__tfm = get_overload_const_list(column)
    else:
        oxn__tfm = [get_literal_value(column)]
    mjfjp__icxh = [df.column_index[praqx__osxms] for praqx__osxms in oxn__tfm]
    for i in mjfjp__icxh:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{mjfjp__icxh[0]})\n'
        )
    for i in range(n):
        if i in mjfjp__icxh:
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
    sctqx__xuwqq = {'inplace': inplace, 'append': append,
        'verify_integrity': verify_integrity}
    baunc__biexz = {'inplace': False, 'append': False, 'verify_integrity': 
        False}
    check_unsupported_args('DataFrame.set_index', sctqx__xuwqq,
        baunc__biexz, package_name='pandas', module_name='DataFrame')
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
    columns = tuple(praqx__osxms for praqx__osxms in df.columns if 
        praqx__osxms != col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    sctqx__xuwqq = {'inplace': inplace}
    baunc__biexz = {'inplace': False}
    check_unsupported_args('query', sctqx__xuwqq, baunc__biexz,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        nmd__lcbg = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[nmd__lcbg]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    sctqx__xuwqq = {'subset': subset, 'keep': keep}
    baunc__biexz = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', sctqx__xuwqq,
        baunc__biexz, package_name='pandas', module_name='DataFrame')
    odif__uqy = len(df.columns)
    vdpc__sjncf = "def impl(df, subset=None, keep='first'):\n"
    for i in range(odif__uqy):
        vdpc__sjncf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    onq__tmc = ', '.join(f'data_{i}' for i in range(odif__uqy))
    onq__tmc += ',' if odif__uqy == 1 else ''
    vdpc__sjncf += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({onq__tmc}))\n')
    vdpc__sjncf += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    vdpc__sjncf += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    impl = chq__mexn['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    sctqx__xuwqq = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    baunc__biexz = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    zqb__crmcd = []
    if is_overload_constant_list(subset):
        zqb__crmcd = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        zqb__crmcd = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        zqb__crmcd = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    aqu__qszaf = []
    for col_name in zqb__crmcd:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        aqu__qszaf.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', sctqx__xuwqq,
        baunc__biexz, package_name='pandas', module_name='DataFrame')
    utyo__iyw = []
    if aqu__qszaf:
        for kgcxk__upfde in aqu__qszaf:
            if isinstance(df.data[kgcxk__upfde], bodo.MapArrayType):
                utyo__iyw.append(df.columns[kgcxk__upfde])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                utyo__iyw.append(col_name)
    if utyo__iyw:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {utyo__iyw} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    odif__uqy = len(df.columns)
    uqrk__rawdv = ['data_{}'.format(i) for i in aqu__qszaf]
    jhd__wiwh = ['data_{}'.format(i) for i in range(odif__uqy) if i not in
        aqu__qszaf]
    if uqrk__rawdv:
        wwg__gxjub = len(uqrk__rawdv)
    else:
        wwg__gxjub = odif__uqy
    icqed__kaos = ', '.join(uqrk__rawdv + jhd__wiwh)
    data_args = ', '.join('data_{}'.format(i) for i in range(odif__uqy))
    vdpc__sjncf = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(odif__uqy):
        vdpc__sjncf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    vdpc__sjncf += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(icqed__kaos, index, wwg__gxjub))
    vdpc__sjncf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(vdpc__sjncf, df.columns, data_args, 'index')


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
            nrg__geixi = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                nrg__geixi = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                nrg__geixi = lambda i: f'other[:,{i}]'
        odif__uqy = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {nrg__geixi(i)})'
             for i in range(odif__uqy))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        xvtqg__mrrsz = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(
            xvtqg__mrrsz)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    vqljc__epoc = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    fsw__fmi = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', vqljc__epoc, fsw__fmi,
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
    odif__uqy = len(df.columns)
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
        for i in range(odif__uqy):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(odif__uqy):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(odif__uqy):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    qph__mjr = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    vdpc__sjncf = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    chq__mexn = {}
    wnt__iikt = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': qph__mjr}
    wnt__iikt.update(extra_globals)
    exec(vdpc__sjncf, wnt__iikt, chq__mexn)
    impl = chq__mexn['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        mxem__bgzju = pd.Index(lhs.columns)
        hzep__rux = pd.Index(rhs.columns)
        fqan__bgv, pgbxn__rcp, ehj__fydjx = mxem__bgzju.join(hzep__rux, how
            ='left' if is_inplace else 'outer', level=None, return_indexers
            =True)
        return tuple(fqan__bgv), pgbxn__rcp, ehj__fydjx
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        azbuq__ghm = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        gxfa__qbrle = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, azbuq__ghm)
        check_runtime_cols_unsupported(rhs, azbuq__ghm)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                fqan__bgv, pgbxn__rcp, ehj__fydjx = _get_binop_columns(lhs, rhs
                    )
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {xmtt__frt}) {azbuq__ghm}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {ssgcj__wbs})'
                     if xmtt__frt != -1 and ssgcj__wbs != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for xmtt__frt, ssgcj__wbs in zip(pgbxn__rcp, ehj__fydjx))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, fqan__bgv, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            qidmz__nze = []
            zppp__clq = []
            if op in gxfa__qbrle:
                for i, kfle__xtg in enumerate(lhs.data):
                    if is_common_scalar_dtype([kfle__xtg.dtype, rhs]):
                        qidmz__nze.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {azbuq__ghm} rhs'
                            )
                    else:
                        lfjs__mfyn = f'arr{i}'
                        zppp__clq.append(lfjs__mfyn)
                        qidmz__nze.append(lfjs__mfyn)
                data_args = ', '.join(qidmz__nze)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {azbuq__ghm} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(zppp__clq) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {lfjs__mfyn} = np.empty(n, dtype=np.bool_)\n' for
                    lfjs__mfyn in zppp__clq)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(lfjs__mfyn, 
                    op == operator.ne) for lfjs__mfyn in zppp__clq)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            qidmz__nze = []
            zppp__clq = []
            if op in gxfa__qbrle:
                for i, kfle__xtg in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, kfle__xtg.dtype]):
                        qidmz__nze.append(
                            f'lhs {azbuq__ghm} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        lfjs__mfyn = f'arr{i}'
                        zppp__clq.append(lfjs__mfyn)
                        qidmz__nze.append(lfjs__mfyn)
                data_args = ', '.join(qidmz__nze)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, azbuq__ghm) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(zppp__clq) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(lfjs__mfyn) for lfjs__mfyn in zppp__clq)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(lfjs__mfyn, 
                    op == operator.ne) for lfjs__mfyn in zppp__clq)
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
        xvtqg__mrrsz = create_binary_op_overload(op)
        overload(op)(xvtqg__mrrsz)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        azbuq__ghm = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, azbuq__ghm)
        check_runtime_cols_unsupported(right, azbuq__ghm)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                fqan__bgv, _, ehj__fydjx = _get_binop_columns(left, right, True
                    )
                vdpc__sjncf = 'def impl(left, right):\n'
                for i, ssgcj__wbs in enumerate(ehj__fydjx):
                    if ssgcj__wbs == -1:
                        vdpc__sjncf += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    vdpc__sjncf += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    vdpc__sjncf += f"""  df_arr{i} {azbuq__ghm} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {ssgcj__wbs})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    fqan__bgv)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(vdpc__sjncf, fqan__bgv, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            vdpc__sjncf = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                vdpc__sjncf += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                vdpc__sjncf += '  df_arr{0} {1} right\n'.format(i, azbuq__ghm)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(vdpc__sjncf, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        xvtqg__mrrsz = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(xvtqg__mrrsz)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            azbuq__ghm = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, azbuq__ghm)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, azbuq__ghm) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        xvtqg__mrrsz = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(xvtqg__mrrsz)


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
            omni__khn = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                omni__khn[i] = bodo.libs.array_kernels.isna(obj, i)
            return omni__khn
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
            omni__khn = np.empty(n, np.bool_)
            for i in range(n):
                omni__khn[i] = pd.isna(obj[i])
            return omni__khn
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
    sctqx__xuwqq = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    baunc__biexz = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', sctqx__xuwqq, baunc__biexz,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    mqjn__svrtg = str(expr_node)
    return mqjn__svrtg.startswith('left.') or mqjn__svrtg.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    amkvh__nubud = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (amkvh__nubud,))
    dfqtk__zecp = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        dmg__pacia = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        bpt__kgbc = {('NOT_NA', dfqtk__zecp(kfle__xtg)): kfle__xtg for
            kfle__xtg in null_set}
        jsgdx__ywip, _, _ = _parse_query_expr(dmg__pacia, env, [], [], None,
            join_cleaned_cols=bpt__kgbc)
        ibd__daw = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            tuk__mnh = pd.core.computation.ops.BinOp('&', jsgdx__ywip,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = ibd__daw
        return tuk__mnh

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                vonx__eks = set()
                lgrdu__mvk = set()
                lif__nphx = _insert_NA_cond_body(expr_node.lhs, vonx__eks)
                vnq__qph = _insert_NA_cond_body(expr_node.rhs, lgrdu__mvk)
                jjc__rvss = vonx__eks.intersection(lgrdu__mvk)
                vonx__eks.difference_update(jjc__rvss)
                lgrdu__mvk.difference_update(jjc__rvss)
                null_set.update(jjc__rvss)
                expr_node.lhs = append_null_checks(lif__nphx, vonx__eks)
                expr_node.rhs = append_null_checks(vnq__qph, lgrdu__mvk)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            vixsx__bimmp = expr_node.name
            qqvs__utm, col_name = vixsx__bimmp.split('.')
            if qqvs__utm == 'left':
                sng__yxxav = left_columns
                data = left_data
            else:
                sng__yxxav = right_columns
                data = right_data
            voyw__suqcw = data[sng__yxxav.index(col_name)]
            if bodo.utils.typing.is_nullable(voyw__suqcw):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    yikl__khs = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        fwi__yfitj = str(expr_node.lhs)
        bjem__sdgmh = str(expr_node.rhs)
        if fwi__yfitj.startswith('left.') and bjem__sdgmh.startswith('left.'
            ) or fwi__yfitj.startswith('right.') and bjem__sdgmh.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [fwi__yfitj.split('.')[1]]
        right_on = [bjem__sdgmh.split('.')[1]]
        if fwi__yfitj.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        xxhb__yfkbh, lhwdm__toaa, cfsyh__jhru = _extract_equal_conds(expr_node
            .lhs)
        gvlqj__rhiiq, renks__civk, pteb__sdsd = _extract_equal_conds(expr_node
            .rhs)
        left_on = xxhb__yfkbh + gvlqj__rhiiq
        right_on = lhwdm__toaa + renks__civk
        if cfsyh__jhru is None:
            return left_on, right_on, pteb__sdsd
        if pteb__sdsd is None:
            return left_on, right_on, cfsyh__jhru
        expr_node.lhs = cfsyh__jhru
        expr_node.rhs = pteb__sdsd
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    amkvh__nubud = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (amkvh__nubud,))
    ycier__rzy = dict()
    dfqtk__zecp = pd.core.computation.parsing.clean_column_name
    for name, dnc__wqj in (('left', left_columns), ('right', right_columns)):
        for kfle__xtg in dnc__wqj:
            oia__unoa = dfqtk__zecp(kfle__xtg)
            joxky__fzt = name, oia__unoa
            if joxky__fzt in ycier__rzy:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{kfle__xtg}' and '{ycier__rzy[oia__unoa]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ycier__rzy[joxky__fzt] = kfle__xtg
    rzzb__kzxk, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ycier__rzy)
    left_on, right_on, wsaym__zeacl = _extract_equal_conds(rzzb__kzxk.terms)
    return left_on, right_on, _insert_NA_cond(wsaym__zeacl, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    vqljc__epoc = dict(sort=sort, copy=copy, validate=validate)
    fsw__fmi = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    nft__bse = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    zow__xeq = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in nft__bse and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, jyk__rgs = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if jyk__rgs is None:
                    zow__xeq = ''
                else:
                    zow__xeq = str(jyk__rgs)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = nft__bse
        right_keys = nft__bse
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
    cfhw__hnyow = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        pmmwg__lyog = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        pmmwg__lyog = list(get_overload_const_list(suffixes))
    suffix_x = pmmwg__lyog[0]
    suffix_y = pmmwg__lyog[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    vdpc__sjncf = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    vdpc__sjncf += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    vdpc__sjncf += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    vdpc__sjncf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, cfhw__hnyow, zow__xeq))
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    _impl = chq__mexn['_impl']
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
    gnebj__mvkw = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    bwq__tjl = {get_overload_const_str(yome__vcukj) for yome__vcukj in (
        left_on, right_on, on) if is_overload_constant_str(yome__vcukj)}
    for df in (left, right):
        for i, kfle__xtg in enumerate(df.data):
            if not isinstance(kfle__xtg, valid_dataframe_column_types
                ) and kfle__xtg not in gnebj__mvkw:
                raise BodoError(
                    f'{name_func}(): use of column with {type(kfle__xtg)} in merge unsupported'
                    )
            if df.columns[i] in bwq__tjl and isinstance(kfle__xtg, MapArrayType
                ):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        pmmwg__lyog = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        pmmwg__lyog = list(get_overload_const_list(suffixes))
    if len(pmmwg__lyog) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    nft__bse = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        tdh__ipzi = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            tdh__ipzi = on_str not in nft__bse and ('left.' in on_str or 
                'right.' in on_str)
        if len(nft__bse) == 0 and not tdh__ipzi:
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
    teu__ocke = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            tgn__yqvy = left.index
            irdsg__uxuu = isinstance(tgn__yqvy, StringIndexType)
            rkwsw__gffpb = right.index
            tcgk__qsru = isinstance(rkwsw__gffpb, StringIndexType)
        elif is_overload_true(left_index):
            tgn__yqvy = left.index
            irdsg__uxuu = isinstance(tgn__yqvy, StringIndexType)
            rkwsw__gffpb = right.data[right.columns.index(right_keys[0])]
            tcgk__qsru = rkwsw__gffpb.dtype == string_type
        elif is_overload_true(right_index):
            tgn__yqvy = left.data[left.columns.index(left_keys[0])]
            irdsg__uxuu = tgn__yqvy.dtype == string_type
            rkwsw__gffpb = right.index
            tcgk__qsru = isinstance(rkwsw__gffpb, StringIndexType)
        if irdsg__uxuu and tcgk__qsru:
            return
        tgn__yqvy = tgn__yqvy.dtype
        rkwsw__gffpb = rkwsw__gffpb.dtype
        try:
            upnda__vwpqg = teu__ocke.resolve_function_type(operator.eq, (
                tgn__yqvy, rkwsw__gffpb), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=tgn__yqvy, rk_dtype=rkwsw__gffpb))
    else:
        for hctar__erxfm, ypn__otpem in zip(left_keys, right_keys):
            tgn__yqvy = left.data[left.columns.index(hctar__erxfm)].dtype
            dfut__utreq = left.data[left.columns.index(hctar__erxfm)]
            rkwsw__gffpb = right.data[right.columns.index(ypn__otpem)].dtype
            gwd__kklco = right.data[right.columns.index(ypn__otpem)]
            if dfut__utreq == gwd__kklco:
                continue
            aahps__ruqob = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=hctar__erxfm, lk_dtype=tgn__yqvy, rk=ypn__otpem,
                rk_dtype=rkwsw__gffpb))
            frd__bii = tgn__yqvy == string_type
            euwqv__mdf = rkwsw__gffpb == string_type
            if frd__bii ^ euwqv__mdf:
                raise_bodo_error(aahps__ruqob)
            try:
                upnda__vwpqg = teu__ocke.resolve_function_type(operator.eq,
                    (tgn__yqvy, rkwsw__gffpb), {})
            except:
                raise_bodo_error(aahps__ruqob)


def validate_keys(keys, df):
    mbi__dfv = set(keys).difference(set(df.columns))
    if len(mbi__dfv) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in mbi__dfv:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {mbi__dfv} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    vqljc__epoc = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fsw__fmi = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', vqljc__epoc, fsw__fmi,
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
    vdpc__sjncf = "def _impl(left, other, on=None, how='left',\n"
    vdpc__sjncf += "    lsuffix='', rsuffix='', sort=False):\n"
    vdpc__sjncf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    _impl = chq__mexn['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        ttux__rba = get_overload_const_list(on)
        validate_keys(ttux__rba, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    nft__bse = tuple(set(left.columns) & set(other.columns))
    if len(nft__bse) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=nft__bse))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    tcxlj__lcv = set(left_keys) & set(right_keys)
    yxhw__eurc = set(left_columns) & set(right_columns)
    dxy__tdpxq = yxhw__eurc - tcxlj__lcv
    ynfbf__eixq = set(left_columns) - yxhw__eurc
    bnsgc__pja = set(right_columns) - yxhw__eurc
    bmyn__ztyuu = {}

    def insertOutColumn(col_name):
        if col_name in bmyn__ztyuu:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        bmyn__ztyuu[col_name] = 0
    for karu__dwmx in tcxlj__lcv:
        insertOutColumn(karu__dwmx)
    for karu__dwmx in dxy__tdpxq:
        iuynw__sbdu = str(karu__dwmx) + suffix_x
        ssy__sajso = str(karu__dwmx) + suffix_y
        insertOutColumn(iuynw__sbdu)
        insertOutColumn(ssy__sajso)
    for karu__dwmx in ynfbf__eixq:
        insertOutColumn(karu__dwmx)
    for karu__dwmx in bnsgc__pja:
        insertOutColumn(karu__dwmx)
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
    nft__bse = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = nft__bse
        right_keys = nft__bse
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
        pmmwg__lyog = suffixes
    if is_overload_constant_list(suffixes):
        pmmwg__lyog = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        pmmwg__lyog = suffixes.value
    suffix_x = pmmwg__lyog[0]
    suffix_y = pmmwg__lyog[1]
    vdpc__sjncf = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    vdpc__sjncf += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    vdpc__sjncf += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    vdpc__sjncf += "    allow_exact_matches=True, direction='backward'):\n"
    vdpc__sjncf += '  suffix_x = suffixes[0]\n'
    vdpc__sjncf += '  suffix_y = suffixes[1]\n'
    vdpc__sjncf += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo}, chq__mexn)
    _impl = chq__mexn['_impl']
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
    vqljc__epoc = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    ojb__nxw = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', vqljc__epoc, ojb__nxw,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    nih__xluz = func_name == 'DataFrame.pivot_table'
    if nih__xluz:
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
    fmioc__wmsum = get_literal_value(columns)
    if isinstance(fmioc__wmsum, (list, tuple)):
        if len(fmioc__wmsum) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {fmioc__wmsum}"
                )
        fmioc__wmsum = fmioc__wmsum[0]
    if fmioc__wmsum not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {fmioc__wmsum} not found in DataFrame {df}."
            )
    hvo__ongpv = df.column_index[fmioc__wmsum]
    if is_overload_none(index):
        mznh__kox = []
        uukk__mljhc = []
    else:
        uukk__mljhc = get_literal_value(index)
        if not isinstance(uukk__mljhc, (list, tuple)):
            uukk__mljhc = [uukk__mljhc]
        mznh__kox = []
        for index in uukk__mljhc:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            mznh__kox.append(df.column_index[index])
    if not (all(isinstance(praqx__osxms, int) for praqx__osxms in
        uukk__mljhc) or all(isinstance(praqx__osxms, str) for praqx__osxms in
        uukk__mljhc)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        uwczd__gptgp = []
        dyfux__fuofa = []
        cuno__tlwgj = mznh__kox + [hvo__ongpv]
        for i, praqx__osxms in enumerate(df.columns):
            if i not in cuno__tlwgj:
                uwczd__gptgp.append(i)
                dyfux__fuofa.append(praqx__osxms)
    else:
        dyfux__fuofa = get_literal_value(values)
        if not isinstance(dyfux__fuofa, (list, tuple)):
            dyfux__fuofa = [dyfux__fuofa]
        uwczd__gptgp = []
        for val in dyfux__fuofa:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            uwczd__gptgp.append(df.column_index[val])
    kfm__zdop = set(uwczd__gptgp) | set(mznh__kox) | {hvo__ongpv}
    if len(kfm__zdop) != len(uwczd__gptgp) + len(mznh__kox) + 1:
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
    if len(mznh__kox) == 0:
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
        for jsmb__ilx in mznh__kox:
            index_column = df.data[jsmb__ilx]
            check_valid_index_typ(index_column)
    hmlgh__xtqib = df.data[hvo__ongpv]
    if isinstance(hmlgh__xtqib, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(hmlgh__xtqib, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for yex__hqdy in uwczd__gptgp:
        yuakp__wmecc = df.data[yex__hqdy]
        if isinstance(yuakp__wmecc, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or yuakp__wmecc == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (uukk__mljhc, fmioc__wmsum, dyfux__fuofa, mznh__kox, hvo__ongpv,
        uwczd__gptgp)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (uukk__mljhc, fmioc__wmsum, dyfux__fuofa, jsmb__ilx, hvo__ongpv,
        qlyr__pzrov) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(uukk__mljhc) == 0:
        if is_overload_none(data.index.name_typ):
            scphu__kdex = None,
        else:
            scphu__kdex = get_literal_value(data.index.name_typ),
    else:
        scphu__kdex = tuple(uukk__mljhc)
    uukk__mljhc = ColNamesMetaType(scphu__kdex)
    dyfux__fuofa = ColNamesMetaType(tuple(dyfux__fuofa))
    fmioc__wmsum = ColNamesMetaType((fmioc__wmsum,))
    vdpc__sjncf = 'def impl(data, index=None, columns=None, values=None):\n'
    vdpc__sjncf += "    ev = tracing.Event('df.pivot')\n"
    vdpc__sjncf += f'    pivot_values = data.iloc[:, {hvo__ongpv}].unique()\n'
    vdpc__sjncf += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(jsmb__ilx) == 0:
        vdpc__sjncf += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        vdpc__sjncf += '        (\n'
        for lcv__qvb in jsmb__ilx:
            vdpc__sjncf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {lcv__qvb}),
"""
        vdpc__sjncf += '        ),\n'
    vdpc__sjncf += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {hvo__ongpv}),),
"""
    vdpc__sjncf += '        (\n'
    for yex__hqdy in qlyr__pzrov:
        vdpc__sjncf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {yex__hqdy}),
"""
    vdpc__sjncf += '        ),\n'
    vdpc__sjncf += '        pivot_values,\n'
    vdpc__sjncf += '        index_lit,\n'
    vdpc__sjncf += '        columns_lit,\n'
    vdpc__sjncf += '        values_lit,\n'
    vdpc__sjncf += '    )\n'
    vdpc__sjncf += '    ev.finalize()\n'
    vdpc__sjncf += '    return result\n'
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'index_lit': uukk__mljhc,
        'columns_lit': fmioc__wmsum, 'values_lit': dyfux__fuofa, 'tracing':
        tracing}, chq__mexn)
    impl = chq__mexn['impl']
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
    vqljc__epoc = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    fsw__fmi = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (uukk__mljhc, fmioc__wmsum, dyfux__fuofa, jsmb__ilx, hvo__ongpv,
        qlyr__pzrov) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    rippa__bwt = uukk__mljhc
    uukk__mljhc = ColNamesMetaType(tuple(uukk__mljhc))
    dyfux__fuofa = ColNamesMetaType(tuple(dyfux__fuofa))
    lloi__gxrp = fmioc__wmsum
    fmioc__wmsum = ColNamesMetaType((fmioc__wmsum,))
    vdpc__sjncf = 'def impl(\n'
    vdpc__sjncf += '    data,\n'
    vdpc__sjncf += '    values=None,\n'
    vdpc__sjncf += '    index=None,\n'
    vdpc__sjncf += '    columns=None,\n'
    vdpc__sjncf += '    aggfunc="mean",\n'
    vdpc__sjncf += '    fill_value=None,\n'
    vdpc__sjncf += '    margins=False,\n'
    vdpc__sjncf += '    dropna=True,\n'
    vdpc__sjncf += '    margins_name="All",\n'
    vdpc__sjncf += '    observed=False,\n'
    vdpc__sjncf += '    sort=True,\n'
    vdpc__sjncf += '    _pivot_values=None,\n'
    vdpc__sjncf += '):\n'
    vdpc__sjncf += "    ev = tracing.Event('df.pivot_table')\n"
    beok__rzh = jsmb__ilx + [hvo__ongpv] + qlyr__pzrov
    vdpc__sjncf += f'    data = data.iloc[:, {beok__rzh}]\n'
    jwdup__wmtr = rippa__bwt + [lloi__gxrp]
    if not is_overload_none(_pivot_values):
        kyt__utj = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(kyt__utj)
        vdpc__sjncf += '    pivot_values = _pivot_values_arr\n'
        vdpc__sjncf += (
            f'    data = data[data.iloc[:, {len(jsmb__ilx)}].isin(pivot_values)]\n'
            )
        if all(isinstance(praqx__osxms, str) for praqx__osxms in kyt__utj):
            llo__qws = pd.array(kyt__utj, 'string')
        elif all(isinstance(praqx__osxms, int) for praqx__osxms in kyt__utj):
            llo__qws = np.array(kyt__utj, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        llo__qws = None
    frps__dsgz = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    rptrb__nnj = len(jwdup__wmtr) if frps__dsgz else len(rippa__bwt)
    vdpc__sjncf += f"""    data = data.groupby({jwdup__wmtr!r}, as_index=False, _bodo_num_shuffle_keys={rptrb__nnj}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        vdpc__sjncf += (
            f'    pivot_values = data.iloc[:, {len(jsmb__ilx)}].unique()\n')
    vdpc__sjncf += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    vdpc__sjncf += '        (\n'
    for i in range(0, len(jsmb__ilx)):
        vdpc__sjncf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    vdpc__sjncf += '        ),\n'
    vdpc__sjncf += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(jsmb__ilx)}),),
"""
    vdpc__sjncf += '        (\n'
    for i in range(len(jsmb__ilx) + 1, len(qlyr__pzrov) + len(jsmb__ilx) + 1):
        vdpc__sjncf += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    vdpc__sjncf += '        ),\n'
    vdpc__sjncf += '        pivot_values,\n'
    vdpc__sjncf += '        index_lit,\n'
    vdpc__sjncf += '        columns_lit,\n'
    vdpc__sjncf += '        values_lit,\n'
    vdpc__sjncf += '        check_duplicates=False,\n'
    vdpc__sjncf += f'        is_already_shuffled={not frps__dsgz},\n'
    vdpc__sjncf += '        _constant_pivot_values=_constant_pivot_values,\n'
    vdpc__sjncf += '    )\n'
    vdpc__sjncf += '    ev.finalize()\n'
    vdpc__sjncf += '    return result\n'
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'numba': numba, 'index_lit':
        uukk__mljhc, 'columns_lit': fmioc__wmsum, 'values_lit':
        dyfux__fuofa, '_pivot_values_arr': llo__qws,
        '_constant_pivot_values': _pivot_values, 'tracing': tracing}, chq__mexn
        )
    impl = chq__mexn['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    vqljc__epoc = dict(col_level=col_level, ignore_index=ignore_index)
    fsw__fmi = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', vqljc__epoc, fsw__fmi,
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
    wsx__wccyk = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(wsx__wccyk, (list, tuple)):
        wsx__wccyk = [wsx__wccyk]
    for praqx__osxms in wsx__wccyk:
        if praqx__osxms not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {praqx__osxms} not found in {frame}."
                )
    hsk__klfj = [frame.column_index[i] for i in wsx__wccyk]
    if is_overload_none(value_vars):
        ywbi__tln = []
        zac__sdvnr = []
        for i, praqx__osxms in enumerate(frame.columns):
            if i not in hsk__klfj:
                ywbi__tln.append(i)
                zac__sdvnr.append(praqx__osxms)
    else:
        zac__sdvnr = get_literal_value(value_vars)
        if not isinstance(zac__sdvnr, (list, tuple)):
            zac__sdvnr = [zac__sdvnr]
        zac__sdvnr = [v for v in zac__sdvnr if v not in wsx__wccyk]
        if not zac__sdvnr:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        ywbi__tln = []
        for val in zac__sdvnr:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            ywbi__tln.append(frame.column_index[val])
    for praqx__osxms in zac__sdvnr:
        if praqx__osxms not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {praqx__osxms} not found in {frame}."
                )
    if not (all(isinstance(praqx__osxms, int) for praqx__osxms in
        zac__sdvnr) or all(isinstance(praqx__osxms, str) for praqx__osxms in
        zac__sdvnr)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    slsx__vxckx = frame.data[ywbi__tln[0]]
    feh__otndu = [frame.data[i].dtype for i in ywbi__tln]
    ywbi__tln = np.array(ywbi__tln, dtype=np.int64)
    hsk__klfj = np.array(hsk__klfj, dtype=np.int64)
    _, fwo__vrby = bodo.utils.typing.get_common_scalar_dtype(feh__otndu)
    if not fwo__vrby:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': zac__sdvnr, 'val_type': slsx__vxckx
        }
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
    if frame.is_table_format and all(v == slsx__vxckx.dtype for v in feh__otndu
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            ywbi__tln))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(zac__sdvnr) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {ywbi__tln[0]})
"""
    else:
        kuts__kdi = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in ywbi__tln)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({kuts__kdi},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in hsk__klfj:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(zac__sdvnr)})\n'
            )
    uptz__kum = ', '.join(f'out_id{i}' for i in hsk__klfj) + (', ' if len(
        hsk__klfj) > 0 else '')
    data_args = uptz__kum + 'var_col, val_col'
    columns = tuple(wsx__wccyk + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(zac__sdvnr)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    vqljc__epoc = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fsw__fmi = dict(values=None, rownames=None, colnames=None, aggfunc=None,
        margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', vqljc__epoc, fsw__fmi,
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
    vqljc__epoc = dict(ignore_index=ignore_index, key=key)
    fsw__fmi = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', vqljc__epoc, fsw__fmi,
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
    lqkh__gzopm = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        lqkh__gzopm.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        vozq__wtbww = [get_overload_const_tuple(by)]
    else:
        vozq__wtbww = get_overload_const_list(by)
    vozq__wtbww = set((k, '') if (k, '') in lqkh__gzopm else k for k in
        vozq__wtbww)
    if len(vozq__wtbww.difference(lqkh__gzopm)) > 0:
        lzdi__ixud = list(set(get_overload_const_list(by)).difference(
            lqkh__gzopm))
        raise_bodo_error(f'sort_values(): invalid keys {lzdi__ixud} for by.')
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
        gkgxl__tuz = get_overload_const_list(na_position)
        for na_position in gkgxl__tuz:
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
    vqljc__epoc = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fsw__fmi = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', vqljc__epoc, fsw__fmi,
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
    vdpc__sjncf = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    odif__uqy = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(odif__uqy))
    for i in range(odif__uqy):
        vdpc__sjncf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(vdpc__sjncf, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    vqljc__epoc = dict(limit=limit, downcast=downcast)
    fsw__fmi = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', vqljc__epoc, fsw__fmi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    tku__qug = not is_overload_none(value)
    uvm__mpku = not is_overload_none(method)
    if tku__qug and uvm__mpku:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not tku__qug and not uvm__mpku:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if tku__qug:
        avdv__sek = 'value=value'
    else:
        avdv__sek = 'method=method'
    data_args = [(
        f"df['{praqx__osxms}'].fillna({avdv__sek}, inplace=inplace)" if
        isinstance(praqx__osxms, str) else
        f'df[{praqx__osxms}].fillna({avdv__sek}, inplace=inplace)') for
        praqx__osxms in df.columns]
    vdpc__sjncf = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        vdpc__sjncf += '  ' + '  \n'.join(data_args) + '\n'
        chq__mexn = {}
        exec(vdpc__sjncf, {}, chq__mexn)
        impl = chq__mexn['impl']
        return impl
    else:
        return _gen_init_df(vdpc__sjncf, df.columns, ', '.join(ztak__izkgz +
            '.values' for ztak__izkgz in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    vqljc__epoc = dict(col_level=col_level, col_fill=col_fill)
    fsw__fmi = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', vqljc__epoc, fsw__fmi,
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
    vdpc__sjncf = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    vdpc__sjncf += (
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
        gdlrc__fvq = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            gdlrc__fvq)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            vdpc__sjncf += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            yfsbs__xskve = ['m_index[{}]'.format(i) for i in range(df.index
                .nlevels)]
            data_args = yfsbs__xskve + data_args
        else:
            yafny__zlef = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [yafny__zlef] + data_args
    return _gen_init_df(vdpc__sjncf, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    arve__nbe = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and arve__nbe == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(arve__nbe))


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
        xihju__hnnx = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        zht__mofb = get_overload_const_list(subset)
        xihju__hnnx = []
        for lxc__hsepe in zht__mofb:
            if lxc__hsepe not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{lxc__hsepe}' not in data frame columns {df}"
                    )
            xihju__hnnx.append(df.column_index[lxc__hsepe])
    odif__uqy = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(odif__uqy))
    vdpc__sjncf = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(odif__uqy):
        vdpc__sjncf += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    vdpc__sjncf += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in xihju__hnnx)))
    vdpc__sjncf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(vdpc__sjncf, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    vqljc__epoc = dict(index=index, level=level, errors=errors)
    fsw__fmi = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', vqljc__epoc, fsw__fmi,
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
            uoy__fbcyt = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            uoy__fbcyt = get_overload_const_list(labels)
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
            uoy__fbcyt = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            uoy__fbcyt = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for praqx__osxms in uoy__fbcyt:
        if praqx__osxms not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(praqx__osxms, df.columns))
    if len(set(uoy__fbcyt)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    rqlnb__myowo = tuple(praqx__osxms for praqx__osxms in df.columns if 
        praqx__osxms not in uoy__fbcyt)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[praqx__osxms], '.copy()' if not inplace else
        '') for praqx__osxms in rqlnb__myowo)
    vdpc__sjncf = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    vdpc__sjncf += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(vdpc__sjncf, rqlnb__myowo, data_args, index)


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
    vqljc__epoc = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    cvwo__benf = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', vqljc__epoc, cvwo__benf,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    odif__uqy = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(odif__uqy))
    gjlyz__qix = ', '.join('rhs_data_{}'.format(i) for i in range(odif__uqy))
    vdpc__sjncf = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    vdpc__sjncf += '  if (frac == 1 or n == len(df)) and not replace:\n'
    vdpc__sjncf += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(odif__uqy):
        vdpc__sjncf += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    vdpc__sjncf += '  if frac is None:\n'
    vdpc__sjncf += '    frac_d = -1.0\n'
    vdpc__sjncf += '  else:\n'
    vdpc__sjncf += '    frac_d = frac\n'
    vdpc__sjncf += '  if n is None:\n'
    vdpc__sjncf += '    n_i = 0\n'
    vdpc__sjncf += '  else:\n'
    vdpc__sjncf += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    vdpc__sjncf += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({gjlyz__qix},), {index}, n_i, frac_d, replace)
"""
    vdpc__sjncf += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(vdpc__sjncf, df.
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
    sctqx__xuwqq = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    baunc__biexz = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', sctqx__xuwqq, baunc__biexz,
        package_name='pandas', module_name='DataFrame')
    knp__hzesy = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            leop__kfbd = knp__hzesy + '\n'
            leop__kfbd += 'Index: 0 entries\n'
            leop__kfbd += 'Empty DataFrame'
            print(leop__kfbd)
        return _info_impl
    else:
        vdpc__sjncf = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        vdpc__sjncf += '    ncols = df.shape[1]\n'
        vdpc__sjncf += f'    lines = "{knp__hzesy}\\n"\n'
        vdpc__sjncf += f'    lines += "{df.index}: "\n'
        vdpc__sjncf += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            vdpc__sjncf += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            vdpc__sjncf += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            vdpc__sjncf += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        vdpc__sjncf += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        vdpc__sjncf += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        vdpc__sjncf += '    column_width = max(space, 7)\n'
        vdpc__sjncf += '    column= "Column"\n'
        vdpc__sjncf += '    underl= "------"\n'
        vdpc__sjncf += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        vdpc__sjncf += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        vdpc__sjncf += '    mem_size = 0\n'
        vdpc__sjncf += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        vdpc__sjncf += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        vdpc__sjncf += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        qur__zhcen = dict()
        for i in range(len(df.columns)):
            vdpc__sjncf += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            rvfg__yqbe = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                rvfg__yqbe = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                nll__ssjq = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                rvfg__yqbe = f'{nll__ssjq[:-7]}'
            vdpc__sjncf += f'    col_dtype[{i}] = "{rvfg__yqbe}"\n'
            if rvfg__yqbe in qur__zhcen:
                qur__zhcen[rvfg__yqbe] += 1
            else:
                qur__zhcen[rvfg__yqbe] = 1
            vdpc__sjncf += f'    col_name[{i}] = "{df.columns[i]}"\n'
            vdpc__sjncf += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        vdpc__sjncf += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        vdpc__sjncf += '    for i in column_info:\n'
        vdpc__sjncf += "        lines += f'{i}\\n'\n"
        hff__qmiy = ', '.join(f'{k}({qur__zhcen[k]})' for k in sorted(
            qur__zhcen))
        vdpc__sjncf += f"    lines += 'dtypes: {hff__qmiy}\\n'\n"
        vdpc__sjncf += '    mem_size += df.index.nbytes\n'
        vdpc__sjncf += '    total_size = _sizeof_fmt(mem_size)\n'
        vdpc__sjncf += "    lines += f'memory usage: {total_size}'\n"
        vdpc__sjncf += '    print(lines)\n'
        chq__mexn = {}
        exec(vdpc__sjncf, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, chq__mexn)
        _info_impl = chq__mexn['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    vdpc__sjncf = 'def impl(df, index=True, deep=False):\n'
    fcyo__bzg = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes'
    lhil__zpuff = is_overload_true(index)
    columns = df.columns
    if lhil__zpuff:
        columns = ('Index',) + columns
    if len(columns) == 0:
        tuct__ufq = ()
    elif all(isinstance(praqx__osxms, int) for praqx__osxms in columns):
        tuct__ufq = np.array(columns, 'int64')
    elif all(isinstance(praqx__osxms, str) for praqx__osxms in columns):
        tuct__ufq = pd.array(columns, 'string')
    else:
        tuct__ufq = columns
    if df.is_table_format and len(df.columns) > 0:
        zjvh__dyq = int(lhil__zpuff)
        bqsh__uga = len(columns)
        vdpc__sjncf += f'  nbytes_arr = np.empty({bqsh__uga}, np.int64)\n'
        vdpc__sjncf += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        vdpc__sjncf += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {zjvh__dyq})
"""
        if lhil__zpuff:
            vdpc__sjncf += f'  nbytes_arr[0] = {fcyo__bzg}\n'
        vdpc__sjncf += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if lhil__zpuff:
            data = f'{fcyo__bzg},{data}'
        else:
            vivh__ccfi = ',' if len(columns) == 1 else ''
            data = f'{data}{vivh__ccfi}'
        vdpc__sjncf += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        tuct__ufq}, chq__mexn)
    impl = chq__mexn['impl']
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
    vbcj__twd = 'read_excel_df{}'.format(next_label())
    setattr(types, vbcj__twd, df_type)
    yfi__ygeek = False
    if is_overload_constant_list(parse_dates):
        yfi__ygeek = get_overload_const_list(parse_dates)
    gkv__irdb = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    vdpc__sjncf = f"""
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
    with numba.objmode(df="{vbcj__twd}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{gkv__irdb}}},
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
            parse_dates={yfi__ygeek},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    chq__mexn = {}
    exec(vdpc__sjncf, globals(), chq__mexn)
    impl = chq__mexn['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as avqc__pavla:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    vdpc__sjncf = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    vdpc__sjncf += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    vdpc__sjncf += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        vdpc__sjncf += '   fig, ax = plt.subplots()\n'
    else:
        vdpc__sjncf += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        vdpc__sjncf += '   fig.set_figwidth(figsize[0])\n'
        vdpc__sjncf += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        vdpc__sjncf += '   xlabel = x\n'
    vdpc__sjncf += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        vdpc__sjncf += '   ylabel = y\n'
    else:
        vdpc__sjncf += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        vdpc__sjncf += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        vdpc__sjncf += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    vdpc__sjncf += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            vdpc__sjncf += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            mzpjn__wljzh = get_overload_const_str(x)
            wmg__phl = df.columns.index(mzpjn__wljzh)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if wmg__phl != i:
                        vdpc__sjncf += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            vdpc__sjncf += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        vdpc__sjncf += '   ax.scatter(df[x], df[y], s=20)\n'
        vdpc__sjncf += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        vdpc__sjncf += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        vdpc__sjncf += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        vdpc__sjncf += '   ax.legend()\n'
    vdpc__sjncf += '   return ax\n'
    chq__mexn = {}
    exec(vdpc__sjncf, {'bodo': bodo, 'plt': plt}, chq__mexn)
    impl = chq__mexn['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for qbes__mxxna in df_typ.data:
        if not (isinstance(qbes__mxxna, IntegerArrayType) or isinstance(
            qbes__mxxna.dtype, types.Number) or qbes__mxxna.dtype in (bodo.
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
        vtg__kbmr = args[0]
        fouj__tdb = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        apzy__ryaq = vtg__kbmr
        check_runtime_cols_unsupported(vtg__kbmr, 'set_df_col()')
        if isinstance(vtg__kbmr, DataFrameType):
            index = vtg__kbmr.index
            if len(vtg__kbmr.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(vtg__kbmr.columns) == 0:
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
            if fouj__tdb in vtg__kbmr.columns:
                rqlnb__myowo = vtg__kbmr.columns
                fmal__mwwhy = vtg__kbmr.columns.index(fouj__tdb)
                dczci__itgeu = list(vtg__kbmr.data)
                dczci__itgeu[fmal__mwwhy] = val
                dczci__itgeu = tuple(dczci__itgeu)
            else:
                rqlnb__myowo = vtg__kbmr.columns + (fouj__tdb,)
                dczci__itgeu = vtg__kbmr.data + (val,)
            apzy__ryaq = DataFrameType(dczci__itgeu, index, rqlnb__myowo,
                vtg__kbmr.dist, vtg__kbmr.is_table_format)
        return apzy__ryaq(*args)


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
        cnadu__joqog = args[0]
        assert isinstance(cnadu__joqog, DataFrameType) and len(cnadu__joqog
            .columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        krw__kgb = args[2]
        assert len(col_names_to_replace) == len(krw__kgb
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(cnadu__joqog.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in cnadu__joqog.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(cnadu__joqog,
            '__bodosql_replace_columns_dummy()')
        index = cnadu__joqog.index
        rqlnb__myowo = cnadu__joqog.columns
        dczci__itgeu = list(cnadu__joqog.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            wlgx__unnvp = krw__kgb[i]
            assert isinstance(wlgx__unnvp, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(wlgx__unnvp, SeriesType):
                wlgx__unnvp = wlgx__unnvp.data
            kgcxk__upfde = cnadu__joqog.column_index[col_name]
            dczci__itgeu[kgcxk__upfde] = wlgx__unnvp
        dczci__itgeu = tuple(dczci__itgeu)
        apzy__ryaq = DataFrameType(dczci__itgeu, index, rqlnb__myowo,
            cnadu__joqog.dist, cnadu__joqog.is_table_format)
        return apzy__ryaq(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    bioa__vpcci = {}

    def _rewrite_membership_op(self, node, left, right):
        gsg__zmrxm = node.op
        op = self.visit(gsg__zmrxm)
        return op, gsg__zmrxm, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    ljdd__glsr = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in ljdd__glsr:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in ljdd__glsr:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        cnxup__qot = node.attr
        value = node.value
        clvf__sycyf = pd.core.computation.ops.LOCAL_TAG
        if cnxup__qot in ('str', 'dt'):
            try:
                vqdrx__awbon = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as fom__fzg:
                col_name = fom__fzg.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            vqdrx__awbon = str(self.visit(value))
        joxky__fzt = vqdrx__awbon, cnxup__qot
        if joxky__fzt in join_cleaned_cols:
            cnxup__qot = join_cleaned_cols[joxky__fzt]
        name = vqdrx__awbon + '.' + cnxup__qot
        if name.startswith(clvf__sycyf):
            name = name[len(clvf__sycyf):]
        if cnxup__qot in ('str', 'dt'):
            mxc__ram = columns[cleaned_columns.index(vqdrx__awbon)]
            bioa__vpcci[mxc__ram] = vqdrx__awbon
            self.env.scope[name] = 0
            return self.term_type(clvf__sycyf + name, self.env)
        ljdd__glsr.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in ljdd__glsr:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        vhr__xxw = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        fouj__tdb = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(vhr__xxw), fouj__tdb))

    def op__str__(self):
        voj__tfq = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            qqc__gnz)) for qqc__gnz in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(voj__tfq)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(voj__tfq)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(voj__tfq))
    lze__had = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    dqud__rnpc = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    pzz__ozg = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    ymbae__znqgl = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    sjro__oydbx = pd.core.computation.ops.Term.__str__
    uat__phywb = pd.core.computation.ops.MathCall.__str__
    uiw__fnjhj = pd.core.computation.ops.Op.__str__
    ibd__daw = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        rzzb__kzxk = pd.core.computation.expr.Expr(expr, env=env)
        psa__rto = str(rzzb__kzxk)
    except pd.core.computation.ops.UndefinedVariableError as fom__fzg:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == fom__fzg.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {fom__fzg}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            lze__had)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            dqud__rnpc)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = pzz__ozg
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = ymbae__znqgl
        pd.core.computation.ops.Term.__str__ = sjro__oydbx
        pd.core.computation.ops.MathCall.__str__ = uat__phywb
        pd.core.computation.ops.Op.__str__ = uiw__fnjhj
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = ibd__daw
    rrk__xzij = pd.core.computation.parsing.clean_column_name
    bioa__vpcci.update({praqx__osxms: rrk__xzij(praqx__osxms) for
        praqx__osxms in columns if rrk__xzij(praqx__osxms) in rzzb__kzxk.names}
        )
    return rzzb__kzxk, psa__rto, bioa__vpcci


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        wmbw__jyq = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(wmbw__jyq))
        ehix__uptl = namedtuple('Pandas', col_names)
        obws__ayfxy = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], ehix__uptl)
        super(DataFrameTupleIterator, self).__init__(name, obws__ayfxy)

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
        fucie__zzoww = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        fucie__zzoww = [types.Array(types.int64, 1, 'C')] + fucie__zzoww
        sqb__dyv = DataFrameTupleIterator(col_names, fucie__zzoww)
        return sqb__dyv(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pphj__yyhx = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            pphj__yyhx)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    hkgjd__nlyg = args[len(args) // 2:]
    oilhk__twko = sig.args[len(sig.args) // 2:]
    qiul__rnpjn = context.make_helper(builder, sig.return_type)
    rbnw__phg = context.get_constant(types.intp, 0)
    kvwq__podh = cgutils.alloca_once_value(builder, rbnw__phg)
    qiul__rnpjn.index = kvwq__podh
    for i, arr in enumerate(hkgjd__nlyg):
        setattr(qiul__rnpjn, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(hkgjd__nlyg, oilhk__twko):
        context.nrt.incref(builder, arr_typ, arr)
    res = qiul__rnpjn._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    mmww__mvmg, = sig.args
    pgii__zoi, = args
    qiul__rnpjn = context.make_helper(builder, mmww__mvmg, value=pgii__zoi)
    txyda__yvcqf = signature(types.intp, mmww__mvmg.array_types[1])
    cij__sqbt = context.compile_internal(builder, lambda a: len(a),
        txyda__yvcqf, [qiul__rnpjn.array0])
    index = builder.load(qiul__rnpjn.index)
    povo__nbvvx = builder.icmp_signed('<', index, cij__sqbt)
    result.set_valid(povo__nbvvx)
    with builder.if_then(povo__nbvvx):
        values = [index]
        for i, arr_typ in enumerate(mmww__mvmg.array_types[1:]):
            tlnkt__dzmz = getattr(qiul__rnpjn, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                ajl__fqu = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    ajl__fqu, [tlnkt__dzmz, index])
            else:
                ajl__fqu = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    ajl__fqu, [tlnkt__dzmz, index])
            values.append(val)
        value = context.make_tuple(builder, mmww__mvmg.yield_type, values)
        result.yield_(value)
        mvsj__dgkd = cgutils.increment_index(builder, index)
        builder.store(mvsj__dgkd, qiul__rnpjn.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    qerb__youc = ir.Assign(rhs, lhs, expr.loc)
    inkfv__sowvo = lhs
    dhl__doe = []
    bybgw__jhiy = []
    ypclo__plo = typ.count
    for i in range(ypclo__plo):
        mpo__utzm = ir.Var(inkfv__sowvo.scope, mk_unique_var('{}_size{}'.
            format(inkfv__sowvo.name, i)), inkfv__sowvo.loc)
        zyh__dfova = ir.Expr.static_getitem(lhs, i, None, inkfv__sowvo.loc)
        self.calltypes[zyh__dfova] = None
        dhl__doe.append(ir.Assign(zyh__dfova, mpo__utzm, inkfv__sowvo.loc))
        self._define(equiv_set, mpo__utzm, types.intp, zyh__dfova)
        bybgw__jhiy.append(mpo__utzm)
    ucx__fbdjo = tuple(bybgw__jhiy)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        ucx__fbdjo, pre=[qerb__youc] + dhl__doe)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
