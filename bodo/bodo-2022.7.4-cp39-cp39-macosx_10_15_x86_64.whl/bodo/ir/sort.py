"""IR node for the data sorting"""
from collections import defaultdict
from typing import List, Set, Tuple, Union
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_data_to_cpp_table, sort_values_table
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import MetaType, type_has_unknown_cats
from bodo.utils.utils import gen_getitem


class Sort(ir.Stmt):

    def __init__(self, df_in: str, df_out: str, in_vars: List[ir.Var],
        out_vars: List[ir.Var], key_inds: Tuple[int], inplace: bool, loc:
        ir.Loc, ascending_list: Union[List[bool], bool]=True, na_position:
        Union[List[str], str]='last', is_table_format: bool=False,
        num_table_arrays: int=0):
        self.df_in = df_in
        self.df_out = df_out
        self.in_vars = in_vars
        self.out_vars = out_vars
        self.key_inds = key_inds
        self.inplace = inplace
        self.is_table_format = is_table_format
        self.num_table_arrays = num_table_arrays
        self.dead_var_inds: Set[int] = set()
        self.dead_key_var_inds: Set[int] = set()
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_inds)
            else:
                self.na_position_b = (False,) * len(key_inds)
        else:
            self.na_position_b = tuple([(True if xzbaj__wqp == 'last' else 
                False) for xzbaj__wqp in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [voiud__qpc for voiud__qpc in self.in_vars if voiud__qpc is not
            None]

    def get_live_out_vars(self):
        return [voiud__qpc for voiud__qpc in self.out_vars if voiud__qpc is not
            None]

    def __repr__(self):
        rbai__wtwr = ', '.join(voiud__qpc.name for voiud__qpc in self.
            get_live_in_vars())
        kwl__vhykq = f'{self.df_in}{{{rbai__wtwr}}}'
        myrcs__ytwf = ', '.join(voiud__qpc.name for voiud__qpc in self.
            get_live_out_vars())
        lhkq__zsyn = f'{self.df_out}{{{myrcs__ytwf}}}'
        return f'Sort (keys: {self.key_inds}): {kwl__vhykq} {lhkq__zsyn}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    lagn__tzj = []
    for tfxx__fwlym in sort_node.get_live_in_vars():
        hfgqt__nii = equiv_set.get_shape(tfxx__fwlym)
        if hfgqt__nii is not None:
            lagn__tzj.append(hfgqt__nii[0])
    if len(lagn__tzj) > 1:
        equiv_set.insert_equiv(*lagn__tzj)
    jrddy__fsb = []
    lagn__tzj = []
    for tfxx__fwlym in sort_node.get_live_out_vars():
        udi__rspy = typemap[tfxx__fwlym.name]
        tqzw__lno = array_analysis._gen_shape_call(equiv_set, tfxx__fwlym,
            udi__rspy.ndim, None, jrddy__fsb)
        equiv_set.insert_equiv(tfxx__fwlym, tqzw__lno)
        lagn__tzj.append(tqzw__lno[0])
        equiv_set.define(tfxx__fwlym, set())
    if len(lagn__tzj) > 1:
        equiv_set.insert_equiv(*lagn__tzj)
    return [], jrddy__fsb


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    nrx__wqw = sort_node.get_live_in_vars()
    ganp__sjruz = sort_node.get_live_out_vars()
    ohtw__nvbar = Distribution.OneD
    for tfxx__fwlym in nrx__wqw:
        ohtw__nvbar = Distribution(min(ohtw__nvbar.value, array_dists[
            tfxx__fwlym.name].value))
    amwy__bex = Distribution(min(ohtw__nvbar.value, Distribution.OneD_Var.
        value))
    for tfxx__fwlym in ganp__sjruz:
        if tfxx__fwlym.name in array_dists:
            amwy__bex = Distribution(min(amwy__bex.value, array_dists[
                tfxx__fwlym.name].value))
    if amwy__bex != Distribution.OneD_Var:
        ohtw__nvbar = amwy__bex
    for tfxx__fwlym in nrx__wqw:
        array_dists[tfxx__fwlym.name] = ohtw__nvbar
    for tfxx__fwlym in ganp__sjruz:
        array_dists[tfxx__fwlym.name] = amwy__bex


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for dgq__xbz, olyr__qibz in enumerate(sort_node.out_vars):
        lqsd__ylq = sort_node.in_vars[dgq__xbz]
        if lqsd__ylq is not None and olyr__qibz is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                olyr__qibz.name, src=lqsd__ylq.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for tfxx__fwlym in sort_node.get_live_out_vars():
            definitions[tfxx__fwlym.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for dgq__xbz in range(len(sort_node.in_vars)):
        if sort_node.in_vars[dgq__xbz] is not None:
            sort_node.in_vars[dgq__xbz] = visit_vars_inner(sort_node.
                in_vars[dgq__xbz], callback, cbdata)
        if sort_node.out_vars[dgq__xbz] is not None:
            sort_node.out_vars[dgq__xbz] = visit_vars_inner(sort_node.
                out_vars[dgq__xbz], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        fsp__iyw = sort_node.out_vars[0]
        if fsp__iyw is not None and fsp__iyw.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            lrcsu__lagol = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & lrcsu__lagol)
            sort_node.dead_var_inds.update(dead_cols - lrcsu__lagol)
            if len(lrcsu__lagol & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for dgq__xbz in range(1, len(sort_node.out_vars)):
            voiud__qpc = sort_node.out_vars[dgq__xbz]
            if voiud__qpc is not None and voiud__qpc.name not in lives:
                sort_node.out_vars[dgq__xbz] = None
                mghfr__gmg = sort_node.num_table_arrays + dgq__xbz - 1
                if mghfr__gmg in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(mghfr__gmg)
                else:
                    sort_node.dead_var_inds.add(mghfr__gmg)
                    sort_node.in_vars[dgq__xbz] = None
    else:
        for dgq__xbz in range(len(sort_node.out_vars)):
            voiud__qpc = sort_node.out_vars[dgq__xbz]
            if voiud__qpc is not None and voiud__qpc.name not in lives:
                sort_node.out_vars[dgq__xbz] = None
                if dgq__xbz in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(dgq__xbz)
                else:
                    sort_node.dead_var_inds.add(dgq__xbz)
                    sort_node.in_vars[dgq__xbz] = None
    if all(voiud__qpc is None for voiud__qpc in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({voiud__qpc.name for voiud__qpc in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({voiud__qpc.name for voiud__qpc in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    ndzxt__ictvz = set()
    if not sort_node.inplace:
        ndzxt__ictvz.update({voiud__qpc.name for voiud__qpc in sort_node.
            get_live_out_vars()})
    return set(), ndzxt__ictvz


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for dgq__xbz in range(len(sort_node.in_vars)):
        if sort_node.in_vars[dgq__xbz] is not None:
            sort_node.in_vars[dgq__xbz] = replace_vars_inner(sort_node.
                in_vars[dgq__xbz], var_dict)
        if sort_node.out_vars[dgq__xbz] is not None:
            sort_node.out_vars[dgq__xbz] = replace_vars_inner(sort_node.
                out_vars[dgq__xbz], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for voiud__qpc in (in_vars + out_vars):
            if array_dists[voiud__qpc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                voiud__qpc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        vldnl__mtkmn = []
        for voiud__qpc in in_vars:
            iol__knp = _copy_array_nodes(voiud__qpc, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            vldnl__mtkmn.append(iol__knp)
        in_vars = vldnl__mtkmn
    out_types = [(typemap[voiud__qpc.name] if voiud__qpc is not None else
        types.none) for voiud__qpc in sort_node.out_vars]
    ergvc__ruye, puf__nbcci = get_sort_cpp_section(sort_node, out_types,
        parallel)
    oocu__ubad = {}
    exec(ergvc__ruye, {}, oocu__ubad)
    mbblg__bdft = oocu__ubad['f']
    puf__nbcci.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    puf__nbcci.update({f'out_type{dgq__xbz}': out_types[dgq__xbz] for
        dgq__xbz in range(len(out_types))})
    iyl__lyei = compile_to_numba_ir(mbblg__bdft, puf__nbcci, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[voiud__qpc.
        name] for voiud__qpc in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(iyl__lyei, in_vars)
    oazpu__wquz = iyl__lyei.body[-2].value.value
    nodes += iyl__lyei.body[:-2]
    for dgq__xbz, voiud__qpc in enumerate(out_vars):
        gen_getitem(voiud__qpc, oazpu__wquz, dgq__xbz, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    glw__vhky = lambda arr: arr.copy()
    slo__gsw = None
    if isinstance(typemap[var.name], TableType):
        kayo__zrkn = len(typemap[var.name].arr_types)
        slo__gsw = set(range(kayo__zrkn)) - dead_cols
        slo__gsw = MetaType(tuple(sorted(slo__gsw)))
        glw__vhky = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    iyl__lyei = compile_to_numba_ir(glw__vhky, {'bodo': bodo, 'types':
        types, '_used_columns': slo__gsw}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(iyl__lyei, [var])
    nodes += iyl__lyei.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    qoyx__cox = len(sort_node.key_inds)
    lka__boj = len(sort_node.in_vars)
    iysao__poa = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + lka__boj - 1 if sort_node.
        is_table_format else lka__boj)
    hdqk__tfq, hhtz__irx, ypo__brql = _get_cpp_col_ind_mappings(sort_node.
        key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols)
    ryw__djbk = []
    if sort_node.is_table_format:
        ryw__djbk.append('arg0')
        for dgq__xbz in range(1, lka__boj):
            mghfr__gmg = sort_node.num_table_arrays + dgq__xbz - 1
            if mghfr__gmg not in sort_node.dead_var_inds:
                ryw__djbk.append(f'arg{mghfr__gmg}')
    else:
        for dgq__xbz in range(n_cols):
            if dgq__xbz not in sort_node.dead_var_inds:
                ryw__djbk.append(f'arg{dgq__xbz}')
    ergvc__ruye = f"def f({', '.join(ryw__djbk)}):\n"
    if sort_node.is_table_format:
        iqc__gfo = ',' if lka__boj - 1 == 1 else ''
        rocgh__scd = []
        for dgq__xbz in range(sort_node.num_table_arrays, n_cols):
            if dgq__xbz in sort_node.dead_var_inds:
                rocgh__scd.append('None')
            else:
                rocgh__scd.append(f'arg{dgq__xbz}')
        ergvc__ruye += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(rocgh__scd)}{iqc__gfo}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        wmo__kkyim = {rveni__ksreg: dgq__xbz for dgq__xbz, rveni__ksreg in
            enumerate(hdqk__tfq)}
        pgl__gwmj = [None] * len(hdqk__tfq)
        for dgq__xbz in range(n_cols):
            uie__yidzn = wmo__kkyim.get(dgq__xbz, -1)
            if uie__yidzn != -1:
                pgl__gwmj[uie__yidzn] = f'array_to_info(arg{dgq__xbz})'
        ergvc__ruye += '  info_list_total = [{}]\n'.format(','.join(pgl__gwmj))
        ergvc__ruye += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    ergvc__ruye += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if kxn__mne else '0' for kxn__mne in sort_node.
        ascending_list))
    ergvc__ruye += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if kxn__mne else '0' for kxn__mne in sort_node.na_position_b))
    ergvc__ruye += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if dgq__xbz in ypo__brql else '0' for dgq__xbz in range(
        qoyx__cox)))
    ergvc__ruye += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    ergvc__ruye += f"""  out_cpp_table = sort_values_table(in_cpp_table, {qoyx__cox}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        iqc__gfo = ',' if iysao__poa == 1 else ''
        ytfx__ofozo = (
            f"({', '.join(f'out_type{dgq__xbz}' if not type_has_unknown_cats(out_types[dgq__xbz]) else f'arg{dgq__xbz}' for dgq__xbz in range(iysao__poa))}{iqc__gfo})"
            )
        ergvc__ruye += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {ytfx__ofozo}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        wmo__kkyim = {rveni__ksreg: dgq__xbz for dgq__xbz, rveni__ksreg in
            enumerate(hhtz__irx)}
        pgl__gwmj = []
        for dgq__xbz in range(n_cols):
            uie__yidzn = wmo__kkyim.get(dgq__xbz, -1)
            if uie__yidzn != -1:
                atnm__cep = f'out_type{dgq__xbz}' if not type_has_unknown_cats(
                    out_types[dgq__xbz]) else f'arg{dgq__xbz}'
                ergvc__ruye += f"""  out{dgq__xbz} = info_to_array(info_from_table(out_cpp_table, {uie__yidzn}), {atnm__cep})
"""
                pgl__gwmj.append(f'out{dgq__xbz}')
        iqc__gfo = ',' if len(pgl__gwmj) == 1 else ''
        bfo__qcif = f"({', '.join(pgl__gwmj)}{iqc__gfo})"
        ergvc__ruye += f'  out_data = {bfo__qcif}\n'
    ergvc__ruye += '  delete_table(out_cpp_table)\n'
    ergvc__ruye += '  delete_table(in_cpp_table)\n'
    ergvc__ruye += f'  return out_data\n'
    return ergvc__ruye, {'in_col_inds': MetaType(tuple(hdqk__tfq)),
        'out_col_inds': MetaType(tuple(hhtz__irx))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    hdqk__tfq = []
    hhtz__irx = []
    ypo__brql = []
    for rveni__ksreg, dgq__xbz in enumerate(key_inds):
        hdqk__tfq.append(dgq__xbz)
        if dgq__xbz in dead_key_var_inds:
            ypo__brql.append(rveni__ksreg)
        else:
            hhtz__irx.append(dgq__xbz)
    for dgq__xbz in range(n_cols):
        if dgq__xbz in dead_var_inds or dgq__xbz in key_inds:
            continue
        hdqk__tfq.append(dgq__xbz)
        hhtz__irx.append(dgq__xbz)
    return hdqk__tfq, hhtz__irx, ypo__brql


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    pyld__zwy = sort_node.in_vars[0].name
    aep__vjc = sort_node.out_vars[0].name
    dmvlg__gsi, wphrx__uoc, faw__gbu = block_use_map[pyld__zwy]
    if wphrx__uoc or faw__gbu:
        return
    rik__zor, pbaom__miv, dbos__yev = _compute_table_column_uses(aep__vjc,
        table_col_use_map, equiv_vars)
    xnfxp__apn = set(dgq__xbz for dgq__xbz in sort_node.key_inds if 
        dgq__xbz < sort_node.num_table_arrays)
    block_use_map[pyld__zwy
        ] = dmvlg__gsi | rik__zor | xnfxp__apn, pbaom__miv or dbos__yev, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    kayo__zrkn = sort_node.num_table_arrays
    aep__vjc = sort_node.out_vars[0].name
    slo__gsw = _find_used_columns(aep__vjc, kayo__zrkn, column_live_map,
        equiv_vars)
    if slo__gsw is None:
        return False
    mkz__ahya = set(range(kayo__zrkn)) - slo__gsw
    xnfxp__apn = set(dgq__xbz for dgq__xbz in sort_node.key_inds if 
        dgq__xbz < kayo__zrkn)
    evqy__frjg = sort_node.dead_key_var_inds | mkz__ahya & xnfxp__apn
    fey__wyimj = sort_node.dead_var_inds | mkz__ahya - xnfxp__apn
    cej__ywh = (evqy__frjg != sort_node.dead_key_var_inds) | (fey__wyimj !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = evqy__frjg
    sort_node.dead_var_inds = fey__wyimj
    return cej__ywh


remove_dead_column_extensions[Sort] = sort_remove_dead_column
