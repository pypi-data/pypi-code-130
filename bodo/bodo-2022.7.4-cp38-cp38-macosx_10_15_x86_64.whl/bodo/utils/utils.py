"""
Collection of utility functions. Needs to be refactored in separate files.
"""
import hashlib
import inspect
import keyword
import re
import warnings
from enum import Enum
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir, ir_utils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.ir_utils import find_callname, find_const, get_definition, guard, mk_unique_var, require
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload
from numba.np.arrayobj import get_itemsize, make_array, populate_array
from numba.np.numpy_support import as_dtype
import bodo
from bodo.hiframes.time_ext import TimeArrayType
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import num_total_chars, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import NOT_CONSTANT, BodoError, BodoWarning, MetaType, is_str_arr_type
int128_type = types.Integer('int128', 128)


class CTypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Date = 13
    Time = 14
    Datetime = 15
    Timedelta = 16
    Int128 = 17
    LIST = 19
    STRUCT = 20
    BINARY = 21


_numba_to_c_type_map = {types.int8: CTypeEnum.Int8.value, types.uint8:
    CTypeEnum.UInt8.value, types.int32: CTypeEnum.Int32.value, types.uint32:
    CTypeEnum.UInt32.value, types.int64: CTypeEnum.Int64.value, types.
    uint64: CTypeEnum.UInt64.value, types.float32: CTypeEnum.Float32.value,
    types.float64: CTypeEnum.Float64.value, types.NPDatetime('ns'):
    CTypeEnum.Datetime.value, types.NPTimedelta('ns'): CTypeEnum.Timedelta.
    value, types.bool_: CTypeEnum.Bool.value, types.int16: CTypeEnum.Int16.
    value, types.uint16: CTypeEnum.UInt16.value, int128_type: CTypeEnum.
    Int128.value}
numba.core.errors.error_extras = {'unsupported_error': '', 'typing': '',
    'reportable': '', 'interpreter': '', 'constant_inference': ''}
np_alloc_callnames = 'empty', 'zeros', 'ones', 'full'
CONST_DICT_SLOW_WARN_THRESHOLD = 100
CONST_LIST_SLOW_WARN_THRESHOLD = 100000


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


def get_constant(func_ir, var, default=NOT_CONSTANT):
    mknac__vccc = guard(get_definition, func_ir, var)
    if mknac__vccc is None:
        return default
    if isinstance(mknac__vccc, ir.Const):
        return mknac__vccc.value
    if isinstance(mknac__vccc, ir.Var):
        return get_constant(func_ir, mknac__vccc, default)
    return default


def numba_to_c_type(t):
    if isinstance(t, bodo.libs.decimal_arr_ext.Decimal128Type):
        return CTypeEnum.Decimal.value
    if t == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return CTypeEnum.Date.value
    if isinstance(t, bodo.hiframes.time_ext.TimeType):
        return CTypeEnum.Time.value
    return _numba_to_c_type_map[t]


def is_alloc_callname(func_name, mod_name):
    return isinstance(mod_name, str) and (mod_name == 'numpy' and func_name in
        np_alloc_callnames or func_name == 'empty_inferred' and mod_name in
        ('numba.extending', 'numba.np.unsafe.ndarray') or func_name ==
        'pre_alloc_string_array' and mod_name == 'bodo.libs.str_arr_ext' or
        func_name == 'pre_alloc_binary_array' and mod_name ==
        'bodo.libs.binary_arr_ext' or func_name ==
        'alloc_random_access_string_array' and mod_name ==
        'bodo.libs.str_ext' or func_name == 'pre_alloc_array_item_array' and
        mod_name == 'bodo.libs.array_item_arr_ext' or func_name ==
        'pre_alloc_struct_array' and mod_name == 'bodo.libs.struct_arr_ext' or
        func_name == 'pre_alloc_map_array' and mod_name ==
        'bodo.libs.map_arr_ext' or func_name == 'pre_alloc_tuple_array' and
        mod_name == 'bodo.libs.tuple_arr_ext' or func_name ==
        'alloc_bool_array' and mod_name == 'bodo.libs.bool_arr_ext' or 
        func_name == 'alloc_int_array' and mod_name ==
        'bodo.libs.int_arr_ext' or func_name == 'alloc_datetime_date_array' and
        mod_name == 'bodo.hiframes.datetime_date_ext' or func_name ==
        'alloc_datetime_timedelta_array' and mod_name ==
        'bodo.hiframes.datetime_timedelta_ext' or func_name ==
        'alloc_decimal_array' and mod_name == 'bodo.libs.decimal_arr_ext' or
        func_name == 'alloc_categorical_array' and mod_name ==
        'bodo.hiframes.pd_categorical_ext' or func_name == 'gen_na_array' and
        mod_name == 'bodo.libs.array_kernels')


