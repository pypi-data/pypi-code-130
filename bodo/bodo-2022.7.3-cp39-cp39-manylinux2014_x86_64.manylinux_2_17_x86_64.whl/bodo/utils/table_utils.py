"""File containing utility functions for supporting DataFrame operations with Table Format."""
from collections import defaultdict
from typing import Dict, Set
import numba
import numpy as np
from numba.core import types
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.table import TableType
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_mappable_table_func(table, func_name, out_arr_typ, is_method,
    used_cols=None):
    if not is_overload_constant_str(func_name) and not is_overload_none(
        func_name):
        raise_bodo_error(
            'generate_mappable_table_func(): func_name must be a constant string'
            )
    if not is_overload_constant_bool(is_method):
        raise_bodo_error(
            'generate_mappable_table_func(): is_method must be a constant boolean'
            )
    vycp__rmuxj = not is_overload_none(func_name)
    if vycp__rmuxj:
        func_name = get_overload_const_str(func_name)
        jvfpk__fhl = get_overload_const_bool(is_method)
    juvv__xcw = out_arr_typ.instance_type if isinstance(out_arr_typ, types.
        TypeRef) else out_arr_typ
    ftaj__gwbmf = juvv__xcw == types.none
    rvy__zvmoy = len(table.arr_types)
    if ftaj__gwbmf:
        wfc__zhwlq = table
    else:
        ibccf__aomo = tuple([juvv__xcw] * rvy__zvmoy)
        wfc__zhwlq = TableType(ibccf__aomo)
    gyorx__isrlu = {'bodo': bodo, 'lst_dtype': juvv__xcw, 'table_typ':
        wfc__zhwlq}
    xsipm__ypt = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if ftaj__gwbmf:
        xsipm__ypt += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        xsipm__ypt += f'  l = len(table)\n'
    else:
        xsipm__ypt += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({rvy__zvmoy}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        mudu__tojyx = used_cols.instance_type
        tnz__xrt = np.array(mudu__tojyx.meta, dtype=np.int64)
        gyorx__isrlu['used_cols_glbl'] = tnz__xrt
        mngvz__jkak = set([table.block_nums[nrx__djm] for nrx__djm in tnz__xrt]
            )
        xsipm__ypt += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        xsipm__ypt += f'  used_cols_set = None\n'
        tnz__xrt = None
    xsipm__ypt += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for cqlp__wxy in table.type_to_blk.values():
        xsipm__ypt += f"""  blk_{cqlp__wxy} = bodo.hiframes.table.get_table_block(table, {cqlp__wxy})
"""
        if ftaj__gwbmf:
            xsipm__ypt += f"""  out_list_{cqlp__wxy} = bodo.hiframes.table.alloc_list_like(blk_{cqlp__wxy}, len(blk_{cqlp__wxy}), False)
"""
            qml__uysq = f'out_list_{cqlp__wxy}'
        else:
            qml__uysq = 'out_list'
        if tnz__xrt is None or cqlp__wxy in mngvz__jkak:
            xsipm__ypt += f'  for i in range(len(blk_{cqlp__wxy})):\n'
            gyorx__isrlu[f'col_indices_{cqlp__wxy}'] = np.array(table.
                block_to_arr_ind[cqlp__wxy], dtype=np.int64)
            xsipm__ypt += f'    col_loc = col_indices_{cqlp__wxy}[i]\n'
            if tnz__xrt is not None:
                xsipm__ypt += f'    if col_loc not in used_cols_set:\n'
                xsipm__ypt += f'        continue\n'
            if ftaj__gwbmf:
                szzs__jmj = 'i'
            else:
                szzs__jmj = 'col_loc'
            if not vycp__rmuxj:
                xsipm__ypt += (
                    f'    {qml__uysq}[{szzs__jmj}] = blk_{cqlp__wxy}[i]\n')
            elif jvfpk__fhl:
                xsipm__ypt += (
                    f'    {qml__uysq}[{szzs__jmj}] = blk_{cqlp__wxy}[i].{func_name}()\n'
                    )
            else:
                xsipm__ypt += (
                    f'    {qml__uysq}[{szzs__jmj}] = {func_name}(blk_{cqlp__wxy}[i])\n'
                    )
        if ftaj__gwbmf:
            xsipm__ypt += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {qml__uysq}, {cqlp__wxy})
