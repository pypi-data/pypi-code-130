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
    cnkeb__tath = tuple(call_list)
    if cnkeb__tath in no_side_effect_call_tuples:
        return True
    if cnkeb__tath == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(cnkeb__tath) == 1 and tuple in getattr(cnkeb__tath[0], '__mro__', ()
        ):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        ewyd__ulld = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        ewyd__ulld = func.__globals__
    if extra_globals is not None:
        ewyd__ulld.update(extra_globals)
    if add_default_globals:
        ewyd__ulld.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, ewyd__ulld, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[arwsg__iznh.name] for arwsg__iznh in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, ewyd__ulld)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        atwe__sahxn = tuple(typing_info.typemap[arwsg__iznh.name] for
            arwsg__iznh in args)
        lvu__cwwq = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, atwe__sahxn, {}, {}, flags)
        lvu__cwwq.run()
    prt__utms = f_ir.blocks.popitem()[1]
    replace_arg_nodes(prt__utms, args)
    qhsan__izgu = prt__utms.body[:-2]
    update_locs(qhsan__izgu[len(args):], loc)
    for stmt in qhsan__izgu[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        jje__zzy = prt__utms.body[-2]
        assert is_assign(jje__zzy) and is_expr(jje__zzy.value, 'cast')
        iaft__xxey = jje__zzy.value.value
        qhsan__izgu.append(ir.Assign(iaft__xxey, ret_var, loc))
    return qhsan__izgu


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for iip__afu in stmt.list_vars():
            iip__afu.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        vnpy__wfrmq = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        yep__pgfk, rcs__oea = vnpy__wfrmq(stmt)
        return rcs__oea
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        fizx__fzcbp = get_const_value_inner(func_ir, var, arg_types,
            typemap, file_info=file_info)
        if isinstance(fizx__fzcbp, ir.UndefinedType):
            fpmb__dgbkd = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{fpmb__dgbkd}' is not defined", loc=loc)
    except GuardException as okb__okia:
        raise BodoError(err_msg, loc=loc)
    return fizx__fzcbp


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    ojew__tkp = get_definition(func_ir, var)
    cwo__bglsp = None
    if typemap is not None:
        cwo__bglsp = typemap.get(var.name, None)
    if isinstance(ojew__tkp, ir.Arg) and arg_types is not None:
        cwo__bglsp = arg_types[ojew__tkp.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(cwo__bglsp):
        return get_literal_value(cwo__bglsp)
    if isinstance(ojew__tkp, (ir.Const, ir.Global, ir.FreeVar)):
        fizx__fzcbp = ojew__tkp.value
        return fizx__fzcbp
    if literalize_args and isinstance(ojew__tkp, ir.Arg
        ) and can_literalize_type(cwo__bglsp, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({ojew__tkp.index}, loc=var.
            loc, file_infos={ojew__tkp.index: file_info} if file_info is not
            None else None)
    if is_expr(ojew__tkp, 'binop'):
        if file_info and ojew__tkp.fn == operator.add:
            try:
                pcm__tvm = get_const_value_inner(func_ir, ojew__tkp.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(pcm__tvm, True)
                nhvst__anmi = get_const_value_inner(func_ir, ojew__tkp.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return ojew__tkp.fn(pcm__tvm, nhvst__anmi)
            except (GuardException, BodoConstUpdatedError) as okb__okia:
                pass
            try:
                nhvst__anmi = get_const_value_inner(func_ir, ojew__tkp.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(nhvst__anmi, False)
                pcm__tvm = get_const_value_inner(func_ir, ojew__tkp.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return ojew__tkp.fn(pcm__tvm, nhvst__anmi)
            except (GuardException, BodoConstUpdatedError) as okb__okia:
                pass
        pcm__tvm = get_const_value_inner(func_ir, ojew__tkp.lhs, arg_types,
            typemap, updated_containers)
        nhvst__anmi = get_const_value_inner(func_ir, ojew__tkp.rhs,
            arg_types, typemap, updated_containers)
        return ojew__tkp.fn(pcm__tvm, nhvst__anmi)
    if is_expr(ojew__tkp, 'unary'):
        fizx__fzcbp = get_const_value_inner(func_ir, ojew__tkp.value,
            arg_types, typemap, updated_containers)
        return ojew__tkp.fn(fizx__fzcbp)
    if is_expr(ojew__tkp, 'getattr') and typemap:
        oktcg__luvn = typemap.get(ojew__tkp.value.name, None)
        if isinstance(oktcg__luvn, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and ojew__tkp.attr == 'columns':
            return pd.Index(oktcg__luvn.columns)
        if isinstance(oktcg__luvn, types.SliceType):
            iby__wscwt = get_definition(func_ir, ojew__tkp.value)
            require(is_call(iby__wscwt))
            nwy__pya = find_callname(func_ir, iby__wscwt)
            phz__zcg = False
            if nwy__pya == ('_normalize_slice', 'numba.cpython.unicode'):
                require(ojew__tkp.attr in ('start', 'step'))
                iby__wscwt = get_definition(func_ir, iby__wscwt.args[0])
                phz__zcg = True
            require(find_callname(func_ir, iby__wscwt) == ('slice', 'builtins')
                )
            if len(iby__wscwt.args) == 1:
                if ojew__tkp.attr == 'start':
                    return 0
                if ojew__tkp.attr == 'step':
                    return 1
                require(ojew__tkp.attr == 'stop')
                return get_const_value_inner(func_ir, iby__wscwt.args[0],
                    arg_types, typemap, updated_containers)
            if ojew__tkp.attr == 'start':
                fizx__fzcbp = get_const_value_inner(func_ir, iby__wscwt.
                    args[0], arg_types, typemap, updated_containers)
                if fizx__fzcbp is None:
                    fizx__fzcbp = 0
                if phz__zcg:
                    require(fizx__fzcbp == 0)
                return fizx__fzcbp
            if ojew__tkp.attr == 'stop':
                assert not phz__zcg
                return get_const_value_inner(func_ir, iby__wscwt.args[1],
                    arg_types, typemap, updated_containers)
            require(ojew__tkp.attr == 'step')
            if len(iby__wscwt.args) == 2:
                return 1
            else:
                fizx__fzcbp = get_const_value_inner(func_ir, iby__wscwt.
                    args[2], arg_types, typemap, updated_containers)
                if fizx__fzcbp is None:
                    fizx__fzcbp = 1
                if phz__zcg:
                    require(fizx__fzcbp == 1)
                return fizx__fzcbp
    if is_expr(ojew__tkp, 'getattr'):
        return getattr(get_const_value_inner(func_ir, ojew__tkp.value,
            arg_types, typemap, updated_containers), ojew__tkp.attr)
    if is_expr(ojew__tkp, 'getitem'):
        value = get_const_value_inner(func_ir, ojew__tkp.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, ojew__tkp.index, arg_types,
            typemap, updated_containers)
        return value[index]
    ozfsm__drspy = guard(find_callname, func_ir, ojew__tkp, typemap)
    if ozfsm__drspy is not None and len(ozfsm__drspy) == 2 and ozfsm__drspy[0
        ] == 'keys' and isinstance(ozfsm__drspy[1], ir.Var):
        iko__xvwpp = ojew__tkp.func
        ojew__tkp = get_definition(func_ir, ozfsm__drspy[1])
        chr__njby = ozfsm__drspy[1].name
        if updated_containers and chr__njby in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                chr__njby, updated_containers[chr__njby]))
        require(is_expr(ojew__tkp, 'build_map'))
        vals = [iip__afu[0] for iip__afu in ojew__tkp.items]
        hhsw__cxlfl = guard(get_definition, func_ir, iko__xvwpp)
        assert isinstance(hhsw__cxlfl, ir.Expr) and hhsw__cxlfl.attr == 'keys'
        hhsw__cxlfl.attr = 'copy'
        return [get_const_value_inner(func_ir, iip__afu, arg_types, typemap,
            updated_containers) for iip__afu in vals]
    if is_expr(ojew__tkp, 'build_map'):
        return {get_const_value_inner(func_ir, iip__afu[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            iip__afu[1], arg_types, typemap, updated_containers) for
            iip__afu in ojew__tkp.items}
    if is_expr(ojew__tkp, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, iip__afu, arg_types,
            typemap, updated_containers) for iip__afu in ojew__tkp.items)
    if is_expr(ojew__tkp, 'build_list'):
        return [get_const_value_inner(func_ir, iip__afu, arg_types, typemap,
            updated_containers) for iip__afu in ojew__tkp.items]
    if is_expr(ojew__tkp, 'build_set'):
        return {get_const_value_inner(func_ir, iip__afu, arg_types, typemap,
            updated_containers) for iip__afu in ojew__tkp.items}
    if ozfsm__drspy == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if ozfsm__drspy == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('range', 'builtins') and len(ojew__tkp.args) == 1:
        return range(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, iip__afu,
            arg_types, typemap, updated_containers) for iip__afu in
            ojew__tkp.args))
    if ozfsm__drspy == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('format', 'builtins'):
        arwsg__iznh = get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers)
        akfa__ouq = get_const_value_inner(func_ir, ojew__tkp.args[1],
            arg_types, typemap, updated_containers) if len(ojew__tkp.args
            ) > 1 else ''
        return format(arwsg__iznh, akfa__ouq)
    if ozfsm__drspy in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, ojew__tkp.args[
            0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, ojew__tkp.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            ojew__tkp.args[2], arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('len', 'builtins') and typemap and isinstance(typemap
        .get(ojew__tkp.args[0].name, None), types.BaseTuple):
        return len(typemap[ojew__tkp.args[0].name])
    if ozfsm__drspy == ('len', 'builtins'):
        ucff__rigfq = guard(get_definition, func_ir, ojew__tkp.args[0])
        if isinstance(ucff__rigfq, ir.Expr) and ucff__rigfq.op in (
            'build_tuple', 'build_list', 'build_set', 'build_map'):
            return len(ucff__rigfq.items)
        return len(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy == ('CategoricalDtype', 'pandas'):
        kws = dict(ojew__tkp.kws)
        fih__xliwl = get_call_expr_arg('CategoricalDtype', ojew__tkp.args,
            kws, 0, 'categories', '')
        nlkh__lprk = get_call_expr_arg('CategoricalDtype', ojew__tkp.args,
            kws, 1, 'ordered', False)
        if nlkh__lprk is not False:
            nlkh__lprk = get_const_value_inner(func_ir, nlkh__lprk,
                arg_types, typemap, updated_containers)
        if fih__xliwl == '':
            fih__xliwl = None
        else:
            fih__xliwl = get_const_value_inner(func_ir, fih__xliwl,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(fih__xliwl, nlkh__lprk)
    if ozfsm__drspy == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, ojew__tkp.args[0],
            arg_types, typemap, updated_containers))
    if ozfsm__drspy is not None and len(ozfsm__drspy) == 2 and ozfsm__drspy[1
        ] == 'pandas' and ozfsm__drspy[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, ozfsm__drspy[0])()
    if ozfsm__drspy is not None and len(ozfsm__drspy) == 2 and isinstance(
        ozfsm__drspy[1], ir.Var):
        fizx__fzcbp = get_const_value_inner(func_ir, ozfsm__drspy[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, iip__afu, arg_types, typemap,
            updated_containers) for iip__afu in ojew__tkp.args]
        kws = {rhq__cca[0]: get_const_value_inner(func_ir, rhq__cca[1],
            arg_types, typemap, updated_containers) for rhq__cca in
            ojew__tkp.kws}
        return getattr(fizx__fzcbp, ozfsm__drspy[0])(*args, **kws)
    if ozfsm__drspy is not None and len(ozfsm__drspy) == 2 and ozfsm__drspy[1
        ] == 'bodo' and ozfsm__drspy[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, iip__afu, arg_types,
            typemap, updated_containers) for iip__afu in ojew__tkp.args)
        kwargs = {fpmb__dgbkd: get_const_value_inner(func_ir, iip__afu,
            arg_types, typemap, updated_containers) for fpmb__dgbkd,
            iip__afu in dict(ojew__tkp.kws).items()}
        return getattr(bodo, ozfsm__drspy[0])(*args, **kwargs)
    if is_call(ojew__tkp) and typemap and isinstance(typemap.get(ojew__tkp.
        func.name, None), types.Dispatcher):
        py_func = typemap[ojew__tkp.func.name].dispatcher.py_func
        require(ojew__tkp.vararg is None)
        args = tuple(get_const_value_inner(func_ir, iip__afu, arg_types,
            typemap, updated_containers) for iip__afu in ojew__tkp.args)
        kwargs = {fpmb__dgbkd: get_const_value_inner(func_ir, iip__afu,
            arg_types, typemap, updated_containers) for fpmb__dgbkd,
            iip__afu in dict(ojew__tkp.kws).items()}
        arg_types = tuple(bodo.typeof(iip__afu) for iip__afu in args)
        kw_types = {lrvre__nbw: bodo.typeof(iip__afu) for lrvre__nbw,
            iip__afu in kwargs.items()}
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
    f_ir, typemap, umik__czuf, umik__czuf = bodo.compiler.get_func_type_info(
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
                    clodj__kxsd = guard(get_definition, f_ir, rhs.func)
                    if isinstance(clodj__kxsd, ir.Const) and isinstance(
                        clodj__kxsd.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    rrttj__xbmpo = guard(find_callname, f_ir, rhs)
                    if rrttj__xbmpo is None:
                        return False
                    func_name, ynn__aim = rrttj__xbmpo
                    if ynn__aim == 'pandas' and func_name.startswith('read_'):
                        return False
                    if rrttj__xbmpo in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if rrttj__xbmpo == ('File', 'h5py'):
                        return False
                    if isinstance(ynn__aim, ir.Var):
                        cwo__bglsp = typemap[ynn__aim.name]
                        if isinstance(cwo__bglsp, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(cwo__bglsp, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(cwo__bglsp, bodo.LoggingLoggerType):
                            return False
                        if str(cwo__bglsp).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir, ynn__aim
                            ), ir.Arg)):
                            return False
                    if ynn__aim in ('numpy.random', 'time', 'logging',
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
        ktde__qvmm = func.literal_value.code
        xbynt__poy = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            xbynt__poy = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(xbynt__poy, ktde__qvmm)
        fix_struct_return(f_ir)
        typemap, yhg__yety, ewd__krc, umik__czuf = (numba.core.typed_passes
            .type_inference_stage(typing_context, target_context, f_ir,
            arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, ewd__krc, yhg__yety = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, ewd__krc, yhg__yety = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, ewd__krc, yhg__yety = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    if is_udf and isinstance(yhg__yety, types.DictType):
        azpl__ffd = guard(get_struct_keynames, f_ir, typemap)
        if azpl__ffd is not None:
            yhg__yety = StructType((yhg__yety.value_type,) * len(azpl__ffd),
                azpl__ffd)
    if is_udf and isinstance(yhg__yety, (SeriesType, HeterogeneousSeriesType)):
        nbb__lsptb = numba.core.registry.cpu_target.typing_context
        avda__wzj = numba.core.registry.cpu_target.target_context
        nwym__fzpn = bodo.transforms.series_pass.SeriesPass(f_ir,
            nbb__lsptb, avda__wzj, typemap, ewd__krc, {})
        nwym__fzpn.run()
        nwym__fzpn.run()
        nwym__fzpn.run()
        uqz__zpg = compute_cfg_from_blocks(f_ir.blocks)
        yaz__gbwi = [guard(_get_const_series_info, f_ir.blocks[dhl__qzsa],
            f_ir, typemap) for dhl__qzsa in uqz__zpg.exit_points() if
            isinstance(f_ir.blocks[dhl__qzsa].body[-1], ir.Return)]
        if None in yaz__gbwi or len(pd.Series(yaz__gbwi).unique()) != 1:
            yhg__yety.const_info = None
        else:
            yhg__yety.const_info = yaz__gbwi[0]
    return yhg__yety


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    ubbc__kcm = block.body[-1].value
    hip__jvax = get_definition(f_ir, ubbc__kcm)
    require(is_expr(hip__jvax, 'cast'))
    hip__jvax = get_definition(f_ir, hip__jvax.value)
    require(is_call(hip__jvax) and find_callname(f_ir, hip__jvax) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    zzw__gyrn = hip__jvax.args[1]
    cropg__hjief = tuple(get_const_value_inner(f_ir, zzw__gyrn, typemap=
        typemap))
    if isinstance(typemap[ubbc__kcm.name], HeterogeneousSeriesType):
        return len(typemap[ubbc__kcm.name].data), cropg__hjief
    zhes__jpwrz = hip__jvax.args[0]
    ixguz__xbqs = get_definition(f_ir, zhes__jpwrz)
    func_name, yqvwb__een = find_callname(f_ir, ixguz__xbqs)
    if is_call(ixguz__xbqs) and bodo.utils.utils.is_alloc_callname(func_name,
        yqvwb__een):
        imz__zmz = ixguz__xbqs.args[0]
        rdx__etpms = get_const_value_inner(f_ir, imz__zmz, typemap=typemap)
        return rdx__etpms, cropg__hjief
    if is_call(ixguz__xbqs) and find_callname(f_ir, ixguz__xbqs) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        zhes__jpwrz = ixguz__xbqs.args[0]
        ixguz__xbqs = get_definition(f_ir, zhes__jpwrz)
    require(is_expr(ixguz__xbqs, 'build_tuple') or is_expr(ixguz__xbqs,
        'build_list'))
    return len(ixguz__xbqs.items), cropg__hjief


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    myma__lsrd = []
    jzwr__rfvl = []
    values = []
    for lrvre__nbw, iip__afu in build_map.items:
        ioowa__ywfb = find_const(f_ir, lrvre__nbw)
        require(isinstance(ioowa__ywfb, str))
        jzwr__rfvl.append(ioowa__ywfb)
        myma__lsrd.append(lrvre__nbw)
        values.append(iip__afu)
    shzpa__xysky = ir.Var(scope, mk_unique_var('val_tup'), loc)
    tea__vnvdh = ir.Assign(ir.Expr.build_tuple(values, loc), shzpa__xysky, loc)
    f_ir._definitions[shzpa__xysky.name] = [tea__vnvdh.value]
    ebxrf__offw = ir.Var(scope, mk_unique_var('key_tup'), loc)
    xsfm__aqgn = ir.Assign(ir.Expr.build_tuple(myma__lsrd, loc),
        ebxrf__offw, loc)
    f_ir._definitions[ebxrf__offw.name] = [xsfm__aqgn.value]
    if typemap is not None:
        typemap[shzpa__xysky.name] = types.Tuple([typemap[iip__afu.name] for
            iip__afu in values])
        typemap[ebxrf__offw.name] = types.Tuple([typemap[iip__afu.name] for
            iip__afu in myma__lsrd])
    return jzwr__rfvl, shzpa__xysky, tea__vnvdh, ebxrf__offw, xsfm__aqgn


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    opnx__uhqa = block.body[-1].value
    xqqb__zznv = guard(get_definition, f_ir, opnx__uhqa)
    require(is_expr(xqqb__zznv, 'cast'))
    hip__jvax = guard(get_definition, f_ir, xqqb__zznv.value)
    require(is_expr(hip__jvax, 'build_map'))
    require(len(hip__jvax.items) > 0)
    loc = block.loc
    scope = block.scope
    jzwr__rfvl, shzpa__xysky, tea__vnvdh, ebxrf__offw, xsfm__aqgn = (
        extract_keyvals_from_struct_map(f_ir, hip__jvax, loc, scope))
    stszb__xvjhi = ir.Var(scope, mk_unique_var('conv_call'), loc)
    kheny__synug = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), stszb__xvjhi, loc)
    f_ir._definitions[stszb__xvjhi.name] = [kheny__synug.value]
    bnpyq__wiv = ir.Var(scope, mk_unique_var('struct_val'), loc)
    gike__pvle = ir.Assign(ir.Expr.call(stszb__xvjhi, [shzpa__xysky,
        ebxrf__offw], {}, loc), bnpyq__wiv, loc)
    f_ir._definitions[bnpyq__wiv.name] = [gike__pvle.value]
    xqqb__zznv.value = bnpyq__wiv
    hip__jvax.items = [(lrvre__nbw, lrvre__nbw) for lrvre__nbw, umik__czuf in
        hip__jvax.items]
    block.body = block.body[:-2] + [tea__vnvdh, xsfm__aqgn, kheny__synug,
        gike__pvle] + block.body[-2:]
    return tuple(jzwr__rfvl)


def get_struct_keynames(f_ir, typemap):
    uqz__zpg = compute_cfg_from_blocks(f_ir.blocks)
    map__xdzhl = list(uqz__zpg.exit_points())[0]
    block = f_ir.blocks[map__xdzhl]
    require(isinstance(block.body[-1], ir.Return))
    opnx__uhqa = block.body[-1].value
    xqqb__zznv = guard(get_definition, f_ir, opnx__uhqa)
    require(is_expr(xqqb__zznv, 'cast'))
    hip__jvax = guard(get_definition, f_ir, xqqb__zznv.value)
    require(is_call(hip__jvax) and find_callname(f_ir, hip__jvax) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[hip__jvax.args[1].name])


def fix_struct_return(f_ir):
    ilh__asjo = None
    uqz__zpg = compute_cfg_from_blocks(f_ir.blocks)
    for map__xdzhl in uqz__zpg.exit_points():
        ilh__asjo = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            map__xdzhl], map__xdzhl)
    return ilh__asjo


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    jkbd__dtqo = ir.Block(ir.Scope(None, loc), loc)
    jkbd__dtqo.body = node_list
    build_definitions({(0): jkbd__dtqo}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(iip__afu) for iip__afu in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    oksnz__wfcr = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(oksnz__wfcr, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for xpp__kuorm in range(len(vals) - 1, -1, -1):
        iip__afu = vals[xpp__kuorm]
        if isinstance(iip__afu, str) and iip__afu.startswith(
            NESTED_TUP_SENTINEL):
            bquj__cts = int(iip__afu[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:xpp__kuorm]) + (
                tuple(vals[xpp__kuorm + 1:xpp__kuorm + bquj__cts + 1]),) +
                tuple(vals[xpp__kuorm + bquj__cts + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    arwsg__iznh = None
    if len(args) > arg_no and arg_no >= 0:
        arwsg__iznh = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        arwsg__iznh = kws[arg_name]
    if arwsg__iznh is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return arwsg__iznh


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
    ewyd__ulld = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        ewyd__ulld.update(extra_globals)
    func.__globals__.update(ewyd__ulld)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            mlvi__cwcmh = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[mlvi__cwcmh.name] = types.literal(default)
            except:
                pass_info.typemap[mlvi__cwcmh.name] = numba.typeof(default)
            abicm__nvtvf = ir.Assign(ir.Const(default, loc), mlvi__cwcmh, loc)
            pre_nodes.append(abicm__nvtvf)
            return mlvi__cwcmh
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    atwe__sahxn = tuple(pass_info.typemap[iip__afu.name] for iip__afu in args)
    if const:
        bqi__andh = []
        for xpp__kuorm, arwsg__iznh in enumerate(args):
            fizx__fzcbp = guard(find_const, pass_info.func_ir, arwsg__iznh)
            if fizx__fzcbp:
                bqi__andh.append(types.literal(fizx__fzcbp))
            else:
                bqi__andh.append(atwe__sahxn[xpp__kuorm])
        atwe__sahxn = tuple(bqi__andh)
    return ReplaceFunc(func, atwe__sahxn, args, ewyd__ulld,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(tmmx__zfaa) for tmmx__zfaa in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        rzi__dht = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {rzi__dht} = 0\n', (rzi__dht,)
    if isinstance(t, ArrayItemArrayType):
        fjuf__dbfof, nhg__gwmtq = gen_init_varsize_alloc_sizes(t.dtype)
        rzi__dht = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {rzi__dht} = 0\n' + fjuf__dbfof, (rzi__dht,) + nhg__gwmtq
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
        return 1 + sum(get_type_alloc_counts(tmmx__zfaa.dtype) for
            tmmx__zfaa in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(tmmx__zfaa) for tmmx__zfaa in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(tmmx__zfaa) for tmmx__zfaa in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    rego__esjfc = typing_context.resolve_getattr(obj_dtype, func_name)
    if rego__esjfc is None:
        nluko__jheuz = types.misc.Module(np)
        try:
            rego__esjfc = typing_context.resolve_getattr(nluko__jheuz,
                func_name)
        except AttributeError as okb__okia:
            rego__esjfc = None
        if rego__esjfc is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return rego__esjfc


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    rego__esjfc = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(rego__esjfc, types.BoundFunction):
        if axis is not None:
            ksmih__kpub = rego__esjfc.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            ksmih__kpub = rego__esjfc.get_call_type(typing_context, (), {})
        return ksmih__kpub.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(rego__esjfc):
            ksmih__kpub = rego__esjfc.get_call_type(typing_context, (
                obj_dtype,), {})
            return ksmih__kpub.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    rego__esjfc = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(rego__esjfc, types.BoundFunction):
        sxi__dlpiy = rego__esjfc.template
        if axis is not None:
            return sxi__dlpiy._overload_func(obj_dtype, axis=axis)
        else:
            return sxi__dlpiy._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    bffxe__opj = get_definition(func_ir, dict_var)
    require(isinstance(bffxe__opj, ir.Expr))
    require(bffxe__opj.op == 'build_map')
    vxkfq__nvmq = bffxe__opj.items
    myma__lsrd = []
    values = []
    tfjcu__lirb = False
    for xpp__kuorm in range(len(vxkfq__nvmq)):
        cwtwr__jdr, value = vxkfq__nvmq[xpp__kuorm]
        try:
            oiy__qcs = get_const_value_inner(func_ir, cwtwr__jdr, arg_types,
                typemap, updated_containers)
            myma__lsrd.append(oiy__qcs)
            values.append(value)
        except GuardException as okb__okia:
            require_const_map[cwtwr__jdr] = label
            tfjcu__lirb = True
    if tfjcu__lirb:
        raise GuardException
    return myma__lsrd, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        myma__lsrd = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as okb__okia:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in myma__lsrd):
        raise BodoError(err_msg, loc)
    return myma__lsrd


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    myma__lsrd = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    tfirh__qyhd = []
    fprf__xad = [bodo.transforms.typing_pass._create_const_var(lrvre__nbw,
        'dict_key', scope, loc, tfirh__qyhd) for lrvre__nbw in myma__lsrd]
    gkco__dga = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        rfz__sfe = ir.Var(scope, mk_unique_var('sentinel'), loc)
        mgwg__nqwf = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        tfirh__qyhd.append(ir.Assign(ir.Const('__bodo_tup', loc), rfz__sfe,
            loc))
        oth__hcxe = [rfz__sfe] + fprf__xad + gkco__dga
        tfirh__qyhd.append(ir.Assign(ir.Expr.build_tuple(oth__hcxe, loc),
            mgwg__nqwf, loc))
        return (mgwg__nqwf,), tfirh__qyhd
    else:
        nnlrr__qtycb = ir.Var(scope, mk_unique_var('values_tup'), loc)
        imv__dbsfx = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        tfirh__qyhd.append(ir.Assign(ir.Expr.build_tuple(gkco__dga, loc),
            nnlrr__qtycb, loc))
        tfirh__qyhd.append(ir.Assign(ir.Expr.build_tuple(fprf__xad, loc),
            imv__dbsfx, loc))
        return (nnlrr__qtycb, imv__dbsfx), tfirh__qyhd
