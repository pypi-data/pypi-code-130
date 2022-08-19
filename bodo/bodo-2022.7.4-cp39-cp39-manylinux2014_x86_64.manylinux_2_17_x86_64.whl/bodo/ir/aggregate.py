"""IR node for the groupby"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, decref_table_array, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, py_data_to_cpp_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, list_cumulative, to_str_arr_if_dict_array, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import gen_getitem, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        qfawn__aojp = func.signature
        if qfawn__aojp == types.none(types.voidptr):
            ebv__xksic = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            rfyc__qvgln = cgutils.get_or_insert_function(builder.module,
                ebv__xksic, sym._literal_value)
            builder.call(rfyc__qvgln, [context.get_constant_null(
                qfawn__aojp.args[0])])
        elif qfawn__aojp == types.none(types.int64, types.voidptr, types.
            voidptr):
            ebv__xksic = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            rfyc__qvgln = cgutils.get_or_insert_function(builder.module,
                ebv__xksic, sym._literal_value)
            builder.call(rfyc__qvgln, [context.get_constant(types.int64, 0),
                context.get_constant_null(qfawn__aojp.args[1]), context.
                get_constant_null(qfawn__aojp.args[2])])
        else:
            ebv__xksic = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            rfyc__qvgln = cgutils.get_or_insert_function(builder.module,
                ebv__xksic, sym._literal_value)
            builder.call(rfyc__qvgln, [context.get_constant_null(
                qfawn__aojp.args[0]), context.get_constant_null(qfawn__aojp
                .args[1]), context.get_constant_null(qfawn__aojp.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'ngroup', 'head', 'transform', 'size',
    'shift', 'sum', 'count', 'nunique', 'median', 'cumsum', 'cumprod',
    'cummin', 'cummax', 'mean', 'min', 'max', 'prod', 'first', 'last',
    'idxmin', 'idxmax', 'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        iqdc__bdm = True
        xnmpd__mqp = 1
        dkf__jyuzg = -1
        if isinstance(rhs, ir.Expr):
            for spk__rze in rhs.kws:
                if func_name in list_cumulative:
                    if spk__rze[0] == 'skipna':
                        iqdc__bdm = guard(find_const, func_ir, spk__rze[1])
                        if not isinstance(iqdc__bdm, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if spk__rze[0] == 'dropna':
                        iqdc__bdm = guard(find_const, func_ir, spk__rze[1])
                        if not isinstance(iqdc__bdm, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            xnmpd__mqp = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', xnmpd__mqp)
            xnmpd__mqp = guard(find_const, func_ir, xnmpd__mqp)
        if func_name == 'head':
            dkf__jyuzg = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(dkf__jyuzg, int):
                dkf__jyuzg = guard(find_const, func_ir, dkf__jyuzg)
            if dkf__jyuzg < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = iqdc__bdm
        func.periods = xnmpd__mqp
        func.head_n = dkf__jyuzg
        if func_name == 'transform':
            kws = dict(rhs.kws)
            fldpf__eqg = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            qwqq__jcb = typemap[fldpf__eqg.name]
            nhjn__rzw = None
            if isinstance(qwqq__jcb, str):
                nhjn__rzw = qwqq__jcb
            elif is_overload_constant_str(qwqq__jcb):
                nhjn__rzw = get_overload_const_str(qwqq__jcb)
            elif bodo.utils.typing.is_builtin_function(qwqq__jcb):
                nhjn__rzw = bodo.utils.typing.get_builtin_function_name(
                    qwqq__jcb)
            if nhjn__rzw not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {nhjn__rzw}')
            func.transform_func = supported_agg_funcs.index(nhjn__rzw)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    fldpf__eqg = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if fldpf__eqg == '':
        qwqq__jcb = types.none
    else:
        qwqq__jcb = typemap[fldpf__eqg.name]
    if is_overload_constant_dict(qwqq__jcb):
        xtzyn__ero = get_overload_constant_dict(qwqq__jcb)
        jrn__nkdx = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in xtzyn__ero.values()]
        return jrn__nkdx
    if qwqq__jcb == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(qwqq__jcb, types.BaseTuple) or is_overload_constant_list(
        qwqq__jcb):
        jrn__nkdx = []
        nazq__oyxsb = 0
        if is_overload_constant_list(qwqq__jcb):
            wbnd__sem = get_overload_const_list(qwqq__jcb)
        else:
            wbnd__sem = qwqq__jcb.types
        for t in wbnd__sem:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                jrn__nkdx.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(wbnd__sem) > 1:
                    func.fname = '<lambda_' + str(nazq__oyxsb) + '>'
                    nazq__oyxsb += 1
                jrn__nkdx.append(func)
        return [jrn__nkdx]
    if is_overload_constant_str(qwqq__jcb):
        func_name = get_overload_const_str(qwqq__jcb)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(qwqq__jcb):
        func_name = bodo.utils.typing.get_builtin_function_name(qwqq__jcb)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        nazq__oyxsb = 0
        cqpb__cavab = []
        for vadq__voibo in f_val:
            func = get_agg_func_udf(func_ir, vadq__voibo, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{nazq__oyxsb}>'
                nazq__oyxsb += 1
            cqpb__cavab.append(func)
        return cqpb__cavab
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    nhjn__rzw = code.co_name
    return nhjn__rzw


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            vbdpc__fnk = types.DType(args[0])
            return signature(vbdpc__fnk, *args)


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_vars, in_vars, in_key_inds, df_in_type, out_type,
        input_has_index, same_index, return_key, loc, func_name, dropna,
        _num_shuffle_keys):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_vars = out_vars
        self.in_vars = in_vars
        self.in_key_inds = in_key_inds
        self.df_in_type = df_in_type
        self.out_type = out_type
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self._num_shuffle_keys = _num_shuffle_keys
        self.dead_in_inds = set()
        self.dead_out_inds = set()

    def get_live_in_vars(self):
        return [kztw__eljye for kztw__eljye in self.in_vars if kztw__eljye
             is not None]

    def get_live_out_vars(self):
        return [kztw__eljye for kztw__eljye in self.out_vars if kztw__eljye
             is not None]

    @property
    def is_in_table_format(self):
        return self.df_in_type.is_table_format

    @property
    def n_in_table_arrays(self):
        return len(self.df_in_type.columns
            ) if self.df_in_type.is_table_format else 1

    @property
    def n_in_cols(self):
        return self.n_in_table_arrays + len(self.in_vars) - 1

    @property
    def in_col_types(self):
        return list(self.df_in_type.data) + list(get_index_data_arr_types(
            self.df_in_type.index))

    @property
    def is_output_table(self):
        return not isinstance(self.out_type, SeriesType)

    @property
    def n_out_table_arrays(self):
        return len(self.out_type.table_type.arr_types) if not isinstance(self
            .out_type, SeriesType) else 1

    @property
    def n_out_cols(self):
        return self.n_out_table_arrays + len(self.out_vars) - 1

    @property
    def out_col_types(self):
        hami__cyxej = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        xgbng__rpaju = list(get_index_data_arr_types(self.out_type.index))
        return hami__cyxej + xgbng__rpaju

    def update_dead_col_info(self):
        for jrri__cat in self.dead_out_inds:
            self.gb_info_out.pop(jrri__cat, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for aqqb__ugosf, vfzfm__ucmu in self.gb_info_in.copy().items():
            qzna__dqfw = []
            for vadq__voibo, uakm__lhu in vfzfm__ucmu:
                if uakm__lhu not in self.dead_out_inds:
                    qzna__dqfw.append((vadq__voibo, uakm__lhu))
            if not qzna__dqfw:
                if (aqqb__ugosf is not None and aqqb__ugosf not in self.
                    in_key_inds):
                    self.dead_in_inds.add(aqqb__ugosf)
                self.gb_info_in.pop(aqqb__ugosf)
            else:
                self.gb_info_in[aqqb__ugosf] = qzna__dqfw
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for ffil__yim in range(1, len(self.in_vars)):
                jrri__cat = self.n_in_table_arrays + ffil__yim - 1
                if jrri__cat in self.dead_in_inds:
                    self.in_vars[ffil__yim] = None
        else:
            for ffil__yim in range(len(self.in_vars)):
                if ffil__yim in self.dead_in_inds:
                    self.in_vars[ffil__yim] = None

    def __repr__(self):
        wnj__qnwet = ', '.join(kztw__eljye.name for kztw__eljye in self.
            get_live_in_vars())
        agtvk__sihmg = f'{self.df_in}{{{wnj__qnwet}}}'
        irq__owojs = ', '.join(kztw__eljye.name for kztw__eljye in self.
            get_live_out_vars())
        pgqc__lsw = f'{self.df_out}{{{irq__owojs}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {agtvk__sihmg} {pgqc__lsw}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({kztw__eljye.name for kztw__eljye in aggregate_node.
        get_live_in_vars()})
    def_set.update({kztw__eljye.name for kztw__eljye in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    zvdt__uoi = agg_node.out_vars[0]
    if zvdt__uoi is not None and zvdt__uoi.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            fmh__jji = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(fmh__jji)
        else:
            agg_node.dead_out_inds.add(0)
    for ffil__yim in range(1, len(agg_node.out_vars)):
        kztw__eljye = agg_node.out_vars[ffil__yim]
        if kztw__eljye is not None and kztw__eljye.name not in lives:
            agg_node.out_vars[ffil__yim] = None
            jrri__cat = agg_node.n_out_table_arrays + ffil__yim - 1
            agg_node.dead_out_inds.add(jrri__cat)
    if all(kztw__eljye is None for kztw__eljye in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    fku__ssq = {kztw__eljye.name for kztw__eljye in aggregate_node.
        get_live_out_vars()}
    return set(), fku__ssq


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for ffil__yim in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[ffil__yim] is not None:
            aggregate_node.in_vars[ffil__yim] = replace_vars_inner(
                aggregate_node.in_vars[ffil__yim], var_dict)
    for ffil__yim in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[ffil__yim] is not None:
            aggregate_node.out_vars[ffil__yim] = replace_vars_inner(
                aggregate_node.out_vars[ffil__yim], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for ffil__yim in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[ffil__yim] is not None:
            aggregate_node.in_vars[ffil__yim] = visit_vars_inner(aggregate_node
                .in_vars[ffil__yim], callback, cbdata)
    for ffil__yim in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[ffil__yim] is not None:
            aggregate_node.out_vars[ffil__yim] = visit_vars_inner(
                aggregate_node.out_vars[ffil__yim], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    juy__lcx = []
    for zsxvw__bmuux in aggregate_node.get_live_in_vars():
        veuol__dzts = equiv_set.get_shape(zsxvw__bmuux)
        if veuol__dzts is not None:
            juy__lcx.append(veuol__dzts[0])
    if len(juy__lcx) > 1:
        equiv_set.insert_equiv(*juy__lcx)
    pgv__gzrw = []
    juy__lcx = []
    for zsxvw__bmuux in aggregate_node.get_live_out_vars():
        ecymt__ypgde = typemap[zsxvw__bmuux.name]
        phuk__tms = array_analysis._gen_shape_call(equiv_set, zsxvw__bmuux,
            ecymt__ypgde.ndim, None, pgv__gzrw)
        equiv_set.insert_equiv(zsxvw__bmuux, phuk__tms)
        juy__lcx.append(phuk__tms[0])
        equiv_set.define(zsxvw__bmuux, set())
    if len(juy__lcx) > 1:
        equiv_set.insert_equiv(*juy__lcx)
    return [], pgv__gzrw


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    gjuky__rzrqg = aggregate_node.get_live_in_vars()
    sss__lms = aggregate_node.get_live_out_vars()
    kdyf__dtash = Distribution.OneD
    for zsxvw__bmuux in gjuky__rzrqg:
        kdyf__dtash = Distribution(min(kdyf__dtash.value, array_dists[
            zsxvw__bmuux.name].value))
    sjvfb__fnpad = Distribution(min(kdyf__dtash.value, Distribution.
        OneD_Var.value))
    for zsxvw__bmuux in sss__lms:
        if zsxvw__bmuux.name in array_dists:
            sjvfb__fnpad = Distribution(min(sjvfb__fnpad.value, array_dists
                [zsxvw__bmuux.name].value))
    if sjvfb__fnpad != Distribution.OneD_Var:
        kdyf__dtash = sjvfb__fnpad
    for zsxvw__bmuux in gjuky__rzrqg:
        array_dists[zsxvw__bmuux.name] = kdyf__dtash
    for zsxvw__bmuux in sss__lms:
        array_dists[zsxvw__bmuux.name] = sjvfb__fnpad


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for zsxvw__bmuux in agg_node.get_live_out_vars():
        definitions[zsxvw__bmuux.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    jpeok__mlsv = agg_node.get_live_in_vars()
    cvc__zugvq = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for kztw__eljye in (jpeok__mlsv + cvc__zugvq):
            if array_dists[kztw__eljye.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                kztw__eljye.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    jrn__nkdx = []
    func_out_types = []
    for uakm__lhu, (aqqb__ugosf, func) in agg_node.gb_info_out.items():
        if aqqb__ugosf is not None:
            t = agg_node.in_col_types[aqqb__ugosf]
            in_col_typs.append(t)
        jrn__nkdx.append(func)
        func_out_types.append(out_col_typs[uakm__lhu])
    ywu__pnn = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for ffil__yim, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            ywu__pnn.update({f'in_cat_dtype_{ffil__yim}': in_col_typ})
    for ffil__yim, kxscu__jgtxy in enumerate(out_col_typs):
        if isinstance(kxscu__jgtxy, bodo.CategoricalArrayType):
            ywu__pnn.update({f'out_cat_dtype_{ffil__yim}': kxscu__jgtxy})
    udf_func_struct = get_udf_func_struct(jrn__nkdx, in_col_typs, typingctx,
        targetctx)
    out_var_types = [(typemap[kztw__eljye.name] if kztw__eljye is not None else
        types.none) for kztw__eljye in agg_node.out_vars]
    ummt__ewq, pxpk__tjfbq = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    ywu__pnn.update(pxpk__tjfbq)
    ywu__pnn.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'decref_table_array': decref_table_array, 'decode_if_dict_array':
        decode_if_dict_array, 'set_table_data': bodo.hiframes.table.
        set_table_data, 'get_table_data': bodo.hiframes.table.
        get_table_data, 'out_typs': out_col_typs})
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            ywu__pnn.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            ywu__pnn.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    eyjvz__ezq = {}
    exec(ummt__ewq, {}, eyjvz__ezq)
    wjtia__vslb = eyjvz__ezq['agg_top']
    laop__mlgqx = compile_to_numba_ir(wjtia__vslb, ywu__pnn, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[kztw__eljye.
        name] for kztw__eljye in jpeok__mlsv), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(laop__mlgqx, jpeok__mlsv)
    lkmh__rij = laop__mlgqx.body[-2].value.value
    iicjx__kcjn = laop__mlgqx.body[:-2]
    for ffil__yim, kztw__eljye in enumerate(cvc__zugvq):
        gen_getitem(kztw__eljye, lkmh__rij, ffil__yim, calltypes, iicjx__kcjn)
    return iicjx__kcjn


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        jxi__wms = IntDtype(t.dtype).name
        assert jxi__wms.endswith('Dtype()')
        jxi__wms = jxi__wms[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{jxi__wms}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif t == bodo.dict_str_arr_type:
        return (
            'bodo.libs.dict_arr_ext.init_dict_arr(pre_alloc_string_array(1, 1), bodo.libs.int_arr_ext.alloc_int_array(1, np.int32), False)'
            )
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        mahm__ofi = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {mahm__ofi}_cat_dtype_{colnum})')
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    do_combine, func_idx_to_in_col, label_suffix):
    ctwi__baurl = udf_func_struct.var_typs
    xhbih__lgdn = len(ctwi__baurl)
    ummt__ewq = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    ummt__ewq += '    if is_null_pointer(in_table):\n'
    ummt__ewq += '        return\n'
    ummt__ewq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ctwi__baurl]), 
        ',' if len(ctwi__baurl) == 1 else '')
    pcn__kalc = n_keys
    riss__dqz = []
    redvar_offsets = []
    aob__qzism = []
    if do_combine:
        for ffil__yim, vadq__voibo in enumerate(allfuncs):
            if vadq__voibo.ftype != 'udf':
                pcn__kalc += vadq__voibo.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(pcn__kalc, pcn__kalc +
                    vadq__voibo.n_redvars))
                pcn__kalc += vadq__voibo.n_redvars
                aob__qzism.append(data_in_typs_[func_idx_to_in_col[ffil__yim]])
                riss__dqz.append(func_idx_to_in_col[ffil__yim] + n_keys)
    else:
        for ffil__yim, vadq__voibo in enumerate(allfuncs):
            if vadq__voibo.ftype != 'udf':
                pcn__kalc += vadq__voibo.ncols_post_shuffle
            else:
                redvar_offsets += list(range(pcn__kalc + 1, pcn__kalc + 1 +
                    vadq__voibo.n_redvars))
                pcn__kalc += vadq__voibo.n_redvars + 1
                aob__qzism.append(data_in_typs_[func_idx_to_in_col[ffil__yim]])
                riss__dqz.append(func_idx_to_in_col[ffil__yim] + n_keys)
    assert len(redvar_offsets) == xhbih__lgdn
    qljjs__ilu = len(aob__qzism)
    jqb__vxfq = []
    for ffil__yim, t in enumerate(aob__qzism):
        jqb__vxfq.append(_gen_dummy_alloc(t, ffil__yim, True))
    ummt__ewq += '    data_in_dummy = ({}{})\n'.format(','.join(jqb__vxfq),
        ',' if len(aob__qzism) == 1 else '')
    ummt__ewq += """
    # initialize redvar cols
