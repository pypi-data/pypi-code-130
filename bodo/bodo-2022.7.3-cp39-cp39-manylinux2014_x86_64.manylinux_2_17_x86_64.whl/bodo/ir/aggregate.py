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
        rsu__stam = func.signature
        if rsu__stam == types.none(types.voidptr):
            clwsm__suyxi = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer()])
            jsour__lwy = cgutils.get_or_insert_function(builder.module,
                clwsm__suyxi, sym._literal_value)
            builder.call(jsour__lwy, [context.get_constant_null(rsu__stam.
                args[0])])
        elif rsu__stam == types.none(types.int64, types.voidptr, types.voidptr
            ):
            clwsm__suyxi = lir.FunctionType(lir.VoidType(), [lir.IntType(64
                ), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            jsour__lwy = cgutils.get_or_insert_function(builder.module,
                clwsm__suyxi, sym._literal_value)
            builder.call(jsour__lwy, [context.get_constant(types.int64, 0),
                context.get_constant_null(rsu__stam.args[1]), context.
                get_constant_null(rsu__stam.args[2])])
        else:
            clwsm__suyxi = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)
                .as_pointer()])
            jsour__lwy = cgutils.get_or_insert_function(builder.module,
                clwsm__suyxi, sym._literal_value)
            builder.call(jsour__lwy, [context.get_constant_null(rsu__stam.
                args[0]), context.get_constant_null(rsu__stam.args[1]),
                context.get_constant_null(rsu__stam.args[2])])
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
        ykgmy__jtaqz = True
        ftp__kvgq = 1
        ccpl__ittse = -1
        if isinstance(rhs, ir.Expr):
            for zsmtk__vuny in rhs.kws:
                if func_name in list_cumulative:
                    if zsmtk__vuny[0] == 'skipna':
                        ykgmy__jtaqz = guard(find_const, func_ir,
                            zsmtk__vuny[1])
                        if not isinstance(ykgmy__jtaqz, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if zsmtk__vuny[0] == 'dropna':
                        ykgmy__jtaqz = guard(find_const, func_ir,
                            zsmtk__vuny[1])
                        if not isinstance(ykgmy__jtaqz, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            ftp__kvgq = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', ftp__kvgq)
            ftp__kvgq = guard(find_const, func_ir, ftp__kvgq)
        if func_name == 'head':
            ccpl__ittse = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(ccpl__ittse, int):
                ccpl__ittse = guard(find_const, func_ir, ccpl__ittse)
            if ccpl__ittse < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = ykgmy__jtaqz
        func.periods = ftp__kvgq
        func.head_n = ccpl__ittse
        if func_name == 'transform':
            kws = dict(rhs.kws)
            gwuat__qle = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            hlsca__uryic = typemap[gwuat__qle.name]
            xigzw__zylra = None
            if isinstance(hlsca__uryic, str):
                xigzw__zylra = hlsca__uryic
            elif is_overload_constant_str(hlsca__uryic):
                xigzw__zylra = get_overload_const_str(hlsca__uryic)
            elif bodo.utils.typing.is_builtin_function(hlsca__uryic):
                xigzw__zylra = bodo.utils.typing.get_builtin_function_name(
                    hlsca__uryic)
            if xigzw__zylra not in bodo.ir.aggregate.supported_transform_funcs[
                :]:
                raise BodoError(
                    f'unsupported transform function {xigzw__zylra}')
            func.transform_func = supported_agg_funcs.index(xigzw__zylra)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    gwuat__qle = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if gwuat__qle == '':
        hlsca__uryic = types.none
    else:
        hlsca__uryic = typemap[gwuat__qle.name]
    if is_overload_constant_dict(hlsca__uryic):
        vwlq__eok = get_overload_constant_dict(hlsca__uryic)
        zig__rqsgf = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in vwlq__eok.values()]
        return zig__rqsgf
    if hlsca__uryic == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(hlsca__uryic, types.BaseTuple) or is_overload_constant_list(
        hlsca__uryic):
        zig__rqsgf = []
        cdyc__xwt = 0
        if is_overload_constant_list(hlsca__uryic):
            dbfq__oxa = get_overload_const_list(hlsca__uryic)
        else:
            dbfq__oxa = hlsca__uryic.types
        for t in dbfq__oxa:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                zig__rqsgf.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(dbfq__oxa) > 1:
                    func.fname = '<lambda_' + str(cdyc__xwt) + '>'
                    cdyc__xwt += 1
                zig__rqsgf.append(func)
        return [zig__rqsgf]
    if is_overload_constant_str(hlsca__uryic):
        func_name = get_overload_const_str(hlsca__uryic)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(hlsca__uryic):
        func_name = bodo.utils.typing.get_builtin_function_name(hlsca__uryic)
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
        cdyc__xwt = 0
        zfwps__gux = []
        for awzc__ttjtd in f_val:
            func = get_agg_func_udf(func_ir, awzc__ttjtd, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{cdyc__xwt}>'
                cdyc__xwt += 1
            zfwps__gux.append(func)
        return zfwps__gux
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
    xigzw__zylra = code.co_name
    return xigzw__zylra


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
            srbsz__mhipq = types.DType(args[0])
            return signature(srbsz__mhipq, *args)


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
        return [kvzxq__lnh for kvzxq__lnh in self.in_vars if kvzxq__lnh is not
            None]

    def get_live_out_vars(self):
        return [kvzxq__lnh for kvzxq__lnh in self.out_vars if kvzxq__lnh is not
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
        bunv__gfvzr = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        gpsrw__tauw = list(get_index_data_arr_types(self.out_type.index))
        return bunv__gfvzr + gpsrw__tauw

    def update_dead_col_info(self):
        for alv__apfw in self.dead_out_inds:
            self.gb_info_out.pop(alv__apfw, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for fveum__gkjm, jxqa__mwlm in self.gb_info_in.copy().items():
            ngwi__grg = []
            for awzc__ttjtd, nfi__huikq in jxqa__mwlm:
                if nfi__huikq not in self.dead_out_inds:
                    ngwi__grg.append((awzc__ttjtd, nfi__huikq))
            if not ngwi__grg:
                if (fveum__gkjm is not None and fveum__gkjm not in self.
                    in_key_inds):
                    self.dead_in_inds.add(fveum__gkjm)
                self.gb_info_in.pop(fveum__gkjm)
            else:
                self.gb_info_in[fveum__gkjm] = ngwi__grg
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for vpmn__sdjcd in range(1, len(self.in_vars)):
                alv__apfw = self.n_in_table_arrays + vpmn__sdjcd - 1
                if alv__apfw in self.dead_in_inds:
                    self.in_vars[vpmn__sdjcd] = None
        else:
            for vpmn__sdjcd in range(len(self.in_vars)):
                if vpmn__sdjcd in self.dead_in_inds:
                    self.in_vars[vpmn__sdjcd] = None

    def __repr__(self):
        zqr__cclct = ', '.join(kvzxq__lnh.name for kvzxq__lnh in self.
            get_live_in_vars())
        bapm__xnqv = f'{self.df_in}{{{zqr__cclct}}}'
        qwy__wvjm = ', '.join(kvzxq__lnh.name for kvzxq__lnh in self.
            get_live_out_vars())
        ssfhw__alm = f'{self.df_out}{{{qwy__wvjm}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {bapm__xnqv} {ssfhw__alm}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({kvzxq__lnh.name for kvzxq__lnh in aggregate_node.
        get_live_in_vars()})
    def_set.update({kvzxq__lnh.name for kvzxq__lnh in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    ccv__ipix = agg_node.out_vars[0]
    if ccv__ipix is not None and ccv__ipix.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            tqjc__wuo = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(tqjc__wuo)
        else:
            agg_node.dead_out_inds.add(0)
    for vpmn__sdjcd in range(1, len(agg_node.out_vars)):
        kvzxq__lnh = agg_node.out_vars[vpmn__sdjcd]
        if kvzxq__lnh is not None and kvzxq__lnh.name not in lives:
            agg_node.out_vars[vpmn__sdjcd] = None
            alv__apfw = agg_node.n_out_table_arrays + vpmn__sdjcd - 1
            agg_node.dead_out_inds.add(alv__apfw)
    if all(kvzxq__lnh is None for kvzxq__lnh in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    jhdpi__bxt = {kvzxq__lnh.name for kvzxq__lnh in aggregate_node.
        get_live_out_vars()}
    return set(), jhdpi__bxt


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for vpmn__sdjcd in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[vpmn__sdjcd] is not None:
            aggregate_node.in_vars[vpmn__sdjcd] = replace_vars_inner(
                aggregate_node.in_vars[vpmn__sdjcd], var_dict)
    for vpmn__sdjcd in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[vpmn__sdjcd] is not None:
            aggregate_node.out_vars[vpmn__sdjcd] = replace_vars_inner(
                aggregate_node.out_vars[vpmn__sdjcd], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for vpmn__sdjcd in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[vpmn__sdjcd] is not None:
            aggregate_node.in_vars[vpmn__sdjcd] = visit_vars_inner(
                aggregate_node.in_vars[vpmn__sdjcd], callback, cbdata)
    for vpmn__sdjcd in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[vpmn__sdjcd] is not None:
            aggregate_node.out_vars[vpmn__sdjcd] = visit_vars_inner(
                aggregate_node.out_vars[vpmn__sdjcd], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    mvyz__bgt = []
    for ijhq__arty in aggregate_node.get_live_in_vars():
        hpgg__vywhg = equiv_set.get_shape(ijhq__arty)
        if hpgg__vywhg is not None:
            mvyz__bgt.append(hpgg__vywhg[0])
    if len(mvyz__bgt) > 1:
        equiv_set.insert_equiv(*mvyz__bgt)
    sic__jvtl = []
    mvyz__bgt = []
    for ijhq__arty in aggregate_node.get_live_out_vars():
        ezx__udmc = typemap[ijhq__arty.name]
        cfnxz__lrt = array_analysis._gen_shape_call(equiv_set, ijhq__arty,
            ezx__udmc.ndim, None, sic__jvtl)
        equiv_set.insert_equiv(ijhq__arty, cfnxz__lrt)
        mvyz__bgt.append(cfnxz__lrt[0])
        equiv_set.define(ijhq__arty, set())
    if len(mvyz__bgt) > 1:
        equiv_set.insert_equiv(*mvyz__bgt)
    return [], sic__jvtl


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    jkdhh__gym = aggregate_node.get_live_in_vars()
    kpt__qbd = aggregate_node.get_live_out_vars()
    apo__xtsh = Distribution.OneD
    for ijhq__arty in jkdhh__gym:
        apo__xtsh = Distribution(min(apo__xtsh.value, array_dists[
            ijhq__arty.name].value))
    xvwwn__fnfe = Distribution(min(apo__xtsh.value, Distribution.OneD_Var.
        value))
    for ijhq__arty in kpt__qbd:
        if ijhq__arty.name in array_dists:
            xvwwn__fnfe = Distribution(min(xvwwn__fnfe.value, array_dists[
                ijhq__arty.name].value))
    if xvwwn__fnfe != Distribution.OneD_Var:
        apo__xtsh = xvwwn__fnfe
    for ijhq__arty in jkdhh__gym:
        array_dists[ijhq__arty.name] = apo__xtsh
    for ijhq__arty in kpt__qbd:
        array_dists[ijhq__arty.name] = xvwwn__fnfe


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for ijhq__arty in agg_node.get_live_out_vars():
        definitions[ijhq__arty.name].append(agg_node)
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
    nsmln__nyf = agg_node.get_live_in_vars()
    ruhw__ecmi = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for kvzxq__lnh in (nsmln__nyf + ruhw__ecmi):
            if array_dists[kvzxq__lnh.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                kvzxq__lnh.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    zig__rqsgf = []
    func_out_types = []
    for nfi__huikq, (fveum__gkjm, func) in agg_node.gb_info_out.items():
        if fveum__gkjm is not None:
            t = agg_node.in_col_types[fveum__gkjm]
            in_col_typs.append(t)
        zig__rqsgf.append(func)
        func_out_types.append(out_col_typs[nfi__huikq])
    duihm__wfey = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for vpmn__sdjcd, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            duihm__wfey.update({f'in_cat_dtype_{vpmn__sdjcd}': in_col_typ})
    for vpmn__sdjcd, upynj__oeug in enumerate(out_col_typs):
        if isinstance(upynj__oeug, bodo.CategoricalArrayType):
            duihm__wfey.update({f'out_cat_dtype_{vpmn__sdjcd}': upynj__oeug})
    udf_func_struct = get_udf_func_struct(zig__rqsgf, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[kvzxq__lnh.name] if kvzxq__lnh is not None else
        types.none) for kvzxq__lnh in agg_node.out_vars]
    jztbd__nhd, rbuit__dkvc = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    duihm__wfey.update(rbuit__dkvc)
    duihm__wfey.update({'pd': pd, 'pre_alloc_string_array':
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
            duihm__wfey.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            duihm__wfey.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    ezt__ddut = {}
    exec(jztbd__nhd, {}, ezt__ddut)
    ocn__wukx = ezt__ddut['agg_top']
    eub__nzk = compile_to_numba_ir(ocn__wukx, duihm__wfey, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[kvzxq__lnh.
        name] for kvzxq__lnh in nsmln__nyf), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(eub__nzk, nsmln__nyf)
    rozcg__luokl = eub__nzk.body[-2].value.value
    hwq__dtic = eub__nzk.body[:-2]
    for vpmn__sdjcd, kvzxq__lnh in enumerate(ruhw__ecmi):
        gen_getitem(kvzxq__lnh, rozcg__luokl, vpmn__sdjcd, calltypes, hwq__dtic
            )
    return hwq__dtic


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        mczz__itza = IntDtype(t.dtype).name
        assert mczz__itza.endswith('Dtype()')
        mczz__itza = mczz__itza[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{mczz__itza}'))"
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
        gjl__nxazj = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {gjl__nxazj}_cat_dtype_{colnum})')
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
    qdry__alnv = udf_func_struct.var_typs
    kng__uwd = len(qdry__alnv)
    jztbd__nhd = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    jztbd__nhd += '    if is_null_pointer(in_table):\n'
    jztbd__nhd += '        return\n'
    jztbd__nhd += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qdry__alnv]), 
        ',' if len(qdry__alnv) == 1 else '')
    bbk__ittea = n_keys
    raov__kaaw = []
    redvar_offsets = []
    lcog__phptc = []
    if do_combine:
        for vpmn__sdjcd, awzc__ttjtd in enumerate(allfuncs):
            if awzc__ttjtd.ftype != 'udf':
                bbk__ittea += awzc__ttjtd.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(bbk__ittea, bbk__ittea +
                    awzc__ttjtd.n_redvars))
                bbk__ittea += awzc__ttjtd.n_redvars
                lcog__phptc.append(data_in_typs_[func_idx_to_in_col[
                    vpmn__sdjcd]])
                raov__kaaw.append(func_idx_to_in_col[vpmn__sdjcd] + n_keys)
    else:
        for vpmn__sdjcd, awzc__ttjtd in enumerate(allfuncs):
            if awzc__ttjtd.ftype != 'udf':
                bbk__ittea += awzc__ttjtd.ncols_post_shuffle
            else:
                redvar_offsets += list(range(bbk__ittea + 1, bbk__ittea + 1 +
                    awzc__ttjtd.n_redvars))
                bbk__ittea += awzc__ttjtd.n_redvars + 1
                lcog__phptc.append(data_in_typs_[func_idx_to_in_col[
                    vpmn__sdjcd]])
                raov__kaaw.append(func_idx_to_in_col[vpmn__sdjcd] + n_keys)
    assert len(redvar_offsets) == kng__uwd
    qvpxv__ldhoh = len(lcog__phptc)
    jup__yva = []
    for vpmn__sdjcd, t in enumerate(lcog__phptc):
        jup__yva.append(_gen_dummy_alloc(t, vpmn__sdjcd, True))
    jztbd__nhd += '    data_in_dummy = ({}{})\n'.format(','.join(jup__yva),
        ',' if len(lcog__phptc) == 1 else '')
    jztbd__nhd += """
    # initialize redvar cols
"""
    jztbd__nhd += '    init_vals = __init_func()\n'
    for vpmn__sdjcd in range(kng__uwd):
        jztbd__nhd += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(vpmn__sdjcd, redvar_offsets[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(redvar_arr_{})\n'.format(vpmn__sdjcd)
        jztbd__nhd += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            vpmn__sdjcd, vpmn__sdjcd)
    jztbd__nhd += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(vpmn__sdjcd) for vpmn__sdjcd in range(kng__uwd)]), ',' if 
        kng__uwd == 1 else '')
    jztbd__nhd += '\n'
    for vpmn__sdjcd in range(qvpxv__ldhoh):
        jztbd__nhd += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(vpmn__sdjcd, raov__kaaw[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(data_in_{})\n'.format(vpmn__sdjcd)
    jztbd__nhd += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(vpmn__sdjcd) for vpmn__sdjcd in range(qvpxv__ldhoh)]), ',' if
        qvpxv__ldhoh == 1 else '')
    jztbd__nhd += '\n'
    jztbd__nhd += '    for i in range(len(data_in_0)):\n'
    jztbd__nhd += '        w_ind = row_to_group[i]\n'
    jztbd__nhd += '        if w_ind != -1:\n'
    jztbd__nhd += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    ezt__ddut = {}
    exec(jztbd__nhd, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ezt__ddut)
    return ezt__ddut['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    qdry__alnv = udf_func_struct.var_typs
    kng__uwd = len(qdry__alnv)
    jztbd__nhd = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    jztbd__nhd += '    if is_null_pointer(in_table):\n'
    jztbd__nhd += '        return\n'
    jztbd__nhd += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qdry__alnv]), 
        ',' if len(qdry__alnv) == 1 else '')
    npktq__sxgf = n_keys
    oatrd__jvhm = n_keys
    pgfs__liprh = []
    amkr__iwvs = []
    for awzc__ttjtd in allfuncs:
        if awzc__ttjtd.ftype != 'udf':
            npktq__sxgf += awzc__ttjtd.ncols_pre_shuffle
            oatrd__jvhm += awzc__ttjtd.ncols_post_shuffle
        else:
            pgfs__liprh += list(range(npktq__sxgf, npktq__sxgf +
                awzc__ttjtd.n_redvars))
            amkr__iwvs += list(range(oatrd__jvhm + 1, oatrd__jvhm + 1 +
                awzc__ttjtd.n_redvars))
            npktq__sxgf += awzc__ttjtd.n_redvars
            oatrd__jvhm += 1 + awzc__ttjtd.n_redvars
    assert len(pgfs__liprh) == kng__uwd
    jztbd__nhd += """
    # initialize redvar cols
"""
    jztbd__nhd += '    init_vals = __init_func()\n'
    for vpmn__sdjcd in range(kng__uwd):
        jztbd__nhd += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(vpmn__sdjcd, amkr__iwvs[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(redvar_arr_{})\n'.format(vpmn__sdjcd)
        jztbd__nhd += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            vpmn__sdjcd, vpmn__sdjcd)
    jztbd__nhd += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(vpmn__sdjcd) for vpmn__sdjcd in range(kng__uwd)]), ',' if 
        kng__uwd == 1 else '')
    jztbd__nhd += '\n'
    for vpmn__sdjcd in range(kng__uwd):
        jztbd__nhd += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(vpmn__sdjcd, pgfs__liprh[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(recv_redvar_arr_{})\n'.format(vpmn__sdjcd)
    jztbd__nhd += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(vpmn__sdjcd) for vpmn__sdjcd in range(
        kng__uwd)]), ',' if kng__uwd == 1 else '')
    jztbd__nhd += '\n'
    if kng__uwd:
        jztbd__nhd += '    for i in range(len(recv_redvar_arr_0)):\n'
        jztbd__nhd += '        w_ind = row_to_group[i]\n'
        jztbd__nhd += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    ezt__ddut = {}
    exec(jztbd__nhd, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ezt__ddut)
    return ezt__ddut['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    qdry__alnv = udf_func_struct.var_typs
    kng__uwd = len(qdry__alnv)
    bbk__ittea = n_keys
    redvar_offsets = []
    ziido__lmugi = []
    wklux__rwau = []
    for vpmn__sdjcd, awzc__ttjtd in enumerate(allfuncs):
        if awzc__ttjtd.ftype != 'udf':
            bbk__ittea += awzc__ttjtd.ncols_post_shuffle
        else:
            ziido__lmugi.append(bbk__ittea)
            redvar_offsets += list(range(bbk__ittea + 1, bbk__ittea + 1 +
                awzc__ttjtd.n_redvars))
            bbk__ittea += 1 + awzc__ttjtd.n_redvars
            wklux__rwau.append(out_data_typs_[vpmn__sdjcd])
    assert len(redvar_offsets) == kng__uwd
    qvpxv__ldhoh = len(wklux__rwau)
    jztbd__nhd = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    jztbd__nhd += '    if is_null_pointer(table):\n'
    jztbd__nhd += '        return\n'
    jztbd__nhd += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qdry__alnv]), 
        ',' if len(qdry__alnv) == 1 else '')
    jztbd__nhd += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        wklux__rwau]), ',' if len(wklux__rwau) == 1 else '')
    for vpmn__sdjcd in range(kng__uwd):
        jztbd__nhd += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(vpmn__sdjcd, redvar_offsets[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(redvar_arr_{})\n'.format(vpmn__sdjcd)
    jztbd__nhd += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(vpmn__sdjcd) for vpmn__sdjcd in range(kng__uwd)]), ',' if 
        kng__uwd == 1 else '')
    jztbd__nhd += '\n'
    for vpmn__sdjcd in range(qvpxv__ldhoh):
        jztbd__nhd += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(vpmn__sdjcd, ziido__lmugi[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(data_out_{})\n'.format(vpmn__sdjcd)
    jztbd__nhd += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(vpmn__sdjcd) for vpmn__sdjcd in range(qvpxv__ldhoh)]), ',' if
        qvpxv__ldhoh == 1 else '')
    jztbd__nhd += '\n'
    jztbd__nhd += '    for i in range(len(data_out_0)):\n'
    jztbd__nhd += '        __eval_res(redvars, data_out, i)\n'
    ezt__ddut = {}
    exec(jztbd__nhd, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ezt__ddut)
    return ezt__ddut['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    bbk__ittea = n_keys
    lyho__qujl = []
    for vpmn__sdjcd, awzc__ttjtd in enumerate(allfuncs):
        if awzc__ttjtd.ftype == 'gen_udf':
            lyho__qujl.append(bbk__ittea)
            bbk__ittea += 1
        elif awzc__ttjtd.ftype != 'udf':
            bbk__ittea += awzc__ttjtd.ncols_post_shuffle
        else:
            bbk__ittea += awzc__ttjtd.n_redvars + 1
    jztbd__nhd = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    jztbd__nhd += '    if num_groups == 0:\n'
    jztbd__nhd += '        return\n'
    for vpmn__sdjcd, func in enumerate(udf_func_struct.general_udf_funcs):
        jztbd__nhd += '    # col {}\n'.format(vpmn__sdjcd)
        jztbd__nhd += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(lyho__qujl[vpmn__sdjcd], vpmn__sdjcd))
        jztbd__nhd += '    incref(out_col)\n'
        jztbd__nhd += '    for j in range(num_groups):\n'
        jztbd__nhd += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(vpmn__sdjcd, vpmn__sdjcd))
        jztbd__nhd += '        incref(in_col)\n'
        jztbd__nhd += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(vpmn__sdjcd))
    duihm__wfey = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    fps__oai = 0
    for vpmn__sdjcd, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[fps__oai]
        duihm__wfey['func_{}'.format(fps__oai)] = func
        duihm__wfey['in_col_{}_typ'.format(fps__oai)] = in_col_typs[
            func_idx_to_in_col[vpmn__sdjcd]]
        duihm__wfey['out_col_{}_typ'.format(fps__oai)] = out_col_typs[
            vpmn__sdjcd]
        fps__oai += 1
    ezt__ddut = {}
    exec(jztbd__nhd, duihm__wfey, ezt__ddut)
    awzc__ttjtd = ezt__ddut['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    wutzc__fev = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(wutzc__fev, nopython=True)(awzc__ttjtd)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    yfyaq__phj = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        mynay__blp = []
        if agg_node.in_vars[0] is not None:
            mynay__blp.append('arg0')
        for vpmn__sdjcd in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if vpmn__sdjcd not in agg_node.dead_in_inds:
                mynay__blp.append(f'arg{vpmn__sdjcd}')
    else:
        mynay__blp = [f'arg{vpmn__sdjcd}' for vpmn__sdjcd, kvzxq__lnh in
            enumerate(agg_node.in_vars) if kvzxq__lnh is not None]
    jztbd__nhd = f"def agg_top({', '.join(mynay__blp)}):\n"
    ywqb__qeyq = []
    if agg_node.is_in_table_format:
        ywqb__qeyq = agg_node.in_key_inds + [fveum__gkjm for fveum__gkjm,
            cdf__asy in agg_node.gb_info_out.values() if fveum__gkjm is not
            None]
        if agg_node.input_has_index:
            ywqb__qeyq.append(agg_node.n_in_cols - 1)
        nli__iuh = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        lkx__depe = []
        for vpmn__sdjcd in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if vpmn__sdjcd in agg_node.dead_in_inds:
                lkx__depe.append('None')
            else:
                lkx__depe.append(f'arg{vpmn__sdjcd}')
        cwub__avm = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        jztbd__nhd += f"""    table = py_data_to_cpp_table({cwub__avm}, ({', '.join(lkx__depe)}{nli__iuh}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        prwbj__iyni = [f'arg{vpmn__sdjcd}' for vpmn__sdjcd in agg_node.
            in_key_inds]
        nerg__eluvb = [f'arg{fveum__gkjm}' for fveum__gkjm, cdf__asy in
            agg_node.gb_info_out.values() if fveum__gkjm is not None]
        onb__yoa = prwbj__iyni + nerg__eluvb
        if agg_node.input_has_index:
            onb__yoa.append(f'arg{len(agg_node.in_vars) - 1}')
        jztbd__nhd += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({vnpuz__xnfs})' for vnpuz__xnfs in onb__yoa))
        jztbd__nhd += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    hfaj__xcvi = []
    func_idx_to_in_col = []
    xtv__vctlm = []
    ykgmy__jtaqz = False
    lner__lvd = 1
    ccpl__ittse = -1
    rlhmu__qjarb = 0
    eeus__nub = 0
    zig__rqsgf = [func for cdf__asy, func in agg_node.gb_info_out.values()]
    for knrx__boas, func in enumerate(zig__rqsgf):
        hfaj__xcvi.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            rlhmu__qjarb += 1
        if hasattr(func, 'skipdropna'):
            ykgmy__jtaqz = func.skipdropna
        if func.ftype == 'shift':
            lner__lvd = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            eeus__nub = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            ccpl__ittse = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(knrx__boas)
        if func.ftype == 'udf':
            xtv__vctlm.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            xtv__vctlm.append(0)
            do_combine = False
    hfaj__xcvi.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if rlhmu__qjarb > 0:
        if rlhmu__qjarb != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    lauvy__fjhde = []
    if udf_func_struct is not None:
        uwz__zstq = next_label()
        if udf_func_struct.regular_udfs:
            wutzc__fev = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            irmm__vsw = numba.cfunc(wutzc__fev, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, uwz__zstq))
            uvllv__ffay = numba.cfunc(wutzc__fev, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, uwz__zstq))
            gief__mpqt = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, uwz__zstq))
            udf_func_struct.set_regular_cfuncs(irmm__vsw, uvllv__ffay,
                gief__mpqt)
            for fcju__rmj in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[fcju__rmj.native_name] = fcju__rmj
                gb_agg_cfunc_addr[fcju__rmj.native_name] = fcju__rmj.address
        if udf_func_struct.general_udfs:
            odeat__epp = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                uwz__zstq)
            udf_func_struct.set_general_cfunc(odeat__epp)
        qdry__alnv = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        hfl__ccv = 0
        vpmn__sdjcd = 0
        for cli__rqxt, awzc__ttjtd in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if awzc__ttjtd.ftype in ('udf', 'gen_udf'):
                lauvy__fjhde.append(out_col_typs[cli__rqxt])
                for bjbpm__fvw in range(hfl__ccv, hfl__ccv + xtv__vctlm[
                    vpmn__sdjcd]):
                    lauvy__fjhde.append(dtype_to_array_type(qdry__alnv[
                        bjbpm__fvw]))
                hfl__ccv += xtv__vctlm[vpmn__sdjcd]
                vpmn__sdjcd += 1
        jztbd__nhd += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{vpmn__sdjcd}' for vpmn__sdjcd in range(len(lauvy__fjhde)))}{',' if len(lauvy__fjhde) == 1 else ''}))
"""
        jztbd__nhd += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(lauvy__fjhde)})
