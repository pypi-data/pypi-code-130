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
        zie__qmzu = func.signature
        jrgku__zsiv = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        wlgi__ssej = cgutils.get_or_insert_function(builder.module,
            jrgku__zsiv, sym._literal_value)
        builder.call(wlgi__ssej, [context.get_constant_null(zie__qmzu.args[
            0]), context.get_constant_null(zie__qmzu.args[1]), context.
            get_constant_null(zie__qmzu.args[2]), context.get_constant_null
            (zie__qmzu.args[3]), context.get_constant_null(zie__qmzu.args[4
            ]), context.get_constant_null(zie__qmzu.args[5]), context.
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
        luyz__yaaf = left_df_type.columns
        wdxqs__wxa = right_df_type.columns
        self.left_col_names = luyz__yaaf
        self.right_col_names = wdxqs__wxa
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(luyz__yaaf) if self.is_left_table else 0
        self.n_right_table_cols = len(wdxqs__wxa) if self.is_right_table else 0
        wthkd__ysi = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        gvggu__ttryc = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(wthkd__ysi)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(gvggu__ttryc)
        self.left_var_map = {sylnb__kas: eyhip__icsco for eyhip__icsco,
            sylnb__kas in enumerate(luyz__yaaf)}
        self.right_var_map = {sylnb__kas: eyhip__icsco for eyhip__icsco,
            sylnb__kas in enumerate(wdxqs__wxa)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = wthkd__ysi
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = gvggu__ttryc
        self.left_key_set = set(self.left_var_map[sylnb__kas] for
            sylnb__kas in left_keys)
        self.right_key_set = set(self.right_var_map[sylnb__kas] for
            sylnb__kas in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[sylnb__kas] for
                sylnb__kas in luyz__yaaf if f'(left.{sylnb__kas})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[sylnb__kas] for
                sylnb__kas in wdxqs__wxa if f'(right.{sylnb__kas})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        odqo__pkfbl: int = -1
        nwqsg__otkgh = set(left_keys) & set(right_keys)
        ozu__skcy = set(luyz__yaaf) & set(wdxqs__wxa)
        pfqk__hypf = ozu__skcy - nwqsg__otkgh
        yusd__fzz: Dict[int, (Literal['left', 'right'], int)] = {}
        kxyrf__uwj: Dict[int, int] = {}
        xhcj__boo: Dict[int, int] = {}
        for eyhip__icsco, sylnb__kas in enumerate(luyz__yaaf):
            if sylnb__kas in pfqk__hypf:
                ysli__ihtm = str(sylnb__kas) + suffix_left
                rqmh__yghem = out_df_type.column_index[ysli__ihtm]
                if (right_index and not left_index and eyhip__icsco in self
                    .left_key_set):
                    odqo__pkfbl = out_df_type.column_index[sylnb__kas]
                    yusd__fzz[odqo__pkfbl] = 'left', eyhip__icsco
            else:
                rqmh__yghem = out_df_type.column_index[sylnb__kas]
            yusd__fzz[rqmh__yghem] = 'left', eyhip__icsco
            kxyrf__uwj[eyhip__icsco] = rqmh__yghem
        for eyhip__icsco, sylnb__kas in enumerate(wdxqs__wxa):
            if sylnb__kas not in nwqsg__otkgh:
                if sylnb__kas in pfqk__hypf:
                    ohhrd__jqdxu = str(sylnb__kas) + suffix_right
                    rqmh__yghem = out_df_type.column_index[ohhrd__jqdxu]
                    if (left_index and not right_index and eyhip__icsco in
                        self.right_key_set):
                        odqo__pkfbl = out_df_type.column_index[sylnb__kas]
                        yusd__fzz[odqo__pkfbl] = 'right', eyhip__icsco
                else:
                    rqmh__yghem = out_df_type.column_index[sylnb__kas]
                yusd__fzz[rqmh__yghem] = 'right', eyhip__icsco
                xhcj__boo[eyhip__icsco] = rqmh__yghem
        if self.left_vars[-1] is not None:
            kxyrf__uwj[wthkd__ysi] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            xhcj__boo[gvggu__ttryc] = self.n_out_table_cols
        self.out_to_input_col_map = yusd__fzz
        self.left_to_output_map = kxyrf__uwj
        self.right_to_output_map = xhcj__boo
        self.extra_data_col_num = odqo__pkfbl
        if len(out_data_vars) > 1:
            sob__rkvqs = 'left' if right_index else 'right'
            if sob__rkvqs == 'left':
                sqym__lpcn = wthkd__ysi
            elif sob__rkvqs == 'right':
                sqym__lpcn = gvggu__ttryc
        else:
            sob__rkvqs = None
            sqym__lpcn = -1
        self.index_source = sob__rkvqs
        self.index_col_num = sqym__lpcn
        btg__rzvo = []
        lsz__hkbm = len(left_keys)
        for ytve__mzhr in range(lsz__hkbm):
            hii__nil = left_keys[ytve__mzhr]
            evf__wxiqy = right_keys[ytve__mzhr]
            btg__rzvo.append(hii__nil == evf__wxiqy)
        self.vect_same_key = btg__rzvo

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
        for mjd__kxwsn in self.left_vars:
            if mjd__kxwsn is not None:
                vars.append(mjd__kxwsn)
        return vars

    def get_live_right_vars(self):
        vars = []
        for mjd__kxwsn in self.right_vars:
            if mjd__kxwsn is not None:
                vars.append(mjd__kxwsn)
        return vars

    def get_live_out_vars(self):
        vars = []
        for mjd__kxwsn in self.out_data_vars:
            if mjd__kxwsn is not None:
                vars.append(mjd__kxwsn)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        oosgq__scj = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[oosgq__scj])
                oosgq__scj += 1
            else:
                left_vars.append(None)
            start = 1
        kis__bdqe = max(self.n_left_table_cols - 1, 0)
        for eyhip__icsco in range(start, len(self.left_vars)):
            if eyhip__icsco + kis__bdqe in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[oosgq__scj])
                oosgq__scj += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        oosgq__scj = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[oosgq__scj])
                oosgq__scj += 1
            else:
                right_vars.append(None)
            start = 1
        kis__bdqe = max(self.n_right_table_cols - 1, 0)
        for eyhip__icsco in range(start, len(self.right_vars)):
            if eyhip__icsco + kis__bdqe in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[oosgq__scj])
                oosgq__scj += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        mtwjl__ipsdx = [self.has_live_out_table_var, self.
            has_live_out_index_var]
        oosgq__scj = 0
        for eyhip__icsco in range(len(self.out_data_vars)):
            if not mtwjl__ipsdx[eyhip__icsco]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[oosgq__scj])
                oosgq__scj += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {eyhip__icsco for eyhip__icsco in self.out_used_cols if 
            eyhip__icsco < self.n_out_table_cols}

    def __repr__(self):
        kum__pcu = ', '.join([f'{sylnb__kas}' for sylnb__kas in self.
            left_col_names])
        dlhik__juvau = f'left={{{kum__pcu}}}'
        kum__pcu = ', '.join([f'{sylnb__kas}' for sylnb__kas in self.
            right_col_names])
        lgqf__datdc = f'right={{{kum__pcu}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, dlhik__juvau, lgqf__datdc)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    khksa__jptgj = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    pvc__gtd = []
    skbqs__rvw = join_node.get_live_left_vars()
    for uxfzt__cvh in skbqs__rvw:
        tgp__fyhi = typemap[uxfzt__cvh.name]
        qrz__nhn = equiv_set.get_shape(uxfzt__cvh)
        if qrz__nhn:
            pvc__gtd.append(qrz__nhn[0])
    if len(pvc__gtd) > 1:
        equiv_set.insert_equiv(*pvc__gtd)
    pvc__gtd = []
    skbqs__rvw = list(join_node.get_live_right_vars())
    for uxfzt__cvh in skbqs__rvw:
        tgp__fyhi = typemap[uxfzt__cvh.name]
        qrz__nhn = equiv_set.get_shape(uxfzt__cvh)
        if qrz__nhn:
            pvc__gtd.append(qrz__nhn[0])
    if len(pvc__gtd) > 1:
        equiv_set.insert_equiv(*pvc__gtd)
    pvc__gtd = []
    for saws__gnx in join_node.get_live_out_vars():
        tgp__fyhi = typemap[saws__gnx.name]
        exb__vwtre = array_analysis._gen_shape_call(equiv_set, saws__gnx,
            tgp__fyhi.ndim, None, khksa__jptgj)
        equiv_set.insert_equiv(saws__gnx, exb__vwtre)
        pvc__gtd.append(exb__vwtre[0])
        equiv_set.define(saws__gnx, set())
    if len(pvc__gtd) > 1:
        equiv_set.insert_equiv(*pvc__gtd)
    return [], khksa__jptgj


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    rxert__mrcdo = Distribution.OneD
    tuqa__jqse = Distribution.OneD
    for uxfzt__cvh in join_node.get_live_left_vars():
        rxert__mrcdo = Distribution(min(rxert__mrcdo.value, array_dists[
            uxfzt__cvh.name].value))
    for uxfzt__cvh in join_node.get_live_right_vars():
        tuqa__jqse = Distribution(min(tuqa__jqse.value, array_dists[
            uxfzt__cvh.name].value))
    wxw__ehz = Distribution.OneD_Var
    for saws__gnx in join_node.get_live_out_vars():
        if saws__gnx.name in array_dists:
            wxw__ehz = Distribution(min(wxw__ehz.value, array_dists[
                saws__gnx.name].value))
    itsu__amajh = Distribution(min(wxw__ehz.value, rxert__mrcdo.value))
    cfzva__nkhao = Distribution(min(wxw__ehz.value, tuqa__jqse.value))
    wxw__ehz = Distribution(max(itsu__amajh.value, cfzva__nkhao.value))
    for saws__gnx in join_node.get_live_out_vars():
        array_dists[saws__gnx.name] = wxw__ehz
    if wxw__ehz != Distribution.OneD_Var:
        rxert__mrcdo = wxw__ehz
        tuqa__jqse = wxw__ehz
    for uxfzt__cvh in join_node.get_live_left_vars():
        array_dists[uxfzt__cvh.name] = rxert__mrcdo
    for uxfzt__cvh in join_node.get_live_right_vars():
        array_dists[uxfzt__cvh.name] = tuqa__jqse
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(mjd__kxwsn, callback,
        cbdata) for mjd__kxwsn in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(mjd__kxwsn, callback,
        cbdata) for mjd__kxwsn in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(mjd__kxwsn, callback,
        cbdata) for mjd__kxwsn in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        bdd__qylh = []
        ash__pqa = join_node.get_out_table_var()
        if ash__pqa.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for hlol__iost in join_node.out_to_input_col_map.keys():
            if hlol__iost in join_node.out_used_cols:
                continue
            bdd__qylh.append(hlol__iost)
            if join_node.indicator_col_num == hlol__iost:
                join_node.indicator_col_num = -1
                continue
            if hlol__iost == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            dcc__vleta, hlol__iost = join_node.out_to_input_col_map[hlol__iost]
            if dcc__vleta == 'left':
                if (hlol__iost not in join_node.left_key_set and hlol__iost
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(hlol__iost)
                    if not join_node.is_left_table:
                        join_node.left_vars[hlol__iost] = None
            elif dcc__vleta == 'right':
                if (hlol__iost not in join_node.right_key_set and 
                    hlol__iost not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(hlol__iost)
                    if not join_node.is_right_table:
                        join_node.right_vars[hlol__iost] = None
        for eyhip__icsco in bdd__qylh:
            del join_node.out_to_input_col_map[eyhip__icsco]
        if join_node.is_left_table:
            tinqm__itc = set(range(join_node.n_left_table_cols))
            qwpv__rea = not bool(tinqm__itc - join_node.left_dead_var_inds)
            if qwpv__rea:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            tinqm__itc = set(range(join_node.n_right_table_cols))
            qwpv__rea = not bool(tinqm__itc - join_node.right_dead_var_inds)
            if qwpv__rea:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        tnwh__ntmqp = join_node.get_out_index_var()
        if tnwh__ntmqp.name not in lives:
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
    fiur__ogrj = False
    if join_node.has_live_out_table_var:
        ioedl__yxc = join_node.get_out_table_var().name
        qsuf__thyv, xqkzo__msvp, smj__exaj = get_live_column_nums_block(
            column_live_map, equiv_vars, ioedl__yxc)
        if not (xqkzo__msvp or smj__exaj):
            qsuf__thyv = trim_extra_used_columns(qsuf__thyv, join_node.
                n_out_table_cols)
            fdzkn__qvui = join_node.get_out_table_used_cols()
            if len(qsuf__thyv) != len(fdzkn__qvui):
                fiur__ogrj = not (join_node.is_left_table and join_node.
                    is_right_table)
                cum__ttyg = fdzkn__qvui - qsuf__thyv
                join_node.out_used_cols = join_node.out_used_cols - cum__ttyg
    return fiur__ogrj


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        mfwrv__lqa = join_node.get_out_table_var()
        uji__zbv, xqkzo__msvp, smj__exaj = _compute_table_column_uses(
            mfwrv__lqa.name, table_col_use_map, equiv_vars)
    else:
        uji__zbv, xqkzo__msvp, smj__exaj = set(), False, False
    if join_node.has_live_left_table_var:
        hofrg__yxm = join_node.left_vars[0].name
        meqo__atoo, rxh__nzyiw, gie__vjpz = block_use_map[hofrg__yxm]
        if not (rxh__nzyiw or gie__vjpz):
            htnaj__eui = set([join_node.out_to_input_col_map[eyhip__icsco][
                1] for eyhip__icsco in uji__zbv if join_node.
                out_to_input_col_map[eyhip__icsco][0] == 'left'])
            hoyth__rsfxq = set(eyhip__icsco for eyhip__icsco in join_node.
                left_key_set | join_node.left_cond_cols if eyhip__icsco <
                join_node.n_left_table_cols)
            if not (xqkzo__msvp or smj__exaj):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (htnaj__eui | hoyth__rsfxq)
            block_use_map[hofrg__yxm] = (meqo__atoo | htnaj__eui |
                hoyth__rsfxq, xqkzo__msvp or smj__exaj, False)
    if join_node.has_live_right_table_var:
        ltxur__zohym = join_node.right_vars[0].name
        meqo__atoo, rxh__nzyiw, gie__vjpz = block_use_map[ltxur__zohym]
        if not (rxh__nzyiw or gie__vjpz):
            ldyv__pigi = set([join_node.out_to_input_col_map[eyhip__icsco][
                1] for eyhip__icsco in uji__zbv if join_node.
                out_to_input_col_map[eyhip__icsco][0] == 'right'])
            dfqa__tths = set(eyhip__icsco for eyhip__icsco in join_node.
                right_key_set | join_node.right_cond_cols if eyhip__icsco <
                join_node.n_right_table_cols)
            if not (xqkzo__msvp or smj__exaj):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (ldyv__pigi | dfqa__tths)
            block_use_map[ltxur__zohym] = (meqo__atoo | ldyv__pigi |
                dfqa__tths, xqkzo__msvp or smj__exaj, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({oijmg__omon.name for oijmg__omon in join_node.
        get_live_left_vars()})
    use_set.update({oijmg__omon.name for oijmg__omon in join_node.
        get_live_right_vars()})
    def_set.update({oijmg__omon.name for oijmg__omon in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    ajc__fvrwi = set(oijmg__omon.name for oijmg__omon in join_node.
        get_live_out_vars())
    return set(), ajc__fvrwi


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(mjd__kxwsn, var_dict) for
        mjd__kxwsn in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(mjd__kxwsn, var_dict) for
        mjd__kxwsn in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(mjd__kxwsn,
        var_dict) for mjd__kxwsn in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for uxfzt__cvh in join_node.get_live_out_vars():
        definitions[uxfzt__cvh.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        wujf__bnu = join_node.loc.strformat()
        cdffo__ikbyd = [join_node.left_col_names[eyhip__icsco] for
            eyhip__icsco in sorted(set(range(len(join_node.left_col_names))
            ) - join_node.left_dead_var_inds)]
        chiqb__rwk = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', chiqb__rwk,
            wujf__bnu, cdffo__ikbyd)
        icu__xdx = [join_node.right_col_names[eyhip__icsco] for
            eyhip__icsco in sorted(set(range(len(join_node.right_col_names)
            )) - join_node.right_dead_var_inds)]
        chiqb__rwk = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', chiqb__rwk,
            wujf__bnu, icu__xdx)
        dsph__podre = [join_node.out_col_names[eyhip__icsco] for
            eyhip__icsco in sorted(join_node.get_out_table_used_cols())]
        chiqb__rwk = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', chiqb__rwk,
            wujf__bnu, dsph__podre)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    lsz__hkbm = len(join_node.left_keys)
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
    xuf__vaakn = 0
    jnb__xgpz = 0
    cbj__aqel = []
    for sylnb__kas in join_node.left_keys:
        tof__ulzyq = join_node.left_var_map[sylnb__kas]
        if not join_node.is_left_table:
            cbj__aqel.append(join_node.left_vars[tof__ulzyq])
        mtwjl__ipsdx = 1
        rqmh__yghem = join_node.left_to_output_map[tof__ulzyq]
        if sylnb__kas == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == tof__ulzyq):
                out_physical_to_logical_list.append(rqmh__yghem)
                left_used_key_nums.add(tof__ulzyq)
            else:
                mtwjl__ipsdx = 0
        elif rqmh__yghem not in join_node.out_used_cols:
            mtwjl__ipsdx = 0
        elif tof__ulzyq in left_used_key_nums:
            mtwjl__ipsdx = 0
        else:
            left_used_key_nums.add(tof__ulzyq)
            out_physical_to_logical_list.append(rqmh__yghem)
        left_physical_to_logical_list.append(tof__ulzyq)
        left_logical_physical_map[tof__ulzyq] = xuf__vaakn
        xuf__vaakn += 1
        left_key_in_output.append(mtwjl__ipsdx)
    cbj__aqel = tuple(cbj__aqel)
    yctg__ixc = []
    for eyhip__icsco in range(len(join_node.left_col_names)):
        if (eyhip__icsco not in join_node.left_dead_var_inds and 
            eyhip__icsco not in join_node.left_key_set):
            if not join_node.is_left_table:
                oijmg__omon = join_node.left_vars[eyhip__icsco]
                yctg__ixc.append(oijmg__omon)
            dsab__tjkzh = 1
            tki__rnwar = 1
            rqmh__yghem = join_node.left_to_output_map[eyhip__icsco]
            if eyhip__icsco in join_node.left_cond_cols:
                if rqmh__yghem not in join_node.out_used_cols:
                    dsab__tjkzh = 0
                left_key_in_output.append(dsab__tjkzh)
            elif eyhip__icsco in join_node.left_dead_var_inds:
                dsab__tjkzh = 0
                tki__rnwar = 0
            if dsab__tjkzh:
                out_physical_to_logical_list.append(rqmh__yghem)
            if tki__rnwar:
                left_physical_to_logical_list.append(eyhip__icsco)
                left_logical_physical_map[eyhip__icsco] = xuf__vaakn
                xuf__vaakn += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            yctg__ixc.append(join_node.left_vars[join_node.index_col_num])
        rqmh__yghem = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rqmh__yghem)
        left_physical_to_logical_list.append(join_node.index_col_num)
    yctg__ixc = tuple(yctg__ixc)
    if join_node.is_left_table:
        yctg__ixc = tuple(join_node.get_live_left_vars())
    rig__jmu = []
    for eyhip__icsco, sylnb__kas in enumerate(join_node.right_keys):
        tof__ulzyq = join_node.right_var_map[sylnb__kas]
        if not join_node.is_right_table:
            rig__jmu.append(join_node.right_vars[tof__ulzyq])
        if not join_node.vect_same_key[eyhip__icsco] and not join_node.is_join:
            mtwjl__ipsdx = 1
            if tof__ulzyq not in join_node.right_to_output_map:
                mtwjl__ipsdx = 0
            else:
                rqmh__yghem = join_node.right_to_output_map[tof__ulzyq]
                if sylnb__kas == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        tof__ulzyq):
                        out_physical_to_logical_list.append(rqmh__yghem)
                        right_used_key_nums.add(tof__ulzyq)
                    else:
                        mtwjl__ipsdx = 0
                elif rqmh__yghem not in join_node.out_used_cols:
                    mtwjl__ipsdx = 0
                elif tof__ulzyq in right_used_key_nums:
                    mtwjl__ipsdx = 0
                else:
                    right_used_key_nums.add(tof__ulzyq)
                    out_physical_to_logical_list.append(rqmh__yghem)
            right_key_in_output.append(mtwjl__ipsdx)
        right_physical_to_logical_list.append(tof__ulzyq)
        right_logical_physical_map[tof__ulzyq] = jnb__xgpz
        jnb__xgpz += 1
    rig__jmu = tuple(rig__jmu)
    phmz__gbwe = []
    for eyhip__icsco in range(len(join_node.right_col_names)):
        if (eyhip__icsco not in join_node.right_dead_var_inds and 
            eyhip__icsco not in join_node.right_key_set):
            if not join_node.is_right_table:
                phmz__gbwe.append(join_node.right_vars[eyhip__icsco])
            dsab__tjkzh = 1
            tki__rnwar = 1
            rqmh__yghem = join_node.right_to_output_map[eyhip__icsco]
            if eyhip__icsco in join_node.right_cond_cols:
                if rqmh__yghem not in join_node.out_used_cols:
                    dsab__tjkzh = 0
                right_key_in_output.append(dsab__tjkzh)
            elif eyhip__icsco in join_node.right_dead_var_inds:
                dsab__tjkzh = 0
                tki__rnwar = 0
            if dsab__tjkzh:
                out_physical_to_logical_list.append(rqmh__yghem)
            if tki__rnwar:
                right_physical_to_logical_list.append(eyhip__icsco)
                right_logical_physical_map[eyhip__icsco] = jnb__xgpz
                jnb__xgpz += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            phmz__gbwe.append(join_node.right_vars[join_node.index_col_num])
        rqmh__yghem = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rqmh__yghem)
        right_physical_to_logical_list.append(join_node.index_col_num)
    phmz__gbwe = tuple(phmz__gbwe)
    if join_node.is_right_table:
        phmz__gbwe = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    sjn__uaw = cbj__aqel + rig__jmu + yctg__ixc + phmz__gbwe
    kmc__lcg = tuple(typemap[oijmg__omon.name] for oijmg__omon in sjn__uaw)
    left_other_names = tuple('t1_c' + str(eyhip__icsco) for eyhip__icsco in
        range(len(yctg__ixc)))
    right_other_names = tuple('t2_c' + str(eyhip__icsco) for eyhip__icsco in
        range(len(phmz__gbwe)))
    if join_node.is_left_table:
        ugyt__avwgu = ()
    else:
        ugyt__avwgu = tuple('t1_key' + str(eyhip__icsco) for eyhip__icsco in
            range(lsz__hkbm))
    if join_node.is_right_table:
        hlxlb__zxr = ()
    else:
        hlxlb__zxr = tuple('t2_key' + str(eyhip__icsco) for eyhip__icsco in
            range(lsz__hkbm))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(ugyt__avwgu + hlxlb__zxr +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            togo__oxq = typemap[join_node.left_vars[0].name]
        else:
            togo__oxq = types.none
        for anxu__pmubp in left_physical_to_logical_list:
            if anxu__pmubp < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                tgp__fyhi = togo__oxq.arr_types[anxu__pmubp]
            else:
                tgp__fyhi = typemap[join_node.left_vars[-1].name]
            if anxu__pmubp in join_node.left_key_set:
                left_key_types.append(tgp__fyhi)
            else:
                left_other_types.append(tgp__fyhi)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[oijmg__omon.name] for oijmg__omon in
            cbj__aqel)
        left_other_types = tuple([typemap[sylnb__kas.name] for sylnb__kas in
            yctg__ixc])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            togo__oxq = typemap[join_node.right_vars[0].name]
        else:
            togo__oxq = types.none
        for anxu__pmubp in right_physical_to_logical_list:
            if anxu__pmubp < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                tgp__fyhi = togo__oxq.arr_types[anxu__pmubp]
            else:
                tgp__fyhi = typemap[join_node.right_vars[-1].name]
            if anxu__pmubp in join_node.right_key_set:
                right_key_types.append(tgp__fyhi)
            else:
                right_other_types.append(tgp__fyhi)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[oijmg__omon.name] for oijmg__omon in
            rig__jmu)
        right_other_types = tuple([typemap[sylnb__kas.name] for sylnb__kas in
            phmz__gbwe])
    matched_key_types = []
    for eyhip__icsco in range(lsz__hkbm):
        fbbl__yxxp = _match_join_key_types(left_key_types[eyhip__icsco],
            right_key_types[eyhip__icsco], loc)
        glbs[f'key_type_{eyhip__icsco}'] = fbbl__yxxp
        matched_key_types.append(fbbl__yxxp)
    if join_node.is_left_table:
        kzwfo__ithyc = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if kzwfo__ithyc:
            ahm__wtcr = False
            uxs__arkde = False
            xfg__oan = None
            if join_node.has_live_left_table_var:
                kwf__ffc = list(typemap[join_node.left_vars[0].name].arr_types)
            else:
                kwf__ffc = None
            for hlol__iost, tgp__fyhi in kzwfo__ithyc.items():
                if hlol__iost < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    kwf__ffc[hlol__iost] = tgp__fyhi
                    ahm__wtcr = True
                else:
                    xfg__oan = tgp__fyhi
                    uxs__arkde = True
            if ahm__wtcr:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(kwf__ffc))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if uxs__arkde:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = xfg__oan
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({ugyt__avwgu[eyhip__icsco]}, key_type_{eyhip__icsco})'
             if left_key_types[eyhip__icsco] != matched_key_types[
            eyhip__icsco] else f'{ugyt__avwgu[eyhip__icsco]}' for
            eyhip__icsco in range(lsz__hkbm)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        kzwfo__ithyc = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if kzwfo__ithyc:
            ahm__wtcr = False
            uxs__arkde = False
            xfg__oan = None
            if join_node.has_live_right_table_var:
                kwf__ffc = list(typemap[join_node.right_vars[0].name].arr_types
                    )
            else:
                kwf__ffc = None
            for hlol__iost, tgp__fyhi in kzwfo__ithyc.items():
                if hlol__iost < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    kwf__ffc[hlol__iost] = tgp__fyhi
                    ahm__wtcr = True
                else:
                    xfg__oan = tgp__fyhi
                    uxs__arkde = True
            if ahm__wtcr:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(kwf__ffc))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if uxs__arkde:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = xfg__oan
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({hlxlb__zxr[eyhip__icsco]}, key_type_{eyhip__icsco})'
             if right_key_types[eyhip__icsco] != matched_key_types[
            eyhip__icsco] else f'{hlxlb__zxr[eyhip__icsco]}' for
            eyhip__icsco in range(lsz__hkbm)))
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
        for eyhip__icsco in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(
                eyhip__icsco, eyhip__icsco)
        for eyhip__icsco in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                eyhip__icsco, eyhip__icsco)
        for eyhip__icsco in range(lsz__hkbm):
            func_text += (
                f'    t1_keys_{eyhip__icsco} = out_t1_keys[{eyhip__icsco}]\n')
        for eyhip__icsco in range(lsz__hkbm):
            func_text += (
                f'    t2_keys_{eyhip__icsco} = out_t2_keys[{eyhip__icsco}]\n')
    kuef__ggjol = {}
    exec(func_text, {}, kuef__ggjol)
    koz__und = kuef__ggjol['f']
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
    uyks__fzuxa = compile_to_numba_ir(koz__und, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=kmc__lcg, typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(uyks__fzuxa, sjn__uaw)
    uvi__rpy = uyks__fzuxa.body[:-3]
    if join_node.has_live_out_index_var:
        uvi__rpy[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        uvi__rpy[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        uvi__rpy.pop(-1)
    elif not join_node.has_live_out_table_var:
        uvi__rpy.pop(-2)
    return uvi__rpy


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    ltc__cwbk = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{ltc__cwbk}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    kuef__ggjol = {}
    exec(func_text, table_getitem_funcs, kuef__ggjol)
    rjbu__bmr = kuef__ggjol[f'bodo_join_gen_cond{ltc__cwbk}']
    phnwx__qmp = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    shml__eyc = numba.cfunc(phnwx__qmp, nopython=True)(rjbu__bmr)
    join_gen_cond_cfunc[shml__eyc.native_name] = shml__eyc
    join_gen_cond_cfunc_addr[shml__eyc.native_name] = shml__eyc.address
    return shml__eyc, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    ied__gnjo = []
    for sylnb__kas, ken__yeg in name_to_var_map.items():
        niz__jzo = f'({table_name}.{sylnb__kas})'
        if niz__jzo not in expr:
            continue
        nrzhm__tpwk = f'getitem_{table_name}_val_{ken__yeg}'
        xzlp__nah = f'_bodo_{table_name}_val_{ken__yeg}'
        if is_table_var:
            owtwa__azg = typemap[col_vars[0].name].arr_types[ken__yeg]
        else:
            owtwa__azg = typemap[col_vars[ken__yeg].name]
        if is_str_arr_type(owtwa__azg) or owtwa__azg == bodo.binary_array_type:
            func_text += f"""  {xzlp__nah}, {xzlp__nah}_size = {nrzhm__tpwk}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {xzlp__nah} = bodo.libs.str_arr_ext.decode_utf8({xzlp__nah}, {xzlp__nah}_size)
"""
        else:
            func_text += (
                f'  {xzlp__nah} = {nrzhm__tpwk}({table_name}_data1, {table_name}_ind)\n'
                )
        esmju__cmzsb = logical_to_physical_ind[ken__yeg]
        table_getitem_funcs[nrzhm__tpwk
            ] = bodo.libs.array._gen_row_access_intrinsic(owtwa__azg,
            esmju__cmzsb)
        expr = expr.replace(niz__jzo, xzlp__nah)
        cuh__ispz = f'({na_check_name}.{table_name}.{sylnb__kas})'
        if cuh__ispz in expr:
            wlwzg__mac = f'nacheck_{table_name}_val_{ken__yeg}'
            wmh__gryg = f'_bodo_isna_{table_name}_val_{ken__yeg}'
            if isinstance(owtwa__azg, bodo.libs.int_arr_ext.IntegerArrayType
                ) or owtwa__azg in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(owtwa__azg):
                func_text += f"""  {wmh__gryg} = {wlwzg__mac}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {wmh__gryg} = {wlwzg__mac}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[wlwzg__mac
                ] = bodo.libs.array._gen_row_na_check_intrinsic(owtwa__azg,
                esmju__cmzsb)
            expr = expr.replace(cuh__ispz, wmh__gryg)
        if ken__yeg not in key_set:
            ied__gnjo.append(esmju__cmzsb)
    return expr, func_text, ied__gnjo


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as rxsbn__ghnc:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    nxv__wttbg = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[oijmg__omon.name] in nxv__wttbg for
        oijmg__omon in join_node.get_live_left_vars())
    right_parallel = all(array_dists[oijmg__omon.name] in nxv__wttbg for
        oijmg__omon in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[oijmg__omon.name] in nxv__wttbg for
            oijmg__omon in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[oijmg__omon.name] in nxv__wttbg for
            oijmg__omon in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[oijmg__omon.name] in nxv__wttbg for
            oijmg__omon in join_node.get_live_out_vars())
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
    ltrhy__cdemr = set(left_col_nums)
    dcmv__gcbii = set(right_col_nums)
    btg__rzvo = join_node.vect_same_key
    wbvrv__bnnzu = []
    for eyhip__icsco in range(len(left_key_types)):
        if left_key_in_output[eyhip__icsco]:
            wbvrv__bnnzu.append(needs_typechange(matched_key_types[
                eyhip__icsco], join_node.is_right, btg__rzvo[eyhip__icsco]))
    bpedm__lyyea = len(left_key_types)
    ltlyr__augg = 0
    ytyaz__efuh = left_physical_to_logical_list[len(left_key_types):]
    for eyhip__icsco, anxu__pmubp in enumerate(ytyaz__efuh):
        xdgs__anja = True
        if anxu__pmubp in ltrhy__cdemr:
            xdgs__anja = left_key_in_output[bpedm__lyyea]
            bpedm__lyyea += 1
        if xdgs__anja:
            wbvrv__bnnzu.append(needs_typechange(left_other_types[
                eyhip__icsco], join_node.is_right, False))
    for eyhip__icsco in range(len(right_key_types)):
        if not btg__rzvo[eyhip__icsco] and not join_node.is_join:
            if right_key_in_output[ltlyr__augg]:
                wbvrv__bnnzu.append(needs_typechange(matched_key_types[
                    eyhip__icsco], join_node.is_left, False))
            ltlyr__augg += 1
    xbli__kjt = right_physical_to_logical_list[len(right_key_types):]
    for eyhip__icsco, anxu__pmubp in enumerate(xbli__kjt):
        xdgs__anja = True
        if anxu__pmubp in dcmv__gcbii:
            xdgs__anja = right_key_in_output[ltlyr__augg]
            ltlyr__augg += 1
        if xdgs__anja:
            wbvrv__bnnzu.append(needs_typechange(right_other_types[
                eyhip__icsco], join_node.is_left, False))
    lsz__hkbm = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            btsrk__durd = left_other_names[1:]
            ash__pqa = left_other_names[0]
        else:
            btsrk__durd = left_other_names
            ash__pqa = None
        vhrl__aclvi = '()' if len(btsrk__durd) == 0 else f'({btsrk__durd[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({ash__pqa}, {vhrl__aclvi}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        hkl__zxit = []
        for eyhip__icsco in range(lsz__hkbm):
            hkl__zxit.append('t1_keys[{}]'.format(eyhip__icsco))
        for eyhip__icsco in range(len(left_other_names)):
            hkl__zxit.append('data_left[{}]'.format(eyhip__icsco))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(doerr__ppfbn) for doerr__ppfbn in
            hkl__zxit))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            vhnnl__ksf = right_other_names[1:]
            ash__pqa = right_other_names[0]
        else:
            vhnnl__ksf = right_other_names
            ash__pqa = None
        vhrl__aclvi = '()' if len(vhnnl__ksf) == 0 else f'({vhnnl__ksf[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({ash__pqa}, {vhrl__aclvi}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        kzrl__mwpti = []
        for eyhip__icsco in range(lsz__hkbm):
            kzrl__mwpti.append('t2_keys[{}]'.format(eyhip__icsco))
        for eyhip__icsco in range(len(right_other_names)):
            kzrl__mwpti.append('data_right[{}]'.format(eyhip__icsco))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(doerr__ppfbn) for doerr__ppfbn in
            kzrl__mwpti))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(btg__rzvo, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(wbvrv__bnnzu, dtype=np.int64)
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
        .format(left_parallel, right_parallel, lsz__hkbm, len(ytyaz__efuh),
        len(xbli__kjt), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    izid__kjkdm = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {izid__kjkdm}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        oosgq__scj = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{oosgq__scj}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        kzwfo__ithyc = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        kzwfo__ithyc.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        ahm__wtcr = False
        uxs__arkde = False
        if join_node.has_live_out_table_var:
            kwf__ffc = list(out_table_type.arr_types)
        else:
            kwf__ffc = None
        for hlol__iost, tgp__fyhi in kzwfo__ithyc.items():
            if hlol__iost < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                kwf__ffc[hlol__iost] = tgp__fyhi
                ahm__wtcr = True
            else:
                xfg__oan = tgp__fyhi
                uxs__arkde = True
        if ahm__wtcr:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            gse__ulk = bodo.TableType(tuple(kwf__ffc))
            glbs['py_table_type'] = gse__ulk
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if uxs__arkde:
            glbs['index_col_type'] = xfg__oan
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
    kzwfo__ithyc: Dict[int, types.Type] = {}
    lsz__hkbm = len(matched_key_types)
    for eyhip__icsco in range(lsz__hkbm):
        if used_key_nums is None or eyhip__icsco in used_key_nums:
            if matched_key_types[eyhip__icsco] != key_types[eyhip__icsco] and (
                convert_dict_col or key_types[eyhip__icsco] != bodo.
                dict_str_arr_type):
                if output_map:
                    oosgq__scj = output_map[eyhip__icsco]
                else:
                    oosgq__scj = eyhip__icsco
                kzwfo__ithyc[oosgq__scj] = matched_key_types[eyhip__icsco]
    return kzwfo__ithyc


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    saht__dknfw = bodo.libs.distributed_api.get_size()
    cryo__wvkkq = np.empty(saht__dknfw, left_key_arrs[0].dtype)
    rsa__yrrp = np.empty(saht__dknfw, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(cryo__wvkkq, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(rsa__yrrp, left_key_arrs[0][-1])
    xed__ojkqc = np.zeros(saht__dknfw, np.int32)
    zhs__fzgu = np.zeros(saht__dknfw, np.int32)
    gelra__tyvj = np.zeros(saht__dknfw, np.int32)
    zps__szsf = right_key_arrs[0][0]
    mtsw__qtx = right_key_arrs[0][-1]
    kis__bdqe = -1
    eyhip__icsco = 0
    while eyhip__icsco < saht__dknfw - 1 and rsa__yrrp[eyhip__icsco
        ] < zps__szsf:
        eyhip__icsco += 1
    while eyhip__icsco < saht__dknfw and cryo__wvkkq[eyhip__icsco
        ] <= mtsw__qtx:
        kis__bdqe, zecie__hogz = _count_overlap(right_key_arrs[0],
            cryo__wvkkq[eyhip__icsco], rsa__yrrp[eyhip__icsco])
        if kis__bdqe != 0:
            kis__bdqe -= 1
            zecie__hogz += 1
        xed__ojkqc[eyhip__icsco] = zecie__hogz
        zhs__fzgu[eyhip__icsco] = kis__bdqe
        eyhip__icsco += 1
    while eyhip__icsco < saht__dknfw:
        xed__ojkqc[eyhip__icsco] = 1
        zhs__fzgu[eyhip__icsco] = len(right_key_arrs[0]) - 1
        eyhip__icsco += 1
    bodo.libs.distributed_api.alltoall(xed__ojkqc, gelra__tyvj, 1)
    bdqeu__cmfn = gelra__tyvj.sum()
    oltkp__igbu = np.empty(bdqeu__cmfn, right_key_arrs[0].dtype)
    xqjzu__clxr = alloc_arr_tup(bdqeu__cmfn, right_data)
    rezbt__mwu = bodo.ir.join.calc_disp(gelra__tyvj)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], oltkp__igbu,
        xed__ojkqc, gelra__tyvj, zhs__fzgu, rezbt__mwu)
    bodo.libs.distributed_api.alltoallv_tup(right_data, xqjzu__clxr,
        xed__ojkqc, gelra__tyvj, zhs__fzgu, rezbt__mwu)
    return (oltkp__igbu,), xqjzu__clxr


@numba.njit
def _count_overlap(r_key_arr, start, end):
    zecie__hogz = 0
    kis__bdqe = 0
    xoto__ppivf = 0
    while xoto__ppivf < len(r_key_arr) and r_key_arr[xoto__ppivf] < start:
        kis__bdqe += 1
        xoto__ppivf += 1
    while xoto__ppivf < len(r_key_arr) and start <= r_key_arr[xoto__ppivf
        ] <= end:
        xoto__ppivf += 1
        zecie__hogz += 1
    return kis__bdqe, zecie__hogz


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    nmwj__fkbyb = np.empty_like(arr)
    nmwj__fkbyb[0] = 0
    for eyhip__icsco in range(1, len(arr)):
        nmwj__fkbyb[eyhip__icsco] = nmwj__fkbyb[eyhip__icsco - 1] + arr[
            eyhip__icsco - 1]
    return nmwj__fkbyb


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    gcs__tvwm = len(left_keys[0])
    lja__rio = len(right_keys[0])
    dzvi__rvuo = alloc_arr_tup(gcs__tvwm, left_keys)
    yku__wqy = alloc_arr_tup(gcs__tvwm, right_keys)
    fsxnx__frvl = alloc_arr_tup(gcs__tvwm, data_left)
    ewrib__ehtsi = alloc_arr_tup(gcs__tvwm, data_right)
    ones__fnxfu = 0
    rqku__dbfk = 0
    for ones__fnxfu in range(gcs__tvwm):
        if rqku__dbfk < 0:
            rqku__dbfk = 0
        while rqku__dbfk < lja__rio and getitem_arr_tup(right_keys, rqku__dbfk
            ) <= getitem_arr_tup(left_keys, ones__fnxfu):
            rqku__dbfk += 1
        rqku__dbfk -= 1
        setitem_arr_tup(dzvi__rvuo, ones__fnxfu, getitem_arr_tup(left_keys,
            ones__fnxfu))
        setitem_arr_tup(fsxnx__frvl, ones__fnxfu, getitem_arr_tup(data_left,
            ones__fnxfu))
        if rqku__dbfk >= 0:
            setitem_arr_tup(yku__wqy, ones__fnxfu, getitem_arr_tup(
                right_keys, rqku__dbfk))
            setitem_arr_tup(ewrib__ehtsi, ones__fnxfu, getitem_arr_tup(
                data_right, rqku__dbfk))
        else:
            bodo.libs.array_kernels.setna_tup(yku__wqy, ones__fnxfu)
            bodo.libs.array_kernels.setna_tup(ewrib__ehtsi, ones__fnxfu)
    return dzvi__rvuo, yku__wqy, fsxnx__frvl, ewrib__ehtsi