"""
    ummt__ewq += '    init_vals = __init_func()\n'
    for ffil__yim in range(xhbih__lgdn):
        ummt__ewq += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(ffil__yim, redvar_offsets[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(redvar_arr_{})\n'.format(ffil__yim)
        ummt__ewq += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(ffil__yim
            , ffil__yim)
    ummt__ewq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(ffil__yim) for ffil__yim in range(xhbih__lgdn)]), ',' if 
        xhbih__lgdn == 1 else '')
    ummt__ewq += '\n'
    for ffil__yim in range(qljjs__ilu):
        ummt__ewq += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(ffil__yim, riss__dqz[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(data_in_{})\n'.format(ffil__yim)
    ummt__ewq += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(ffil__yim) for ffil__yim in range(qljjs__ilu)]), ',' if 
        qljjs__ilu == 1 else '')
    ummt__ewq += '\n'
    ummt__ewq += '    for i in range(len(data_in_0)):\n'
    ummt__ewq += '        w_ind = row_to_group[i]\n'
    ummt__ewq += '        if w_ind != -1:\n'
    ummt__ewq += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    eyjvz__ezq = {}
    exec(ummt__ewq, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, eyjvz__ezq)
    return eyjvz__ezq['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    ctwi__baurl = udf_func_struct.var_typs
    xhbih__lgdn = len(ctwi__baurl)
    ummt__ewq = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    ummt__ewq += '    if is_null_pointer(in_table):\n'
    ummt__ewq += '        return\n'
    ummt__ewq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ctwi__baurl]), 
        ',' if len(ctwi__baurl) == 1 else '')
    vvui__gciuo = n_keys
    bsln__fxjde = n_keys
    iqos__svqiz = []
    yjaoh__ufq = []
    for vadq__voibo in allfuncs:
        if vadq__voibo.ftype != 'udf':
            vvui__gciuo += vadq__voibo.ncols_pre_shuffle
            bsln__fxjde += vadq__voibo.ncols_post_shuffle
        else:
            iqos__svqiz += list(range(vvui__gciuo, vvui__gciuo +
                vadq__voibo.n_redvars))
            yjaoh__ufq += list(range(bsln__fxjde + 1, bsln__fxjde + 1 +
                vadq__voibo.n_redvars))
            vvui__gciuo += vadq__voibo.n_redvars
            bsln__fxjde += 1 + vadq__voibo.n_redvars
    assert len(iqos__svqiz) == xhbih__lgdn
    ummt__ewq += """
    # initialize redvar cols
