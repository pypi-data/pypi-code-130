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
    abcs__jlu = typemap[node.file_name.name]
    if types.unliteral(abcs__jlu) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {abcs__jlu}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        nlaiz__zfh = typemap[node.skiprows.name]
        if isinstance(nlaiz__zfh, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(nlaiz__zfh, types.Integer) and not (isinstance(
            nlaiz__zfh, (types.List, types.Tuple)) and isinstance(
            nlaiz__zfh.dtype, types.Integer)) and not isinstance(nlaiz__zfh,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {nlaiz__zfh}."
                , loc=node.skiprows.loc)
        elif isinstance(nlaiz__zfh, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        wafob__emke = typemap[node.nrows.name]
        if not isinstance(wafob__emke, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {wafob__emke}."
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
        ijjs__owey = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        vfbpw__wqaa = cgutils.get_or_insert_function(builder.module,
            ijjs__owey, name='csv_file_chunk_reader')
        lccxy__slsf = builder.call(vfbpw__wqaa, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        gsp__hwi = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        fat__pri = context.get_python_api(builder)
        gsp__hwi.meminfo = fat__pri.nrt_meminfo_new_from_pyobject(context.
            get_constant_null(types.voidptr), lccxy__slsf)
        gsp__hwi.pyobj = lccxy__slsf
        fat__pri.decref(lccxy__slsf)
        return gsp__hwi._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        ltonw__sxjf = csv_node.out_vars[0]
        if ltonw__sxjf.name not in lives:
            return None
    else:
        kbszh__msmdi = csv_node.out_vars[0]
        iwd__kqcdk = csv_node.out_vars[1]
        if kbszh__msmdi.name not in lives and iwd__kqcdk.name not in lives:
            return None
        elif iwd__kqcdk.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif kbszh__msmdi.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    nlaiz__zfh = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            thi__pim = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            cvsg__lpei = csv_node.loc.strformat()
            zsubn__edq = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', thi__pim,
                cvsg__lpei, zsubn__edq)
            eouy__svfs = csv_node.out_types[0].yield_type.data
            bpr__ioy = [xdei__biy for zbrt__dzo, xdei__biy in enumerate(
                csv_node.df_colnames) if isinstance(eouy__svfs[zbrt__dzo],
                bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if bpr__ioy:
                bhon__uoxhq = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    bhon__uoxhq, cvsg__lpei, bpr__ioy)
        if array_dists is not None:
            ziwf__uwwt = csv_node.out_vars[0].name
            parallel = array_dists[ziwf__uwwt] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        zpp__fdxm = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        zpp__fdxm += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        zpp__fdxm += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        vdzo__dhj = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(zpp__fdxm, {}, vdzo__dhj)
        kck__wsf = vdzo__dhj['csv_iterator_impl']
        yadoa__liw = 'def csv_reader_init(fname, nrows, skiprows):\n'
        yadoa__liw += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        yadoa__liw += '  return f_reader\n'
        exec(yadoa__liw, globals(), vdzo__dhj)
        tjd__ibu = vdzo__dhj['csv_reader_init']
        rew__qzwz = numba.njit(tjd__ibu)
        compiled_funcs.append(rew__qzwz)
        edjrw__xety = compile_to_numba_ir(kck__wsf, {'_csv_reader_init':
            rew__qzwz, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, nlaiz__zfh), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(edjrw__xety, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        lhw__tfr = edjrw__xety.body[:-3]
        lhw__tfr[-1].target = csv_node.out_vars[0]
        return lhw__tfr
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    zpp__fdxm = 'def csv_impl(fname, nrows, skiprows):\n'
    zpp__fdxm += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    vdzo__dhj = {}
    exec(zpp__fdxm, {}, vdzo__dhj)
    zdix__epda = vdzo__dhj['csv_impl']
    qng__huu = csv_node.usecols
    if qng__huu:
        qng__huu = [csv_node.usecols[zbrt__dzo] for zbrt__dzo in csv_node.
            out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        thi__pim = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        cvsg__lpei = csv_node.loc.strformat()
        zsubn__edq = []
        bpr__ioy = []
        if qng__huu:
            for zbrt__dzo in csv_node.out_used_cols:
                esguf__ecdia = csv_node.df_colnames[zbrt__dzo]
                zsubn__edq.append(esguf__ecdia)
                if isinstance(csv_node.out_types[zbrt__dzo], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    bpr__ioy.append(esguf__ecdia)
        bodo.user_logging.log_message('Column Pruning', thi__pim,
            cvsg__lpei, zsubn__edq)
        if bpr__ioy:
            bhon__uoxhq = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                bhon__uoxhq, cvsg__lpei, bpr__ioy)
    ide__kjd = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        qng__huu, csv_node.out_used_cols, csv_node.sep, parallel, csv_node.
        header, csv_node.compression, csv_node.is_skiprows_list, csv_node.
        pd_low_memory, csv_node.escapechar, csv_node.storage_options,
        idx_col_index=csv_node.index_column_index, idx_col_typ=csv_node.
        index_column_typ)
    edjrw__xety = compile_to_numba_ir(zdix__epda, {'_csv_reader_py':
        ide__kjd}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, nlaiz__zfh), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(edjrw__xety, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    lhw__tfr = edjrw__xety.body[:-3]
    lhw__tfr[-1].target = csv_node.out_vars[1]
    lhw__tfr[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not qng__huu
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        lhw__tfr.pop(-1)
    elif not qng__huu:
        lhw__tfr.pop(-2)
    return lhw__tfr


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
    vbduf__sfofc = t.dtype
    if isinstance(vbduf__sfofc, PDCategoricalDtype):
        bnfn__leip = CategoricalArrayType(vbduf__sfofc)
        zvnl__xfarz = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, zvnl__xfarz, bnfn__leip)
        return zvnl__xfarz
    if vbduf__sfofc == types.NPDatetime('ns'):
        vbduf__sfofc = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        pvmdx__cmd = 'int_arr_{}'.format(vbduf__sfofc)
        setattr(types, pvmdx__cmd, t)
        return pvmdx__cmd
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if vbduf__sfofc == types.bool_:
        vbduf__sfofc = 'bool_'
    if vbduf__sfofc == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(vbduf__sfofc, (
        StringArrayType, ArrayItemArrayType)):
        xth__qkrcc = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, xth__qkrcc, t)
        return xth__qkrcc
    return '{}[::1]'.format(vbduf__sfofc)


def _get_pd_dtype_str(t):
    vbduf__sfofc = t.dtype
    if isinstance(vbduf__sfofc, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(vbduf__sfofc.categories)
    if vbduf__sfofc == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if vbduf__sfofc.signed else 'U',
            vbduf__sfofc.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(vbduf__sfofc, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(vbduf__sfofc)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    zhurr__onxq = ''
    from collections import defaultdict
    bbf__uvgru = defaultdict(list)
    for tks__rfo, oiv__ymis in typemap.items():
        bbf__uvgru[oiv__ymis].append(tks__rfo)
    iwa__kfwy = df.columns.to_list()
    xcrbp__mvfut = []
    for oiv__ymis, tel__doab in bbf__uvgru.items():
        try:
            xcrbp__mvfut.append(df.loc[:, tel__doab].astype(oiv__ymis, copy
                =False))
            df = df.drop(tel__doab, axis=1)
        except (ValueError, TypeError) as fwsac__jgd:
            zhurr__onxq = (
                f"Caught the runtime error '{fwsac__jgd}' on columns {tel__doab}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    hyo__sgbmx = bool(zhurr__onxq)
    if parallel:
        iuhs__bmdfw = MPI.COMM_WORLD
        hyo__sgbmx = iuhs__bmdfw.allreduce(hyo__sgbmx, op=MPI.LOR)
    if hyo__sgbmx:
        cvopm__vek = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if zhurr__onxq:
            raise TypeError(f'{cvopm__vek}\n{zhurr__onxq}')
        else:
            raise TypeError(
                f'{cvopm__vek}\nPlease refer to errors on other ranks.')
    df = pd.concat(xcrbp__mvfut + [df], axis=1)
    hup__qia = df.loc[:, iwa__kfwy]
    return hup__qia


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    sla__bbzic = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        zpp__fdxm = '  skiprows = sorted(set(skiprows))\n'
    else:
        zpp__fdxm = '  skiprows = [skiprows]\n'
    zpp__fdxm += '  skiprows_list_len = len(skiprows)\n'
    zpp__fdxm += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    zpp__fdxm += '  check_java_installation(fname)\n'
    zpp__fdxm += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    zpp__fdxm += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    zpp__fdxm += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    zpp__fdxm += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, sla__bbzic, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    zpp__fdxm += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    zpp__fdxm += "      raise FileNotFoundError('File does not exist')\n"
    return zpp__fdxm


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    rrd__pszq = [str(zbrt__dzo) for zbrt__dzo, kwonh__zehk in enumerate(
        usecols) if col_typs[out_used_cols[zbrt__dzo]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        rrd__pszq.append(str(idx_col_index))
    yxopa__bzgq = ', '.join(rrd__pszq)
    cobj__yfmlt = _gen_parallel_flag_name(sanitized_cnames)
    dur__gfbmx = f"{cobj__yfmlt}='bool_'" if check_parallel_runtime else ''
    mjvx__pcm = [_get_pd_dtype_str(col_typs[out_used_cols[zbrt__dzo]]) for
        zbrt__dzo in range(len(usecols))]
    wybgy__jtjm = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    hrxa__lqjuu = [kwonh__zehk for zbrt__dzo, kwonh__zehk in enumerate(
        usecols) if mjvx__pcm[zbrt__dzo] == 'str']
    if idx_col_index is not None and wybgy__jtjm == 'str':
        hrxa__lqjuu.append(idx_col_index)
    jxbi__fai = np.array(hrxa__lqjuu, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = jxbi__fai
    zpp__fdxm = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    hepc__ycid = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = hepc__ycid
    zpp__fdxm += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    puvo__ibzi = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = puvo__ibzi
        zpp__fdxm += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    jfzbv__hjxtk = defaultdict(list)
    for zbrt__dzo, kwonh__zehk in enumerate(usecols):
        if mjvx__pcm[zbrt__dzo] == 'str':
            continue
        jfzbv__hjxtk[mjvx__pcm[zbrt__dzo]].append(kwonh__zehk)
    if idx_col_index is not None and wybgy__jtjm != 'str':
        jfzbv__hjxtk[wybgy__jtjm].append(idx_col_index)
    for zbrt__dzo, jwllp__qorxc in enumerate(jfzbv__hjxtk.values()):
        glbs[f't_arr_{zbrt__dzo}_{call_id}'] = np.asarray(jwllp__qorxc)
        zpp__fdxm += (
            f'  t_arr_{zbrt__dzo}_{call_id}_2 = t_arr_{zbrt__dzo}_{call_id}\n')
    if idx_col_index != None:
        zpp__fdxm += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {dur__gfbmx}):
"""
    else:
        zpp__fdxm += f'  with objmode(T=table_type_{call_id}, {dur__gfbmx}):\n'
    zpp__fdxm += f'    typemap = {{}}\n'
    for zbrt__dzo, skpj__fgbpv in enumerate(jfzbv__hjxtk.keys()):
        zpp__fdxm += f"""    typemap.update({{i:{skpj__fgbpv} for i in t_arr_{zbrt__dzo}_{call_id}_2}})
"""
    zpp__fdxm += '    if f_reader.get_chunk_size() == 0:\n'
    zpp__fdxm += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    zpp__fdxm += '    else:\n'
    zpp__fdxm += '      df = pd.read_csv(f_reader,\n'
    zpp__fdxm += '        header=None,\n'
    zpp__fdxm += '        parse_dates=[{}],\n'.format(yxopa__bzgq)
    zpp__fdxm += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    zpp__fdxm += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        zpp__fdxm += f'    {cobj__yfmlt} = f_reader.is_parallel()\n'
    else:
        zpp__fdxm += f'    {cobj__yfmlt} = {parallel}\n'
    zpp__fdxm += f'    df = astype(df, typemap, {cobj__yfmlt})\n'
    if idx_col_index != None:
        inpu__ixhi = sorted(hepc__ycid).index(idx_col_index)
        zpp__fdxm += f'    idx_arr = df.iloc[:, {inpu__ixhi}].values\n'
        zpp__fdxm += (
            f'    df.drop(columns=df.columns[{inpu__ixhi}], inplace=True)\n')
    if len(usecols) == 0:
        zpp__fdxm += f'    T = None\n'
    else:
        zpp__fdxm += f'    arrs = []\n'
        zpp__fdxm += f'    for i in range(df.shape[1]):\n'
        zpp__fdxm += f'      arrs.append(df.iloc[:, i].values)\n'
        zpp__fdxm += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return zpp__fdxm


def _gen_parallel_flag_name(sanitized_cnames):
    cobj__yfmlt = '_parallel_value'
    while cobj__yfmlt in sanitized_cnames:
        cobj__yfmlt = '_' + cobj__yfmlt
    return cobj__yfmlt


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(xdei__biy) for xdei__biy in col_names]
    zpp__fdxm = 'def csv_reader_py(fname, nrows, skiprows):\n'
    zpp__fdxm += _gen_csv_file_reader_init(parallel, header, compression, -
        1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    wnzrt__ypid = globals()
    if idx_col_typ != types.none:
        wnzrt__ypid[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        wnzrt__ypid[f'table_type_{call_id}'] = types.none
    else:
        wnzrt__ypid[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    zpp__fdxm += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, wnzrt__ypid, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        zpp__fdxm += '  return (T, idx_arr)\n'
    else:
        zpp__fdxm += '  return (T, None)\n'
    vdzo__dhj = {}
    wnzrt__ypid['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(zpp__fdxm, wnzrt__ypid, vdzo__dhj)
    ide__kjd = vdzo__dhj['csv_reader_py']
    rew__qzwz = numba.njit(ide__kjd)
    compiled_funcs.append(rew__qzwz)
    return rew__qzwz