"""
        if udf_func_struct.regular_udfs:
            jztbd__nhd += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{irmm__vsw.native_name}')\n"
                )
            jztbd__nhd += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{uvllv__ffay.native_name}')\n"
                )
            jztbd__nhd += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{gief__mpqt.native_name}')\n"
                )
            jztbd__nhd += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{irmm__vsw.native_name}')\n"
                )
            jztbd__nhd += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{uvllv__ffay.native_name}')
"""
            jztbd__nhd += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{gief__mpqt.native_name}')\n"
                )
        else:
            jztbd__nhd += '    cpp_cb_update_addr = 0\n'
            jztbd__nhd += '    cpp_cb_combine_addr = 0\n'
            jztbd__nhd += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            fcju__rmj = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[fcju__rmj.native_name] = fcju__rmj
            gb_agg_cfunc_addr[fcju__rmj.native_name] = fcju__rmj.address
            jztbd__nhd += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{fcju__rmj.native_name}')\n"
                )
            jztbd__nhd += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{fcju__rmj.native_name}')\n"
                )
        else:
            jztbd__nhd += '    cpp_cb_general_addr = 0\n'
    else:
        jztbd__nhd += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        jztbd__nhd += '    cpp_cb_update_addr = 0\n'
        jztbd__nhd += '    cpp_cb_combine_addr = 0\n'
        jztbd__nhd += '    cpp_cb_eval_addr = 0\n'
        jztbd__nhd += '    cpp_cb_general_addr = 0\n'
    jztbd__nhd += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(awzc__ttjtd.ftype)) for
        awzc__ttjtd in allfuncs] + ['0']))
    jztbd__nhd += (
        f'    func_offsets = np.array({str(hfaj__xcvi)}, dtype=np.int32)\n')
    if len(xtv__vctlm) > 0:
        jztbd__nhd += (
            f'    udf_ncols = np.array({str(xtv__vctlm)}, dtype=np.int32)\n')
    else:
        jztbd__nhd += '    udf_ncols = np.array([0], np.int32)\n'
    jztbd__nhd += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    ybf__dth = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    jztbd__nhd += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {ykgmy__jtaqz}, {lner__lvd}, {eeus__nub}, {ccpl__ittse}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {ybf__dth})