"""
    ummt__ewq += '    init_vals = __init_func()\n'
    for ffil__yim in range(xhbih__lgdn):
        ummt__ewq += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(ffil__yim, yjaoh__ufq[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(redvar_arr_{})\n'.format(ffil__yim)
        ummt__ewq += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(ffil__yim
            , ffil__yim)
    ummt__ewq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(ffil__yim) for ffil__yim in range(xhbih__lgdn)]), ',' if 
        xhbih__lgdn == 1 else '')
    ummt__ewq += '\n'
    for ffil__yim in range(xhbih__lgdn):
        ummt__ewq += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(ffil__yim, iqos__svqiz[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(recv_redvar_arr_{})\n'.format(ffil__yim)
    ummt__ewq += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(ffil__yim) for ffil__yim in range(
        xhbih__lgdn)]), ',' if xhbih__lgdn == 1 else '')
    ummt__ewq += '\n'
    if xhbih__lgdn:
        ummt__ewq += '    for i in range(len(recv_redvar_arr_0)):\n'
        ummt__ewq += '        w_ind = row_to_group[i]\n'
        ummt__ewq += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    eyjvz__ezq = {}
    exec(ummt__ewq, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, eyjvz__ezq)
    return eyjvz__ezq['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    ctwi__baurl = udf_func_struct.var_typs
    xhbih__lgdn = len(ctwi__baurl)
    pcn__kalc = n_keys
    redvar_offsets = []
    xmpfk__vdxax = []
    qhz__mozke = []
    for ffil__yim, vadq__voibo in enumerate(allfuncs):
        if vadq__voibo.ftype != 'udf':
            pcn__kalc += vadq__voibo.ncols_post_shuffle
        else:
            xmpfk__vdxax.append(pcn__kalc)
            redvar_offsets += list(range(pcn__kalc + 1, pcn__kalc + 1 +
                vadq__voibo.n_redvars))
            pcn__kalc += 1 + vadq__voibo.n_redvars
            qhz__mozke.append(out_data_typs_[ffil__yim])
    assert len(redvar_offsets) == xhbih__lgdn
    qljjs__ilu = len(qhz__mozke)
    ummt__ewq = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    ummt__ewq += '    if is_null_pointer(table):\n'
    ummt__ewq += '        return\n'
    ummt__ewq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ctwi__baurl]), 
        ',' if len(ctwi__baurl) == 1 else '')
    ummt__ewq += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        qhz__mozke]), ',' if len(qhz__mozke) == 1 else '')
    for ffil__yim in range(xhbih__lgdn):
        ummt__ewq += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(ffil__yim, redvar_offsets[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(redvar_arr_{})\n'.format(ffil__yim)
    ummt__ewq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(ffil__yim) for ffil__yim in range(xhbih__lgdn)]), ',' if 
        xhbih__lgdn == 1 else '')
    ummt__ewq += '\n'
    for ffil__yim in range(qljjs__ilu):
        ummt__ewq += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(ffil__yim, xmpfk__vdxax[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(data_out_{})\n'.format(ffil__yim)
    ummt__ewq += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(ffil__yim) for ffil__yim in range(qljjs__ilu)]), ',' if 
        qljjs__ilu == 1 else '')
    ummt__ewq += '\n'
    ummt__ewq += '    for i in range(len(data_out_0)):\n'
    ummt__ewq += '        __eval_res(redvars, data_out, i)\n'
    eyjvz__ezq = {}
    exec(ummt__ewq, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, eyjvz__ezq)
    return eyjvz__ezq['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    pcn__kalc = n_keys
    iybpy__qtp = []
    for ffil__yim, vadq__voibo in enumerate(allfuncs):
        if vadq__voibo.ftype == 'gen_udf':
            iybpy__qtp.append(pcn__kalc)
            pcn__kalc += 1
        elif vadq__voibo.ftype != 'udf':
            pcn__kalc += vadq__voibo.ncols_post_shuffle
        else:
            pcn__kalc += vadq__voibo.n_redvars + 1
    ummt__ewq = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    ummt__ewq += '    if num_groups == 0:\n'
    ummt__ewq += '        return\n'
    for ffil__yim, func in enumerate(udf_func_struct.general_udf_funcs):
        ummt__ewq += '    # col {}\n'.format(ffil__yim)
        ummt__ewq += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(iybpy__qtp[ffil__yim], ffil__yim))
        ummt__ewq += '    incref(out_col)\n'
        ummt__ewq += '    for j in range(num_groups):\n'
        ummt__ewq += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(ffil__yim, ffil__yim))
        ummt__ewq += '        incref(in_col)\n'
        ummt__ewq += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(ffil__yim))
    ywu__pnn = {'pd': pd, 'info_to_array': info_to_array, 'info_from_table':
        info_from_table, 'incref': incref}
    qciia__trle = 0
    for ffil__yim, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[qciia__trle]
        ywu__pnn['func_{}'.format(qciia__trle)] = func
        ywu__pnn['in_col_{}_typ'.format(qciia__trle)] = in_col_typs[
            func_idx_to_in_col[ffil__yim]]
        ywu__pnn['out_col_{}_typ'.format(qciia__trle)] = out_col_typs[ffil__yim
            ]
        qciia__trle += 1
    eyjvz__ezq = {}
    exec(ummt__ewq, ywu__pnn, eyjvz__ezq)
    vadq__voibo = eyjvz__ezq['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    wsbwy__fcoi = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(wsbwy__fcoi, nopython=True)(vadq__voibo)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    qaq__foiz = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        rpnv__eqjcw = []
        if agg_node.in_vars[0] is not None:
            rpnv__eqjcw.append('arg0')
        for ffil__yim in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if ffil__yim not in agg_node.dead_in_inds:
                rpnv__eqjcw.append(f'arg{ffil__yim}')
    else:
        rpnv__eqjcw = [f'arg{ffil__yim}' for ffil__yim, kztw__eljye in
            enumerate(agg_node.in_vars) if kztw__eljye is not None]
    ummt__ewq = f"def agg_top({', '.join(rpnv__eqjcw)}):\n"
    ypul__moq = []
    if agg_node.is_in_table_format:
        ypul__moq = agg_node.in_key_inds + [aqqb__ugosf for aqqb__ugosf,
            wiaj__pfed in agg_node.gb_info_out.values() if aqqb__ugosf is not
            None]
        if agg_node.input_has_index:
            ypul__moq.append(agg_node.n_in_cols - 1)
        qkssf__bod = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        jmg__apo = []
        for ffil__yim in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if ffil__yim in agg_node.dead_in_inds:
                jmg__apo.append('None')
            else:
                jmg__apo.append(f'arg{ffil__yim}')
        bptk__qfhr = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        ummt__ewq += f"""    table = py_data_to_cpp_table({bptk__qfhr}, ({', '.join(jmg__apo)}{qkssf__bod}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        upfop__uwqqz = [f'arg{ffil__yim}' for ffil__yim in agg_node.in_key_inds
            ]
        rjtez__wdykw = [f'arg{aqqb__ugosf}' for aqqb__ugosf, wiaj__pfed in
            agg_node.gb_info_out.values() if aqqb__ugosf is not None]
        hcfm__bwsak = upfop__uwqqz + rjtez__wdykw
        if agg_node.input_has_index:
            hcfm__bwsak.append(f'arg{len(agg_node.in_vars) - 1}')
        ummt__ewq += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({fdskb__acty})' for fdskb__acty in hcfm__bwsak))
        ummt__ewq += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    jlhf__ait = []
    func_idx_to_in_col = []
    yifxk__ibfb = []
    iqdc__bdm = False
    krodg__umc = 1
    dkf__jyuzg = -1
    pjh__ufh = 0
    qtsh__zxjbb = 0
    jrn__nkdx = [func for wiaj__pfed, func in agg_node.gb_info_out.values()]
    for pktdn__dnnud, func in enumerate(jrn__nkdx):
        jlhf__ait.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            pjh__ufh += 1
        if hasattr(func, 'skipdropna'):
            iqdc__bdm = func.skipdropna
        if func.ftype == 'shift':
            krodg__umc = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            qtsh__zxjbb = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            dkf__jyuzg = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(pktdn__dnnud)
        if func.ftype == 'udf':
            yifxk__ibfb.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            yifxk__ibfb.append(0)
            do_combine = False
    jlhf__ait.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if pjh__ufh > 0:
        if pjh__ufh != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    qgmux__khux = []
    if udf_func_struct is not None:
        zkzcz__igsyw = next_label()
        if udf_func_struct.regular_udfs:
            wsbwy__fcoi = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            gcbz__zoh = numba.cfunc(wsbwy__fcoi, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, zkzcz__igsyw))
            noc__veqgn = numba.cfunc(wsbwy__fcoi, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, zkzcz__igsyw))
            rrslm__pylr = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, zkzcz__igsyw))
            udf_func_struct.set_regular_cfuncs(gcbz__zoh, noc__veqgn,
                rrslm__pylr)
            for qrgp__iojd in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[qrgp__iojd.native_name] = qrgp__iojd
                gb_agg_cfunc_addr[qrgp__iojd.native_name] = qrgp__iojd.address
        if udf_func_struct.general_udfs:
            uwr__dvb = gen_general_udf_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, func_out_types, func_idx_to_in_col, zkzcz__igsyw)
            udf_func_struct.set_general_cfunc(uwr__dvb)
        ctwi__baurl = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        uruz__doyj = 0
        ffil__yim = 0
        for prkdb__fbjwj, vadq__voibo in zip(agg_node.gb_info_out.keys(),
            allfuncs):
            if vadq__voibo.ftype in ('udf', 'gen_udf'):
                qgmux__khux.append(out_col_typs[prkdb__fbjwj])
                for ebs__zgepu in range(uruz__doyj, uruz__doyj +
                    yifxk__ibfb[ffil__yim]):
                    qgmux__khux.append(dtype_to_array_type(ctwi__baurl[
                        ebs__zgepu]))
                uruz__doyj += yifxk__ibfb[ffil__yim]
                ffil__yim += 1
        ummt__ewq += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{ffil__yim}' for ffil__yim in range(len(qgmux__khux)))}{',' if len(qgmux__khux) == 1 else ''}))
