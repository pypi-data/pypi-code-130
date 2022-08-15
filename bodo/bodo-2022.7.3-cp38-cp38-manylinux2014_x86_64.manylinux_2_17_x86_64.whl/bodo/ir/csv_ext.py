from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import check_and_propagate_cpp_exception, sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        storage_options=None, index_column_index=None, index_column_typ=
        types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.storage_options = storage_options
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.out_used_cols = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, escapechar={}, storage_options={}, index_column_index={}, index_colum_typ = {}, out_used_colss={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            escapechar, self.storage_options, self.index_column_index, self
            .index_column_typ, self.out_used_cols))


def check_node_typing(node, typemap):
    piiex__kmdz = typemap[node.file_name.name]
    if types.unliteral(piiex__kmdz) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {piiex__kmdz}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        uemz__nem = typemap[node.skiprows.name]
        if isinstance(uemz__nem, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(uemz__nem, types.Integer) and not (isinstance(
            uemz__nem, (types.List, types.Tuple)) and isinstance(uemz__nem.
            dtype, types.Integer)) and not isinstance(uemz__nem, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {uemz__nem}."
                , loc=node.skiprows.loc)
        elif isinstance(uemz__nem, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        xfejj__wvkpo = typemap[node.nrows.name]
        if not isinstance(xfejj__wvkpo, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {xfejj__wvkpo}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)


@intrinsic
def csv_file_chunk_reader(typingctx, fname_t, is_parallel_t, skiprows_t,
    nrows_t, header_t, compression_t, bucket_region_t, storage_options_t,
    chunksize_t, is_skiprows_list_t, skiprows_list_len_t, pd_low_memory_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        joq__hgxin = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        rcip__oytaz = cgutils.get_or_insert_function(builder.module,
            joq__hgxin, name='csv_file_chunk_reader')
        uxlhy__qiavc = builder.call(rcip__oytaz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        qpuz__lkf = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        qqsm__ylurt = context.get_python_api(builder)
        qpuz__lkf.meminfo = qqsm__ylurt.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), uxlhy__qiavc)
        qpuz__lkf.pyobj = uxlhy__qiavc
        qqsm__ylurt.decref(uxlhy__qiavc)
        return qpuz__lkf._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        kmkb__pofs = csv_node.out_vars[0]
        if kmkb__pofs.name not in lives:
            return None
    else:
        syvc__keu = csv_node.out_vars[0]
        sicq__ddkhq = csv_node.out_vars[1]
        if syvc__keu.name not in lives and sicq__ddkhq.name not in lives:
            return None
        elif sicq__ddkhq.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif syvc__keu.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    uemz__nem = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            yxjq__kiu = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            hnjl__wobg = csv_node.loc.strformat()
            hqlkq__vmv = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', yxjq__kiu,
                hnjl__wobg, hqlkq__vmv)
            clqyb__dcghu = csv_node.out_types[0].yield_type.data
            rovg__gmz = [mxqp__yqjl for hohjm__oup, mxqp__yqjl in enumerate
                (csv_node.df_colnames) if isinstance(clqyb__dcghu[
                hohjm__oup], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if rovg__gmz:
                yejd__ccgo = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    yejd__ccgo, hnjl__wobg, rovg__gmz)
        if array_dists is not None:
            mua__wih = csv_node.out_vars[0].name
            parallel = array_dists[mua__wih] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        skhv__bcx = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        skhv__bcx += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        skhv__bcx += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        flbv__uousc = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(skhv__bcx, {}, flbv__uousc)
        nnb__bvyiq = flbv__uousc['csv_iterator_impl']
        ztg__qigup = 'def csv_reader_init(fname, nrows, skiprows):\n'
        ztg__qigup += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        ztg__qigup += '  return f_reader\n'
        exec(ztg__qigup, globals(), flbv__uousc)
        mdbs__vzdw = flbv__uousc['csv_reader_init']
        jpni__dfd = numba.njit(mdbs__vzdw)
        compiled_funcs.append(jpni__dfd)
        njzr__gtb = compile_to_numba_ir(nnb__bvyiq, {'_csv_reader_init':
            jpni__dfd, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, uemz__nem), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(njzr__gtb, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        ydr__wfbmz = njzr__gtb.body[:-3]
        ydr__wfbmz[-1].target = csv_node.out_vars[0]
        return ydr__wfbmz
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    skhv__bcx = 'def csv_impl(fname, nrows, skiprows):\n'
    skhv__bcx += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    flbv__uousc = {}
    exec(skhv__bcx, {}, flbv__uousc)
    acryg__khgaf = flbv__uousc['csv_impl']
    bvoxc__svh = csv_node.usecols
    if bvoxc__svh:
        bvoxc__svh = [csv_node.usecols[hohjm__oup] for hohjm__oup in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        yxjq__kiu = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        hnjl__wobg = csv_node.loc.strformat()
        hqlkq__vmv = []
        rovg__gmz = []
        if bvoxc__svh:
            for hohjm__oup in csv_node.out_used_cols:
                ltpfd__nltaq = csv_node.df_colnames[hohjm__oup]
                hqlkq__vmv.append(ltpfd__nltaq)
                if isinstance(csv_node.out_types[hohjm__oup], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    rovg__gmz.append(ltpfd__nltaq)
        bodo.user_logging.log_message('Column Pruning', yxjq__kiu,
            hnjl__wobg, hqlkq__vmv)
        if rovg__gmz:
            yejd__ccgo = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', yejd__ccgo,
                hnjl__wobg, rovg__gmz)
    hjys__wziv = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, bvoxc__svh, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    njzr__gtb = compile_to_numba_ir(acryg__khgaf, {'_csv_reader_py':
        hjys__wziv}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, uemz__nem), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(njzr__gtb, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    ydr__wfbmz = njzr__gtb.body[:-3]
    ydr__wfbmz[-1].target = csv_node.out_vars[1]
    ydr__wfbmz[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not bvoxc__svh
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        ydr__wfbmz.pop(-1)
    elif not bvoxc__svh:
        ydr__wfbmz.pop(-2)
    return ydr__wfbmz


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    return bodo.ir.connector.base_connector_remove_dead_columns(csv_node,
        column_live_map, equiv_vars, typemap, 'CSVReader', csv_node.usecols)


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader
    ] = bodo.ir.connector.connector_table_column_use


def _get_dtype_str(t):
    yzet__wxlm = t.dtype
    if isinstance(yzet__wxlm, PDCategoricalDtype):
        kjnjr__zma = CategoricalArrayType(yzet__wxlm)
        ocx__qpci = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, ocx__qpci, kjnjr__zma)
        return ocx__qpci
    if yzet__wxlm == types.NPDatetime('ns'):
        yzet__wxlm = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        mgabt__cxmgp = 'int_arr_{}'.format(yzet__wxlm)
        setattr(types, mgabt__cxmgp, t)
        return mgabt__cxmgp
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if yzet__wxlm == types.bool_:
        yzet__wxlm = 'bool_'
    if yzet__wxlm == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(yzet__wxlm, (
        StringArrayType, ArrayItemArrayType)):
        gmh__fpvyz = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, gmh__fpvyz, t)
        return gmh__fpvyz
    return '{}[::1]'.format(yzet__wxlm)


def _get_pd_dtype_str(t):
    yzet__wxlm = t.dtype
    if isinstance(yzet__wxlm, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(yzet__wxlm.categories)
    if yzet__wxlm == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if yzet__wxlm.signed else 'U',
            yzet__wxlm.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(yzet__wxlm, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(yzet__wxlm)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    rzbg__gbqr = ''
    from collections import defaultdict
    zkwvc__nrdb = defaultdict(list)
    for epof__wpylc, uni__cjn in typemap.items():
        zkwvc__nrdb[uni__cjn].append(epof__wpylc)
    aqf__mwdax = df.columns.to_list()
    rhog__sfzw = []
    for uni__cjn, dct__oume in zkwvc__nrdb.items():
        try:
            rhog__sfzw.append(df.loc[:, dct__oume].astype(uni__cjn, copy=False)
                )
            df = df.drop(dct__oume, axis=1)
        except (ValueError, TypeError) as upryn__ryft:
            rzbg__gbqr = (
                f"Caught the runtime error '{upryn__ryft}' on columns {dct__oume}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    rcx__ayv = bool(rzbg__gbqr)
    if parallel:
        naj__yosrg = MPI.COMM_WORLD
        rcx__ayv = naj__yosrg.allreduce(rcx__ayv, op=MPI.LOR)
    if rcx__ayv:
        npptx__gwh = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if rzbg__gbqr:
            raise TypeError(f'{npptx__gwh}\n{rzbg__gbqr}')
        else:
            raise TypeError(
                f'{npptx__gwh}\nPlease refer to errors on other ranks.')
    df = pd.concat(rhog__sfzw + [df], axis=1)
    miw__fmk = df.loc[:, aqf__mwdax]
    return miw__fmk


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    ojhm__ropq = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        skhv__bcx = '  skiprows = sorted(set(skiprows))\n'
    else:
        skhv__bcx = '  skiprows = [skiprows]\n'
    skhv__bcx += '  skiprows_list_len = len(skiprows)\n'
    skhv__bcx += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    skhv__bcx += '  check_java_installation(fname)\n'
    skhv__bcx += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    skhv__bcx += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    skhv__bcx += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    skhv__bcx += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, ojhm__ropq, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    skhv__bcx += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    skhv__bcx += "      raise FileNotFoundError('File does not exist')\n"
    return skhv__bcx


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    kzmk__exvp = [str(hohjm__oup) for hohjm__oup, flei__pdix in enumerate(
        usecols) if col_typs[out_used_cols[hohjm__oup]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        kzmk__exvp.append(str(idx_col_index))
    kvi__kztlf = ', '.join(kzmk__exvp)
    dgvx__rqv = _gen_parallel_flag_name(sanitized_cnames)
    ikaym__sms = f"{dgvx__rqv}='bool_'" if check_parallel_runtime else ''
    tyi__ltycn = [_get_pd_dtype_str(col_typs[out_used_cols[hohjm__oup]]) for
        hohjm__oup in range(len(usecols))]
    iavg__yndrj = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    vtmcv__gqzqj = [flei__pdix for hohjm__oup, flei__pdix in enumerate(
        usecols) if tyi__ltycn[hohjm__oup] == 'str']
    if idx_col_index is not None and iavg__yndrj == 'str':
        vtmcv__gqzqj.append(idx_col_index)
    nkso__qbgas = np.array(vtmcv__gqzqj, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = nkso__qbgas
    skhv__bcx = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    uzcy__esoh = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = uzcy__esoh
    skhv__bcx += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    vrytn__afmux = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = vrytn__afmux
        skhv__bcx += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    xggg__udm = defaultdict(list)
    for hohjm__oup, flei__pdix in enumerate(usecols):
        if tyi__ltycn[hohjm__oup] == 'str':
            continue
        xggg__udm[tyi__ltycn[hohjm__oup]].append(flei__pdix)
    if idx_col_index is not None and iavg__yndrj != 'str':
        xggg__udm[iavg__yndrj].append(idx_col_index)
    for hohjm__oup, udlzn__zvsn in enumerate(xggg__udm.values()):
        glbs[f't_arr_{hohjm__oup}_{call_id}'] = np.asarray(udlzn__zvsn)
        skhv__bcx += (
            f'  t_arr_{hohjm__oup}_{call_id}_2 = t_arr_{hohjm__oup}_{call_id}\n'
            )
    if idx_col_index != None:
        skhv__bcx += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {ikaym__sms}):
"""
    else:
        skhv__bcx += f'  with objmode(T=table_type_{call_id}, {ikaym__sms}):\n'
    skhv__bcx += f'    typemap = {{}}\n'
    for hohjm__oup, tcfkw__bvl in enumerate(xggg__udm.keys()):
        skhv__bcx += f"""    typemap.update({{i:{tcfkw__bvl} for i in t_arr_{hohjm__oup}_{call_id}_2}})
"""
    skhv__bcx += '    if f_reader.get_chunk_size() == 0:\n'
    skhv__bcx += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    skhv__bcx += '    else:\n'
    skhv__bcx += '      df = pd.read_csv(f_reader,\n'
    skhv__bcx += '        header=None,\n'
    skhv__bcx += '        parse_dates=[{}],\n'.format(kvi__kztlf)
    skhv__bcx += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    skhv__bcx += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        skhv__bcx += f'    {dgvx__rqv} = f_reader.is_parallel()\n'
    else:
        skhv__bcx += f'    {dgvx__rqv} = {parallel}\n'
    skhv__bcx += f'    df = astype(df, typemap, {dgvx__rqv})\n'
    if idx_col_index != None:
        hzqww__gtc = sorted(uzcy__esoh).index(idx_col_index)
        skhv__bcx += f'    idx_arr = df.iloc[:, {hzqww__gtc}].values\n'
        skhv__bcx += (
            f'    df.drop(columns=df.columns[{hzqww__gtc}], inplace=True)\n')
    if len(usecols) == 0:
        skhv__bcx += f'    T = None\n'
    else:
        skhv__bcx += f'    arrs = []\n'
        skhv__bcx += f'    for i in range(df.shape[1]):\n'
        skhv__bcx += f'      arrs.append(df.iloc[:, i].values)\n'
        skhv__bcx += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return skhv__bcx


def _gen_parallel_flag_name(sanitized_cnames):
    dgvx__rqv = '_parallel_value'
    while dgvx__rqv in sanitized_cnames:
        dgvx__rqv = '_' + dgvx__rqv
    return dgvx__rqv


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(mxqp__yqjl) for mxqp__yqjl in
        col_names]
    skhv__bcx = 'def csv_reader_py(fname, nrows, skiprows):\n'
    skhv__bcx += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    lpy__pjfld = globals()
    if idx_col_typ != types.none:
        lpy__pjfld[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        lpy__pjfld[f'table_type_{call_id}'] = types.none
    else:
        lpy__pjfld[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    skhv__bcx += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, lpy__pjfld, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        skhv__bcx += '  return (T, idx_arr)\n'
    else:
        skhv__bcx += '  return (T, None)\n'
    flbv__uousc = {}
    lpy__pjfld['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(skhv__bcx, lpy__pjfld, flbv__uousc)
    hjys__wziv = flbv__uousc['csv_reader_py']
    jpni__dfd = numba.njit(hjys__wziv)
    compiled_funcs.append(jpni__dfd)
    return jpni__dfd
