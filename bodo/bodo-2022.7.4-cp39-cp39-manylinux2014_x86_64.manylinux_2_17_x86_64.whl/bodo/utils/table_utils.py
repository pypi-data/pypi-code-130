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
    gjszs__jbnlr = not is_overload_none(func_name)
    if gjszs__jbnlr:
        func_name = get_overload_const_str(func_name)
        osv__arlsf = get_overload_const_bool(is_method)
    ejqe__msf = out_arr_typ.instance_type if isinstance(out_arr_typ, types.
        TypeRef) else out_arr_typ
    pksx__mtehp = ejqe__msf == types.none
    ngrw__fqxof = len(table.arr_types)
    if pksx__mtehp:
        tcvxx__qmhg = table
    else:
        nztkm__wthfm = tuple([ejqe__msf] * ngrw__fqxof)
        tcvxx__qmhg = TableType(nztkm__wthfm)
    vent__cnjrx = {'bodo': bodo, 'lst_dtype': ejqe__msf, 'table_typ':
        tcvxx__qmhg}
    rjmzr__gram = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if pksx__mtehp:
        rjmzr__gram += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        rjmzr__gram += f'  l = len(table)\n'
    else:
        rjmzr__gram += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({ngrw__fqxof}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        brgmk__gqy = used_cols.instance_type
        gmr__nnret = np.array(brgmk__gqy.meta, dtype=np.int64)
        vent__cnjrx['used_cols_glbl'] = gmr__nnret
        wjrd__ajdeq = set([table.block_nums[rpz__apq] for rpz__apq in
            gmr__nnret])
        rjmzr__gram += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        rjmzr__gram += f'  used_cols_set = None\n'
        gmr__nnret = None
    rjmzr__gram += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for zlnk__psyf in table.type_to_blk.values():
        rjmzr__gram += f"""  blk_{zlnk__psyf} = bodo.hiframes.table.get_table_block(table, {zlnk__psyf})
"""
        if pksx__mtehp:
            rjmzr__gram += f"""  out_list_{zlnk__psyf} = bodo.hiframes.table.alloc_list_like(blk_{zlnk__psyf}, len(blk_{zlnk__psyf}), False)
"""
            zvn__tcc = f'out_list_{zlnk__psyf}'
        else:
            zvn__tcc = 'out_list'
        if gmr__nnret is None or zlnk__psyf in wjrd__ajdeq:
            rjmzr__gram += f'  for i in range(len(blk_{zlnk__psyf})):\n'
            vent__cnjrx[f'col_indices_{zlnk__psyf}'] = np.array(table.
                block_to_arr_ind[zlnk__psyf], dtype=np.int64)
            rjmzr__gram += f'    col_loc = col_indices_{zlnk__psyf}[i]\n'
            if gmr__nnret is not None:
                rjmzr__gram += f'    if col_loc not in used_cols_set:\n'
                rjmzr__gram += f'        continue\n'
            if pksx__mtehp:
                ygjs__hocq = 'i'
            else:
                ygjs__hocq = 'col_loc'
            if not gjszs__jbnlr:
                rjmzr__gram += (
                    f'    {zvn__tcc}[{ygjs__hocq}] = blk_{zlnk__psyf}[i]\n')
            elif osv__arlsf:
                rjmzr__gram += (
                    f'    {zvn__tcc}[{ygjs__hocq}] = blk_{zlnk__psyf}[i].{func_name}()\n'
                    )
            else:
                rjmzr__gram += (
                    f'    {zvn__tcc}[{ygjs__hocq}] = {func_name}(blk_{zlnk__psyf}[i])\n'
                    )
        if pksx__mtehp:
            rjmzr__gram += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {zvn__tcc}, {zlnk__psyf})