"""
        ummt__ewq += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(qgmux__khux)})
"""
        if udf_func_struct.regular_udfs:
            ummt__ewq += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{gcbz__zoh.native_name}')\n"
                )
            ummt__ewq += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{noc__veqgn.native_name}')\n"
                )
            ummt__ewq += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{rrslm__pylr.native_name}')\n"
                )
            ummt__ewq += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{gcbz__zoh.native_name}')\n"
                )
            ummt__ewq += (
                f"    cpp_cb_combine_addr = get_agg_udf_addr('{noc__veqgn.native_name}')\n"
                )
            ummt__ewq += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{rrslm__pylr.native_name}')\n"
                )
        else:
            ummt__ewq += '    cpp_cb_update_addr = 0\n'
            ummt__ewq += '    cpp_cb_combine_addr = 0\n'
            ummt__ewq += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            qrgp__iojd = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[qrgp__iojd.native_name] = qrgp__iojd
            gb_agg_cfunc_addr[qrgp__iojd.native_name] = qrgp__iojd.address
            ummt__ewq += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{qrgp__iojd.native_name}')\n"
                )
            ummt__ewq += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{qrgp__iojd.native_name}')\n"
                )
        else:
            ummt__ewq += '    cpp_cb_general_addr = 0\n'
    else:
        ummt__ewq += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        ummt__ewq += '    cpp_cb_update_addr = 0\n'
        ummt__ewq += '    cpp_cb_combine_addr = 0\n'
        ummt__ewq += '    cpp_cb_eval_addr = 0\n'
        ummt__ewq += '    cpp_cb_general_addr = 0\n'
    ummt__ewq += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(vadq__voibo.ftype)) for
        vadq__voibo in allfuncs] + ['0']))
    ummt__ewq += (
        f'    func_offsets = np.array({str(jlhf__ait)}, dtype=np.int32)\n')
    if len(yifxk__ibfb) > 0:
        ummt__ewq += (
            f'    udf_ncols = np.array({str(yifxk__ibfb)}, dtype=np.int32)\n')
    else:
        ummt__ewq += '    udf_ncols = np.array([0], np.int32)\n'
    ummt__ewq += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    fjxj__vwqdh = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    ummt__ewq += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {iqdc__bdm}, {krodg__umc}, {qtsh__zxjbb}, {dkf__jyuzg}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {fjxj__vwqdh})