def find_build_tuple(func_ir, var):
    require(isinstance(var, (ir.Var, str)))
    grz__uhh = get_definition(func_ir, var)
    require(isinstance(grz__uhh, ir.Expr))
    require(grz__uhh.op == 'build_tuple')
    return grz__uhh.items


def cprint(*s):
    print(*s)


@infer_global(cprint)
class CprintInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.none, *unliteral_all(args))


typ_to_format = {types.int32: 'd', types.uint32: 'u', types.int64: 'lld',
    types.uint64: 'llu', types.float32: 'f', types.float64: 'lf', types.
    voidptr: 's'}


@lower_builtin(cprint, types.VarArg(types.Any))
def cprint_lower(context, builder, sig, args):
    for yrn__cbhli, val in enumerate(args):
        typ = sig.args[yrn__cbhli]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        hkj__wajo = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(hkj__wajo), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    wsn__mtn = get_definition(func_ir, var)
    require(isinstance(wsn__mtn, ir.Expr) and wsn__mtn.op == 'call')
    assert len(wsn__mtn.args) == 2 or accept_stride and len(wsn__mtn.args) == 3
    assert find_callname(func_ir, wsn__mtn) == ('slice', 'builtins')
    ggxl__gln = get_definition(func_ir, wsn__mtn.args[0])
    kngb__pasf = get_definition(func_ir, wsn__mtn.args[1])
    require(isinstance(ggxl__gln, ir.Const) and ggxl__gln.value == None)
    require(isinstance(kngb__pasf, ir.Const) and kngb__pasf.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    nli__aqp = get_definition(func_ir, index_var)
    require(find_callname(func_ir, nli__aqp) == ('slice', 'builtins'))
    require(len(nli__aqp.args) in (2, 3))
    require(find_const(func_ir, nli__aqp.args[0]) in (0, None))
    require(equiv_set.is_equiv(nli__aqp.args[1], arr_var.name + '#0'))
    require(accept_stride or len(nli__aqp.args) == 2 or find_const(func_ir,
        nli__aqp.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    wsn__mtn = get_definition(func_ir, var)
    require(isinstance(wsn__mtn, ir.Expr) and wsn__mtn.op == 'call')
    assert len(wsn__mtn.args) == 3
    return wsn__mtn.args[2]


def is_array_typ(var_typ, include_index_series=True):
    return is_np_array_typ(var_typ) or var_typ in (string_array_type, bodo.
        binary_array_type, bodo.dict_str_arr_type, bodo.hiframes.split_impl
        .string_array_split_view_type, bodo.hiframes.datetime_date_ext.
        datetime_date_array_type, bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type, boolean_array, bodo.libs.str_ext.
        random_access_string_array, bodo.libs.interval_arr_ext.
        IntervalArrayType) or isinstance(var_typ, (IntegerArrayType, bodo.
        libs.decimal_arr_ext.DecimalArrayType, bodo.hiframes.
        pd_categorical_ext.CategoricalArrayType, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType, bodo.libs.struct_arr_ext.
        StructArrayType, bodo.libs.interval_arr_ext.IntervalArrayType, bodo
        .libs.tuple_arr_ext.TupleArrayType, bodo.libs.map_arr_ext.
        MapArrayType, bodo.libs.csr_matrix_ext.CSRMatrixType, bodo.
        DatetimeArrayType, TimeArrayType)) or include_index_series and (
        isinstance(var_typ, (bodo.hiframes.pd_series_ext.SeriesType, bodo.
        hiframes.pd_multi_index_ext.MultiIndexType)) or bodo.hiframes.
        pd_index_ext.is_pd_index_type(var_typ))


def is_np_array_typ(var_typ):
    return isinstance(var_typ, types.Array)


def is_distributable_typ(var_typ):
    return is_array_typ(var_typ) or isinstance(var_typ, bodo.hiframes.table
        .TableType) or isinstance(var_typ, bodo.hiframes.pd_dataframe_ext.
        DataFrameType) or isinstance(var_typ, types.List
        ) and is_distributable_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_typ(var_typ.value_type)


def is_distributable_tuple_typ(var_typ):
    try:
        from bodosql.context_ext import BodoSQLContextType
    except ImportError as boy__oboqj:
        BodoSQLContextType = None
    return isinstance(var_typ, types.BaseTuple) and any(
        is_distributable_typ(t) or is_distributable_tuple_typ(t) for t in
        var_typ.types) or isinstance(var_typ, types.List
        ) and is_distributable_tuple_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_tuple_typ(var_typ.value_type
        ) or isinstance(var_typ, types.iterators.EnumerateType) and (
        is_distributable_typ(var_typ.yield_type[1]) or
        is_distributable_tuple_typ(var_typ.yield_type[1])
        ) or BodoSQLContextType is not None and isinstance(var_typ,
        BodoSQLContextType) and any([is_distributable_typ(fdjk__kpuik) for
        fdjk__kpuik in var_typ.dataframes])


@numba.generated_jit(nopython=True, cache=True)
def build_set_seen_na(A):

    def impl(A):
        s = dict()
        sni__vlexv = False
        for yrn__cbhli in range(len(A)):
            if bodo.libs.array_kernels.isna(A, yrn__cbhli):
                sni__vlexv = True
                continue
            s[A[yrn__cbhli]] = 0
        return s, sni__vlexv
    return impl


def empty_like_type(n, arr):
    return np.empty(n, arr.dtype)


@overload(empty_like_type, no_unliteral=True)
def empty_like_type_overload(n, arr):
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda n, arr: bodo.hiframes.pd_categorical_ext.
            alloc_categorical_array(n, arr.dtype))
    if isinstance(arr, types.Array):
        return lambda n, arr: np.empty(n, arr.dtype)
    if isinstance(arr, types.List) and arr.dtype == string_type:

        def empty_like_type_str_list(n, arr):
            return [''] * n
        return empty_like_type_str_list
    if isinstance(arr, types.List) and arr.dtype == bytes_type:

        def empty_like_type_binary_list(n, arr):
            return [b''] * n
        return empty_like_type_binary_list
    if isinstance(arr, IntegerArrayType):
        yzgj__ldvf = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, yzgj__ldvf)
        return empty_like_type_int_arr
    if arr == boolean_array:

        def empty_like_type_bool_arr(n, arr):
            return bodo.libs.bool_arr_ext.alloc_bool_array(n)
        return empty_like_type_bool_arr
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def empty_like_type_datetime_date_arr(n, arr):
            return bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(n)
        return empty_like_type_datetime_date_arr
    if isinstance(arr, bodo.hiframes.time_ext.TimeArrayType):

        def empty_like_type_time_arr(n, arr):
            return bodo.hiframes.time_ext.alloc_time_array(n)
        return empty_like_type_time_arr
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def empty_like_type_datetime_timedelta_arr(n, arr):
            return (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(n))
        return empty_like_type_datetime_timedelta_arr
    if isinstance(arr, bodo.libs.decimal_arr_ext.DecimalArrayType):
        precision = arr.precision
        scale = arr.scale

        def empty_like_type_decimal_arr(n, arr):
            return bodo.libs.decimal_arr_ext.alloc_decimal_array(n,
                precision, scale)
        return empty_like_type_decimal_arr
    assert arr == string_array_type

    def empty_like_type_str_arr(n, arr):
        gdnx__shd = 20
        if len(arr) != 0:
            gdnx__shd = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * gdnx__shd)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    rcp__xat = make_array(arrtype)
    uxj__qkiba = rcp__xat(context, builder)
    tow__xpmi = context.get_data_type(arrtype.dtype)
    ruu__jtde = context.get_constant(types.intp, get_itemsize(context, arrtype)
        )
    enh__qic = context.get_constant(types.intp, 1)
    papg__isiun = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        kkd__jxlf = builder.smul_with_overflow(enh__qic, s)
        enh__qic = builder.extract_value(kkd__jxlf, 0)
        papg__isiun = builder.or_(papg__isiun, builder.extract_value(
            kkd__jxlf, 1))
    if arrtype.ndim == 0:
        fleap__zgjk = ()
    elif arrtype.layout == 'C':
        fleap__zgjk = [ruu__jtde]
        for jggri__ccsks in reversed(shapes[1:]):
            fleap__zgjk.append(builder.mul(fleap__zgjk[-1], jggri__ccsks))
        fleap__zgjk = tuple(reversed(fleap__zgjk))
    elif arrtype.layout == 'F':
        fleap__zgjk = [ruu__jtde]
        for jggri__ccsks in shapes[:-1]:
            fleap__zgjk.append(builder.mul(fleap__zgjk[-1], jggri__ccsks))
        fleap__zgjk = tuple(fleap__zgjk)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    stzhv__ixdqw = builder.smul_with_overflow(enh__qic, ruu__jtde)
    brlxr__zgxew = builder.extract_value(stzhv__ixdqw, 0)
    papg__isiun = builder.or_(papg__isiun, builder.extract_value(
        stzhv__ixdqw, 1))
    with builder.if_then(papg__isiun, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    vgp__yjrmr = context.get_preferred_array_alignment(dtype)
    rvh__ttk = context.get_constant(types.uint32, vgp__yjrmr)
    cat__coj = context.nrt.meminfo_alloc_aligned(builder, size=brlxr__zgxew,
        align=rvh__ttk)
    data = context.nrt.meminfo_data(builder, cat__coj)
    ukej__fxpg = context.get_value_type(types.intp)
    nzo__fiks = cgutils.pack_array(builder, shapes, ty=ukej__fxpg)
    jwj__puvy = cgutils.pack_array(builder, fleap__zgjk, ty=ukej__fxpg)
    populate_array(uxj__qkiba, data=builder.bitcast(data, tow__xpmi.
        as_pointer()), shape=nzo__fiks, strides=jwj__puvy, itemsize=
        ruu__jtde, meminfo=cat__coj)
    return uxj__qkiba


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    bytoo__vzkvw = []
    for lky__lsjr in arr_tup:
        bytoo__vzkvw.append(np.empty(n, lky__lsjr.dtype))
    return tuple(bytoo__vzkvw)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    dxgb__nqquf = data.count
    oph__wyzp = ','.join(['empty_like_type(n, data[{}])'.format(yrn__cbhli) for
        yrn__cbhli in range(dxgb__nqquf)])
    if init_vals != ():
        oph__wyzp = ','.join(['np.full(n, init_vals[{}], data[{}].dtype)'.
            format(yrn__cbhli, yrn__cbhli) for yrn__cbhli in range(
            dxgb__nqquf)])
    xhufo__vnjir = 'def f(n, data, init_vals=()):\n'
    xhufo__vnjir += '  return ({}{})\n'.format(oph__wyzp, ',' if 
        dxgb__nqquf == 1 else '')
    suqs__oyu = {}
    exec(xhufo__vnjir, {'empty_like_type': empty_like_type, 'np': np},
        suqs__oyu)
    pdzf__kml = suqs__oyu['f']
    return pdzf__kml


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_to_scalar(n):
    if isinstance(n, types.BaseTuple) and len(n.types) == 1:
        return lambda n: n[0]
    return lambda n: n


def create_categorical_type(categories, data, is_ordered):
    if data == bodo.string_array_type or bodo.utils.typing.is_dtype_nullable(
        data):
        new_cats_arr = pd.CategoricalDtype(pd.array(categories), is_ordered
            ).categories.array
        if isinstance(data.dtype, types.Number):
            new_cats_arr = new_cats_arr.astype(data.
                get_pandas_scalar_type_instance)
    else:
        new_cats_arr = pd.CategoricalDtype(categories, is_ordered
            ).categories.values
        if isinstance(data.dtype, types.Number):
            new_cats_arr = new_cats_arr.astype(as_dtype(data.dtype))
    return new_cats_arr


def alloc_type(n, t, s=None):
    return np.empty(n, t.dtype)


@overload(alloc_type)
def overload_alloc_type(n, t, s=None):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(typ,
        'bodo.alloc_type()')
    if is_str_arr_type(typ):
        return (lambda n, t, s=None: bodo.libs.str_arr_ext.
            pre_alloc_string_array(n, s[0]))
    if typ == bodo.binary_array_type:
        return (lambda n, t, s=None: bodo.libs.binary_arr_ext.
            pre_alloc_binary_array(n, s[0]))
    if isinstance(typ, bodo.libs.array_item_arr_ext.ArrayItemArrayType):
        dtype = typ.dtype
        return (lambda n, t, s=None: bodo.libs.array_item_arr_ext.
            pre_alloc_array_item_array(n, s, dtype))
    if isinstance(typ, bodo.libs.struct_arr_ext.StructArrayType):
        dtypes = typ.data
        names = typ.names
        return (lambda n, t, s=None: bodo.libs.struct_arr_ext.
            pre_alloc_struct_array(n, s, dtypes, names))
    if isinstance(typ, bodo.libs.map_arr_ext.MapArrayType):
        struct_typ = bodo.libs.struct_arr_ext.StructArrayType((typ.
            key_arr_type, typ.value_arr_type), ('key', 'value'))
        return lambda n, t, s=None: bodo.libs.map_arr_ext.pre_alloc_map_array(n
            , s, struct_typ)
    if isinstance(typ, bodo.libs.tuple_arr_ext.TupleArrayType):
        dtypes = typ.data
        return (lambda n, t, s=None: bodo.libs.tuple_arr_ext.
            pre_alloc_tuple_array(n, s, dtypes))
    if isinstance(typ, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        if isinstance(t, types.TypeRef):
            if typ.dtype.categories is None:
                raise BodoError(
                    'UDFs or Groupbys that return Categorical values must have categories known at compile time.'
                    )
            is_ordered = typ.dtype.ordered
            int_type = typ.dtype.int_type
            new_cats_arr = create_categorical_type(typ.dtype.categories,
                typ.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(new_cats_arr))
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, bodo.hiframes.pd_categorical_ext
                .init_cat_dtype(bodo.utils.conversion.index_from_array(
                new_cats_arr), is_ordered, int_type, new_cats_tup)))
        else:
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, t.dtype))
    if typ.dtype == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return (lambda n, t, s=None: bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(n))
    if isinstance(typ.dtype, bodo.hiframes.time_ext.TimeType):
        return lambda n, t, s=None: bodo.hiframes.time_ext.alloc_time_array(n)
    if (typ.dtype == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_type):
        return (lambda n, t, s=None: bodo.hiframes.datetime_timedelta_ext.
            alloc_datetime_timedelta_array(n))
    if isinstance(typ, DecimalArrayType):
        precision = typ.dtype.precision
        scale = typ.dtype.scale
        return (lambda n, t, s=None: bodo.libs.decimal_arr_ext.
            alloc_decimal_array(n, precision, scale))
    dtype = numba.np.numpy_support.as_dtype(typ.dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda n, t, s=None: bodo.libs.int_arr_ext.alloc_int_array(n,
            dtype)
    if typ == boolean_array:
        return lambda n, t, s=None: bodo.libs.bool_arr_ext.alloc_bool_array(n)
    return lambda n, t, s=None: np.empty(n, dtype)


def astype(A, t):
    return A.astype(t.dtype)


@overload(astype, no_unliteral=True)
def overload_astype(A, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    dtype = typ.dtype
    if A == typ:
        return lambda A, t: A
    if isinstance(A, (types.Array, IntegerArrayType)) and isinstance(typ,
        types.Array):
        return lambda A, t: A.astype(dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda A, t: bodo.libs.int_arr_ext.init_integer_array(A.
            astype(dtype), np.full(len(A) + 7 >> 3, 255, np.uint8))
    if (A == bodo.libs.dict_arr_ext.dict_str_arr_type and typ == bodo.
        string_array_type):
        return lambda A, t: bodo.utils.typing.decode_if_dict_array(A)
    raise BodoError(f'cannot convert array type {A} to {typ}')


def full_type(n, val, t):
    return np.full(n, val, t.dtype)


@overload(full_type, no_unliteral=True)
def overload_full_type(n, val, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if isinstance(typ, types.Array):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: np.full(n, val, dtype)
    if isinstance(typ, IntegerArrayType):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: bodo.libs.int_arr_ext.init_integer_array(np
            .full(n, val, dtype), np.full(tuple_to_scalar(n) + 7 >> 3, 255,
            np.uint8))
    if typ == boolean_array:
        return lambda n, val, t: bodo.libs.bool_arr_ext.init_bool_array(np.
            full(n, val, np.bool_), np.full(tuple_to_scalar(n) + 7 >> 3, 
            255, np.uint8))
    if typ == string_array_type:

        def impl_str(n, val, t):
            urek__krjlk = n * bodo.libs.str_arr_ext.get_utf8_size(val)
            A = pre_alloc_string_array(n, urek__krjlk)
            for yrn__cbhli in range(n):
                A[yrn__cbhli] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for yrn__cbhli in range(n):
            A[yrn__cbhli] = val
        return A
    return impl


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        ugc__tkxbo, = args
        yswo__upg = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', ugc__tkxbo, yswo__upg)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        wczpz__kqgrr = cgutils.alloca_once_value(builder, val)
        gzx__hwqu = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, wczpz__kqgrr, gzx__hwqu)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'tuple_list_to_array()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(elem_type,
        'tuple_list_to_array()')
    xhufo__vnjir = 'def impl(A, data, elem_type):\n'
    xhufo__vnjir += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        xhufo__vnjir += (
            '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n')
    else:
        xhufo__vnjir += '    A[i] = d\n'
    suqs__oyu = {}
    exec(xhufo__vnjir, {'bodo': bodo}, suqs__oyu)
    impl = suqs__oyu['impl']
    return impl


def object_length(c, obj):
    urehp__spzz = c.context.get_argument_type(types.pyobject)
    yuvm__vcnav = lir.FunctionType(lir.IntType(64), [urehp__spzz])
    keg__eaya = cgutils.get_or_insert_function(c.builder.module,
        yuvm__vcnav, name='PyObject_Length')
    return c.builder.call(keg__eaya, (obj,))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        iljty__tzk, = args
        context.nrt.incref(builder, signature.args[0], iljty__tzk)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    fut__mji = out_var.loc
    qnb__oqiix = ir.Expr.static_getitem(in_var, ind, None, fut__mji)
    calltypes[qnb__oqiix] = None
    nodes.append(ir.Assign(qnb__oqiix, out_var, fut__mji))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            vog__xundj = types.literal(node.index)
        except:
            vog__xundj = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = vog__xundj
        nodes.append(ir.Assign(ir.Const(node.index, node.loc), index_var,
            node.loc))
    return index_var


import copy
ir.Const.__deepcopy__ = lambda self, memo: ir.Const(self.value, copy.
    deepcopy(self.loc))


def is_call_assign(stmt):
    return isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
        ) and stmt.value.op == 'call'


def is_call(expr):
    return isinstance(expr, ir.Expr) and expr.op == 'call'


def is_var_assign(inst):
    return isinstance(inst, ir.Assign) and isinstance(inst.value, ir.Var)


def is_assign(inst):
    return isinstance(inst, ir.Assign)


def is_expr(val, op):
    return isinstance(val, ir.Expr) and val.op == op


def sanitize_varname(varname):
    if isinstance(varname, (tuple, list)):
        varname = '_'.join(sanitize_varname(v) for v in varname)
    varname = str(varname)
    zparb__zzn = re.sub('\\W+', '_', varname)
    if not zparb__zzn or not zparb__zzn[0].isalpha():
        zparb__zzn = '_' + zparb__zzn
    if not zparb__zzn.isidentifier() or keyword.iskeyword(zparb__zzn):
        zparb__zzn = mk_unique_var('new_name').replace('.', '_')
    return zparb__zzn


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            kmex__emzy = len(A)
            for yrn__cbhli in range(kmex__emzy):
                yield A[kmex__emzy - 1 - yrn__cbhli]
        return impl_reversed


@numba.njit
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit
def nanvar_ddof1(a):
    uzm__gaj = count_nonnan(a)
    if uzm__gaj <= 1:
        return np.nan
    return np.nanvar(a) * (uzm__gaj / (uzm__gaj - 1))


@numba.njit
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as boy__oboqj:
        yqj__kqfka = False
    else:
        yqj__kqfka = h5py.version.hdf5_version_tuple[1] in (10, 12)
    return yqj__kqfka


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as boy__oboqj:
        tffz__imi = False
    else:
        tffz__imi = True
    return tffz__imi


def has_scipy():
    try:
        import scipy
    except ImportError as boy__oboqj:
        hntb__ypzi = False
    else:
        hntb__ypzi = True
    return hntb__ypzi


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        pjpw__drkf = context.get_python_api(builder)
        ubdn__ijjh = pjpw__drkf.err_occurred()
        idqo__tmhtp = cgutils.is_not_null(builder, ubdn__ijjh)
        with builder.if_then(idqo__tmhtp):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    pjpw__drkf = context.get_python_api(builder)
    ubdn__ijjh = pjpw__drkf.err_occurred()
    idqo__tmhtp = cgutils.is_not_null(builder, ubdn__ijjh)
    with builder.if_then(idqo__tmhtp):
        builder.ret(numba.core.callconv.RETCODE_EXC)


@numba.njit
def check_java_installation(fname):
    with numba.objmode():
        check_java_installation_(fname)


def check_java_installation_(fname):
    if not fname.startswith('hdfs://'):
        return
    import shutil
    if not shutil.which('java'):
        xdtpz__hpf = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install 'openjdk>=9.0,<12' -c conda-forge'."
            )
        raise BodoError(xdtpz__hpf)


