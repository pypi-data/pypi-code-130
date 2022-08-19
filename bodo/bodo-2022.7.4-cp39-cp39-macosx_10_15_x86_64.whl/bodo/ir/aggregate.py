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
        yveas__zfdt = func.signature
        if yveas__zfdt == types.none(types.voidptr):
            ifa__ebdst = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            wxmv__syuhs = cgutils.get_or_insert_function(builder.module,
                ifa__ebdst, sym._literal_value)
            builder.call(wxmv__syuhs, [context.get_constant_null(
                yveas__zfdt.args[0])])
        elif yveas__zfdt == types.none(types.int64, types.voidptr, types.
            voidptr):
            ifa__ebdst = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            wxmv__syuhs = cgutils.get_or_insert_function(builder.module,
                ifa__ebdst, sym._literal_value)
            builder.call(wxmv__syuhs, [context.get_constant(types.int64, 0),
                context.get_constant_null(yveas__zfdt.args[1]), context.
                get_constant_null(yveas__zfdt.args[2])])
        else:
            ifa__ebdst = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            wxmv__syuhs = cgutils.get_or_insert_function(builder.module,
                ifa__ebdst, sym._literal_value)
            builder.call(wxmv__syuhs, [context.get_constant_null(
                yveas__zfdt.args[0]), context.get_constant_null(yveas__zfdt
                .args[1]), context.get_constant_null(yveas__zfdt.args[2])])
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
        qzl__svvwi = True
        itvc__qszbi = 1
        opg__cepyf = -1
        if isinstance(rhs, ir.Expr):
            for rplox__eey in rhs.kws:
                if func_name in list_cumulative:
                    if rplox__eey[0] == 'skipna':
                        qzl__svvwi = guard(find_const, func_ir, rplox__eey[1])
                        if not isinstance(qzl__svvwi, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if rplox__eey[0] == 'dropna':
                        qzl__svvwi = guard(find_const, func_ir, rplox__eey[1])
                        if not isinstance(qzl__svvwi, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            itvc__qszbi = get_call_expr_arg('shift', rhs.args, dict(rhs.kws
                ), 0, 'periods', itvc__qszbi)
            itvc__qszbi = guard(find_const, func_ir, itvc__qszbi)
        if func_name == 'head':
            opg__cepyf = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(opg__cepyf, int):
                opg__cepyf = guard(find_const, func_ir, opg__cepyf)
            if opg__cepyf < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = qzl__svvwi
        func.periods = itvc__qszbi
        func.head_n = opg__cepyf
        if func_name == 'transform':
            kws = dict(rhs.kws)
            duu__csx = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            lxqef__hbmq = typemap[duu__csx.name]
            uht__zuc = None
            if isinstance(lxqef__hbmq, str):
                uht__zuc = lxqef__hbmq
            elif is_overload_constant_str(lxqef__hbmq):
                uht__zuc = get_overload_const_str(lxqef__hbmq)
            elif bodo.utils.typing.is_builtin_function(lxqef__hbmq):
                uht__zuc = bodo.utils.typing.get_builtin_function_name(
                    lxqef__hbmq)
            if uht__zuc not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {uht__zuc}')
            func.transform_func = supported_agg_funcs.index(uht__zuc)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    duu__csx = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if duu__csx == '':
        lxqef__hbmq = types.none
    else:
        lxqef__hbmq = typemap[duu__csx.name]
    if is_overload_constant_dict(lxqef__hbmq):
        cjg__fpnsu = get_overload_constant_dict(lxqef__hbmq)
        tmjrv__ixzbu = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in cjg__fpnsu.values()]
        return tmjrv__ixzbu
    if lxqef__hbmq == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(lxqef__hbmq, types.BaseTuple) or is_overload_constant_list(
        lxqef__hbmq):
        tmjrv__ixzbu = []
        evs__owmp = 0
        if is_overload_constant_list(lxqef__hbmq):
            ivf__scpir = get_overload_const_list(lxqef__hbmq)
        else:
            ivf__scpir = lxqef__hbmq.types
        for t in ivf__scpir:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                tmjrv__ixzbu.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(ivf__scpir) > 1:
                    func.fname = '<lambda_' + str(evs__owmp) + '>'
                    evs__owmp += 1
                tmjrv__ixzbu.append(func)
        return [tmjrv__ixzbu]
    if is_overload_constant_str(lxqef__hbmq):
        func_name = get_overload_const_str(lxqef__hbmq)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(lxqef__hbmq):
        func_name = bodo.utils.typing.get_builtin_function_name(lxqef__hbmq)
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
        evs__owmp = 0
        mbroy__obqll = []
        for ufaqm__pbehj in f_val:
            func = get_agg_func_udf(func_ir, ufaqm__pbehj, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{evs__owmp}>'
                evs__owmp += 1
            mbroy__obqll.append(func)
        return mbroy__obqll
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
    uht__zuc = code.co_name
    return uht__zuc


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
            qdzia__wal = types.DType(args[0])
            return signature(qdzia__wal, *args)


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
        return [thxo__xfrn for thxo__xfrn in self.in_vars if thxo__xfrn is not
            None]

    def get_live_out_vars(self):
        return [thxo__xfrn for thxo__xfrn in self.out_vars if thxo__xfrn is not
            None]

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
        ssi__nwvbh = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        lnc__thk = list(get_index_data_arr_types(self.out_type.index))
        return ssi__nwvbh + lnc__thk

    def update_dead_col_info(self):
        for tngjg__mbveu in self.dead_out_inds:
            self.gb_info_out.pop(tngjg__mbveu, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for sowib__foboi, tovhi__vxzfk in self.gb_info_in.copy().items():
            tlt__fxtbj = []
            for ufaqm__pbehj, cspy__naae in tovhi__vxzfk:
                if cspy__naae not in self.dead_out_inds:
                    tlt__fxtbj.append((ufaqm__pbehj, cspy__naae))
            if not tlt__fxtbj:
                if (sowib__foboi is not None and sowib__foboi not in self.
                    in_key_inds):
                    self.dead_in_inds.add(sowib__foboi)
                self.gb_info_in.pop(sowib__foboi)
            else:
                self.gb_info_in[sowib__foboi] = tlt__fxtbj
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for uiytg__xkl in range(1, len(self.in_vars)):
                tngjg__mbveu = self.n_in_table_arrays + uiytg__xkl - 1
                if tngjg__mbveu in self.dead_in_inds:
                    self.in_vars[uiytg__xkl] = None
        else:
            for uiytg__xkl in range(len(self.in_vars)):
                if uiytg__xkl in self.dead_in_inds:
                    self.in_vars[uiytg__xkl] = None

    def __repr__(self):
        txoh__toxpc = ', '.join(thxo__xfrn.name for thxo__xfrn in self.
            get_live_in_vars())
        owl__hblcq = f'{self.df_in}{{{txoh__toxpc}}}'
        lubfq__rpgre = ', '.join(thxo__xfrn.name for thxo__xfrn in self.
            get_live_out_vars())
        rdlhs__adu = f'{self.df_out}{{{lubfq__rpgre}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {owl__hblcq} {rdlhs__adu}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({thxo__xfrn.name for thxo__xfrn in aggregate_node.
        get_live_in_vars()})
    def_set.update({thxo__xfrn.name for thxo__xfrn in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    eylz__hmx = agg_node.out_vars[0]
    if eylz__hmx is not None and eylz__hmx.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            lkuy__fxyp = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(lkuy__fxyp)
        else:
            agg_node.dead_out_inds.add(0)
    for uiytg__xkl in range(1, len(agg_node.out_vars)):
        thxo__xfrn = agg_node.out_vars[uiytg__xkl]
        if thxo__xfrn is not None and thxo__xfrn.name not in lives:
            agg_node.out_vars[uiytg__xkl] = None
            tngjg__mbveu = agg_node.n_out_table_arrays + uiytg__xkl - 1
            agg_node.dead_out_inds.add(tngjg__mbveu)
    if all(thxo__xfrn is None for thxo__xfrn in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    irdso__kle = {thxo__xfrn.name for thxo__xfrn in aggregate_node.
        get_live_out_vars()}
    return set(), irdso__kle


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for uiytg__xkl in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[uiytg__xkl] is not None:
            aggregate_node.in_vars[uiytg__xkl] = replace_vars_inner(
                aggregate_node.in_vars[uiytg__xkl], var_dict)
    for uiytg__xkl in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[uiytg__xkl] is not None:
            aggregate_node.out_vars[uiytg__xkl] = replace_vars_inner(
                aggregate_node.out_vars[uiytg__xkl], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for uiytg__xkl in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[uiytg__xkl] is not None:
            aggregate_node.in_vars[uiytg__xkl] = visit_vars_inner(
                aggregate_node.in_vars[uiytg__xkl], callback, cbdata)
    for uiytg__xkl in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[uiytg__xkl] is not None:
            aggregate_node.out_vars[uiytg__xkl] = visit_vars_inner(
                aggregate_node.out_vars[uiytg__xkl], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    xipbq__supbd = []
    for yztf__fug in aggregate_node.get_live_in_vars():
        tezh__hydth = equiv_set.get_shape(yztf__fug)
        if tezh__hydth is not None:
            xipbq__supbd.append(tezh__hydth[0])
    if len(xipbq__supbd) > 1:
        equiv_set.insert_equiv(*xipbq__supbd)
    kcmvo__ming = []
    xipbq__supbd = []
    for yztf__fug in aggregate_node.get_live_out_vars():
        ntkh__haoa = typemap[yztf__fug.name]
        zfbke__wnlc = array_analysis._gen_shape_call(equiv_set, yztf__fug,
            ntkh__haoa.ndim, None, kcmvo__ming)
        equiv_set.insert_equiv(yztf__fug, zfbke__wnlc)
        xipbq__supbd.append(zfbke__wnlc[0])
        equiv_set.define(yztf__fug, set())
    if len(xipbq__supbd) > 1:
        equiv_set.insert_equiv(*xipbq__supbd)
    return [], kcmvo__ming


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    kuau__cnciw = aggregate_node.get_live_in_vars()
    dlqr__hdvi = aggregate_node.get_live_out_vars()
    pom__mfaq = Distribution.OneD
    for yztf__fug in kuau__cnciw:
        pom__mfaq = Distribution(min(pom__mfaq.value, array_dists[yztf__fug
            .name].value))
    htd__cttn = Distribution(min(pom__mfaq.value, Distribution.OneD_Var.value))
    for yztf__fug in dlqr__hdvi:
        if yztf__fug.name in array_dists:
            htd__cttn = Distribution(min(htd__cttn.value, array_dists[
                yztf__fug.name].value))
    if htd__cttn != Distribution.OneD_Var:
        pom__mfaq = htd__cttn
    for yztf__fug in kuau__cnciw:
        array_dists[yztf__fug.name] = pom__mfaq
    for yztf__fug in dlqr__hdvi:
        array_dists[yztf__fug.name] = htd__cttn


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for yztf__fug in agg_node.get_live_out_vars():
        definitions[yztf__fug.name].append(agg_node)
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
    qpmo__zqj = agg_node.get_live_in_vars()
    ubba__awjir = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for thxo__xfrn in (qpmo__zqj + ubba__awjir):
            if array_dists[thxo__xfrn.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                thxo__xfrn.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    tmjrv__ixzbu = []
    func_out_types = []
    for cspy__naae, (sowib__foboi, func) in agg_node.gb_info_out.items():
        if sowib__foboi is not None:
            t = agg_node.in_col_types[sowib__foboi]
            in_col_typs.append(t)
        tmjrv__ixzbu.append(func)
        func_out_types.append(out_col_typs[cspy__naae])
    apra__zoc = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for uiytg__xkl, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            apra__zoc.update({f'in_cat_dtype_{uiytg__xkl}': in_col_typ})
    for uiytg__xkl, bzm__mxa in enumerate(out_col_typs):
        if isinstance(bzm__mxa, bodo.CategoricalArrayType):
            apra__zoc.update({f'out_cat_dtype_{uiytg__xkl}': bzm__mxa})
    udf_func_struct = get_udf_func_struct(tmjrv__ixzbu, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[thxo__xfrn.name] if thxo__xfrn is not None else
        types.none) for thxo__xfrn in agg_node.out_vars]
    jgqhc__cqj, lyup__xbt = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    apra__zoc.update(lyup__xbt)
    apra__zoc.update({'pd': pd, 'pre_alloc_string_array':
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
            apra__zoc.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            apra__zoc.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    ibeka__leb = {}
    exec(jgqhc__cqj, {}, ibeka__leb)
    bqyl__jni = ibeka__leb['agg_top']
    ltgl__txey = compile_to_numba_ir(bqyl__jni, apra__zoc, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[thxo__xfrn.
        name] for thxo__xfrn in qpmo__zqj), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(ltgl__txey, qpmo__zqj)
    wlcf__firp = ltgl__txey.body[-2].value.value
    kit__fbj = ltgl__txey.body[:-2]
    for uiytg__xkl, thxo__xfrn in enumerate(ubba__awjir):
        gen_getitem(thxo__xfrn, wlcf__firp, uiytg__xkl, calltypes, kit__fbj)
    return kit__fbj


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        blh__lgg = IntDtype(t.dtype).name
        assert blh__lgg.endswith('Dtype()')
        blh__lgg = blh__lgg[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{blh__lgg}'))"
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
        ftcdg__nbu = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {ftcdg__nbu}_cat_dtype_{colnum})')
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
    cwm__iso = udf_func_struct.var_typs
    gdg__xts = len(cwm__iso)
    jgqhc__cqj = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    jgqhc__cqj += '    if is_null_pointer(in_table):\n'
    jgqhc__cqj += '        return\n'
    jgqhc__cqj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cwm__iso]), ',' if
        len(cwm__iso) == 1 else '')
    pwxx__rzzte = n_keys
    hke__dxz = []
    redvar_offsets = []
    spvww__qubl = []
    if do_combine:
        for uiytg__xkl, ufaqm__pbehj in enumerate(allfuncs):
            if ufaqm__pbehj.ftype != 'udf':
                pwxx__rzzte += ufaqm__pbehj.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(pwxx__rzzte, pwxx__rzzte +
                    ufaqm__pbehj.n_redvars))
                pwxx__rzzte += ufaqm__pbehj.n_redvars
                spvww__qubl.append(data_in_typs_[func_idx_to_in_col[
                    uiytg__xkl]])
                hke__dxz.append(func_idx_to_in_col[uiytg__xkl] + n_keys)
    else:
        for uiytg__xkl, ufaqm__pbehj in enumerate(allfuncs):
            if ufaqm__pbehj.ftype != 'udf':
                pwxx__rzzte += ufaqm__pbehj.ncols_post_shuffle
            else:
                redvar_offsets += list(range(pwxx__rzzte + 1, pwxx__rzzte +
                    1 + ufaqm__pbehj.n_redvars))
                pwxx__rzzte += ufaqm__pbehj.n_redvars + 1
                spvww__qubl.append(data_in_typs_[func_idx_to_in_col[
                    uiytg__xkl]])
                hke__dxz.append(func_idx_to_in_col[uiytg__xkl] + n_keys)
    assert len(redvar_offsets) == gdg__xts
    uzgfh__cisz = len(spvww__qubl)
    fuere__kgdy = []
    for uiytg__xkl, t in enumerate(spvww__qubl):
        fuere__kgdy.append(_gen_dummy_alloc(t, uiytg__xkl, True))
    jgqhc__cqj += '    data_in_dummy = ({}{})\n'.format(','.join(
        fuere__kgdy), ',' if len(spvww__qubl) == 1 else '')
    jgqhc__cqj += """
    # initialize redvar cols
"""
    jgqhc__cqj += '    init_vals = __init_func()\n'
    for uiytg__xkl in range(gdg__xts):
        jgqhc__cqj += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(uiytg__xkl, redvar_offsets[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(redvar_arr_{})\n'.format(uiytg__xkl)
        jgqhc__cqj += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            uiytg__xkl, uiytg__xkl)
    jgqhc__cqj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(uiytg__xkl) for uiytg__xkl in range(gdg__xts)]), ',' if 
        gdg__xts == 1 else '')
    jgqhc__cqj += '\n'
    for uiytg__xkl in range(uzgfh__cisz):
        jgqhc__cqj += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(uiytg__xkl, hke__dxz[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(data_in_{})\n'.format(uiytg__xkl)
    jgqhc__cqj += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(uiytg__xkl) for uiytg__xkl in range(uzgfh__cisz)]), ',' if 
        uzgfh__cisz == 1 else '')
    jgqhc__cqj += '\n'
    jgqhc__cqj += '    for i in range(len(data_in_0)):\n'
    jgqhc__cqj += '        w_ind = row_to_group[i]\n'
    jgqhc__cqj += '        if w_ind != -1:\n'
    jgqhc__cqj += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    ibeka__leb = {}
    exec(jgqhc__cqj, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ibeka__leb)
    return ibeka__leb['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    cwm__iso = udf_func_struct.var_typs
    gdg__xts = len(cwm__iso)
    jgqhc__cqj = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    jgqhc__cqj += '    if is_null_pointer(in_table):\n'
    jgqhc__cqj += '        return\n'
    jgqhc__cqj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cwm__iso]), ',' if
        len(cwm__iso) == 1 else '')
    stf__qign = n_keys
    zcijb__xuop = n_keys
    wewst__ssc = []
    wgrhn__zaw = []
    for ufaqm__pbehj in allfuncs:
        if ufaqm__pbehj.ftype != 'udf':
            stf__qign += ufaqm__pbehj.ncols_pre_shuffle
            zcijb__xuop += ufaqm__pbehj.ncols_post_shuffle
        else:
            wewst__ssc += list(range(stf__qign, stf__qign + ufaqm__pbehj.
                n_redvars))
            wgrhn__zaw += list(range(zcijb__xuop + 1, zcijb__xuop + 1 +
                ufaqm__pbehj.n_redvars))
            stf__qign += ufaqm__pbehj.n_redvars
            zcijb__xuop += 1 + ufaqm__pbehj.n_redvars
    assert len(wewst__ssc) == gdg__xts
    jgqhc__cqj += """
    # initialize redvar cols
"""
    jgqhc__cqj += '    init_vals = __init_func()\n'
    for uiytg__xkl in range(gdg__xts):
        jgqhc__cqj += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(uiytg__xkl, wgrhn__zaw[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(redvar_arr_{})\n'.format(uiytg__xkl)
        jgqhc__cqj += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            uiytg__xkl, uiytg__xkl)
    jgqhc__cqj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(uiytg__xkl) for uiytg__xkl in range(gdg__xts)]), ',' if 
        gdg__xts == 1 else '')
    jgqhc__cqj += '\n'
    for uiytg__xkl in range(gdg__xts):
        jgqhc__cqj += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(uiytg__xkl, wewst__ssc[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(recv_redvar_arr_{})\n'.format(uiytg__xkl)
    jgqhc__cqj += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(uiytg__xkl) for uiytg__xkl in range(
        gdg__xts)]), ',' if gdg__xts == 1 else '')
    jgqhc__cqj += '\n'
    if gdg__xts:
        jgqhc__cqj += '    for i in range(len(recv_redvar_arr_0)):\n'
        jgqhc__cqj += '        w_ind = row_to_group[i]\n'
        jgqhc__cqj += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    ibeka__leb = {}
    exec(jgqhc__cqj, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ibeka__leb)
    return ibeka__leb['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    cwm__iso = udf_func_struct.var_typs
    gdg__xts = len(cwm__iso)
    pwxx__rzzte = n_keys
    redvar_offsets = []
    xqfo__uob = []
    llq__ogkhs = []
    for uiytg__xkl, ufaqm__pbehj in enumerate(allfuncs):
        if ufaqm__pbehj.ftype != 'udf':
            pwxx__rzzte += ufaqm__pbehj.ncols_post_shuffle
        else:
            xqfo__uob.append(pwxx__rzzte)
            redvar_offsets += list(range(pwxx__rzzte + 1, pwxx__rzzte + 1 +
                ufaqm__pbehj.n_redvars))
            pwxx__rzzte += 1 + ufaqm__pbehj.n_redvars
            llq__ogkhs.append(out_data_typs_[uiytg__xkl])
    assert len(redvar_offsets) == gdg__xts
    uzgfh__cisz = len(llq__ogkhs)
    jgqhc__cqj = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    jgqhc__cqj += '    if is_null_pointer(table):\n'
    jgqhc__cqj += '        return\n'
    jgqhc__cqj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in cwm__iso]), ',' if
        len(cwm__iso) == 1 else '')
    jgqhc__cqj += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        llq__ogkhs]), ',' if len(llq__ogkhs) == 1 else '')
    for uiytg__xkl in range(gdg__xts):
        jgqhc__cqj += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(uiytg__xkl, redvar_offsets[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(redvar_arr_{})\n'.format(uiytg__xkl)
    jgqhc__cqj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(uiytg__xkl) for uiytg__xkl in range(gdg__xts)]), ',' if 
        gdg__xts == 1 else '')
    jgqhc__cqj += '\n'
    for uiytg__xkl in range(uzgfh__cisz):
        jgqhc__cqj += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(uiytg__xkl, xqfo__uob[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(data_out_{})\n'.format(uiytg__xkl)
    jgqhc__cqj += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(uiytg__xkl) for uiytg__xkl in range(uzgfh__cisz)]), ',' if 
        uzgfh__cisz == 1 else '')
    jgqhc__cqj += '\n'
    jgqhc__cqj += '    for i in range(len(data_out_0)):\n'
    jgqhc__cqj += '        __eval_res(redvars, data_out, i)\n'
    ibeka__leb = {}
    exec(jgqhc__cqj, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ibeka__leb)
    return ibeka__leb['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    pwxx__rzzte = n_keys
    sahc__crwt = []
    for uiytg__xkl, ufaqm__pbehj in enumerate(allfuncs):
        if ufaqm__pbehj.ftype == 'gen_udf':
            sahc__crwt.append(pwxx__rzzte)
            pwxx__rzzte += 1
        elif ufaqm__pbehj.ftype != 'udf':
            pwxx__rzzte += ufaqm__pbehj.ncols_post_shuffle
        else:
            pwxx__rzzte += ufaqm__pbehj.n_redvars + 1
    jgqhc__cqj = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    jgqhc__cqj += '    if num_groups == 0:\n'
    jgqhc__cqj += '        return\n'
    for uiytg__xkl, func in enumerate(udf_func_struct.general_udf_funcs):
        jgqhc__cqj += '    # col {}\n'.format(uiytg__xkl)
        jgqhc__cqj += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(sahc__crwt[uiytg__xkl], uiytg__xkl))
        jgqhc__cqj += '    incref(out_col)\n'
        jgqhc__cqj += '    for j in range(num_groups):\n'
        jgqhc__cqj += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(uiytg__xkl, uiytg__xkl))
        jgqhc__cqj += '        incref(in_col)\n'
        jgqhc__cqj += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(uiytg__xkl))
    apra__zoc = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    ufjpm__qgewr = 0
    for uiytg__xkl, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[ufjpm__qgewr]
        apra__zoc['func_{}'.format(ufjpm__qgewr)] = func
        apra__zoc['in_col_{}_typ'.format(ufjpm__qgewr)] = in_col_typs[
            func_idx_to_in_col[uiytg__xkl]]
        apra__zoc['out_col_{}_typ'.format(ufjpm__qgewr)] = out_col_typs[
            uiytg__xkl]
        ufjpm__qgewr += 1
    ibeka__leb = {}
    exec(jgqhc__cqj, apra__zoc, ibeka__leb)
    ufaqm__pbehj = ibeka__leb['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    oko__vypj = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(oko__vypj, nopython=True)(ufaqm__pbehj)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    jtxyc__cfja = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        kdt__svnoa = []
        if agg_node.in_vars[0] is not None:
            kdt__svnoa.append('arg0')
        for uiytg__xkl in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if uiytg__xkl not in agg_node.dead_in_inds:
                kdt__svnoa.append(f'arg{uiytg__xkl}')
    else:
        kdt__svnoa = [f'arg{uiytg__xkl}' for uiytg__xkl, thxo__xfrn in
            enumerate(agg_node.in_vars) if thxo__xfrn is not None]
    jgqhc__cqj = f"def agg_top({', '.join(kdt__svnoa)}):\n"
    ppte__nxce = []
    if agg_node.is_in_table_format:
        ppte__nxce = agg_node.in_key_inds + [sowib__foboi for sowib__foboi,
            mrbi__hobi in agg_node.gb_info_out.values() if sowib__foboi is not
            None]
        if agg_node.input_has_index:
            ppte__nxce.append(agg_node.n_in_cols - 1)
        ynp__ckl = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        lov__pbif = []
        for uiytg__xkl in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if uiytg__xkl in agg_node.dead_in_inds:
                lov__pbif.append('None')
            else:
                lov__pbif.append(f'arg{uiytg__xkl}')
        kaz__qcoz = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        jgqhc__cqj += f"""    table = py_data_to_cpp_table({kaz__qcoz}, ({', '.join(lov__pbif)}{ynp__ckl}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        ojd__gasc = [f'arg{uiytg__xkl}' for uiytg__xkl in agg_node.in_key_inds]
        xqo__woau = [f'arg{sowib__foboi}' for sowib__foboi, mrbi__hobi in
            agg_node.gb_info_out.values() if sowib__foboi is not None]
        jxcyk__cfuzm = ojd__gasc + xqo__woau
        if agg_node.input_has_index:
            jxcyk__cfuzm.append(f'arg{len(agg_node.in_vars) - 1}')
        jgqhc__cqj += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({zum__uktg})' for zum__uktg in jxcyk__cfuzm))
        jgqhc__cqj += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    pgub__dgseb = []
    func_idx_to_in_col = []
    rqvyw__hri = []
    qzl__svvwi = False
    wqu__qlew = 1
    opg__cepyf = -1
    xpfnd__ssk = 0
    teuzc__besv = 0
    tmjrv__ixzbu = [func for mrbi__hobi, func in agg_node.gb_info_out.values()]
    for kuyl__swbln, func in enumerate(tmjrv__ixzbu):
        pgub__dgseb.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            xpfnd__ssk += 1
        if hasattr(func, 'skipdropna'):
            qzl__svvwi = func.skipdropna
        if func.ftype == 'shift':
            wqu__qlew = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            teuzc__besv = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            opg__cepyf = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(kuyl__swbln)
        if func.ftype == 'udf':
            rqvyw__hri.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            rqvyw__hri.append(0)
            do_combine = False
    pgub__dgseb.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if xpfnd__ssk > 0:
        if xpfnd__ssk != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    abqob__uyhj = []
    if udf_func_struct is not None:
        vakye__mexb = next_label()
        if udf_func_struct.regular_udfs:
            oko__vypj = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            wwmsf__fppp = numba.cfunc(oko__vypj, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, vakye__mexb))
            kpaxe__yndl = numba.cfunc(oko__vypj, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, vakye__mexb))
            lfsqm__ngga = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, vakye__mexb))
            udf_func_struct.set_regular_cfuncs(wwmsf__fppp, kpaxe__yndl,
                lfsqm__ngga)
            for nqf__sim in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[nqf__sim.native_name] = nqf__sim
                gb_agg_cfunc_addr[nqf__sim.native_name] = nqf__sim.address
        if udf_func_struct.general_udfs:
            ypw__yqn = gen_general_udf_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, func_out_types, func_idx_to_in_col, vakye__mexb)
            udf_func_struct.set_general_cfunc(ypw__yqn)
        cwm__iso = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        yihfj__pcv = 0
        uiytg__xkl = 0
        for tks__nwf, ufaqm__pbehj in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if ufaqm__pbehj.ftype in ('udf', 'gen_udf'):
                abqob__uyhj.append(out_col_typs[tks__nwf])
                for gjyml__epgl in range(yihfj__pcv, yihfj__pcv +
                    rqvyw__hri[uiytg__xkl]):
                    abqob__uyhj.append(dtype_to_array_type(cwm__iso[
                        gjyml__epgl]))
                yihfj__pcv += rqvyw__hri[uiytg__xkl]
                uiytg__xkl += 1
        jgqhc__cqj += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{uiytg__xkl}' for uiytg__xkl in range(len(abqob__uyhj)))}{',' if len(abqob__uyhj) == 1 else ''}))
"""
        jgqhc__cqj += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(abqob__uyhj)})
