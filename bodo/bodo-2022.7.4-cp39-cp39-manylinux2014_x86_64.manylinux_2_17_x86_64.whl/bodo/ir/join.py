"""IR node for the join and merge"""
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Tuple, Union
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic
import bodo
from bodo.hiframes.table import TableType
from bodo.ir.connector import trim_extra_used_columns
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, hash_join_table, py_data_to_cpp_table
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import INDEX_SENTINEL, BodoError, MetaType, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, is_str_arr_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        brd__qib = func.signature
        dhuxq__lgopx = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        wyxij__ccei = cgutils.get_or_insert_function(builder.module,
            dhuxq__lgopx, sym._literal_value)
        builder.call(wyxij__ccei, [context.get_constant_null(brd__qib.args[
            0]), context.get_constant_null(brd__qib.args[1]), context.
            get_constant_null(brd__qib.args[2]), context.get_constant_null(
            brd__qib.args[3]), context.get_constant_null(brd__qib.args[4]),
            context.get_constant_null(brd__qib.args[5]), context.
            get_constant(types.int64, 0), context.get_constant(types.int64, 0)]
            )
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


HOW_OPTIONS = Literal['inner', 'left', 'right', 'outer', 'asof']


class Join(ir.Stmt):

    def __init__(self, left_keys: Union[List[str], str], right_keys: Union[
        List[str], str], out_data_vars: List[ir.Var], out_df_type: bodo.
        DataFrameType, left_vars: List[ir.Var], left_df_type: bodo.
        DataFrameType, right_vars: List[ir.Var], right_df_type: bodo.
        DataFrameType, how: HOW_OPTIONS, suffix_left: str, suffix_right:
        str, loc: ir.Loc, is_left: bool, is_right: bool, is_join: bool,
        left_index: bool, right_index: bool, indicator_col_num: int,
        is_na_equal: bool, gen_cond_expr: str):
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.out_col_names = out_df_type.columns
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator_col_num = indicator_col_num
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.n_out_table_cols = len(self.out_col_names)
        self.out_used_cols = set(range(self.n_out_table_cols))
        if self.out_data_vars[1] is not None:
            self.out_used_cols.add(self.n_out_table_cols)
        udagm__ncsfa = left_df_type.columns
        malu__hif = right_df_type.columns
        self.left_col_names = udagm__ncsfa
        self.right_col_names = malu__hif
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(udagm__ncsfa) if self.is_left_table else 0
        self.n_right_table_cols = len(malu__hif) if self.is_right_table else 0
        vxvzo__suu = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        otj__mbdi = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(vxvzo__suu)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(otj__mbdi)
        self.left_var_map = {xtipy__ntt: nnb__urns for nnb__urns,
            xtipy__ntt in enumerate(udagm__ncsfa)}
        self.right_var_map = {xtipy__ntt: nnb__urns for nnb__urns,
            xtipy__ntt in enumerate(malu__hif)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = vxvzo__suu
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = otj__mbdi
        self.left_key_set = set(self.left_var_map[xtipy__ntt] for
            xtipy__ntt in left_keys)
        self.right_key_set = set(self.right_var_map[xtipy__ntt] for
            xtipy__ntt in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[xtipy__ntt] for
                xtipy__ntt in udagm__ncsfa if f'(left.{xtipy__ntt})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[xtipy__ntt] for
                xtipy__ntt in malu__hif if f'(right.{xtipy__ntt})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        xge__glexp: int = -1
        phrka__iylrl = set(left_keys) & set(right_keys)
        vwzm__rcm = set(udagm__ncsfa) & set(malu__hif)
        jhrv__vvc = vwzm__rcm - phrka__iylrl
        hdic__myfy: Dict[int, (Literal['left', 'right'], int)] = {}
        kis__sohkl: Dict[int, int] = {}
        fsyyx__cjlaa: Dict[int, int] = {}
        for nnb__urns, xtipy__ntt in enumerate(udagm__ncsfa):
            if xtipy__ntt in jhrv__vvc:
                ulaq__lnudi = str(xtipy__ntt) + suffix_left
                rdtmi__btgg = out_df_type.column_index[ulaq__lnudi]
                if (right_index and not left_index and nnb__urns in self.
                    left_key_set):
                    xge__glexp = out_df_type.column_index[xtipy__ntt]
                    hdic__myfy[xge__glexp] = 'left', nnb__urns
            else:
                rdtmi__btgg = out_df_type.column_index[xtipy__ntt]
            hdic__myfy[rdtmi__btgg] = 'left', nnb__urns
            kis__sohkl[nnb__urns] = rdtmi__btgg
        for nnb__urns, xtipy__ntt in enumerate(malu__hif):
            if xtipy__ntt not in phrka__iylrl:
                if xtipy__ntt in jhrv__vvc:
                    nsi__ami = str(xtipy__ntt) + suffix_right
                    rdtmi__btgg = out_df_type.column_index[nsi__ami]
                    if (left_index and not right_index and nnb__urns in
                        self.right_key_set):
                        xge__glexp = out_df_type.column_index[xtipy__ntt]
                        hdic__myfy[xge__glexp] = 'right', nnb__urns
                else:
                    rdtmi__btgg = out_df_type.column_index[xtipy__ntt]
                hdic__myfy[rdtmi__btgg] = 'right', nnb__urns
                fsyyx__cjlaa[nnb__urns] = rdtmi__btgg
        if self.left_vars[-1] is not None:
            kis__sohkl[vxvzo__suu] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            fsyyx__cjlaa[otj__mbdi] = self.n_out_table_cols
        self.out_to_input_col_map = hdic__myfy
        self.left_to_output_map = kis__sohkl
        self.right_to_output_map = fsyyx__cjlaa
        self.extra_data_col_num = xge__glexp
        if len(out_data_vars) > 1:
            irula__bcb = 'left' if right_index else 'right'
            if irula__bcb == 'left':
                qrixy__dahs = vxvzo__suu
            elif irula__bcb == 'right':
                qrixy__dahs = otj__mbdi
        else:
            irula__bcb = None
            qrixy__dahs = -1
        self.index_source = irula__bcb
        self.index_col_num = qrixy__dahs
        nsxpp__jgxi = []
        bbiyx__lcuj = len(left_keys)
        for mni__wrscw in range(bbiyx__lcuj):
            qnkdi__torrs = left_keys[mni__wrscw]
            xup__sidbd = right_keys[mni__wrscw]
            nsxpp__jgxi.append(qnkdi__torrs == xup__sidbd)
        self.vect_same_key = nsxpp__jgxi

    @property
    def has_live_left_table_var(self):
        return self.is_left_table and self.left_vars[0] is not None

    @property
    def has_live_right_table_var(self):
        return self.is_right_table and self.right_vars[0] is not None

    @property
    def has_live_out_table_var(self):
        return self.out_data_vars[0] is not None

    @property
    def has_live_out_index_var(self):
        return self.out_data_vars[1] is not None

    def get_out_table_var(self):
        return self.out_data_vars[0]

    def get_out_index_var(self):
        return self.out_data_vars[1]

    def get_live_left_vars(self):
        vars = []
        for pfj__ngz in self.left_vars:
            if pfj__ngz is not None:
                vars.append(pfj__ngz)
        return vars

    def get_live_right_vars(self):
        vars = []
        for pfj__ngz in self.right_vars:
            if pfj__ngz is not None:
                vars.append(pfj__ngz)
        return vars

    def get_live_out_vars(self):
        vars = []
        for pfj__ngz in self.out_data_vars:
            if pfj__ngz is not None:
                vars.append(pfj__ngz)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        fkxev__attx = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[fkxev__attx])
                fkxev__attx += 1
            else:
                left_vars.append(None)
            start = 1
        yunp__orecx = max(self.n_left_table_cols - 1, 0)
        for nnb__urns in range(start, len(self.left_vars)):
            if nnb__urns + yunp__orecx in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[fkxev__attx])
                fkxev__attx += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        fkxev__attx = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[fkxev__attx])
                fkxev__attx += 1
            else:
                right_vars.append(None)
            start = 1
        yunp__orecx = max(self.n_right_table_cols - 1, 0)
        for nnb__urns in range(start, len(self.right_vars)):
            if nnb__urns + yunp__orecx in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[fkxev__attx])
                fkxev__attx += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        nfcfs__loojt = [self.has_live_out_table_var, self.
            has_live_out_index_var]
        fkxev__attx = 0
        for nnb__urns in range(len(self.out_data_vars)):
            if not nfcfs__loojt[nnb__urns]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[fkxev__attx])
                fkxev__attx += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {nnb__urns for nnb__urns in self.out_used_cols if nnb__urns <
            self.n_out_table_cols}

    def __repr__(self):
        sdpx__nbpve = ', '.join([f'{xtipy__ntt}' for xtipy__ntt in self.
            left_col_names])
        xge__umct = f'left={{{sdpx__nbpve}}}'
        sdpx__nbpve = ', '.join([f'{xtipy__ntt}' for xtipy__ntt in self.
            right_col_names])
        cko__wldo = f'right={{{sdpx__nbpve}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, xge__umct, cko__wldo)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    wzpgk__nihr = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    guinq__rbfny = []
    cbume__mzbn = join_node.get_live_left_vars()
    for mnw__kwt in cbume__mzbn:
        tvtc__zmmv = typemap[mnw__kwt.name]
        nmaid__ccqxk = equiv_set.get_shape(mnw__kwt)
        if nmaid__ccqxk:
            guinq__rbfny.append(nmaid__ccqxk[0])
    if len(guinq__rbfny) > 1:
        equiv_set.insert_equiv(*guinq__rbfny)
    guinq__rbfny = []
    cbume__mzbn = list(join_node.get_live_right_vars())
    for mnw__kwt in cbume__mzbn:
        tvtc__zmmv = typemap[mnw__kwt.name]
        nmaid__ccqxk = equiv_set.get_shape(mnw__kwt)
        if nmaid__ccqxk:
            guinq__rbfny.append(nmaid__ccqxk[0])
    if len(guinq__rbfny) > 1:
        equiv_set.insert_equiv(*guinq__rbfny)
    guinq__rbfny = []
    for tubd__bflav in join_node.get_live_out_vars():
        tvtc__zmmv = typemap[tubd__bflav.name]
        obgks__udj = array_analysis._gen_shape_call(equiv_set, tubd__bflav,
            tvtc__zmmv.ndim, None, wzpgk__nihr)
        equiv_set.insert_equiv(tubd__bflav, obgks__udj)
        guinq__rbfny.append(obgks__udj[0])
        equiv_set.define(tubd__bflav, set())
    if len(guinq__rbfny) > 1:
        equiv_set.insert_equiv(*guinq__rbfny)
    return [], wzpgk__nihr


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    srjf__utt = Distribution.OneD
    pqkh__jei = Distribution.OneD
    for mnw__kwt in join_node.get_live_left_vars():
        srjf__utt = Distribution(min(srjf__utt.value, array_dists[mnw__kwt.
            name].value))
    for mnw__kwt in join_node.get_live_right_vars():
        pqkh__jei = Distribution(min(pqkh__jei.value, array_dists[mnw__kwt.
            name].value))
    gfl__ceqi = Distribution.OneD_Var
    for tubd__bflav in join_node.get_live_out_vars():
        if tubd__bflav.name in array_dists:
            gfl__ceqi = Distribution(min(gfl__ceqi.value, array_dists[
                tubd__bflav.name].value))
    odv__hyix = Distribution(min(gfl__ceqi.value, srjf__utt.value))
    gxgbl__qtwx = Distribution(min(gfl__ceqi.value, pqkh__jei.value))
    gfl__ceqi = Distribution(max(odv__hyix.value, gxgbl__qtwx.value))
    for tubd__bflav in join_node.get_live_out_vars():
        array_dists[tubd__bflav.name] = gfl__ceqi
    if gfl__ceqi != Distribution.OneD_Var:
        srjf__utt = gfl__ceqi
        pqkh__jei = gfl__ceqi
    for mnw__kwt in join_node.get_live_left_vars():
        array_dists[mnw__kwt.name] = srjf__utt
    for mnw__kwt in join_node.get_live_right_vars():
        array_dists[mnw__kwt.name] = pqkh__jei
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(pfj__ngz, callback,
        cbdata) for pfj__ngz in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(pfj__ngz, callback,
        cbdata) for pfj__ngz in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(pfj__ngz, callback,
        cbdata) for pfj__ngz in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        qpdz__jnlsk = []
        nxh__pffkv = join_node.get_out_table_var()
        if nxh__pffkv.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for vbq__dne in join_node.out_to_input_col_map.keys():
            if vbq__dne in join_node.out_used_cols:
                continue
            qpdz__jnlsk.append(vbq__dne)
            if join_node.indicator_col_num == vbq__dne:
                join_node.indicator_col_num = -1
                continue
            if vbq__dne == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            fyqf__rzixr, vbq__dne = join_node.out_to_input_col_map[vbq__dne]
            if fyqf__rzixr == 'left':
                if (vbq__dne not in join_node.left_key_set and vbq__dne not in
                    join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(vbq__dne)
                    if not join_node.is_left_table:
                        join_node.left_vars[vbq__dne] = None
            elif fyqf__rzixr == 'right':
                if (vbq__dne not in join_node.right_key_set and vbq__dne not in
                    join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(vbq__dne)
                    if not join_node.is_right_table:
                        join_node.right_vars[vbq__dne] = None
        for nnb__urns in qpdz__jnlsk:
            del join_node.out_to_input_col_map[nnb__urns]
        if join_node.is_left_table:
            vmyke__hbcb = set(range(join_node.n_left_table_cols))
            aaebj__otpvy = not bool(vmyke__hbcb - join_node.left_dead_var_inds)
            if aaebj__otpvy:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            vmyke__hbcb = set(range(join_node.n_right_table_cols))
            aaebj__otpvy = not bool(vmyke__hbcb - join_node.right_dead_var_inds
                )
            if aaebj__otpvy:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        qtcqk__yvc = join_node.get_out_index_var()
        if qtcqk__yvc.name not in lives:
            join_node.out_data_vars[1] = None
            join_node.out_used_cols.remove(join_node.n_out_table_cols)
            if join_node.index_source == 'left':
                if (join_node.index_col_num not in join_node.left_key_set and
                    join_node.index_col_num not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(join_node.index_col_num)
                    join_node.left_vars[-1] = None
            elif join_node.index_col_num not in join_node.right_key_set and join_node.index_col_num not in join_node.right_cond_cols:
                join_node.right_dead_var_inds.add(join_node.index_col_num)
                join_node.right_vars[-1] = None
    if not (join_node.has_live_out_table_var or join_node.
        has_live_out_index_var):
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_remove_dead_column(join_node, column_live_map, equiv_vars, typemap):
    enpgc__ddv = False
    if join_node.has_live_out_table_var:
        kfw__crz = join_node.get_out_table_var().name
        mzhrr__rqm, exxab__xys, hww__oompt = get_live_column_nums_block(
            column_live_map, equiv_vars, kfw__crz)
        if not (exxab__xys or hww__oompt):
            mzhrr__rqm = trim_extra_used_columns(mzhrr__rqm, join_node.
                n_out_table_cols)
            sxts__ulpi = join_node.get_out_table_used_cols()
            if len(mzhrr__rqm) != len(sxts__ulpi):
                enpgc__ddv = not (join_node.is_left_table and join_node.
                    is_right_table)
                btdbg__xfhm = sxts__ulpi - mzhrr__rqm
                join_node.out_used_cols = join_node.out_used_cols - btdbg__xfhm
    return enpgc__ddv


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        vzv__ltjyw = join_node.get_out_table_var()
        ldzlt__wzk, exxab__xys, hww__oompt = _compute_table_column_uses(
            vzv__ltjyw.name, table_col_use_map, equiv_vars)
    else:
        ldzlt__wzk, exxab__xys, hww__oompt = set(), False, False
    if join_node.has_live_left_table_var:
        jphy__guwb = join_node.left_vars[0].name
        nwupq__opdq, xlzvp__dadlt, tfk__hmvn = block_use_map[jphy__guwb]
        if not (xlzvp__dadlt or tfk__hmvn):
            rvliz__ffq = set([join_node.out_to_input_col_map[nnb__urns][1] for
                nnb__urns in ldzlt__wzk if join_node.out_to_input_col_map[
                nnb__urns][0] == 'left'])
            pohm__biybp = set(nnb__urns for nnb__urns in join_node.
                left_key_set | join_node.left_cond_cols if nnb__urns <
                join_node.n_left_table_cols)
            if not (exxab__xys or hww__oompt):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (rvliz__ffq | pohm__biybp)
            block_use_map[jphy__guwb] = (nwupq__opdq | rvliz__ffq |
                pohm__biybp, exxab__xys or hww__oompt, False)
    if join_node.has_live_right_table_var:
        mtxf__hhk = join_node.right_vars[0].name
        nwupq__opdq, xlzvp__dadlt, tfk__hmvn = block_use_map[mtxf__hhk]
        if not (xlzvp__dadlt or tfk__hmvn):
            dbu__uzxk = set([join_node.out_to_input_col_map[nnb__urns][1] for
                nnb__urns in ldzlt__wzk if join_node.out_to_input_col_map[
                nnb__urns][0] == 'right'])
            zprzt__dxjmm = set(nnb__urns for nnb__urns in join_node.
                right_key_set | join_node.right_cond_cols if nnb__urns <
                join_node.n_right_table_cols)
            if not (exxab__xys or hww__oompt):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (dbu__uzxk | zprzt__dxjmm)
            block_use_map[mtxf__hhk] = (nwupq__opdq | dbu__uzxk |
                zprzt__dxjmm, exxab__xys or hww__oompt, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({mxlk__tym.name for mxlk__tym in join_node.
        get_live_left_vars()})
    use_set.update({mxlk__tym.name for mxlk__tym in join_node.
        get_live_right_vars()})
    def_set.update({mxlk__tym.name for mxlk__tym in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    hurwd__amxqc = set(mxlk__tym.name for mxlk__tym in join_node.
        get_live_out_vars())
    return set(), hurwd__amxqc


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(pfj__ngz, var_dict) for
        pfj__ngz in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(pfj__ngz, var_dict) for
        pfj__ngz in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(pfj__ngz, var_dict
        ) for pfj__ngz in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for mnw__kwt in join_node.get_live_out_vars():
        definitions[mnw__kwt.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        dse__znncf = join_node.loc.strformat()
        xpyv__pma = [join_node.left_col_names[nnb__urns] for nnb__urns in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        shfje__kvr = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', shfje__kvr,
            dse__znncf, xpyv__pma)
        vny__enj = [join_node.right_col_names[nnb__urns] for nnb__urns in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        shfje__kvr = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', shfje__kvr,
            dse__znncf, vny__enj)
        ttzne__zyk = [join_node.out_col_names[nnb__urns] for nnb__urns in
            sorted(join_node.get_out_table_used_cols())]
        shfje__kvr = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', shfje__kvr,
            dse__znncf, ttzne__zyk)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    bbiyx__lcuj = len(join_node.left_keys)
    out_physical_to_logical_list = []
    if join_node.has_live_out_table_var:
        out_table_type = typemap[join_node.get_out_table_var().name]
    else:
        out_table_type = types.none
    if join_node.has_live_out_index_var:
        index_col_type = typemap[join_node.get_out_index_var().name]
    else:
        index_col_type = types.none
    if join_node.extra_data_col_num != -1:
        out_physical_to_logical_list.append(join_node.extra_data_col_num)
    left_key_in_output = []
    right_key_in_output = []
    left_used_key_nums = set()
    right_used_key_nums = set()
    left_logical_physical_map = {}
    right_logical_physical_map = {}
    left_physical_to_logical_list = []
    right_physical_to_logical_list = []
    otyur__gqeru = 0
    wrrt__rqmo = 0
    axouz__tvkdf = []
    for xtipy__ntt in join_node.left_keys:
        hce__owa = join_node.left_var_map[xtipy__ntt]
        if not join_node.is_left_table:
            axouz__tvkdf.append(join_node.left_vars[hce__owa])
        nfcfs__loojt = 1
        rdtmi__btgg = join_node.left_to_output_map[hce__owa]
        if xtipy__ntt == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == hce__owa):
                out_physical_to_logical_list.append(rdtmi__btgg)
                left_used_key_nums.add(hce__owa)
            else:
                nfcfs__loojt = 0
        elif rdtmi__btgg not in join_node.out_used_cols:
            nfcfs__loojt = 0
        elif hce__owa in left_used_key_nums:
            nfcfs__loojt = 0
        else:
            left_used_key_nums.add(hce__owa)
            out_physical_to_logical_list.append(rdtmi__btgg)
        left_physical_to_logical_list.append(hce__owa)
        left_logical_physical_map[hce__owa] = otyur__gqeru
        otyur__gqeru += 1
        left_key_in_output.append(nfcfs__loojt)
    axouz__tvkdf = tuple(axouz__tvkdf)
    luxmy__apx = []
    for nnb__urns in range(len(join_node.left_col_names)):
        if (nnb__urns not in join_node.left_dead_var_inds and nnb__urns not in
            join_node.left_key_set):
            if not join_node.is_left_table:
                mxlk__tym = join_node.left_vars[nnb__urns]
                luxmy__apx.append(mxlk__tym)
            lnpq__bwfjs = 1
            ibupd__vvjnh = 1
            rdtmi__btgg = join_node.left_to_output_map[nnb__urns]
            if nnb__urns in join_node.left_cond_cols:
                if rdtmi__btgg not in join_node.out_used_cols:
                    lnpq__bwfjs = 0
                left_key_in_output.append(lnpq__bwfjs)
            elif nnb__urns in join_node.left_dead_var_inds:
                lnpq__bwfjs = 0
                ibupd__vvjnh = 0
            if lnpq__bwfjs:
                out_physical_to_logical_list.append(rdtmi__btgg)
            if ibupd__vvjnh:
                left_physical_to_logical_list.append(nnb__urns)
                left_logical_physical_map[nnb__urns] = otyur__gqeru
                otyur__gqeru += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            luxmy__apx.append(join_node.left_vars[join_node.index_col_num])
        rdtmi__btgg = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rdtmi__btgg)
        left_physical_to_logical_list.append(join_node.index_col_num)
    luxmy__apx = tuple(luxmy__apx)
    if join_node.is_left_table:
        luxmy__apx = tuple(join_node.get_live_left_vars())
    rwe__jne = []
    for nnb__urns, xtipy__ntt in enumerate(join_node.right_keys):
        hce__owa = join_node.right_var_map[xtipy__ntt]
        if not join_node.is_right_table:
            rwe__jne.append(join_node.right_vars[hce__owa])
        if not join_node.vect_same_key[nnb__urns] and not join_node.is_join:
            nfcfs__loojt = 1
            if hce__owa not in join_node.right_to_output_map:
                nfcfs__loojt = 0
            else:
                rdtmi__btgg = join_node.right_to_output_map[hce__owa]
                if xtipy__ntt == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        hce__owa):
                        out_physical_to_logical_list.append(rdtmi__btgg)
                        right_used_key_nums.add(hce__owa)
                    else:
                        nfcfs__loojt = 0
                elif rdtmi__btgg not in join_node.out_used_cols:
                    nfcfs__loojt = 0
                elif hce__owa in right_used_key_nums:
                    nfcfs__loojt = 0
                else:
                    right_used_key_nums.add(hce__owa)
                    out_physical_to_logical_list.append(rdtmi__btgg)
            right_key_in_output.append(nfcfs__loojt)
        right_physical_to_logical_list.append(hce__owa)
        right_logical_physical_map[hce__owa] = wrrt__rqmo
        wrrt__rqmo += 1
    rwe__jne = tuple(rwe__jne)
    clch__voxmm = []
    for nnb__urns in range(len(join_node.right_col_names)):
        if (nnb__urns not in join_node.right_dead_var_inds and nnb__urns not in
            join_node.right_key_set):
            if not join_node.is_right_table:
                clch__voxmm.append(join_node.right_vars[nnb__urns])
            lnpq__bwfjs = 1
            ibupd__vvjnh = 1
            rdtmi__btgg = join_node.right_to_output_map[nnb__urns]
            if nnb__urns in join_node.right_cond_cols:
                if rdtmi__btgg not in join_node.out_used_cols:
                    lnpq__bwfjs = 0
                right_key_in_output.append(lnpq__bwfjs)
            elif nnb__urns in join_node.right_dead_var_inds:
                lnpq__bwfjs = 0
                ibupd__vvjnh = 0
            if lnpq__bwfjs:
                out_physical_to_logical_list.append(rdtmi__btgg)
            if ibupd__vvjnh:
                right_physical_to_logical_list.append(nnb__urns)
                right_logical_physical_map[nnb__urns] = wrrt__rqmo
                wrrt__rqmo += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            clch__voxmm.append(join_node.right_vars[join_node.index_col_num])
        rdtmi__btgg = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rdtmi__btgg)
        right_physical_to_logical_list.append(join_node.index_col_num)
    clch__voxmm = tuple(clch__voxmm)
    if join_node.is_right_table:
        clch__voxmm = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    vrui__wdz = axouz__tvkdf + rwe__jne + luxmy__apx + clch__voxmm
    ujih__siadv = tuple(typemap[mxlk__tym.name] for mxlk__tym in vrui__wdz)
    left_other_names = tuple('t1_c' + str(nnb__urns) for nnb__urns in range
        (len(luxmy__apx)))
    right_other_names = tuple('t2_c' + str(nnb__urns) for nnb__urns in
        range(len(clch__voxmm)))
    if join_node.is_left_table:
        wwzj__qbg = ()
    else:
        wwzj__qbg = tuple('t1_key' + str(nnb__urns) for nnb__urns in range(
            bbiyx__lcuj))
    if join_node.is_right_table:
        jco__pae = ()
    else:
        jco__pae = tuple('t2_key' + str(nnb__urns) for nnb__urns in range(
            bbiyx__lcuj))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(wwzj__qbg + jco__pae +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            flf__awlya = typemap[join_node.left_vars[0].name]
        else:
            flf__awlya = types.none
        for mey__ngobi in left_physical_to_logical_list:
            if mey__ngobi < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                tvtc__zmmv = flf__awlya.arr_types[mey__ngobi]
            else:
                tvtc__zmmv = typemap[join_node.left_vars[-1].name]
            if mey__ngobi in join_node.left_key_set:
                left_key_types.append(tvtc__zmmv)
            else:
                left_other_types.append(tvtc__zmmv)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[mxlk__tym.name] for mxlk__tym in
            axouz__tvkdf)
        left_other_types = tuple([typemap[xtipy__ntt.name] for xtipy__ntt in
            luxmy__apx])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            flf__awlya = typemap[join_node.right_vars[0].name]
        else:
            flf__awlya = types.none
        for mey__ngobi in right_physical_to_logical_list:
            if mey__ngobi < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                tvtc__zmmv = flf__awlya.arr_types[mey__ngobi]
            else:
                tvtc__zmmv = typemap[join_node.right_vars[-1].name]
            if mey__ngobi in join_node.right_key_set:
                right_key_types.append(tvtc__zmmv)
            else:
                right_other_types.append(tvtc__zmmv)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[mxlk__tym.name] for mxlk__tym in
            rwe__jne)
        right_other_types = tuple([typemap[xtipy__ntt.name] for xtipy__ntt in
            clch__voxmm])
    matched_key_types = []
    for nnb__urns in range(bbiyx__lcuj):
        dzuzm__tjc = _match_join_key_types(left_key_types[nnb__urns],
            right_key_types[nnb__urns], loc)
        glbs[f'key_type_{nnb__urns}'] = dzuzm__tjc
        matched_key_types.append(dzuzm__tjc)
    if join_node.is_left_table:
        htln__krf = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if htln__krf:
            sexg__ozssx = False
            rdxc__nyqz = False
            pvpe__tgfwt = None
            if join_node.has_live_left_table_var:
                ojkmw__clcjk = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                ojkmw__clcjk = None
            for vbq__dne, tvtc__zmmv in htln__krf.items():
                if vbq__dne < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    ojkmw__clcjk[vbq__dne] = tvtc__zmmv
                    sexg__ozssx = True
                else:
                    pvpe__tgfwt = tvtc__zmmv
                    rdxc__nyqz = True
            if sexg__ozssx:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(ojkmw__clcjk))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if rdxc__nyqz:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = pvpe__tgfwt
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({wwzj__qbg[nnb__urns]}, key_type_{nnb__urns})'
             if left_key_types[nnb__urns] != matched_key_types[nnb__urns] else
            f'{wwzj__qbg[nnb__urns]}' for nnb__urns in range(bbiyx__lcuj)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        htln__krf = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if htln__krf:
            sexg__ozssx = False
            rdxc__nyqz = False
            pvpe__tgfwt = None
            if join_node.has_live_right_table_var:
                ojkmw__clcjk = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                ojkmw__clcjk = None
            for vbq__dne, tvtc__zmmv in htln__krf.items():
                if vbq__dne < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    ojkmw__clcjk[vbq__dne] = tvtc__zmmv
                    sexg__ozssx = True
                else:
                    pvpe__tgfwt = tvtc__zmmv
                    rdxc__nyqz = True
            if sexg__ozssx:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(ojkmw__clcjk))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if rdxc__nyqz:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = pvpe__tgfwt
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({jco__pae[nnb__urns]}, key_type_{nnb__urns})'
             if right_key_types[nnb__urns] != matched_key_types[nnb__urns] else
            f'{jco__pae[nnb__urns]}' for nnb__urns in range(bbiyx__lcuj)))
        func_text += '    data_right = ({}{})\n'.format(','.join(
            right_other_names), ',' if len(right_other_names) != 0 else '')
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap,
        left_logical_physical_map, right_logical_physical_map))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel, 'pd.merge_asof requires both left and right to be replicated or distributed'
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(join_node, left_key_types,
            right_key_types, matched_key_types, left_other_names,
            right_other_names, left_other_types, right_other_types,
            left_key_in_output, right_key_in_output, left_parallel,
            right_parallel, glbs, out_physical_to_logical_list,
            out_table_type, index_col_type, join_node.
            get_out_table_used_cols(), left_used_key_nums,
            right_used_key_nums, general_cond_cfunc, left_col_nums,
            right_col_nums, left_physical_to_logical_list,
            right_physical_to_logical_list)
    if join_node.how == 'asof':
        for nnb__urns in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(nnb__urns,
                nnb__urns)
        for nnb__urns in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(nnb__urns
                , nnb__urns)
        for nnb__urns in range(bbiyx__lcuj):
            func_text += (
                f'    t1_keys_{nnb__urns} = out_t1_keys[{nnb__urns}]\n')
        for nnb__urns in range(bbiyx__lcuj):
            func_text += (
                f'    t2_keys_{nnb__urns} = out_t2_keys[{nnb__urns}]\n')
    iban__ugdvt = {}
    exec(func_text, {}, iban__ugdvt)
    jqla__wziiv = iban__ugdvt['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'delete_table': delete_table,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr, 'key_in_output': np.array
        (left_key_in_output + right_key_in_output, dtype=np.bool_),
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    zepqa__vdcox = compile_to_numba_ir(jqla__wziiv, glbs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=ujih__siadv, typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(zepqa__vdcox, vrui__wdz)
    likx__phnz = zepqa__vdcox.body[:-3]
    if join_node.has_live_out_index_var:
        likx__phnz[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        likx__phnz[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        likx__phnz.pop(-1)
    elif not join_node.has_live_out_table_var:
        likx__phnz.pop(-2)
    return likx__phnz


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    kgkt__hqb = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{kgkt__hqb}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        left_logical_physical_map, join_node.left_var_map, typemap,
        join_node.left_vars, table_getitem_funcs, func_text, 'left',
        join_node.left_key_set, na_check_name, join_node.is_left_table)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        right_logical_physical_map, join_node.right_var_map, typemap,
        join_node.right_vars, table_getitem_funcs, func_text, 'right',
        join_node.right_key_set, na_check_name, join_node.is_right_table)
    func_text += f'  return {expr}'
    iban__ugdvt = {}
    exec(func_text, table_getitem_funcs, iban__ugdvt)
    lnpxy__vrp = iban__ugdvt[f'bodo_join_gen_cond{kgkt__hqb}']
    cuf__giprw = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    kfm__qomn = numba.cfunc(cuf__giprw, nopython=True)(lnpxy__vrp)
    join_gen_cond_cfunc[kfm__qomn.native_name] = kfm__qomn
    join_gen_cond_cfunc_addr[kfm__qomn.native_name] = kfm__qomn.address
    return kfm__qomn, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    hiixz__iuox = []
    for xtipy__ntt, ast__lmbli in name_to_var_map.items():
        gsmv__vlw = f'({table_name}.{xtipy__ntt})'
        if gsmv__vlw not in expr:
            continue
        bwqr__ccy = f'getitem_{table_name}_val_{ast__lmbli}'
        yop__ddkxo = f'_bodo_{table_name}_val_{ast__lmbli}'
        if is_table_var:
            tcn__wkpsj = typemap[col_vars[0].name].arr_types[ast__lmbli]
        else:
            tcn__wkpsj = typemap[col_vars[ast__lmbli].name]
        if is_str_arr_type(tcn__wkpsj) or tcn__wkpsj == bodo.binary_array_type:
            func_text += f"""  {yop__ddkxo}, {yop__ddkxo}_size = {bwqr__ccy}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {yop__ddkxo} = bodo.libs.str_arr_ext.decode_utf8({yop__ddkxo}, {yop__ddkxo}_size)
"""
        else:
            func_text += (
                f'  {yop__ddkxo} = {bwqr__ccy}({table_name}_data1, {table_name}_ind)\n'
                )
        csj__ufxi = logical_to_physical_ind[ast__lmbli]
        table_getitem_funcs[bwqr__ccy
            ] = bodo.libs.array._gen_row_access_intrinsic(tcn__wkpsj, csj__ufxi
            )
        expr = expr.replace(gsmv__vlw, yop__ddkxo)
        kbu__czxo = f'({na_check_name}.{table_name}.{xtipy__ntt})'
        if kbu__czxo in expr:
            tlhro__mczl = f'nacheck_{table_name}_val_{ast__lmbli}'
            iqrd__oijlh = f'_bodo_isna_{table_name}_val_{ast__lmbli}'
            if isinstance(tcn__wkpsj, bodo.libs.int_arr_ext.IntegerArrayType
                ) or tcn__wkpsj in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(tcn__wkpsj):
                func_text += f"""  {iqrd__oijlh} = {tlhro__mczl}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {iqrd__oijlh} = {tlhro__mczl}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[tlhro__mczl
                ] = bodo.libs.array._gen_row_na_check_intrinsic(tcn__wkpsj,
                csj__ufxi)
            expr = expr.replace(kbu__czxo, iqrd__oijlh)
        if ast__lmbli not in key_set:
            hiixz__iuox.append(csj__ufxi)
    return expr, func_text, hiixz__iuox


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as xox__tpes:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    polgx__nht = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[mxlk__tym.name] in polgx__nht for
        mxlk__tym in join_node.get_live_left_vars())
    right_parallel = all(array_dists[mxlk__tym.name] in polgx__nht for
        mxlk__tym in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[mxlk__tym.name] in polgx__nht for
            mxlk__tym in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[mxlk__tym.name] in polgx__nht for
            mxlk__tym in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[mxlk__tym.name] in polgx__nht for mxlk__tym in
            join_node.get_live_out_vars())
    return left_parallel, right_parallel


def _gen_local_hash_join(join_node, left_key_types, right_key_types,
    matched_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, left_key_in_output,
    right_key_in_output, left_parallel, right_parallel, glbs,
    out_physical_to_logical_list, out_table_type, index_col_type,
    out_table_used_cols, left_used_key_nums, right_used_key_nums,
    general_cond_cfunc, left_col_nums, right_col_nums,
    left_physical_to_logical_list, right_physical_to_logical_list):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    wfd__ujo = set(left_col_nums)
    grws__qbsjl = set(right_col_nums)
    nsxpp__jgxi = join_node.vect_same_key
    fmjc__pkd = []
    for nnb__urns in range(len(left_key_types)):
        if left_key_in_output[nnb__urns]:
            fmjc__pkd.append(needs_typechange(matched_key_types[nnb__urns],
                join_node.is_right, nsxpp__jgxi[nnb__urns]))
    azx__clc = len(left_key_types)
    qpdvm__ttynn = 0
    mej__tohd = left_physical_to_logical_list[len(left_key_types):]
    for nnb__urns, mey__ngobi in enumerate(mej__tohd):
        clruz__ddqi = True
        if mey__ngobi in wfd__ujo:
            clruz__ddqi = left_key_in_output[azx__clc]
            azx__clc += 1
        if clruz__ddqi:
            fmjc__pkd.append(needs_typechange(left_other_types[nnb__urns],
                join_node.is_right, False))
    for nnb__urns in range(len(right_key_types)):
        if not nsxpp__jgxi[nnb__urns] and not join_node.is_join:
            if right_key_in_output[qpdvm__ttynn]:
                fmjc__pkd.append(needs_typechange(matched_key_types[
                    nnb__urns], join_node.is_left, False))
            qpdvm__ttynn += 1
    mtet__erd = right_physical_to_logical_list[len(right_key_types):]
    for nnb__urns, mey__ngobi in enumerate(mtet__erd):
        clruz__ddqi = True
        if mey__ngobi in grws__qbsjl:
            clruz__ddqi = right_key_in_output[qpdvm__ttynn]
            qpdvm__ttynn += 1
        if clruz__ddqi:
            fmjc__pkd.append(needs_typechange(right_other_types[nnb__urns],
                join_node.is_left, False))
    bbiyx__lcuj = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            hmpfn__vbo = left_other_names[1:]
            nxh__pffkv = left_other_names[0]
        else:
            hmpfn__vbo = left_other_names
            nxh__pffkv = None
        wwupn__rupa = '()' if len(hmpfn__vbo) == 0 else f'({hmpfn__vbo[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({nxh__pffkv}, {wwupn__rupa}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        vlwb__vxnia = []
        for nnb__urns in range(bbiyx__lcuj):
            vlwb__vxnia.append('t1_keys[{}]'.format(nnb__urns))
        for nnb__urns in range(len(left_other_names)):
            vlwb__vxnia.append('data_left[{}]'.format(nnb__urns))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(tts__yxxw) for tts__yxxw in vlwb__vxnia)
            )
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            ypq__bdh = right_other_names[1:]
            nxh__pffkv = right_other_names[0]
        else:
            ypq__bdh = right_other_names
            nxh__pffkv = None
        wwupn__rupa = '()' if len(ypq__bdh) == 0 else f'({ypq__bdh[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({nxh__pffkv}, {wwupn__rupa}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        mzpi__hrdi = []
        for nnb__urns in range(bbiyx__lcuj):
            mzpi__hrdi.append('t2_keys[{}]'.format(nnb__urns))
        for nnb__urns in range(len(right_other_names)):
            mzpi__hrdi.append('data_right[{}]'.format(nnb__urns))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(tts__yxxw) for tts__yxxw in mzpi__hrdi))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(nsxpp__jgxi, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(fmjc__pkd, dtype=np.int64)
    glbs['left_table_cond_columns'] = np.array(left_col_nums if len(
        left_col_nums) > 0 else [-1], dtype=np.int64)
    glbs['right_table_cond_columns'] = np.array(right_col_nums if len(
        right_col_nums) > 0 else [-1], dtype=np.int64)
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, key_in_output.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {}, total_rows_np.ctypes)
"""
        .format(left_parallel, right_parallel, bbiyx__lcuj, len(mej__tohd),
        len(mtet__erd), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    qiqs__wkkob = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {qiqs__wkkob}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        fkxev__attx = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{fkxev__attx}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        htln__krf = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        htln__krf.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        sexg__ozssx = False
        rdxc__nyqz = False
        if join_node.has_live_out_table_var:
            ojkmw__clcjk = list(out_table_type.arr_types)
        else:
            ojkmw__clcjk = None
        for vbq__dne, tvtc__zmmv in htln__krf.items():
            if vbq__dne < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                ojkmw__clcjk[vbq__dne] = tvtc__zmmv
                sexg__ozssx = True
            else:
                pvpe__tgfwt = tvtc__zmmv
                rdxc__nyqz = True
        if sexg__ozssx:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            pjnkp__ehv = bodo.TableType(tuple(ojkmw__clcjk))
            glbs['py_table_type'] = pjnkp__ehv
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if rdxc__nyqz:
            glbs['index_col_type'] = pvpe__tgfwt
            glbs['index_cast_type'] = index_col_type
            func_text += (
                f'    index_var = bodo.utils.utils.astype(index_var, index_cast_type)\n'
                )
    func_text += f'    out_table = T\n'
    func_text += f'    out_index = index_var\n'
    return func_text


def determine_table_cast_map(matched_key_types: List[types.Type], key_types:
    List[types.Type], used_key_nums: Optional[Set[int]], output_map:
    Optional[Dict[int, int]], convert_dict_col: bool, loc: ir.Loc):
    htln__krf: Dict[int, types.Type] = {}
    bbiyx__lcuj = len(matched_key_types)
    for nnb__urns in range(bbiyx__lcuj):
        if used_key_nums is None or nnb__urns in used_key_nums:
            if matched_key_types[nnb__urns] != key_types[nnb__urns] and (
                convert_dict_col or key_types[nnb__urns] != bodo.
                dict_str_arr_type):
                if output_map:
                    fkxev__attx = output_map[nnb__urns]
                else:
                    fkxev__attx = nnb__urns
                htln__krf[fkxev__attx] = matched_key_types[nnb__urns]
    return htln__krf


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    anc__vigh = bodo.libs.distributed_api.get_size()
    ubwl__sxs = np.empty(anc__vigh, left_key_arrs[0].dtype)
    lgpq__gvy = np.empty(anc__vigh, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(ubwl__sxs, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(lgpq__gvy, left_key_arrs[0][-1])
    rba__gil = np.zeros(anc__vigh, np.int32)
    ckfs__dfqhw = np.zeros(anc__vigh, np.int32)
    fesy__wcoz = np.zeros(anc__vigh, np.int32)
    brp__nnewe = right_key_arrs[0][0]
    qwqk__nvknk = right_key_arrs[0][-1]
    yunp__orecx = -1
    nnb__urns = 0
    while nnb__urns < anc__vigh - 1 and lgpq__gvy[nnb__urns] < brp__nnewe:
        nnb__urns += 1
    while nnb__urns < anc__vigh and ubwl__sxs[nnb__urns] <= qwqk__nvknk:
        yunp__orecx, ahkax__gzpo = _count_overlap(right_key_arrs[0],
            ubwl__sxs[nnb__urns], lgpq__gvy[nnb__urns])
        if yunp__orecx != 0:
            yunp__orecx -= 1
            ahkax__gzpo += 1
        rba__gil[nnb__urns] = ahkax__gzpo
        ckfs__dfqhw[nnb__urns] = yunp__orecx
        nnb__urns += 1
    while nnb__urns < anc__vigh:
        rba__gil[nnb__urns] = 1
        ckfs__dfqhw[nnb__urns] = len(right_key_arrs[0]) - 1
        nnb__urns += 1
    bodo.libs.distributed_api.alltoall(rba__gil, fesy__wcoz, 1)
    pbmrn__dxm = fesy__wcoz.sum()
    flbt__jqmpr = np.empty(pbmrn__dxm, right_key_arrs[0].dtype)
    sqgqn__feg = alloc_arr_tup(pbmrn__dxm, right_data)
    ohbg__adp = bodo.ir.join.calc_disp(fesy__wcoz)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], flbt__jqmpr,
        rba__gil, fesy__wcoz, ckfs__dfqhw, ohbg__adp)
    bodo.libs.distributed_api.alltoallv_tup(right_data, sqgqn__feg,
        rba__gil, fesy__wcoz, ckfs__dfqhw, ohbg__adp)
    return (flbt__jqmpr,), sqgqn__feg


@numba.njit
def _count_overlap(r_key_arr, start, end):
    ahkax__gzpo = 0
    yunp__orecx = 0
    wmnkz__sam = 0
    while wmnkz__sam < len(r_key_arr) and r_key_arr[wmnkz__sam] < start:
        yunp__orecx += 1
        wmnkz__sam += 1
    while wmnkz__sam < len(r_key_arr) and start <= r_key_arr[wmnkz__sam
        ] <= end:
        wmnkz__sam += 1
        ahkax__gzpo += 1
    return yunp__orecx, ahkax__gzpo


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    jjqis__vlf = np.empty_like(arr)
    jjqis__vlf[0] = 0
    for nnb__urns in range(1, len(arr)):
        jjqis__vlf[nnb__urns] = jjqis__vlf[nnb__urns - 1] + arr[nnb__urns - 1]
    return jjqis__vlf


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    yited__omy = len(left_keys[0])
    opanp__rcvx = len(right_keys[0])
    wpl__nbbj = alloc_arr_tup(yited__omy, left_keys)
    ogyon__oqws = alloc_arr_tup(yited__omy, right_keys)
    hhz__jrp = alloc_arr_tup(yited__omy, data_left)
    tloqw__ooa = alloc_arr_tup(yited__omy, data_right)
    vbrbx__qfssw = 0
    lke__nfqak = 0
    for vbrbx__qfssw in range(yited__omy):
        if lke__nfqak < 0:
            lke__nfqak = 0
        while lke__nfqak < opanp__rcvx and getitem_arr_tup(right_keys,
            lke__nfqak) <= getitem_arr_tup(left_keys, vbrbx__qfssw):
            lke__nfqak += 1
        lke__nfqak -= 1
        setitem_arr_tup(wpl__nbbj, vbrbx__qfssw, getitem_arr_tup(left_keys,
            vbrbx__qfssw))
        setitem_arr_tup(hhz__jrp, vbrbx__qfssw, getitem_arr_tup(data_left,
            vbrbx__qfssw))
        if lke__nfqak >= 0:
            setitem_arr_tup(ogyon__oqws, vbrbx__qfssw, getitem_arr_tup(
                right_keys, lke__nfqak))
            setitem_arr_tup(tloqw__ooa, vbrbx__qfssw, getitem_arr_tup(
                data_right, lke__nfqak))
        else:
            bodo.libs.array_kernels.setna_tup(ogyon__oqws, vbrbx__qfssw)
            bodo.libs.array_kernels.setna_tup(tloqw__ooa, vbrbx__qfssw)
    return wpl__nbbj, ogyon__oqws, hhz__jrp, tloqw__ooa
