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
    iagk__vlfie = not is_overload_none(func_name)
    if iagk__vlfie:
        func_name = get_overload_const_str(func_name)
        jvwda__dvpvy = get_overload_const_bool(is_method)
    sduq__snb = out_arr_typ.instance_type if isinstance(out_arr_typ, types.
        TypeRef) else out_arr_typ
    vhmfj__swl = sduq__snb == types.none
    diyk__kmw = len(table.arr_types)
    if vhmfj__swl:
        dupvh__ewg = table
    else:
        vwr__zcm = tuple([sduq__snb] * diyk__kmw)
        dupvh__ewg = TableType(vwr__zcm)
    ixp__erm = {'bodo': bodo, 'lst_dtype': sduq__snb, 'table_typ': dupvh__ewg}
    mtifp__zbcey = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if vhmfj__swl:
        mtifp__zbcey += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        mtifp__zbcey += f'  l = len(table)\n'
    else:
        mtifp__zbcey += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({diyk__kmw}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        qukuj__lzpcr = used_cols.instance_type
        zvvu__vnqdt = np.array(qukuj__lzpcr.meta, dtype=np.int64)
        ixp__erm['used_cols_glbl'] = zvvu__vnqdt
        pua__pah = set([table.block_nums[kro__wshnw] for kro__wshnw in
            zvvu__vnqdt])
        mtifp__zbcey += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        mtifp__zbcey += f'  used_cols_set = None\n'
        zvvu__vnqdt = None
    mtifp__zbcey += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for bmqmw__zjkvb in table.type_to_blk.values():
        mtifp__zbcey += f"""  blk_{bmqmw__zjkvb} = bodo.hiframes.table.get_table_block(table, {bmqmw__zjkvb})
"""
        if vhmfj__swl:
            mtifp__zbcey += f"""  out_list_{bmqmw__zjkvb} = bodo.hiframes.table.alloc_list_like(blk_{bmqmw__zjkvb}, len(blk_{bmqmw__zjkvb}), False)
"""
            dmql__kahs = f'out_list_{bmqmw__zjkvb}'
        else:
            dmql__kahs = 'out_list'
        if zvvu__vnqdt is None or bmqmw__zjkvb in pua__pah:
            mtifp__zbcey += f'  for i in range(len(blk_{bmqmw__zjkvb})):\n'
            ixp__erm[f'col_indices_{bmqmw__zjkvb}'] = np.array(table.
                block_to_arr_ind[bmqmw__zjkvb], dtype=np.int64)
            mtifp__zbcey += f'    col_loc = col_indices_{bmqmw__zjkvb}[i]\n'
            if zvvu__vnqdt is not None:
                mtifp__zbcey += f'    if col_loc not in used_cols_set:\n'
                mtifp__zbcey += f'        continue\n'
            if vhmfj__swl:
                liih__gerl = 'i'
            else:
                liih__gerl = 'col_loc'
            if not iagk__vlfie:
                mtifp__zbcey += (
                    f'    {dmql__kahs}[{liih__gerl}] = blk_{bmqmw__zjkvb}[i]\n'
                    )
            elif jvwda__dvpvy:
                mtifp__zbcey += f"""    {dmql__kahs}[{liih__gerl}] = blk_{bmqmw__zjkvb}[i].{func_name}()
"""
            else:
                mtifp__zbcey += f"""    {dmql__kahs}[{liih__gerl}] = {func_name}(blk_{bmqmw__zjkvb}[i])
"""
        if vhmfj__swl:
            mtifp__zbcey += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {dmql__kahs}, {bmqmw__zjkvb})
"""
    if vhmfj__swl:
        mtifp__zbcey += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        mtifp__zbcey += '  return out_table\n'
    else:
        mtifp__zbcey += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    spb__vvv = {}
    exec(mtifp__zbcey, ixp__erm, spb__vvv)
    return spb__vvv['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    xiqi__szwq = args[0]
    if equiv_set.has_shape(xiqi__szwq):
        return ArrayAnalysis.AnalyzeResult(shape=xiqi__szwq, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    ixp__erm = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.distributed_api.
        Reduce_Type.Sum.value)}
    mtifp__zbcey = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    mtifp__zbcey += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for bmqmw__zjkvb in table.type_to_blk.values():
        mtifp__zbcey += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {bmqmw__zjkvb})\n'
            )
        ixp__erm[f'col_indices_{bmqmw__zjkvb}'] = np.array(table.
            block_to_arr_ind[bmqmw__zjkvb], dtype=np.int64)
        mtifp__zbcey += '  for i in range(len(blk)):\n'
        mtifp__zbcey += f'    col_loc = col_indices_{bmqmw__zjkvb}[i]\n'
        mtifp__zbcey += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    mtifp__zbcey += '  if parallel:\n'
    mtifp__zbcey += '    for i in range(start_offset, len(out_arr)):\n'
    mtifp__zbcey += """      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)