"""
        if udf_func_struct.regular_udfs:
            jgqhc__cqj += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{wwmsf__fppp.native_name}')\n"
                )
            jgqhc__cqj += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{kpaxe__yndl.native_name}')\n"
                )
            jgqhc__cqj += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{lfsqm__ngga.native_name}')\n"
                )
            jgqhc__cqj += f"""    cpp_cb_update_addr = get_agg_udf_addr('{wwmsf__fppp.native_name}')
"""
            jgqhc__cqj += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{kpaxe__yndl.native_name}')
"""
            jgqhc__cqj += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{lfsqm__ngga.native_name}')\n"
                )
        else:
            jgqhc__cqj += '    cpp_cb_update_addr = 0\n'
            jgqhc__cqj += '    cpp_cb_combine_addr = 0\n'
            jgqhc__cqj += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            nqf__sim = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[nqf__sim.native_name] = nqf__sim
            gb_agg_cfunc_addr[nqf__sim.native_name] = nqf__sim.address
            jgqhc__cqj += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{nqf__sim.native_name}')\n"
                )
            jgqhc__cqj += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{nqf__sim.native_name}')\n"
                )
        else:
            jgqhc__cqj += '    cpp_cb_general_addr = 0\n'
    else:
        jgqhc__cqj += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        jgqhc__cqj += '    cpp_cb_update_addr = 0\n'
        jgqhc__cqj += '    cpp_cb_combine_addr = 0\n'
        jgqhc__cqj += '    cpp_cb_eval_addr = 0\n'
        jgqhc__cqj += '    cpp_cb_general_addr = 0\n'
    jgqhc__cqj += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(ufaqm__pbehj.ftype)) for
        ufaqm__pbehj in allfuncs] + ['0']))
    jgqhc__cqj += (
        f'    func_offsets = np.array({str(pgub__dgseb)}, dtype=np.int32)\n')
    if len(rqvyw__hri) > 0:
        jgqhc__cqj += (
            f'    udf_ncols = np.array({str(rqvyw__hri)}, dtype=np.int32)\n')
    else:
        jgqhc__cqj += '    udf_ncols = np.array([0], np.int32)\n'
    jgqhc__cqj += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    hnj__pzfta = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    jgqhc__cqj += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {qzl__svvwi}, {wqu__qlew}, {teuzc__besv}, {opg__cepyf}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {hnj__pzfta})
