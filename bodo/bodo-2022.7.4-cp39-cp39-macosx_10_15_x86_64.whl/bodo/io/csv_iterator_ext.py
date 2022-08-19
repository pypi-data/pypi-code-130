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
        zumql__nah = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(zumql__nah)
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
        utdi__lwcd = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, utdi__lwcd)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    dgyds__vdx = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    pru__czk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()])
    yfy__ozgzk = cgutils.get_or_insert_function(builder.module, pru__czk,
        name='initialize_csv_reader')
    sgpl__yibgt = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=dgyds__vdx.csv_reader)
    builder.call(yfy__ozgzk, [sgpl__yibgt.pyobj])
    builder.store(context.get_constant(types.uint64, 0), dgyds__vdx.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [bge__ryzkb] = sig.args
    [jzv__xxa] = args
    dgyds__vdx = cgutils.create_struct_proxy(bge__ryzkb)(context, builder,
        value=jzv__xxa)
    pru__czk = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()])
    yfy__ozgzk = cgutils.get_or_insert_function(builder.module, pru__czk,
        name='update_csv_reader')
    sgpl__yibgt = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=dgyds__vdx.csv_reader)
    dghqm__mris = builder.call(yfy__ozgzk, [sgpl__yibgt.pyobj])
    result.set_valid(dghqm__mris)
    with builder.if_then(dghqm__mris):
        nxfki__wtt = builder.load(dgyds__vdx.index)
        spb__oahhh = types.Tuple([sig.return_type.first_type, types.int64])
        oyl__hjn = gen_read_csv_objmode(sig.args[0])
        uaz__fcye = signature(spb__oahhh, types.stream_reader_type, types.int64
            )
        oxk__eoxzh = context.compile_internal(builder, oyl__hjn, uaz__fcye,
            [dgyds__vdx.csv_reader, nxfki__wtt])
        rrhic__sns, vnpm__vncw = cgutils.unpack_tuple(builder, oxk__eoxzh)
        wpp__cdx = builder.add(nxfki__wtt, vnpm__vncw, flags=['nsw'])
        builder.store(wpp__cdx, dgyds__vdx.index)
        result.yield_(rrhic__sns)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        zxuc__fjgxq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        zxuc__fjgxq.csv_reader = args[0]
        zedew__xvcs = context.get_constant(types.uintp, 0)
        zxuc__fjgxq.index = cgutils.alloca_once_value(builder, zedew__xvcs)
        return zxuc__fjgxq._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    ppy__uwyt = csv_iterator_typeref.instance_type
    sig = signature(ppy__uwyt, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    dpd__kxs = 'def read_csv_objmode(f_reader):\n'
    hgp__stu = [sanitize_varname(zopg__lwzgp) for zopg__lwzgp in
        csv_iterator_type._out_colnames]
    aforx__mjl = ir_utils.next_label()
    hgxn__tqz = globals()
    out_types = csv_iterator_type._out_types
    hgxn__tqz[f'table_type_{aforx__mjl}'] = TableType(tuple(out_types))
    hgxn__tqz[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    eewb__exp = list(range(len(csv_iterator_type._usecols)))
    dpd__kxs += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        hgp__stu, out_types, csv_iterator_type._usecols, eewb__exp,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, aforx__mjl, hgxn__tqz, parallel
        =False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    zlw__opgdv = bodo.ir.csv_ext._gen_parallel_flag_name(hgp__stu)
    bwutk__rhwr = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [zlw__opgdv]
    dpd__kxs += f"  return {', '.join(bwutk__rhwr)}"
    hgxn__tqz = globals()
    zzwm__wsdx = {}
    exec(dpd__kxs, hgxn__tqz, zzwm__wsdx)
    hhgv__nsqrj = zzwm__wsdx['read_csv_objmode']
    ccuw__frk = numba.njit(hhgv__nsqrj)
    bodo.ir.csv_ext.compiled_funcs.append(ccuw__frk)
    eext__paou = 'def read_func(reader, local_start):\n'
    eext__paou += f"  {', '.join(bwutk__rhwr)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        eext__paou += f'  local_len = len(T)\n'
        eext__paou += '  total_size = local_len\n'
        eext__paou += f'  if ({zlw__opgdv}):\n'
        eext__paou += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        eext__paou += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        uqvk__qdk = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        eext__paou += '  total_size = 0\n'
        uqvk__qdk = (
            f'bodo.utils.conversion.convert_to_index({bwutk__rhwr[1]}, {csv_iterator_type._index_name!r})'
            )
    eext__paou += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({bwutk__rhwr[0]},), {uqvk__qdk}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(eext__paou, {'bodo': bodo, 'objmode_func': ccuw__frk, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, zzwm__wsdx)
    return zzwm__wsdx['read_func']
