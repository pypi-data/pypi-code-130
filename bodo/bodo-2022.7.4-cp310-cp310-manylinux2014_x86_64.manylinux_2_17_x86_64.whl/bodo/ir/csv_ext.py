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
    efgbx__hin = typemap[node.file_name.name]
    if types.unliteral(efgbx__hin) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {efgbx__hin}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        fse__pzdb = typemap[node.skiprows.name]
        if isinstance(fse__pzdb, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(fse__pzdb, types.Integer) and not (isinstance(
            fse__pzdb, (types.List, types.Tuple)) and isinstance(fse__pzdb.
            dtype, types.Integer)) and not isinstance(fse__pzdb, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {fse__pzdb}."
                , loc=node.skiprows.loc)
        elif isinstance(fse__pzdb, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        eos__eir = typemap[node.nrows.name]
        if not isinstance(eos__eir, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {eos__eir}."
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
        dpeb__tilc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        rex__zhr = cgutils.get_or_insert_function(builder.module,
            dpeb__tilc, name='csv_file_chunk_reader')
        vpuy__mcul = builder.call(rex__zhr, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        kdz__iquh = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        jiq__ifq = context.get_python_api(builder)
        kdz__iquh.meminfo = jiq__ifq.nrt_meminfo_new_from_pyobject(context.
            get_constant_null(types.voidptr), vpuy__mcul)
        kdz__iquh.pyobj = vpuy__mcul
        jiq__ifq.decref(vpuy__mcul)
        return kdz__iquh._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        wdiqu__tcj = csv_node.out_vars[0]
        if wdiqu__tcj.name not in lives:
            return None
    else:
        mjl__kkwhe = csv_node.out_vars[0]
        gzjx__kuz = csv_node.out_vars[1]
        if mjl__kkwhe.name not in lives and gzjx__kuz.name not in lives:
            return None
        elif gzjx__kuz.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif mjl__kkwhe.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    fse__pzdb = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            acplr__vvoc = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            ahbf__fad = csv_node.loc.strformat()
            cqf__gnzf = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', acplr__vvoc,
                ahbf__fad, cqf__gnzf)
            odfix__jsav = csv_node.out_types[0].yield_type.data
            bmq__wqum = [qnbhf__arsvj for krv__qop, qnbhf__arsvj in
                enumerate(csv_node.df_colnames) if isinstance(odfix__jsav[
                krv__qop], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if bmq__wqum:
                uiteq__fjhxe = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    uiteq__fjhxe, ahbf__fad, bmq__wqum)
        if array_dists is not None:
            gbwq__wfg = csv_node.out_vars[0].name
            parallel = array_dists[gbwq__wfg] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        cym__kjsck = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        cym__kjsck += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        cym__kjsck += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        oizi__xedn = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(cym__kjsck, {}, oizi__xedn)
        fvdio__tqk = oizi__xedn['csv_iterator_impl']
        mone__eqszg = 'def csv_reader_init(fname, nrows, skiprows):\n'
        mone__eqszg += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        mone__eqszg += '  return f_reader\n'
        exec(mone__eqszg, globals(), oizi__xedn)
        wpiu__umy = oizi__xedn['csv_reader_init']
        vprlr__mutm = numba.njit(wpiu__umy)
        compiled_funcs.append(vprlr__mutm)
        ftkgr__btcsh = compile_to_numba_ir(fvdio__tqk, {'_csv_reader_init':
            vprlr__mutm, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, fse__pzdb), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(ftkgr__btcsh, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        wzpz__cindn = ftkgr__btcsh.body[:-3]
        wzpz__cindn[-1].target = csv_node.out_vars[0]
        return wzpz__cindn
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    cym__kjsck = 'def csv_impl(fname, nrows, skiprows):\n'
    cym__kjsck += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    oizi__xedn = {}
    exec(cym__kjsck, {}, oizi__xedn)
    qodz__hmx = oizi__xedn['csv_impl']
    mqv__vzox = csv_node.usecols
    if mqv__vzox:
        mqv__vzox = [csv_node.usecols[krv__qop] for krv__qop in csv_node.
            out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        acplr__vvoc = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        ahbf__fad = csv_node.loc.strformat()
        cqf__gnzf = []
        bmq__wqum = []
        if mqv__vzox:
            for krv__qop in csv_node.out_used_cols:
                dcx__mtwln = csv_node.df_colnames[krv__qop]
                cqf__gnzf.append(dcx__mtwln)
                if isinstance(csv_node.out_types[krv__qop], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    bmq__wqum.append(dcx__mtwln)
        bodo.user_logging.log_message('Column Pruning', acplr__vvoc,
            ahbf__fad, cqf__gnzf)
        if bmq__wqum:
            uiteq__fjhxe = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                uiteq__fjhxe, ahbf__fad, bmq__wqum)
    tpi__npd = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        mqv__vzox, csv_node.out_used_cols, csv_node.sep, parallel, csv_node
        .header, csv_node.compression, csv_node.is_skiprows_list, csv_node.
        pd_low_memory, csv_node.escapechar, csv_node.storage_options,
        idx_col_index=csv_node.index_column_index, idx_col_typ=csv_node.
        index_column_typ)
    ftkgr__btcsh = compile_to_numba_ir(qodz__hmx, {'_csv_reader_py':
        tpi__npd}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, fse__pzdb), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(ftkgr__btcsh, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    wzpz__cindn = ftkgr__btcsh.body[:-3]
    wzpz__cindn[-1].target = csv_node.out_vars[1]
    wzpz__cindn[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not mqv__vzox
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        wzpz__cindn.pop(-1)
    elif not mqv__vzox:
        wzpz__cindn.pop(-2)
    return wzpz__cindn


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
    obv__aenk = t.dtype
    if isinstance(obv__aenk, PDCategoricalDtype):
        hca__owij = CategoricalArrayType(obv__aenk)
        fjm__nqrk = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, fjm__nqrk, hca__owij)
        return fjm__nqrk
    if obv__aenk == types.NPDatetime('ns'):
        obv__aenk = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        ofsl__lqkqg = 'int_arr_{}'.format(obv__aenk)
        setattr(types, ofsl__lqkqg, t)
        return ofsl__lqkqg
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if obv__aenk == types.bool_:
        obv__aenk = 'bool_'
    if obv__aenk == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(obv__aenk, (
        StringArrayType, ArrayItemArrayType)):
        tym__gwzh = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, tym__gwzh, t)
        return tym__gwzh
    return '{}[::1]'.format(obv__aenk)


def _get_pd_dtype_str(t):
    obv__aenk = t.dtype
    if isinstance(obv__aenk, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(obv__aenk.categories)
    if obv__aenk == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if obv__aenk.signed else 'U',
            obv__aenk.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(obv__aenk, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(obv__aenk)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    ukyyp__kez = ''
    from collections import defaultdict
    unv__kjwt = defaultdict(list)
    for gfgd__uau, wpqqi__oqjls in typemap.items():
        unv__kjwt[wpqqi__oqjls].append(gfgd__uau)
    khv__zybx = df.columns.to_list()
    nlr__qog = []
    for wpqqi__oqjls, inezf__adqfc in unv__kjwt.items():
        try:
            nlr__qog.append(df.loc[:, inezf__adqfc].astype(wpqqi__oqjls,
                copy=False))
            df = df.drop(inezf__adqfc, axis=1)
        except (ValueError, TypeError) as yswf__chn:
            ukyyp__kez = (
                f"Caught the runtime error '{yswf__chn}' on columns {inezf__adqfc}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    jep__iotst = bool(ukyyp__kez)
    if parallel:
        uefhu__jxhh = MPI.COMM_WORLD
        jep__iotst = uefhu__jxhh.allreduce(jep__iotst, op=MPI.LOR)
    if jep__iotst:
        ohop__kad = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if ukyyp__kez:
            raise TypeError(f'{ohop__kad}\n{ukyyp__kez}')
        else:
            raise TypeError(
                f'{ohop__kad}\nPlease refer to errors on other ranks.')
    df = pd.concat(nlr__qog + [df], axis=1)
    tvp__zkcnh = df.loc[:, khv__zybx]
    return tvp__zkcnh


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    sbqj__ugbot = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        cym__kjsck = '  skiprows = sorted(set(skiprows))\n'
    else:
        cym__kjsck = '  skiprows = [skiprows]\n'
    cym__kjsck += '  skiprows_list_len = len(skiprows)\n'
    cym__kjsck += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    cym__kjsck += '  check_java_installation(fname)\n'
    cym__kjsck += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    cym__kjsck += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    cym__kjsck += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    cym__kjsck += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, sbqj__ugbot, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    cym__kjsck += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    cym__kjsck += "      raise FileNotFoundError('File does not exist')\n"
    return cym__kjsck


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    kmas__mfong = [str(krv__qop) for krv__qop, vhm__vgso in enumerate(
        usecols) if col_typs[out_used_cols[krv__qop]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        kmas__mfong.append(str(idx_col_index))
    ktihy__wkj = ', '.join(kmas__mfong)
    ykx__jhsdo = _gen_parallel_flag_name(sanitized_cnames)
    hgewl__gxbni = f"{ykx__jhsdo}='bool_'" if check_parallel_runtime else ''
    nsbbh__ini = [_get_pd_dtype_str(col_typs[out_used_cols[krv__qop]]) for
        krv__qop in range(len(usecols))]
    pzu__qjk = None if idx_col_index is None else _get_pd_dtype_str(idx_col_typ
        )
    mpelt__covc = [vhm__vgso for krv__qop, vhm__vgso in enumerate(usecols) if
        nsbbh__ini[krv__qop] == 'str']
    if idx_col_index is not None and pzu__qjk == 'str':
        mpelt__covc.append(idx_col_index)
    moba__vxhf = np.array(mpelt__covc, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = moba__vxhf
    cym__kjsck = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    dyisf__ohg = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = dyisf__ohg
    cym__kjsck += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    brgxp__djcaz = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = brgxp__djcaz
        cym__kjsck += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    tzvb__rsy = defaultdict(list)
    for krv__qop, vhm__vgso in enumerate(usecols):
        if nsbbh__ini[krv__qop] == 'str':
            continue
        tzvb__rsy[nsbbh__ini[krv__qop]].append(vhm__vgso)
    if idx_col_index is not None and pzu__qjk != 'str':
        tzvb__rsy[pzu__qjk].append(idx_col_index)
    for krv__qop, gwup__fmldv in enumerate(tzvb__rsy.values()):
        glbs[f't_arr_{krv__qop}_{call_id}'] = np.asarray(gwup__fmldv)
        cym__kjsck += (
            f'  t_arr_{krv__qop}_{call_id}_2 = t_arr_{krv__qop}_{call_id}\n')
    if idx_col_index != None:
        cym__kjsck += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {hgewl__gxbni}):
"""
    else:
        cym__kjsck += (
            f'  with objmode(T=table_type_{call_id}, {hgewl__gxbni}):\n')
    cym__kjsck += f'    typemap = {{}}\n'
    for krv__qop, puzpu__qugy in enumerate(tzvb__rsy.keys()):
        cym__kjsck += f"""    typemap.update({{i:{puzpu__qugy} for i in t_arr_{krv__qop}_{call_id}_2}})
"""
    cym__kjsck += '    if f_reader.get_chunk_size() == 0:\n'
    cym__kjsck += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    cym__kjsck += '    else:\n'
    cym__kjsck += '      df = pd.read_csv(f_reader,\n'
    cym__kjsck += '        header=None,\n'
    cym__kjsck += '        parse_dates=[{}],\n'.format(ktihy__wkj)
    cym__kjsck += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    cym__kjsck += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        cym__kjsck += f'    {ykx__jhsdo} = f_reader.is_parallel()\n'
    else:
        cym__kjsck += f'    {ykx__jhsdo} = {parallel}\n'
    cym__kjsck += f'    df = astype(df, typemap, {ykx__jhsdo})\n'
    if idx_col_index != None:
        cow__ooub = sorted(dyisf__ohg).index(idx_col_index)
        cym__kjsck += f'    idx_arr = df.iloc[:, {cow__ooub}].values\n'
        cym__kjsck += (
            f'    df.drop(columns=df.columns[{cow__ooub}], inplace=True)\n')
    if len(usecols) == 0:
        cym__kjsck += f'    T = None\n'
    else:
        cym__kjsck += f'    arrs = []\n'
        cym__kjsck += f'    for i in range(df.shape[1]):\n'
        cym__kjsck += f'      arrs.append(df.iloc[:, i].values)\n'
        cym__kjsck += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return cym__kjsck


def _gen_parallel_flag_name(sanitized_cnames):
    ykx__jhsdo = '_parallel_value'
    while ykx__jhsdo in sanitized_cnames:
        ykx__jhsdo = '_' + ykx__jhsdo
    return ykx__jhsdo


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(qnbhf__arsvj) for qnbhf__arsvj in
        col_names]
    cym__kjsck = 'def csv_reader_py(fname, nrows, skiprows):\n'
    cym__kjsck += _gen_csv_file_reader_init(parallel, header, compression, 
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    wjky__iwmwp = globals()
    if idx_col_typ != types.none:
        wjky__iwmwp[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        wjky__iwmwp[f'table_type_{call_id}'] = types.none
    else:
        wjky__iwmwp[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    cym__kjsck += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, wjky__iwmwp, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        cym__kjsck += '  return (T, idx_arr)\n'
    else:
        cym__kjsck += '  return (T, None)\n'
    oizi__xedn = {}
    wjky__iwmwp['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(cym__kjsck, wjky__iwmwp, oizi__xedn)
    tpi__npd = oizi__xedn['csv_reader_py']
    vprlr__mutm = numba.njit(tpi__npd)
    compiled_funcs.append(vprlr__mutm)
    return vprlr__mutm