"""
    if pksx__mtehp:
        rjmzr__gram += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        rjmzr__gram += '  return out_table\n'
    else:
        rjmzr__gram += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    aut__cdaa = {}
    exec(rjmzr__gram, vent__cnjrx, aut__cdaa)
    return aut__cdaa['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    xxz__oyo = args[0]
    if equiv_set.has_shape(xxz__oyo):
        return ArrayAnalysis.AnalyzeResult(shape=xxz__oyo, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    vent__cnjrx = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    rjmzr__gram = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    rjmzr__gram += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for zlnk__psyf in table.type_to_blk.values():
        rjmzr__gram += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {zlnk__psyf})\n'
            )
        vent__cnjrx[f'col_indices_{zlnk__psyf}'] = np.array(table.
            block_to_arr_ind[zlnk__psyf], dtype=np.int64)
        rjmzr__gram += '  for i in range(len(blk)):\n'
        rjmzr__gram += f'    col_loc = col_indices_{zlnk__psyf}[i]\n'
        rjmzr__gram += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    rjmzr__gram += '  if parallel:\n'
    rjmzr__gram += '    for i in range(start_offset, len(out_arr)):\n'
    rjmzr__gram += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    aut__cdaa = {}
    exec(rjmzr__gram, vent__cnjrx, aut__cdaa)
    return aut__cdaa['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    utueo__szta = table.type_to_blk[arr_type]
    vent__cnjrx = {'bodo': bodo}
    vent__cnjrx['col_indices'] = np.array(table.block_to_arr_ind[
        utueo__szta], dtype=np.int64)
    oiypx__ntfqw = col_nums_meta.instance_type
    vent__cnjrx['col_nums'] = np.array(oiypx__ntfqw.meta, np.int64)
    rjmzr__gram = 'def impl(table, col_nums_meta, arr_type):\n'
    rjmzr__gram += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {utueo__szta})\n')
    rjmzr__gram += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    rjmzr__gram += '  n = len(table)\n'
    llgi__parz = arr_type == bodo.string_array_type
    if llgi__parz:
        rjmzr__gram += '  total_chars = 0\n'
        rjmzr__gram += '  for c in col_nums:\n'
        rjmzr__gram += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        rjmzr__gram += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        rjmzr__gram += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        rjmzr__gram += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        rjmzr__gram += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    rjmzr__gram += '  for i in range(len(col_nums)):\n'
    rjmzr__gram += '    c = col_nums[i]\n'
    if not llgi__parz:
        rjmzr__gram += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    rjmzr__gram += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    rjmzr__gram += '    off = i * n\n'
    rjmzr__gram += '    for j in range(len(arr)):\n'
    rjmzr__gram += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    rjmzr__gram += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    rjmzr__gram += '      else:\n'
    rjmzr__gram += '        out_arr[off+j] = arr[j]\n'
    rjmzr__gram += '  return out_arr\n'
    pnfsq__pxcwb = {}
    exec(rjmzr__gram, vent__cnjrx, pnfsq__pxcwb)
    svos__yliwf = pnfsq__pxcwb['impl']
    return svos__yliwf


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    vmrpj__fqq = not is_overload_false(copy)
    ariae__uhcj = is_overload_true(copy)
    vent__cnjrx = {'bodo': bodo}
    vcd__rev = table.arr_types
    aefv__hqte = new_table_typ.arr_types
    nihzn__atdoh: Set[int] = set()
    oyjg__jobg: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    fdrtq__jiz: Set[types.Type] = set()
    for rpz__apq, aivk__drwoe in enumerate(vcd__rev):
        cnsnu__ufbsp = aefv__hqte[rpz__apq]
        if aivk__drwoe == cnsnu__ufbsp:
            fdrtq__jiz.add(aivk__drwoe)
        else:
            nihzn__atdoh.add(rpz__apq)
            oyjg__jobg[cnsnu__ufbsp].add(aivk__drwoe)
    rjmzr__gram = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    rjmzr__gram += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    rjmzr__gram += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    hnx__zloc = set(range(len(vcd__rev)))
    kckn__nkg = hnx__zloc - nihzn__atdoh
    if not is_overload_none(used_cols):
        brgmk__gqy = used_cols.instance_type
        sue__trol = set(brgmk__gqy.meta)
        nihzn__atdoh = nihzn__atdoh & sue__trol
        kckn__nkg = kckn__nkg & sue__trol
        wjrd__ajdeq = set([table.block_nums[rpz__apq] for rpz__apq in
            sue__trol])
    else:
        sue__trol = None
    vent__cnjrx['cast_cols'] = np.array(list(nihzn__atdoh), dtype=np.int64)
    vent__cnjrx['copied_cols'] = np.array(list(kckn__nkg), dtype=np.int64)
    rjmzr__gram += f'  copied_cols_set = set(copied_cols)\n'
    rjmzr__gram += f'  cast_cols_set = set(cast_cols)\n'
    for zhv__nipk, zlnk__psyf in new_table_typ.type_to_blk.items():
        vent__cnjrx[f'typ_list_{zlnk__psyf}'] = types.List(zhv__nipk)
        rjmzr__gram += f"""  out_arr_list_{zlnk__psyf} = bodo.hiframes.table.alloc_list_like(typ_list_{zlnk__psyf}, {len(new_table_typ.block_to_arr_ind[zlnk__psyf])}, False)
"""
        if zhv__nipk in fdrtq__jiz:
            rlbcy__cnyrj = table.type_to_blk[zhv__nipk]
            if sue__trol is None or rlbcy__cnyrj in wjrd__ajdeq:
                qqo__uyynm = table.block_to_arr_ind[rlbcy__cnyrj]
                nhsot__szsi = [new_table_typ.block_offsets[lrmrk__wrts] for
                    lrmrk__wrts in qqo__uyynm]
                vent__cnjrx[f'new_idx_{rlbcy__cnyrj}'] = np.array(nhsot__szsi,
                    np.int64)
                vent__cnjrx[f'orig_arr_inds_{rlbcy__cnyrj}'] = np.array(
                    qqo__uyynm, np.int64)
                rjmzr__gram += f"""  arr_list_{rlbcy__cnyrj} = bodo.hiframes.table.get_table_block(table, {rlbcy__cnyrj})
