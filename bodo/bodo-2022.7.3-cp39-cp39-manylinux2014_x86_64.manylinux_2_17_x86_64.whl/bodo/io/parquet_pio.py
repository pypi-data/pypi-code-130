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
        except OSError as jnzo__xaq:
            if 'non-file path' in str(jnzo__xaq):
                raise FileNotFoundError(str(jnzo__xaq))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        dclc__gxsk = lhs.scope
        iwta__qgqbj = lhs.loc
        gjz__viq = None
        if lhs.name in self.locals:
            gjz__viq = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        nfsn__pdxpv = {}
        if lhs.name + ':convert' in self.locals:
            nfsn__pdxpv = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if gjz__viq is None:
            pesp__kdkri = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            lcw__kocj = get_const_value(file_name, self.func_ir,
                pesp__kdkri, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            sdsaj__ytqq = False
            qvmtm__liz = guard(get_definition, self.func_ir, file_name)
            if isinstance(qvmtm__liz, ir.Arg):
                typ = self.args[qvmtm__liz.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, uydt__ukxhb, sab__vlc, col_indices,
                        partition_names, sjrbg__axbzr, nqs__lcnf) = typ.schema
                    sdsaj__ytqq = True
            if not sdsaj__ytqq:
                (col_names, uydt__ukxhb, sab__vlc, col_indices,
                    partition_names, sjrbg__axbzr, nqs__lcnf) = (
                    parquet_file_schema(lcw__kocj, columns, storage_options
                    =storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            urlx__djphz = list(gjz__viq.keys())
            permz__tjsuo = {c: phuti__flnu for phuti__flnu, c in enumerate(
                urlx__djphz)}
            yzqw__wsj = [hzgsn__odkae for hzgsn__odkae in gjz__viq.values()]
            sab__vlc = 'index' if 'index' in permz__tjsuo else None
            if columns is None:
                selected_columns = urlx__djphz
            else:
                selected_columns = columns
            col_indices = [permz__tjsuo[c] for c in selected_columns]
            uydt__ukxhb = [yzqw__wsj[permz__tjsuo[c]] for c in selected_columns
                ]
            col_names = selected_columns
            sab__vlc = sab__vlc if sab__vlc in col_names else None
            partition_names = []
            sjrbg__axbzr = []
            nqs__lcnf = []
        wbfq__hyqlj = None if isinstance(sab__vlc, dict
            ) or sab__vlc is None else sab__vlc
        index_column_index = None
        index_column_type = types.none
        if wbfq__hyqlj:
            qpoh__zpm = col_names.index(wbfq__hyqlj)
            index_column_index = col_indices.pop(qpoh__zpm)
            index_column_type = uydt__ukxhb.pop(qpoh__zpm)
            col_names.pop(qpoh__zpm)
        for phuti__flnu, c in enumerate(col_names):
            if c in nfsn__pdxpv:
                uydt__ukxhb[phuti__flnu] = nfsn__pdxpv[c]
        mhs__nmaf = [ir.Var(dclc__gxsk, mk_unique_var('pq_table'),
            iwta__qgqbj), ir.Var(dclc__gxsk, mk_unique_var('pq_index'),
            iwta__qgqbj)]
        nkjep__wqkzg = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, uydt__ukxhb, mhs__nmaf,
            iwta__qgqbj, partition_names, storage_options,
            index_column_index, index_column_type, input_file_name_col,
            sjrbg__axbzr, nqs__lcnf)]
        return (col_names, mhs__nmaf, sab__vlc, nkjep__wqkzg, uydt__ukxhb,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    shds__vouzd = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    zrrtw__vjq, hhkl__uok = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(zrrtw__vjq.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, zrrtw__vjq, hhkl__uok, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    iena__uch = ', '.join(f'out{phuti__flnu}' for phuti__flnu in range(
        shds__vouzd))
    zggo__ztj = f'def pq_impl(fname, {extra_args}):\n'
    zggo__ztj += (
        f'    (total_rows, {iena__uch},) = _pq_reader_py(fname, {extra_args})\n'
        )
    oln__adc = {}
    exec(zggo__ztj, {}, oln__adc)
    gzwt__cekyp = oln__adc['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        vtrjc__ccer = pq_node.loc.strformat()
        mmv__xnbak = []
        eyq__qrcsp = []
        for phuti__flnu in pq_node.out_used_cols:
            ohyeh__dbkg = pq_node.df_colnames[phuti__flnu]
            mmv__xnbak.append(ohyeh__dbkg)
            if isinstance(pq_node.out_types[phuti__flnu], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                eyq__qrcsp.append(ohyeh__dbkg)
        dws__vus = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', dws__vus,
            vtrjc__ccer, mmv__xnbak)
        if eyq__qrcsp:
            nxb__lhg = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', nxb__lhg,
                vtrjc__ccer, eyq__qrcsp)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        arcz__yxqd = set(pq_node.out_used_cols)
        kph__adqjn = set(pq_node.unsupported_columns)
        sik__dxv = arcz__yxqd & kph__adqjn
        if sik__dxv:
            acnil__pjne = sorted(sik__dxv)
            qzruz__yric = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            llny__ylsr = 0
            for ahn__rwcpz in acnil__pjne:
                while pq_node.unsupported_columns[llny__ylsr] != ahn__rwcpz:
                    llny__ylsr += 1
                qzruz__yric.append(
                    f"Column '{pq_node.df_colnames[ahn__rwcpz]}' with unsupported arrow type {pq_node.unsupported_arrow_types[llny__ylsr]}"
                    )
                llny__ylsr += 1
            lple__mquj = '\n'.join(qzruz__yric)
            raise BodoError(lple__mquj, loc=pq_node.loc)
    xvg__cyt = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col, not pq_node.is_live_table)
    kcbu__hig = typemap[pq_node.file_name.name]
    eqc__xzy = (kcbu__hig,) + tuple(typemap[agkfn__twslc.name] for
        agkfn__twslc in hhkl__uok)
    cgtdm__nvzv = compile_to_numba_ir(gzwt__cekyp, {'_pq_reader_py':
        xvg__cyt}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        eqc__xzy, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(cgtdm__nvzv, [pq_node.file_name] + hhkl__uok)
    nkjep__wqkzg = cgtdm__nvzv.body[:-3]
    if meta_head_only_info:
        nkjep__wqkzg[-3].target = meta_head_only_info[1]
    nkjep__wqkzg[-2].target = pq_node.out_vars[0]
    nkjep__wqkzg[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        is_live_table
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        nkjep__wqkzg.pop(-1)
    elif not pq_node.is_live_table:
        nkjep__wqkzg.pop(-2)
    return nkjep__wqkzg


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    ojoda__wvomu = get_overload_const_str(dnf_filter_str)
    ygm__pixe = get_overload_const_str(expr_filter_str)
    sgbic__ueup = ', '.join(f'f{phuti__flnu}' for phuti__flnu in range(len(
        var_tup)))
    zggo__ztj = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        zggo__ztj += f'  {sgbic__ueup}, = var_tup\n'
    zggo__ztj += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    zggo__ztj += f'    dnf_filters_py = {ojoda__wvomu}\n'
    zggo__ztj += f'    expr_filters_py = {ygm__pixe}\n'
    zggo__ztj += '  return (dnf_filters_py, expr_filters_py)\n'
    oln__adc = {}
    exec(zggo__ztj, globals(), oln__adc)
    return oln__adc['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col, is_dead_table):
    npxk__cgu = next_label()
    syrrr__jbfj = ',' if extra_args else ''
    zggo__ztj = f'def pq_reader_py(fname,{extra_args}):\n'
    zggo__ztj += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    zggo__ztj += f"    ev.add_attribute('g_fname', fname)\n"
    zggo__ztj += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{syrrr__jbfj}))
"""
    zggo__ztj += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    zggo__ztj += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    zdur__xgf = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    hwbht__rtmrb = {c: phuti__flnu for phuti__flnu, c in enumerate(col_indices)
        }
    spco__smm = {c: phuti__flnu for phuti__flnu, c in enumerate(zdur__xgf)}
    ldgh__cdhv = []
    tnuht__udga = set()
    ccgu__ayren = partition_names + [input_file_name_col]
    for phuti__flnu in out_used_cols:
        if zdur__xgf[phuti__flnu] not in ccgu__ayren:
            ldgh__cdhv.append(col_indices[phuti__flnu])
        elif not input_file_name_col or zdur__xgf[phuti__flnu
            ] != input_file_name_col:
            tnuht__udga.add(col_indices[phuti__flnu])
    if index_column_index is not None:
        ldgh__cdhv.append(index_column_index)
    ldgh__cdhv = sorted(ldgh__cdhv)
    tffaf__icx = {c: phuti__flnu for phuti__flnu, c in enumerate(ldgh__cdhv)}
    xfcfx__wxzcp = [(int(is_nullable(out_types[hwbht__rtmrb[bwb__hyo]])) if
        bwb__hyo != index_column_index else int(is_nullable(
        index_column_type))) for bwb__hyo in ldgh__cdhv]
    str_as_dict_cols = []
    for bwb__hyo in ldgh__cdhv:
        if bwb__hyo == index_column_index:
            hzgsn__odkae = index_column_type
        else:
            hzgsn__odkae = out_types[hwbht__rtmrb[bwb__hyo]]
        if hzgsn__odkae == dict_str_arr_type:
            str_as_dict_cols.append(bwb__hyo)
    baij__lxlxu = []
    emuka__zwsvm = {}
    oel__gsub = []
    bfpor__sts = []
    for phuti__flnu, uvw__duc in enumerate(partition_names):
        try:
            vuwa__jwes = spco__smm[uvw__duc]
            if col_indices[vuwa__jwes] not in tnuht__udga:
                continue
        except (KeyError, ValueError) as qmna__gpmi:
            continue
        emuka__zwsvm[uvw__duc] = len(baij__lxlxu)
        baij__lxlxu.append(uvw__duc)
        oel__gsub.append(phuti__flnu)
        glt__llfhe = out_types[vuwa__jwes].dtype
        uci__jooe = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            glt__llfhe)
        bfpor__sts.append(numba_to_c_type(uci__jooe))
    zggo__ztj += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    zggo__ztj += f'    out_table = pq_read(\n'
    zggo__ztj += f'        fname_py, {is_parallel},\n'
    zggo__ztj += f'        dnf_filters, expr_filters,\n'
    zggo__ztj += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{npxk__cgu}.ctypes,
"""
    zggo__ztj += f'        {len(ldgh__cdhv)},\n'
    zggo__ztj += f'        nullable_cols_arr_{npxk__cgu}.ctypes,\n'
    if len(oel__gsub) > 0:
        zggo__ztj += f'        np.array({oel__gsub}, dtype=np.int32).ctypes,\n'
        zggo__ztj += (
            f'        np.array({bfpor__sts}, dtype=np.int32).ctypes,\n')
        zggo__ztj += f'        {len(oel__gsub)},\n'
    else:
        zggo__ztj += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        zggo__ztj += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        zggo__ztj += f'        0, 0,\n'
    zggo__ztj += f'        total_rows_np.ctypes,\n'
    zggo__ztj += f'        {input_file_name_col is not None},\n'
    zggo__ztj += f'    )\n'
    zggo__ztj += f'    check_and_propagate_cpp_exception()\n'
    zggo__ztj += f'    total_rows = total_rows_np[0]\n'
    if is_parallel:
        zggo__ztj += f"""    local_rows = get_node_portion(total_rows, bodo.get_size(), bodo.get_rank())
"""
    else:
        zggo__ztj += f'    local_rows = total_rows\n'
    gwiq__iwrfp = index_column_type
    deinn__kpq = TableType(tuple(out_types))
    if is_dead_table:
        deinn__kpq = types.none
    if is_dead_table:
        qepdi__pfe = None
    else:
        qepdi__pfe = []
        wuit__fjglb = 0
        hvr__wszo = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for phuti__flnu, ahn__rwcpz in enumerate(col_indices):
            if wuit__fjglb < len(out_used_cols
                ) and phuti__flnu == out_used_cols[wuit__fjglb]:
                kly__wpi = col_indices[phuti__flnu]
                if hvr__wszo and kly__wpi == hvr__wszo:
                    qepdi__pfe.append(len(ldgh__cdhv) + len(baij__lxlxu))
                elif kly__wpi in tnuht__udga:
                    web__zxtf = zdur__xgf[phuti__flnu]
                    qepdi__pfe.append(len(ldgh__cdhv) + emuka__zwsvm[web__zxtf]
                        )
                else:
                    qepdi__pfe.append(tffaf__icx[ahn__rwcpz])
                wuit__fjglb += 1
            else:
                qepdi__pfe.append(-1)
        qepdi__pfe = np.array(qepdi__pfe, dtype=np.int64)
    if is_dead_table:
        zggo__ztj += '    T = None\n'
    else:
        zggo__ztj += f"""    T = cpp_table_to_py_table(out_table, table_idx_{npxk__cgu}, py_table_type_{npxk__cgu})
"""
        zggo__ztj += f'    T = set_table_len(T, local_rows)\n'
    if index_column_index is None:
        zggo__ztj += '    index_arr = None\n'
    else:
        ebtg__dcrg = tffaf__icx[index_column_index]
        zggo__ztj += f"""    index_arr = info_to_array(info_from_table(out_table, {ebtg__dcrg}), index_arr_type)
"""
    zggo__ztj += f'    delete_table(out_table)\n'
    zggo__ztj += f'    ev.finalize()\n'
    zggo__ztj += f'    return (total_rows, T, index_arr)\n'
    oln__adc = {}
    dxoql__zzff = {f'py_table_type_{npxk__cgu}': deinn__kpq,
        f'table_idx_{npxk__cgu}': qepdi__pfe,
        f'selected_cols_arr_{npxk__cgu}': np.array(ldgh__cdhv, np.int32),
        f'nullable_cols_arr_{npxk__cgu}': np.array(xfcfx__wxzcp, np.int32),
        'index_arr_type': gwiq__iwrfp, 'cpp_table_to_py_table':
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
    exec(zggo__ztj, dxoql__zzff, oln__adc)
    xvg__cyt = oln__adc['pq_reader_py']
    amaue__etvh = numba.njit(xvg__cyt, no_cpython_wrapper=True)
    return amaue__etvh


def unify_schemas(schemas):
    vtd__sjdua = []
    for schema in schemas:
        for phuti__flnu in range(len(schema)):
            hhjux__sipj = schema.field(phuti__flnu)
            if hhjux__sipj.type == pa.large_string():
                schema = schema.set(phuti__flnu, hhjux__sipj.with_type(pa.
                    string()))
            elif hhjux__sipj.type == pa.large_binary():
                schema = schema.set(phuti__flnu, hhjux__sipj.with_type(pa.
                    binary()))
            elif isinstance(hhjux__sipj.type, (pa.ListType, pa.LargeListType)
                ) and hhjux__sipj.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(phuti__flnu, hhjux__sipj.with_type(pa.
                    list_(pa.field(hhjux__sipj.type.value_field.name, pa.
                    string()))))
            elif isinstance(hhjux__sipj.type, pa.LargeListType):
                schema = schema.set(phuti__flnu, hhjux__sipj.with_type(pa.
                    list_(pa.field(hhjux__sipj.type.value_field.name,
                    hhjux__sipj.type.value_type))))
        vtd__sjdua.append(schema)
    return pa.unify_schemas(vtd__sjdua)


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
        for phuti__flnu in range(len(self.schema)):
            hhjux__sipj = self.schema.field(phuti__flnu)
            if hhjux__sipj.type == pa.large_string():
                self.schema = self.schema.set(phuti__flnu, hhjux__sipj.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for aba__iznk in self.pieces:
            aba__iznk.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            zhbv__ptgkz = {aba__iznk: self.partitioning_dictionaries[
                phuti__flnu] for phuti__flnu, aba__iznk in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, zhbv__ptgkz)


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
            self.partition_keys = [(uvw__duc, partitioning.dictionaries[
                phuti__flnu].index(self.partition_keys[uvw__duc]).as_py()) for
                phuti__flnu, uvw__duc in enumerate(partition_names)]

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
        tvlgs__gdxks = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    wvyir__nmo = MPI.COMM_WORLD
    if isinstance(fpath, list):
        mcmq__lyf = urlparse(fpath[0])
        protocol = mcmq__lyf.scheme
        vog__oht = mcmq__lyf.netloc
        for phuti__flnu in range(len(fpath)):
            hhjux__sipj = fpath[phuti__flnu]
            wbe__kmah = urlparse(hhjux__sipj)
            if wbe__kmah.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if wbe__kmah.netloc != vog__oht:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[phuti__flnu] = hhjux__sipj.rstrip('/')
    else:
        mcmq__lyf = urlparse(fpath)
        protocol = mcmq__lyf.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as qmna__gpmi:
            gjc__hgbls = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(gjc__hgbls)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as qmna__gpmi:
            gjc__hgbls = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            xaub__lfbv = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(xaub__lfbv)))
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
            rqmq__xdy = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(rqmq__xdy) == 0:
            raise BodoError('No files found matching glob pattern')
        return rqmq__xdy
    jhh__obm = False
    if get_row_counts:
        eamgo__lfk = getfs(parallel=True)
        jhh__obm = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        dwh__mkxud = 1
        gpcbd__jbo = os.cpu_count()
        if gpcbd__jbo is not None and gpcbd__jbo > 1:
            dwh__mkxud = gpcbd__jbo // 2
        try:
            if get_row_counts:
                ilq__cof = tracing.Event('pq.ParquetDataset', is_parallel=False
                    )
                if tracing.is_tracing():
                    ilq__cof.add_attribute('g_dnf_filter', str(dnf_filters))
            xeb__nkme = pa.io_thread_count()
            pa.set_io_thread_count(dwh__mkxud)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{mcmq__lyf.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    jdb__rpsl = [hhjux__sipj[len(prefix):] for hhjux__sipj in
                        fpath]
                else:
                    jdb__rpsl = fpath[len(prefix):]
            else:
                jdb__rpsl = fpath
            if isinstance(jdb__rpsl, list):
                xqfz__jcd = []
                for aba__iznk in jdb__rpsl:
                    if has_magic(aba__iznk):
                        xqfz__jcd += glob(protocol, getfs(), aba__iznk)
                    else:
                        xqfz__jcd.append(aba__iznk)
                jdb__rpsl = xqfz__jcd
            elif has_magic(jdb__rpsl):
                jdb__rpsl = glob(protocol, getfs(), jdb__rpsl)
            unskl__onz = pq.ParquetDataset(jdb__rpsl, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                unskl__onz._filters = dnf_filters
                unskl__onz._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            lcx__asy = len(unskl__onz.files)
            unskl__onz = ParquetDataset(unskl__onz, prefix)
            pa.set_io_thread_count(xeb__nkme)
            if typing_pa_schema:
                unskl__onz.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    ilq__cof.add_attribute('num_pieces_before_filter', lcx__asy
                        )
                    ilq__cof.add_attribute('num_pieces_after_filter', len(
                        unskl__onz.pieces))
                ilq__cof.finalize()
        except Exception as jnzo__xaq:
            if isinstance(jnzo__xaq, IsADirectoryError):
                jnzo__xaq = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(jnzo__xaq, (OSError,
                FileNotFoundError)):
                jnzo__xaq = BodoError(str(jnzo__xaq) + list_of_files_error_msg)
            else:
                jnzo__xaq = BodoError(
                    f"""error from pyarrow: {type(jnzo__xaq).__name__}: {str(jnzo__xaq)}
"""
                    )
            wvyir__nmo.bcast(jnzo__xaq)
            raise jnzo__xaq
        if get_row_counts:
            scpbz__rssi = tracing.Event('bcast dataset')
        unskl__onz = wvyir__nmo.bcast(unskl__onz)
    else:
        if get_row_counts:
            scpbz__rssi = tracing.Event('bcast dataset')
        unskl__onz = wvyir__nmo.bcast(None)
        if isinstance(unskl__onz, Exception):
            hldf__iuys = unskl__onz
            raise hldf__iuys
    unskl__onz.set_fs(getfs())
    if get_row_counts:
        scpbz__rssi.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = jhh__obm = False
    if get_row_counts or jhh__obm:
        if get_row_counts and tracing.is_tracing():
            kvzfe__opdd = tracing.Event('get_row_counts')
            kvzfe__opdd.add_attribute('g_num_pieces', len(unskl__onz.pieces))
            kvzfe__opdd.add_attribute('g_expr_filters', str(expr_filters))
        hkz__sko = 0.0
        num_pieces = len(unskl__onz.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        taeka__pax = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        oqr__byiq = 0
        qbog__uqt = 0
        jgwte__tks = 0
        yjgy__ooqb = True
        if expr_filters is not None:
            import random
            random.seed(37)
            nxf__viy = random.sample(unskl__onz.pieces, k=len(unskl__onz.
                pieces))
        else:
            nxf__viy = unskl__onz.pieces
        fpaths = [aba__iznk.path for aba__iznk in nxf__viy[start:taeka__pax]]
        dwh__mkxud = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(dwh__mkxud)
        pa.set_cpu_count(dwh__mkxud)
        hldf__iuys = None
        try:
            jmevm__mlwa = ds.dataset(fpaths, filesystem=unskl__onz.
                filesystem, partitioning=unskl__onz.partitioning)
            for hfo__blzo, frag in zip(nxf__viy[start:taeka__pax],
                jmevm__mlwa.get_fragments()):
                if jhh__obm:
                    cghrh__iphr = frag.metadata.schema.to_arrow_schema()
                    wyfcv__xeqj = set(cghrh__iphr.names)
                    rpwu__ovxz = set(unskl__onz.schema.names) - set(unskl__onz
                        .partition_names)
                    if rpwu__ovxz != wyfcv__xeqj:
                        skz__omund = wyfcv__xeqj - rpwu__ovxz
                        yhtk__nzov = rpwu__ovxz - wyfcv__xeqj
                        pesp__kdkri = f'Schema in {hfo__blzo} was different.\n'
                        if skz__omund:
                            pesp__kdkri += f"""File contains column(s) {skz__omund} not found in other files in the dataset.
"""
                        if yhtk__nzov:
                            pesp__kdkri += f"""File missing column(s) {yhtk__nzov} found in other files in the dataset.
"""
                        raise BodoError(pesp__kdkri)
                    try:
                        unskl__onz.schema = unify_schemas([unskl__onz.
                            schema, cghrh__iphr])
                    except Exception as jnzo__xaq:
                        pesp__kdkri = (
                            f'Schema in {hfo__blzo} was different.\n' + str
                            (jnzo__xaq))
                        raise BodoError(pesp__kdkri)
                qrpxo__ghur = time.time()
                rihp__etk = frag.scanner(schema=jmevm__mlwa.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                hkz__sko += time.time() - qrpxo__ghur
                hfo__blzo._bodo_num_rows = rihp__etk
                oqr__byiq += rihp__etk
                qbog__uqt += frag.num_row_groups
                jgwte__tks += sum(sxm__thrb.total_byte_size for sxm__thrb in
                    frag.row_groups)
        except Exception as jnzo__xaq:
            hldf__iuys = jnzo__xaq
        if wvyir__nmo.allreduce(hldf__iuys is not None, op=MPI.LOR):
            for hldf__iuys in wvyir__nmo.allgather(hldf__iuys):
                if hldf__iuys:
                    if isinstance(fpath, list) and isinstance(hldf__iuys, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(hldf__iuys) +
                            list_of_files_error_msg)
                    raise hldf__iuys
        if jhh__obm:
            yjgy__ooqb = wvyir__nmo.allreduce(yjgy__ooqb, op=MPI.LAND)
            if not yjgy__ooqb:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            unskl__onz._bodo_total_rows = wvyir__nmo.allreduce(oqr__byiq,
                op=MPI.SUM)
            vwul__ndho = wvyir__nmo.allreduce(qbog__uqt, op=MPI.SUM)
            qxwh__dmo = wvyir__nmo.allreduce(jgwte__tks, op=MPI.SUM)
            tzr__ahdjr = np.array([aba__iznk._bodo_num_rows for aba__iznk in
                unskl__onz.pieces])
            tzr__ahdjr = wvyir__nmo.allreduce(tzr__ahdjr, op=MPI.SUM)
            for aba__iznk, nlqy__jsore in zip(unskl__onz.pieces, tzr__ahdjr):
                aba__iznk._bodo_num_rows = nlqy__jsore
            if is_parallel and bodo.get_rank(
                ) == 0 and vwul__ndho < bodo.get_size() and vwul__ndho != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({vwul__ndho}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if vwul__ndho == 0:
                dinp__pxpb = 0
            else:
                dinp__pxpb = qxwh__dmo // vwul__ndho
            if (bodo.get_rank() == 0 and qxwh__dmo >= 20 * 1048576 and 
                dinp__pxpb < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({dinp__pxpb} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                kvzfe__opdd.add_attribute('g_total_num_row_groups', vwul__ndho)
                kvzfe__opdd.add_attribute('total_scan_time', hkz__sko)
                hkhkg__valro = np.array([aba__iznk._bodo_num_rows for
                    aba__iznk in unskl__onz.pieces])
                bft__sbj = np.percentile(hkhkg__valro, [25, 50, 75])
                kvzfe__opdd.add_attribute('g_row_counts_min', hkhkg__valro.
                    min())
                kvzfe__opdd.add_attribute('g_row_counts_Q1', bft__sbj[0])
                kvzfe__opdd.add_attribute('g_row_counts_median', bft__sbj[1])
                kvzfe__opdd.add_attribute('g_row_counts_Q3', bft__sbj[2])
                kvzfe__opdd.add_attribute('g_row_counts_max', hkhkg__valro.
                    max())
                kvzfe__opdd.add_attribute('g_row_counts_mean', hkhkg__valro
                    .mean())
                kvzfe__opdd.add_attribute('g_row_counts_std', hkhkg__valro.
                    std())
                kvzfe__opdd.add_attribute('g_row_counts_sum', hkhkg__valro.
                    sum())
                kvzfe__opdd.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(unskl__onz)
    if get_row_counts:
        tvlgs__gdxks.finalize()
    if jhh__obm and is_parallel:
        if tracing.is_tracing():
            hdl__dqnde = tracing.Event('unify_schemas_across_ranks')
        hldf__iuys = None
        try:
            unskl__onz.schema = wvyir__nmo.allreduce(unskl__onz.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as jnzo__xaq:
            hldf__iuys = jnzo__xaq
        if tracing.is_tracing():
            hdl__dqnde.finalize()
        if wvyir__nmo.allreduce(hldf__iuys is not None, op=MPI.LOR):
            for hldf__iuys in wvyir__nmo.allgather(hldf__iuys):
                if hldf__iuys:
                    pesp__kdkri = (
                        f'Schema in some files were different.\n' + str(
                        hldf__iuys))
                    raise BodoError(pesp__kdkri)
    return unskl__onz


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    gpcbd__jbo = os.cpu_count()
    if gpcbd__jbo is None or gpcbd__jbo == 0:
        gpcbd__jbo = 2
    qgv__qhvrx = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), gpcbd__jbo)
    gfcx__qmmeo = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        gpcbd__jbo)
    if is_parallel and len(fpaths) > gfcx__qmmeo and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(gfcx__qmmeo)
        pa.set_cpu_count(gfcx__qmmeo)
    else:
        pa.set_io_thread_count(qgv__qhvrx)
        pa.set_cpu_count(qgv__qhvrx)
    jusko__pnng = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    qwm__quu = set(str_as_dict_cols)
    for phuti__flnu, name in enumerate(schema.names):
        if name in qwm__quu:
            rojq__kspg = schema.field(phuti__flnu)
            nbg__vng = pa.field(name, pa.dictionary(pa.int32(), rojq__kspg.
                type), rojq__kspg.nullable)
            schema = schema.remove(phuti__flnu).insert(phuti__flnu, nbg__vng)
    unskl__onz = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=jusko__pnng)
    col_names = unskl__onz.schema.names
    byl__lsep = [col_names[ipaec__hkcc] for ipaec__hkcc in selected_fields]
    fmi__wjj = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if fmi__wjj and expr_filters is None:
        rbo__amuxg = []
        tgzo__wcr = 0
        qtqb__tofx = 0
        for frag in unskl__onz.get_fragments():
            opsbs__nqrru = []
            for sxm__thrb in frag.row_groups:
                bgd__fsrtb = sxm__thrb.num_rows
                if start_offset < tgzo__wcr + bgd__fsrtb:
                    if qtqb__tofx == 0:
                        ogq__tzj = start_offset - tgzo__wcr
                        ctj__oqav = min(bgd__fsrtb - ogq__tzj, rows_to_read)
                    else:
                        ctj__oqav = min(bgd__fsrtb, rows_to_read - qtqb__tofx)
                    qtqb__tofx += ctj__oqav
                    opsbs__nqrru.append(sxm__thrb.id)
                tgzo__wcr += bgd__fsrtb
                if qtqb__tofx == rows_to_read:
                    break
            rbo__amuxg.append(frag.subset(row_group_ids=opsbs__nqrru))
            if qtqb__tofx == rows_to_read:
                break
        unskl__onz = ds.FileSystemDataset(rbo__amuxg, unskl__onz.schema,
            jusko__pnng, filesystem=unskl__onz.filesystem)
        start_offset = ogq__tzj
    sbllr__ihk = unskl__onz.scanner(columns=byl__lsep, filter=expr_filters,
        use_threads=True).to_reader()
    return unskl__onz, sbllr__ihk, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    avzn__trkx = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(avzn__trkx) == 0:
        pq_dataset._category_info = {}
        return
    wvyir__nmo = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            aqepz__axt = pq_dataset.pieces[0].frag.head(100, columns=avzn__trkx
                )
            pkj__pgy = {c: tuple(aqepz__axt.column(c).chunk(0).dictionary.
                to_pylist()) for c in avzn__trkx}
            del aqepz__axt
        except Exception as jnzo__xaq:
            wvyir__nmo.bcast(jnzo__xaq)
            raise jnzo__xaq
        wvyir__nmo.bcast(pkj__pgy)
    else:
        pkj__pgy = wvyir__nmo.bcast(None)
        if isinstance(pkj__pgy, Exception):
            hldf__iuys = pkj__pgy
            raise hldf__iuys
    pq_dataset._category_info = pkj__pgy


def get_pandas_metadata(schema, num_pieces):
    sab__vlc = None
    armwb__vgzle = defaultdict(lambda : None)
    ccln__hij = b'pandas'
    if schema.metadata is not None and ccln__hij in schema.metadata:
        import json
        wkiez__gujtu = json.loads(schema.metadata[ccln__hij].decode('utf8'))
        ijmfy__ygqv = len(wkiez__gujtu['index_columns'])
        if ijmfy__ygqv > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        sab__vlc = wkiez__gujtu['index_columns'][0] if ijmfy__ygqv else None
        if not isinstance(sab__vlc, str) and not isinstance(sab__vlc, dict):
            sab__vlc = None
        for wqu__trhvz in wkiez__gujtu['columns']:
            pgpgh__tkrh = wqu__trhvz['name']
            if wqu__trhvz['pandas_type'].startswith('int'
                ) and pgpgh__tkrh is not None:
                if wqu__trhvz['numpy_type'].startswith('Int'):
                    armwb__vgzle[pgpgh__tkrh] = True
                else:
                    armwb__vgzle[pgpgh__tkrh] = False
    return sab__vlc, armwb__vgzle


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for pgpgh__tkrh in pa_schema.names:
        wgqg__isz = pa_schema.field(pgpgh__tkrh)
        if wgqg__isz.type in (pa.string(), pa.large_string()):
            str_columns.append(pgpgh__tkrh)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    wvyir__nmo = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        nxf__viy = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        nxf__viy = pq_dataset.pieces
    jrfd__fjecm = np.zeros(len(str_columns), dtype=np.int64)
    ygg__mig = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(nxf__viy):
        hfo__blzo = nxf__viy[bodo.get_rank()]
        try:
            metadata = hfo__blzo.metadata
            for phuti__flnu in range(hfo__blzo.num_row_groups):
                for wuit__fjglb, pgpgh__tkrh in enumerate(str_columns):
                    llny__ylsr = pa_schema.get_field_index(pgpgh__tkrh)
                    jrfd__fjecm[wuit__fjglb] += metadata.row_group(phuti__flnu
                        ).column(llny__ylsr).total_uncompressed_size
            byq__pqul = metadata.num_rows
        except Exception as jnzo__xaq:
            if isinstance(jnzo__xaq, (OSError, FileNotFoundError)):
                byq__pqul = 0
            else:
                raise
    else:
        byq__pqul = 0
    store__zvqh = wvyir__nmo.allreduce(byq__pqul, op=MPI.SUM)
    if store__zvqh == 0:
        return set()
    wvyir__nmo.Allreduce(jrfd__fjecm, ygg__mig, op=MPI.SUM)
    rca__zxsw = ygg__mig / store__zvqh
    oigt__sdb = set()
    for phuti__flnu, ajmge__ypgy in enumerate(rca__zxsw):
        if ajmge__ypgy < READ_STR_AS_DICT_THRESHOLD:
            pgpgh__tkrh = str_columns[phuti__flnu][0]
            oigt__sdb.add(pgpgh__tkrh)
    return oigt__sdb


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    uydt__ukxhb = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    llhm__ozv = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    dopek__rhh = read_as_dict_cols - llhm__ozv
    if len(dopek__rhh) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {dopek__rhh}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(llhm__ozv)
    llhm__ozv = llhm__ozv - read_as_dict_cols
    str_columns = [jchoc__zpbi for jchoc__zpbi in str_columns if 
        jchoc__zpbi in llhm__ozv]
    oigt__sdb: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    oigt__sdb.update(read_as_dict_cols)
    col_names = pa_schema.names
    sab__vlc, armwb__vgzle = get_pandas_metadata(pa_schema, num_pieces)
    yzqw__wsj = []
    cawhy__xntbo = []
    ademw__usir = []
    for phuti__flnu, c in enumerate(col_names):
        if c in partition_names:
            continue
        wgqg__isz = pa_schema.field(c)
        ttiv__iigg, vbmli__zsknx = _get_numba_typ_from_pa_typ(wgqg__isz, c ==
            sab__vlc, armwb__vgzle[c], pq_dataset._category_info,
            str_as_dict=c in oigt__sdb)
        yzqw__wsj.append(ttiv__iigg)
        cawhy__xntbo.append(vbmli__zsknx)
        ademw__usir.append(wgqg__isz.type)
    if partition_names:
        yzqw__wsj += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[phuti__flnu]) for phuti__flnu in
            range(len(partition_names))]
        cawhy__xntbo.extend([True] * len(partition_names))
        ademw__usir.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        yzqw__wsj += [dict_str_arr_type]
        cawhy__xntbo.append(True)
        ademw__usir.append(None)
    shoh__rdac = {c: phuti__flnu for phuti__flnu, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in shoh__rdac:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if sab__vlc and not isinstance(sab__vlc, dict
        ) and sab__vlc not in selected_columns:
        selected_columns.append(sab__vlc)
    col_names = selected_columns
    col_indices = []
    uydt__ukxhb = []
    sjrbg__axbzr = []
    nqs__lcnf = []
    for phuti__flnu, c in enumerate(col_names):
        kly__wpi = shoh__rdac[c]
        col_indices.append(kly__wpi)
        uydt__ukxhb.append(yzqw__wsj[kly__wpi])
        if not cawhy__xntbo[kly__wpi]:
            sjrbg__axbzr.append(phuti__flnu)
            nqs__lcnf.append(ademw__usir[kly__wpi])
    return (col_names, uydt__ukxhb, sab__vlc, col_indices, partition_names,
        sjrbg__axbzr, nqs__lcnf)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    uaopm__pbd = dictionary.to_pandas()
    rbrat__bca = bodo.typeof(uaopm__pbd).dtype
    if isinstance(rbrat__bca, types.Integer):
        avj__tlcu = PDCategoricalDtype(tuple(uaopm__pbd), rbrat__bca, False,
            int_type=rbrat__bca)
    else:
        avj__tlcu = PDCategoricalDtype(tuple(uaopm__pbd), rbrat__bca, False)
    return CategoricalArrayType(avj__tlcu)


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
        cfs__hjh = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        cytv__uvd = cgutils.get_or_insert_function(builder.module, cfs__hjh,
            name='pq_write')
        nkscn__hrgqe = builder.call(cytv__uvd, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return nkscn__hrgqe
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
        cfs__hjh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        cytv__uvd = cgutils.get_or_insert_function(builder.module, cfs__hjh,
            name='pq_write_partitioned')
        builder.call(cytv__uvd, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