"""
    buzwa__htn = []
    itly__pia = 0
    if agg_node.return_key:
        cdl__zygcm = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for uiytg__xkl in range(n_keys):
            tngjg__mbveu = cdl__zygcm + uiytg__xkl
            buzwa__htn.append(tngjg__mbveu if tngjg__mbveu not in agg_node.
                dead_out_inds else -1)
            itly__pia += 1
    for tks__nwf in agg_node.gb_info_out.keys():
        buzwa__htn.append(tks__nwf)
        itly__pia += 1
    tnvwh__lii = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            buzwa__htn.append(agg_node.n_out_cols - 1)
        else:
            tnvwh__lii = True
    ynp__ckl = ',' if jtxyc__cfja == 1 else ''
    rth__hjzbr = (
        f"({', '.join(f'out_type{uiytg__xkl}' for uiytg__xkl in range(jtxyc__cfja))}{ynp__ckl})"
        )
    qib__qyn = []
    jcamg__tejtd = []
    for uiytg__xkl, t in enumerate(out_col_typs):
        if uiytg__xkl not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if uiytg__xkl in agg_node.gb_info_out:
                sowib__foboi = agg_node.gb_info_out[uiytg__xkl][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                vbl__rvo = uiytg__xkl - cdl__zygcm
                sowib__foboi = agg_node.in_key_inds[vbl__rvo]
            jcamg__tejtd.append(uiytg__xkl)
            if (agg_node.is_in_table_format and sowib__foboi < agg_node.
                n_in_table_arrays):
                qib__qyn.append(f'get_table_data(arg0, {sowib__foboi})')
            else:
                qib__qyn.append(f'arg{sowib__foboi}')
    ynp__ckl = ',' if len(qib__qyn) == 1 else ''
    jgqhc__cqj += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {rth__hjzbr}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(qib__qyn)}{ynp__ckl}), unknown_cat_out_inds)
"""
    jgqhc__cqj += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    jgqhc__cqj += '    delete_table_decref_arrays(table)\n'
    jgqhc__cqj += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for uiytg__xkl in range(n_keys):
            if buzwa__htn[uiytg__xkl] == -1:
                jgqhc__cqj += (
                    f'    decref_table_array(out_table, {uiytg__xkl})\n')
    if tnvwh__lii:
        mfvzs__amevb = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        jgqhc__cqj += f'    decref_table_array(out_table, {mfvzs__amevb})\n'
    jgqhc__cqj += '    delete_table(out_table)\n'
    jgqhc__cqj += '    ev_clean.finalize()\n'
    jgqhc__cqj += '    return out_data\n'
    tuow__mvgf = {f'out_type{uiytg__xkl}': out_var_types[uiytg__xkl] for
        uiytg__xkl in range(jtxyc__cfja)}
    tuow__mvgf['out_col_inds'] = MetaType(tuple(buzwa__htn))
    tuow__mvgf['in_col_inds'] = MetaType(tuple(ppte__nxce))
    tuow__mvgf['cpp_table_to_py_data'] = cpp_table_to_py_data
    tuow__mvgf['py_data_to_cpp_table'] = py_data_to_cpp_table
    tuow__mvgf.update({f'udf_type{uiytg__xkl}': t for uiytg__xkl, t in
        enumerate(abqob__uyhj)})
    tuow__mvgf['udf_dummy_col_inds'] = MetaType(tuple(range(len(abqob__uyhj))))
    tuow__mvgf['create_dummy_table'] = create_dummy_table
    tuow__mvgf['unknown_cat_out_inds'] = MetaType(tuple(jcamg__tejtd))
    tuow__mvgf['get_table_data'] = bodo.hiframes.table.get_table_data
    return jgqhc__cqj, tuow__mvgf


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    aipb__yna = tuple(unwrap_typeref(data_types.types[uiytg__xkl]) for
        uiytg__xkl in range(len(data_types.types)))
    tcb__fyu = bodo.TableType(aipb__yna)
    tuow__mvgf = {'table_type': tcb__fyu}
    jgqhc__cqj = 'def impl(data_types):\n'
    jgqhc__cqj += '  py_table = init_table(table_type, False)\n'
    jgqhc__cqj += '  py_table = set_table_len(py_table, 1)\n'
    for ntkh__haoa, mwq__jrze in tcb__fyu.type_to_blk.items():
        tuow__mvgf[f'typ_list_{mwq__jrze}'] = types.List(ntkh__haoa)
        tuow__mvgf[f'typ_{mwq__jrze}'] = ntkh__haoa
        smqv__sjtf = len(tcb__fyu.block_to_arr_ind[mwq__jrze])
        jgqhc__cqj += f"""  arr_list_{mwq__jrze} = alloc_list_like(typ_list_{mwq__jrze}, {smqv__sjtf}, False)
"""
        jgqhc__cqj += f'  for i in range(len(arr_list_{mwq__jrze})):\n'
        jgqhc__cqj += (
            f'    arr_list_{mwq__jrze}[i] = alloc_type(1, typ_{mwq__jrze}, (-1,))\n'
            )
        jgqhc__cqj += (
            f'  py_table = set_table_block(py_table, arr_list_{mwq__jrze}, {mwq__jrze})\n'
            )
    jgqhc__cqj += '  return py_table\n'
    tuow__mvgf.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    ibeka__leb = {}
    exec(jgqhc__cqj, tuow__mvgf, ibeka__leb)
    return ibeka__leb['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    ssqz__sibhn = agg_node.in_vars[0].name
    xwjs__hzqz, vrq__llxly, ignp__txxgl = block_use_map[ssqz__sibhn]
    if vrq__llxly or ignp__txxgl:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        ohmqs__pbkna, qwp__eircv, hagvg__lexw = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if qwp__eircv or hagvg__lexw:
            ohmqs__pbkna = set(range(agg_node.n_out_table_arrays))
    else:
        ohmqs__pbkna = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            ohmqs__pbkna = {0}
    olb__uuxxu = set(uiytg__xkl for uiytg__xkl in agg_node.in_key_inds if 
        uiytg__xkl < agg_node.n_in_table_arrays)
    cdf__wld = set(agg_node.gb_info_out[uiytg__xkl][0] for uiytg__xkl in
        ohmqs__pbkna if uiytg__xkl in agg_node.gb_info_out and agg_node.
        gb_info_out[uiytg__xkl][0] is not None)
    cdf__wld |= olb__uuxxu | xwjs__hzqz
    rwmo__inf = len(set(range(agg_node.n_in_table_arrays)) - cdf__wld) == 0
    block_use_map[ssqz__sibhn] = cdf__wld, rwmo__inf, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    rodho__nqs = agg_node.n_out_table_arrays
    nqyyr__lwxe = agg_node.out_vars[0].name
    laxhw__tyhmb = _find_used_columns(nqyyr__lwxe, rodho__nqs,
        column_live_map, equiv_vars)
    if laxhw__tyhmb is None:
        return False
    rtq__cqyr = set(range(rodho__nqs)) - laxhw__tyhmb
    nlree__gnkp = len(rtq__cqyr - agg_node.dead_out_inds) != 0
    if nlree__gnkp:
        agg_node.dead_out_inds.update(rtq__cqyr)
        agg_node.update_dead_col_info()
    return nlree__gnkp


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for hux__jzkl in block.body:
            if is_call_assign(hux__jzkl) and find_callname(f_ir, hux__jzkl.
                value) == ('len', 'builtins') and hux__jzkl.value.args[0
                ].name == f_ir.arg_names[0]:
                lwx__qdwoj = get_definition(f_ir, hux__jzkl.value.func)
                lwx__qdwoj.name = 'dummy_agg_count'
                lwx__qdwoj.value = dummy_agg_count
    wkyh__gdbkg = get_name_var_table(f_ir.blocks)
    icd__bad = {}
    for name, mrbi__hobi in wkyh__gdbkg.items():
        icd__bad[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, icd__bad)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    uarse__yuxiz = numba.core.compiler.Flags()
    uarse__yuxiz.nrt = True
    wcrq__dcoe = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, uarse__yuxiz)
    wcrq__dcoe.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, rvn__hnb, calltypes, mrbi__hobi = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    iiku__pefr = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    efg__smpzp = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    fpbeh__tactq = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    twhvi__pjqbo = fpbeh__tactq(typemap, calltypes)
    pm = efg__smpzp(typingctx, targetctx, None, f_ir, typemap, rvn__hnb,
        calltypes, twhvi__pjqbo, {}, uarse__yuxiz, None)
    azmz__vvh = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = efg__smpzp(typingctx, targetctx, None, f_ir, typemap, rvn__hnb,
        calltypes, twhvi__pjqbo, {}, uarse__yuxiz, azmz__vvh)
    iskpx__uwuz = numba.core.typed_passes.InlineOverloads()
    iskpx__uwuz.run_pass(pm)
    djeen__aiz = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    djeen__aiz.run()
    for block in f_ir.blocks.values():
        for hux__jzkl in block.body:
            if is_assign(hux__jzkl) and isinstance(hux__jzkl.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[hux__jzkl.target.name],
                SeriesType):
                ntkh__haoa = typemap.pop(hux__jzkl.target.name)
                typemap[hux__jzkl.target.name] = ntkh__haoa.data
            if is_call_assign(hux__jzkl) and find_callname(f_ir, hux__jzkl.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[hux__jzkl.target.name].remove(hux__jzkl.value
                    )
                hux__jzkl.value = hux__jzkl.value.args[0]
                f_ir._definitions[hux__jzkl.target.name].append(hux__jzkl.value
                    )
            if is_call_assign(hux__jzkl) and find_callname(f_ir, hux__jzkl.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[hux__jzkl.target.name].remove(hux__jzkl.value
                    )
                hux__jzkl.value = ir.Const(False, hux__jzkl.loc)
                f_ir._definitions[hux__jzkl.target.name].append(hux__jzkl.value
                    )
            if is_call_assign(hux__jzkl) and find_callname(f_ir, hux__jzkl.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[hux__jzkl.target.name].remove(hux__jzkl.value
                    )
                hux__jzkl.value = ir.Const(False, hux__jzkl.loc)
                f_ir._definitions[hux__jzkl.target.name].append(hux__jzkl.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    rqzu__fjrl = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, iiku__pefr)
    rqzu__fjrl.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    ccs__pfw = numba.core.compiler.StateDict()
    ccs__pfw.func_ir = f_ir
    ccs__pfw.typemap = typemap
    ccs__pfw.calltypes = calltypes
    ccs__pfw.typingctx = typingctx
    ccs__pfw.targetctx = targetctx
    ccs__pfw.return_type = rvn__hnb
    numba.core.rewrites.rewrite_registry.apply('after-inference', ccs__pfw)
    kyxy__nbr = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        rvn__hnb, typingctx, targetctx, iiku__pefr, uarse__yuxiz, {})
    kyxy__nbr.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            ajoso__rugw = ctypes.pythonapi.PyCell_Get
            ajoso__rugw.restype = ctypes.py_object
            ajoso__rugw.argtypes = ctypes.py_object,
            cjg__fpnsu = tuple(ajoso__rugw(ipalj__hxr) for ipalj__hxr in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            cjg__fpnsu = closure.items
        assert len(code.co_freevars) == len(cjg__fpnsu)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, cjg__fpnsu
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
        sie__zqgsf = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (sie__zqgsf,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        cph__tmg, arr_var = _rm_arg_agg_block(block, pm.typemap)
        ydq__uxvr = -1
        for uiytg__xkl, hux__jzkl in enumerate(cph__tmg):
            if isinstance(hux__jzkl, numba.parfors.parfor.Parfor):
                assert ydq__uxvr == -1, 'only one parfor for aggregation function'
                ydq__uxvr = uiytg__xkl
        parfor = None
        if ydq__uxvr != -1:
            parfor = cph__tmg[ydq__uxvr]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = cph__tmg[:ydq__uxvr] + parfor.init_block.body
        eval_nodes = cph__tmg[ydq__uxvr + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for hux__jzkl in init_nodes:
            if is_assign(hux__jzkl) and hux__jzkl.target.name in redvars:
                ind = redvars.index(hux__jzkl.target.name)
                reduce_vars[ind] = hux__jzkl.target
        var_types = [pm.typemap[thxo__xfrn] for thxo__xfrn in redvars]
        azgo__jxa = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        iez__ukvuk = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        olcak__fmktv = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(olcak__fmktv)
        self.all_update_funcs.append(iez__ukvuk)
        self.all_combine_funcs.append(azgo__jxa)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        qktmq__jhys = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        zrhnu__dwqk = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        teup__kuool = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        uoo__tsip = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets)
        return (self.all_vartypes, qktmq__jhys, zrhnu__dwqk, teup__kuool,
            uoo__tsip)


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
    krt__qbm = []
    for t, ufaqm__pbehj in zip(in_col_types, agg_func):
        krt__qbm.append((t, ufaqm__pbehj))
    erojo__oxk = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    lmr__qoqwv = GeneralUDFGenerator()
    for in_col_typ, func in krt__qbm:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            erojo__oxk.add_udf(in_col_typ, func)
        except:
            lmr__qoqwv.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = erojo__oxk.gen_all_func()
    general_udf_funcs = lmr__qoqwv.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    vvgdn__svhps = compute_use_defs(parfor.loop_body)
    rdcu__qkvf = set()
    for hxgm__pvq in vvgdn__svhps.usemap.values():
        rdcu__qkvf |= hxgm__pvq
    uajo__gfx = set()
    for hxgm__pvq in vvgdn__svhps.defmap.values():
        uajo__gfx |= hxgm__pvq
    qbb__jgj = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    qbb__jgj.body = eval_nodes
    ahg__qezrw = compute_use_defs({(0): qbb__jgj})
    xhp__ainh = ahg__qezrw.usemap[0]
    pcq__yrcg = set()
    hqwtl__fox = []
    vqbcx__vork = []
    for hux__jzkl in reversed(init_nodes):
        bsee__awhdl = {thxo__xfrn.name for thxo__xfrn in hux__jzkl.list_vars()}
        if is_assign(hux__jzkl):
            thxo__xfrn = hux__jzkl.target.name
            bsee__awhdl.remove(thxo__xfrn)
            if (thxo__xfrn in rdcu__qkvf and thxo__xfrn not in pcq__yrcg and
                thxo__xfrn not in xhp__ainh and thxo__xfrn not in uajo__gfx):
                vqbcx__vork.append(hux__jzkl)
                rdcu__qkvf |= bsee__awhdl
                uajo__gfx.add(thxo__xfrn)
                continue
        pcq__yrcg |= bsee__awhdl
        hqwtl__fox.append(hux__jzkl)
    vqbcx__vork.reverse()
    hqwtl__fox.reverse()
    imta__zjerf = min(parfor.loop_body.keys())
    xve__dwanc = parfor.loop_body[imta__zjerf]
    xve__dwanc.body = vqbcx__vork + xve__dwanc.body
    return hqwtl__fox


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    fdwu__xzw = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    wuhzm__xsxto = set()
    elwv__fmwrb = []
    for hux__jzkl in init_nodes:
        if is_assign(hux__jzkl) and isinstance(hux__jzkl.value, ir.Global
            ) and isinstance(hux__jzkl.value.value, pytypes.FunctionType
            ) and hux__jzkl.value.value in fdwu__xzw:
            wuhzm__xsxto.add(hux__jzkl.target.name)
        elif is_call_assign(hux__jzkl
            ) and hux__jzkl.value.func.name in wuhzm__xsxto:
            pass
        else:
            elwv__fmwrb.append(hux__jzkl)
    init_nodes = elwv__fmwrb
    wxudg__fcur = types.Tuple(var_types)
    gmc__lejds = lambda : None
    f_ir = compile_to_numba_ir(gmc__lejds, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    ftf__klfeb = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    cai__zfb = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), ftf__klfeb, loc
        )
    block.body = block.body[-2:]
    block.body = init_nodes + [cai__zfb] + block.body
    block.body[-2].value.value = ftf__klfeb
    pwzq__jdq = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        wxudg__fcur, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    ayw__ojhet = numba.core.target_extension.dispatcher_registry[cpu_target](
        gmc__lejds)
    ayw__ojhet.add_overload(pwzq__jdq)
    return ayw__ojhet


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    zyzo__tecr = len(update_funcs)
    oksoz__yjox = len(in_col_types)
    jgqhc__cqj = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for gjyml__epgl in range(zyzo__tecr):
        qmd__ypiz = ', '.join(['redvar_arrs[{}][w_ind]'.format(uiytg__xkl) for
            uiytg__xkl in range(redvar_offsets[gjyml__epgl], redvar_offsets
            [gjyml__epgl + 1])])
        if qmd__ypiz:
            jgqhc__cqj += ('  {} = update_vars_{}({},  data_in[{}][i])\n'.
                format(qmd__ypiz, gjyml__epgl, qmd__ypiz, 0 if oksoz__yjox ==
                1 else gjyml__epgl))
    jgqhc__cqj += '  return\n'
    apra__zoc = {}
    for uiytg__xkl, ufaqm__pbehj in enumerate(update_funcs):
        apra__zoc['update_vars_{}'.format(uiytg__xkl)] = ufaqm__pbehj
    ibeka__leb = {}
    exec(jgqhc__cqj, apra__zoc, ibeka__leb)
    muq__tqen = ibeka__leb['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(muq__tqen)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    ivmsj__hdpae = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = ivmsj__hdpae, ivmsj__hdpae, types.intp, types.intp
    qbhvn__yoww = len(redvar_offsets) - 1
    jgqhc__cqj = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for gjyml__epgl in range(qbhvn__yoww):
        qmd__ypiz = ', '.join(['redvar_arrs[{}][w_ind]'.format(uiytg__xkl) for
            uiytg__xkl in range(redvar_offsets[gjyml__epgl], redvar_offsets
            [gjyml__epgl + 1])])
        iwt__cib = ', '.join(['recv_arrs[{}][i]'.format(uiytg__xkl) for
            uiytg__xkl in range(redvar_offsets[gjyml__epgl], redvar_offsets
            [gjyml__epgl + 1])])
        if iwt__cib:
            jgqhc__cqj += '  {} = combine_vars_{}({}, {})\n'.format(qmd__ypiz,
                gjyml__epgl, qmd__ypiz, iwt__cib)
    jgqhc__cqj += '  return\n'
    apra__zoc = {}
    for uiytg__xkl, ufaqm__pbehj in enumerate(combine_funcs):
        apra__zoc['combine_vars_{}'.format(uiytg__xkl)] = ufaqm__pbehj
    ibeka__leb = {}
    exec(jgqhc__cqj, apra__zoc, ibeka__leb)
    nue__gjc = ibeka__leb['combine_all_f']
    f_ir = compile_to_numba_ir(nue__gjc, apra__zoc)
    teup__kuool = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    ayw__ojhet = numba.core.target_extension.dispatcher_registry[cpu_target](
        nue__gjc)
    ayw__ojhet.add_overload(teup__kuool)
    return ayw__ojhet


def gen_all_eval_func(eval_funcs, redvar_offsets):
    qbhvn__yoww = len(redvar_offsets) - 1
    jgqhc__cqj = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for gjyml__epgl in range(qbhvn__yoww):
        qmd__ypiz = ', '.join(['redvar_arrs[{}][j]'.format(uiytg__xkl) for
            uiytg__xkl in range(redvar_offsets[gjyml__epgl], redvar_offsets
            [gjyml__epgl + 1])])
        jgqhc__cqj += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            gjyml__epgl, gjyml__epgl, qmd__ypiz)
    jgqhc__cqj += '  return\n'
    apra__zoc = {}
    for uiytg__xkl, ufaqm__pbehj in enumerate(eval_funcs):
        apra__zoc['eval_vars_{}'.format(uiytg__xkl)] = ufaqm__pbehj
    ibeka__leb = {}
    exec(jgqhc__cqj, apra__zoc, ibeka__leb)
    okd__jytbw = ibeka__leb['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(okd__jytbw)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    jcx__eadxg = len(var_types)
    maz__pwzhc = [f'in{uiytg__xkl}' for uiytg__xkl in range(jcx__eadxg)]
    wxudg__fcur = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    hdah__fdfr = wxudg__fcur(0)
    jgqhc__cqj = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        maz__pwzhc))
    ibeka__leb = {}
    exec(jgqhc__cqj, {'_zero': hdah__fdfr}, ibeka__leb)
    duwu__fuzjb = ibeka__leb['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(duwu__fuzjb, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': hdah__fdfr}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    dhxx__nga = []
    for uiytg__xkl, thxo__xfrn in enumerate(reduce_vars):
        dhxx__nga.append(ir.Assign(block.body[uiytg__xkl].target,
            thxo__xfrn, thxo__xfrn.loc))
        for cwno__fwrr in thxo__xfrn.versioned_names:
            dhxx__nga.append(ir.Assign(thxo__xfrn, ir.Var(thxo__xfrn.scope,
                cwno__fwrr, thxo__xfrn.loc), thxo__xfrn.loc))
    block.body = block.body[:jcx__eadxg] + dhxx__nga + eval_nodes
    olcak__fmktv = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        wxudg__fcur, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    ayw__ojhet = numba.core.target_extension.dispatcher_registry[cpu_target](
        duwu__fuzjb)
    ayw__ojhet.add_overload(olcak__fmktv)
    return ayw__ojhet


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    jcx__eadxg = len(redvars)
    vnkag__ysh = [f'v{uiytg__xkl}' for uiytg__xkl in range(jcx__eadxg)]
    maz__pwzhc = [f'in{uiytg__xkl}' for uiytg__xkl in range(jcx__eadxg)]
    jgqhc__cqj = 'def agg_combine({}):\n'.format(', '.join(vnkag__ysh +
        maz__pwzhc))
    udnar__buzox = wrap_parfor_blocks(parfor)
    qehng__ooam = find_topo_order(udnar__buzox)
    qehng__ooam = qehng__ooam[1:]
    unwrap_parfor_blocks(parfor)
    cdmna__jgq = {}
    hhij__neilq = []
    for bwtve__dun in qehng__ooam:
        sql__uadfm = parfor.loop_body[bwtve__dun]
        for hux__jzkl in sql__uadfm.body:
            if is_assign(hux__jzkl) and hux__jzkl.target.name in redvars:
                sus__hpt = hux__jzkl.target.name
                ind = redvars.index(sus__hpt)
                if ind in hhij__neilq:
                    continue
                if len(f_ir._definitions[sus__hpt]) == 2:
                    var_def = f_ir._definitions[sus__hpt][0]
                    jgqhc__cqj += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[sus__hpt][1]
                    jgqhc__cqj += _match_reduce_def(var_def, f_ir, ind)
    jgqhc__cqj += '    return {}'.format(', '.join(['v{}'.format(uiytg__xkl
        ) for uiytg__xkl in range(jcx__eadxg)]))
    ibeka__leb = {}
    exec(jgqhc__cqj, {}, ibeka__leb)
    qxnnm__ghog = ibeka__leb['agg_combine']
    arg_typs = tuple(2 * var_types)
    apra__zoc = {'numba': numba, 'bodo': bodo, 'np': np}
    apra__zoc.update(cdmna__jgq)
    f_ir = compile_to_numba_ir(qxnnm__ghog, apra__zoc, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    wxudg__fcur = pm.typemap[block.body[-1].value.name]
    azgo__jxa = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        wxudg__fcur, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    ayw__ojhet = numba.core.target_extension.dispatcher_registry[cpu_target](
        qxnnm__ghog)
    ayw__ojhet.add_overload(azgo__jxa)
    return ayw__ojhet


def _match_reduce_def(var_def, f_ir, ind):
    jgqhc__cqj = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        jgqhc__cqj = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        mlr__qhf = guard(find_callname, f_ir, var_def)
        if mlr__qhf == ('min', 'builtins'):
            jgqhc__cqj = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if mlr__qhf == ('max', 'builtins'):
            jgqhc__cqj = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return jgqhc__cqj


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    jcx__eadxg = len(redvars)
    nqfyo__ziy = 1
    in_vars = []
    for uiytg__xkl in range(nqfyo__ziy):
        glf__hqr = ir.Var(arr_var.scope, f'$input{uiytg__xkl}', arr_var.loc)
        in_vars.append(glf__hqr)
    kkxp__ijr = parfor.loop_nests[0].index_variable
    qmld__litp = [0] * jcx__eadxg
    for sql__uadfm in parfor.loop_body.values():
        zad__dzgji = []
        for hux__jzkl in sql__uadfm.body:
            if is_var_assign(hux__jzkl
                ) and hux__jzkl.value.name == kkxp__ijr.name:
                continue
            if is_getitem(hux__jzkl
                ) and hux__jzkl.value.value.name == arr_var.name:
                hux__jzkl.value = in_vars[0]
            if is_call_assign(hux__jzkl) and guard(find_callname, pm.
                func_ir, hux__jzkl.value) == ('isna', 'bodo.libs.array_kernels'
                ) and hux__jzkl.value.args[0].name == arr_var.name:
                hux__jzkl.value = ir.Const(False, hux__jzkl.target.loc)
            if is_assign(hux__jzkl) and hux__jzkl.target.name in redvars:
                ind = redvars.index(hux__jzkl.target.name)
                qmld__litp[ind] = hux__jzkl.target
            zad__dzgji.append(hux__jzkl)
        sql__uadfm.body = zad__dzgji
    vnkag__ysh = ['v{}'.format(uiytg__xkl) for uiytg__xkl in range(jcx__eadxg)]
    maz__pwzhc = ['in{}'.format(uiytg__xkl) for uiytg__xkl in range(nqfyo__ziy)
        ]
    jgqhc__cqj = 'def agg_update({}):\n'.format(', '.join(vnkag__ysh +
        maz__pwzhc))
    jgqhc__cqj += '    __update_redvars()\n'
    jgqhc__cqj += '    return {}'.format(', '.join(['v{}'.format(uiytg__xkl
        ) for uiytg__xkl in range(jcx__eadxg)]))
    ibeka__leb = {}
    exec(jgqhc__cqj, {}, ibeka__leb)
    qmiud__hru = ibeka__leb['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * nqfyo__ziy)
    f_ir = compile_to_numba_ir(qmiud__hru, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    pdu__ejmj = f_ir.blocks.popitem()[1].body
    wxudg__fcur = pm.typemap[pdu__ejmj[-1].value.name]
    udnar__buzox = wrap_parfor_blocks(parfor)
    qehng__ooam = find_topo_order(udnar__buzox)
    qehng__ooam = qehng__ooam[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    xve__dwanc = f_ir.blocks[qehng__ooam[0]]
    uan__jtp = f_ir.blocks[qehng__ooam[-1]]
    pfliz__qbul = pdu__ejmj[:jcx__eadxg + nqfyo__ziy]
    if jcx__eadxg > 1:
        cxw__ieiit = pdu__ejmj[-3:]
        assert is_assign(cxw__ieiit[0]) and isinstance(cxw__ieiit[0].value,
            ir.Expr) and cxw__ieiit[0].value.op == 'build_tuple'
    else:
        cxw__ieiit = pdu__ejmj[-2:]
    for uiytg__xkl in range(jcx__eadxg):
        ndxzq__lwj = pdu__ejmj[uiytg__xkl].target
        hjrh__dcdso = ir.Assign(ndxzq__lwj, qmld__litp[uiytg__xkl],
            ndxzq__lwj.loc)
        pfliz__qbul.append(hjrh__dcdso)
    for uiytg__xkl in range(jcx__eadxg, jcx__eadxg + nqfyo__ziy):
        ndxzq__lwj = pdu__ejmj[uiytg__xkl].target
        hjrh__dcdso = ir.Assign(ndxzq__lwj, in_vars[uiytg__xkl - jcx__eadxg
            ], ndxzq__lwj.loc)
        pfliz__qbul.append(hjrh__dcdso)
    xve__dwanc.body = pfliz__qbul + xve__dwanc.body
    nmda__mdpyl = []
    for uiytg__xkl in range(jcx__eadxg):
        ndxzq__lwj = pdu__ejmj[uiytg__xkl].target
        hjrh__dcdso = ir.Assign(qmld__litp[uiytg__xkl], ndxzq__lwj,
            ndxzq__lwj.loc)
        nmda__mdpyl.append(hjrh__dcdso)
    uan__jtp.body += nmda__mdpyl + cxw__ieiit
    fdbpe__xkbut = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        wxudg__fcur, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    ayw__ojhet = numba.core.target_extension.dispatcher_registry[cpu_target](
        qmiud__hru)
    ayw__ojhet.add_overload(fdbpe__xkbut)
    return ayw__ojhet


def _rm_arg_agg_block(block, typemap):
    cph__tmg = []
    arr_var = None
    for uiytg__xkl, hux__jzkl in enumerate(block.body):
        if is_assign(hux__jzkl) and isinstance(hux__jzkl.value, ir.Arg):
            arr_var = hux__jzkl.target
            yht__srf = typemap[arr_var.name]
            if not isinstance(yht__srf, types.ArrayCompatible):
                cph__tmg += block.body[uiytg__xkl + 1:]
                break
            hau__uvkbj = block.body[uiytg__xkl + 1]
            assert is_assign(hau__uvkbj) and isinstance(hau__uvkbj.value,
                ir.Expr
                ) and hau__uvkbj.value.op == 'getattr' and hau__uvkbj.value.attr == 'shape' and hau__uvkbj.value.value.name == arr_var.name
            bjmy__nij = hau__uvkbj.target
            jai__fgct = block.body[uiytg__xkl + 2]
            assert is_assign(jai__fgct) and isinstance(jai__fgct.value, ir.Expr
                ) and jai__fgct.value.op == 'static_getitem' and jai__fgct.value.value.name == bjmy__nij.name
            cph__tmg += block.body[uiytg__xkl + 3:]
            break
        cph__tmg.append(hux__jzkl)
    return cph__tmg, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    udnar__buzox = wrap_parfor_blocks(parfor)
    qehng__ooam = find_topo_order(udnar__buzox)
    qehng__ooam = qehng__ooam[1:]
    unwrap_parfor_blocks(parfor)
    for bwtve__dun in reversed(qehng__ooam):
        for hux__jzkl in reversed(parfor.loop_body[bwtve__dun].body):
            if isinstance(hux__jzkl, ir.Assign) and (hux__jzkl.target.name in
                parfor_params or hux__jzkl.target.name in var_to_param):
                xeoox__tfd = hux__jzkl.target.name
                rhs = hux__jzkl.value
                wdyqz__too = (xeoox__tfd if xeoox__tfd in parfor_params else
                    var_to_param[xeoox__tfd])
                kiaq__uujhg = []
                if isinstance(rhs, ir.Var):
                    kiaq__uujhg = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    kiaq__uujhg = [thxo__xfrn.name for thxo__xfrn in
                        hux__jzkl.value.list_vars()]
                param_uses[wdyqz__too].extend(kiaq__uujhg)
                for thxo__xfrn in kiaq__uujhg:
                    var_to_param[thxo__xfrn] = wdyqz__too
            if isinstance(hux__jzkl, Parfor):
                get_parfor_reductions(hux__jzkl, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for yjqx__uea, kiaq__uujhg in param_uses.items():
        if yjqx__uea in kiaq__uujhg and yjqx__uea not in reduce_varnames:
            reduce_varnames.append(yjqx__uea)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
