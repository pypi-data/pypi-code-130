"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'datetime_date_arr_to_dt64_arr', 'pd_timestamp_ext', 'hiframes', bodo),
    (bodo.libs.bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('rep_return', 'distributed_api',
    'libs', bodo), ('init_dataframe', 'pd_dataframe_ext', 'hiframes', bodo),
    ('get_dataframe_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_all_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_table', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_column_names', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_table_data', 'table', 'hiframes', bodo), ('get_dataframe_index',
    'pd_dataframe_ext', 'hiframes', bodo), ('init_rolling',
    'pd_rolling_ext', 'hiframes', bodo), ('init_groupby', 'pd_groupby_ext',
    'hiframes', bodo), ('calc_nitems', 'array_kernels', 'libs', bodo), (
    'concat', 'array_kernels', 'libs', bodo), ('unique', 'array_kernels',
    'libs', bodo), ('nunique', 'array_kernels', 'libs', bodo), ('quantile',
    'array_kernels', 'libs', bodo), ('explode', 'array_kernels', 'libs',
    bodo), ('explode_no_index', 'array_kernels', 'libs', bodo), (
    'get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('arange', np), (
    'internal_prange', 'parfor', numba), ('internal_prange', 'parfor',
    'parfors', numba), ('empty_inferred', 'ndarray', 'unsafe', numba), (
    '_slice_span', 'unicode', numba), ('_normalize_slice', 'unicode', numba
    ), ('init_session_builder', 'pyspark_ext', 'libs', bodo), (
    'init_session', 'pyspark_ext', 'libs', bodo), ('init_spark_df',
    'pyspark_ext', 'libs', bodo), ('h5size', 'h5_api', 'io', bodo), (
    'pre_alloc_struct_array', 'struct_arr_ext', 'libs', bodo), (bodo.libs.
    struct_arr_ext.pre_alloc_struct_array,), ('pre_alloc_tuple_array',
    'tuple_arr_ext', 'libs', bodo), (bodo.libs.tuple_arr_ext.
    pre_alloc_tuple_array,), ('pre_alloc_array_item_array',
    'array_item_arr_ext', 'libs', bodo), (bodo.libs.array_item_arr_ext.
    pre_alloc_array_item_array,), ('dist_reduce', 'distributed_api', 'libs',
    bodo), (bodo.libs.distributed_api.dist_reduce,), (
    'pre_alloc_string_array', 'str_arr_ext', 'libs', bodo), (bodo.libs.
    str_arr_ext.pre_alloc_string_array,), ('pre_alloc_binary_array',
    'binary_arr_ext', 'libs', bodo), (bodo.libs.binary_arr_ext.
    pre_alloc_binary_array,), ('pre_alloc_map_array', 'map_arr_ext', 'libs',
    bodo), (bodo.libs.map_arr_ext.pre_alloc_map_array,), (
    'convert_dict_arr_to_int', 'dict_arr_ext', 'libs', bodo), (
    'cat_dict_str', 'dict_arr_ext', 'libs', bodo), ('str_replace',
    'dict_arr_ext', 'libs', bodo), ('dict_arr_eq', 'dict_arr_ext', 'libs',
    bodo), ('dict_arr_ne', 'dict_arr_ext', 'libs', bodo), ('str_startswith',
    'dict_arr_ext', 'libs', bodo), ('str_endswith', 'dict_arr_ext', 'libs',
    bodo), ('str_contains_non_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_series_contains_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_capitalize', 'dict_arr_ext', 'libs', bodo), ('str_lower',
    'dict_arr_ext', 'libs', bodo), ('str_swapcase', 'dict_arr_ext', 'libs',
    bodo), ('str_title', 'dict_arr_ext', 'libs', bodo), ('str_upper',
    'dict_arr_ext', 'libs', bodo), ('str_center', 'dict_arr_ext', 'libs',
    bodo), ('str_get', 'dict_arr_ext', 'libs', bodo), ('str_repeat_int',
    'dict_arr_ext', 'libs', bodo), ('str_lstrip', 'dict_arr_ext', 'libs',
    bodo), ('str_rstrip', 'dict_arr_ext', 'libs', bodo), ('str_strip',
    'dict_arr_ext', 'libs', bodo), ('str_zfill', 'dict_arr_ext', 'libs',
    bodo), ('str_ljust', 'dict_arr_ext', 'libs', bodo), ('str_rjust',
    'dict_arr_ext', 'libs', bodo), ('str_find', 'dict_arr_ext', 'libs',
    bodo), ('str_rfind', 'dict_arr_ext', 'libs', bodo), ('str_index',
    'dict_arr_ext', 'libs', bodo), ('str_rindex', 'dict_arr_ext', 'libs',
    bodo), ('str_slice', 'dict_arr_ext', 'libs', bodo), ('str_extract',
    'dict_arr_ext', 'libs', bodo), ('str_extractall', 'dict_arr_ext',
    'libs', bodo), ('str_extractall_multi', 'dict_arr_ext', 'libs', bodo),
    ('str_len', 'dict_arr_ext', 'libs', bodo), ('str_count', 'dict_arr_ext',
    'libs', bodo), ('str_isalnum', 'dict_arr_ext', 'libs', bodo), (
    'str_isalpha', 'dict_arr_ext', 'libs', bodo), ('str_isdigit',
    'dict_arr_ext', 'libs', bodo), ('str_isspace', 'dict_arr_ext', 'libs',
    bodo), ('str_islower', 'dict_arr_ext', 'libs', bodo), ('str_isupper',
    'dict_arr_ext', 'libs', bodo), ('str_istitle', 'dict_arr_ext', 'libs',
    bodo), ('str_isnumeric', 'dict_arr_ext', 'libs', bodo), (
    'str_isdecimal', 'dict_arr_ext', 'libs', bodo), ('str_match',
    'dict_arr_ext', 'libs', bodo), ('prange', bodo), (bodo.prange,), (
    'objmode', bodo), (bodo.objmode,), ('get_label_dict_from_categories',
    'pd_categorial_ext', 'hiframes', bodo), (
    'get_label_dict_from_categories_no_duplicates', 'pd_categorial_ext',
    'hiframes', bodo), ('build_nullable_tuple', 'nullable_tuple_ext',
    'libs', bodo), ('generate_mappable_table_func', 'table_utils', 'utils',
    bodo), ('table_astype', 'table_utils', 'utils', bodo), ('table_concat',
    'table_utils', 'utils', bodo), ('table_filter', 'table', 'hiframes',
    bodo), ('table_subset', 'table', 'hiframes', bodo), (
    'logical_table_to_table', 'table', 'hiframes', bodo), ('startswith',),
    ('endswith',)}


