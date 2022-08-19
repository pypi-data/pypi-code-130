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
        dedi__dqeej = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        ecyy__wxmab = cgutils.get_or_insert_function(builder.module,
            dedi__dqeej, name='json_file_chunk_reader')
        cku__vysr = builder.call(ecyy__wxmab, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        udw__tqena = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        cbqpf__pxdhb = context.get_python_api(builder)
        udw__tqena.meminfo = cbqpf__pxdhb.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), cku__vysr)
        udw__tqena.pyobj = cku__vysr
        cbqpf__pxdhb.decref(cku__vysr)
        return udw__tqena._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    xeqm__ettaw = []
    wjktp__gnfk = []
    wxr__btoh = []
    for udz__hghc, ednb__desq in enumerate(json_node.out_vars):
        if ednb__desq.name in lives:
            xeqm__ettaw.append(json_node.df_colnames[udz__hghc])
            wjktp__gnfk.append(json_node.out_vars[udz__hghc])
            wxr__btoh.append(json_node.out_types[udz__hghc])
    json_node.df_colnames = xeqm__ettaw
    json_node.out_vars = wjktp__gnfk
    json_node.out_types = wxr__btoh
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        sued__flr = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        fna__rqujc = json_node.loc.strformat()
        axu__vzgg = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', sued__flr,
            fna__rqujc, axu__vzgg)
        bax__wudhe = [gyx__znhxj for udz__hghc, gyx__znhxj in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            udz__hghc], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if bax__wudhe:
            awje__ceth = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', awje__ceth,
                fna__rqujc, bax__wudhe)
    parallel = False
    if array_dists is not None:
        parallel = True
        for mpa__hel in json_node.out_vars:
            if array_dists[mpa__hel.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                mpa__hel.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    ypjs__xksce = len(json_node.out_vars)
    oqzf__iyf = ', '.join('arr' + str(udz__hghc) for udz__hghc in range(
        ypjs__xksce))
    izdl__kxf = 'def json_impl(fname):\n'
    izdl__kxf += '    ({},) = _json_reader_py(fname)\n'.format(oqzf__iyf)
    cohym__ufoyo = {}
    exec(izdl__kxf, {}, cohym__ufoyo)
    ypbi__evs = cohym__ufoyo['json_impl']
    hcy__klp = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    hkekm__ndmll = compile_to_numba_ir(ypbi__evs, {'_json_reader_py':
        hcy__klp}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(hkekm__ndmll, [json_node.file_name])
    qyig__ijste = hkekm__ndmll.body[:-3]
    for udz__hghc in range(len(json_node.out_vars)):
        qyig__ijste[-len(json_node.out_vars) + udz__hghc
            ].target = json_node.out_vars[udz__hghc]
    return qyig__ijste


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
    tir__zsma = [sanitize_varname(gyx__znhxj) for gyx__znhxj in col_names]
    dlo__jluh = ', '.join(str(udz__hghc) for udz__hghc, exysh__okaj in
        enumerate(col_typs) if exysh__okaj.dtype == types.NPDatetime('ns'))
    ewyy__smo = ', '.join(["{}='{}'".format(qdv__hizu, bodo.ir.csv_ext.
        _get_dtype_str(exysh__okaj)) for qdv__hizu, exysh__okaj in zip(
        tir__zsma, col_typs)])
    mquv__vlcxp = ', '.join(["'{}':{}".format(lbgmh__tydgo, bodo.ir.csv_ext
        ._get_pd_dtype_str(exysh__okaj)) for lbgmh__tydgo, exysh__okaj in
        zip(col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    izdl__kxf = 'def json_reader_py(fname):\n'
    izdl__kxf += '  df_typeref_2 = df_typeref\n'
    izdl__kxf += '  check_java_installation(fname)\n'
    izdl__kxf += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    izdl__kxf += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    izdl__kxf += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    izdl__kxf += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    izdl__kxf += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    izdl__kxf += "      raise FileNotFoundError('File does not exist')\n"
    izdl__kxf += f'  with objmode({ewyy__smo}):\n'
    izdl__kxf += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    izdl__kxf += f'       convert_dates = {convert_dates}, \n'
    izdl__kxf += f'       precise_float={precise_float}, \n'
    izdl__kxf += f'       lines={lines}, \n'
    izdl__kxf += '       dtype={{{}}},\n'.format(mquv__vlcxp)
    izdl__kxf += '       )\n'
    izdl__kxf += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for qdv__hizu, lbgmh__tydgo in zip(tir__zsma, col_names):
        izdl__kxf += '    if len(df) > 0:\n'
        izdl__kxf += "        {} = df['{}'].values\n".format(qdv__hizu,
            lbgmh__tydgo)
        izdl__kxf += '    else:\n'
        izdl__kxf += '        {} = np.array([])\n'.format(qdv__hizu)
    izdl__kxf += '  return ({},)\n'.format(', '.join(juizp__njf for
        juizp__njf in tir__zsma))
    ibl__qzgm = globals()
    ibl__qzgm.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    cohym__ufoyo = {}
    exec(izdl__kxf, ibl__qzgm, cohym__ufoyo)
    hcy__klp = cohym__ufoyo['json_reader_py']
    ldoqf__kjvid = numba.njit(hcy__klp)
    compiled_funcs.append(ldoqf__kjvid)
    return ldoqf__kjvid
