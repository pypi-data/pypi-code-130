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
        except OSError as mnjo__dkic:
            if 'non-file path' in str(mnjo__dkic):
                raise FileNotFoundError(str(mnjo__dkic))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        ykevo__xdcqf = lhs.scope
        nqn__eot = lhs.loc
        fne__ycl = None
        if lhs.name in self.locals:
            fne__ycl = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        gvthb__lzzli = {}
        if lhs.name + ':convert' in self.locals:
            gvthb__lzzli = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if fne__ycl is None:
            sagqt__yrdd = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            akl__dnqw = get_const_value(file_name, self.func_ir,
                sagqt__yrdd, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            lsxxg__kyxxh = False
            owzza__aco = guard(get_definition, self.func_ir, file_name)
            if isinstance(owzza__aco, ir.Arg):
                typ = self.args[owzza__aco.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, kcwz__yqa, jem__iivfw, col_indices,
                        partition_names, uro__sixa, nhkch__hsr) = typ.schema
                    lsxxg__kyxxh = True
            if not lsxxg__kyxxh:
                (col_names, kcwz__yqa, jem__iivfw, col_indices,
                    partition_names, uro__sixa, nhkch__hsr) = (
                    parquet_file_schema(akl__dnqw, columns, storage_options
                    =storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            paux__gim = list(fne__ycl.keys())
            skvq__zdmqm = {c: ryoe__lzial for ryoe__lzial, c in enumerate(
                paux__gim)}
            nnlhk__jcrp = [rin__viguj for rin__viguj in fne__ycl.values()]
            jem__iivfw = 'index' if 'index' in skvq__zdmqm else None
            if columns is None:
                selected_columns = paux__gim
            else:
                selected_columns = columns
            col_indices = [skvq__zdmqm[c] for c in selected_columns]
            kcwz__yqa = [nnlhk__jcrp[skvq__zdmqm[c]] for c in selected_columns]
            col_names = selected_columns
            jem__iivfw = jem__iivfw if jem__iivfw in col_names else None
            partition_names = []
            uro__sixa = []
            nhkch__hsr = []
        zay__oovj = None if isinstance(jem__iivfw, dict
            ) or jem__iivfw is None else jem__iivfw
        index_column_index = None
        index_column_type = types.none
        if zay__oovj:
            kptrv__qfbi = col_names.index(zay__oovj)
            index_column_index = col_indices.pop(kptrv__qfbi)
            index_column_type = kcwz__yqa.pop(kptrv__qfbi)
            col_names.pop(kptrv__qfbi)
        for ryoe__lzial, c in enumerate(col_names):
            if c in gvthb__lzzli:
                kcwz__yqa[ryoe__lzial] = gvthb__lzzli[c]
        pir__yqo = [ir.Var(ykevo__xdcqf, mk_unique_var('pq_table'),
            nqn__eot), ir.Var(ykevo__xdcqf, mk_unique_var('pq_index'),
            nqn__eot)]
        idic__woh = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, kcwz__yqa, pir__yqo, nqn__eot,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, uro__sixa, nhkch__hsr)]
        return (col_names, pir__yqo, jem__iivfw, idic__woh, kcwz__yqa,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    pmkxw__ithn = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    ssp__hxklb, scs__zxrjd = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(ssp__hxklb.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, ssp__hxklb, scs__zxrjd, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    wbzz__bpe = ', '.join(f'out{ryoe__lzial}' for ryoe__lzial in range(
        pmkxw__ithn))
    ygwt__oso = f'def pq_impl(fname, {extra_args}):\n'
    ygwt__oso += (
        f'    (total_rows, {wbzz__bpe},) = _pq_reader_py(fname, {extra_args})\n'
        )
    odo__tejmp = {}
    exec(ygwt__oso, {}, odo__tejmp)
    nho__evmxa = odo__tejmp['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        zqsgb__raghs = pq_node.loc.strformat()
        eup__zfkq = []
        wrntf__ojym = []
        for ryoe__lzial in pq_node.out_used_cols:
            lnqbn__szry = pq_node.df_colnames[ryoe__lzial]
            eup__zfkq.append(lnqbn__szry)
            if isinstance(pq_node.out_types[ryoe__lzial], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                wrntf__ojym.append(lnqbn__szry)
        ahv__ixlt = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', ahv__ixlt,
            zqsgb__raghs, eup__zfkq)
        if wrntf__ojym:
            kql__akatl = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', kql__akatl,
                zqsgb__raghs, wrntf__ojym)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        ofjs__sni = set(pq_node.out_used_cols)
        korzk__xpp = set(pq_node.unsupported_columns)
        pvck__gin = ofjs__sni & korzk__xpp
        if pvck__gin:
            nmzps__uxnep = sorted(pvck__gin)
            qjv__vear = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            jpm__gbirt = 0
            for rplw__melp in nmzps__uxnep:
                while pq_node.unsupported_columns[jpm__gbirt] != rplw__melp:
                    jpm__gbirt += 1
                qjv__vear.append(
                    f"Column '{pq_node.df_colnames[rplw__melp]}' with unsupported arrow type {pq_node.unsupported_arrow_types[jpm__gbirt]}"
                    )
                jpm__gbirt += 1
            lme__qxpu = '\n'.join(qjv__vear)
            raise BodoError(lme__qxpu, loc=pq_node.loc)
    ighbp__xfhw = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col, not pq_node.is_live_table)
    erjb__bhao = typemap[pq_node.file_name.name]
    yfpzr__epnqt = (erjb__bhao,) + tuple(typemap[qbh__lobi.name] for
        qbh__lobi in scs__zxrjd)
    jzatt__ukhi = compile_to_numba_ir(nho__evmxa, {'_pq_reader_py':
        ighbp__xfhw}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        yfpzr__epnqt, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(jzatt__ukhi, [pq_node.file_name] + scs__zxrjd)
    idic__woh = jzatt__ukhi.body[:-3]
    if meta_head_only_info:
        idic__woh[-3].target = meta_head_only_info[1]
    idic__woh[-2].target = pq_node.out_vars[0]
    idic__woh[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        is_live_table
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        idic__woh.pop(-1)
    elif not pq_node.is_live_table:
        idic__woh.pop(-2)
    return idic__woh


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    nuu__qaulm = get_overload_const_str(dnf_filter_str)
    vbds__lud = get_overload_const_str(expr_filter_str)
    nlvc__imr = ', '.join(f'f{ryoe__lzial}' for ryoe__lzial in range(len(
        var_tup)))
    ygwt__oso = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        ygwt__oso += f'  {nlvc__imr}, = var_tup\n'
    ygwt__oso += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    ygwt__oso += f'    dnf_filters_py = {nuu__qaulm}\n'
    ygwt__oso += f'    expr_filters_py = {vbds__lud}\n'
    ygwt__oso += '  return (dnf_filters_py, expr_filters_py)\n'
    odo__tejmp = {}
    exec(ygwt__oso, globals(), odo__tejmp)
    return odo__tejmp['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col, is_dead_table):
    uxlk__tzkp = next_label()
    lwbw__jxnbd = ',' if extra_args else ''
    ygwt__oso = f'def pq_reader_py(fname,{extra_args}):\n'
    ygwt__oso += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    ygwt__oso += f"    ev.add_attribute('g_fname', fname)\n"
    ygwt__oso += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{lwbw__jxnbd}))
"""
    ygwt__oso += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    ygwt__oso += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    cwof__dvjs = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    pwzye__whvw = {c: ryoe__lzial for ryoe__lzial, c in enumerate(col_indices)}
    vyhx__dgd = {c: ryoe__lzial for ryoe__lzial, c in enumerate(cwof__dvjs)}
    jmom__csg = []
    nqmdo__ihwxi = set()
    shvj__acbtw = partition_names + [input_file_name_col]
    for ryoe__lzial in out_used_cols:
        if cwof__dvjs[ryoe__lzial] not in shvj__acbtw:
            jmom__csg.append(col_indices[ryoe__lzial])
        elif not input_file_name_col or cwof__dvjs[ryoe__lzial
            ] != input_file_name_col:
            nqmdo__ihwxi.add(col_indices[ryoe__lzial])
    if index_column_index is not None:
        jmom__csg.append(index_column_index)
    jmom__csg = sorted(jmom__csg)
    mrc__zcr = {c: ryoe__lzial for ryoe__lzial, c in enumerate(jmom__csg)}
    eeslc__xaqz = [(int(is_nullable(out_types[pwzye__whvw[xgok__kxch]])) if
        xgok__kxch != index_column_index else int(is_nullable(
        index_column_type))) for xgok__kxch in jmom__csg]
    str_as_dict_cols = []
    for xgok__kxch in jmom__csg:
        if xgok__kxch == index_column_index:
            rin__viguj = index_column_type
        else:
            rin__viguj = out_types[pwzye__whvw[xgok__kxch]]
        if rin__viguj == dict_str_arr_type:
            str_as_dict_cols.append(xgok__kxch)
    pyxgj__zmj = []
    abk__ugivp = {}
    brf__wduw = []
    zhlha__tjtag = []
    for ryoe__lzial, tzy__gtpd in enumerate(partition_names):
        try:
            pvs__babax = vyhx__dgd[tzy__gtpd]
            if col_indices[pvs__babax] not in nqmdo__ihwxi:
                continue
        except (KeyError, ValueError) as ujm__qpu:
            continue
        abk__ugivp[tzy__gtpd] = len(pyxgj__zmj)
        pyxgj__zmj.append(tzy__gtpd)
        brf__wduw.append(ryoe__lzial)
        krfl__xwxnv = out_types[pvs__babax].dtype
        fscca__sgk = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            krfl__xwxnv)
        zhlha__tjtag.append(numba_to_c_type(fscca__sgk))
    ygwt__oso += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    ygwt__oso += f'    out_table = pq_read(\n'
    ygwt__oso += f'        fname_py, {is_parallel},\n'
    ygwt__oso += f'        dnf_filters, expr_filters,\n'
    ygwt__oso += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{uxlk__tzkp}.ctypes,
"""
    ygwt__oso += f'        {len(jmom__csg)},\n'
    ygwt__oso += f'        nullable_cols_arr_{uxlk__tzkp}.ctypes,\n'
    if len(brf__wduw) > 0:
        ygwt__oso += f'        np.array({brf__wduw}, dtype=np.int32).ctypes,\n'
        ygwt__oso += (
            f'        np.array({zhlha__tjtag}, dtype=np.int32).ctypes,\n')
        ygwt__oso += f'        {len(brf__wduw)},\n'
    else:
        ygwt__oso += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        ygwt__oso += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        ygwt__oso += f'        0, 0,\n'
    ygwt__oso += f'        total_rows_np.ctypes,\n'
    ygwt__oso += f'        {input_file_name_col is not None},\n'
    ygwt__oso += f'    )\n'
    ygwt__oso += f'    check_and_propagate_cpp_exception()\n'
    ygwt__oso += f'    total_rows = total_rows_np[0]\n'
    if is_parallel:
        ygwt__oso += f"""    local_rows = get_node_portion(total_rows, bodo.get_size(), bodo.get_rank())
"""
    else:
        ygwt__oso += f'    local_rows = total_rows\n'
    lxi__acna = index_column_type
    vwd__qucx = TableType(tuple(out_types))
    if is_dead_table:
        vwd__qucx = types.none
    if is_dead_table:
        zrmkd__sbgxc = None
    else:
        zrmkd__sbgxc = []
        ldpwy__ghqpr = 0
        vfy__vhx = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for ryoe__lzial, rplw__melp in enumerate(col_indices):
            if ldpwy__ghqpr < len(out_used_cols
                ) and ryoe__lzial == out_used_cols[ldpwy__ghqpr]:
                xjgv__fzhz = col_indices[ryoe__lzial]
                if vfy__vhx and xjgv__fzhz == vfy__vhx:
                    zrmkd__sbgxc.append(len(jmom__csg) + len(pyxgj__zmj))
                elif xjgv__fzhz in nqmdo__ihwxi:
                    ulkg__bjg = cwof__dvjs[ryoe__lzial]
                    zrmkd__sbgxc.append(len(jmom__csg) + abk__ugivp[ulkg__bjg])
                else:
                    zrmkd__sbgxc.append(mrc__zcr[rplw__melp])
                ldpwy__ghqpr += 1
            else:
                zrmkd__sbgxc.append(-1)
        zrmkd__sbgxc = np.array(zrmkd__sbgxc, dtype=np.int64)
    if is_dead_table:
        ygwt__oso += '    T = None\n'
    else:
        ygwt__oso += f"""    T = cpp_table_to_py_table(out_table, table_idx_{uxlk__tzkp}, py_table_type_{uxlk__tzkp})
"""
        ygwt__oso += f'    T = set_table_len(T, local_rows)\n'
    if index_column_index is None:
        ygwt__oso += '    index_arr = None\n'
    else:
        oib__bvch = mrc__zcr[index_column_index]
        ygwt__oso += f"""    index_arr = info_to_array(info_from_table(out_table, {oib__bvch}), index_arr_type)
"""
    ygwt__oso += f'    delete_table(out_table)\n'
    ygwt__oso += f'    ev.finalize()\n'
    ygwt__oso += f'    return (total_rows, T, index_arr)\n'
    odo__tejmp = {}
    zbte__xnyrf = {f'py_table_type_{uxlk__tzkp}': vwd__qucx,
        f'table_idx_{uxlk__tzkp}': zrmkd__sbgxc,
        f'selected_cols_arr_{uxlk__tzkp}': np.array(jmom__csg, np.int32),
        f'nullable_cols_arr_{uxlk__tzkp}': np.array(eeslc__xaqz, np.int32),
        'index_arr_type': lxi__acna, 'cpp_table_to_py_table':
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
    exec(ygwt__oso, zbte__xnyrf, odo__tejmp)
    ighbp__xfhw = odo__tejmp['pq_reader_py']
    mpkiy__idso = numba.njit(ighbp__xfhw, no_cpython_wrapper=True)
    return mpkiy__idso


def unify_schemas(schemas):
    yhxl__cxn = []
    for schema in schemas:
        for ryoe__lzial in range(len(schema)):
            ydvp__aake = schema.field(ryoe__lzial)
            if ydvp__aake.type == pa.large_string():
                schema = schema.set(ryoe__lzial, ydvp__aake.with_type(pa.
                    string()))
            elif ydvp__aake.type == pa.large_binary():
                schema = schema.set(ryoe__lzial, ydvp__aake.with_type(pa.
                    binary()))
            elif isinstance(ydvp__aake.type, (pa.ListType, pa.LargeListType)
                ) and ydvp__aake.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(ryoe__lzial, ydvp__aake.with_type(pa.
                    list_(pa.field(ydvp__aake.type.value_field.name, pa.
                    string()))))
            elif isinstance(ydvp__aake.type, pa.LargeListType):
                schema = schema.set(ryoe__lzial, ydvp__aake.with_type(pa.
                    list_(pa.field(ydvp__aake.type.value_field.name,
                    ydvp__aake.type.value_type))))
        yhxl__cxn.append(schema)
    return pa.unify_schemas(yhxl__cxn)


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
        for ryoe__lzial in range(len(self.schema)):
            ydvp__aake = self.schema.field(ryoe__lzial)
            if ydvp__aake.type == pa.large_string():
                self.schema = self.schema.set(ryoe__lzial, ydvp__aake.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for ywtd__ovc in self.pieces:
            ywtd__ovc.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            orztv__fjtz = {ywtd__ovc: self.partitioning_dictionaries[
                ryoe__lzial] for ryoe__lzial, ywtd__ovc in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, orztv__fjtz)


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
            self.partition_keys = [(tzy__gtpd, partitioning.dictionaries[
                ryoe__lzial].index(self.partition_keys[tzy__gtpd]).as_py()) for
                ryoe__lzial, tzy__gtpd in enumerate(partition_names)]

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
        urgs__yvra = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    stmh__ewff = MPI.COMM_WORLD
    if isinstance(fpath, list):
        edrd__yit = urlparse(fpath[0])
        protocol = edrd__yit.scheme
        dnqfz__bzpu = edrd__yit.netloc
        for ryoe__lzial in range(len(fpath)):
            ydvp__aake = fpath[ryoe__lzial]
            bezxd__iqss = urlparse(ydvp__aake)
            if bezxd__iqss.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if bezxd__iqss.netloc != dnqfz__bzpu:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[ryoe__lzial] = ydvp__aake.rstrip('/')
    else:
        edrd__yit = urlparse(fpath)
        protocol = edrd__yit.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as ujm__qpu:
            ksx__skbi = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(ksx__skbi)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as ujm__qpu:
            ksx__skbi = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            ntbi__xvzaq = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(ntbi__xvzaq)))
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
            oor__zyba = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(oor__zyba) == 0:
            raise BodoError('No files found matching glob pattern')
        return oor__zyba
    bhsil__zkuyn = False
    if get_row_counts:
        xad__npn = getfs(parallel=True)
        bhsil__zkuyn = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        pqf__igtpo = 1
        tlym__kim = os.cpu_count()
        if tlym__kim is not None and tlym__kim > 1:
            pqf__igtpo = tlym__kim // 2
        try:
            if get_row_counts:
                qqg__wiymu = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    qqg__wiymu.add_attribute('g_dnf_filter', str(dnf_filters))
            ggt__ikya = pa.io_thread_count()
            pa.set_io_thread_count(pqf__igtpo)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{edrd__yit.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    hykqj__xxzs = [ydvp__aake[len(prefix):] for ydvp__aake in
                        fpath]
                else:
                    hykqj__xxzs = fpath[len(prefix):]
            else:
                hykqj__xxzs = fpath
            if isinstance(hykqj__xxzs, list):
                ggylx__uob = []
                for ywtd__ovc in hykqj__xxzs:
                    if has_magic(ywtd__ovc):
                        ggylx__uob += glob(protocol, getfs(), ywtd__ovc)
                    else:
                        ggylx__uob.append(ywtd__ovc)
                hykqj__xxzs = ggylx__uob
            elif has_magic(hykqj__xxzs):
                hykqj__xxzs = glob(protocol, getfs(), hykqj__xxzs)
            knrl__fsaji = pq.ParquetDataset(hykqj__xxzs, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                knrl__fsaji._filters = dnf_filters
                knrl__fsaji._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            dzx__pptmt = len(knrl__fsaji.files)
            knrl__fsaji = ParquetDataset(knrl__fsaji, prefix)
            pa.set_io_thread_count(ggt__ikya)
            if typing_pa_schema:
                knrl__fsaji.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    qqg__wiymu.add_attribute('num_pieces_before_filter',
                        dzx__pptmt)
                    qqg__wiymu.add_attribute('num_pieces_after_filter', len
                        (knrl__fsaji.pieces))
                qqg__wiymu.finalize()
        except Exception as mnjo__dkic:
            if isinstance(mnjo__dkic, IsADirectoryError):
                mnjo__dkic = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(mnjo__dkic, (
                OSError, FileNotFoundError)):
                mnjo__dkic = BodoError(str(mnjo__dkic) +
                    list_of_files_error_msg)
            else:
                mnjo__dkic = BodoError(
                    f"""error from pyarrow: {type(mnjo__dkic).__name__}: {str(mnjo__dkic)}
"""
                    )
            stmh__ewff.bcast(mnjo__dkic)
            raise mnjo__dkic
        if get_row_counts:
            vaiw__nie = tracing.Event('bcast dataset')
        knrl__fsaji = stmh__ewff.bcast(knrl__fsaji)
    else:
        if get_row_counts:
            vaiw__nie = tracing.Event('bcast dataset')
        knrl__fsaji = stmh__ewff.bcast(None)
        if isinstance(knrl__fsaji, Exception):
            gnb__vatxi = knrl__fsaji
            raise gnb__vatxi
    knrl__fsaji.set_fs(getfs())
    if get_row_counts:
        vaiw__nie.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = bhsil__zkuyn = False
    if get_row_counts or bhsil__zkuyn:
        if get_row_counts and tracing.is_tracing():
            qbs__utci = tracing.Event('get_row_counts')
            qbs__utci.add_attribute('g_num_pieces', len(knrl__fsaji.pieces))
            qbs__utci.add_attribute('g_expr_filters', str(expr_filters))
        iadg__acyaq = 0.0
        num_pieces = len(knrl__fsaji.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        rty__pok = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        lpnop__bixtf = 0
        xmuqw__dsf = 0
        vbat__aszl = 0
        xdr__eoj = True
        if expr_filters is not None:
            import random
            random.seed(37)
            vtuu__afabs = random.sample(knrl__fsaji.pieces, k=len(
                knrl__fsaji.pieces))
        else:
            vtuu__afabs = knrl__fsaji.pieces
        fpaths = [ywtd__ovc.path for ywtd__ovc in vtuu__afabs[start:rty__pok]]
        pqf__igtpo = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(pqf__igtpo)
        pa.set_cpu_count(pqf__igtpo)
        gnb__vatxi = None
        try:
            yxj__lmp = ds.dataset(fpaths, filesystem=knrl__fsaji.filesystem,
                partitioning=knrl__fsaji.partitioning)
            for nfwo__nym, frag in zip(vtuu__afabs[start:rty__pok],
                yxj__lmp.get_fragments()):
                if bhsil__zkuyn:
                    jwyo__ilgky = frag.metadata.schema.to_arrow_schema()
                    rxros__cro = set(jwyo__ilgky.names)
                    tdz__vueb = set(knrl__fsaji.schema.names) - set(knrl__fsaji
                        .partition_names)
                    if tdz__vueb != rxros__cro:
                        bpm__ruals = rxros__cro - tdz__vueb
                        nbs__dsofn = tdz__vueb - rxros__cro
                        sagqt__yrdd = f'Schema in {nfwo__nym} was different.\n'
                        if bpm__ruals:
                            sagqt__yrdd += f"""File contains column(s) {bpm__ruals} not found in other files in the dataset.
"""
                        if nbs__dsofn:
                            sagqt__yrdd += f"""File missing column(s) {nbs__dsofn} found in other files in the dataset.
"""
                        raise BodoError(sagqt__yrdd)
                    try:
                        knrl__fsaji.schema = unify_schemas([knrl__fsaji.
                            schema, jwyo__ilgky])
                    except Exception as mnjo__dkic:
                        sagqt__yrdd = (
                            f'Schema in {nfwo__nym} was different.\n' + str
                            (mnjo__dkic))
                        raise BodoError(sagqt__yrdd)
                icu__lwm = time.time()
                vqxm__yas = frag.scanner(schema=yxj__lmp.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                iadg__acyaq += time.time() - icu__lwm
                nfwo__nym._bodo_num_rows = vqxm__yas
                lpnop__bixtf += vqxm__yas
                xmuqw__dsf += frag.num_row_groups
                vbat__aszl += sum(apie__islrz.total_byte_size for
                    apie__islrz in frag.row_groups)
        except Exception as mnjo__dkic:
            gnb__vatxi = mnjo__dkic
        if stmh__ewff.allreduce(gnb__vatxi is not None, op=MPI.LOR):
            for gnb__vatxi in stmh__ewff.allgather(gnb__vatxi):
                if gnb__vatxi:
                    if isinstance(fpath, list) and isinstance(gnb__vatxi, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(gnb__vatxi) +
                            list_of_files_error_msg)
                    raise gnb__vatxi
        if bhsil__zkuyn:
            xdr__eoj = stmh__ewff.allreduce(xdr__eoj, op=MPI.LAND)
            if not xdr__eoj:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            knrl__fsaji._bodo_total_rows = stmh__ewff.allreduce(lpnop__bixtf,
                op=MPI.SUM)
            tmjv__vjsfp = stmh__ewff.allreduce(xmuqw__dsf, op=MPI.SUM)
            ilqo__waz = stmh__ewff.allreduce(vbat__aszl, op=MPI.SUM)
            dtcvb__zancw = np.array([ywtd__ovc._bodo_num_rows for ywtd__ovc in
                knrl__fsaji.pieces])
            dtcvb__zancw = stmh__ewff.allreduce(dtcvb__zancw, op=MPI.SUM)
            for ywtd__ovc, yoe__dnrs in zip(knrl__fsaji.pieces, dtcvb__zancw):
                ywtd__ovc._bodo_num_rows = yoe__dnrs
            if is_parallel and bodo.get_rank(
                ) == 0 and tmjv__vjsfp < bodo.get_size() and tmjv__vjsfp != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({tmjv__vjsfp}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if tmjv__vjsfp == 0:
                fcb__ustd = 0
            else:
                fcb__ustd = ilqo__waz // tmjv__vjsfp
            if (bodo.get_rank() == 0 and ilqo__waz >= 20 * 1048576 and 
                fcb__ustd < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({fcb__ustd} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                qbs__utci.add_attribute('g_total_num_row_groups', tmjv__vjsfp)
                qbs__utci.add_attribute('total_scan_time', iadg__acyaq)
                sjz__kld = np.array([ywtd__ovc._bodo_num_rows for ywtd__ovc in
                    knrl__fsaji.pieces])
                aby__teqx = np.percentile(sjz__kld, [25, 50, 75])
                qbs__utci.add_attribute('g_row_counts_min', sjz__kld.min())
                qbs__utci.add_attribute('g_row_counts_Q1', aby__teqx[0])
                qbs__utci.add_attribute('g_row_counts_median', aby__teqx[1])
                qbs__utci.add_attribute('g_row_counts_Q3', aby__teqx[2])
                qbs__utci.add_attribute('g_row_counts_max', sjz__kld.max())
                qbs__utci.add_attribute('g_row_counts_mean', sjz__kld.mean())
                qbs__utci.add_attribute('g_row_counts_std', sjz__kld.std())
                qbs__utci.add_attribute('g_row_counts_sum', sjz__kld.sum())
                qbs__utci.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(knrl__fsaji)
    if get_row_counts:
        urgs__yvra.finalize()
    if bhsil__zkuyn and is_parallel:
        if tracing.is_tracing():
            fnl__umib = tracing.Event('unify_schemas_across_ranks')
        gnb__vatxi = None
        try:
            knrl__fsaji.schema = stmh__ewff.allreduce(knrl__fsaji.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as mnjo__dkic:
            gnb__vatxi = mnjo__dkic
        if tracing.is_tracing():
            fnl__umib.finalize()
        if stmh__ewff.allreduce(gnb__vatxi is not None, op=MPI.LOR):
            for gnb__vatxi in stmh__ewff.allgather(gnb__vatxi):
                if gnb__vatxi:
                    sagqt__yrdd = (
                        f'Schema in some files were different.\n' + str(
                        gnb__vatxi))
                    raise BodoError(sagqt__yrdd)
    return knrl__fsaji


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    tlym__kim = os.cpu_count()
    if tlym__kim is None or tlym__kim == 0:
        tlym__kim = 2
    zjg__uvv = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), tlym__kim)
    yszes__amuj = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), tlym__kim
        )
    if is_parallel and len(fpaths) > yszes__amuj and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(yszes__amuj)
        pa.set_cpu_count(yszes__amuj)
    else:
        pa.set_io_thread_count(zjg__uvv)
        pa.set_cpu_count(zjg__uvv)
    roi__pnjds = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    pmru__oltv = set(str_as_dict_cols)
    for ryoe__lzial, name in enumerate(schema.names):
        if name in pmru__oltv:
            hxg__exhyy = schema.field(ryoe__lzial)
            brznr__zgca = pa.field(name, pa.dictionary(pa.int32(),
                hxg__exhyy.type), hxg__exhyy.nullable)
            schema = schema.remove(ryoe__lzial).insert(ryoe__lzial, brznr__zgca
                )
    knrl__fsaji = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=roi__pnjds)
    col_names = knrl__fsaji.schema.names
    wxwww__lng = [col_names[amtcg__vah] for amtcg__vah in selected_fields]
    dpmuv__pgao = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if dpmuv__pgao and expr_filters is None:
        dhpy__nayww = []
        vjgdx__kwci = 0
        oce__pps = 0
        for frag in knrl__fsaji.get_fragments():
            dmrc__eacj = []
            for apie__islrz in frag.row_groups:
                vnakp__usu = apie__islrz.num_rows
                if start_offset < vjgdx__kwci + vnakp__usu:
                    if oce__pps == 0:
                        pxq__ybh = start_offset - vjgdx__kwci
                        seu__osfy = min(vnakp__usu - pxq__ybh, rows_to_read)
                    else:
                        seu__osfy = min(vnakp__usu, rows_to_read - oce__pps)
                    oce__pps += seu__osfy
                    dmrc__eacj.append(apie__islrz.id)
                vjgdx__kwci += vnakp__usu
                if oce__pps == rows_to_read:
                    break
            dhpy__nayww.append(frag.subset(row_group_ids=dmrc__eacj))
            if oce__pps == rows_to_read:
                break
        knrl__fsaji = ds.FileSystemDataset(dhpy__nayww, knrl__fsaji.schema,
            roi__pnjds, filesystem=knrl__fsaji.filesystem)
        start_offset = pxq__ybh
    bsd__nfhpm = knrl__fsaji.scanner(columns=wxwww__lng, filter=
        expr_filters, use_threads=True).to_reader()
    return knrl__fsaji, bsd__nfhpm, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    sjiae__ihzkl = [c for c in pa_schema.names if isinstance(pa_schema.
        field(c).type, pa.DictionaryType) and c not in pq_dataset.
        partition_names]
    if len(sjiae__ihzkl) == 0:
        pq_dataset._category_info = {}
        return
    stmh__ewff = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            ima__qegnv = pq_dataset.pieces[0].frag.head(100, columns=
                sjiae__ihzkl)
            msgm__tifk = {c: tuple(ima__qegnv.column(c).chunk(0).dictionary
                .to_pylist()) for c in sjiae__ihzkl}
            del ima__qegnv
        except Exception as mnjo__dkic:
            stmh__ewff.bcast(mnjo__dkic)
            raise mnjo__dkic
        stmh__ewff.bcast(msgm__tifk)
    else:
        msgm__tifk = stmh__ewff.bcast(None)
        if isinstance(msgm__tifk, Exception):
            gnb__vatxi = msgm__tifk
            raise gnb__vatxi
    pq_dataset._category_info = msgm__tifk


def get_pandas_metadata(schema, num_pieces):
    jem__iivfw = None
    avyt__pmee = defaultdict(lambda : None)
    bkim__aeewv = b'pandas'
    if schema.metadata is not None and bkim__aeewv in schema.metadata:
        import json
        czrwg__txru = json.loads(schema.metadata[bkim__aeewv].decode('utf8'))
        xjn__lcuea = len(czrwg__txru['index_columns'])
        if xjn__lcuea > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        jem__iivfw = czrwg__txru['index_columns'][0] if xjn__lcuea else None
        if not isinstance(jem__iivfw, str) and not isinstance(jem__iivfw, dict
            ):
            jem__iivfw = None
        for bks__fddl in czrwg__txru['columns']:
            hqes__zjduk = bks__fddl['name']
            if bks__fddl['pandas_type'].startswith('int'
                ) and hqes__zjduk is not None:
                if bks__fddl['numpy_type'].startswith('Int'):
                    avyt__pmee[hqes__zjduk] = True
                else:
                    avyt__pmee[hqes__zjduk] = False
    return jem__iivfw, avyt__pmee


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for hqes__zjduk in pa_schema.names:
        idejv__plv = pa_schema.field(hqes__zjduk)
        if idejv__plv.type in (pa.string(), pa.large_string()):
            str_columns.append(hqes__zjduk)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    stmh__ewff = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        vtuu__afabs = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        vtuu__afabs = pq_dataset.pieces
    jtma__xfnx = np.zeros(len(str_columns), dtype=np.int64)
    hgku__wvpp = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(vtuu__afabs):
        nfwo__nym = vtuu__afabs[bodo.get_rank()]
        try:
            metadata = nfwo__nym.metadata
            for ryoe__lzial in range(nfwo__nym.num_row_groups):
                for ldpwy__ghqpr, hqes__zjduk in enumerate(str_columns):
                    jpm__gbirt = pa_schema.get_field_index(hqes__zjduk)
                    jtma__xfnx[ldpwy__ghqpr] += metadata.row_group(ryoe__lzial
                        ).column(jpm__gbirt).total_uncompressed_size
            bnk__brhgm = metadata.num_rows
        except Exception as mnjo__dkic:
            if isinstance(mnjo__dkic, (OSError, FileNotFoundError)):
                bnk__brhgm = 0
            else:
                raise
    else:
        bnk__brhgm = 0
    tcj__bmlhj = stmh__ewff.allreduce(bnk__brhgm, op=MPI.SUM)
    if tcj__bmlhj == 0:
        return set()
    stmh__ewff.Allreduce(jtma__xfnx, hgku__wvpp, op=MPI.SUM)
    qraki__bafme = hgku__wvpp / tcj__bmlhj
    hgl__wzrmg = set()
    for ryoe__lzial, jnhn__yiv in enumerate(qraki__bafme):
        if jnhn__yiv < READ_STR_AS_DICT_THRESHOLD:
            hqes__zjduk = str_columns[ryoe__lzial][0]
            hgl__wzrmg.add(hqes__zjduk)
    return hgl__wzrmg


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    kcwz__yqa = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    xpw__vllic = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    ukfz__ukpy = read_as_dict_cols - xpw__vllic
    if len(ukfz__ukpy) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {ukfz__ukpy}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(xpw__vllic)
    xpw__vllic = xpw__vllic - read_as_dict_cols
    str_columns = [zqyyl__qjgb for zqyyl__qjgb in str_columns if 
        zqyyl__qjgb in xpw__vllic]
    hgl__wzrmg: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    hgl__wzrmg.update(read_as_dict_cols)
    col_names = pa_schema.names
    jem__iivfw, avyt__pmee = get_pandas_metadata(pa_schema, num_pieces)
    nnlhk__jcrp = []
    tkcs__ldkz = []
    ifj__yneu = []
    for ryoe__lzial, c in enumerate(col_names):
        if c in partition_names:
            continue
        idejv__plv = pa_schema.field(c)
        uml__dowix, hhly__juvav = _get_numba_typ_from_pa_typ(idejv__plv, c ==
            jem__iivfw, avyt__pmee[c], pq_dataset._category_info,
            str_as_dict=c in hgl__wzrmg)
        nnlhk__jcrp.append(uml__dowix)
        tkcs__ldkz.append(hhly__juvav)
        ifj__yneu.append(idejv__plv.type)
    if partition_names:
        nnlhk__jcrp += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[ryoe__lzial]) for ryoe__lzial in
            range(len(partition_names))]
        tkcs__ldkz.extend([True] * len(partition_names))
        ifj__yneu.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        nnlhk__jcrp += [dict_str_arr_type]
        tkcs__ldkz.append(True)
        ifj__yneu.append(None)
    tsywk__evuni = {c: ryoe__lzial for ryoe__lzial, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in tsywk__evuni:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if jem__iivfw and not isinstance(jem__iivfw, dict
        ) and jem__iivfw not in selected_columns:
        selected_columns.append(jem__iivfw)
    col_names = selected_columns
    col_indices = []
    kcwz__yqa = []
    uro__sixa = []
    nhkch__hsr = []
    for ryoe__lzial, c in enumerate(col_names):
        xjgv__fzhz = tsywk__evuni[c]
        col_indices.append(xjgv__fzhz)
        kcwz__yqa.append(nnlhk__jcrp[xjgv__fzhz])
        if not tkcs__ldkz[xjgv__fzhz]:
            uro__sixa.append(ryoe__lzial)
            nhkch__hsr.append(ifj__yneu[xjgv__fzhz])
    return (col_names, kcwz__yqa, jem__iivfw, col_indices, partition_names,
        uro__sixa, nhkch__hsr)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    cxx__jfm = dictionary.to_pandas()
    atwon__uorjb = bodo.typeof(cxx__jfm).dtype
    if isinstance(atwon__uorjb, types.Integer):
        ywsws__dmvv = PDCategoricalDtype(tuple(cxx__jfm), atwon__uorjb, 
            False, int_type=atwon__uorjb)
    else:
        ywsws__dmvv = PDCategoricalDtype(tuple(cxx__jfm), atwon__uorjb, False)
    return CategoricalArrayType(ywsws__dmvv)


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
        dcfvs__xbm = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        uzj__fts = cgutils.get_or_insert_function(builder.module,
            dcfvs__xbm, name='pq_write')
        skz__nzcc = builder.call(uzj__fts, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return skz__nzcc
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
        dcfvs__xbm = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        uzj__fts = cgutils.get_or_insert_function(builder.module,
            dcfvs__xbm, name='pq_write_partitioned')
        builder.call(uzj__fts, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