"""
                rjmzr__gram += (
                    f'  for i in range(len(arr_list_{rlbcy__cnyrj})):\n')
                rjmzr__gram += (
                    f'    arr_ind_{rlbcy__cnyrj} = orig_arr_inds_{rlbcy__cnyrj}[i]\n'
                    )
                rjmzr__gram += (
                    f'    if arr_ind_{rlbcy__cnyrj} not in copied_cols_set:\n')
                rjmzr__gram += f'      continue\n'
                rjmzr__gram += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{rlbcy__cnyrj}, i, arr_ind_{rlbcy__cnyrj})
"""
                rjmzr__gram += f"""    out_idx_{zlnk__psyf}_{rlbcy__cnyrj} = new_idx_{rlbcy__cnyrj}[i]
"""
                rjmzr__gram += (
                    f'    arr_val_{rlbcy__cnyrj} = arr_list_{rlbcy__cnyrj}[i]\n'
                    )
                if ariae__uhcj:
                    rjmzr__gram += (
                        f'    arr_val_{rlbcy__cnyrj} = arr_val_{rlbcy__cnyrj}.copy()\n'
                        )
                elif vmrpj__fqq:
                    rjmzr__gram += f"""    arr_val_{rlbcy__cnyrj} = arr_val_{rlbcy__cnyrj}.copy() if copy else arr_val_{zlnk__psyf}
"""
                rjmzr__gram += f"""    out_arr_list_{zlnk__psyf}[out_idx_{zlnk__psyf}_{rlbcy__cnyrj}] = arr_val_{rlbcy__cnyrj}
"""
    jrcd__kjay = set()
    for zhv__nipk, zlnk__psyf in new_table_typ.type_to_blk.items():
        if zhv__nipk in oyjg__jobg:
            if isinstance(zhv__nipk, bodo.IntegerArrayType):
                mqs__obpel = zhv__nipk.get_pandas_scalar_type_instance.name
            else:
                mqs__obpel = zhv__nipk.dtype
            vent__cnjrx[f'typ_{zlnk__psyf}'] = mqs__obpel
            unmu__omwqr = oyjg__jobg[zhv__nipk]
            for hwfnv__quf in unmu__omwqr:
                rlbcy__cnyrj = table.type_to_blk[hwfnv__quf]
                if sue__trol is None or rlbcy__cnyrj in wjrd__ajdeq:
                    if (hwfnv__quf not in fdrtq__jiz and hwfnv__quf not in
                        jrcd__kjay):
                        qqo__uyynm = table.block_to_arr_ind[rlbcy__cnyrj]
                        nhsot__szsi = [new_table_typ.block_offsets[
                            lrmrk__wrts] for lrmrk__wrts in qqo__uyynm]
                        vent__cnjrx[f'new_idx_{rlbcy__cnyrj}'] = np.array(
                            nhsot__szsi, np.int64)
                        vent__cnjrx[f'orig_arr_inds_{rlbcy__cnyrj}'
                            ] = np.array(qqo__uyynm, np.int64)
                        rjmzr__gram += f"""  arr_list_{rlbcy__cnyrj} = bodo.hiframes.table.get_table_block(table, {rlbcy__cnyrj})
"""
                    jrcd__kjay.add(hwfnv__quf)
                    rjmzr__gram += (
                        f'  for i in range(len(arr_list_{rlbcy__cnyrj})):\n')
                    rjmzr__gram += (
                        f'    arr_ind_{rlbcy__cnyrj} = orig_arr_inds_{rlbcy__cnyrj}[i]\n'
                        )
                    rjmzr__gram += (
                        f'    if arr_ind_{rlbcy__cnyrj} not in cast_cols_set:\n'
                        )
                    rjmzr__gram += f'      continue\n'
                    rjmzr__gram += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{rlbcy__cnyrj}, i, arr_ind_{rlbcy__cnyrj})
"""
                    rjmzr__gram += f"""    out_idx_{zlnk__psyf}_{rlbcy__cnyrj} = new_idx_{rlbcy__cnyrj}[i]
"""
                    rjmzr__gram += f"""    arr_val_{zlnk__psyf} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{rlbcy__cnyrj}[i], typ_{zlnk__psyf}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    rjmzr__gram += f"""    out_arr_list_{zlnk__psyf}[out_idx_{zlnk__psyf}_{rlbcy__cnyrj}] = arr_val_{zlnk__psyf}
"""
        rjmzr__gram += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{zlnk__psyf}, {zlnk__psyf})
"""
    rjmzr__gram += '  return out_table\n'
    aut__cdaa = {}
    exec(rjmzr__gram, vent__cnjrx, aut__cdaa)
    return aut__cdaa['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    xxz__oyo = args[0]
    if equiv_set.has_shape(xxz__oyo):
        return ArrayAnalysis.AnalyzeResult(shape=xxz__oyo, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