"""
    if ftaj__gwbmf:
        xsipm__ypt += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        xsipm__ypt += '  return out_table\n'
    else:
        xsipm__ypt += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    qgucm__bmaby = {}
    exec(xsipm__ypt, gyorx__isrlu, qgucm__bmaby)
    return qgucm__bmaby['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    fwbxm__hewy = args[0]
    if equiv_set.has_shape(fwbxm__hewy):
        return ArrayAnalysis.AnalyzeResult(shape=fwbxm__hewy, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    gyorx__isrlu = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    xsipm__ypt = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    xsipm__ypt += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for cqlp__wxy in table.type_to_blk.values():
        xsipm__ypt += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {cqlp__wxy})\n'
            )
        gyorx__isrlu[f'col_indices_{cqlp__wxy}'] = np.array(table.
            block_to_arr_ind[cqlp__wxy], dtype=np.int64)
        xsipm__ypt += '  for i in range(len(blk)):\n'
        xsipm__ypt += f'    col_loc = col_indices_{cqlp__wxy}[i]\n'
        xsipm__ypt += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    xsipm__ypt += '  if parallel:\n'
    xsipm__ypt += '    for i in range(start_offset, len(out_arr)):\n'
    xsipm__ypt += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    qgucm__bmaby = {}
    exec(xsipm__ypt, gyorx__isrlu, qgucm__bmaby)
    return qgucm__bmaby['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    xrv__dfss = table.type_to_blk[arr_type]
    gyorx__isrlu = {'bodo': bodo}
    gyorx__isrlu['col_indices'] = np.array(table.block_to_arr_ind[xrv__dfss
        ], dtype=np.int64)
    nsx__dqmz = col_nums_meta.instance_type
    gyorx__isrlu['col_nums'] = np.array(nsx__dqmz.meta, np.int64)
    xsipm__ypt = 'def impl(table, col_nums_meta, arr_type):\n'
    xsipm__ypt += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {xrv__dfss})\n')
    xsipm__ypt += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    xsipm__ypt += '  n = len(table)\n'
    swm__xtyiz = bodo.utils.typing.is_str_arr_type(arr_type)
    if swm__xtyiz:
        xsipm__ypt += '  total_chars = 0\n'
        xsipm__ypt += '  for c in col_nums:\n'
        xsipm__ypt += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        xsipm__ypt += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        xsipm__ypt += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        xsipm__ypt += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        xsipm__ypt += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    xsipm__ypt += '  for i in range(len(col_nums)):\n'
    xsipm__ypt += '    c = col_nums[i]\n'
    if not swm__xtyiz:
        xsipm__ypt += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    xsipm__ypt += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    xsipm__ypt += '    off = i * n\n'
    xsipm__ypt += '    for j in range(len(arr)):\n'
    xsipm__ypt += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    xsipm__ypt += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    xsipm__ypt += '      else:\n'
    xsipm__ypt += '        out_arr[off+j] = arr[j]\n'
    xsipm__ypt += '  return out_arr\n'
    nywr__gsu = {}
    exec(xsipm__ypt, gyorx__isrlu, nywr__gsu)
    qlyh__pmw = nywr__gsu['impl']
    return qlyh__pmw


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    fkkd__meu = not is_overload_false(copy)
    zgdgl__wpdy = is_overload_true(copy)
    gyorx__isrlu = {'bodo': bodo}
    etpd__pkmc = table.arr_types
    geyn__ayo = new_table_typ.arr_types
    flnzt__hxzn: Set[int] = set()
    hnboi__bzjkq: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    wuzvm__cklqm: Set[types.Type] = set()
    for nrx__djm, gxv__gmx in enumerate(etpd__pkmc):
        dqv__diqmp = geyn__ayo[nrx__djm]
        if gxv__gmx == dqv__diqmp:
            wuzvm__cklqm.add(gxv__gmx)
        else:
            flnzt__hxzn.add(nrx__djm)
            hnboi__bzjkq[dqv__diqmp].add(gxv__gmx)
    xsipm__ypt = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    xsipm__ypt += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    xsipm__ypt += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    hbjz__jasq = set(range(len(etpd__pkmc)))
    paz__cqe = hbjz__jasq - flnzt__hxzn
    if not is_overload_none(used_cols):
        mudu__tojyx = used_cols.instance_type
        pcivw__mzo = set(mudu__tojyx.meta)
        flnzt__hxzn = flnzt__hxzn & pcivw__mzo
        paz__cqe = paz__cqe & pcivw__mzo
        mngvz__jkak = set([table.block_nums[nrx__djm] for nrx__djm in
            pcivw__mzo])
    else:
        pcivw__mzo = None
    gyorx__isrlu['cast_cols'] = np.array(list(flnzt__hxzn), dtype=np.int64)
    gyorx__isrlu['copied_cols'] = np.array(list(paz__cqe), dtype=np.int64)
    xsipm__ypt += f'  copied_cols_set = set(copied_cols)\n'
    xsipm__ypt += f'  cast_cols_set = set(cast_cols)\n'
    for vfhk__gumy, cqlp__wxy in new_table_typ.type_to_blk.items():
        gyorx__isrlu[f'typ_list_{cqlp__wxy}'] = types.List(vfhk__gumy)
        xsipm__ypt += f"""  out_arr_list_{cqlp__wxy} = bodo.hiframes.table.alloc_list_like(typ_list_{cqlp__wxy}, {len(new_table_typ.block_to_arr_ind[cqlp__wxy])}, False)