def remove_hiframes(rhs, lives, call_list):
    ecgcc__god = tuple(call_list)
    if ecgcc__god in no_side_effect_call_tuples:
        return True
    if ecgcc__god == (bodo.hiframes.pd_index_ext.init_range_index,):
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if call_list == ['set_table_data_null', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['ensure_column_unboxed', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives and rhs.args[1].name not in lives:
        return True
    if call_list == ['generate_table_nbytes', 'table_utils', 'utils', bodo
        ] and rhs.args[1].name not in lives:
        return True
    if len(ecgcc__god) == 1 and tuple in getattr(ecgcc__god[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        slhxa__wof = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        slhxa__wof = func.__globals__
    if extra_globals is not None:
        slhxa__wof.update(extra_globals)
    if add_default_globals:
        slhxa__wof.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, slhxa__wof, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[ykm__moupn.name] for ykm__moupn in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, slhxa__wof)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        fqpnn__kzyp = tuple(typing_info.typemap[ykm__moupn.name] for
            ykm__moupn in args)
        gnv__nvihk = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, fqpnn__kzyp, {}, {}, flags)
        gnv__nvihk.run()
    qyw__xwvll = f_ir.blocks.popitem()[1]
    replace_arg_nodes(qyw__xwvll, args)
    kge__lguct = qyw__xwvll.body[:-2]
    update_locs(kge__lguct[len(args):], loc)
    for stmt in kge__lguct[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        whi__qugy = qyw__xwvll.body[-2]
        assert is_assign(whi__qugy) and is_expr(whi__qugy.value, 'cast')
        fgklq__xkkus = whi__qugy.value.value
        kge__lguct.append(ir.Assign(fgklq__xkkus, ret_var, loc))
    return kge__lguct


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for usm__fko in stmt.list_vars():
            usm__fko.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        jlzx__zqg = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        qgxbl__anp, vyy__zutar = jlzx__zqg(stmt)
        return vyy__zutar
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        roi__xjik = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(roi__xjik, ir.UndefinedType):
            dfh__ycaq = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{dfh__ycaq}' is not defined", loc=loc)
    except GuardException as fxkx__frgc:
        raise BodoError(err_msg, loc=loc)
    return roi__xjik


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    dptl__wfhp = get_definition(func_ir, var)
    ewls__bkgtd = None
    if typemap is not None:
        ewls__bkgtd = typemap.get(var.name, None)
    if isinstance(dptl__wfhp, ir.Arg) and arg_types is not None:
        ewls__bkgtd = arg_types[dptl__wfhp.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(ewls__bkgtd):
        return get_literal_value(ewls__bkgtd)
    if isinstance(dptl__wfhp, (ir.Const, ir.Global, ir.FreeVar)):
        roi__xjik = dptl__wfhp.value
        return roi__xjik
    if literalize_args and isinstance(dptl__wfhp, ir.Arg
        ) and can_literalize_type(ewls__bkgtd, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({dptl__wfhp.index}, loc=var
            .loc, file_infos={dptl__wfhp.index: file_info} if file_info is not
            None else None)
    if is_expr(dptl__wfhp, 'binop'):
        if file_info and dptl__wfhp.fn == operator.add:
            try:
                mhv__zcddz = get_const_value_inner(func_ir, dptl__wfhp.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(mhv__zcddz, True)
                dkazq__cvgq = get_const_value_inner(func_ir, dptl__wfhp.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return dptl__wfhp.fn(mhv__zcddz, dkazq__cvgq)
            except (GuardException, BodoConstUpdatedError) as fxkx__frgc:
                pass
            try:
                dkazq__cvgq = get_const_value_inner(func_ir, dptl__wfhp.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(dkazq__cvgq, False)
                mhv__zcddz = get_const_value_inner(func_ir, dptl__wfhp.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return dptl__wfhp.fn(mhv__zcddz, dkazq__cvgq)
            except (GuardException, BodoConstUpdatedError) as fxkx__frgc:
                pass
        mhv__zcddz = get_const_value_inner(func_ir, dptl__wfhp.lhs,
            arg_types, typemap, updated_containers)
        dkazq__cvgq = get_const_value_inner(func_ir, dptl__wfhp.rhs,
            arg_types, typemap, updated_containers)
        return dptl__wfhp.fn(mhv__zcddz, dkazq__cvgq)
    if is_expr(dptl__wfhp, 'unary'):
        roi__xjik = get_const_value_inner(func_ir, dptl__wfhp.value,
            arg_types, typemap, updated_containers)
        return dptl__wfhp.fn(roi__xjik)
    if is_expr(dptl__wfhp, 'getattr') and typemap:
        soj__bplq = typemap.get(dptl__wfhp.value.name, None)
        if isinstance(soj__bplq, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and dptl__wfhp.attr == 'columns':
            return pd.Index(soj__bplq.columns)
        if isinstance(soj__bplq, types.SliceType):
            ihbr__fuwb = get_definition(func_ir, dptl__wfhp.value)
            require(is_call(ihbr__fuwb))
            iarp__eyy = find_callname(func_ir, ihbr__fuwb)
            xga__owdcr = False
            if iarp__eyy == ('_normalize_slice', 'numba.cpython.unicode'):
                require(dptl__wfhp.attr in ('start', 'step'))
                ihbr__fuwb = get_definition(func_ir, ihbr__fuwb.args[0])
                xga__owdcr = True
            require(find_callname(func_ir, ihbr__fuwb) == ('slice', 'builtins')
                )
            if len(ihbr__fuwb.args) == 1:
                if dptl__wfhp.attr == 'start':
                    return 0
                if dptl__wfhp.attr == 'step':
                    return 1
                require(dptl__wfhp.attr == 'stop')
                return get_const_value_inner(func_ir, ihbr__fuwb.args[0],
                    arg_types, typemap, updated_containers)
            if dptl__wfhp.attr == 'start':
                roi__xjik = get_const_value_inner(func_ir, ihbr__fuwb.args[
                    0], arg_types, typemap, updated_containers)
                if roi__xjik is None:
                    roi__xjik = 0
                if xga__owdcr:
                    require(roi__xjik == 0)
                return roi__xjik
            if dptl__wfhp.attr == 'stop':
                assert not xga__owdcr
                return get_const_value_inner(func_ir, ihbr__fuwb.args[1],
                    arg_types, typemap, updated_containers)
            require(dptl__wfhp.attr == 'step')
            if len(ihbr__fuwb.args) == 2:
                return 1
            else:
                roi__xjik = get_const_value_inner(func_ir, ihbr__fuwb.args[
                    2], arg_types, typemap, updated_containers)
                if roi__xjik is None:
                    roi__xjik = 1
                if xga__owdcr:
                    require(roi__xjik == 1)
                return roi__xjik
    if is_expr(dptl__wfhp, 'getattr'):
        return getattr(get_const_value_inner(func_ir, dptl__wfhp.value,
            arg_types, typemap, updated_containers), dptl__wfhp.attr)
    if is_expr(dptl__wfhp, 'getitem'):
        value = get_const_value_inner(func_ir, dptl__wfhp.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, dptl__wfhp.index, arg_types,
            typemap, updated_containers)
        return value[index]
    hurj__axx = guard(find_callname, func_ir, dptl__wfhp, typemap)
    if hurj__axx is not None and len(hurj__axx) == 2 and hurj__axx[0
        ] == 'keys' and isinstance(hurj__axx[1], ir.Var):
        ignsi__zcn = dptl__wfhp.func
        dptl__wfhp = get_definition(func_ir, hurj__axx[1])
        clubx__bsux = hurj__axx[1].name
        if updated_containers and clubx__bsux in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                clubx__bsux, updated_containers[clubx__bsux]))
        require(is_expr(dptl__wfhp, 'build_map'))
        vals = [usm__fko[0] for usm__fko in dptl__wfhp.items]
        qscmo__knres = guard(get_definition, func_ir, ignsi__zcn)
        assert isinstance(qscmo__knres, ir.Expr
            ) and qscmo__knres.attr == 'keys'
        qscmo__knres.attr = 'copy'
        return [get_const_value_inner(func_ir, usm__fko, arg_types, typemap,
            updated_containers) for usm__fko in vals]
    if is_expr(dptl__wfhp, 'build_map'):
        return {get_const_value_inner(func_ir, usm__fko[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            usm__fko[1], arg_types, typemap, updated_containers) for
            usm__fko in dptl__wfhp.items}
    if is_expr(dptl__wfhp, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, usm__fko, arg_types,
            typemap, updated_containers) for usm__fko in dptl__wfhp.items)
    if is_expr(dptl__wfhp, 'build_list'):
        return [get_const_value_inner(func_ir, usm__fko, arg_types, typemap,
            updated_containers) for usm__fko in dptl__wfhp.items]
    if is_expr(dptl__wfhp, 'build_set'):
        return {get_const_value_inner(func_ir, usm__fko, arg_types, typemap,
            updated_containers) for usm__fko in dptl__wfhp.items}
    if hurj__axx == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if hurj__axx == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('range', 'builtins') and len(dptl__wfhp.args) == 1:
        return range(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, usm__fko,
            arg_types, typemap, updated_containers) for usm__fko in
            dptl__wfhp.args))
    if hurj__axx == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('format', 'builtins'):
        ykm__moupn = get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers)
        dyr__kwfl = get_const_value_inner(func_ir, dptl__wfhp.args[1],
            arg_types, typemap, updated_containers) if len(dptl__wfhp.args
            ) > 1 else ''
        return format(ykm__moupn, dyr__kwfl)
    if hurj__axx in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, dptl__wfhp.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, dptl__wfhp.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            dptl__wfhp.args[2], arg_types, typemap, updated_containers))
    if hurj__axx == ('len', 'builtins') and typemap and isinstance(typemap.
        get(dptl__wfhp.args[0].name, None), types.BaseTuple):
        return len(typemap[dptl__wfhp.args[0].name])
    if hurj__axx == ('len', 'builtins'):
        nyw__aps = guard(get_definition, func_ir, dptl__wfhp.args[0])
        if isinstance(nyw__aps, ir.Expr) and nyw__aps.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(nyw__aps.items)
        return len(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx == ('CategoricalDtype', 'pandas'):
        kws = dict(dptl__wfhp.kws)
        tqj__copa = get_call_expr_arg('CategoricalDtype', dptl__wfhp.args,
            kws, 0, 'categories', '')
        mley__tglgc = get_call_expr_arg('CategoricalDtype', dptl__wfhp.args,
            kws, 1, 'ordered', False)
        if mley__tglgc is not False:
            mley__tglgc = get_const_value_inner(func_ir, mley__tglgc,
                arg_types, typemap, updated_containers)
        if tqj__copa == '':
            tqj__copa = None
        else:
            tqj__copa = get_const_value_inner(func_ir, tqj__copa, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(tqj__copa, mley__tglgc)
    if hurj__axx == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, dptl__wfhp.args[0],
            arg_types, typemap, updated_containers))
    if hurj__axx is not None and len(hurj__axx) == 2 and hurj__axx[1
        ] == 'pandas' and hurj__axx[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, hurj__axx[0])()
    if hurj__axx is not None and len(hurj__axx) == 2 and isinstance(hurj__axx
        [1], ir.Var):
        roi__xjik = get_const_value_inner(func_ir, hurj__axx[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, usm__fko, arg_types, typemap,
            updated_containers) for usm__fko in dptl__wfhp.args]
        kws = {zbszf__bdd[0]: get_const_value_inner(func_ir, zbszf__bdd[1],
            arg_types, typemap, updated_containers) for zbszf__bdd in
            dptl__wfhp.kws}
        return getattr(roi__xjik, hurj__axx[0])(*args, **kws)
    if hurj__axx is not None and len(hurj__axx) == 2 and hurj__axx[1
        ] == 'bodo' and hurj__axx[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, usm__fko, arg_types,
            typemap, updated_containers) for usm__fko in dptl__wfhp.args)
        kwargs = {dfh__ycaq: get_const_value_inner(func_ir, usm__fko,
            arg_types, typemap, updated_containers) for dfh__ycaq, usm__fko in
            dict(dptl__wfhp.kws).items()}
        return getattr(bodo, hurj__axx[0])(*args, **kwargs)
    if is_call(dptl__wfhp) and typemap and isinstance(typemap.get(
        dptl__wfhp.func.name, None), types.Dispatcher):
        py_func = typemap[dptl__wfhp.func.name].dispatcher.py_func
        require(dptl__wfhp.vararg is None)
        args = tuple(get_const_value_inner(func_ir, usm__fko, arg_types,
            typemap, updated_containers) for usm__fko in dptl__wfhp.args)
        kwargs = {dfh__ycaq: get_const_value_inner(func_ir, usm__fko,
            arg_types, typemap, updated_containers) for dfh__ycaq, usm__fko in
            dict(dptl__wfhp.kws).items()}
        arg_types = tuple(bodo.typeof(usm__fko) for usm__fko in args)
        kw_types = {sjsvy__iglvv: bodo.typeof(usm__fko) for sjsvy__iglvv,
            usm__fko in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, mzvt__oxkqo, mzvt__oxkqo = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    exxyn__syses = guard(get_definition, f_ir, rhs.func)
                    if isinstance(exxyn__syses, ir.Const) and isinstance(
                        exxyn__syses.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    cagqp__nrfl = guard(find_callname, f_ir, rhs)
                    if cagqp__nrfl is None:
                        return False
                    func_name, biq__luyt = cagqp__nrfl
                    if biq__luyt == 'pandas' and func_name.startswith('read_'):
                        return False
                    if cagqp__nrfl in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if cagqp__nrfl == ('File', 'h5py'):
                        return False
                    if isinstance(biq__luyt, ir.Var):
                        ewls__bkgtd = typemap[biq__luyt.name]
                        if isinstance(ewls__bkgtd, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(ewls__bkgtd, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(ewls__bkgtd, bodo.LoggingLoggerType):
                            return False
                        if str(ewls__bkgtd).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            biq__luyt), ir.Arg)):
                            return False
                    if biq__luyt in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        xfooe__vrfii = func.literal_value.code
        dgjy__oaov = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            dgjy__oaov = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(dgjy__oaov, xfooe__vrfii)
        fix_struct_return(f_ir)
        typemap, hgo__acol, got__pjob, mzvt__oxkqo = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, got__pjob, hgo__acol = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, got__pjob, hgo__acol = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, got__pjob, hgo__acol = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    if is_udf and isinstance(hgo__acol, types.DictType):
        ddujm__thg = guard(get_struct_keynames, f_ir, typemap)
        if ddujm__thg is not None:
            hgo__acol = StructType((hgo__acol.value_type,) * len(ddujm__thg
                ), ddujm__thg)
    if is_udf and isinstance(hgo__acol, (SeriesType, HeterogeneousSeriesType)):
        pjoqv__spca = numba.core.registry.cpu_target.typing_context
        tqkx__rxsd = numba.core.registry.cpu_target.target_context
        wtt__qlt = bodo.transforms.series_pass.SeriesPass(f_ir, pjoqv__spca,
            tqkx__rxsd, typemap, got__pjob, {})
        wtt__qlt.run()
        wtt__qlt.run()
        wtt__qlt.run()
        sbs__knr = compute_cfg_from_blocks(f_ir.blocks)
        xao__rjqb = [guard(_get_const_series_info, f_ir.blocks[bgqu__stk],
            f_ir, typemap) for bgqu__stk in sbs__knr.exit_points() if
            isinstance(f_ir.blocks[bgqu__stk].body[-1], ir.Return)]
        if None in xao__rjqb or len(pd.Series(xao__rjqb).unique()) != 1:
            hgo__acol.const_info = None
        else:
            hgo__acol.const_info = xao__rjqb[0]
    return hgo__acol


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    nwxgp__cvm = block.body[-1].value
    kcr__dgah = get_definition(f_ir, nwxgp__cvm)
    require(is_expr(kcr__dgah, 'cast'))
    kcr__dgah = get_definition(f_ir, kcr__dgah.value)
    require(is_call(kcr__dgah) and find_callname(f_ir, kcr__dgah) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    djl__kfq = kcr__dgah.args[1]
    cgvzr__zygy = tuple(get_const_value_inner(f_ir, djl__kfq, typemap=typemap))
    if isinstance(typemap[nwxgp__cvm.name], HeterogeneousSeriesType):
        return len(typemap[nwxgp__cvm.name].data), cgvzr__zygy
    jceic__egz = kcr__dgah.args[0]
    fnqq__pqkvf = get_definition(f_ir, jceic__egz)
    func_name, ejq__cuva = find_callname(f_ir, fnqq__pqkvf)
    if is_call(fnqq__pqkvf) and bodo.utils.utils.is_alloc_callname(func_name,
        ejq__cuva):
        wiepz__ugdwf = fnqq__pqkvf.args[0]
        zdc__ndan = get_const_value_inner(f_ir, wiepz__ugdwf, typemap=typemap)
        return zdc__ndan, cgvzr__zygy
    if is_call(fnqq__pqkvf) and find_callname(f_ir, fnqq__pqkvf) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        jceic__egz = fnqq__pqkvf.args[0]
        fnqq__pqkvf = get_definition(f_ir, jceic__egz)
    require(is_expr(fnqq__pqkvf, 'build_tuple') or is_expr(fnqq__pqkvf,
        'build_list'))
    return len(fnqq__pqkvf.items), cgvzr__zygy


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    vsgf__nzb = []
    beff__kinkw = []
    values = []
    for sjsvy__iglvv, usm__fko in build_map.items:
        ubs__jfm = find_const(f_ir, sjsvy__iglvv)
        require(isinstance(ubs__jfm, str))
        beff__kinkw.append(ubs__jfm)
        vsgf__nzb.append(sjsvy__iglvv)
        values.append(usm__fko)
    dob__aedx = ir.Var(scope, mk_unique_var('val_tup'), loc)
    hioi__iyq = ir.Assign(ir.Expr.build_tuple(values, loc), dob__aedx, loc)
    f_ir._definitions[dob__aedx.name] = [hioi__iyq.value]
    vfz__gyp = ir.Var(scope, mk_unique_var('key_tup'), loc)
    zcbm__tjyv = ir.Assign(ir.Expr.build_tuple(vsgf__nzb, loc), vfz__gyp, loc)
    f_ir._definitions[vfz__gyp.name] = [zcbm__tjyv.value]
    if typemap is not None:
        typemap[dob__aedx.name] = types.Tuple([typemap[usm__fko.name] for
            usm__fko in values])
        typemap[vfz__gyp.name] = types.Tuple([typemap[usm__fko.name] for
            usm__fko in vsgf__nzb])
    return beff__kinkw, dob__aedx, hioi__iyq, vfz__gyp, zcbm__tjyv


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    uux__vzn = block.body[-1].value
    swg__oakvd = guard(get_definition, f_ir, uux__vzn)
    require(is_expr(swg__oakvd, 'cast'))
    kcr__dgah = guard(get_definition, f_ir, swg__oakvd.value)
    require(is_expr(kcr__dgah, 'build_map'))
    require(len(kcr__dgah.items) > 0)
    loc = block.loc
    scope = block.scope
    beff__kinkw, dob__aedx, hioi__iyq, vfz__gyp, zcbm__tjyv = (
        extract_keyvals_from_struct_map(f_ir, kcr__dgah, loc, scope))
    cjvd__yfg = ir.Var(scope, mk_unique_var('conv_call'), loc)
    oqnmt__deya = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), cjvd__yfg, loc)
    f_ir._definitions[cjvd__yfg.name] = [oqnmt__deya.value]
    fmsv__zgplr = ir.Var(scope, mk_unique_var('struct_val'), loc)
    vfvq__xduc = ir.Assign(ir.Expr.call(cjvd__yfg, [dob__aedx, vfz__gyp], {
        }, loc), fmsv__zgplr, loc)
    f_ir._definitions[fmsv__zgplr.name] = [vfvq__xduc.value]
    swg__oakvd.value = fmsv__zgplr
    kcr__dgah.items = [(sjsvy__iglvv, sjsvy__iglvv) for sjsvy__iglvv,
        mzvt__oxkqo in kcr__dgah.items]
    block.body = block.body[:-2] + [hioi__iyq, zcbm__tjyv, oqnmt__deya,
        vfvq__xduc] + block.body[-2:]
    return tuple(beff__kinkw)


def get_struct_keynames(f_ir, typemap):
    sbs__knr = compute_cfg_from_blocks(f_ir.blocks)
    jzif__pkqgp = list(sbs__knr.exit_points())[0]
    block = f_ir.blocks[jzif__pkqgp]
    require(isinstance(block.body[-1], ir.Return))
    uux__vzn = block.body[-1].value
    swg__oakvd = guard(get_definition, f_ir, uux__vzn)
    require(is_expr(swg__oakvd, 'cast'))
    kcr__dgah = guard(get_definition, f_ir, swg__oakvd.value)
    require(is_call(kcr__dgah) and find_callname(f_ir, kcr__dgah) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[kcr__dgah.args[1].name])


def fix_struct_return(f_ir):
    nzfkn__htb = None
    sbs__knr = compute_cfg_from_blocks(f_ir.blocks)
    for jzif__pkqgp in sbs__knr.exit_points():
        nzfkn__htb = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            jzif__pkqgp], jzif__pkqgp)
    return nzfkn__htb


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    shqm__uqc = ir.Block(ir.Scope(None, loc), loc)
    shqm__uqc.body = node_list
    build_definitions({(0): shqm__uqc}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(usm__fko) for usm__fko in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    ked__hgjsr = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(ked__hgjsr, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for tnk__jgd in range(len(vals) - 1, -1, -1):
        usm__fko = vals[tnk__jgd]
        if isinstance(usm__fko, str) and usm__fko.startswith(
            NESTED_TUP_SENTINEL):
            gpk__kgngf = int(usm__fko[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:tnk__jgd]) + (
                tuple(vals[tnk__jgd + 1:tnk__jgd + gpk__kgngf + 1]),) +
                tuple(vals[tnk__jgd + gpk__kgngf + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    ykm__moupn = None
    if len(args) > arg_no and arg_no >= 0:
        ykm__moupn = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        ykm__moupn = kws[arg_name]
    if ykm__moupn is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return ykm__moupn


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    slhxa__wof = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        slhxa__wof.update(extra_globals)
    func.__globals__.update(slhxa__wof)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            zhwkf__lfyi = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[zhwkf__lfyi.name] = types.literal(default)
            except:
                pass_info.typemap[zhwkf__lfyi.name] = numba.typeof(default)
            zskhx__cbsl = ir.Assign(ir.Const(default, loc), zhwkf__lfyi, loc)
            pre_nodes.append(zskhx__cbsl)
            return zhwkf__lfyi
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    fqpnn__kzyp = tuple(pass_info.typemap[usm__fko.name] for usm__fko in args)
    if const:
        atryn__evsc = []
        for tnk__jgd, ykm__moupn in enumerate(args):
            roi__xjik = guard(find_const, pass_info.func_ir, ykm__moupn)
            if roi__xjik:
                atryn__evsc.append(types.literal(roi__xjik))
            else:
                atryn__evsc.append(fqpnn__kzyp[tnk__jgd])
        fqpnn__kzyp = tuple(atryn__evsc)
    return ReplaceFunc(func, fqpnn__kzyp, args, slhxa__wof,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(xbd__uczcy) for xbd__uczcy in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        mxqxj__dcs = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {mxqxj__dcs} = 0\n', (mxqxj__dcs,)
    if isinstance(t, ArrayItemArrayType):
        qmljm__sbl, cptuo__vzhir = gen_init_varsize_alloc_sizes(t.dtype)
        mxqxj__dcs = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {mxqxj__dcs} = 0\n' + qmljm__sbl, (mxqxj__dcs,
            ) + cptuo__vzhir
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(xbd__uczcy.dtype) for
            xbd__uczcy in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(xbd__uczcy) for xbd__uczcy in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(xbd__uczcy) for xbd__uczcy in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    idtt__omytw = typing_context.resolve_getattr(obj_dtype, func_name)
    if idtt__omytw is None:
        vlt__kpwlf = types.misc.Module(np)
        try:
            idtt__omytw = typing_context.resolve_getattr(vlt__kpwlf, func_name)
        except AttributeError as fxkx__frgc:
            idtt__omytw = None
        if idtt__omytw is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return idtt__omytw


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    idtt__omytw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(idtt__omytw, types.BoundFunction):
        if axis is not None:
            krc__khitu = idtt__omytw.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            krc__khitu = idtt__omytw.get_call_type(typing_context, (), {})
        return krc__khitu.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(idtt__omytw):
            krc__khitu = idtt__omytw.get_call_type(typing_context, (
                obj_dtype,), {})
            return krc__khitu.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    idtt__omytw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(idtt__omytw, types.BoundFunction):
        jvt__ottxf = idtt__omytw.template
        if axis is not None:
            return jvt__ottxf._overload_func(obj_dtype, axis=axis)
        else:
            return jvt__ottxf._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    nuxti__jgq = get_definition(func_ir, dict_var)
    require(isinstance(nuxti__jgq, ir.Expr))
    require(nuxti__jgq.op == 'build_map')
    uhuu__clmd = nuxti__jgq.items
    vsgf__nzb = []
    values = []
    wyrgo__yndh = False
    for tnk__jgd in range(len(uhuu__clmd)):
        qdazy__bwi, value = uhuu__clmd[tnk__jgd]
        try:
            ouwy__xhwa = get_const_value_inner(func_ir, qdazy__bwi,
                arg_types, typemap, updated_containers)
            vsgf__nzb.append(ouwy__xhwa)
            values.append(value)
        except GuardException as fxkx__frgc:
            require_const_map[qdazy__bwi] = label
            wyrgo__yndh = True
    if wyrgo__yndh:
        raise GuardException
    return vsgf__nzb, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        vsgf__nzb = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as fxkx__frgc:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in vsgf__nzb):
        raise BodoError(err_msg, loc)
    return vsgf__nzb


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    vsgf__nzb = _get_const_keys_from_dict(args, func_ir, build_map, err_msg,
        loc)
    vtoxb__opg = []
    amp__ygexx = [bodo.transforms.typing_pass._create_const_var(
        sjsvy__iglvv, 'dict_key', scope, loc, vtoxb__opg) for sjsvy__iglvv in
        vsgf__nzb]
    wknl__gjosx = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        mtv__llkaq = ir.Var(scope, mk_unique_var('sentinel'), loc)
        zlya__ogf = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        vtoxb__opg.append(ir.Assign(ir.Const('__bodo_tup', loc), mtv__llkaq,
            loc))
        qlvnf__wjt = [mtv__llkaq] + amp__ygexx + wknl__gjosx
        vtoxb__opg.append(ir.Assign(ir.Expr.build_tuple(qlvnf__wjt, loc),
            zlya__ogf, loc))
        return (zlya__ogf,), vtoxb__opg
    else:
        qdval__hgule = ir.Var(scope, mk_unique_var('values_tup'), loc)
        wae__aqhx = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        vtoxb__opg.append(ir.Assign(ir.Expr.build_tuple(wknl__gjosx, loc),
            qdval__hgule, loc))
        vtoxb__opg.append(ir.Assign(ir.Expr.build_tuple(amp__ygexx, loc),
            wae__aqhx, loc))
        return (qdval__hgule, wae__aqhx), vtoxb__opg