"""
    eqm__qmpgh = []
    trj__jasq = 0
    if agg_node.return_key:
        xbxj__nsvt = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for ffil__yim in range(n_keys):
            jrri__cat = xbxj__nsvt + ffil__yim
            eqm__qmpgh.append(jrri__cat if jrri__cat not in agg_node.
                dead_out_inds else -1)
            trj__jasq += 1
    for prkdb__fbjwj in agg_node.gb_info_out.keys():
        eqm__qmpgh.append(prkdb__fbjwj)
        trj__jasq += 1
    jejn__sqb = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            eqm__qmpgh.append(agg_node.n_out_cols - 1)
        else:
            jejn__sqb = True
    qkssf__bod = ',' if qaq__foiz == 1 else ''
    uhi__jcr = (
        f"({', '.join(f'out_type{ffil__yim}' for ffil__yim in range(qaq__foiz))}{qkssf__bod})"
        )
    ghziz__cte = []
    uszdt__rtqk = []
    for ffil__yim, t in enumerate(out_col_typs):
        if ffil__yim not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if ffil__yim in agg_node.gb_info_out:
                aqqb__ugosf = agg_node.gb_info_out[ffil__yim][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                vehwa__ozzy = ffil__yim - xbxj__nsvt
                aqqb__ugosf = agg_node.in_key_inds[vehwa__ozzy]
            uszdt__rtqk.append(ffil__yim)
            if (agg_node.is_in_table_format and aqqb__ugosf < agg_node.
                n_in_table_arrays):
                ghziz__cte.append(f'get_table_data(arg0, {aqqb__ugosf})')
            else:
                ghziz__cte.append(f'arg{aqqb__ugosf}')
    qkssf__bod = ',' if len(ghziz__cte) == 1 else ''
    ummt__ewq += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {uhi__jcr}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(ghziz__cte)}{qkssf__bod}), unknown_cat_out_inds)
"""
    ummt__ewq += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    ummt__ewq += '    delete_table_decref_arrays(table)\n'
    ummt__ewq += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for ffil__yim in range(n_keys):
            if eqm__qmpgh[ffil__yim] == -1:
                ummt__ewq += (
                    f'    decref_table_array(out_table, {ffil__yim})\n')
    if jejn__sqb:
        ultd__xzqyz = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        ummt__ewq += f'    decref_table_array(out_table, {ultd__xzqyz})\n'
    ummt__ewq += '    delete_table(out_table)\n'
    ummt__ewq += '    ev_clean.finalize()\n'
    ummt__ewq += '    return out_data\n'
    xry__sufc = {f'out_type{ffil__yim}': out_var_types[ffil__yim] for
        ffil__yim in range(qaq__foiz)}
    xry__sufc['out_col_inds'] = MetaType(tuple(eqm__qmpgh))
    xry__sufc['in_col_inds'] = MetaType(tuple(ypul__moq))
    xry__sufc['cpp_table_to_py_data'] = cpp_table_to_py_data
    xry__sufc['py_data_to_cpp_table'] = py_data_to_cpp_table
    xry__sufc.update({f'udf_type{ffil__yim}': t for ffil__yim, t in
        enumerate(qgmux__khux)})
    xry__sufc['udf_dummy_col_inds'] = MetaType(tuple(range(len(qgmux__khux))))
    xry__sufc['create_dummy_table'] = create_dummy_table
    xry__sufc['unknown_cat_out_inds'] = MetaType(tuple(uszdt__rtqk))
    xry__sufc['get_table_data'] = bodo.hiframes.table.get_table_data
    return ummt__ewq, xry__sufc


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    ivr__hxz = tuple(unwrap_typeref(data_types.types[ffil__yim]) for
        ffil__yim in range(len(data_types.types)))
    trwx__wbb = bodo.TableType(ivr__hxz)
    xry__sufc = {'table_type': trwx__wbb}
    ummt__ewq = 'def impl(data_types):\n'
    ummt__ewq += '  py_table = init_table(table_type, False)\n'
    ummt__ewq += '  py_table = set_table_len(py_table, 1)\n'
    for ecymt__ypgde, vbfrc__talb in trwx__wbb.type_to_blk.items():
        xry__sufc[f'typ_list_{vbfrc__talb}'] = types.List(ecymt__ypgde)
        xry__sufc[f'typ_{vbfrc__talb}'] = ecymt__ypgde
        lyow__vcunn = len(trwx__wbb.block_to_arr_ind[vbfrc__talb])
        ummt__ewq += f"""  arr_list_{vbfrc__talb} = alloc_list_like(typ_list_{vbfrc__talb}, {lyow__vcunn}, False)
"""
        ummt__ewq += f'  for i in range(len(arr_list_{vbfrc__talb})):\n'
        ummt__ewq += (
            f'    arr_list_{vbfrc__talb}[i] = alloc_type(1, typ_{vbfrc__talb}, (-1,))\n'
            )
        ummt__ewq += f"""  py_table = set_table_block(py_table, arr_list_{vbfrc__talb}, {vbfrc__talb})
"""
    ummt__ewq += '  return py_table\n'
    xry__sufc.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    eyjvz__ezq = {}
    exec(ummt__ewq, xry__sufc, eyjvz__ezq)
    return eyjvz__ezq['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    haz__osk = agg_node.in_vars[0].name
    tcfoi__lohlt, kelb__tnk, cnagx__gbgu = block_use_map[haz__osk]
    if kelb__tnk or cnagx__gbgu:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        hlbni__ubllv, smr__hnpd, bulsz__mlqrs = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if smr__hnpd or bulsz__mlqrs:
            hlbni__ubllv = set(range(agg_node.n_out_table_arrays))
    else:
        hlbni__ubllv = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            hlbni__ubllv = {0}
    xaaw__lcqyi = set(ffil__yim for ffil__yim in agg_node.in_key_inds if 
        ffil__yim < agg_node.n_in_table_arrays)
    kcdag__jvtbf = set(agg_node.gb_info_out[ffil__yim][0] for ffil__yim in
        hlbni__ubllv if ffil__yim in agg_node.gb_info_out and agg_node.
        gb_info_out[ffil__yim][0] is not None)
    kcdag__jvtbf |= xaaw__lcqyi | tcfoi__lohlt
    ovzi__vff = len(set(range(agg_node.n_in_table_arrays)) - kcdag__jvtbf) == 0
    block_use_map[haz__osk] = kcdag__jvtbf, ovzi__vff, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    zusz__wzfr = agg_node.n_out_table_arrays
    fvtbd__uxxxn = agg_node.out_vars[0].name
    opj__wyazu = _find_used_columns(fvtbd__uxxxn, zusz__wzfr,
        column_live_map, equiv_vars)
    if opj__wyazu is None:
        return False
    noyp__zgwu = set(range(zusz__wzfr)) - opj__wyazu
    jpe__yah = len(noyp__zgwu - agg_node.dead_out_inds) != 0
    if jpe__yah:
        agg_node.dead_out_inds.update(noyp__zgwu)
        agg_node.update_dead_col_info()
    return jpe__yah


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for urjt__ljh in block.body:
            if is_call_assign(urjt__ljh) and find_callname(f_ir, urjt__ljh.
                value) == ('len', 'builtins') and urjt__ljh.value.args[0
                ].name == f_ir.arg_names[0]:
                zrn__owlv = get_definition(f_ir, urjt__ljh.value.func)
                zrn__owlv.name = 'dummy_agg_count'
                zrn__owlv.value = dummy_agg_count
    jdo__umoo = get_name_var_table(f_ir.blocks)
    vihj__ntsbk = {}
    for name, wiaj__pfed in jdo__umoo.items():
        vihj__ntsbk[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, vihj__ntsbk)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    jyun__uund = numba.core.compiler.Flags()
    jyun__uund.nrt = True
    zja__spjit = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, jyun__uund)
    zja__spjit.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, bktem__rgc, calltypes, wiaj__pfed = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    okom__gmlos = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    vkggl__zig = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    olc__qdwqm = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    ffg__lyy = olc__qdwqm(typemap, calltypes)
    pm = vkggl__zig(typingctx, targetctx, None, f_ir, typemap, bktem__rgc,
        calltypes, ffg__lyy, {}, jyun__uund, None)
    zvddh__uigrz = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = vkggl__zig(typingctx, targetctx, None, f_ir, typemap, bktem__rgc,
        calltypes, ffg__lyy, {}, jyun__uund, zvddh__uigrz)
    qgs__lgtxp = numba.core.typed_passes.InlineOverloads()
    qgs__lgtxp.run_pass(pm)
    pvh__wrrd = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    pvh__wrrd.run()
    for block in f_ir.blocks.values():
        for urjt__ljh in block.body:
            if is_assign(urjt__ljh) and isinstance(urjt__ljh.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[urjt__ljh.target.name],
                SeriesType):
                ecymt__ypgde = typemap.pop(urjt__ljh.target.name)
                typemap[urjt__ljh.target.name] = ecymt__ypgde.data
            if is_call_assign(urjt__ljh) and find_callname(f_ir, urjt__ljh.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[urjt__ljh.target.name].remove(urjt__ljh.value
                    )
                urjt__ljh.value = urjt__ljh.value.args[0]
                f_ir._definitions[urjt__ljh.target.name].append(urjt__ljh.value
                    )
            if is_call_assign(urjt__ljh) and find_callname(f_ir, urjt__ljh.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[urjt__ljh.target.name].remove(urjt__ljh.value
                    )
                urjt__ljh.value = ir.Const(False, urjt__ljh.loc)
                f_ir._definitions[urjt__ljh.target.name].append(urjt__ljh.value
                    )
            if is_call_assign(urjt__ljh) and find_callname(f_ir, urjt__ljh.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[urjt__ljh.target.name].remove(urjt__ljh.value
                    )
                urjt__ljh.value = ir.Const(False, urjt__ljh.loc)
                f_ir._definitions[urjt__ljh.target.name].append(urjt__ljh.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    sqix__icjv = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, okom__gmlos)
    sqix__icjv.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    jaik__ylfv = numba.core.compiler.StateDict()
    jaik__ylfv.func_ir = f_ir
    jaik__ylfv.typemap = typemap
    jaik__ylfv.calltypes = calltypes
    jaik__ylfv.typingctx = typingctx
    jaik__ylfv.targetctx = targetctx
    jaik__ylfv.return_type = bktem__rgc
    numba.core.rewrites.rewrite_registry.apply('after-inference', jaik__ylfv)
    ihz__kixft = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        bktem__rgc, typingctx, targetctx, okom__gmlos, jyun__uund, {})
    ihz__kixft.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            kqfa__uaiyt = ctypes.pythonapi.PyCell_Get
            kqfa__uaiyt.restype = ctypes.py_object
            kqfa__uaiyt.argtypes = ctypes.py_object,
            xtzyn__ero = tuple(kqfa__uaiyt(pit__tztsh) for pit__tztsh in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            xtzyn__ero = closure.items
        assert len(code.co_freevars) == len(xtzyn__ero)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, xtzyn__ero
            )


class RegularUDFGenerator:

    def __init__(self, in_col_types, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        xcsvk__dmwtb = SeriesType(in_col_typ.dtype,
            to_str_arr_if_dict_array(in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (xcsvk__dmwtb,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        vity__hfozp, arr_var = _rm_arg_agg_block(block, pm.typemap)
        ifwzm__psbe = -1
        for ffil__yim, urjt__ljh in enumerate(vity__hfozp):
            if isinstance(urjt__ljh, numba.parfors.parfor.Parfor):
                assert ifwzm__psbe == -1, 'only one parfor for aggregation function'
                ifwzm__psbe = ffil__yim
        parfor = None
        if ifwzm__psbe != -1:
            parfor = vity__hfozp[ifwzm__psbe]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = vity__hfozp[:ifwzm__psbe] + parfor.init_block.body
        eval_nodes = vity__hfozp[ifwzm__psbe + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for urjt__ljh in init_nodes:
            if is_assign(urjt__ljh) and urjt__ljh.target.name in redvars:
                ind = redvars.index(urjt__ljh.target.name)
                reduce_vars[ind] = urjt__ljh.target
        var_types = [pm.typemap[kztw__eljye] for kztw__eljye in redvars]
        tyx__wukvq = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        rqmt__ehh = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        hyq__flb = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(hyq__flb)
        self.all_update_funcs.append(rqmt__ehh)
        self.all_combine_funcs.append(tyx__wukvq)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        xsekm__duig = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        wdwv__cgr = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        eymef__equy = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        uwrg__bkjd = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return (self.all_vartypes, xsekm__duig, wdwv__cgr, eymef__equy,
            uwrg__bkjd)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, in_col_types, typingctx, targetctx):
    unm__qjw = []
    for t, vadq__voibo in zip(in_col_types, agg_func):
        unm__qjw.append((t, vadq__voibo))
    vlhc__khm = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    lnynd__uifpj = GeneralUDFGenerator()
    for in_col_typ, func in unm__qjw:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            vlhc__khm.add_udf(in_col_typ, func)
        except:
            lnynd__uifpj.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = vlhc__khm.gen_all_func()
    general_udf_funcs = lnynd__uifpj.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    mynmw__qqmrh = compute_use_defs(parfor.loop_body)
    movn__trlsn = set()
    for sfy__dtl in mynmw__qqmrh.usemap.values():
        movn__trlsn |= sfy__dtl
    hke__sxcx = set()
    for sfy__dtl in mynmw__qqmrh.defmap.values():
        hke__sxcx |= sfy__dtl
    hei__jjp = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    hei__jjp.body = eval_nodes
    fpffn__zsid = compute_use_defs({(0): hei__jjp})
    xjway__cxla = fpffn__zsid.usemap[0]
    bsqr__lav = set()
    oqyxa__pvpw = []
    dscuj__gpnuk = []
    for urjt__ljh in reversed(init_nodes):
        qckf__kvmpj = {kztw__eljye.name for kztw__eljye in urjt__ljh.
            list_vars()}
        if is_assign(urjt__ljh):
            kztw__eljye = urjt__ljh.target.name
            qckf__kvmpj.remove(kztw__eljye)
            if (kztw__eljye in movn__trlsn and kztw__eljye not in bsqr__lav and
                kztw__eljye not in xjway__cxla and kztw__eljye not in hke__sxcx
                ):
                dscuj__gpnuk.append(urjt__ljh)
                movn__trlsn |= qckf__kvmpj
                hke__sxcx.add(kztw__eljye)
                continue
        bsqr__lav |= qckf__kvmpj
        oqyxa__pvpw.append(urjt__ljh)
    dscuj__gpnuk.reverse()
    oqyxa__pvpw.reverse()
    hpiy__ojg = min(parfor.loop_body.keys())
    dak__dmivx = parfor.loop_body[hpiy__ojg]
    dak__dmivx.body = dscuj__gpnuk + dak__dmivx.body
    return oqyxa__pvpw


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    grlsl__jgwp = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    iiwg__xop = set()
    zqlv__fzjug = []
    for urjt__ljh in init_nodes:
        if is_assign(urjt__ljh) and isinstance(urjt__ljh.value, ir.Global
            ) and isinstance(urjt__ljh.value.value, pytypes.FunctionType
            ) and urjt__ljh.value.value in grlsl__jgwp:
            iiwg__xop.add(urjt__ljh.target.name)
        elif is_call_assign(urjt__ljh
            ) and urjt__ljh.value.func.name in iiwg__xop:
            pass
        else:
            zqlv__fzjug.append(urjt__ljh)
    init_nodes = zqlv__fzjug
    qnwji__ozojl = types.Tuple(var_types)
    hewo__hepg = lambda : None
    f_ir = compile_to_numba_ir(hewo__hepg, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    pzw__pxn = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    nzfy__dbid = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), pzw__pxn, loc
        )
    block.body = block.body[-2:]
    block.body = init_nodes + [nzfy__dbid] + block.body
    block.body[-2].value.value = pzw__pxn
    zgtzs__ibpzr = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        qnwji__ozojl, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    qaaw__kplr = numba.core.target_extension.dispatcher_registry[cpu_target](
        hewo__hepg)
    qaaw__kplr.add_overload(zgtzs__ibpzr)
    return qaaw__kplr


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    wecj__vpr = len(update_funcs)
    qha__hbgw = len(in_col_types)
    ummt__ewq = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for ebs__zgepu in range(wecj__vpr):
        ouqr__hsh = ', '.join(['redvar_arrs[{}][w_ind]'.format(ffil__yim) for
            ffil__yim in range(redvar_offsets[ebs__zgepu], redvar_offsets[
            ebs__zgepu + 1])])
        if ouqr__hsh:
            ummt__ewq += '  {} = update_vars_{}({},  data_in[{}][i])\n'.format(
                ouqr__hsh, ebs__zgepu, ouqr__hsh, 0 if qha__hbgw == 1 else
                ebs__zgepu)
    ummt__ewq += '  return\n'
    ywu__pnn = {}
    for ffil__yim, vadq__voibo in enumerate(update_funcs):
        ywu__pnn['update_vars_{}'.format(ffil__yim)] = vadq__voibo
    eyjvz__ezq = {}
    exec(ummt__ewq, ywu__pnn, eyjvz__ezq)
    ump__uhxh = eyjvz__ezq['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(ump__uhxh)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    xwxn__jqst = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = xwxn__jqst, xwxn__jqst, types.intp, types.intp
    ckq__wdxo = len(redvar_offsets) - 1
    ummt__ewq = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for ebs__zgepu in range(ckq__wdxo):
        ouqr__hsh = ', '.join(['redvar_arrs[{}][w_ind]'.format(ffil__yim) for
            ffil__yim in range(redvar_offsets[ebs__zgepu], redvar_offsets[
            ebs__zgepu + 1])])
        qap__dcl = ', '.join(['recv_arrs[{}][i]'.format(ffil__yim) for
            ffil__yim in range(redvar_offsets[ebs__zgepu], redvar_offsets[
            ebs__zgepu + 1])])
        if qap__dcl:
            ummt__ewq += '  {} = combine_vars_{}({}, {})\n'.format(ouqr__hsh,
                ebs__zgepu, ouqr__hsh, qap__dcl)
    ummt__ewq += '  return\n'
    ywu__pnn = {}
    for ffil__yim, vadq__voibo in enumerate(combine_funcs):
        ywu__pnn['combine_vars_{}'.format(ffil__yim)] = vadq__voibo
    eyjvz__ezq = {}
    exec(ummt__ewq, ywu__pnn, eyjvz__ezq)
    ijqb__jojw = eyjvz__ezq['combine_all_f']
    f_ir = compile_to_numba_ir(ijqb__jojw, ywu__pnn)
    eymef__equy = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    qaaw__kplr = numba.core.target_extension.dispatcher_registry[cpu_target](
        ijqb__jojw)
    qaaw__kplr.add_overload(eymef__equy)
    return qaaw__kplr


def gen_all_eval_func(eval_funcs, redvar_offsets):
    ckq__wdxo = len(redvar_offsets) - 1
    ummt__ewq = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for ebs__zgepu in range(ckq__wdxo):
        ouqr__hsh = ', '.join(['redvar_arrs[{}][j]'.format(ffil__yim) for
            ffil__yim in range(redvar_offsets[ebs__zgepu], redvar_offsets[
            ebs__zgepu + 1])])
        ummt__ewq += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(ebs__zgepu
            , ebs__zgepu, ouqr__hsh)
    ummt__ewq += '  return\n'
    ywu__pnn = {}
    for ffil__yim, vadq__voibo in enumerate(eval_funcs):
        ywu__pnn['eval_vars_{}'.format(ffil__yim)] = vadq__voibo
    eyjvz__ezq = {}
    exec(ummt__ewq, ywu__pnn, eyjvz__ezq)
    bce__zvqac = eyjvz__ezq['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(bce__zvqac)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    ddn__rlez = len(var_types)
    nhzk__mbwf = [f'in{ffil__yim}' for ffil__yim in range(ddn__rlez)]
    qnwji__ozojl = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    trrh__njlbq = qnwji__ozojl(0)
    ummt__ewq = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        nhzk__mbwf))
    eyjvz__ezq = {}
    exec(ummt__ewq, {'_zero': trrh__njlbq}, eyjvz__ezq)
    uug__ekhxl = eyjvz__ezq['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(uug__ekhxl, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': trrh__njlbq}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    hosmr__odp = []
    for ffil__yim, kztw__eljye in enumerate(reduce_vars):
        hosmr__odp.append(ir.Assign(block.body[ffil__yim].target,
            kztw__eljye, kztw__eljye.loc))
        for jajn__bcd in kztw__eljye.versioned_names:
            hosmr__odp.append(ir.Assign(kztw__eljye, ir.Var(kztw__eljye.
                scope, jajn__bcd, kztw__eljye.loc), kztw__eljye.loc))
    block.body = block.body[:ddn__rlez] + hosmr__odp + eval_nodes
    hyq__flb = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qnwji__ozojl, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    qaaw__kplr = numba.core.target_extension.dispatcher_registry[cpu_target](
        uug__ekhxl)
    qaaw__kplr.add_overload(hyq__flb)
    return qaaw__kplr


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    ddn__rlez = len(redvars)
    agh__jjwt = [f'v{ffil__yim}' for ffil__yim in range(ddn__rlez)]
    nhzk__mbwf = [f'in{ffil__yim}' for ffil__yim in range(ddn__rlez)]
    ummt__ewq = 'def agg_combine({}):\n'.format(', '.join(agh__jjwt +
        nhzk__mbwf))
    ubhey__jgusd = wrap_parfor_blocks(parfor)
    agxc__arny = find_topo_order(ubhey__jgusd)
    agxc__arny = agxc__arny[1:]
    unwrap_parfor_blocks(parfor)
    jvsno__sxy = {}
    zmg__bhd = []
    for nrlu__bdxd in agxc__arny:
        hpxwv__gxz = parfor.loop_body[nrlu__bdxd]
        for urjt__ljh in hpxwv__gxz.body:
            if is_assign(urjt__ljh) and urjt__ljh.target.name in redvars:
                xsg__hmx = urjt__ljh.target.name
                ind = redvars.index(xsg__hmx)
                if ind in zmg__bhd:
                    continue
                if len(f_ir._definitions[xsg__hmx]) == 2:
                    var_def = f_ir._definitions[xsg__hmx][0]
                    ummt__ewq += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[xsg__hmx][1]
                    ummt__ewq += _match_reduce_def(var_def, f_ir, ind)
    ummt__ewq += '    return {}'.format(', '.join(['v{}'.format(ffil__yim) for
        ffil__yim in range(ddn__rlez)]))
    eyjvz__ezq = {}
    exec(ummt__ewq, {}, eyjvz__ezq)
    vhc__gqq = eyjvz__ezq['agg_combine']
    arg_typs = tuple(2 * var_types)
    ywu__pnn = {'numba': numba, 'bodo': bodo, 'np': np}
    ywu__pnn.update(jvsno__sxy)
    f_ir = compile_to_numba_ir(vhc__gqq, ywu__pnn, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    qnwji__ozojl = pm.typemap[block.body[-1].value.name]
    tyx__wukvq = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qnwji__ozojl, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    qaaw__kplr = numba.core.target_extension.dispatcher_registry[cpu_target](
        vhc__gqq)
    qaaw__kplr.add_overload(tyx__wukvq)
    return qaaw__kplr


def _match_reduce_def(var_def, f_ir, ind):
    ummt__ewq = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        ummt__ewq = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        lvw__eggos = guard(find_callname, f_ir, var_def)
        if lvw__eggos == ('min', 'builtins'):
            ummt__ewq = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if lvw__eggos == ('max', 'builtins'):
            ummt__ewq = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return ummt__ewq


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    ddn__rlez = len(redvars)
    wkkh__jbaat = 1
    in_vars = []
    for ffil__yim in range(wkkh__jbaat):
        aspzy__eajxn = ir.Var(arr_var.scope, f'$input{ffil__yim}', arr_var.loc)
        in_vars.append(aspzy__eajxn)
    gij__ebo = parfor.loop_nests[0].index_variable
    fkdne__jwylg = [0] * ddn__rlez
    for hpxwv__gxz in parfor.loop_body.values():
        jfj__sdtni = []
        for urjt__ljh in hpxwv__gxz.body:
            if is_var_assign(urjt__ljh
                ) and urjt__ljh.value.name == gij__ebo.name:
                continue
            if is_getitem(urjt__ljh
                ) and urjt__ljh.value.value.name == arr_var.name:
                urjt__ljh.value = in_vars[0]
            if is_call_assign(urjt__ljh) and guard(find_callname, pm.
                func_ir, urjt__ljh.value) == ('isna', 'bodo.libs.array_kernels'
                ) and urjt__ljh.value.args[0].name == arr_var.name:
                urjt__ljh.value = ir.Const(False, urjt__ljh.target.loc)
            if is_assign(urjt__ljh) and urjt__ljh.target.name in redvars:
                ind = redvars.index(urjt__ljh.target.name)
                fkdne__jwylg[ind] = urjt__ljh.target
            jfj__sdtni.append(urjt__ljh)
        hpxwv__gxz.body = jfj__sdtni
    agh__jjwt = ['v{}'.format(ffil__yim) for ffil__yim in range(ddn__rlez)]
    nhzk__mbwf = ['in{}'.format(ffil__yim) for ffil__yim in range(wkkh__jbaat)]
    ummt__ewq = 'def agg_update({}):\n'.format(', '.join(agh__jjwt +
        nhzk__mbwf))
    ummt__ewq += '    __update_redvars()\n'
    ummt__ewq += '    return {}'.format(', '.join(['v{}'.format(ffil__yim) for
        ffil__yim in range(ddn__rlez)]))
    eyjvz__ezq = {}
    exec(ummt__ewq, {}, eyjvz__ezq)
    oof__mghtr = eyjvz__ezq['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * wkkh__jbaat)
    f_ir = compile_to_numba_ir(oof__mghtr, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    mvsgw__wmjky = f_ir.blocks.popitem()[1].body
    qnwji__ozojl = pm.typemap[mvsgw__wmjky[-1].value.name]
    ubhey__jgusd = wrap_parfor_blocks(parfor)
    agxc__arny = find_topo_order(ubhey__jgusd)
    agxc__arny = agxc__arny[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    dak__dmivx = f_ir.blocks[agxc__arny[0]]
    rha__hky = f_ir.blocks[agxc__arny[-1]]
    bbxuf__vujk = mvsgw__wmjky[:ddn__rlez + wkkh__jbaat]
    if ddn__rlez > 1:
        nxpx__bedp = mvsgw__wmjky[-3:]
        assert is_assign(nxpx__bedp[0]) and isinstance(nxpx__bedp[0].value,
            ir.Expr) and nxpx__bedp[0].value.op == 'build_tuple'
    else:
        nxpx__bedp = mvsgw__wmjky[-2:]
    for ffil__yim in range(ddn__rlez):
        lmtty__tco = mvsgw__wmjky[ffil__yim].target
        kke__naqne = ir.Assign(lmtty__tco, fkdne__jwylg[ffil__yim],
            lmtty__tco.loc)
        bbxuf__vujk.append(kke__naqne)
    for ffil__yim in range(ddn__rlez, ddn__rlez + wkkh__jbaat):
        lmtty__tco = mvsgw__wmjky[ffil__yim].target
        kke__naqne = ir.Assign(lmtty__tco, in_vars[ffil__yim - ddn__rlez],
            lmtty__tco.loc)
        bbxuf__vujk.append(kke__naqne)
    dak__dmivx.body = bbxuf__vujk + dak__dmivx.body
    lzcs__yjscc = []
    for ffil__yim in range(ddn__rlez):
        lmtty__tco = mvsgw__wmjky[ffil__yim].target
        kke__naqne = ir.Assign(fkdne__jwylg[ffil__yim], lmtty__tco,
            lmtty__tco.loc)
        lzcs__yjscc.append(kke__naqne)
    rha__hky.body += lzcs__yjscc + nxpx__bedp
    thvm__wmaji = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        qnwji__ozojl, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    qaaw__kplr = numba.core.target_extension.dispatcher_registry[cpu_target](
        oof__mghtr)
    qaaw__kplr.add_overload(thvm__wmaji)
    return qaaw__kplr


def _rm_arg_agg_block(block, typemap):
    vity__hfozp = []
    arr_var = None
    for ffil__yim, urjt__ljh in enumerate(block.body):
        if is_assign(urjt__ljh) and isinstance(urjt__ljh.value, ir.Arg):
            arr_var = urjt__ljh.target
            vzw__mpgy = typemap[arr_var.name]
            if not isinstance(vzw__mpgy, types.ArrayCompatible):
                vity__hfozp += block.body[ffil__yim + 1:]
                break
            zvoh__tlio = block.body[ffil__yim + 1]
            assert is_assign(zvoh__tlio) and isinstance(zvoh__tlio.value,
                ir.Expr
                ) and zvoh__tlio.value.op == 'getattr' and zvoh__tlio.value.attr == 'shape' and zvoh__tlio.value.value.name == arr_var.name
            ifx__ffv = zvoh__tlio.target
            nfgh__cvzs = block.body[ffil__yim + 2]
            assert is_assign(nfgh__cvzs) and isinstance(nfgh__cvzs.value,
                ir.Expr
                ) and nfgh__cvzs.value.op == 'static_getitem' and nfgh__cvzs.value.value.name == ifx__ffv.name
            vity__hfozp += block.body[ffil__yim + 3:]
            break
        vity__hfozp.append(urjt__ljh)
    return vity__hfozp, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    ubhey__jgusd = wrap_parfor_blocks(parfor)
    agxc__arny = find_topo_order(ubhey__jgusd)
    agxc__arny = agxc__arny[1:]
    unwrap_parfor_blocks(parfor)
    for nrlu__bdxd in reversed(agxc__arny):
        for urjt__ljh in reversed(parfor.loop_body[nrlu__bdxd].body):
            if isinstance(urjt__ljh, ir.Assign) and (urjt__ljh.target.name in
                parfor_params or urjt__ljh.target.name in var_to_param):
                kdi__jpt = urjt__ljh.target.name
                rhs = urjt__ljh.value
                gvwzq__zfuwc = (kdi__jpt if kdi__jpt in parfor_params else
                    var_to_param[kdi__jpt])
                jrd__wuawo = []
                if isinstance(rhs, ir.Var):
                    jrd__wuawo = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    jrd__wuawo = [kztw__eljye.name for kztw__eljye in
                        urjt__ljh.value.list_vars()]
                param_uses[gvwzq__zfuwc].extend(jrd__wuawo)
                for kztw__eljye in jrd__wuawo:
                    var_to_param[kztw__eljye] = gvwzq__zfuwc
            if isinstance(urjt__ljh, Parfor):
                get_parfor_reductions(urjt__ljh, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for csh__keg, jrd__wuawo in param_uses.items():
        if csh__keg in jrd__wuawo and csh__keg not in reduce_varnames:
            reduce_varnames.append(csh__keg)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