"""
        if vfhk__gumy in wuzvm__cklqm:
            mqgd__otpt = table.type_to_blk[vfhk__gumy]
            if pcivw__mzo is None or mqgd__otpt in mngvz__jkak:
                tfj__xnmqb = table.block_to_arr_ind[mqgd__otpt]
                nhnr__drhyx = [new_table_typ.block_offsets[uxzt__eel] for
                    uxzt__eel in tfj__xnmqb]
                gyorx__isrlu[f'new_idx_{mqgd__otpt}'] = np.array(nhnr__drhyx,
                    np.int64)
                gyorx__isrlu[f'orig_arr_inds_{mqgd__otpt}'] = np.array(
                    tfj__xnmqb, np.int64)
                xsipm__ypt += f"""  arr_list_{mqgd__otpt} = bodo.hiframes.table.get_table_block(table, {mqgd__otpt})
"""
                xsipm__ypt += (
                    f'  for i in range(len(arr_list_{mqgd__otpt})):\n')
                xsipm__ypt += (
                    f'    arr_ind_{mqgd__otpt} = orig_arr_inds_{mqgd__otpt}[i]\n'
                    )
                xsipm__ypt += (
                    f'    if arr_ind_{mqgd__otpt} not in copied_cols_set:\n')
                xsipm__ypt += f'      continue\n'
                xsipm__ypt += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{mqgd__otpt}, i, arr_ind_{mqgd__otpt})
"""
                xsipm__ypt += (
                    f'    out_idx_{cqlp__wxy}_{mqgd__otpt} = new_idx_{mqgd__otpt}[i]\n'
                    )
                xsipm__ypt += (
                    f'    arr_val_{mqgd__otpt} = arr_list_{mqgd__otpt}[i]\n')
                if zgdgl__wpdy:
                    xsipm__ypt += (
                        f'    arr_val_{mqgd__otpt} = arr_val_{mqgd__otpt}.copy()\n'
                        )
                elif fkkd__meu:
                    xsipm__ypt += f"""    arr_val_{mqgd__otpt} = arr_val_{mqgd__otpt}.copy() if copy else arr_val_{cqlp__wxy}
"""
                xsipm__ypt += f"""    out_arr_list_{cqlp__wxy}[out_idx_{cqlp__wxy}_{mqgd__otpt}] = arr_val_{mqgd__otpt}
"""
    ewr__tnqmm = set()
    for vfhk__gumy, cqlp__wxy in new_table_typ.type_to_blk.items():
        if vfhk__gumy in hnboi__bzjkq:
            if isinstance(vfhk__gumy, bodo.IntegerArrayType):
                pumt__fre = vfhk__gumy.get_pandas_scalar_type_instance.name
            else:
                pumt__fre = vfhk__gumy.dtype
            gyorx__isrlu[f'typ_{cqlp__wxy}'] = pumt__fre
            huhi__xele = hnboi__bzjkq[vfhk__gumy]
            for wbfbx__gpbu in huhi__xele:
                mqgd__otpt = table.type_to_blk[wbfbx__gpbu]
                if pcivw__mzo is None or mqgd__otpt in mngvz__jkak:
                    if (wbfbx__gpbu not in wuzvm__cklqm and wbfbx__gpbu not in
                        ewr__tnqmm):
                        tfj__xnmqb = table.block_to_arr_ind[mqgd__otpt]
                        nhnr__drhyx = [new_table_typ.block_offsets[
                            uxzt__eel] for uxzt__eel in tfj__xnmqb]
                        gyorx__isrlu[f'new_idx_{mqgd__otpt}'] = np.array(
                            nhnr__drhyx, np.int64)
                        gyorx__isrlu[f'orig_arr_inds_{mqgd__otpt}'] = np.array(
                            tfj__xnmqb, np.int64)
                        xsipm__ypt += f"""  arr_list_{mqgd__otpt} = bodo.hiframes.table.get_table_block(table, {mqgd__otpt})
"""
                    ewr__tnqmm.add(wbfbx__gpbu)
                    xsipm__ypt += (
                        f'  for i in range(len(arr_list_{mqgd__otpt})):\n')
                    xsipm__ypt += (
                        f'    arr_ind_{mqgd__otpt} = orig_arr_inds_{mqgd__otpt}[i]\n'
                        )
                    xsipm__ypt += (
                        f'    if arr_ind_{mqgd__otpt} not in cast_cols_set:\n')
                    xsipm__ypt += f'      continue\n'
                    xsipm__ypt += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{mqgd__otpt}, i, arr_ind_{mqgd__otpt})
"""
                    xsipm__ypt += f"""    out_idx_{cqlp__wxy}_{mqgd__otpt} = new_idx_{mqgd__otpt}[i]
"""
                    xsipm__ypt += f"""    arr_val_{cqlp__wxy} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{mqgd__otpt}[i], typ_{cqlp__wxy}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    xsipm__ypt += f"""    out_arr_list_{cqlp__wxy}[out_idx_{cqlp__wxy}_{mqgd__otpt}] = arr_val_{cqlp__wxy}
"""
        xsipm__ypt += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{cqlp__wxy}, {cqlp__wxy})
"""
    xsipm__ypt += '  return out_table\n'
    qgucm__bmaby = {}
    exec(xsipm__ypt, gyorx__isrlu, qgucm__bmaby)
    return qgucm__bmaby['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    fwbxm__hewy = args[0]
    if equiv_set.has_shape(fwbxm__hewy):
        return ArrayAnalysis.AnalyzeResult(shape=fwbxm__hewy, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