"""
    spb__vvv = {}
    exec(mtifp__zbcey, ixp__erm, spb__vvv)
    return spb__vvv['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    lduzu__dqbz = table.type_to_blk[arr_type]
    ixp__erm = {'bodo': bodo}
    ixp__erm['col_indices'] = np.array(table.block_to_arr_ind[lduzu__dqbz],
        dtype=np.int64)
    wqzpr__xsm = col_nums_meta.instance_type
    ixp__erm['col_nums'] = np.array(wqzpr__xsm.meta, np.int64)
    mtifp__zbcey = 'def impl(table, col_nums_meta, arr_type):\n'
    mtifp__zbcey += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {lduzu__dqbz})\n')
    mtifp__zbcey += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    mtifp__zbcey += '  n = len(table)\n'
    lyc__bno = arr_type == bodo.string_array_type
    if lyc__bno:
        mtifp__zbcey += '  total_chars = 0\n'
        mtifp__zbcey += '  for c in col_nums:\n'
        mtifp__zbcey += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        mtifp__zbcey += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        mtifp__zbcey += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        mtifp__zbcey += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        mtifp__zbcey += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    mtifp__zbcey += '  for i in range(len(col_nums)):\n'
    mtifp__zbcey += '    c = col_nums[i]\n'
    if not lyc__bno:
        mtifp__zbcey += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    mtifp__zbcey += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    mtifp__zbcey += '    off = i * n\n'
    mtifp__zbcey += '    for j in range(len(arr)):\n'
    mtifp__zbcey += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    mtifp__zbcey += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    mtifp__zbcey += '      else:\n'
    mtifp__zbcey += '        out_arr[off+j] = arr[j]\n'
    mtifp__zbcey += '  return out_arr\n'
    mktvo__dzwyd = {}
    exec(mtifp__zbcey, ixp__erm, mktvo__dzwyd)
    adfi__rrnh = mktvo__dzwyd['impl']
    return adfi__rrnh


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    ucqcp__hbnt = not is_overload_false(copy)
    fjxts__asqos = is_overload_true(copy)
    ixp__erm = {'bodo': bodo}
    ilrbc__gsu = table.arr_types
    rxitw__wxm = new_table_typ.arr_types
    wbgxj__zpg: Set[int] = set()
    wvoce__fyq: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    xygqp__vmi: Set[types.Type] = set()
    for kro__wshnw, tfjkd__uokxr in enumerate(ilrbc__gsu):
        pcrw__tmh = rxitw__wxm[kro__wshnw]
        if tfjkd__uokxr == pcrw__tmh:
            xygqp__vmi.add(tfjkd__uokxr)
        else:
            wbgxj__zpg.add(kro__wshnw)
            wvoce__fyq[pcrw__tmh].add(tfjkd__uokxr)
    mtifp__zbcey = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    mtifp__zbcey += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    mtifp__zbcey += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    eemy__jkxa = set(range(len(ilrbc__gsu)))
    braq__soxyn = eemy__jkxa - wbgxj__zpg
    if not is_overload_none(used_cols):
        qukuj__lzpcr = used_cols.instance_type
        qfntr__lcay = set(qukuj__lzpcr.meta)
        wbgxj__zpg = wbgxj__zpg & qfntr__lcay
        braq__soxyn = braq__soxyn & qfntr__lcay
        pua__pah = set([table.block_nums[kro__wshnw] for kro__wshnw in
            qfntr__lcay])
    else:
        qfntr__lcay = None
    ixp__erm['cast_cols'] = np.array(list(wbgxj__zpg), dtype=np.int64)
    ixp__erm['copied_cols'] = np.array(list(braq__soxyn), dtype=np.int64)
    mtifp__zbcey += f'  copied_cols_set = set(copied_cols)\n'
    mtifp__zbcey += f'  cast_cols_set = set(cast_cols)\n'
    for jmonp__bftir, bmqmw__zjkvb in new_table_typ.type_to_blk.items():
        ixp__erm[f'typ_list_{bmqmw__zjkvb}'] = types.List(jmonp__bftir)
        mtifp__zbcey += f"""  out_arr_list_{bmqmw__zjkvb} = bodo.hiframes.table.alloc_list_like(typ_list_{bmqmw__zjkvb}, {len(new_table_typ.block_to_arr_ind[bmqmw__zjkvb])}, False)
"""
        if jmonp__bftir in xygqp__vmi:
            kkm__sei = table.type_to_blk[jmonp__bftir]
            if qfntr__lcay is None or kkm__sei in pua__pah:
                jdeul__xup = table.block_to_arr_ind[kkm__sei]
                tak__mhwfr = [new_table_typ.block_offsets[mbet__mjksf] for
                    mbet__mjksf in jdeul__xup]
                ixp__erm[f'new_idx_{kkm__sei}'] = np.array(tak__mhwfr, np.int64
                    )
                ixp__erm[f'orig_arr_inds_{kkm__sei}'] = np.array(jdeul__xup,
                    np.int64)
                mtifp__zbcey += f"""  arr_list_{kkm__sei} = bodo.hiframes.table.get_table_block(table, {kkm__sei})
