import os
import warnings
from collections import defaultdict
from glob import has_magic
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow as pa
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, box, intrinsic, models, overload, register_model, unbox
from pyarrow._fs import PyFileSystem
from pyarrow.fs import FSSpecHandler
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_storage_options_pyobject, storage_options_dict_type
from bodo.io.helpers import _get_numba_typ_from_pa_typ, is_nullable
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.str_ext import unicode_to_utf8
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}
READ_STR_AS_DICT_THRESHOLD = 1.0
list_of_files_error_msg = (
    '. Make sure the list/glob passed to read_parquet() only contains paths to files (no directories)'
    )


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(ParquetPredicateType)
def box_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return val


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None, input_file_name_col=
        None, read_as_dict_cols=None):
        self.columns = columns
        self.storage_options = storage_options
        self.input_file_name_col = input_file_name_col
        self.read_as_dict_cols = read_as_dict_cols
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options, input_file_name_col=
                self.input_file_name_col, read_as_dict_cols=self.
                read_as_dict_cols)
        except OSError as cagjw__lebnc:
            if 'non-file path' in str(cagjw__lebnc):
                raise FileNotFoundError(str(cagjw__lebnc))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        zvpxy__tng = lhs.scope
        asahl__kdjzx = lhs.loc
        kab__kaw = None
        if lhs.name in self.locals:
            kab__kaw = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        zkix__icp = {}
        if lhs.name + ':convert' in self.locals:
            zkix__icp = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if kab__kaw is None:
            xbgz__mqoal = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            jcit__iza = get_const_value(file_name, self.func_ir,
                xbgz__mqoal, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            uslyc__cawd = False
            vjz__ivrrz = guard(get_definition, self.func_ir, file_name)
            if isinstance(vjz__ivrrz, ir.Arg):
                typ = self.args[vjz__ivrrz.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, nufkp__wvjis, hen__qdb, col_indices,
                        partition_names, npi__zcj, obpz__mrqqb) = typ.schema
                    uslyc__cawd = True
            if not uslyc__cawd:
                (col_names, nufkp__wvjis, hen__qdb, col_indices,
                    partition_names, npi__zcj, obpz__mrqqb) = (
                    parquet_file_schema(jcit__iza, columns, storage_options
                    =storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            yfbe__crf = list(kab__kaw.keys())
            wwic__emq = {c: htmj__eei for htmj__eei, c in enumerate(yfbe__crf)}
            dbw__hsp = [kjn__opq for kjn__opq in kab__kaw.values()]
            hen__qdb = 'index' if 'index' in wwic__emq else None
            if columns is None:
                selected_columns = yfbe__crf
            else:
                selected_columns = columns
            col_indices = [wwic__emq[c] for c in selected_columns]
            nufkp__wvjis = [dbw__hsp[wwic__emq[c]] for c in selected_columns]
            col_names = selected_columns
            hen__qdb = hen__qdb if hen__qdb in col_names else None
            partition_names = []
            npi__zcj = []
            obpz__mrqqb = []
        nhmhd__jvkx = None if isinstance(hen__qdb, dict
            ) or hen__qdb is None else hen__qdb
        index_column_index = None
        index_column_type = types.none
        if nhmhd__jvkx:
            hoc__yqj = col_names.index(nhmhd__jvkx)
            index_column_index = col_indices.pop(hoc__yqj)
            index_column_type = nufkp__wvjis.pop(hoc__yqj)
            col_names.pop(hoc__yqj)
        for htmj__eei, c in enumerate(col_names):
            if c in zkix__icp:
                nufkp__wvjis[htmj__eei] = zkix__icp[c]
        jhir__qdw = [ir.Var(zvpxy__tng, mk_unique_var('pq_table'),
            asahl__kdjzx), ir.Var(zvpxy__tng, mk_unique_var('pq_index'),
            asahl__kdjzx)]
        lxqx__amc = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, nufkp__wvjis, jhir__qdw, asahl__kdjzx,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, npi__zcj, obpz__mrqqb)]
        return (col_names, jhir__qdw, hen__qdb, lxqx__amc, nufkp__wvjis,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    gyf__smxhb = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    jsp__xigr, kxz__kvpwi = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(jsp__xigr.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, jsp__xigr, kxz__kvpwi, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    mbup__kfy = ', '.join(f'out{htmj__eei}' for htmj__eei in range(gyf__smxhb))
    epb__vnlns = f'def pq_impl(fname, {extra_args}):\n'
    epb__vnlns += (
        f'    (total_rows, {mbup__kfy},) = _pq_reader_py(fname, {extra_args})\n'
        )
    zgum__sck = {}
    exec(epb__vnlns, {}, zgum__sck)
    wpclb__jtb = zgum__sck['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        knou__uuzdj = pq_node.loc.strformat()
        cber__dhq = []
        nsd__noncs = []
        for htmj__eei in pq_node.out_used_cols:
            hhz__jyisn = pq_node.df_colnames[htmj__eei]
            cber__dhq.append(hhz__jyisn)
            if isinstance(pq_node.out_types[htmj__eei], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                nsd__noncs.append(hhz__jyisn)
        lafu__jzg = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', lafu__jzg,
            knou__uuzdj, cber__dhq)
        if nsd__noncs:
            mtkj__lthc = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', mtkj__lthc,
                knou__uuzdj, nsd__noncs)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        evlui__uitrq = set(pq_node.out_used_cols)
        uorrf__kqet = set(pq_node.unsupported_columns)
        jai__yobhf = evlui__uitrq & uorrf__kqet
        if jai__yobhf:
            hjj__pwtp = sorted(jai__yobhf)
            vam__pfq = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            mvwdi__zqnv = 0
            for woi__wnve in hjj__pwtp:
                while pq_node.unsupported_columns[mvwdi__zqnv] != woi__wnve:
                    mvwdi__zqnv += 1
                vam__pfq.append(
                    f"Column '{pq_node.df_colnames[woi__wnve]}' with unsupported arrow type {pq_node.unsupported_arrow_types[mvwdi__zqnv]}"
                    )
                mvwdi__zqnv += 1
            lam__pxo = '\n'.join(vam__pfq)
            raise BodoError(lam__pxo, loc=pq_node.loc)
    ruh__pekt = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col, not pq_node.is_live_table)
    imhol__rgxs = typemap[pq_node.file_name.name]
    srl__ehfy = (imhol__rgxs,) + tuple(typemap[onxbb__uah.name] for
        onxbb__uah in kxz__kvpwi)
    sksm__qpqwd = compile_to_numba_ir(wpclb__jtb, {'_pq_reader_py':
        ruh__pekt}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        srl__ehfy, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(sksm__qpqwd, [pq_node.file_name] + kxz__kvpwi)
    lxqx__amc = sksm__qpqwd.body[:-3]
    if meta_head_only_info:
        lxqx__amc[-3].target = meta_head_only_info[1]
    lxqx__amc[-2].target = pq_node.out_vars[0]
    lxqx__amc[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        is_live_table
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        lxqx__amc.pop(-1)
    elif not pq_node.is_live_table:
        lxqx__amc.pop(-2)
    return lxqx__amc


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    objxk__trhsl = get_overload_const_str(dnf_filter_str)
    mrsxj__hcopu = get_overload_const_str(expr_filter_str)
    wtvac__ftpus = ', '.join(f'f{htmj__eei}' for htmj__eei in range(len(
        var_tup)))
    epb__vnlns = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        epb__vnlns += f'  {wtvac__ftpus}, = var_tup\n'
    epb__vnlns += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    epb__vnlns += f'    dnf_filters_py = {objxk__trhsl}\n'
    epb__vnlns += f'    expr_filters_py = {mrsxj__hcopu}\n'
    epb__vnlns += '  return (dnf_filters_py, expr_filters_py)\n'
    zgum__sck = {}
    exec(epb__vnlns, globals(), zgum__sck)
    return zgum__sck['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col, is_dead_table):
    riq__vuzj = next_label()
    jyih__hquao = ',' if extra_args else ''
    epb__vnlns = f'def pq_reader_py(fname,{extra_args}):\n'
    epb__vnlns += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    epb__vnlns += f"    ev.add_attribute('g_fname', fname)\n"
    epb__vnlns += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{jyih__hquao}))
"""
    epb__vnlns += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    epb__vnlns += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    kwgr__clcch = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    koyph__waej = {c: htmj__eei for htmj__eei, c in enumerate(col_indices)}
    vhj__oica = {c: htmj__eei for htmj__eei, c in enumerate(kwgr__clcch)}
    jqao__kfdt = []
    lzq__glk = set()
    jev__ykotw = partition_names + [input_file_name_col]
    for htmj__eei in out_used_cols:
        if kwgr__clcch[htmj__eei] not in jev__ykotw:
            jqao__kfdt.append(col_indices[htmj__eei])
        elif not input_file_name_col or kwgr__clcch[htmj__eei
            ] != input_file_name_col:
            lzq__glk.add(col_indices[htmj__eei])
    if index_column_index is not None:
        jqao__kfdt.append(index_column_index)
    jqao__kfdt = sorted(jqao__kfdt)
    gjxd__ulcm = {c: htmj__eei for htmj__eei, c in enumerate(jqao__kfdt)}
    rskw__bxrqt = [(int(is_nullable(out_types[koyph__waej[hxls__zkkg]])) if
        hxls__zkkg != index_column_index else int(is_nullable(
        index_column_type))) for hxls__zkkg in jqao__kfdt]
    str_as_dict_cols = []
    for hxls__zkkg in jqao__kfdt:
        if hxls__zkkg == index_column_index:
            kjn__opq = index_column_type
        else:
            kjn__opq = out_types[koyph__waej[hxls__zkkg]]
        if kjn__opq == dict_str_arr_type:
            str_as_dict_cols.append(hxls__zkkg)
    xgaji__gbtz = []
    zscx__rzlkc = {}
    qbyct__swat = []
    lglw__eknb = []
    for htmj__eei, uol__iinfj in enumerate(partition_names):
        try:
            xwuo__npcph = vhj__oica[uol__iinfj]
            if col_indices[xwuo__npcph] not in lzq__glk:
                continue
        except (KeyError, ValueError) as ovxi__pcmm:
            continue
        zscx__rzlkc[uol__iinfj] = len(xgaji__gbtz)
        xgaji__gbtz.append(uol__iinfj)
        qbyct__swat.append(htmj__eei)
        ond__oiegp = out_types[xwuo__npcph].dtype
        sldmp__xihp = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            ond__oiegp)
        lglw__eknb.append(numba_to_c_type(sldmp__xihp))
    epb__vnlns += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    epb__vnlns += f'    out_table = pq_read(\n'
    epb__vnlns += f'        fname_py, {is_parallel},\n'
    epb__vnlns += f'        dnf_filters, expr_filters,\n'
    epb__vnlns += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{riq__vuzj}.ctypes,
"""
    epb__vnlns += f'        {len(jqao__kfdt)},\n'
    epb__vnlns += f'        nullable_cols_arr_{riq__vuzj}.ctypes,\n'
    if len(qbyct__swat) > 0:
        epb__vnlns += (
            f'        np.array({qbyct__swat}, dtype=np.int32).ctypes,\n')
        epb__vnlns += (
            f'        np.array({lglw__eknb}, dtype=np.int32).ctypes,\n')
        epb__vnlns += f'        {len(qbyct__swat)},\n'
    else:
        epb__vnlns += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        epb__vnlns += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        epb__vnlns += f'        0, 0,\n'
    epb__vnlns += f'        total_rows_np.ctypes,\n'
    epb__vnlns += f'        {input_file_name_col is not None},\n'
    epb__vnlns += f'    )\n'
    epb__vnlns += f'    check_and_propagate_cpp_exception()\n'
    epb__vnlns += f'    total_rows = total_rows_np[0]\n'
    if is_parallel:
        epb__vnlns += f"""    local_rows = get_node_portion(total_rows, bodo.get_size(), bodo.get_rank())
"""
    else:
        epb__vnlns += f'    local_rows = total_rows\n'
    sxocg__uxac = index_column_type
    jkmn__jup = TableType(tuple(out_types))
    if is_dead_table:
        jkmn__jup = types.none
    if is_dead_table:
        xtw__fgyt = None
    else:
        xtw__fgyt = []
        tokvp__onnq = 0
        rzyym__ovt = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for htmj__eei, woi__wnve in enumerate(col_indices):
            if tokvp__onnq < len(out_used_cols) and htmj__eei == out_used_cols[
                tokvp__onnq]:
                ksby__szgt = col_indices[htmj__eei]
                if rzyym__ovt and ksby__szgt == rzyym__ovt:
                    xtw__fgyt.append(len(jqao__kfdt) + len(xgaji__gbtz))
                elif ksby__szgt in lzq__glk:
                    roobf__koidb = kwgr__clcch[htmj__eei]
                    xtw__fgyt.append(len(jqao__kfdt) + zscx__rzlkc[
                        roobf__koidb])
                else:
                    xtw__fgyt.append(gjxd__ulcm[woi__wnve])
                tokvp__onnq += 1
            else:
                xtw__fgyt.append(-1)
        xtw__fgyt = np.array(xtw__fgyt, dtype=np.int64)
    if is_dead_table:
        epb__vnlns += '    T = None\n'
    else:
        epb__vnlns += f"""    T = cpp_table_to_py_table(out_table, table_idx_{riq__vuzj}, py_table_type_{riq__vuzj})
"""
        epb__vnlns += f'    T = set_table_len(T, local_rows)\n'
    if index_column_index is None:
        epb__vnlns += '    index_arr = None\n'
    else:
        qihwd__tthr = gjxd__ulcm[index_column_index]
        epb__vnlns += f"""    index_arr = info_to_array(info_from_table(out_table, {qihwd__tthr}), index_arr_type)
"""
    epb__vnlns += f'    delete_table(out_table)\n'
    epb__vnlns += f'    ev.finalize()\n'
    epb__vnlns += f'    return (total_rows, T, index_arr)\n'
    zgum__sck = {}
    tbz__igdf = {f'py_table_type_{riq__vuzj}': jkmn__jup,
        f'table_idx_{riq__vuzj}': xtw__fgyt,
        f'selected_cols_arr_{riq__vuzj}': np.array(jqao__kfdt, np.int32),
        f'nullable_cols_arr_{riq__vuzj}': np.array(rskw__bxrqt, np.int32),
        'index_arr_type': sxocg__uxac, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo,
        'get_node_portion': bodo.libs.distributed_api.get_node_portion,
        'set_table_len': bodo.hiframes.table.set_table_len}
    exec(epb__vnlns, tbz__igdf, zgum__sck)
    ruh__pekt = zgum__sck['pq_reader_py']
    akxqn__qjeu = numba.njit(ruh__pekt, no_cpython_wrapper=True)
    return akxqn__qjeu


def unify_schemas(schemas):
    pmp__eilmq = []
    for schema in schemas:
        for htmj__eei in range(len(schema)):
            uvj__xivao = schema.field(htmj__eei)
            if uvj__xivao.type == pa.large_string():
                schema = schema.set(htmj__eei, uvj__xivao.with_type(pa.
                    string()))
            elif uvj__xivao.type == pa.large_binary():
                schema = schema.set(htmj__eei, uvj__xivao.with_type(pa.
                    binary()))
            elif isinstance(uvj__xivao.type, (pa.ListType, pa.LargeListType)
                ) and uvj__xivao.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(htmj__eei, uvj__xivao.with_type(pa.
                    list_(pa.field(uvj__xivao.type.value_field.name, pa.
                    string()))))
            elif isinstance(uvj__xivao.type, pa.LargeListType):
                schema = schema.set(htmj__eei, uvj__xivao.with_type(pa.
                    list_(pa.field(uvj__xivao.type.value_field.name,
                    uvj__xivao.type.value_type))))
        pmp__eilmq.append(schema)
    return pa.unify_schemas(pmp__eilmq)


class ParquetDataset(object):

    def __init__(self, pa_pq_dataset, prefix=''):
        self.schema = pa_pq_dataset.schema
        self.filesystem = None
        self._bodo_total_rows = 0
        self._prefix = prefix
        self.partitioning = None
        partitioning = pa_pq_dataset.partitioning
        self.partition_names = ([] if partitioning is None or partitioning.
            schema == pa_pq_dataset.schema else list(partitioning.schema.names)
            )
        if self.partition_names:
            self.partitioning_dictionaries = partitioning.dictionaries
            self.partitioning_cls = partitioning.__class__
            self.partitioning_schema = partitioning.schema
        else:
            self.partitioning_dictionaries = {}
        for htmj__eei in range(len(self.schema)):
            uvj__xivao = self.schema.field(htmj__eei)
            if uvj__xivao.type == pa.large_string():
                self.schema = self.schema.set(htmj__eei, uvj__xivao.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for mvmad__pzlv in self.pieces:
            mvmad__pzlv.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            cpxrn__efjm = {mvmad__pzlv: self.partitioning_dictionaries[
                htmj__eei] for htmj__eei, mvmad__pzlv in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, cpxrn__efjm)


class ParquetPiece(object):

    def __init__(self, frag, partitioning, partition_names):
        self._frag = None
        self.format = frag.format
        self.path = frag.path
        self._bodo_num_rows = 0
        self.partition_keys = []
        if partitioning is not None:
            self.partition_keys = ds._get_partition_keys(frag.
                partition_expression)
            self.partition_keys = [(uol__iinfj, partitioning.dictionaries[
                htmj__eei].index(self.partition_keys[uol__iinfj]).as_py()) for
                htmj__eei, uol__iinfj in enumerate(partition_names)]

    @property
    def frag(self):
        if self._frag is None:
            self._frag = self.format.make_fragment(self.path, self.filesystem)
            del self.format
        return self._frag

    @property
    def metadata(self):
        return self.frag.metadata

    @property
    def num_row_groups(self):
        return self.frag.num_row_groups


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None,
    partitioning='hive'):
    if get_row_counts:
        xxzs__noru = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    xlb__evjo = MPI.COMM_WORLD
    if isinstance(fpath, list):
        jmpch__wfps = urlparse(fpath[0])
        protocol = jmpch__wfps.scheme
        blfxh__lmtee = jmpch__wfps.netloc
        for htmj__eei in range(len(fpath)):
            uvj__xivao = fpath[htmj__eei]
            vuxq__gkkap = urlparse(uvj__xivao)
            if vuxq__gkkap.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if vuxq__gkkap.netloc != blfxh__lmtee:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[htmj__eei] = uvj__xivao.rstrip('/')
    else:
        jmpch__wfps = urlparse(fpath)
        protocol = jmpch__wfps.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as ovxi__pcmm:
            nnmg__vts = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(nnmg__vts)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as ovxi__pcmm:
            nnmg__vts = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            ugq__irb = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(ugq__irb)))
        elif protocol == 'http':
            fs.append(PyFileSystem(FSSpecHandler(fsspec.filesystem('http'))))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(pa.fs.LocalFileSystem())
        return fs[0]

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pa.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            mrgwe__ymw = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(mrgwe__ymw) == 0:
            raise BodoError('No files found matching glob pattern')
        return mrgwe__ymw
    cltr__bgoma = False
    if get_row_counts:
        njl__yrqyi = getfs(parallel=True)
        cltr__bgoma = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        btl__fkxjp = 1
        tugi__fqoea = os.cpu_count()
        if tugi__fqoea is not None and tugi__fqoea > 1:
            btl__fkxjp = tugi__fqoea // 2
        try:
            if get_row_counts:
                wzhg__jsq = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    wzhg__jsq.add_attribute('g_dnf_filter', str(dnf_filters))
            vehqw__qdzrg = pa.io_thread_count()
            pa.set_io_thread_count(btl__fkxjp)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{jmpch__wfps.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    clem__bbxmj = [uvj__xivao[len(prefix):] for uvj__xivao in
                        fpath]
                else:
                    clem__bbxmj = fpath[len(prefix):]
            else:
                clem__bbxmj = fpath
            if isinstance(clem__bbxmj, list):
                rjbov__uwri = []
                for mvmad__pzlv in clem__bbxmj:
                    if has_magic(mvmad__pzlv):
                        rjbov__uwri += glob(protocol, getfs(), mvmad__pzlv)
                    else:
                        rjbov__uwri.append(mvmad__pzlv)
                clem__bbxmj = rjbov__uwri
            elif has_magic(clem__bbxmj):
                clem__bbxmj = glob(protocol, getfs(), clem__bbxmj)
            sbb__aard = pq.ParquetDataset(clem__bbxmj, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                sbb__aard._filters = dnf_filters
                sbb__aard._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            xze__iucz = len(sbb__aard.files)
            sbb__aard = ParquetDataset(sbb__aard, prefix)
            pa.set_io_thread_count(vehqw__qdzrg)
            if typing_pa_schema:
                sbb__aard.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    wzhg__jsq.add_attribute('num_pieces_before_filter',
                        xze__iucz)
                    wzhg__jsq.add_attribute('num_pieces_after_filter', len(
                        sbb__aard.pieces))
                wzhg__jsq.finalize()
        except Exception as cagjw__lebnc:
            if isinstance(cagjw__lebnc, IsADirectoryError):
                cagjw__lebnc = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(cagjw__lebnc, (
                OSError, FileNotFoundError)):
                cagjw__lebnc = BodoError(str(cagjw__lebnc) +
                    list_of_files_error_msg)
            else:
                cagjw__lebnc = BodoError(
                    f"""error from pyarrow: {type(cagjw__lebnc).__name__}: {str(cagjw__lebnc)}
"""
                    )
            xlb__evjo.bcast(cagjw__lebnc)
            raise cagjw__lebnc
        if get_row_counts:
            pwefs__bbxj = tracing.Event('bcast dataset')
        sbb__aard = xlb__evjo.bcast(sbb__aard)
    else:
        if get_row_counts:
            pwefs__bbxj = tracing.Event('bcast dataset')
        sbb__aard = xlb__evjo.bcast(None)
        if isinstance(sbb__aard, Exception):
            gywm__vteix = sbb__aard
            raise gywm__vteix
    sbb__aard.set_fs(getfs())
    if get_row_counts:
        pwefs__bbxj.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = cltr__bgoma = False
    if get_row_counts or cltr__bgoma:
        if get_row_counts and tracing.is_tracing():
            jqhh__vzly = tracing.Event('get_row_counts')
            jqhh__vzly.add_attribute('g_num_pieces', len(sbb__aard.pieces))
            jqhh__vzly.add_attribute('g_expr_filters', str(expr_filters))
        lmnmq__qvjfv = 0.0
        num_pieces = len(sbb__aard.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        anv__kuc = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        zqzdq__zaazr = 0
        pqpvg__jdwu = 0
        sfuqo__ztxi = 0
        seft__wtsq = True
        if expr_filters is not None:
            import random
            random.seed(37)
            koylt__igbc = random.sample(sbb__aard.pieces, k=len(sbb__aard.
                pieces))
        else:
            koylt__igbc = sbb__aard.pieces
        fpaths = [mvmad__pzlv.path for mvmad__pzlv in koylt__igbc[start:
            anv__kuc]]
        btl__fkxjp = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(btl__fkxjp)
        pa.set_cpu_count(btl__fkxjp)
        gywm__vteix = None
        try:
            prsz__lked = ds.dataset(fpaths, filesystem=sbb__aard.filesystem,
                partitioning=sbb__aard.partitioning)
            for ewarh__jytes, frag in zip(koylt__igbc[start:anv__kuc],
                prsz__lked.get_fragments()):
                if cltr__bgoma:
                    hthxa__hblza = frag.metadata.schema.to_arrow_schema()
                    rqo__qvv = set(hthxa__hblza.names)
                    oxlc__zcktr = set(sbb__aard.schema.names) - set(sbb__aard
                        .partition_names)
                    if oxlc__zcktr != rqo__qvv:
                        olwyi__jvih = rqo__qvv - oxlc__zcktr
                        mips__qwghh = oxlc__zcktr - rqo__qvv
                        xbgz__mqoal = (
                            f'Schema in {ewarh__jytes} was different.\n')
                        if olwyi__jvih:
                            xbgz__mqoal += f"""File contains column(s) {olwyi__jvih} not found in other files in the dataset.
"""
                        if mips__qwghh:
                            xbgz__mqoal += f"""File missing column(s) {mips__qwghh} found in other files in the dataset.
"""
                        raise BodoError(xbgz__mqoal)
                    try:
                        sbb__aard.schema = unify_schemas([sbb__aard.schema,
                            hthxa__hblza])
                    except Exception as cagjw__lebnc:
                        xbgz__mqoal = (
                            f'Schema in {ewarh__jytes} was different.\n' +
                            str(cagjw__lebnc))
                        raise BodoError(xbgz__mqoal)
                hlak__mdgwg = time.time()
                mzkav__zbuma = frag.scanner(schema=prsz__lked.schema,
                    filter=expr_filters, use_threads=True).count_rows()
                lmnmq__qvjfv += time.time() - hlak__mdgwg
                ewarh__jytes._bodo_num_rows = mzkav__zbuma
                zqzdq__zaazr += mzkav__zbuma
                pqpvg__jdwu += frag.num_row_groups
                sfuqo__ztxi += sum(ocxw__wsc.total_byte_size for ocxw__wsc in
                    frag.row_groups)
        except Exception as cagjw__lebnc:
            gywm__vteix = cagjw__lebnc
        if xlb__evjo.allreduce(gywm__vteix is not None, op=MPI.LOR):
            for gywm__vteix in xlb__evjo.allgather(gywm__vteix):
                if gywm__vteix:
                    if isinstance(fpath, list) and isinstance(gywm__vteix,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(gywm__vteix) +
                            list_of_files_error_msg)
                    raise gywm__vteix
        if cltr__bgoma:
            seft__wtsq = xlb__evjo.allreduce(seft__wtsq, op=MPI.LAND)
            if not seft__wtsq:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            sbb__aard._bodo_total_rows = xlb__evjo.allreduce(zqzdq__zaazr,
                op=MPI.SUM)
            adcf__ein = xlb__evjo.allreduce(pqpvg__jdwu, op=MPI.SUM)
            aeg__fgai = xlb__evjo.allreduce(sfuqo__ztxi, op=MPI.SUM)
            xdoyt__uikpw = np.array([mvmad__pzlv._bodo_num_rows for
                mvmad__pzlv in sbb__aard.pieces])
            xdoyt__uikpw = xlb__evjo.allreduce(xdoyt__uikpw, op=MPI.SUM)
            for mvmad__pzlv, vjubk__girh in zip(sbb__aard.pieces, xdoyt__uikpw
                ):
                mvmad__pzlv._bodo_num_rows = vjubk__girh
            if is_parallel and bodo.get_rank(
                ) == 0 and adcf__ein < bodo.get_size() and adcf__ein != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({adcf__ein}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if adcf__ein == 0:
                iqz__xyqpx = 0
            else:
                iqz__xyqpx = aeg__fgai // adcf__ein
            if (bodo.get_rank() == 0 and aeg__fgai >= 20 * 1048576 and 
                iqz__xyqpx < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({iqz__xyqpx} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                jqhh__vzly.add_attribute('g_total_num_row_groups', adcf__ein)
                jqhh__vzly.add_attribute('total_scan_time', lmnmq__qvjfv)
                crej__uylnw = np.array([mvmad__pzlv._bodo_num_rows for
                    mvmad__pzlv in sbb__aard.pieces])
                ubag__isrwl = np.percentile(crej__uylnw, [25, 50, 75])
                jqhh__vzly.add_attribute('g_row_counts_min', crej__uylnw.min())
                jqhh__vzly.add_attribute('g_row_counts_Q1', ubag__isrwl[0])
                jqhh__vzly.add_attribute('g_row_counts_median', ubag__isrwl[1])
                jqhh__vzly.add_attribute('g_row_counts_Q3', ubag__isrwl[2])
                jqhh__vzly.add_attribute('g_row_counts_max', crej__uylnw.max())
                jqhh__vzly.add_attribute('g_row_counts_mean', crej__uylnw.
                    mean())
                jqhh__vzly.add_attribute('g_row_counts_std', crej__uylnw.std())
                jqhh__vzly.add_attribute('g_row_counts_sum', crej__uylnw.sum())
                jqhh__vzly.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(sbb__aard)
    if get_row_counts:
        xxzs__noru.finalize()
    if cltr__bgoma and is_parallel:
        if tracing.is_tracing():
            brc__bcqky = tracing.Event('unify_schemas_across_ranks')
        gywm__vteix = None
        try:
            sbb__aard.schema = xlb__evjo.allreduce(sbb__aard.schema, bodo.
                io.helpers.pa_schema_unify_mpi_op)
        except Exception as cagjw__lebnc:
            gywm__vteix = cagjw__lebnc
        if tracing.is_tracing():
            brc__bcqky.finalize()
        if xlb__evjo.allreduce(gywm__vteix is not None, op=MPI.LOR):
            for gywm__vteix in xlb__evjo.allgather(gywm__vteix):
                if gywm__vteix:
                    xbgz__mqoal = (
                        f'Schema in some files were different.\n' + str(
                        gywm__vteix))
                    raise BodoError(xbgz__mqoal)
    return sbb__aard


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    tugi__fqoea = os.cpu_count()
    if tugi__fqoea is None or tugi__fqoea == 0:
        tugi__fqoea = 2
    kowj__bxll = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), tugi__fqoea
        )
    mhqc__wyb = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), tugi__fqoea
        )
    if is_parallel and len(fpaths) > mhqc__wyb and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(mhqc__wyb)
        pa.set_cpu_count(mhqc__wyb)
    else:
        pa.set_io_thread_count(kowj__bxll)
        pa.set_cpu_count(kowj__bxll)
    omu__aad = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    itmf__rpcgq = set(str_as_dict_cols)
    for htmj__eei, name in enumerate(schema.names):
        if name in itmf__rpcgq:
            gbg__rbozz = schema.field(htmj__eei)
            fjos__dkr = pa.field(name, pa.dictionary(pa.int32(), gbg__rbozz
                .type), gbg__rbozz.nullable)
            schema = schema.remove(htmj__eei).insert(htmj__eei, fjos__dkr)
    sbb__aard = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=omu__aad)
    col_names = sbb__aard.schema.names
    umtu__ymedb = [col_names[uodsf__mykt] for uodsf__mykt in selected_fields]
    oyr__bzh = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if oyr__bzh and expr_filters is None:
        yxi__rosoe = []
        rmbwo__bmqaj = 0
        ddgaq__zbyax = 0
        for frag in sbb__aard.get_fragments():
            evt__zjs = []
            for ocxw__wsc in frag.row_groups:
                hkca__kec = ocxw__wsc.num_rows
                if start_offset < rmbwo__bmqaj + hkca__kec:
                    if ddgaq__zbyax == 0:
                        ifh__qlj = start_offset - rmbwo__bmqaj
                        uvp__gpq = min(hkca__kec - ifh__qlj, rows_to_read)
                    else:
                        uvp__gpq = min(hkca__kec, rows_to_read - ddgaq__zbyax)
                    ddgaq__zbyax += uvp__gpq
                    evt__zjs.append(ocxw__wsc.id)
                rmbwo__bmqaj += hkca__kec
                if ddgaq__zbyax == rows_to_read:
                    break
            yxi__rosoe.append(frag.subset(row_group_ids=evt__zjs))
            if ddgaq__zbyax == rows_to_read:
                break
        sbb__aard = ds.FileSystemDataset(yxi__rosoe, sbb__aard.schema,
            omu__aad, filesystem=sbb__aard.filesystem)
        start_offset = ifh__qlj
    xda__hhs = sbb__aard.scanner(columns=umtu__ymedb, filter=expr_filters,
        use_threads=True).to_reader()
    return sbb__aard, xda__hhs, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    wjt__dto = [c for c in pa_schema.names if isinstance(pa_schema.field(c)
        .type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(wjt__dto) == 0:
        pq_dataset._category_info = {}
        return
    xlb__evjo = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            tvigm__focg = pq_dataset.pieces[0].frag.head(100, columns=wjt__dto)
            jtq__kkaw = {c: tuple(tvigm__focg.column(c).chunk(0).dictionary
                .to_pylist()) for c in wjt__dto}
            del tvigm__focg
        except Exception as cagjw__lebnc:
            xlb__evjo.bcast(cagjw__lebnc)
            raise cagjw__lebnc
        xlb__evjo.bcast(jtq__kkaw)
    else:
        jtq__kkaw = xlb__evjo.bcast(None)
        if isinstance(jtq__kkaw, Exception):
            gywm__vteix = jtq__kkaw
            raise gywm__vteix
    pq_dataset._category_info = jtq__kkaw


def get_pandas_metadata(schema, num_pieces):
    hen__qdb = None
    oyhx__bfaci = defaultdict(lambda : None)
    gwuw__fqk = b'pandas'
    if schema.metadata is not None and gwuw__fqk in schema.metadata:
        import json
        ewpz__cwy = json.loads(schema.metadata[gwuw__fqk].decode('utf8'))
        fcicm__tuuz = len(ewpz__cwy['index_columns'])
        if fcicm__tuuz > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        hen__qdb = ewpz__cwy['index_columns'][0] if fcicm__tuuz else None
        if not isinstance(hen__qdb, str) and not isinstance(hen__qdb, dict):
            hen__qdb = None
        for rvs__qzt in ewpz__cwy['columns']:
            zicd__wwl = rvs__qzt['name']
            if rvs__qzt['pandas_type'].startswith('int'
                ) and zicd__wwl is not None:
                if rvs__qzt['numpy_type'].startswith('Int'):
                    oyhx__bfaci[zicd__wwl] = True
                else:
                    oyhx__bfaci[zicd__wwl] = False
    return hen__qdb, oyhx__bfaci


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for zicd__wwl in pa_schema.names:
        adrcl__hyqci = pa_schema.field(zicd__wwl)
        if adrcl__hyqci.type in (pa.string(), pa.large_string()):
            str_columns.append(zicd__wwl)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    xlb__evjo = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        koylt__igbc = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        koylt__igbc = pq_dataset.pieces
    ukuh__ehtf = np.zeros(len(str_columns), dtype=np.int64)
    qtvl__fnuzw = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(koylt__igbc):
        ewarh__jytes = koylt__igbc[bodo.get_rank()]
        try:
            metadata = ewarh__jytes.metadata
            for htmj__eei in range(ewarh__jytes.num_row_groups):
                for tokvp__onnq, zicd__wwl in enumerate(str_columns):
                    mvwdi__zqnv = pa_schema.get_field_index(zicd__wwl)
                    ukuh__ehtf[tokvp__onnq] += metadata.row_group(htmj__eei
                        ).column(mvwdi__zqnv).total_uncompressed_size
            yja__mzrmx = metadata.num_rows
        except Exception as cagjw__lebnc:
            if isinstance(cagjw__lebnc, (OSError, FileNotFoundError)):
                yja__mzrmx = 0
            else:
                raise
    else:
        yja__mzrmx = 0
    aek__sqi = xlb__evjo.allreduce(yja__mzrmx, op=MPI.SUM)
    if aek__sqi == 0:
        return set()
    xlb__evjo.Allreduce(ukuh__ehtf, qtvl__fnuzw, op=MPI.SUM)
    slvd__tihl = qtvl__fnuzw / aek__sqi
    tpgw__bhgd = set()
    for htmj__eei, kvt__jqx in enumerate(slvd__tihl):
        if kvt__jqx < READ_STR_AS_DICT_THRESHOLD:
            zicd__wwl = str_columns[htmj__eei][0]
            tpgw__bhgd.add(zicd__wwl)
    return tpgw__bhgd


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    nufkp__wvjis = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    qvh__lioo = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    begk__mfzxh = read_as_dict_cols - qvh__lioo
    if len(begk__mfzxh) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {begk__mfzxh}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(qvh__lioo)
    qvh__lioo = qvh__lioo - read_as_dict_cols
    str_columns = [vicrb__qbc for vicrb__qbc in str_columns if vicrb__qbc in
        qvh__lioo]
    tpgw__bhgd: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    tpgw__bhgd.update(read_as_dict_cols)
    col_names = pa_schema.names
    hen__qdb, oyhx__bfaci = get_pandas_metadata(pa_schema, num_pieces)
    dbw__hsp = []
    yzs__rdct = []
    ulq__fmg = []
    for htmj__eei, c in enumerate(col_names):
        if c in partition_names:
            continue
        adrcl__hyqci = pa_schema.field(c)
        inzsg__abhf, iak__ecsff = _get_numba_typ_from_pa_typ(adrcl__hyqci, 
            c == hen__qdb, oyhx__bfaci[c], pq_dataset._category_info,
            str_as_dict=c in tpgw__bhgd)
        dbw__hsp.append(inzsg__abhf)
        yzs__rdct.append(iak__ecsff)
        ulq__fmg.append(adrcl__hyqci.type)
    if partition_names:
        dbw__hsp += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[htmj__eei]) for htmj__eei in range(
            len(partition_names))]
        yzs__rdct.extend([True] * len(partition_names))
        ulq__fmg.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        dbw__hsp += [dict_str_arr_type]
        yzs__rdct.append(True)
        ulq__fmg.append(None)
    kwdg__xbhkn = {c: htmj__eei for htmj__eei, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in kwdg__xbhkn:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if hen__qdb and not isinstance(hen__qdb, dict
        ) and hen__qdb not in selected_columns:
        selected_columns.append(hen__qdb)
    col_names = selected_columns
    col_indices = []
    nufkp__wvjis = []
    npi__zcj = []
    obpz__mrqqb = []
    for htmj__eei, c in enumerate(col_names):
        ksby__szgt = kwdg__xbhkn[c]
        col_indices.append(ksby__szgt)
        nufkp__wvjis.append(dbw__hsp[ksby__szgt])
        if not yzs__rdct[ksby__szgt]:
            npi__zcj.append(htmj__eei)
            obpz__mrqqb.append(ulq__fmg[ksby__szgt])
    return (col_names, nufkp__wvjis, hen__qdb, col_indices, partition_names,
        npi__zcj, obpz__mrqqb)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    baup__tsxv = dictionary.to_pandas()
    code__rbu = bodo.typeof(baup__tsxv).dtype
    if isinstance(code__rbu, types.Integer):
        afbrn__dcawl = PDCategoricalDtype(tuple(baup__tsxv), code__rbu, 
            False, int_type=code__rbu)
    else:
        afbrn__dcawl = PDCategoricalDtype(tuple(baup__tsxv), code__rbu, False)
    return CategoricalArrayType(afbrn__dcawl)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, parquet_predicate_type,
    parquet_predicate_type, storage_options_dict_type, types.int64, types.
    voidptr, types.int32, types.voidptr, types.voidptr, types.voidptr,
    types.int32, types.voidptr, types.int32, types.voidptr, types.boolean))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        dnfqz__wbumh = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        egxf__pou = cgutils.get_or_insert_function(builder.module,
            dnfqz__wbumh, name='pq_write')
        vfxlp__atp = builder.call(egxf__pou, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return vfxlp__atp
    return types.int64(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr,
        types.int64, types.voidptr), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        dnfqz__wbumh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        egxf__pou = cgutils.get_or_insert_function(builder.module,
            dnfqz__wbumh, name='pq_write_partitioned')
        builder.call(egxf__pou, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