dt_err = """
        If you are trying to set NULL values for timedelta64 in regular Python, 

        consider using np.timedelta64('nat') instead of None
        """


@lower_constant(types.List)
def lower_constant_list(context, builder, typ, pyval):
    if len(pyval) > CONST_LIST_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global lists can result in long compilation times. Please pass large lists as arguments to JIT functions or use arrays.'
            ))
    oknkq__ccac = []
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in list must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
        oknkq__ccac.append(context.get_constant_generic(builder, typ.dtype, a))
    mwu__tmkn = context.get_constant_generic(builder, types.int64, len(pyval))
    bphen__uir = context.get_constant_generic(builder, types.bool_, False)
    gycpf__kib = context.get_constant_null(types.pyobject)
    tcczs__yptk = lir.Constant.literal_struct([mwu__tmkn, mwu__tmkn,
        bphen__uir] + oknkq__ccac)
    tcczs__yptk = cgutils.global_constant(builder, '.const.payload',
        tcczs__yptk).bitcast(cgutils.voidptr_t)
    vya__hiiw = context.get_constant(types.int64, -1)
    twi__uts = context.get_constant_null(types.voidptr)
    cat__coj = lir.Constant.literal_struct([vya__hiiw, twi__uts, twi__uts,
        tcczs__yptk, vya__hiiw])
    cat__coj = cgutils.global_constant(builder, '.const.meminfo', cat__coj
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([cat__coj, gycpf__kib])


@lower_constant(types.Set)
def lower_constant_set(context, builder, typ, pyval):
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in set must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
    tqymp__mviv = types.List(typ.dtype)
    mswzo__shfr = context.get_constant_generic(builder, tqymp__mviv, list(
        pyval))
    ezbra__fabqr = context.compile_internal(builder, lambda l: set(l),
        types.Set(typ.dtype)(tqymp__mviv), [mswzo__shfr])
    return ezbra__fabqr


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    raoyw__bcge = pd.Series(pyval.keys()).values
    zou__caqht = pd.Series(pyval.values()).values
    biacn__gxeqh = bodo.typeof(raoyw__bcge)
    ozx__qkgf = bodo.typeof(zou__caqht)
    require(biacn__gxeqh.dtype == typ.key_type or can_replace(typ.key_type,
        biacn__gxeqh.dtype))
    require(ozx__qkgf.dtype == typ.value_type or can_replace(typ.value_type,
        ozx__qkgf.dtype))
    izi__bgi = context.get_constant_generic(builder, biacn__gxeqh, raoyw__bcge)
    tqgks__jgy = context.get_constant_generic(builder, ozx__qkgf, zou__caqht)

    def create_dict(keys, vals):
        nyl__kmsac = {}
        for k, v in zip(keys, vals):
            nyl__kmsac[k] = v
        return nyl__kmsac
    wltyy__bxp = context.compile_internal(builder, create_dict, typ(
        biacn__gxeqh, ozx__qkgf), [izi__bgi, tqgks__jgy])
    return wltyy__bxp


@lower_constant(types.DictType)
def lower_constant_dict(context, builder, typ, pyval):
    try:
        return lower_const_dict_fast_path(context, builder, typ, pyval)
    except:
        pass
    if len(pyval) > CONST_DICT_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global dictionaries can result in long compilation times. Please pass large dictionaries as arguments to JIT functions.'
            ))
    kio__ospco = typ.key_type
    ielpw__pnp = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(kio__ospco, ielpw__pnp)
    wltyy__bxp = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        sxnta__kmxya = context.get_constant_generic(builder, kio__ospco, k)
        qeb__rjt = context.get_constant_generic(builder, ielpw__pnp, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            kio__ospco, ielpw__pnp), [wltyy__bxp, sxnta__kmxya, qeb__rjt])
    return wltyy__bxp


def synchronize_error(exception_str, error_message):
    if exception_str == 'ValueError':
        ihyt__jobdl = ValueError
    else:
        ihyt__jobdl = RuntimeError
    nml__ascky = MPI.COMM_WORLD
    if nml__ascky.allreduce(error_message != '', op=MPI.LOR):
        for error_message in nml__ascky.allgather(error_message):
            if error_message:
                raise ihyt__jobdl(error_message)


@numba.njit
def synchronize_error_njit(exception_str, error_message):
    with numba.objmode():
        synchronize_error(exception_str, error_message)
