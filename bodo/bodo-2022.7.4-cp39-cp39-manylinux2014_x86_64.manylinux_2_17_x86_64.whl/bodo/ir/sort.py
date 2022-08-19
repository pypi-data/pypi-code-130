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
            self.na_position_b = tuple([(True if oul__vdha == 'last' else 
                False) for oul__vdha in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [vlj__vbnq for vlj__vbnq in self.in_vars if vlj__vbnq is not
            None]

    def get_live_out_vars(self):
        return [vlj__vbnq for vlj__vbnq in self.out_vars if vlj__vbnq is not
            None]

    def __repr__(self):
        dqmqp__oawo = ', '.join(vlj__vbnq.name for vlj__vbnq in self.
            get_live_in_vars())
        ugeqh__drq = f'{self.df_in}{{{dqmqp__oawo}}}'
        gld__wthy = ', '.join(vlj__vbnq.name for vlj__vbnq in self.
            get_live_out_vars())
        lfj__gwzc = f'{self.df_out}{{{gld__wthy}}}'
        return f'Sort (keys: {self.key_inds}): {ugeqh__drq} {lfj__gwzc}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    zjej__mvgu = []
    for bpksd__sptp in sort_node.get_live_in_vars():
        nzwtb__czj = equiv_set.get_shape(bpksd__sptp)
        if nzwtb__czj is not None:
            zjej__mvgu.append(nzwtb__czj[0])
    if len(zjej__mvgu) > 1:
        equiv_set.insert_equiv(*zjej__mvgu)
    sxzp__dov = []
    zjej__mvgu = []
    for bpksd__sptp in sort_node.get_live_out_vars():
        vrnxo__rhhn = typemap[bpksd__sptp.name]
        kccn__hndg = array_analysis._gen_shape_call(equiv_set, bpksd__sptp,
            vrnxo__rhhn.ndim, None, sxzp__dov)
        equiv_set.insert_equiv(bpksd__sptp, kccn__hndg)
        zjej__mvgu.append(kccn__hndg[0])
        equiv_set.define(bpksd__sptp, set())
    if len(zjej__mvgu) > 1:
        equiv_set.insert_equiv(*zjej__mvgu)
    return [], sxzp__dov


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    zvje__vdwdm = sort_node.get_live_in_vars()
    vgqn__tvd = sort_node.get_live_out_vars()
    nqdr__qnof = Distribution.OneD
    for bpksd__sptp in zvje__vdwdm:
        nqdr__qnof = Distribution(min(nqdr__qnof.value, array_dists[
            bpksd__sptp.name].value))
    dzz__iowb = Distribution(min(nqdr__qnof.value, Distribution.OneD_Var.value)
        )
    for bpksd__sptp in vgqn__tvd:
        if bpksd__sptp.name in array_dists:
            dzz__iowb = Distribution(min(dzz__iowb.value, array_dists[
                bpksd__sptp.name].value))
    if dzz__iowb != Distribution.OneD_Var:
        nqdr__qnof = dzz__iowb
    for bpksd__sptp in zvje__vdwdm:
        array_dists[bpksd__sptp.name] = nqdr__qnof
    for bpksd__sptp in vgqn__tvd:
        array_dists[bpksd__sptp.name] = dzz__iowb


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for ylh__uhi, ndflb__tkbbj in enumerate(sort_node.out_vars):
        lljs__gelut = sort_node.in_vars[ylh__uhi]
        if lljs__gelut is not None and ndflb__tkbbj is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                ndflb__tkbbj.name, src=lljs__gelut.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for bpksd__sptp in sort_node.get_live_out_vars():
            definitions[bpksd__sptp.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for ylh__uhi in range(len(sort_node.in_vars)):
        if sort_node.in_vars[ylh__uhi] is not None:
            sort_node.in_vars[ylh__uhi] = visit_vars_inner(sort_node.
                in_vars[ylh__uhi], callback, cbdata)
        if sort_node.out_vars[ylh__uhi] is not None:
            sort_node.out_vars[ylh__uhi] = visit_vars_inner(sort_node.
                out_vars[ylh__uhi], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        ggq__fki = sort_node.out_vars[0]
        if ggq__fki is not None and ggq__fki.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            czs__kyojg = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & czs__kyojg)
            sort_node.dead_var_inds.update(dead_cols - czs__kyojg)
            if len(czs__kyojg & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for ylh__uhi in range(1, len(sort_node.out_vars)):
            vlj__vbnq = sort_node.out_vars[ylh__uhi]
            if vlj__vbnq is not None and vlj__vbnq.name not in lives:
                sort_node.out_vars[ylh__uhi] = None
                gxb__qhhd = sort_node.num_table_arrays + ylh__uhi - 1
                if gxb__qhhd in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(gxb__qhhd)
                else:
                    sort_node.dead_var_inds.add(gxb__qhhd)
                    sort_node.in_vars[ylh__uhi] = None
    else:
        for ylh__uhi in range(len(sort_node.out_vars)):
            vlj__vbnq = sort_node.out_vars[ylh__uhi]
            if vlj__vbnq is not None and vlj__vbnq.name not in lives:
                sort_node.out_vars[ylh__uhi] = None
                if ylh__uhi in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(ylh__uhi)
                else:
                    sort_node.dead_var_inds.add(ylh__uhi)
                    sort_node.in_vars[ylh__uhi] = None
    if all(vlj__vbnq is None for vlj__vbnq in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({vlj__vbnq.name for vlj__vbnq in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({vlj__vbnq.name for vlj__vbnq in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    qsm__edlaz = set()
    if not sort_node.inplace:
        qsm__edlaz.update({vlj__vbnq.name for vlj__vbnq in sort_node.
            get_live_out_vars()})
    return set(), qsm__edlaz


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for ylh__uhi in range(len(sort_node.in_vars)):
        if sort_node.in_vars[ylh__uhi] is not None:
            sort_node.in_vars[ylh__uhi] = replace_vars_inner(sort_node.
                in_vars[ylh__uhi], var_dict)
        if sort_node.out_vars[ylh__uhi] is not None:
            sort_node.out_vars[ylh__uhi] = replace_vars_inner(sort_node.
                out_vars[ylh__uhi], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for vlj__vbnq in (in_vars + out_vars):
            if array_dists[vlj__vbnq.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                vlj__vbnq.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        wqny__pnp = []
        for vlj__vbnq in in_vars:
            gwxeo__aewjd = _copy_array_nodes(vlj__vbnq, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            wqny__pnp.append(gwxeo__aewjd)
        in_vars = wqny__pnp
    out_types = [(typemap[vlj__vbnq.name] if vlj__vbnq is not None else
        types.none) for vlj__vbnq in sort_node.out_vars]
    umrv__eyn, yocql__rkyz = get_sort_cpp_section(sort_node, out_types,
        parallel)
    vihdm__uyfox = {}
    exec(umrv__eyn, {}, vihdm__uyfox)
    tsoox__qqn = vihdm__uyfox['f']
    yocql__rkyz.update({'bodo': bodo, 'np': np, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info, 'py_data_to_cpp_table':
        py_data_to_cpp_table, 'cpp_table_to_py_data': cpp_table_to_py_data})
    yocql__rkyz.update({f'out_type{ylh__uhi}': out_types[ylh__uhi] for
        ylh__uhi in range(len(out_types))})
    vhb__cex = compile_to_numba_ir(tsoox__qqn, yocql__rkyz, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[vlj__vbnq.
        name] for vlj__vbnq in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(vhb__cex, in_vars)
    ukc__inppc = vhb__cex.body[-2].value.value
    nodes += vhb__cex.body[:-2]
    for ylh__uhi, vlj__vbnq in enumerate(out_vars):
        gen_getitem(vlj__vbnq, ukc__inppc, ylh__uhi, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    xyr__njvov = lambda arr: arr.copy()
    mendx__dtg = None
    if isinstance(typemap[var.name], TableType):
        ibubw__hgoz = len(typemap[var.name].arr_types)
        mendx__dtg = set(range(ibubw__hgoz)) - dead_cols
        mendx__dtg = MetaType(tuple(sorted(mendx__dtg)))
        xyr__njvov = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    vhb__cex = compile_to_numba_ir(xyr__njvov, {'bodo': bodo, 'types':
        types, '_used_columns': mendx__dtg}, typingctx=typingctx, targetctx
        =targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(vhb__cex, [var])
    nodes += vhb__cex.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    bmcr__ewr = len(sort_node.key_inds)
    xnt__nmb = len(sort_node.in_vars)
    rgsd__dfeu = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + xnt__nmb - 1 if sort_node.
        is_table_format else xnt__nmb)
    wldx__exwi, svm__yes, usjw__scafk = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    nazcy__zhvkq = []
    if sort_node.is_table_format:
        nazcy__zhvkq.append('arg0')
        for ylh__uhi in range(1, xnt__nmb):
            gxb__qhhd = sort_node.num_table_arrays + ylh__uhi - 1
            if gxb__qhhd not in sort_node.dead_var_inds:
                nazcy__zhvkq.append(f'arg{gxb__qhhd}')
    else:
        for ylh__uhi in range(n_cols):
            if ylh__uhi not in sort_node.dead_var_inds:
                nazcy__zhvkq.append(f'arg{ylh__uhi}')
    umrv__eyn = f"def f({', '.join(nazcy__zhvkq)}):\n"
    if sort_node.is_table_format:
        xfm__ruk = ',' if xnt__nmb - 1 == 1 else ''
        dyjtu__tpxas = []
        for ylh__uhi in range(sort_node.num_table_arrays, n_cols):
            if ylh__uhi in sort_node.dead_var_inds:
                dyjtu__tpxas.append('None')
            else:
                dyjtu__tpxas.append(f'arg{ylh__uhi}')
        umrv__eyn += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(dyjtu__tpxas)}{xfm__ruk}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        nnbp__xaym = {onf__ojt: ylh__uhi for ylh__uhi, onf__ojt in
            enumerate(wldx__exwi)}
        ezhr__hdov = [None] * len(wldx__exwi)
        for ylh__uhi in range(n_cols):
            mpwxz__obv = nnbp__xaym.get(ylh__uhi, -1)
            if mpwxz__obv != -1:
                ezhr__hdov[mpwxz__obv] = f'array_to_info(arg{ylh__uhi})'
        umrv__eyn += '  info_list_total = [{}]\n'.format(','.join(ezhr__hdov))
        umrv__eyn += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    umrv__eyn += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if sny__tpg else '0' for sny__tpg in sort_node.
        ascending_list))
    umrv__eyn += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if sny__tpg else '0' for sny__tpg in sort_node.na_position_b))
    umrv__eyn += '  dead_keys = np.array([{}], np.int64)\n'.format(','.join
        ('1' if ylh__uhi in usjw__scafk else '0' for ylh__uhi in range(
        bmcr__ewr)))
    umrv__eyn += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    umrv__eyn += f"""  out_cpp_table = sort_values_table(in_cpp_table, {bmcr__ewr}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        xfm__ruk = ',' if rgsd__dfeu == 1 else ''
        qxu__dxtg = (
            f"({', '.join(f'out_type{ylh__uhi}' if not type_has_unknown_cats(out_types[ylh__uhi]) else f'arg{ylh__uhi}' for ylh__uhi in range(rgsd__dfeu))}{xfm__ruk})"
            )
        umrv__eyn += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {qxu__dxtg}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        nnbp__xaym = {onf__ojt: ylh__uhi for ylh__uhi, onf__ojt in
            enumerate(svm__yes)}
        ezhr__hdov = []
        for ylh__uhi in range(n_cols):
            mpwxz__obv = nnbp__xaym.get(ylh__uhi, -1)
            if mpwxz__obv != -1:
                lrlqf__icyt = (f'out_type{ylh__uhi}' if not
                    type_has_unknown_cats(out_types[ylh__uhi]) else
                    f'arg{ylh__uhi}')
                umrv__eyn += f"""  out{ylh__uhi} = info_to_array(info_from_table(out_cpp_table, {mpwxz__obv}), {lrlqf__icyt})
"""
                ezhr__hdov.append(f'out{ylh__uhi}')
        xfm__ruk = ',' if len(ezhr__hdov) == 1 else ''
        ygvg__gloms = f"({', '.join(ezhr__hdov)}{xfm__ruk})"
        umrv__eyn += f'  out_data = {ygvg__gloms}\n'
    umrv__eyn += '  delete_table(out_cpp_table)\n'
    umrv__eyn += '  delete_table(in_cpp_table)\n'
    umrv__eyn += f'  return out_data\n'
    return umrv__eyn, {'in_col_inds': MetaType(tuple(wldx__exwi)),
        'out_col_inds': MetaType(tuple(svm__yes))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    wldx__exwi = []
    svm__yes = []
    usjw__scafk = []
    for onf__ojt, ylh__uhi in enumerate(key_inds):
        wldx__exwi.append(ylh__uhi)
        if ylh__uhi in dead_key_var_inds:
            usjw__scafk.append(onf__ojt)
        else:
            svm__yes.append(ylh__uhi)
    for ylh__uhi in range(n_cols):
        if ylh__uhi in dead_var_inds or ylh__uhi in key_inds:
            continue
        wldx__exwi.append(ylh__uhi)
        svm__yes.append(ylh__uhi)
    return wldx__exwi, svm__yes, usjw__scafk


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    epgac__nhyus = sort_node.in_vars[0].name
    acda__uxzu = sort_node.out_vars[0].name
    gksx__jkve, dagmz__dwrm, psx__jkd = block_use_map[epgac__nhyus]
    if dagmz__dwrm or psx__jkd:
        return
    aczc__elxrc, wbnmv__wfa, cbjl__wpav = _compute_table_column_uses(acda__uxzu
        , table_col_use_map, equiv_vars)
    dsto__fqz = set(ylh__uhi for ylh__uhi in sort_node.key_inds if ylh__uhi <
        sort_node.num_table_arrays)
    block_use_map[epgac__nhyus
        ] = gksx__jkve | aczc__elxrc | dsto__fqz, wbnmv__wfa or cbjl__wpav, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    ibubw__hgoz = sort_node.num_table_arrays
    acda__uxzu = sort_node.out_vars[0].name
    mendx__dtg = _find_used_columns(acda__uxzu, ibubw__hgoz,
        column_live_map, equiv_vars)
    if mendx__dtg is None:
        return False
    iqwsm__epkwx = set(range(ibubw__hgoz)) - mendx__dtg
    dsto__fqz = set(ylh__uhi for ylh__uhi in sort_node.key_inds if ylh__uhi <
        ibubw__hgoz)
    xamkq__jnk = sort_node.dead_key_var_inds | iqwsm__epkwx & dsto__fqz
    sgn__jjif = sort_node.dead_var_inds | iqwsm__epkwx - dsto__fqz
    tyvy__xvmiy = (xamkq__jnk != sort_node.dead_key_var_inds) | (sgn__jjif !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = xamkq__jnk
    sort_node.dead_var_inds = sgn__jjif
    return tyvy__xvmiy


remove_dead_column_extensions[Sort] = sort_remove_dead_column
