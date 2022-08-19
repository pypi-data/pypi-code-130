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
        vnmjh__ukyz = func.signature
        vixov__ppay = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        tah__glbgm = cgutils.get_or_insert_function(builder.module,
            vixov__ppay, sym._literal_value)
        builder.call(tah__glbgm, [context.get_constant_null(vnmjh__ukyz.
            args[0]), context.get_constant_null(vnmjh__ukyz.args[1]),
            context.get_constant_null(vnmjh__ukyz.args[2]), context.
            get_constant_null(vnmjh__ukyz.args[3]), context.
            get_constant_null(vnmjh__ukyz.args[4]), context.
            get_constant_null(vnmjh__ukyz.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
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
        tsc__fgplm = left_df_type.columns
        skymn__cxr = right_df_type.columns
        self.left_col_names = tsc__fgplm
        self.right_col_names = skymn__cxr
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(tsc__fgplm) if self.is_left_table else 0
        self.n_right_table_cols = len(skymn__cxr) if self.is_right_table else 0
        hxt__bpsqw = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        vevc__hvjjx = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(hxt__bpsqw)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(vevc__hvjjx)
        self.left_var_map = {bvhq__wez: sait__epzze for sait__epzze,
            bvhq__wez in enumerate(tsc__fgplm)}
        self.right_var_map = {bvhq__wez: sait__epzze for sait__epzze,
            bvhq__wez in enumerate(skymn__cxr)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = hxt__bpsqw
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = vevc__hvjjx
        self.left_key_set = set(self.left_var_map[bvhq__wez] for bvhq__wez in
            left_keys)
        self.right_key_set = set(self.right_var_map[bvhq__wez] for
            bvhq__wez in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[bvhq__wez] for
                bvhq__wez in tsc__fgplm if f'(left.{bvhq__wez})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[bvhq__wez] for
                bvhq__wez in skymn__cxr if f'(right.{bvhq__wez})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        aeb__mgqrx: int = -1
        fmy__qlz = set(left_keys) & set(right_keys)
        ttrcp__pmsq = set(tsc__fgplm) & set(skymn__cxr)
        avj__zioqf = ttrcp__pmsq - fmy__qlz
        wjrt__goco: Dict[int, (Literal['left', 'right'], int)] = {}
        hoiaa__euzq: Dict[int, int] = {}
        flfq__nlg: Dict[int, int] = {}
        for sait__epzze, bvhq__wez in enumerate(tsc__fgplm):
            if bvhq__wez in avj__zioqf:
                jmo__xdm = str(bvhq__wez) + suffix_left
                zrrb__dqtri = out_df_type.column_index[jmo__xdm]
                if (right_index and not left_index and sait__epzze in self.
                    left_key_set):
                    aeb__mgqrx = out_df_type.column_index[bvhq__wez]
                    wjrt__goco[aeb__mgqrx] = 'left', sait__epzze
            else:
                zrrb__dqtri = out_df_type.column_index[bvhq__wez]
            wjrt__goco[zrrb__dqtri] = 'left', sait__epzze
            hoiaa__euzq[sait__epzze] = zrrb__dqtri
        for sait__epzze, bvhq__wez in enumerate(skymn__cxr):
            if bvhq__wez not in fmy__qlz:
                if bvhq__wez in avj__zioqf:
                    aot__mijeo = str(bvhq__wez) + suffix_right
                    zrrb__dqtri = out_df_type.column_index[aot__mijeo]
                    if (left_index and not right_index and sait__epzze in
                        self.right_key_set):
                        aeb__mgqrx = out_df_type.column_index[bvhq__wez]
                        wjrt__goco[aeb__mgqrx] = 'right', sait__epzze
                else:
                    zrrb__dqtri = out_df_type.column_index[bvhq__wez]
                wjrt__goco[zrrb__dqtri] = 'right', sait__epzze
                flfq__nlg[sait__epzze] = zrrb__dqtri
        if self.left_vars[-1] is not None:
            hoiaa__euzq[hxt__bpsqw] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            flfq__nlg[vevc__hvjjx] = self.n_out_table_cols
        self.out_to_input_col_map = wjrt__goco
        self.left_to_output_map = hoiaa__euzq
        self.right_to_output_map = flfq__nlg
        self.extra_data_col_num = aeb__mgqrx
        if len(out_data_vars) > 1:
            rlco__wava = 'left' if right_index else 'right'
            if rlco__wava == 'left':
                ihtn__ncyg = hxt__bpsqw
            elif rlco__wava == 'right':
                ihtn__ncyg = vevc__hvjjx
        else:
            rlco__wava = None
            ihtn__ncyg = -1
        self.index_source = rlco__wava
        self.index_col_num = ihtn__ncyg
        otv__rah = []
        wsomb__gew = len(left_keys)
        for yups__oocj in range(wsomb__gew):
            eir__dgr = left_keys[yups__oocj]
            pllm__pzdt = right_keys[yups__oocj]
            otv__rah.append(eir__dgr == pllm__pzdt)
        self.vect_same_key = otv__rah

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
        for pcqq__hjmnz in self.left_vars:
            if pcqq__hjmnz is not None:
                vars.append(pcqq__hjmnz)
        return vars

    def get_live_right_vars(self):
        vars = []
        for pcqq__hjmnz in self.right_vars:
            if pcqq__hjmnz is not None:
                vars.append(pcqq__hjmnz)
        return vars

    def get_live_out_vars(self):
        vars = []
        for pcqq__hjmnz in self.out_data_vars:
            if pcqq__hjmnz is not None:
                vars.append(pcqq__hjmnz)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        kpxe__cnjbg = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[kpxe__cnjbg])
                kpxe__cnjbg += 1
            else:
                left_vars.append(None)
            start = 1
        kfzsv__oqq = max(self.n_left_table_cols - 1, 0)
        for sait__epzze in range(start, len(self.left_vars)):
            if sait__epzze + kfzsv__oqq in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[kpxe__cnjbg])
                kpxe__cnjbg += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        kpxe__cnjbg = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[kpxe__cnjbg])
                kpxe__cnjbg += 1
            else:
                right_vars.append(None)
            start = 1
        kfzsv__oqq = max(self.n_right_table_cols - 1, 0)
        for sait__epzze in range(start, len(self.right_vars)):
            if sait__epzze + kfzsv__oqq in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[kpxe__cnjbg])
                kpxe__cnjbg += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        vxm__levx = [self.has_live_out_table_var, self.has_live_out_index_var]
        kpxe__cnjbg = 0
        for sait__epzze in range(len(self.out_data_vars)):
            if not vxm__levx[sait__epzze]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[kpxe__cnjbg])
                kpxe__cnjbg += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {sait__epzze for sait__epzze in self.out_used_cols if 
            sait__epzze < self.n_out_table_cols}

    def __repr__(self):
        gqrmj__bxdcm = ', '.join([f'{bvhq__wez}' for bvhq__wez in self.
            left_col_names])
        akxm__kvsoa = f'left={{{gqrmj__bxdcm}}}'
        gqrmj__bxdcm = ', '.join([f'{bvhq__wez}' for bvhq__wez in self.
            right_col_names])
        wbqtk__xwozy = f'right={{{gqrmj__bxdcm}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, akxm__kvsoa, wbqtk__xwozy)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    hvg__xifjd = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    idhj__rtafe = []
    ohwid__zqbmd = join_node.get_live_left_vars()
    for tcw__kav in ohwid__zqbmd:
        vlodd__xbl = typemap[tcw__kav.name]
        goeru__wukb = equiv_set.get_shape(tcw__kav)
        if goeru__wukb:
            idhj__rtafe.append(goeru__wukb[0])
    if len(idhj__rtafe) > 1:
        equiv_set.insert_equiv(*idhj__rtafe)
    idhj__rtafe = []
    ohwid__zqbmd = list(join_node.get_live_right_vars())
    for tcw__kav in ohwid__zqbmd:
        vlodd__xbl = typemap[tcw__kav.name]
        goeru__wukb = equiv_set.get_shape(tcw__kav)
        if goeru__wukb:
            idhj__rtafe.append(goeru__wukb[0])
    if len(idhj__rtafe) > 1:
        equiv_set.insert_equiv(*idhj__rtafe)
    idhj__rtafe = []
    for fydn__iqrq in join_node.get_live_out_vars():
        vlodd__xbl = typemap[fydn__iqrq.name]
        gpbmv__oyxl = array_analysis._gen_shape_call(equiv_set, fydn__iqrq,
            vlodd__xbl.ndim, None, hvg__xifjd)
        equiv_set.insert_equiv(fydn__iqrq, gpbmv__oyxl)
        idhj__rtafe.append(gpbmv__oyxl[0])
        equiv_set.define(fydn__iqrq, set())
    if len(idhj__rtafe) > 1:
        equiv_set.insert_equiv(*idhj__rtafe)
    return [], hvg__xifjd


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    ttp__yqnvz = Distribution.OneD
    kyr__nvs = Distribution.OneD
    for tcw__kav in join_node.get_live_left_vars():
        ttp__yqnvz = Distribution(min(ttp__yqnvz.value, array_dists[
            tcw__kav.name].value))
    for tcw__kav in join_node.get_live_right_vars():
        kyr__nvs = Distribution(min(kyr__nvs.value, array_dists[tcw__kav.
            name].value))
    xos__aay = Distribution.OneD_Var
    for fydn__iqrq in join_node.get_live_out_vars():
        if fydn__iqrq.name in array_dists:
            xos__aay = Distribution(min(xos__aay.value, array_dists[
                fydn__iqrq.name].value))
    wyin__gwrj = Distribution(min(xos__aay.value, ttp__yqnvz.value))
    myhnh__pxoht = Distribution(min(xos__aay.value, kyr__nvs.value))
    xos__aay = Distribution(max(wyin__gwrj.value, myhnh__pxoht.value))
    for fydn__iqrq in join_node.get_live_out_vars():
        array_dists[fydn__iqrq.name] = xos__aay
    if xos__aay != Distribution.OneD_Var:
        ttp__yqnvz = xos__aay
        kyr__nvs = xos__aay
    for tcw__kav in join_node.get_live_left_vars():
        array_dists[tcw__kav.name] = ttp__yqnvz
    for tcw__kav in join_node.get_live_right_vars():
        array_dists[tcw__kav.name] = kyr__nvs
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(pcqq__hjmnz, callback,
        cbdata) for pcqq__hjmnz in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(pcqq__hjmnz, callback,
        cbdata) for pcqq__hjmnz in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(pcqq__hjmnz,
        callback, cbdata) for pcqq__hjmnz in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        emq__kua = []
        hvcf__nbvqi = join_node.get_out_table_var()
        if hvcf__nbvqi.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for zrjdm__zezlv in join_node.out_to_input_col_map.keys():
            if zrjdm__zezlv in join_node.out_used_cols:
                continue
            emq__kua.append(zrjdm__zezlv)
            if join_node.indicator_col_num == zrjdm__zezlv:
                join_node.indicator_col_num = -1
                continue
            if zrjdm__zezlv == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            jkit__ldn, zrjdm__zezlv = join_node.out_to_input_col_map[
                zrjdm__zezlv]
            if jkit__ldn == 'left':
                if (zrjdm__zezlv not in join_node.left_key_set and 
                    zrjdm__zezlv not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(zrjdm__zezlv)
                    if not join_node.is_left_table:
                        join_node.left_vars[zrjdm__zezlv] = None
            elif jkit__ldn == 'right':
                if (zrjdm__zezlv not in join_node.right_key_set and 
                    zrjdm__zezlv not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(zrjdm__zezlv)
                    if not join_node.is_right_table:
                        join_node.right_vars[zrjdm__zezlv] = None
        for sait__epzze in emq__kua:
            del join_node.out_to_input_col_map[sait__epzze]
        if join_node.is_left_table:
            pdt__xlrnw = set(range(join_node.n_left_table_cols))
            lbm__sjb = not bool(pdt__xlrnw - join_node.left_dead_var_inds)
            if lbm__sjb:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            pdt__xlrnw = set(range(join_node.n_right_table_cols))
            lbm__sjb = not bool(pdt__xlrnw - join_node.right_dead_var_inds)
            if lbm__sjb:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        fsvfu__bahu = join_node.get_out_index_var()
        if fsvfu__bahu.name not in lives:
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
    muh__tbod = False
    if join_node.has_live_out_table_var:
        ooffv__nsx = join_node.get_out_table_var().name
        lxt__sfu, jme__akq, yamdi__omhyk = get_live_column_nums_block(
            column_live_map, equiv_vars, ooffv__nsx)
        if not (jme__akq or yamdi__omhyk):
            lxt__sfu = trim_extra_used_columns(lxt__sfu, join_node.
                n_out_table_cols)
            tytyg__fsso = join_node.get_out_table_used_cols()
            if len(lxt__sfu) != len(tytyg__fsso):
                muh__tbod = not (join_node.is_left_table and join_node.
                    is_right_table)
                cvhz__orzo = tytyg__fsso - lxt__sfu
                join_node.out_used_cols = join_node.out_used_cols - cvhz__orzo
    return muh__tbod


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        pwfl__kmpm = join_node.get_out_table_var()
        eca__uunml, jme__akq, yamdi__omhyk = _compute_table_column_uses(
            pwfl__kmpm.name, table_col_use_map, equiv_vars)
    else:
        eca__uunml, jme__akq, yamdi__omhyk = set(), False, False
    if join_node.has_live_left_table_var:
        rzz__qcapw = join_node.left_vars[0].name
        oryz__khlra, fydm__erv, slpsi__adrj = block_use_map[rzz__qcapw]
        if not (fydm__erv or slpsi__adrj):
            ghl__uadjy = set([join_node.out_to_input_col_map[sait__epzze][1
                ] for sait__epzze in eca__uunml if join_node.
                out_to_input_col_map[sait__epzze][0] == 'left'])
            ltfmk__dudj = set(sait__epzze for sait__epzze in join_node.
                left_key_set | join_node.left_cond_cols if sait__epzze <
                join_node.n_left_table_cols)
            if not (jme__akq or yamdi__omhyk):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (ghl__uadjy | ltfmk__dudj)
            block_use_map[rzz__qcapw] = (oryz__khlra | ghl__uadjy |
                ltfmk__dudj, jme__akq or yamdi__omhyk, False)
    if join_node.has_live_right_table_var:
        cdbkp__ahaq = join_node.right_vars[0].name
        oryz__khlra, fydm__erv, slpsi__adrj = block_use_map[cdbkp__ahaq]
        if not (fydm__erv or slpsi__adrj):
            iihe__qkdap = set([join_node.out_to_input_col_map[sait__epzze][
                1] for sait__epzze in eca__uunml if join_node.
                out_to_input_col_map[sait__epzze][0] == 'right'])
            wemly__towj = set(sait__epzze for sait__epzze in join_node.
                right_key_set | join_node.right_cond_cols if sait__epzze <
                join_node.n_right_table_cols)
            if not (jme__akq or yamdi__omhyk):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (iihe__qkdap | wemly__towj)
            block_use_map[cdbkp__ahaq] = (oryz__khlra | iihe__qkdap |
                wemly__towj, jme__akq or yamdi__omhyk, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({lmo__jwnfh.name for lmo__jwnfh in join_node.
        get_live_left_vars()})
    use_set.update({lmo__jwnfh.name for lmo__jwnfh in join_node.
        get_live_right_vars()})
    def_set.update({lmo__jwnfh.name for lmo__jwnfh in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    smah__zvt = set(lmo__jwnfh.name for lmo__jwnfh in join_node.
        get_live_out_vars())
    return set(), smah__zvt


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(pcqq__hjmnz, var_dict) for
        pcqq__hjmnz in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(pcqq__hjmnz, var_dict
        ) for pcqq__hjmnz in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(pcqq__hjmnz,
        var_dict) for pcqq__hjmnz in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for tcw__kav in join_node.get_live_out_vars():
        definitions[tcw__kav.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        dlzxn__bsqte = join_node.loc.strformat()
        vrzok__bcp = [join_node.left_col_names[sait__epzze] for sait__epzze in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        kxkqu__det = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', kxkqu__det,
            dlzxn__bsqte, vrzok__bcp)
        guty__wsvs = [join_node.right_col_names[sait__epzze] for
            sait__epzze in sorted(set(range(len(join_node.right_col_names))
            ) - join_node.right_dead_var_inds)]
        kxkqu__det = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', kxkqu__det,
            dlzxn__bsqte, guty__wsvs)
        yrj__rkl = [join_node.out_col_names[sait__epzze] for sait__epzze in
            sorted(join_node.get_out_table_used_cols())]
        kxkqu__det = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', kxkqu__det,
            dlzxn__bsqte, yrj__rkl)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    wsomb__gew = len(join_node.left_keys)
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
    nti__fatvo = 0
    hyppo__eyhe = 0
    ieva__sfupa = []
    for bvhq__wez in join_node.left_keys:
        hbngc__rjbc = join_node.left_var_map[bvhq__wez]
        if not join_node.is_left_table:
            ieva__sfupa.append(join_node.left_vars[hbngc__rjbc])
        vxm__levx = 1
        zrrb__dqtri = join_node.left_to_output_map[hbngc__rjbc]
        if bvhq__wez == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == hbngc__rjbc):
                out_physical_to_logical_list.append(zrrb__dqtri)
                left_used_key_nums.add(hbngc__rjbc)
            else:
                vxm__levx = 0
        elif zrrb__dqtri not in join_node.out_used_cols:
            vxm__levx = 0
        elif hbngc__rjbc in left_used_key_nums:
            vxm__levx = 0
        else:
            left_used_key_nums.add(hbngc__rjbc)
            out_physical_to_logical_list.append(zrrb__dqtri)
        left_physical_to_logical_list.append(hbngc__rjbc)
        left_logical_physical_map[hbngc__rjbc] = nti__fatvo
        nti__fatvo += 1
        left_key_in_output.append(vxm__levx)
    ieva__sfupa = tuple(ieva__sfupa)
    vgo__yzuqp = []
    for sait__epzze in range(len(join_node.left_col_names)):
        if (sait__epzze not in join_node.left_dead_var_inds and sait__epzze
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                lmo__jwnfh = join_node.left_vars[sait__epzze]
                vgo__yzuqp.append(lmo__jwnfh)
            eyfk__hrb = 1
            ccr__nephm = 1
            zrrb__dqtri = join_node.left_to_output_map[sait__epzze]
            if sait__epzze in join_node.left_cond_cols:
                if zrrb__dqtri not in join_node.out_used_cols:
                    eyfk__hrb = 0
                left_key_in_output.append(eyfk__hrb)
            elif sait__epzze in join_node.left_dead_var_inds:
                eyfk__hrb = 0
                ccr__nephm = 0
            if eyfk__hrb:
                out_physical_to_logical_list.append(zrrb__dqtri)
            if ccr__nephm:
                left_physical_to_logical_list.append(sait__epzze)
                left_logical_physical_map[sait__epzze] = nti__fatvo
                nti__fatvo += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            vgo__yzuqp.append(join_node.left_vars[join_node.index_col_num])
        zrrb__dqtri = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(zrrb__dqtri)
        left_physical_to_logical_list.append(join_node.index_col_num)
    vgo__yzuqp = tuple(vgo__yzuqp)
    if join_node.is_left_table:
        vgo__yzuqp = tuple(join_node.get_live_left_vars())
    avmhg__ghdh = []
    for sait__epzze, bvhq__wez in enumerate(join_node.right_keys):
        hbngc__rjbc = join_node.right_var_map[bvhq__wez]
        if not join_node.is_right_table:
            avmhg__ghdh.append(join_node.right_vars[hbngc__rjbc])
        if not join_node.vect_same_key[sait__epzze] and not join_node.is_join:
            vxm__levx = 1
            if hbngc__rjbc not in join_node.right_to_output_map:
                vxm__levx = 0
            else:
                zrrb__dqtri = join_node.right_to_output_map[hbngc__rjbc]
                if bvhq__wez == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        hbngc__rjbc):
                        out_physical_to_logical_list.append(zrrb__dqtri)
                        right_used_key_nums.add(hbngc__rjbc)
                    else:
                        vxm__levx = 0
                elif zrrb__dqtri not in join_node.out_used_cols:
                    vxm__levx = 0
                elif hbngc__rjbc in right_used_key_nums:
                    vxm__levx = 0
                else:
                    right_used_key_nums.add(hbngc__rjbc)
                    out_physical_to_logical_list.append(zrrb__dqtri)
            right_key_in_output.append(vxm__levx)
        right_physical_to_logical_list.append(hbngc__rjbc)
        right_logical_physical_map[hbngc__rjbc] = hyppo__eyhe
        hyppo__eyhe += 1
    avmhg__ghdh = tuple(avmhg__ghdh)
    udjm__haev = []
    for sait__epzze in range(len(join_node.right_col_names)):
        if (sait__epzze not in join_node.right_dead_var_inds and 
            sait__epzze not in join_node.right_key_set):
            if not join_node.is_right_table:
                udjm__haev.append(join_node.right_vars[sait__epzze])
            eyfk__hrb = 1
            ccr__nephm = 1
            zrrb__dqtri = join_node.right_to_output_map[sait__epzze]
            if sait__epzze in join_node.right_cond_cols:
                if zrrb__dqtri not in join_node.out_used_cols:
                    eyfk__hrb = 0
                right_key_in_output.append(eyfk__hrb)
            elif sait__epzze in join_node.right_dead_var_inds:
                eyfk__hrb = 0
                ccr__nephm = 0
            if eyfk__hrb:
                out_physical_to_logical_list.append(zrrb__dqtri)
            if ccr__nephm:
                right_physical_to_logical_list.append(sait__epzze)
                right_logical_physical_map[sait__epzze] = hyppo__eyhe
                hyppo__eyhe += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            udjm__haev.append(join_node.right_vars[join_node.index_col_num])
        zrrb__dqtri = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(zrrb__dqtri)
        right_physical_to_logical_list.append(join_node.index_col_num)
    udjm__haev = tuple(udjm__haev)
    if join_node.is_right_table:
        udjm__haev = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    qltcj__zzi = ieva__sfupa + avmhg__ghdh + vgo__yzuqp + udjm__haev
    kkpci__sbblw = tuple(typemap[lmo__jwnfh.name] for lmo__jwnfh in qltcj__zzi)
    left_other_names = tuple('t1_c' + str(sait__epzze) for sait__epzze in
        range(len(vgo__yzuqp)))
    right_other_names = tuple('t2_c' + str(sait__epzze) for sait__epzze in
        range(len(udjm__haev)))
    if join_node.is_left_table:
        ngvzy__gnv = ()
    else:
        ngvzy__gnv = tuple('t1_key' + str(sait__epzze) for sait__epzze in
            range(wsomb__gew))
    if join_node.is_right_table:
        gms__btc = ()
    else:
        gms__btc = tuple('t2_key' + str(sait__epzze) for sait__epzze in
            range(wsomb__gew))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(ngvzy__gnv + gms__btc +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            yyf__sjab = typemap[join_node.left_vars[0].name]
        else:
            yyf__sjab = types.none
        for tjje__vbmv in left_physical_to_logical_list:
            if tjje__vbmv < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                vlodd__xbl = yyf__sjab.arr_types[tjje__vbmv]
            else:
                vlodd__xbl = typemap[join_node.left_vars[-1].name]
            if tjje__vbmv in join_node.left_key_set:
                left_key_types.append(vlodd__xbl)
            else:
                left_other_types.append(vlodd__xbl)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[lmo__jwnfh.name] for lmo__jwnfh in
            ieva__sfupa)
        left_other_types = tuple([typemap[bvhq__wez.name] for bvhq__wez in
            vgo__yzuqp])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            yyf__sjab = typemap[join_node.right_vars[0].name]
        else:
            yyf__sjab = types.none
        for tjje__vbmv in right_physical_to_logical_list:
            if tjje__vbmv < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                vlodd__xbl = yyf__sjab.arr_types[tjje__vbmv]
            else:
                vlodd__xbl = typemap[join_node.right_vars[-1].name]
            if tjje__vbmv in join_node.right_key_set:
                right_key_types.append(vlodd__xbl)
            else:
                right_other_types.append(vlodd__xbl)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[lmo__jwnfh.name] for lmo__jwnfh in
            avmhg__ghdh)
        right_other_types = tuple([typemap[bvhq__wez.name] for bvhq__wez in
            udjm__haev])
    matched_key_types = []
    for sait__epzze in range(wsomb__gew):
        khim__uhn = _match_join_key_types(left_key_types[sait__epzze],
            right_key_types[sait__epzze], loc)
        glbs[f'key_type_{sait__epzze}'] = khim__uhn
        matched_key_types.append(khim__uhn)
    if join_node.is_left_table:
        tnzv__hkk = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if tnzv__hkk:
            kofk__fusd = False
            lkoi__povqv = False
            txzrv__kpviw = None
            if join_node.has_live_left_table_var:
                bkcz__rba = list(typemap[join_node.left_vars[0].name].arr_types
                    )
            else:
                bkcz__rba = None
            for zrjdm__zezlv, vlodd__xbl in tnzv__hkk.items():
                if zrjdm__zezlv < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    bkcz__rba[zrjdm__zezlv] = vlodd__xbl
                    kofk__fusd = True
                else:
                    txzrv__kpviw = vlodd__xbl
                    lkoi__povqv = True
            if kofk__fusd:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(bkcz__rba))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if lkoi__povqv:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = txzrv__kpviw
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({ngvzy__gnv[sait__epzze]}, key_type_{sait__epzze})'
             if left_key_types[sait__epzze] != matched_key_types[
            sait__epzze] else f'{ngvzy__gnv[sait__epzze]}' for sait__epzze in
            range(wsomb__gew)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        tnzv__hkk = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if tnzv__hkk:
            kofk__fusd = False
            lkoi__povqv = False
            txzrv__kpviw = None
            if join_node.has_live_right_table_var:
                bkcz__rba = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                bkcz__rba = None
            for zrjdm__zezlv, vlodd__xbl in tnzv__hkk.items():
                if zrjdm__zezlv < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    bkcz__rba[zrjdm__zezlv] = vlodd__xbl
                    kofk__fusd = True
                else:
                    txzrv__kpviw = vlodd__xbl
                    lkoi__povqv = True
            if kofk__fusd:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(bkcz__rba))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if lkoi__povqv:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = txzrv__kpviw
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({gms__btc[sait__epzze]}, key_type_{sait__epzze})'
             if right_key_types[sait__epzze] != matched_key_types[
            sait__epzze] else f'{gms__btc[sait__epzze]}' for sait__epzze in
            range(wsomb__gew)))
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
        for sait__epzze in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(sait__epzze
                , sait__epzze)
        for sait__epzze in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                sait__epzze, sait__epzze)
        for sait__epzze in range(wsomb__gew):
            func_text += (
                f'    t1_keys_{sait__epzze} = out_t1_keys[{sait__epzze}]\n')
        for sait__epzze in range(wsomb__gew):
            func_text += (
                f'    t2_keys_{sait__epzze} = out_t2_keys[{sait__epzze}]\n')
    gftgu__lohdy = {}
    exec(func_text, {}, gftgu__lohdy)
    cfqhh__eywsf = gftgu__lohdy['f']
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
    xczjc__kgpz = compile_to_numba_ir(cfqhh__eywsf, glbs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=kkpci__sbblw, typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(xczjc__kgpz, qltcj__zzi)
    tpl__ykvh = xczjc__kgpz.body[:-3]
    if join_node.has_live_out_index_var:
        tpl__ykvh[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        tpl__ykvh[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        tpl__ykvh.pop(-1)
    elif not join_node.has_live_out_table_var:
        tpl__ykvh.pop(-2)
    return tpl__ykvh


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    uhse__egn = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{uhse__egn}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    gftgu__lohdy = {}
    exec(func_text, table_getitem_funcs, gftgu__lohdy)
    irtr__ddpf = gftgu__lohdy[f'bodo_join_gen_cond{uhse__egn}']
    tooc__qzhmq = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    fkbw__lph = numba.cfunc(tooc__qzhmq, nopython=True)(irtr__ddpf)
    join_gen_cond_cfunc[fkbw__lph.native_name] = fkbw__lph
    join_gen_cond_cfunc_addr[fkbw__lph.native_name] = fkbw__lph.address
    return fkbw__lph, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    pxk__aba = []
    for bvhq__wez, iwm__sok in name_to_var_map.items():
        vzban__yjcv = f'({table_name}.{bvhq__wez})'
        if vzban__yjcv not in expr:
            continue
        atvk__kdu = f'getitem_{table_name}_val_{iwm__sok}'
        bptvr__kbup = f'_bodo_{table_name}_val_{iwm__sok}'
        if is_table_var:
            quctz__oyc = typemap[col_vars[0].name].arr_types[iwm__sok]
        else:
            quctz__oyc = typemap[col_vars[iwm__sok].name]
        if is_str_arr_type(quctz__oyc) or quctz__oyc == bodo.binary_array_type:
            func_text += f"""  {bptvr__kbup}, {bptvr__kbup}_size = {atvk__kdu}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {bptvr__kbup} = bodo.libs.str_arr_ext.decode_utf8({bptvr__kbup}, {bptvr__kbup}_size)
"""
        else:
            func_text += (
                f'  {bptvr__kbup} = {atvk__kdu}({table_name}_data1, {table_name}_ind)\n'
                )
        byqbp__qnrd = logical_to_physical_ind[iwm__sok]
        table_getitem_funcs[atvk__kdu
            ] = bodo.libs.array._gen_row_access_intrinsic(quctz__oyc,
            byqbp__qnrd)
        expr = expr.replace(vzban__yjcv, bptvr__kbup)
        pfzhi__pdr = f'({na_check_name}.{table_name}.{bvhq__wez})'
        if pfzhi__pdr in expr:
            pve__znmln = f'nacheck_{table_name}_val_{iwm__sok}'
            txsoc__anctv = f'_bodo_isna_{table_name}_val_{iwm__sok}'
            if isinstance(quctz__oyc, bodo.libs.int_arr_ext.IntegerArrayType
                ) or quctz__oyc in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(quctz__oyc):
                func_text += f"""  {txsoc__anctv} = {pve__znmln}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {txsoc__anctv} = {pve__znmln}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[pve__znmln
                ] = bodo.libs.array._gen_row_na_check_intrinsic(quctz__oyc,
                byqbp__qnrd)
            expr = expr.replace(pfzhi__pdr, txsoc__anctv)
        if iwm__sok not in key_set:
            pxk__aba.append(byqbp__qnrd)
    return expr, func_text, pxk__aba


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as cuz__deh:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    yzy__ntis = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[lmo__jwnfh.name] in yzy__ntis for
        lmo__jwnfh in join_node.get_live_left_vars())
    right_parallel = all(array_dists[lmo__jwnfh.name] in yzy__ntis for
        lmo__jwnfh in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[lmo__jwnfh.name] in yzy__ntis for
            lmo__jwnfh in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[lmo__jwnfh.name] in yzy__ntis for
            lmo__jwnfh in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[lmo__jwnfh.name] in yzy__ntis for lmo__jwnfh in
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
    eoizy__arjd = set(left_col_nums)
    srs__cmxyr = set(right_col_nums)
    otv__rah = join_node.vect_same_key
    qeq__oghw = []
    for sait__epzze in range(len(left_key_types)):
        if left_key_in_output[sait__epzze]:
            qeq__oghw.append(needs_typechange(matched_key_types[sait__epzze
                ], join_node.is_right, otv__rah[sait__epzze]))
    tpsqt__wwbfv = len(left_key_types)
    fpzl__yiwgs = 0
    csvd__qorg = left_physical_to_logical_list[len(left_key_types):]
    for sait__epzze, tjje__vbmv in enumerate(csvd__qorg):
        jwzr__aqmw = True
        if tjje__vbmv in eoizy__arjd:
            jwzr__aqmw = left_key_in_output[tpsqt__wwbfv]
            tpsqt__wwbfv += 1
        if jwzr__aqmw:
            qeq__oghw.append(needs_typechange(left_other_types[sait__epzze],
                join_node.is_right, False))
    for sait__epzze in range(len(right_key_types)):
        if not otv__rah[sait__epzze] and not join_node.is_join:
            if right_key_in_output[fpzl__yiwgs]:
                qeq__oghw.append(needs_typechange(matched_key_types[
                    sait__epzze], join_node.is_left, False))
            fpzl__yiwgs += 1
    ifzot__hemvd = right_physical_to_logical_list[len(right_key_types):]
    for sait__epzze, tjje__vbmv in enumerate(ifzot__hemvd):
        jwzr__aqmw = True
        if tjje__vbmv in srs__cmxyr:
            jwzr__aqmw = right_key_in_output[fpzl__yiwgs]
            fpzl__yiwgs += 1
        if jwzr__aqmw:
            qeq__oghw.append(needs_typechange(right_other_types[sait__epzze
                ], join_node.is_left, False))
    wsomb__gew = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            ncjbz__nemoq = left_other_names[1:]
            hvcf__nbvqi = left_other_names[0]
        else:
            ncjbz__nemoq = left_other_names
            hvcf__nbvqi = None
        iga__ukfur = '()' if len(ncjbz__nemoq
            ) == 0 else f'({ncjbz__nemoq[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({hvcf__nbvqi}, {iga__ukfur}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        jqa__tnt = []
        for sait__epzze in range(wsomb__gew):
            jqa__tnt.append('t1_keys[{}]'.format(sait__epzze))
        for sait__epzze in range(len(left_other_names)):
            jqa__tnt.append('data_left[{}]'.format(sait__epzze))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(nedg__ywo) for nedg__ywo in jqa__tnt))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            vpc__mcj = right_other_names[1:]
            hvcf__nbvqi = right_other_names[0]
        else:
            vpc__mcj = right_other_names
            hvcf__nbvqi = None
        iga__ukfur = '()' if len(vpc__mcj) == 0 else f'({vpc__mcj[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({hvcf__nbvqi}, {iga__ukfur}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        uvz__rij = []
        for sait__epzze in range(wsomb__gew):
            uvz__rij.append('t2_keys[{}]'.format(sait__epzze))
        for sait__epzze in range(len(right_other_names)):
            uvz__rij.append('data_right[{}]'.format(sait__epzze))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(nedg__ywo) for nedg__ywo in uvz__rij))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(otv__rah, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(qeq__oghw, dtype=np.int64)
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
        .format(left_parallel, right_parallel, wsomb__gew, len(csvd__qorg),
        len(ifzot__hemvd), join_node.is_left, join_node.is_right, join_node
        .is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    yfykw__cyo = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {yfykw__cyo}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        kpxe__cnjbg = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{kpxe__cnjbg}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        tnzv__hkk = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        tnzv__hkk.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        kofk__fusd = False
        lkoi__povqv = False
        if join_node.has_live_out_table_var:
            bkcz__rba = list(out_table_type.arr_types)
        else:
            bkcz__rba = None
        for zrjdm__zezlv, vlodd__xbl in tnzv__hkk.items():
            if zrjdm__zezlv < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                bkcz__rba[zrjdm__zezlv] = vlodd__xbl
                kofk__fusd = True
            else:
                txzrv__kpviw = vlodd__xbl
                lkoi__povqv = True
        if kofk__fusd:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            rfddz__zraj = bodo.TableType(tuple(bkcz__rba))
            glbs['py_table_type'] = rfddz__zraj
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if lkoi__povqv:
            glbs['index_col_type'] = txzrv__kpviw
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
    tnzv__hkk: Dict[int, types.Type] = {}
    wsomb__gew = len(matched_key_types)
    for sait__epzze in range(wsomb__gew):
        if used_key_nums is None or sait__epzze in used_key_nums:
            if matched_key_types[sait__epzze] != key_types[sait__epzze] and (
                convert_dict_col or key_types[sait__epzze] != bodo.
                dict_str_arr_type):
                if output_map:
                    kpxe__cnjbg = output_map[sait__epzze]
                else:
                    kpxe__cnjbg = sait__epzze
                tnzv__hkk[kpxe__cnjbg] = matched_key_types[sait__epzze]
    return tnzv__hkk


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    wqr__dmeag = bodo.libs.distributed_api.get_size()
    jwkdh__otltn = np.empty(wqr__dmeag, left_key_arrs[0].dtype)
    nrpkr__hyal = np.empty(wqr__dmeag, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(jwkdh__otltn, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(nrpkr__hyal, left_key_arrs[0][-1])
    tuhf__mgf = np.zeros(wqr__dmeag, np.int32)
    gny__qere = np.zeros(wqr__dmeag, np.int32)
    plbp__beeia = np.zeros(wqr__dmeag, np.int32)
    inyhp__fno = right_key_arrs[0][0]
    ueur__rgec = right_key_arrs[0][-1]
    kfzsv__oqq = -1
    sait__epzze = 0
    while sait__epzze < wqr__dmeag - 1 and nrpkr__hyal[sait__epzze
        ] < inyhp__fno:
        sait__epzze += 1
    while sait__epzze < wqr__dmeag and jwkdh__otltn[sait__epzze] <= ueur__rgec:
        kfzsv__oqq, iowti__wsc = _count_overlap(right_key_arrs[0],
            jwkdh__otltn[sait__epzze], nrpkr__hyal[sait__epzze])
        if kfzsv__oqq != 0:
            kfzsv__oqq -= 1
            iowti__wsc += 1
        tuhf__mgf[sait__epzze] = iowti__wsc
        gny__qere[sait__epzze] = kfzsv__oqq
        sait__epzze += 1
    while sait__epzze < wqr__dmeag:
        tuhf__mgf[sait__epzze] = 1
        gny__qere[sait__epzze] = len(right_key_arrs[0]) - 1
        sait__epzze += 1
    bodo.libs.distributed_api.alltoall(tuhf__mgf, plbp__beeia, 1)
    bypvp__cdn = plbp__beeia.sum()
    zke__hjeup = np.empty(bypvp__cdn, right_key_arrs[0].dtype)
    zqoum__tvu = alloc_arr_tup(bypvp__cdn, right_data)
    kcul__zlkfd = bodo.ir.join.calc_disp(plbp__beeia)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], zke__hjeup,
        tuhf__mgf, plbp__beeia, gny__qere, kcul__zlkfd)
    bodo.libs.distributed_api.alltoallv_tup(right_data, zqoum__tvu,
        tuhf__mgf, plbp__beeia, gny__qere, kcul__zlkfd)
    return (zke__hjeup,), zqoum__tvu


@numba.njit
def _count_overlap(r_key_arr, start, end):
    iowti__wsc = 0
    kfzsv__oqq = 0
    ghuri__xbac = 0
    while ghuri__xbac < len(r_key_arr) and r_key_arr[ghuri__xbac] < start:
        kfzsv__oqq += 1
        ghuri__xbac += 1
    while ghuri__xbac < len(r_key_arr) and start <= r_key_arr[ghuri__xbac
        ] <= end:
        ghuri__xbac += 1
        iowti__wsc += 1
    return kfzsv__oqq, iowti__wsc


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    swgxc__xjaj = np.empty_like(arr)
    swgxc__xjaj[0] = 0
    for sait__epzze in range(1, len(arr)):
        swgxc__xjaj[sait__epzze] = swgxc__xjaj[sait__epzze - 1] + arr[
            sait__epzze - 1]
    return swgxc__xjaj


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    anpip__hmmk = len(left_keys[0])
    jse__izr = len(right_keys[0])
    jml__lrako = alloc_arr_tup(anpip__hmmk, left_keys)
    fhtr__rlc = alloc_arr_tup(anpip__hmmk, right_keys)
    uvkvh__bfb = alloc_arr_tup(anpip__hmmk, data_left)
    ppxy__lfirq = alloc_arr_tup(anpip__hmmk, data_right)
    vajzv__tki = 0
    waigo__evo = 0
    for vajzv__tki in range(anpip__hmmk):
        if waigo__evo < 0:
            waigo__evo = 0
        while waigo__evo < jse__izr and getitem_arr_tup(right_keys, waigo__evo
            ) <= getitem_arr_tup(left_keys, vajzv__tki):
            waigo__evo += 1
        waigo__evo -= 1
        setitem_arr_tup(jml__lrako, vajzv__tki, getitem_arr_tup(left_keys,
            vajzv__tki))
        setitem_arr_tup(uvkvh__bfb, vajzv__tki, getitem_arr_tup(data_left,
            vajzv__tki))
        if waigo__evo >= 0:
            setitem_arr_tup(fhtr__rlc, vajzv__tki, getitem_arr_tup(
                right_keys, waigo__evo))
            setitem_arr_tup(ppxy__lfirq, vajzv__tki, getitem_arr_tup(
                data_right, waigo__evo))
        else:
            bodo.libs.array_kernels.setna_tup(fhtr__rlc, vajzv__tki)
            bodo.libs.array_kernels.setna_tup(ppxy__lfirq, vajzv__tki)
    return jml__lrako, fhtr__rlc, uvkvh__bfb, ppxy__lfirq
