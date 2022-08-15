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
    sle__yikik = tuple(call_list)
    if sle__yikik in no_side_effect_call_tuples:
        return True
    if sle__yikik == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(sle__yikik) == 1 and tuple in getattr(sle__yikik[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        xbg__ule = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        xbg__ule = func.__globals__
    if extra_globals is not None:
        xbg__ule.update(extra_globals)
    if add_default_globals:
        xbg__ule.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, xbg__ule, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[otp__rizx.name] for otp__rizx in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, xbg__ule)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        jqri__fnep = tuple(typing_info.typemap[otp__rizx.name] for
            otp__rizx in args)
        nowne__rjt = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, jqri__fnep, {}, {}, flags)
        nowne__rjt.run()
    trejk__emahl = f_ir.blocks.popitem()[1]
    replace_arg_nodes(trejk__emahl, args)
    xyu__iuw = trejk__emahl.body[:-2]
    update_locs(xyu__iuw[len(args):], loc)
    for stmt in xyu__iuw[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        sfyb__hmgrl = trejk__emahl.body[-2]
        assert is_assign(sfyb__hmgrl) and is_expr(sfyb__hmgrl.value, 'cast')
        fqoj__lht = sfyb__hmgrl.value.value
        xyu__iuw.append(ir.Assign(fqoj__lht, ret_var, loc))
    return xyu__iuw


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for lsj__bzlj in stmt.list_vars():
            lsj__bzlj.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        tyb__gkr = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        yhbs__cdbp, qplvk__hgyl = tyb__gkr(stmt)
        return qplvk__hgyl
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        aot__nyerp = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(aot__nyerp, ir.UndefinedType):
            zov__roof = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{zov__roof}' is not defined", loc=loc)
    except GuardException as qiyr__bbhjh:
        raise BodoError(err_msg, loc=loc)
    return aot__nyerp


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    vllqs__ivry = get_definition(func_ir, var)
    vcbvm__hzg = None
    if typemap is not None:
        vcbvm__hzg = typemap.get(var.name, None)
    if isinstance(vllqs__ivry, ir.Arg) and arg_types is not None:
        vcbvm__hzg = arg_types[vllqs__ivry.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(vcbvm__hzg):
        return get_literal_value(vcbvm__hzg)
    if isinstance(vllqs__ivry, (ir.Const, ir.Global, ir.FreeVar)):
        aot__nyerp = vllqs__ivry.value
        return aot__nyerp
    if literalize_args and isinstance(vllqs__ivry, ir.Arg
        ) and can_literalize_type(vcbvm__hzg, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({vllqs__ivry.index}, loc=
            var.loc, file_infos={vllqs__ivry.index: file_info} if file_info
             is not None else None)
    if is_expr(vllqs__ivry, 'binop'):
        if file_info and vllqs__ivry.fn == operator.add:
            try:
                rqdf__bccky = get_const_value_inner(func_ir, vllqs__ivry.
                    lhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(rqdf__bccky, True)
                kkap__ixcy = get_const_value_inner(func_ir, vllqs__ivry.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return vllqs__ivry.fn(rqdf__bccky, kkap__ixcy)
            except (GuardException, BodoConstUpdatedError) as qiyr__bbhjh:
                pass
            try:
                kkap__ixcy = get_const_value_inner(func_ir, vllqs__ivry.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(kkap__ixcy, False)
                rqdf__bccky = get_const_value_inner(func_ir, vllqs__ivry.
                    lhs, arg_types, typemap, updated_containers, file_info)
                return vllqs__ivry.fn(rqdf__bccky, kkap__ixcy)
            except (GuardException, BodoConstUpdatedError) as qiyr__bbhjh:
                pass
        rqdf__bccky = get_const_value_inner(func_ir, vllqs__ivry.lhs,
            arg_types, typemap, updated_containers)
        kkap__ixcy = get_const_value_inner(func_ir, vllqs__ivry.rhs,
            arg_types, typemap, updated_containers)
        return vllqs__ivry.fn(rqdf__bccky, kkap__ixcy)
    if is_expr(vllqs__ivry, 'unary'):
        aot__nyerp = get_const_value_inner(func_ir, vllqs__ivry.value,
            arg_types, typemap, updated_containers)
        return vllqs__ivry.fn(aot__nyerp)
    if is_expr(vllqs__ivry, 'getattr') and typemap:
        zrc__nkd = typemap.get(vllqs__ivry.value.name, None)
        if isinstance(zrc__nkd, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and vllqs__ivry.attr == 'columns':
            return pd.Index(zrc__nkd.columns)
        if isinstance(zrc__nkd, types.SliceType):
            rbuic__lygty = get_definition(func_ir, vllqs__ivry.value)
            require(is_call(rbuic__lygty))
            yib__myuq = find_callname(func_ir, rbuic__lygty)
            jpp__ijl = False
            if yib__myuq == ('_normalize_slice', 'numba.cpython.unicode'):
                require(vllqs__ivry.attr in ('start', 'step'))
                rbuic__lygty = get_definition(func_ir, rbuic__lygty.args[0])
                jpp__ijl = True
            require(find_callname(func_ir, rbuic__lygty) == ('slice',
                'builtins'))
            if len(rbuic__lygty.args) == 1:
                if vllqs__ivry.attr == 'start':
                    return 0
                if vllqs__ivry.attr == 'step':
                    return 1
                require(vllqs__ivry.attr == 'stop')
                return get_const_value_inner(func_ir, rbuic__lygty.args[0],
                    arg_types, typemap, updated_containers)
            if vllqs__ivry.attr == 'start':
                aot__nyerp = get_const_value_inner(func_ir, rbuic__lygty.
                    args[0], arg_types, typemap, updated_containers)
                if aot__nyerp is None:
                    aot__nyerp = 0
                if jpp__ijl:
                    require(aot__nyerp == 0)
                return aot__nyerp
            if vllqs__ivry.attr == 'stop':
                assert not jpp__ijl
                return get_const_value_inner(func_ir, rbuic__lygty.args[1],
                    arg_types, typemap, updated_containers)
            require(vllqs__ivry.attr == 'step')
            if len(rbuic__lygty.args) == 2:
                return 1
            else:
                aot__nyerp = get_const_value_inner(func_ir, rbuic__lygty.
                    args[2], arg_types, typemap, updated_containers)
                if aot__nyerp is None:
                    aot__nyerp = 1
                if jpp__ijl:
                    require(aot__nyerp == 1)
                return aot__nyerp
    if is_expr(vllqs__ivry, 'getattr'):
        return getattr(get_const_value_inner(func_ir, vllqs__ivry.value,
            arg_types, typemap, updated_containers), vllqs__ivry.attr)
    if is_expr(vllqs__ivry, 'getitem'):
        value = get_const_value_inner(func_ir, vllqs__ivry.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, vllqs__ivry.index, arg_types,
            typemap, updated_containers)
        return value[index]
    tgrwd__ocrsk = guard(find_callname, func_ir, vllqs__ivry, typemap)
    if tgrwd__ocrsk is not None and len(tgrwd__ocrsk) == 2 and tgrwd__ocrsk[0
        ] == 'keys' and isinstance(tgrwd__ocrsk[1], ir.Var):
        ywvmz__aezxz = vllqs__ivry.func
        vllqs__ivry = get_definition(func_ir, tgrwd__ocrsk[1])
        zbmh__zfhyu = tgrwd__ocrsk[1].name
        if updated_containers and zbmh__zfhyu in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                zbmh__zfhyu, updated_containers[zbmh__zfhyu]))
        require(is_expr(vllqs__ivry, 'build_map'))
        vals = [lsj__bzlj[0] for lsj__bzlj in vllqs__ivry.items]
        edwc__bjger = guard(get_definition, func_ir, ywvmz__aezxz)
        assert isinstance(edwc__bjger, ir.Expr) and edwc__bjger.attr == 'keys'
        edwc__bjger.attr = 'copy'
        return [get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vals]
    if is_expr(vllqs__ivry, 'build_map'):
        return {get_const_value_inner(func_ir, lsj__bzlj[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            lsj__bzlj[1], arg_types, typemap, updated_containers) for
            lsj__bzlj in vllqs__ivry.items}
    if is_expr(vllqs__ivry, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.items)
    if is_expr(vllqs__ivry, 'build_list'):
        return [get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.items]
    if is_expr(vllqs__ivry, 'build_set'):
        return {get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.items}
    if tgrwd__ocrsk == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if tgrwd__ocrsk == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('range', 'builtins') and len(vllqs__ivry.args) == 1:
        return range(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, lsj__bzlj,
            arg_types, typemap, updated_containers) for lsj__bzlj in
            vllqs__ivry.args))
    if tgrwd__ocrsk == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('format', 'builtins'):
        otp__rizx = get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers)
        uhdls__wmu = get_const_value_inner(func_ir, vllqs__ivry.args[1],
            arg_types, typemap, updated_containers) if len(vllqs__ivry.args
            ) > 1 else ''
        return format(otp__rizx, uhdls__wmu)
    if tgrwd__ocrsk in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, vllqs__ivry.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, vllqs__ivry.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            vllqs__ivry.args[2], arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('len', 'builtins') and typemap and isinstance(typemap
        .get(vllqs__ivry.args[0].name, None), types.BaseTuple):
        return len(typemap[vllqs__ivry.args[0].name])
    if tgrwd__ocrsk == ('len', 'builtins'):
        eyf__yhze = guard(get_definition, func_ir, vllqs__ivry.args[0])
        if isinstance(eyf__yhze, ir.Expr) and eyf__yhze.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(eyf__yhze.items)
        return len(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk == ('CategoricalDtype', 'pandas'):
        kws = dict(vllqs__ivry.kws)
        mdj__zyoc = get_call_expr_arg('CategoricalDtype', vllqs__ivry.args,
            kws, 0, 'categories', '')
        ciomw__pdb = get_call_expr_arg('CategoricalDtype', vllqs__ivry.args,
            kws, 1, 'ordered', False)
        if ciomw__pdb is not False:
            ciomw__pdb = get_const_value_inner(func_ir, ciomw__pdb,
                arg_types, typemap, updated_containers)
        if mdj__zyoc == '':
            mdj__zyoc = None
        else:
            mdj__zyoc = get_const_value_inner(func_ir, mdj__zyoc, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(mdj__zyoc, ciomw__pdb)
    if tgrwd__ocrsk == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, vllqs__ivry.args[0],
            arg_types, typemap, updated_containers))
    if tgrwd__ocrsk is not None and len(tgrwd__ocrsk) == 2 and tgrwd__ocrsk[1
        ] == 'pandas' and tgrwd__ocrsk[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, tgrwd__ocrsk[0])()
    if tgrwd__ocrsk is not None and len(tgrwd__ocrsk) == 2 and isinstance(
        tgrwd__ocrsk[1], ir.Var):
        aot__nyerp = get_const_value_inner(func_ir, tgrwd__ocrsk[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.args]
        kws = {zum__kfa[0]: get_const_value_inner(func_ir, zum__kfa[1],
            arg_types, typemap, updated_containers) for zum__kfa in
            vllqs__ivry.kws}
        return getattr(aot__nyerp, tgrwd__ocrsk[0])(*args, **kws)
    if tgrwd__ocrsk is not None and len(tgrwd__ocrsk) == 2 and tgrwd__ocrsk[1
        ] == 'bodo' and tgrwd__ocrsk[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.args)
        kwargs = {zov__roof: get_const_value_inner(func_ir, lsj__bzlj,
            arg_types, typemap, updated_containers) for zov__roof,
            lsj__bzlj in dict(vllqs__ivry.kws).items()}
        return getattr(bodo, tgrwd__ocrsk[0])(*args, **kwargs)
    if is_call(vllqs__ivry) and typemap and isinstance(typemap.get(
        vllqs__ivry.func.name, None), types.Dispatcher):
        py_func = typemap[vllqs__ivry.func.name].dispatcher.py_func
        require(vllqs__ivry.vararg is None)
        args = tuple(get_const_value_inner(func_ir, lsj__bzlj, arg_types,
            typemap, updated_containers) for lsj__bzlj in vllqs__ivry.args)
        kwargs = {zov__roof: get_const_value_inner(func_ir, lsj__bzlj,
            arg_types, typemap, updated_containers) for zov__roof,
            lsj__bzlj in dict(vllqs__ivry.kws).items()}
        arg_types = tuple(bodo.typeof(lsj__bzlj) for lsj__bzlj in args)
        kw_types = {iaf__wnwf: bodo.typeof(lsj__bzlj) for iaf__wnwf,
            lsj__bzlj in kwargs.items()}
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
    f_ir, typemap, frd__llyh, frd__llyh = bodo.compiler.get_func_type_info(
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
                    upyu__rfidk = guard(get_definition, f_ir, rhs.func)
                    if isinstance(upyu__rfidk, ir.Const) and isinstance(
                        upyu__rfidk.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    paw__mvocl = guard(find_callname, f_ir, rhs)
                    if paw__mvocl is None:
                        return False
                    func_name, rvpo__dxz = paw__mvocl
                    if rvpo__dxz == 'pandas' and func_name.startswith('read_'):
                        return False
                    if paw__mvocl in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if paw__mvocl == ('File', 'h5py'):
                        return False
                    if isinstance(rvpo__dxz, ir.Var):
                        vcbvm__hzg = typemap[rvpo__dxz.name]
                        if isinstance(vcbvm__hzg, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(vcbvm__hzg, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(vcbvm__hzg, bodo.LoggingLoggerType):
                            return False
                        if str(vcbvm__hzg).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            rvpo__dxz), ir.Arg)):
                            return False
                    if rvpo__dxz in ('numpy.random', 'time', 'logging',
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
        zozy__fjio = func.literal_value.code
        rhxpj__fpvvg = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            rhxpj__fpvvg = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(rhxpj__fpvvg, zozy__fjio)
        fix_struct_return(f_ir)
        typemap, ygov__cnj, qcw__tbv, frd__llyh = (numba.core.typed_passes.
            type_inference_stage(typing_context, target_context, f_ir,
            arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, qcw__tbv, ygov__cnj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, qcw__tbv, ygov__cnj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, qcw__tbv, ygov__cnj = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    if is_udf and isinstance(ygov__cnj, types.DictType):
        ihn__pyd = guard(get_struct_keynames, f_ir, typemap)
        if ihn__pyd is not None:
            ygov__cnj = StructType((ygov__cnj.value_type,) * len(ihn__pyd),
                ihn__pyd)
    if is_udf and isinstance(ygov__cnj, (SeriesType, HeterogeneousSeriesType)):
        ydjoq__tvlo = numba.core.registry.cpu_target.typing_context
        tflsl__xou = numba.core.registry.cpu_target.target_context
        btxun__nwvf = bodo.transforms.series_pass.SeriesPass(f_ir,
            ydjoq__tvlo, tflsl__xou, typemap, qcw__tbv, {})
        btxun__nwvf.run()
        btxun__nwvf.run()
        btxun__nwvf.run()
        pxmv__xvfuy = compute_cfg_from_blocks(f_ir.blocks)
        uamq__mrrh = [guard(_get_const_series_info, f_ir.blocks[wxu__bnucp],
            f_ir, typemap) for wxu__bnucp in pxmv__xvfuy.exit_points() if
            isinstance(f_ir.blocks[wxu__bnucp].body[-1], ir.Return)]
        if None in uamq__mrrh or len(pd.Series(uamq__mrrh).unique()) != 1:
            ygov__cnj.const_info = None
        else:
            ygov__cnj.const_info = uamq__mrrh[0]
    return ygov__cnj


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    aelqf__eau = block.body[-1].value
    imyn__wvput = get_definition(f_ir, aelqf__eau)
    require(is_expr(imyn__wvput, 'cast'))
    imyn__wvput = get_definition(f_ir, imyn__wvput.value)
    require(is_call(imyn__wvput) and find_callname(f_ir, imyn__wvput) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    viplk__kkduw = imyn__wvput.args[1]
    mpoh__clj = tuple(get_const_value_inner(f_ir, viplk__kkduw, typemap=
        typemap))
    if isinstance(typemap[aelqf__eau.name], HeterogeneousSeriesType):
        return len(typemap[aelqf__eau.name].data), mpoh__clj
    qvd__pxuz = imyn__wvput.args[0]
    jgl__nme = get_definition(f_ir, qvd__pxuz)
    func_name, cwbk__jsgq = find_callname(f_ir, jgl__nme)
    if is_call(jgl__nme) and bodo.utils.utils.is_alloc_callname(func_name,
        cwbk__jsgq):
        hvu__nyfa = jgl__nme.args[0]
        jym__mitx = get_const_value_inner(f_ir, hvu__nyfa, typemap=typemap)
        return jym__mitx, mpoh__clj
    if is_call(jgl__nme) and find_callname(f_ir, jgl__nme) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'), (
        'build_nullable_tuple', 'bodo.libs.nullable_tuple_ext')]:
        qvd__pxuz = jgl__nme.args[0]
        jgl__nme = get_definition(f_ir, qvd__pxuz)
    require(is_expr(jgl__nme, 'build_tuple') or is_expr(jgl__nme, 'build_list')
        )
    return len(jgl__nme.items), mpoh__clj


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    pchn__yfydn = []
    kqryu__rveg = []
    values = []
    for iaf__wnwf, lsj__bzlj in build_map.items:
        vqakd__bpjl = find_const(f_ir, iaf__wnwf)
        require(isinstance(vqakd__bpjl, str))
        kqryu__rveg.append(vqakd__bpjl)
        pchn__yfydn.append(iaf__wnwf)
        values.append(lsj__bzlj)
    bdd__cuvq = ir.Var(scope, mk_unique_var('val_tup'), loc)
    tcyke__qso = ir.Assign(ir.Expr.build_tuple(values, loc), bdd__cuvq, loc)
    f_ir._definitions[bdd__cuvq.name] = [tcyke__qso.value]
    ybdv__xplsy = ir.Var(scope, mk_unique_var('key_tup'), loc)
    fgzbs__hsk = ir.Assign(ir.Expr.build_tuple(pchn__yfydn, loc),
        ybdv__xplsy, loc)
    f_ir._definitions[ybdv__xplsy.name] = [fgzbs__hsk.value]
    if typemap is not None:
        typemap[bdd__cuvq.name] = types.Tuple([typemap[lsj__bzlj.name] for
            lsj__bzlj in values])
        typemap[ybdv__xplsy.name] = types.Tuple([typemap[lsj__bzlj.name] for
            lsj__bzlj in pchn__yfydn])
    return kqryu__rveg, bdd__cuvq, tcyke__qso, ybdv__xplsy, fgzbs__hsk


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    xazl__ipq = block.body[-1].value
    dkaye__sqey = guard(get_definition, f_ir, xazl__ipq)
    require(is_expr(dkaye__sqey, 'cast'))
    imyn__wvput = guard(get_definition, f_ir, dkaye__sqey.value)
    require(is_expr(imyn__wvput, 'build_map'))
    require(len(imyn__wvput.items) > 0)
    loc = block.loc
    scope = block.scope
    kqryu__rveg, bdd__cuvq, tcyke__qso, ybdv__xplsy, fgzbs__hsk = (
        extract_keyvals_from_struct_map(f_ir, imyn__wvput, loc, scope))
    ixrm__gfup = ir.Var(scope, mk_unique_var('conv_call'), loc)
    smvt__fex = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), ixrm__gfup, loc)
    f_ir._definitions[ixrm__gfup.name] = [smvt__fex.value]
    bcvm__dwuv = ir.Var(scope, mk_unique_var('struct_val'), loc)
    mfblt__pkq = ir.Assign(ir.Expr.call(ixrm__gfup, [bdd__cuvq, ybdv__xplsy
        ], {}, loc), bcvm__dwuv, loc)
    f_ir._definitions[bcvm__dwuv.name] = [mfblt__pkq.value]
    dkaye__sqey.value = bcvm__dwuv
    imyn__wvput.items = [(iaf__wnwf, iaf__wnwf) for iaf__wnwf, frd__llyh in
        imyn__wvput.items]
    block.body = block.body[:-2] + [tcyke__qso, fgzbs__hsk, smvt__fex,
        mfblt__pkq] + block.body[-2:]
    return tuple(kqryu__rveg)


def get_struct_keynames(f_ir, typemap):
    pxmv__xvfuy = compute_cfg_from_blocks(f_ir.blocks)
    jmmzz__eti = list(pxmv__xvfuy.exit_points())[0]
    block = f_ir.blocks[jmmzz__eti]
    require(isinstance(block.body[-1], ir.Return))
    xazl__ipq = block.body[-1].value
    dkaye__sqey = guard(get_definition, f_ir, xazl__ipq)
    require(is_expr(dkaye__sqey, 'cast'))
    imyn__wvput = guard(get_definition, f_ir, dkaye__sqey.value)
    require(is_call(imyn__wvput) and find_callname(f_ir, imyn__wvput) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[imyn__wvput.args[1].name])


def fix_struct_return(f_ir):
    nbj__dfz = None
    pxmv__xvfuy = compute_cfg_from_blocks(f_ir.blocks)
    for jmmzz__eti in pxmv__xvfuy.exit_points():
        nbj__dfz = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            jmmzz__eti], jmmzz__eti)
    return nbj__dfz


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    hhws__sbuvw = ir.Block(ir.Scope(None, loc), loc)
    hhws__sbuvw.body = node_list
    build_definitions({(0): hhws__sbuvw}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(lsj__bzlj) for lsj__bzlj in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    fbpn__wws = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(fbpn__wws, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for duh__etmto in range(len(vals) - 1, -1, -1):
        lsj__bzlj = vals[duh__etmto]
        if isinstance(lsj__bzlj, str) and lsj__bzlj.startswith(
            NESTED_TUP_SENTINEL):
            tha__ewje = int(lsj__bzlj[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:duh__etmto]) + (
                tuple(vals[duh__etmto + 1:duh__etmto + tha__ewje + 1]),) +
                tuple(vals[duh__etmto + tha__ewje + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    otp__rizx = None
    if len(args) > arg_no and arg_no >= 0:
        otp__rizx = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        otp__rizx = kws[arg_name]
    if otp__rizx is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return otp__rizx


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
    xbg__ule = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        xbg__ule.update(extra_globals)
    func.__globals__.update(xbg__ule)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            jijhp__aao = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[jijhp__aao.name] = types.literal(default)
            except:
                pass_info.typemap[jijhp__aao.name] = numba.typeof(default)
            pgw__cnrw = ir.Assign(ir.Const(default, loc), jijhp__aao, loc)
            pre_nodes.append(pgw__cnrw)
            return jijhp__aao
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    jqri__fnep = tuple(pass_info.typemap[lsj__bzlj.name] for lsj__bzlj in args)
    if const:
        paszm__ltwp = []
        for duh__etmto, otp__rizx in enumerate(args):
            aot__nyerp = guard(find_const, pass_info.func_ir, otp__rizx)
            if aot__nyerp:
                paszm__ltwp.append(types.literal(aot__nyerp))
            else:
                paszm__ltwp.append(jqri__fnep[duh__etmto])
        jqri__fnep = tuple(paszm__ltwp)
    return ReplaceFunc(func, jqri__fnep, args, xbg__ule, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(ypel__hhock) for ypel__hhock in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        qkui__cxlzt = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {qkui__cxlzt} = 0\n', (qkui__cxlzt,)
    if isinstance(t, ArrayItemArrayType):
        hcxqj__inzx, zgtm__zku = gen_init_varsize_alloc_sizes(t.dtype)
        qkui__cxlzt = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {qkui__cxlzt} = 0\n' + hcxqj__inzx, (qkui__cxlzt,
            ) + zgtm__zku
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
        return 1 + sum(get_type_alloc_counts(ypel__hhock.dtype) for
            ypel__hhock in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(ypel__hhock) for ypel__hhock in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(ypel__hhock) for ypel__hhock in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    rejrp__nvls = typing_context.resolve_getattr(obj_dtype, func_name)
    if rejrp__nvls is None:
        ppwg__dnvi = types.misc.Module(np)
        try:
            rejrp__nvls = typing_context.resolve_getattr(ppwg__dnvi, func_name)
        except AttributeError as qiyr__bbhjh:
            rejrp__nvls = None
        if rejrp__nvls is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return rejrp__nvls


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    rejrp__nvls = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(rejrp__nvls, types.BoundFunction):
        if axis is not None:
            cmg__geugi = rejrp__nvls.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            cmg__geugi = rejrp__nvls.get_call_type(typing_context, (), {})
        return cmg__geugi.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(rejrp__nvls):
            cmg__geugi = rejrp__nvls.get_call_type(typing_context, (
                obj_dtype,), {})
            return cmg__geugi.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    rejrp__nvls = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(rejrp__nvls, types.BoundFunction):
        mpe__boiuo = rejrp__nvls.template
        if axis is not None:
            return mpe__boiuo._overload_func(obj_dtype, axis=axis)
        else:
            return mpe__boiuo._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    thwwr__bizy = get_definition(func_ir, dict_var)
    require(isinstance(thwwr__bizy, ir.Expr))
    require(thwwr__bizy.op == 'build_map')
    lqu__pexjk = thwwr__bizy.items
    pchn__yfydn = []
    values = []
    esuh__wycb = False
    for duh__etmto in range(len(lqu__pexjk)):
        axyr__xwn, value = lqu__pexjk[duh__etmto]
        try:
            pxsg__whp = get_const_value_inner(func_ir, axyr__xwn, arg_types,
                typemap, updated_containers)
            pchn__yfydn.append(pxsg__whp)
            values.append(value)
        except GuardException as qiyr__bbhjh:
            require_const_map[axyr__xwn] = label
            esuh__wycb = True
    if esuh__wycb:
        raise GuardException
    return pchn__yfydn, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        pchn__yfydn = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as qiyr__bbhjh:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in pchn__yfydn):
        raise BodoError(err_msg, loc)
    return pchn__yfydn


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    pchn__yfydn = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    juoey__wewek = []
    zxxrt__xrbdv = [bodo.transforms.typing_pass._create_const_var(iaf__wnwf,
        'dict_key', scope, loc, juoey__wewek) for iaf__wnwf in pchn__yfydn]
    zlks__eolfx = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        zsp__ywsoy = ir.Var(scope, mk_unique_var('sentinel'), loc)
        tekj__lxm = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        juoey__wewek.append(ir.Assign(ir.Const('__bodo_tup', loc),
            zsp__ywsoy, loc))
        kvw__svc = [zsp__ywsoy] + zxxrt__xrbdv + zlks__eolfx
        juoey__wewek.append(ir.Assign(ir.Expr.build_tuple(kvw__svc, loc),
            tekj__lxm, loc))
        return (tekj__lxm,), juoey__wewek
    else:
        emi__lpp = ir.Var(scope, mk_unique_var('values_tup'), loc)
        rxo__lec = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        juoey__wewek.append(ir.Assign(ir.Expr.build_tuple(zlks__eolfx, loc),
            emi__lpp, loc))
        juoey__wewek.append(ir.Assign(ir.Expr.build_tuple(zxxrt__xrbdv, loc
            ), rxo__lec, loc))
        return (emi__lpp, rxo__lec), juoey__wewek
