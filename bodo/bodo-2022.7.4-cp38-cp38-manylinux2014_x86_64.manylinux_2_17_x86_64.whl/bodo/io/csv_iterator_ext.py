"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.typing import ColNamesMetaType
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar, storage_options):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        ygj__nucf = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(ygj__nucf)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar
        self._storage_options = storage_options

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        drxt__zmi = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, drxt__zmi)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    ilv__pnmc = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    kys__zbalp = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()]
        )
    logfz__akcgs = cgutils.get_or_insert_function(builder.module,
        kys__zbalp, name='initialize_csv_reader')
    aam__grbb = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=ilv__pnmc.csv_reader)
    builder.call(logfz__akcgs, [aam__grbb.pyobj])
    builder.store(context.get_constant(types.uint64, 0), ilv__pnmc.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [nyi__eccz] = sig.args
    [xeix__twiau] = args
    ilv__pnmc = cgutils.create_struct_proxy(nyi__eccz)(context, builder,
        value=xeix__twiau)
    kys__zbalp = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()]
        )
    logfz__akcgs = cgutils.get_or_insert_function(builder.module,
        kys__zbalp, name='update_csv_reader')
    aam__grbb = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=ilv__pnmc.csv_reader)
    thw__daj = builder.call(logfz__akcgs, [aam__grbb.pyobj])
    result.set_valid(thw__daj)
    with builder.if_then(thw__daj):
        ocli__lttf = builder.load(ilv__pnmc.index)
        xkuu__ducbo = types.Tuple([sig.return_type.first_type, types.int64])
        ovkf__uub = gen_read_csv_objmode(sig.args[0])
        odu__kdbpv = signature(xkuu__ducbo, types.stream_reader_type, types
            .int64)
        qyl__jmgci = context.compile_internal(builder, ovkf__uub,
            odu__kdbpv, [ilv__pnmc.csv_reader, ocli__lttf])
        kcuj__khbr, uxwf__kws = cgutils.unpack_tuple(builder, qyl__jmgci)
        mhd__vojab = builder.add(ocli__lttf, uxwf__kws, flags=['nsw'])
        builder.store(mhd__vojab, ilv__pnmc.index)
        result.yield_(kcuj__khbr)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        gibt__unxsf = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        gibt__unxsf.csv_reader = args[0]
        irlhj__aww = context.get_constant(types.uintp, 0)
        gibt__unxsf.index = cgutils.alloca_once_value(builder, irlhj__aww)
        return gibt__unxsf._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    livz__ubfe = csv_iterator_typeref.instance_type
    sig = signature(livz__ubfe, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    kqpm__msm = 'def read_csv_objmode(f_reader):\n'
    dba__odk = [sanitize_varname(stqbl__ghcsy) for stqbl__ghcsy in
        csv_iterator_type._out_colnames]
    cbp__lyf = ir_utils.next_label()
    geua__jjoo = globals()
    out_types = csv_iterator_type._out_types
    geua__jjoo[f'table_type_{cbp__lyf}'] = TableType(tuple(out_types))
    geua__jjoo[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    uiw__erux = list(range(len(csv_iterator_type._usecols)))
    kqpm__msm += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        dba__odk, out_types, csv_iterator_type._usecols, uiw__erux,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, cbp__lyf, geua__jjoo, parallel=
        False, check_parallel_runtime=True, idx_col_index=csv_iterator_type
        ._index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    koejy__bwvi = bodo.ir.csv_ext._gen_parallel_flag_name(dba__odk)
    lppzi__qjidt = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [koejy__bwvi]
    kqpm__msm += f"  return {', '.join(lppzi__qjidt)}"
    geua__jjoo = globals()
    idis__rxlb = {}
    exec(kqpm__msm, geua__jjoo, idis__rxlb)
    wulnx__zlok = idis__rxlb['read_csv_objmode']
    obs__pbl = numba.njit(wulnx__zlok)
    bodo.ir.csv_ext.compiled_funcs.append(obs__pbl)
    ocuxw__safct = 'def read_func(reader, local_start):\n'
    ocuxw__safct += f"  {', '.join(lppzi__qjidt)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        ocuxw__safct += f'  local_len = len(T)\n'
        ocuxw__safct += '  total_size = local_len\n'
        ocuxw__safct += f'  if ({koejy__bwvi}):\n'
        ocuxw__safct += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        ocuxw__safct += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        naoti__xfe = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        ocuxw__safct += '  total_size = 0\n'
        naoti__xfe = (
            f'bodo.utils.conversion.convert_to_index({lppzi__qjidt[1]}, {csv_iterator_type._index_name!r})'
            )
    ocuxw__safct += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({lppzi__qjidt[0]},), {naoti__xfe}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(ocuxw__safct, {'bodo': bodo, 'objmode_func': obs__pbl, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, idis__rxlb)
    return idis__rxlb['read_func']