"""
                mtifp__zbcey += (
                    f'  for i in range(len(arr_list_{kkm__sei})):\n')
                mtifp__zbcey += (
                    f'    arr_ind_{kkm__sei} = orig_arr_inds_{kkm__sei}[i]\n')
                mtifp__zbcey += (
                    f'    if arr_ind_{kkm__sei} not in copied_cols_set:\n')
                mtifp__zbcey += f'      continue\n'
                mtifp__zbcey += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{kkm__sei}, i, arr_ind_{kkm__sei})
"""
                mtifp__zbcey += (
                    f'    out_idx_{bmqmw__zjkvb}_{kkm__sei} = new_idx_{kkm__sei}[i]\n'
                    )
                mtifp__zbcey += (
                    f'    arr_val_{kkm__sei} = arr_list_{kkm__sei}[i]\n')
                if fjxts__asqos:
                    mtifp__zbcey += (
                        f'    arr_val_{kkm__sei} = arr_val_{kkm__sei}.copy()\n'
                        )
                elif ucqcp__hbnt:
                    mtifp__zbcey += f"""    arr_val_{kkm__sei} = arr_val_{kkm__sei}.copy() if copy else arr_val_{bmqmw__zjkvb}
"""
                mtifp__zbcey += f"""    out_arr_list_{bmqmw__zjkvb}[out_idx_{bmqmw__zjkvb}_{kkm__sei}] = arr_val_{kkm__sei}
"""
    pyj__dciv = set()
    for jmonp__bftir, bmqmw__zjkvb in new_table_typ.type_to_blk.items():
        if jmonp__bftir in wvoce__fyq:
            if isinstance(jmonp__bftir, bodo.IntegerArrayType):
                wsjhl__xlcgo = (jmonp__bftir.
                    get_pandas_scalar_type_instance.name)
            else:
                wsjhl__xlcgo = jmonp__bftir.dtype
            ixp__erm[f'typ_{bmqmw__zjkvb}'] = wsjhl__xlcgo
            uei__kmjp = wvoce__fyq[jmonp__bftir]
            for ljef__dkis in uei__kmjp:
                kkm__sei = table.type_to_blk[ljef__dkis]
                if qfntr__lcay is None or kkm__sei in pua__pah:
                    if (ljef__dkis not in xygqp__vmi and ljef__dkis not in
                        pyj__dciv):
                        jdeul__xup = table.block_to_arr_ind[kkm__sei]
                        tak__mhwfr = [new_table_typ.block_offsets[
                            mbet__mjksf] for mbet__mjksf in jdeul__xup]
                        ixp__erm[f'new_idx_{kkm__sei}'] = np.array(tak__mhwfr,
                            np.int64)
                        ixp__erm[f'orig_arr_inds_{kkm__sei}'] = np.array(
                            jdeul__xup, np.int64)
                        mtifp__zbcey += f"""  arr_list_{kkm__sei} = bodo.hiframes.table.get_table_block(table, {kkm__sei})
"""
                    pyj__dciv.add(ljef__dkis)
                    mtifp__zbcey += (
                        f'  for i in range(len(arr_list_{kkm__sei})):\n')
                    mtifp__zbcey += (
                        f'    arr_ind_{kkm__sei} = orig_arr_inds_{kkm__sei}[i]\n'
                        )
                    mtifp__zbcey += (
                        f'    if arr_ind_{kkm__sei} not in cast_cols_set:\n')
                    mtifp__zbcey += f'      continue\n'
                    mtifp__zbcey += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{kkm__sei}, i, arr_ind_{kkm__sei})
"""
                    mtifp__zbcey += f"""    out_idx_{bmqmw__zjkvb}_{kkm__sei} = new_idx_{kkm__sei}[i]
"""
                    mtifp__zbcey += f"""    arr_val_{bmqmw__zjkvb} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{kkm__sei}[i], typ_{bmqmw__zjkvb}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    mtifp__zbcey += f"""    out_arr_list_{bmqmw__zjkvb}[out_idx_{bmqmw__zjkvb}_{kkm__sei}] = arr_val_{bmqmw__zjkvb}
"""
        mtifp__zbcey += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{bmqmw__zjkvb}, {bmqmw__zjkvb})
"""
    mtifp__zbcey += '  return out_table\n'
    spb__vvv = {}
    exec(mtifp__zbcey, ixp__erm, spb__vvv)
    return spb__vvv['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    xiqi__szwq = args[0]
    if equiv_set.has_shape(xiqi__szwq):
        return ArrayAnalysis.AnalyzeResult(shape=xiqi__szwq, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
