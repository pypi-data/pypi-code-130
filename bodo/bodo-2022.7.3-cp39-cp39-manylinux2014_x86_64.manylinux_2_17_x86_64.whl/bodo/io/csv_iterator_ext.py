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
        vzskf__wxm = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(vzskf__wxm)
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
        evhfx__otoey = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, evhfx__otoey)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    kzkj__fulzv = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    hkfp__xnhhz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    euc__wyyg = cgutils.get_or_insert_function(builder.module, hkfp__xnhhz,
        name='initialize_csv_reader')
    vxq__tvpkb = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=kzkj__fulzv.csv_reader)
    builder.call(euc__wyyg, [vxq__tvpkb.pyobj])
    builder.store(context.get_constant(types.uint64, 0), kzkj__fulzv.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [gsl__vitwg] = sig.args
    [srn__lss] = args
    kzkj__fulzv = cgutils.create_struct_proxy(gsl__vitwg)(context, builder,
        value=srn__lss)
    hkfp__xnhhz = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    euc__wyyg = cgutils.get_or_insert_function(builder.module, hkfp__xnhhz,
        name='update_csv_reader')
    vxq__tvpkb = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=kzkj__fulzv.csv_reader)
    cezo__kzent = builder.call(euc__wyyg, [vxq__tvpkb.pyobj])
    result.set_valid(cezo__kzent)
    with builder.if_then(cezo__kzent):
        fyrjg__idy = builder.load(kzkj__fulzv.index)
        cqor__oag = types.Tuple([sig.return_type.first_type, types.int64])
        dbhi__ouq = gen_read_csv_objmode(sig.args[0])
        efhmm__etrs = signature(cqor__oag, types.stream_reader_type, types.
            int64)
        zudfe__aqc = context.compile_internal(builder, dbhi__ouq,
            efhmm__etrs, [kzkj__fulzv.csv_reader, fyrjg__idy])
        vrjb__ayqbh, xllb__nmfm = cgutils.unpack_tuple(builder, zudfe__aqc)
        skkp__dmytf = builder.add(fyrjg__idy, xllb__nmfm, flags=['nsw'])
        builder.store(skkp__dmytf, kzkj__fulzv.index)
        result.yield_(vrjb__ayqbh)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        srv__sibmf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        srv__sibmf.csv_reader = args[0]
        hiqh__rfs = context.get_constant(types.uintp, 0)
        srv__sibmf.index = cgutils.alloca_once_value(builder, hiqh__rfs)
        return srv__sibmf._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    zij__snm = csv_iterator_typeref.instance_type
    sig = signature(zij__snm, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    qux__jwr = 'def read_csv_objmode(f_reader):\n'
    mhha__fhpd = [sanitize_varname(wvlij__mgsgl) for wvlij__mgsgl in
        csv_iterator_type._out_colnames]
    pdocl__syucx = ir_utils.next_label()
    yvyb__gjknh = globals()
    out_types = csv_iterator_type._out_types
    yvyb__gjknh[f'table_type_{pdocl__syucx}'] = TableType(tuple(out_types))
    yvyb__gjknh[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    fei__zbdpl = list(range(len(csv_iterator_type._usecols)))
    qux__jwr += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        mhha__fhpd, out_types, csv_iterator_type._usecols, fei__zbdpl,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, pdocl__syucx, yvyb__gjknh,
        parallel=False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    yead__urhy = bodo.ir.csv_ext._gen_parallel_flag_name(mhha__fhpd)
    owb__rmg = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [yead__urhy]
    qux__jwr += f"  return {', '.join(owb__rmg)}"
    yvyb__gjknh = globals()
    zquj__zwmu = {}
    exec(qux__jwr, yvyb__gjknh, zquj__zwmu)
    tnl__cspha = zquj__zwmu['read_csv_objmode']
    sueb__pgte = numba.njit(tnl__cspha)
    bodo.ir.csv_ext.compiled_funcs.append(sueb__pgte)
    eyms__ugd = 'def read_func(reader, local_start):\n'
    eyms__ugd += f"  {', '.join(owb__rmg)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        eyms__ugd += f'  local_len = len(T)\n'
        eyms__ugd += '  total_size = local_len\n'
        eyms__ugd += f'  if ({yead__urhy}):\n'
        eyms__ugd += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        eyms__ugd += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        xxmyv__hggyo = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        eyms__ugd += '  total_size = 0\n'
        xxmyv__hggyo = (
            f'bodo.utils.conversion.convert_to_index({owb__rmg[1]}, {csv_iterator_type._index_name!r})'
            )
    eyms__ugd += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({owb__rmg[0]},), {xxmyv__hggyo}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(eyms__ugd, {'bodo': bodo, 'objmode_func': sueb__pgte, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, zquj__zwmu)
    return zquj__zwmu['read_func']
