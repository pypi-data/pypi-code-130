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
            self.na_position_b = tuple([(True if ktowe__ucz == 'last' else 
                False) for ktowe__ucz in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [ayoa__vsg for ayoa__vsg in self.in_vars if ayoa__vsg is not
            None]

    def get_live_out_vars(self):
        return [ayoa__vsg for ayoa__vsg in self.out_vars if ayoa__vsg is not
            None]

    def __repr__(self):
        rnsy__ukfwb = ', '.join(ayoa__vsg.name for ayoa__vsg in self.
            get_live_in_vars())
        qlrtu__ggnn = f'{self.df_in}{{{rnsy__ukfwb}}}'
        njn__cuwn = ', '.join(ayoa__vsg.name for ayoa__vsg in self.
            get_live_out_vars())
        mmkf__zhyoj = f'{self.df_out}{{{njn__cuwn}}}'
        return f'Sort (keys: {self.key_inds}): {qlrtu__ggnn} {mmkf__zhyoj}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    agg__weica = []
    for ofj__oue in sort_node.get_live_in_vars():
        mggk__gsx = equiv_set.get_shape(ofj__oue)
        if mggk__gsx is not None:
            agg__weica.append(mggk__gsx[0])
    if len(agg__weica) > 1:
        equiv_set.insert_equiv(*agg__weica)
    nzz__epq = []
    agg__weica = []
    for ofj__oue in sort_node.get_live_out_vars():
        tuq__udfpi = typemap[ofj__oue.name]
        ump__etsf = array_analysis._gen_shape_call(equiv_set, ofj__oue,
            tuq__udfpi.ndim, None, nzz__epq)
        equiv_set.insert_equiv(ofj__oue, ump__etsf)
        agg__weica.append(ump__etsf[0])
        equiv_set.define(ofj__oue, set())
    if len(agg__weica) > 1:
        equiv_set.insert_equiv(*agg__weica)
    return [], nzz__epq


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    sck__zkhik = sort_node.get_live_in_vars()
    icmm__qlcfz = sort_node.get_live_out_vars()
    rtc__prv = Distribution.OneD
    for ofj__oue in sck__zkhik:
        rtc__prv = Distribution(min(rtc__prv.value, array_dists[ofj__oue.
            name].value))
    ntb__cbk = Distribution(min(rtc__prv.value, Distribution.OneD_Var.value))
    for ofj__oue in icmm__qlcfz:
        if ofj__oue.name in array_dists:
            ntb__cbk = Distribution(min(ntb__cbk.value, array_dists[
                ofj__oue.name].value))
    if ntb__cbk != Distribution.OneD_Var:
        rtc__prv = ntb__cbk
    for ofj__oue in sck__zkhik:
        array_dists[ofj__oue.name] = rtc__prv
    for ofj__oue in icmm__qlcfz:
        array_dists[ofj__oue.name] = ntb__cbk


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for wndwc__mbcra, cue__kmtm in enumerate(sort_node.out_vars):
        gcyvl__giqd = sort_node.in_vars[wndwc__mbcra]
        if gcyvl__giqd is not None and cue__kmtm is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                cue__kmtm.name, src=gcyvl__giqd.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for ofj__oue in sort_node.get_live_out_vars():
            definitions[ofj__oue.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for wndwc__mbcra in range(len(sort_node.in_vars)):
        if sort_node.in_vars[wndwc__mbcra] is not None:
            sort_node.in_vars[wndwc__mbcra] = visit_vars_inner(sort_node.
                in_vars[wndwc__mbcra], callback, cbdata)
        if sort_node.out_vars[wndwc__mbcra] is not None:
            sort_node.out_vars[wndwc__mbcra] = visit_vars_inner(sort_node.
                out_vars[wndwc__mbcra], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        terab__wsrs = sort_node.out_vars[0]
        if terab__wsrs is not None and terab__wsrs.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            jmmeh__bte = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & jmmeh__bte)
            sort_node.dead_var_inds.update(dead_cols - jmmeh__bte)
            if len(jmmeh__bte & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for wndwc__mbcra in range(1, len(sort_node.out_vars)):
            ayoa__vsg = sort_node.out_vars[wndwc__mbcra]
            if ayoa__vsg is not None and ayoa__vsg.name not in lives:
                sort_node.out_vars[wndwc__mbcra] = None
                rpdla__uoqy = sort_node.num_table_arrays + wndwc__mbcra - 1
                if rpdla__uoqy in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(rpdla__uoqy)
                else:
                    sort_node.dead_var_inds.add(rpdla__uoqy)
                    sort_node.in_vars[wndwc__mbcra] = None
    else:
        for wndwc__mbcra in range(len(sort_node.out_vars)):
            ayoa__vsg = sort_node.out_vars[wndwc__mbcra]
            if ayoa__vsg is not None and ayoa__vsg.name not in lives:
                sort_node.out_vars[wndwc__mbcra] = None
                if wndwc__mbcra in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(wndwc__mbcra)
                else:
                    sort_node.dead_var_inds.add(wndwc__mbcra)
                    sort_node.in_vars[wndwc__mbcra] = None
    if all(ayoa__vsg is None for ayoa__vsg in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ayoa__vsg.name for ayoa__vsg in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({ayoa__vsg.name for ayoa__vsg in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    revc__rtcl = set()
    if not sort_node.inplace:
        revc__rtcl.update({ayoa__vsg.name for ayoa__vsg in sort_node.
            get_live_out_vars()})
    return set(), revc__rtcl


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for wndwc__mbcra in range(len(sort_node.in_vars)):
        if sort_node.in_vars[wndwc__mbcra] is not None:
            sort_node.in_vars[wndwc__mbcra] = replace_vars_inner(sort_node.
                in_vars[wndwc__mbcra], var_dict)
        if sort_node.out_vars[wndwc__mbcra] is not None:
            sort_node.out_vars[wndwc__mbcra] = replace_vars_inner(sort_node
                .out_vars[wndwc__mbcra], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for ayoa__vsg in (in_vars + out_vars):
            if array_dists[ayoa__vsg.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ayoa__vsg.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        jevg__vir = []
        for ayoa__vsg in in_vars:
            zgqw__nwu = _copy_array_nodes(ayoa__vsg, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            jevg__vir.append(zgqw__nwu)
        in_vars = jevg__vir
    out_types = [(typemap[ayoa__vsg.name] if ayoa__vsg is not None else
        types.none) for ayoa__vsg in sort_node.out_vars]
    bxy__kbkuv, ptyk__zlsc = get_sort_cpp_section(sort_node, out_types,
        parallel)
    rri__tmrao = {}
    exec(bxy__kbkuv, {}, rri__tmrao)
    aeqyp__eavwv = rri__tmrao['f']
    ptyk__zlsc.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    ptyk__zlsc.update({f'out_type{wndwc__mbcra}': out_types[wndwc__mbcra] for
        wndwc__mbcra in range(len(out_types))})
    zbpx__kifa = compile_to_numba_ir(aeqyp__eavwv, ptyk__zlsc, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[ayoa__vsg.
        name] for ayoa__vsg in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(zbpx__kifa, in_vars)
    cdoa__hgns = zbpx__kifa.body[-2].value.value
    nodes += zbpx__kifa.body[:-2]
    for wndwc__mbcra, ayoa__vsg in enumerate(out_vars):
        gen_getitem(ayoa__vsg, cdoa__hgns, wndwc__mbcra, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    mrp__tsslk = lambda arr: arr.copy()
    qhimx__jpjc = None
    if isinstance(typemap[var.name], TableType):
        ajr__ooqxs = len(typemap[var.name].arr_types)
        qhimx__jpjc = set(range(ajr__ooqxs)) - dead_cols
        qhimx__jpjc = MetaType(tuple(sorted(qhimx__jpjc)))
        mrp__tsslk = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    zbpx__kifa = compile_to_numba_ir(mrp__tsslk, {'bodo': bodo, 'types':
        types, '_used_columns': qhimx__jpjc}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(zbpx__kifa, [var])
    nodes += zbpx__kifa.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    uedt__fmjn = len(sort_node.key_inds)
    rocib__noebw = len(sort_node.in_vars)
    sjuo__tqdf = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + rocib__noebw - 1 if sort_node.
        is_table_format else rocib__noebw)
    accnq__hiy, nfzpu__yzwv, xzf__hsgbt = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    cvqg__xrpck = []
    if sort_node.is_table_format:
        cvqg__xrpck.append('arg0')
        for wndwc__mbcra in range(1, rocib__noebw):
            rpdla__uoqy = sort_node.num_table_arrays + wndwc__mbcra - 1
            if rpdla__uoqy not in sort_node.dead_var_inds:
                cvqg__xrpck.append(f'arg{rpdla__uoqy}')
    else:
        for wndwc__mbcra in range(n_cols):
            if wndwc__mbcra not in sort_node.dead_var_inds:
                cvqg__xrpck.append(f'arg{wndwc__mbcra}')
    bxy__kbkuv = f"def f({', '.join(cvqg__xrpck)}):\n"
    if sort_node.is_table_format:
        owhq__yqgua = ',' if rocib__noebw - 1 == 1 else ''
        ypdw__ebn = []
        for wndwc__mbcra in range(sort_node.num_table_arrays, n_cols):
            if wndwc__mbcra in sort_node.dead_var_inds:
                ypdw__ebn.append('None')
            else:
                ypdw__ebn.append(f'arg{wndwc__mbcra}')
        bxy__kbkuv += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(ypdw__ebn)}{owhq__yqgua}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        qycp__rxp = {fhk__xxjd: wndwc__mbcra for wndwc__mbcra, fhk__xxjd in
            enumerate(accnq__hiy)}
        yatx__daik = [None] * len(accnq__hiy)
        for wndwc__mbcra in range(n_cols):
            ddfp__cmulc = qycp__rxp.get(wndwc__mbcra, -1)
            if ddfp__cmulc != -1:
                yatx__daik[ddfp__cmulc] = f'array_to_info(arg{wndwc__mbcra})'
        bxy__kbkuv += '  info_list_total = [{}]\n'.format(','.join(yatx__daik))
        bxy__kbkuv += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    bxy__kbkuv += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if ivtr__qayf else '0' for ivtr__qayf in sort_node.
        ascending_list))
    bxy__kbkuv += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if ivtr__qayf else '0' for ivtr__qayf in sort_node.
        na_position_b))
    bxy__kbkuv += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if wndwc__mbcra in xzf__hsgbt else '0' for wndwc__mbcra in
        range(uedt__fmjn)))
    bxy__kbkuv += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    bxy__kbkuv += f"""  out_cpp_table = sort_values_table(in_cpp_table, {uedt__fmjn}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        owhq__yqgua = ',' if sjuo__tqdf == 1 else ''
        yyetv__eayy = (
            f"({', '.join(f'out_type{wndwc__mbcra}' if not type_has_unknown_cats(out_types[wndwc__mbcra]) else f'arg{wndwc__mbcra}' for wndwc__mbcra in range(sjuo__tqdf))}{owhq__yqgua})"
            )
        bxy__kbkuv += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {yyetv__eayy}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        qycp__rxp = {fhk__xxjd: wndwc__mbcra for wndwc__mbcra, fhk__xxjd in
            enumerate(nfzpu__yzwv)}
        yatx__daik = []
        for wndwc__mbcra in range(n_cols):
            ddfp__cmulc = qycp__rxp.get(wndwc__mbcra, -1)
            if ddfp__cmulc != -1:
                rqvc__aimp = (f'out_type{wndwc__mbcra}' if not
                    type_has_unknown_cats(out_types[wndwc__mbcra]) else
                    f'arg{wndwc__mbcra}')
                bxy__kbkuv += f"""  out{wndwc__mbcra} = info_to_array(info_from_table(out_cpp_table, {ddfp__cmulc}), {rqvc__aimp})
"""
                yatx__daik.append(f'out{wndwc__mbcra}')
        owhq__yqgua = ',' if len(yatx__daik) == 1 else ''
        kjs__adji = f"({', '.join(yatx__daik)}{owhq__yqgua})"
        bxy__kbkuv += f'  out_data = {kjs__adji}\n'
    bxy__kbkuv += '  delete_table(out_cpp_table)\n'
    bxy__kbkuv += '  delete_table(in_cpp_table)\n'
    bxy__kbkuv += f'  return out_data\n'
    return bxy__kbkuv, {'in_col_inds': MetaType(tuple(accnq__hiy)),
        'out_col_inds': MetaType(tuple(nfzpu__yzwv))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    accnq__hiy = []
    nfzpu__yzwv = []
    xzf__hsgbt = []
    for fhk__xxjd, wndwc__mbcra in enumerate(key_inds):
        accnq__hiy.append(wndwc__mbcra)
        if wndwc__mbcra in dead_key_var_inds:
            xzf__hsgbt.append(fhk__xxjd)
        else:
            nfzpu__yzwv.append(wndwc__mbcra)
    for wndwc__mbcra in range(n_cols):
        if wndwc__mbcra in dead_var_inds or wndwc__mbcra in key_inds:
            continue
        accnq__hiy.append(wndwc__mbcra)
        nfzpu__yzwv.append(wndwc__mbcra)
    return accnq__hiy, nfzpu__yzwv, xzf__hsgbt


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    lsrj__juzyc = sort_node.in_vars[0].name
    fmzxs__fra = sort_node.out_vars[0].name
    gzqo__naw, mex__iiy, qcep__ymh = block_use_map[lsrj__juzyc]
    if mex__iiy or qcep__ymh:
        return
    dqhq__nra, nsx__ttxs, jmepq__riedk = _compute_table_column_uses(fmzxs__fra,
        table_col_use_map, equiv_vars)
    rwtro__hph = set(wndwc__mbcra for wndwc__mbcra in sort_node.key_inds if
        wndwc__mbcra < sort_node.num_table_arrays)
    block_use_map[lsrj__juzyc
        ] = gzqo__naw | dqhq__nra | rwtro__hph, nsx__ttxs or jmepq__riedk, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    ajr__ooqxs = sort_node.num_table_arrays
    fmzxs__fra = sort_node.out_vars[0].name
    qhimx__jpjc = _find_used_columns(fmzxs__fra, ajr__ooqxs,
        column_live_map, equiv_vars)
    if qhimx__jpjc is None:
        return False
    gjsyv__fluut = set(range(ajr__ooqxs)) - qhimx__jpjc
    rwtro__hph = set(wndwc__mbcra for wndwc__mbcra in sort_node.key_inds if
        wndwc__mbcra < ajr__ooqxs)
    eav__fxecr = sort_node.dead_key_var_inds | gjsyv__fluut & rwtro__hph
    rkr__usti = sort_node.dead_var_inds | gjsyv__fluut - rwtro__hph
    bsuj__srd = (eav__fxecr != sort_node.dead_key_var_inds) | (rkr__usti !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = eav__fxecr
    sort_node.dead_var_inds = rkr__usti
    return bsuj__srd


remove_dead_column_extensions[Sort] = sort_remove_dead_column