"""
    cvehc__sot = []
    kuws__qla = 0
    if agg_node.return_key:
        ggbk__uzchc = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for vpmn__sdjcd in range(n_keys):
            alv__apfw = ggbk__uzchc + vpmn__sdjcd
            cvehc__sot.append(alv__apfw if alv__apfw not in agg_node.
                dead_out_inds else -1)
            kuws__qla += 1
    for cli__rqxt in agg_node.gb_info_out.keys():
        cvehc__sot.append(cli__rqxt)
        kuws__qla += 1
    zbh__akn = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            cvehc__sot.append(agg_node.n_out_cols - 1)
        else:
            zbh__akn = True
    nli__iuh = ',' if yfyaq__phj == 1 else ''
    mlr__dlm = (
        f"({', '.join(f'out_type{vpmn__sdjcd}' for vpmn__sdjcd in range(yfyaq__phj))}{nli__iuh})"
        )
    zrnlp__soamk = []
    dpgt__uvzq = []
    for vpmn__sdjcd, t in enumerate(out_col_typs):
        if vpmn__sdjcd not in agg_node.dead_out_inds and type_has_unknown_cats(
            t):
            if vpmn__sdjcd in agg_node.gb_info_out:
                fveum__gkjm = agg_node.gb_info_out[vpmn__sdjcd][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                vrps__gtspu = vpmn__sdjcd - ggbk__uzchc
                fveum__gkjm = agg_node.in_key_inds[vrps__gtspu]
            dpgt__uvzq.append(vpmn__sdjcd)
            if (agg_node.is_in_table_format and fveum__gkjm < agg_node.
                n_in_table_arrays):
                zrnlp__soamk.append(f'get_table_data(arg0, {fveum__gkjm})')
            else:
                zrnlp__soamk.append(f'arg{fveum__gkjm}')
    nli__iuh = ',' if len(zrnlp__soamk) == 1 else ''
    jztbd__nhd += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {mlr__dlm}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(zrnlp__soamk)}{nli__iuh}), unknown_cat_out_inds)
"""
    jztbd__nhd += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    jztbd__nhd += '    delete_table_decref_arrays(table)\n'
    jztbd__nhd += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for vpmn__sdjcd in range(n_keys):
            if cvehc__sot[vpmn__sdjcd] == -1:
                jztbd__nhd += (
                    f'    decref_table_array(out_table, {vpmn__sdjcd})\n')
    if zbh__akn:
        skn__pgs = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        jztbd__nhd += f'    decref_table_array(out_table, {skn__pgs})\n'
    jztbd__nhd += '    delete_table(out_table)\n'
    jztbd__nhd += '    ev_clean.finalize()\n'
    jztbd__nhd += '    return out_data\n'
    vqvt__fxb = {f'out_type{vpmn__sdjcd}': out_var_types[vpmn__sdjcd] for
        vpmn__sdjcd in range(yfyaq__phj)}
    vqvt__fxb['out_col_inds'] = MetaType(tuple(cvehc__sot))
    vqvt__fxb['in_col_inds'] = MetaType(tuple(ywqb__qeyq))
    vqvt__fxb['cpp_table_to_py_data'] = cpp_table_to_py_data
    vqvt__fxb['py_data_to_cpp_table'] = py_data_to_cpp_table
    vqvt__fxb.update({f'udf_type{vpmn__sdjcd}': t for vpmn__sdjcd, t in
        enumerate(lauvy__fjhde)})
    vqvt__fxb['udf_dummy_col_inds'] = MetaType(tuple(range(len(lauvy__fjhde))))
    vqvt__fxb['create_dummy_table'] = create_dummy_table
    vqvt__fxb['unknown_cat_out_inds'] = MetaType(tuple(dpgt__uvzq))
    vqvt__fxb['get_table_data'] = bodo.hiframes.table.get_table_data
    return jztbd__nhd, vqvt__fxb


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    zkfmw__huz = tuple(unwrap_typeref(data_types.types[vpmn__sdjcd]) for
        vpmn__sdjcd in range(len(data_types.types)))
    fzm__xzkns = bodo.TableType(zkfmw__huz)
    vqvt__fxb = {'table_type': fzm__xzkns}
    jztbd__nhd = 'def impl(data_types):\n'
    jztbd__nhd += '  py_table = init_table(table_type, False)\n'
    jztbd__nhd += '  py_table = set_table_len(py_table, 1)\n'
    for ezx__udmc, kzbnr__vikrh in fzm__xzkns.type_to_blk.items():
        vqvt__fxb[f'typ_list_{kzbnr__vikrh}'] = types.List(ezx__udmc)
        vqvt__fxb[f'typ_{kzbnr__vikrh}'] = ezx__udmc
        tpmo__brlde = len(fzm__xzkns.block_to_arr_ind[kzbnr__vikrh])
        jztbd__nhd += f"""  arr_list_{kzbnr__vikrh} = alloc_list_like(typ_list_{kzbnr__vikrh}, {tpmo__brlde}, False)
"""
        jztbd__nhd += f'  for i in range(len(arr_list_{kzbnr__vikrh})):\n'
        jztbd__nhd += (
            f'    arr_list_{kzbnr__vikrh}[i] = alloc_type(1, typ_{kzbnr__vikrh}, (-1,))\n'
            )
        jztbd__nhd += f"""  py_table = set_table_block(py_table, arr_list_{kzbnr__vikrh}, {kzbnr__vikrh})
"""
    jztbd__nhd += '  return py_table\n'
    vqvt__fxb.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    ezt__ddut = {}
    exec(jztbd__nhd, vqvt__fxb, ezt__ddut)
    return ezt__ddut['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    esh__jem = agg_node.in_vars[0].name
    xnvrp__dmk, onpqx__puuzz, hsp__fkp = block_use_map[esh__jem]
    if onpqx__puuzz or hsp__fkp:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        whi__qge, rkwx__zkin, vfuzj__lohis = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if rkwx__zkin or vfuzj__lohis:
            whi__qge = set(range(agg_node.n_out_table_arrays))
    else:
        whi__qge = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            whi__qge = {0}
    rclri__elhsx = set(vpmn__sdjcd for vpmn__sdjcd in agg_node.in_key_inds if
        vpmn__sdjcd < agg_node.n_in_table_arrays)
    cwz__cercy = set(agg_node.gb_info_out[vpmn__sdjcd][0] for vpmn__sdjcd in
        whi__qge if vpmn__sdjcd in agg_node.gb_info_out and agg_node.
        gb_info_out[vpmn__sdjcd][0] is not None)
    cwz__cercy |= rclri__elhsx | xnvrp__dmk
    lqab__brrm = len(set(range(agg_node.n_in_table_arrays)) - cwz__cercy) == 0
    block_use_map[esh__jem] = cwz__cercy, lqab__brrm, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    ztrj__amzb = agg_node.n_out_table_arrays
    qzngm__fus = agg_node.out_vars[0].name
    lhce__ani = _find_used_columns(qzngm__fus, ztrj__amzb, column_live_map,
        equiv_vars)
    if lhce__ani is None:
        return False
    uaay__uuywy = set(range(ztrj__amzb)) - lhce__ani
    hax__mni = len(uaay__uuywy - agg_node.dead_out_inds) != 0
    if hax__mni:
        agg_node.dead_out_inds.update(uaay__uuywy)
        agg_node.update_dead_col_info()
    return hax__mni


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for uafe__evpvi in block.body:
            if is_call_assign(uafe__evpvi) and find_callname(f_ir,
                uafe__evpvi.value) == ('len', 'builtins'
                ) and uafe__evpvi.value.args[0].name == f_ir.arg_names[0]:
                hcxyi__aqcfq = get_definition(f_ir, uafe__evpvi.value.func)
                hcxyi__aqcfq.name = 'dummy_agg_count'
                hcxyi__aqcfq.value = dummy_agg_count
    tkg__ahpi = get_name_var_table(f_ir.blocks)
    vpa__rmr = {}
    for name, cdf__asy in tkg__ahpi.items():
        vpa__rmr[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, vpa__rmr)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    xara__lymhc = numba.core.compiler.Flags()
    xara__lymhc.nrt = True
    nsb__jcxd = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, xara__lymhc)
    nsb__jcxd.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, brh__gato, calltypes, cdf__asy = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    kbzf__zmvne = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    twsm__gytmj = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    fil__fdps = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    qupoz__cppqq = fil__fdps(typemap, calltypes)
    pm = twsm__gytmj(typingctx, targetctx, None, f_ir, typemap, brh__gato,
        calltypes, qupoz__cppqq, {}, xara__lymhc, None)
    jveo__lvwq = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = twsm__gytmj(typingctx, targetctx, None, f_ir, typemap, brh__gato,
        calltypes, qupoz__cppqq, {}, xara__lymhc, jveo__lvwq)
    dye__sot = numba.core.typed_passes.InlineOverloads()
    dye__sot.run_pass(pm)
    rbz__xdvv = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    rbz__xdvv.run()
    for block in f_ir.blocks.values():
        for uafe__evpvi in block.body:
            if is_assign(uafe__evpvi) and isinstance(uafe__evpvi.value, (ir
                .Arg, ir.Var)) and isinstance(typemap[uafe__evpvi.target.
                name], SeriesType):
                ezx__udmc = typemap.pop(uafe__evpvi.target.name)
                typemap[uafe__evpvi.target.name] = ezx__udmc.data
            if is_call_assign(uafe__evpvi) and find_callname(f_ir,
                uafe__evpvi.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[uafe__evpvi.target.name].remove(uafe__evpvi
                    .value)
                uafe__evpvi.value = uafe__evpvi.value.args[0]
                f_ir._definitions[uafe__evpvi.target.name].append(uafe__evpvi
                    .value)
            if is_call_assign(uafe__evpvi) and find_callname(f_ir,
                uafe__evpvi.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[uafe__evpvi.target.name].remove(uafe__evpvi
                    .value)
                uafe__evpvi.value = ir.Const(False, uafe__evpvi.loc)
                f_ir._definitions[uafe__evpvi.target.name].append(uafe__evpvi
                    .value)
            if is_call_assign(uafe__evpvi) and find_callname(f_ir,
                uafe__evpvi.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[uafe__evpvi.target.name].remove(uafe__evpvi
                    .value)
                uafe__evpvi.value = ir.Const(False, uafe__evpvi.loc)
                f_ir._definitions[uafe__evpvi.target.name].append(uafe__evpvi
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    drvjm__uvck = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, kbzf__zmvne)
    drvjm__uvck.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    omeo__sukt = numba.core.compiler.StateDict()
    omeo__sukt.func_ir = f_ir
    omeo__sukt.typemap = typemap
    omeo__sukt.calltypes = calltypes
    omeo__sukt.typingctx = typingctx
    omeo__sukt.targetctx = targetctx
    omeo__sukt.return_type = brh__gato
    numba.core.rewrites.rewrite_registry.apply('after-inference', omeo__sukt)
    ttlft__phwmi = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        brh__gato, typingctx, targetctx, kbzf__zmvne, xara__lymhc, {})
    ttlft__phwmi.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            jqg__nzn = ctypes.pythonapi.PyCell_Get
            jqg__nzn.restype = ctypes.py_object
            jqg__nzn.argtypes = ctypes.py_object,
            vwlq__eok = tuple(jqg__nzn(uue__xjxfz) for uue__xjxfz in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            vwlq__eok = closure.items
        assert len(code.co_freevars) == len(vwlq__eok)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, vwlq__eok)


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
        hzw__irr = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (hzw__irr,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        bfoo__zpjoy, arr_var = _rm_arg_agg_block(block, pm.typemap)
        lzih__qkxgj = -1
        for vpmn__sdjcd, uafe__evpvi in enumerate(bfoo__zpjoy):
            if isinstance(uafe__evpvi, numba.parfors.parfor.Parfor):
                assert lzih__qkxgj == -1, 'only one parfor for aggregation function'
                lzih__qkxgj = vpmn__sdjcd
        parfor = None
        if lzih__qkxgj != -1:
            parfor = bfoo__zpjoy[lzih__qkxgj]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = bfoo__zpjoy[:lzih__qkxgj] + parfor.init_block.body
        eval_nodes = bfoo__zpjoy[lzih__qkxgj + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for uafe__evpvi in init_nodes:
            if is_assign(uafe__evpvi) and uafe__evpvi.target.name in redvars:
                ind = redvars.index(uafe__evpvi.target.name)
                reduce_vars[ind] = uafe__evpvi.target
        var_types = [pm.typemap[kvzxq__lnh] for kvzxq__lnh in redvars]
        olhi__tyj = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        tomjh__znwt = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        cwj__adb = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(cwj__adb)
        self.all_update_funcs.append(tomjh__znwt)
        self.all_combine_funcs.append(olhi__tyj)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        kopg__pjlfx = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        wnf__ygmll = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        mam__vlcn = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        tlhwe__vbd = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return (self.all_vartypes, kopg__pjlfx, wnf__ygmll, mam__vlcn,
            tlhwe__vbd)


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
    vmyar__lfkwq = []
    for t, awzc__ttjtd in zip(in_col_types, agg_func):
        vmyar__lfkwq.append((t, awzc__ttjtd))
    noze__dcvc = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    wmdzf__aladr = GeneralUDFGenerator()
    for in_col_typ, func in vmyar__lfkwq:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            noze__dcvc.add_udf(in_col_typ, func)
        except:
            wmdzf__aladr.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = noze__dcvc.gen_all_func()
    general_udf_funcs = wmdzf__aladr.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    yvl__ktzfk = compute_use_defs(parfor.loop_body)
    lan__qdcv = set()
    for ghk__lvmx in yvl__ktzfk.usemap.values():
        lan__qdcv |= ghk__lvmx
    oip__nzj = set()
    for ghk__lvmx in yvl__ktzfk.defmap.values():
        oip__nzj |= ghk__lvmx
    jwpv__ofsw = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    jwpv__ofsw.body = eval_nodes
    urt__qwae = compute_use_defs({(0): jwpv__ofsw})
    xnux__mkvo = urt__qwae.usemap[0]
    ddzq__tjdg = set()
    ill__ptnia = []
    gsnop__tga = []
    for uafe__evpvi in reversed(init_nodes):
        szwp__dpqhk = {kvzxq__lnh.name for kvzxq__lnh in uafe__evpvi.
            list_vars()}
        if is_assign(uafe__evpvi):
            kvzxq__lnh = uafe__evpvi.target.name
            szwp__dpqhk.remove(kvzxq__lnh)
            if (kvzxq__lnh in lan__qdcv and kvzxq__lnh not in ddzq__tjdg and
                kvzxq__lnh not in xnux__mkvo and kvzxq__lnh not in oip__nzj):
                gsnop__tga.append(uafe__evpvi)
                lan__qdcv |= szwp__dpqhk
                oip__nzj.add(kvzxq__lnh)
                continue
        ddzq__tjdg |= szwp__dpqhk
        ill__ptnia.append(uafe__evpvi)
    gsnop__tga.reverse()
    ill__ptnia.reverse()
    wzuq__ipi = min(parfor.loop_body.keys())
    pvd__oably = parfor.loop_body[wzuq__ipi]
    pvd__oably.body = gsnop__tga + pvd__oably.body
    return ill__ptnia


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    wlm__xshbu = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    dix__vtovl = set()
    anamu__dgvkm = []
    for uafe__evpvi in init_nodes:
        if is_assign(uafe__evpvi) and isinstance(uafe__evpvi.value, ir.Global
            ) and isinstance(uafe__evpvi.value.value, pytypes.FunctionType
            ) and uafe__evpvi.value.value in wlm__xshbu:
            dix__vtovl.add(uafe__evpvi.target.name)
        elif is_call_assign(uafe__evpvi
            ) and uafe__evpvi.value.func.name in dix__vtovl:
            pass
        else:
            anamu__dgvkm.append(uafe__evpvi)
    init_nodes = anamu__dgvkm
    vkf__fetqf = types.Tuple(var_types)
    lsv__ktyg = lambda : None
    f_ir = compile_to_numba_ir(lsv__ktyg, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    itavb__swo = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    ktot__lyc = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), itavb__swo,
        loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [ktot__lyc] + block.body
    block.body[-2].value.value = itavb__swo
    dmry__phn = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        vkf__fetqf, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uodp__ltdce = numba.core.target_extension.dispatcher_registry[cpu_target](
        lsv__ktyg)
    uodp__ltdce.add_overload(dmry__phn)
    return uodp__ltdce


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    jmmoj__kuzt = len(update_funcs)
    dnqf__duo = len(in_col_types)
    jztbd__nhd = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for bjbpm__fvw in range(jmmoj__kuzt):
        abu__lgyc = ', '.join(['redvar_arrs[{}][w_ind]'.format(vpmn__sdjcd) for
            vpmn__sdjcd in range(redvar_offsets[bjbpm__fvw], redvar_offsets
            [bjbpm__fvw + 1])])
        if abu__lgyc:
            jztbd__nhd += ('  {} = update_vars_{}({},  data_in[{}][i])\n'.
                format(abu__lgyc, bjbpm__fvw, abu__lgyc, 0 if dnqf__duo == 
                1 else bjbpm__fvw))
    jztbd__nhd += '  return\n'
    duihm__wfey = {}
    for vpmn__sdjcd, awzc__ttjtd in enumerate(update_funcs):
        duihm__wfey['update_vars_{}'.format(vpmn__sdjcd)] = awzc__ttjtd
    ezt__ddut = {}
    exec(jztbd__nhd, duihm__wfey, ezt__ddut)
    kitu__pbm = ezt__ddut['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(kitu__pbm)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    zejex__kxsd = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = zejex__kxsd, zejex__kxsd, types.intp, types.intp
    ydvyf__ynpfy = len(redvar_offsets) - 1
    jztbd__nhd = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for bjbpm__fvw in range(ydvyf__ynpfy):
        abu__lgyc = ', '.join(['redvar_arrs[{}][w_ind]'.format(vpmn__sdjcd) for
            vpmn__sdjcd in range(redvar_offsets[bjbpm__fvw], redvar_offsets
            [bjbpm__fvw + 1])])
        xjc__kfd = ', '.join(['recv_arrs[{}][i]'.format(vpmn__sdjcd) for
            vpmn__sdjcd in range(redvar_offsets[bjbpm__fvw], redvar_offsets
            [bjbpm__fvw + 1])])
        if xjc__kfd:
            jztbd__nhd += '  {} = combine_vars_{}({}, {})\n'.format(abu__lgyc,
                bjbpm__fvw, abu__lgyc, xjc__kfd)
    jztbd__nhd += '  return\n'
    duihm__wfey = {}
    for vpmn__sdjcd, awzc__ttjtd in enumerate(combine_funcs):
        duihm__wfey['combine_vars_{}'.format(vpmn__sdjcd)] = awzc__ttjtd
    ezt__ddut = {}
    exec(jztbd__nhd, duihm__wfey, ezt__ddut)
    jlzdt__bbdcq = ezt__ddut['combine_all_f']
    f_ir = compile_to_numba_ir(jlzdt__bbdcq, duihm__wfey)
    mam__vlcn = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uodp__ltdce = numba.core.target_extension.dispatcher_registry[cpu_target](
        jlzdt__bbdcq)
    uodp__ltdce.add_overload(mam__vlcn)
    return uodp__ltdce


def gen_all_eval_func(eval_funcs, redvar_offsets):
    ydvyf__ynpfy = len(redvar_offsets) - 1
    jztbd__nhd = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for bjbpm__fvw in range(ydvyf__ynpfy):
        abu__lgyc = ', '.join(['redvar_arrs[{}][j]'.format(vpmn__sdjcd) for
            vpmn__sdjcd in range(redvar_offsets[bjbpm__fvw], redvar_offsets
            [bjbpm__fvw + 1])])
        jztbd__nhd += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            bjbpm__fvw, bjbpm__fvw, abu__lgyc)
    jztbd__nhd += '  return\n'
    duihm__wfey = {}
    for vpmn__sdjcd, awzc__ttjtd in enumerate(eval_funcs):
        duihm__wfey['eval_vars_{}'.format(vpmn__sdjcd)] = awzc__ttjtd
    ezt__ddut = {}
    exec(jztbd__nhd, duihm__wfey, ezt__ddut)
    qwf__rdql = ezt__ddut['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(qwf__rdql)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    oror__hcvqa = len(var_types)
    xzl__smk = [f'in{vpmn__sdjcd}' for vpmn__sdjcd in range(oror__hcvqa)]
    vkf__fetqf = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    fosp__dfys = vkf__fetqf(0)
    jztbd__nhd = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        xzl__smk))
    ezt__ddut = {}
    exec(jztbd__nhd, {'_zero': fosp__dfys}, ezt__ddut)
    wua__eevzt = ezt__ddut['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(wua__eevzt, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': fosp__dfys}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    buwu__zqs = []
    for vpmn__sdjcd, kvzxq__lnh in enumerate(reduce_vars):
        buwu__zqs.append(ir.Assign(block.body[vpmn__sdjcd].target,
            kvzxq__lnh, kvzxq__lnh.loc))
        for lvac__ipe in kvzxq__lnh.versioned_names:
            buwu__zqs.append(ir.Assign(kvzxq__lnh, ir.Var(kvzxq__lnh.scope,
                lvac__ipe, kvzxq__lnh.loc), kvzxq__lnh.loc))
    block.body = block.body[:oror__hcvqa] + buwu__zqs + eval_nodes
    cwj__adb = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        vkf__fetqf, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uodp__ltdce = numba.core.target_extension.dispatcher_registry[cpu_target](
        wua__eevzt)
    uodp__ltdce.add_overload(cwj__adb)
    return uodp__ltdce


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    oror__hcvqa = len(redvars)
    raxc__rycu = [f'v{vpmn__sdjcd}' for vpmn__sdjcd in range(oror__hcvqa)]
    xzl__smk = [f'in{vpmn__sdjcd}' for vpmn__sdjcd in range(oror__hcvqa)]
    jztbd__nhd = 'def agg_combine({}):\n'.format(', '.join(raxc__rycu +
        xzl__smk))
    csp__okg = wrap_parfor_blocks(parfor)
    egyrr__hdfg = find_topo_order(csp__okg)
    egyrr__hdfg = egyrr__hdfg[1:]
    unwrap_parfor_blocks(parfor)
    oscg__rns = {}
    hacjc__opg = []
    for olvx__osir in egyrr__hdfg:
        nwzed__qonjq = parfor.loop_body[olvx__osir]
        for uafe__evpvi in nwzed__qonjq.body:
            if is_assign(uafe__evpvi) and uafe__evpvi.target.name in redvars:
                drug__ewsym = uafe__evpvi.target.name
                ind = redvars.index(drug__ewsym)
                if ind in hacjc__opg:
                    continue
                if len(f_ir._definitions[drug__ewsym]) == 2:
                    var_def = f_ir._definitions[drug__ewsym][0]
                    jztbd__nhd += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[drug__ewsym][1]
                    jztbd__nhd += _match_reduce_def(var_def, f_ir, ind)
    jztbd__nhd += '    return {}'.format(', '.join(['v{}'.format(
        vpmn__sdjcd) for vpmn__sdjcd in range(oror__hcvqa)]))
    ezt__ddut = {}
    exec(jztbd__nhd, {}, ezt__ddut)
    ohgnv__axmz = ezt__ddut['agg_combine']
    arg_typs = tuple(2 * var_types)
    duihm__wfey = {'numba': numba, 'bodo': bodo, 'np': np}
    duihm__wfey.update(oscg__rns)
    f_ir = compile_to_numba_ir(ohgnv__axmz, duihm__wfey, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=pm.
        typemap, calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    vkf__fetqf = pm.typemap[block.body[-1].value.name]
    olhi__tyj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        vkf__fetqf, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uodp__ltdce = numba.core.target_extension.dispatcher_registry[cpu_target](
        ohgnv__axmz)
    uodp__ltdce.add_overload(olhi__tyj)
    return uodp__ltdce


def _match_reduce_def(var_def, f_ir, ind):
    jztbd__nhd = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        jztbd__nhd = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        nhf__jciqw = guard(find_callname, f_ir, var_def)
        if nhf__jciqw == ('min', 'builtins'):
            jztbd__nhd = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if nhf__jciqw == ('max', 'builtins'):
            jztbd__nhd = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return jztbd__nhd


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    oror__hcvqa = len(redvars)
    icfb__btwl = 1
    in_vars = []
    for vpmn__sdjcd in range(icfb__btwl):
        dir__kcxfu = ir.Var(arr_var.scope, f'$input{vpmn__sdjcd}', arr_var.loc)
        in_vars.append(dir__kcxfu)
    ohjam__ncmc = parfor.loop_nests[0].index_variable
    wszym__bcihm = [0] * oror__hcvqa
    for nwzed__qonjq in parfor.loop_body.values():
        zifiy__szfo = []
        for uafe__evpvi in nwzed__qonjq.body:
            if is_var_assign(uafe__evpvi
                ) and uafe__evpvi.value.name == ohjam__ncmc.name:
                continue
            if is_getitem(uafe__evpvi
                ) and uafe__evpvi.value.value.name == arr_var.name:
                uafe__evpvi.value = in_vars[0]
            if is_call_assign(uafe__evpvi) and guard(find_callname, pm.
                func_ir, uafe__evpvi.value) == ('isna',
                'bodo.libs.array_kernels') and uafe__evpvi.value.args[0
                ].name == arr_var.name:
                uafe__evpvi.value = ir.Const(False, uafe__evpvi.target.loc)
            if is_assign(uafe__evpvi) and uafe__evpvi.target.name in redvars:
                ind = redvars.index(uafe__evpvi.target.name)
                wszym__bcihm[ind] = uafe__evpvi.target
            zifiy__szfo.append(uafe__evpvi)
        nwzed__qonjq.body = zifiy__szfo
    raxc__rycu = ['v{}'.format(vpmn__sdjcd) for vpmn__sdjcd in range(
        oror__hcvqa)]
    xzl__smk = ['in{}'.format(vpmn__sdjcd) for vpmn__sdjcd in range(icfb__btwl)
        ]
    jztbd__nhd = 'def agg_update({}):\n'.format(', '.join(raxc__rycu +
        xzl__smk))
    jztbd__nhd += '    __update_redvars()\n'
    jztbd__nhd += '    return {}'.format(', '.join(['v{}'.format(
        vpmn__sdjcd) for vpmn__sdjcd in range(oror__hcvqa)]))
    ezt__ddut = {}
    exec(jztbd__nhd, {}, ezt__ddut)
    omjk__bbnt = ezt__ddut['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * icfb__btwl)
    f_ir = compile_to_numba_ir(omjk__bbnt, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    poyy__mwg = f_ir.blocks.popitem()[1].body
    vkf__fetqf = pm.typemap[poyy__mwg[-1].value.name]
    csp__okg = wrap_parfor_blocks(parfor)
    egyrr__hdfg = find_topo_order(csp__okg)
    egyrr__hdfg = egyrr__hdfg[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    pvd__oably = f_ir.blocks[egyrr__hdfg[0]]
    woq__kqi = f_ir.blocks[egyrr__hdfg[-1]]
    irgc__hlqgb = poyy__mwg[:oror__hcvqa + icfb__btwl]
    if oror__hcvqa > 1:
        gkxr__lagkc = poyy__mwg[-3:]
        assert is_assign(gkxr__lagkc[0]) and isinstance(gkxr__lagkc[0].
            value, ir.Expr) and gkxr__lagkc[0].value.op == 'build_tuple'
    else:
        gkxr__lagkc = poyy__mwg[-2:]
    for vpmn__sdjcd in range(oror__hcvqa):
        dfacl__tcysx = poyy__mwg[vpmn__sdjcd].target
        ecci__qbh = ir.Assign(dfacl__tcysx, wszym__bcihm[vpmn__sdjcd],
            dfacl__tcysx.loc)
        irgc__hlqgb.append(ecci__qbh)
    for vpmn__sdjcd in range(oror__hcvqa, oror__hcvqa + icfb__btwl):
        dfacl__tcysx = poyy__mwg[vpmn__sdjcd].target
        ecci__qbh = ir.Assign(dfacl__tcysx, in_vars[vpmn__sdjcd -
            oror__hcvqa], dfacl__tcysx.loc)
        irgc__hlqgb.append(ecci__qbh)
    pvd__oably.body = irgc__hlqgb + pvd__oably.body
    ueux__xrg = []
    for vpmn__sdjcd in range(oror__hcvqa):
        dfacl__tcysx = poyy__mwg[vpmn__sdjcd].target
        ecci__qbh = ir.Assign(wszym__bcihm[vpmn__sdjcd], dfacl__tcysx,
            dfacl__tcysx.loc)
        ueux__xrg.append(ecci__qbh)
    woq__kqi.body += ueux__xrg + gkxr__lagkc
    nmsb__kssqq = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        vkf__fetqf, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uodp__ltdce = numba.core.target_extension.dispatcher_registry[cpu_target](
        omjk__bbnt)
    uodp__ltdce.add_overload(nmsb__kssqq)
    return uodp__ltdce


def _rm_arg_agg_block(block, typemap):
    bfoo__zpjoy = []
    arr_var = None
    for vpmn__sdjcd, uafe__evpvi in enumerate(block.body):
        if is_assign(uafe__evpvi) and isinstance(uafe__evpvi.value, ir.Arg):
            arr_var = uafe__evpvi.target
            fby__moyoz = typemap[arr_var.name]
            if not isinstance(fby__moyoz, types.ArrayCompatible):
                bfoo__zpjoy += block.body[vpmn__sdjcd + 1:]
                break
            pane__zrfv = block.body[vpmn__sdjcd + 1]
            assert is_assign(pane__zrfv) and isinstance(pane__zrfv.value,
                ir.Expr
                ) and pane__zrfv.value.op == 'getattr' and pane__zrfv.value.attr == 'shape' and pane__zrfv.value.value.name == arr_var.name
            xbm__qnl = pane__zrfv.target
            gmr__nxzz = block.body[vpmn__sdjcd + 2]
            assert is_assign(gmr__nxzz) and isinstance(gmr__nxzz.value, ir.Expr
                ) and gmr__nxzz.value.op == 'static_getitem' and gmr__nxzz.value.value.name == xbm__qnl.name
            bfoo__zpjoy += block.body[vpmn__sdjcd + 3:]
            break
        bfoo__zpjoy.append(uafe__evpvi)
    return bfoo__zpjoy, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    csp__okg = wrap_parfor_blocks(parfor)
    egyrr__hdfg = find_topo_order(csp__okg)
    egyrr__hdfg = egyrr__hdfg[1:]
    unwrap_parfor_blocks(parfor)
    for olvx__osir in reversed(egyrr__hdfg):
        for uafe__evpvi in reversed(parfor.loop_body[olvx__osir].body):
            if isinstance(uafe__evpvi, ir.Assign) and (uafe__evpvi.target.
                name in parfor_params or uafe__evpvi.target.name in
                var_to_param):
                tqfcu__hshxn = uafe__evpvi.target.name
                rhs = uafe__evpvi.value
                byb__ugil = (tqfcu__hshxn if tqfcu__hshxn in parfor_params else
                    var_to_param[tqfcu__hshxn])
                dmlyf__jwgwc = []
                if isinstance(rhs, ir.Var):
                    dmlyf__jwgwc = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    dmlyf__jwgwc = [kvzxq__lnh.name for kvzxq__lnh in
                        uafe__evpvi.value.list_vars()]
                param_uses[byb__ugil].extend(dmlyf__jwgwc)
                for kvzxq__lnh in dmlyf__jwgwc:
                    var_to_param[kvzxq__lnh] = byb__ugil
            if isinstance(uafe__evpvi, Parfor):
                get_parfor_reductions(uafe__evpvi, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for ipnjh__yekq, dmlyf__jwgwc in param_uses.items():
        if ipnjh__yekq in dmlyf__jwgwc and ipnjh__yekq not in reduce_varnames:
            reduce_varnames.append(ipnjh__yekq)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
