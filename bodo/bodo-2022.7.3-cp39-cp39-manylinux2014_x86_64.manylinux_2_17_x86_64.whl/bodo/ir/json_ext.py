import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_and_propagate_cpp_exception, check_java_installation, sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines,
        compression, storage_options):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression
        self.storage_options = storage_options

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)


@intrinsic
def json_file_chunk_reader(typingctx, fname_t, lines_t, is_parallel_t,
    nrows_t, compression_t, bucket_region_t, storage_options_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        daweo__dvo = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jsl__ldid = cgutils.get_or_insert_function(builder.module,
            daweo__dvo, name='json_file_chunk_reader')
        heiex__xsy = builder.call(jsl__ldid, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dazq__why = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        pdbqu__fgmu = context.get_python_api(builder)
        dazq__why.meminfo = pdbqu__fgmu.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), heiex__xsy)
        dazq__why.pyobj = heiex__xsy
        pdbqu__fgmu.decref(heiex__xsy)
        return dazq__why._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    jndbg__dnodd = []
    stcw__llues = []
    plr__jos = []
    for eqa__zpwx, ypv__vvng in enumerate(json_node.out_vars):
        if ypv__vvng.name in lives:
            jndbg__dnodd.append(json_node.df_colnames[eqa__zpwx])
            stcw__llues.append(json_node.out_vars[eqa__zpwx])
            plr__jos.append(json_node.out_types[eqa__zpwx])
    json_node.df_colnames = jndbg__dnodd
    json_node.out_vars = stcw__llues
    json_node.out_types = plr__jos
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        tgxvc__ncjy = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        qhdr__krw = json_node.loc.strformat()
        eqxn__lshwr = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', tgxvc__ncjy,
            qhdr__krw, eqxn__lshwr)
        iax__cfsda = [ktezm__orsv for eqa__zpwx, ktezm__orsv in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            eqa__zpwx], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if iax__cfsda:
            pfhvm__zhv = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', pfhvm__zhv,
                qhdr__krw, iax__cfsda)
    parallel = False
    if array_dists is not None:
        parallel = True
        for pcui__fty in json_node.out_vars:
            if array_dists[pcui__fty.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                pcui__fty.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    suqin__wah = len(json_node.out_vars)
    vxf__gnnje = ', '.join('arr' + str(eqa__zpwx) for eqa__zpwx in range(
        suqin__wah))
    cler__qje = 'def json_impl(fname):\n'
    cler__qje += '    ({},) = _json_reader_py(fname)\n'.format(vxf__gnnje)
    bbm__efk = {}
    exec(cler__qje, {}, bbm__efk)
    xtawb__bhbp = bbm__efk['json_impl']
    eyv__nqgx = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    izgjl__ivsct = compile_to_numba_ir(xtawb__bhbp, {'_json_reader_py':
        eyv__nqgx}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(izgjl__ivsct, [json_node.file_name])
    cldva__ejzm = izgjl__ivsct.body[:-3]
    for eqa__zpwx in range(len(json_node.out_vars)):
        cldva__ejzm[-len(json_node.out_vars) + eqa__zpwx
            ].target = json_node.out_vars[eqa__zpwx]
    return cldva__ejzm


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression, storage_options):
    tzg__woq = [sanitize_varname(ktezm__orsv) for ktezm__orsv in col_names]
    khhvg__vcno = ', '.join(str(eqa__zpwx) for eqa__zpwx, fhuc__jctvk in
        enumerate(col_typs) if fhuc__jctvk.dtype == types.NPDatetime('ns'))
    qdxhv__decwc = ', '.join(["{}='{}'".format(agkx__vzr, bodo.ir.csv_ext.
        _get_dtype_str(fhuc__jctvk)) for agkx__vzr, fhuc__jctvk in zip(
        tzg__woq, col_typs)])
    wwk__xfuba = ', '.join(["'{}':{}".format(bcrqu__xrk, bodo.ir.csv_ext.
        _get_pd_dtype_str(fhuc__jctvk)) for bcrqu__xrk, fhuc__jctvk in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    cler__qje = 'def json_reader_py(fname):\n'
    cler__qje += '  df_typeref_2 = df_typeref\n'
    cler__qje += '  check_java_installation(fname)\n'
    cler__qje += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    cler__qje += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    cler__qje += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    cler__qje += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    cler__qje += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    cler__qje += "      raise FileNotFoundError('File does not exist')\n"
    cler__qje += f'  with objmode({qdxhv__decwc}):\n'
    cler__qje += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    cler__qje += f'       convert_dates = {convert_dates}, \n'
    cler__qje += f'       precise_float={precise_float}, \n'
    cler__qje += f'       lines={lines}, \n'
    cler__qje += '       dtype={{{}}},\n'.format(wwk__xfuba)
    cler__qje += '       )\n'
    cler__qje += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for agkx__vzr, bcrqu__xrk in zip(tzg__woq, col_names):
        cler__qje += '    if len(df) > 0:\n'
        cler__qje += "        {} = df['{}'].values\n".format(agkx__vzr,
            bcrqu__xrk)
        cler__qje += '    else:\n'
        cler__qje += '        {} = np.array([])\n'.format(agkx__vzr)
    cler__qje += '  return ({},)\n'.format(', '.join(voe__jpr for voe__jpr in
        tzg__woq))
    qqpf__psiv = globals()
    qqpf__psiv.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    bbm__efk = {}
    exec(cler__qje, qqpf__psiv, bbm__efk)
    eyv__nqgx = bbm__efk['json_reader_py']
    sulfq__luuez = numba.njit(eyv__nqgx)
    compiled_funcs.append(sulfq__luuez)
    return sulfq__luuez
