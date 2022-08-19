"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.np.arrayobj import _getitem_array_single_int
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.hiframes.time_ext import TimeArrayType
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType, PandasDatetimeTZDtype
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
ll.add_symbol('is_np_array', hstr_ext.is_np_array)
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20
_use_dict_str_type = False


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    lhbm__qaoh = tuple(val.columns.to_list())
    cnb__rhf = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        csgp__zmw = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        csgp__zmw = numba.typeof(val.index)
    mmwx__sbp = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    ikm__kbxd = len(cnb__rhf) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(cnb__rhf, csgp__zmw, lhbm__qaoh, mmwx__sbp,
        is_table_format=ikm__kbxd)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    mmwx__sbp = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        kebt__ojq = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        kebt__ojq = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    fxv__xso = dtype_to_array_type(dtype)
    if _use_dict_str_type and fxv__xso == string_array_type:
        fxv__xso = bodo.dict_str_arr_type
    return SeriesType(dtype, data=fxv__xso, index=kebt__ojq, name_typ=numba
        .typeof(val.name), dist=mmwx__sbp)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    ihwhu__uvwco = c.pyapi.object_getattr_string(val, 'index')
    qqbgm__dsm = c.pyapi.to_native_value(typ.index, ihwhu__uvwco).value
    c.pyapi.decref(ihwhu__uvwco)
    if typ.is_table_format:
        fvok__bbajo = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        fvok__bbajo.parent = val
        for rbz__zivyg, ufga__zji in typ.table_type.type_to_blk.items():
            lpcdv__mfd = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[ufga__zji]))
            kda__eiyy, hltyn__iptnc = ListInstance.allocate_ex(c.context, c
                .builder, types.List(rbz__zivyg), lpcdv__mfd)
            hltyn__iptnc.size = lpcdv__mfd
            setattr(fvok__bbajo, f'block_{ufga__zji}', hltyn__iptnc.value)
        rijf__dkxb = c.pyapi.call_method(val, '__len__', ())
        lcv__lrg = c.pyapi.long_as_longlong(rijf__dkxb)
        c.pyapi.decref(rijf__dkxb)
        fvok__bbajo.len = lcv__lrg
        mql__jwino = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [fvok__bbajo._getvalue()])
    else:
        iamw__ukbwq = [c.context.get_constant_null(rbz__zivyg) for
            rbz__zivyg in typ.data]
        mql__jwino = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            iamw__ukbwq)
    xlbl__lpf = construct_dataframe(c.context, c.builder, typ, mql__jwino,
        qqbgm__dsm, val, None)
    return NativeValue(xlbl__lpf)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        hkmlw__dwbo = df._bodo_meta['type_metadata'][1]
    else:
        hkmlw__dwbo = [None] * len(df.columns)
    roc__dryy = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=hkmlw__dwbo[i])) for i in range(len(df.columns))]
    roc__dryy = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        rbz__zivyg == string_array_type else rbz__zivyg) for rbz__zivyg in
        roc__dryy]
    return tuple(roc__dryy)


class SeriesDtypeEnum(Enum):
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
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    egl__ozb, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(egl__ozb) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {egl__ozb}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        yhdu__sbvha, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return yhdu__sbvha, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        yhdu__sbvha, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return yhdu__sbvha, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        aog__xzdr = typ_enum_list[1]
        rwe__szujk = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(aog__xzdr, rwe__szujk)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        moep__psq = typ_enum_list[1]
        vxwsc__yris = tuple(typ_enum_list[2:2 + moep__psq])
        inopd__oyn = typ_enum_list[2 + moep__psq:]
        zur__vgnd = []
        for i in range(moep__psq):
            inopd__oyn, qxb__edtdd = _dtype_from_type_enum_list_recursor(
                inopd__oyn)
            zur__vgnd.append(qxb__edtdd)
        return inopd__oyn, StructType(tuple(zur__vgnd), vxwsc__yris)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hnupn__kqjul = typ_enum_list[1]
        inopd__oyn = typ_enum_list[2:]
        return inopd__oyn, hnupn__kqjul
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hnupn__kqjul = typ_enum_list[1]
        inopd__oyn = typ_enum_list[2:]
        return inopd__oyn, numba.types.literal(hnupn__kqjul)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        inopd__oyn, pmyz__ysgu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        inopd__oyn, iktjb__pus = _dtype_from_type_enum_list_recursor(inopd__oyn
            )
        inopd__oyn, bdieg__ytqgq = _dtype_from_type_enum_list_recursor(
            inopd__oyn)
        inopd__oyn, trxe__ykdkv = _dtype_from_type_enum_list_recursor(
            inopd__oyn)
        inopd__oyn, ted__nnf = _dtype_from_type_enum_list_recursor(inopd__oyn)
        return inopd__oyn, PDCategoricalDtype(pmyz__ysgu, iktjb__pus,
            bdieg__ytqgq, trxe__ykdkv, ted__nnf)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return inopd__oyn, DatetimeIndexType(rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        inopd__oyn, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(inopd__oyn
            )
        inopd__oyn, trxe__ykdkv = _dtype_from_type_enum_list_recursor(
            inopd__oyn)
        return inopd__oyn, NumericIndexType(dtype, rkjcj__abe, trxe__ykdkv)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        inopd__oyn, bss__pqjmt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(inopd__oyn
            )
        return inopd__oyn, PeriodIndexType(bss__pqjmt, rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        inopd__oyn, trxe__ykdkv = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(inopd__oyn
            )
        return inopd__oyn, CategoricalIndexType(trxe__ykdkv, rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return inopd__oyn, RangeIndexType(rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return inopd__oyn, StringIndexType(rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return inopd__oyn, BinaryIndexType(rkjcj__abe)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        inopd__oyn, rkjcj__abe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return inopd__oyn, TimedeltaIndexType(rkjcj__abe)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        gxqz__ezoa = get_overload_const_int(typ)
        if numba.types.maybe_literal(gxqz__ezoa) == typ:
            return [SeriesDtypeEnum.LiteralType.value, gxqz__ezoa]
    elif is_overload_constant_str(typ):
        gxqz__ezoa = get_overload_const_str(typ)
        if numba.types.maybe_literal(gxqz__ezoa) == typ:
            return [SeriesDtypeEnum.LiteralType.value, gxqz__ezoa]
    elif is_overload_constant_bool(typ):
        gxqz__ezoa = get_overload_const_bool(typ)
        if numba.types.maybe_literal(gxqz__ezoa) == typ:
            return [SeriesDtypeEnum.LiteralType.value, gxqz__ezoa]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        pidap__qkq = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for vjo__ryylt in typ.names:
            pidap__qkq.append(vjo__ryylt)
        for euraw__azvp in typ.data:
            pidap__qkq += _dtype_to_type_enum_list_recursor(euraw__azvp)
        return pidap__qkq
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        bbgos__fxb = _dtype_to_type_enum_list_recursor(typ.categories)
        sazg__whz = _dtype_to_type_enum_list_recursor(typ.elem_type)
        lcyc__hoeo = _dtype_to_type_enum_list_recursor(typ.ordered)
        ltlzn__inm = _dtype_to_type_enum_list_recursor(typ.data)
        pcc__xleai = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + bbgos__fxb + sazg__whz + lcyc__hoeo + ltlzn__inm + pcc__xleai
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                mhjf__jbhp = types.float64
                tygqb__ssqpd = types.Array(mhjf__jbhp, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                mhjf__jbhp = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    tygqb__ssqpd = IntegerArrayType(mhjf__jbhp)
                else:
                    tygqb__ssqpd = types.Array(mhjf__jbhp, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                mhjf__jbhp = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    tygqb__ssqpd = IntegerArrayType(mhjf__jbhp)
                else:
                    tygqb__ssqpd = types.Array(mhjf__jbhp, 1, 'C')
            elif typ.dtype == types.bool_:
                mhjf__jbhp = typ.dtype
                tygqb__ssqpd = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(mhjf__jbhp
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(tygqb__ssqpd)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0 or S.isna().sum() == len(S):
            if array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
            elif hasattr(S, '_bodo_meta'
                ) and S._bodo_meta is not None and 'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None:
                jut__awiq = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(jut__awiq)
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.floating.FloatingDtype):
        raise BodoError(
            """Bodo does not currently support Series constructed with Pandas FloatingArray.
Please use Series.astype() to convert any input Series input to Bodo JIT functions."""
            )
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        qmhl__qrdad = S.dtype.unit
        if qmhl__qrdad != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        bpy__qixhg = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(bpy__qixhg)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    ede__tud = cgutils.is_not_null(builder, parent_obj)
    lonv__wxufp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(ede__tud):
        bazrm__afj = pyapi.object_getattr_string(parent_obj, 'columns')
        rijf__dkxb = pyapi.call_method(bazrm__afj, '__len__', ())
        builder.store(pyapi.long_as_longlong(rijf__dkxb), lonv__wxufp)
        pyapi.decref(rijf__dkxb)
        pyapi.decref(bazrm__afj)
    use_parent_obj = builder.and_(ede__tud, builder.icmp_unsigned('==',
        builder.load(lonv__wxufp), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        pui__gkbik = df_typ.runtime_colname_typ
        context.nrt.incref(builder, pui__gkbik, dataframe_payload.columns)
        return pyapi.from_native_value(pui__gkbik, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        ygl__aio = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        ygl__aio = np.array(df_typ.columns, 'int64')
    else:
        ygl__aio = df_typ.columns
    avyl__njwum = numba.typeof(ygl__aio)
    qvvl__rsad = context.get_constant_generic(builder, avyl__njwum, ygl__aio)
    ybex__hyhq = pyapi.from_native_value(avyl__njwum, qvvl__rsad, c.env_manager
        )
    return ybex__hyhq


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (ziz__etr, xiyik__cmihk):
        with ziz__etr:
            pyapi.incref(obj)
            hfkz__yes = context.insert_const_string(c.builder.module, 'numpy')
            sald__vqk = pyapi.import_module_noblock(hfkz__yes)
            if df_typ.has_runtime_cols:
                twjb__ftni = 0
            else:
                twjb__ftni = len(df_typ.columns)
            vkcnp__hblgn = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), twjb__ftni))
            xwbm__ior = pyapi.call_method(sald__vqk, 'arange', (vkcnp__hblgn,))
            pyapi.object_setattr_string(obj, 'columns', xwbm__ior)
            pyapi.decref(sald__vqk)
            pyapi.decref(xwbm__ior)
            pyapi.decref(vkcnp__hblgn)
        with xiyik__cmihk:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            wux__wwq = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            hfkz__yes = context.insert_const_string(c.builder.module, 'pandas')
            sald__vqk = pyapi.import_module_noblock(hfkz__yes)
            df_obj = pyapi.call_method(sald__vqk, 'DataFrame', (pyapi.
                borrow_none(), wux__wwq))
            pyapi.decref(sald__vqk)
            pyapi.decref(wux__wwq)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    ovfd__gmzds = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = ovfd__gmzds.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        skr__tml = typ.table_type
        fvok__bbajo = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, skr__tml, fvok__bbajo)
        tnyh__zwio = box_table(skr__tml, fvok__bbajo, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (gwv__hkmp, uiyli__fkd):
            with gwv__hkmp:
                zogr__hrqpu = pyapi.object_getattr_string(tnyh__zwio, 'arrays')
                relgm__oshrp = c.pyapi.make_none()
                if n_cols is None:
                    rijf__dkxb = pyapi.call_method(zogr__hrqpu, '__len__', ())
                    lpcdv__mfd = pyapi.long_as_longlong(rijf__dkxb)
                    pyapi.decref(rijf__dkxb)
                else:
                    lpcdv__mfd = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, lpcdv__mfd) as bvxs__xdbak:
                    i = bvxs__xdbak.index
                    gjes__xfvv = pyapi.list_getitem(zogr__hrqpu, i)
                    ooms__rgo = c.builder.icmp_unsigned('!=', gjes__xfvv,
                        relgm__oshrp)
                    with builder.if_then(ooms__rgo):
                        duyun__shu = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, duyun__shu, gjes__xfvv)
                        pyapi.decref(duyun__shu)
                pyapi.decref(zogr__hrqpu)
                pyapi.decref(relgm__oshrp)
            with uiyli__fkd:
                df_obj = builder.load(res)
                wux__wwq = pyapi.object_getattr_string(df_obj, 'index')
                jdtty__xvj = c.pyapi.call_method(tnyh__zwio, 'to_pandas', (
                    wux__wwq,))
                builder.store(jdtty__xvj, res)
                pyapi.decref(df_obj)
                pyapi.decref(wux__wwq)
        pyapi.decref(tnyh__zwio)
    else:
        rcd__gcjo = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        nigi__tvcrj = typ.data
        for i, vlyk__xpnvk, fxv__xso in zip(range(n_cols), rcd__gcjo,
            nigi__tvcrj):
            rrsc__wvn = cgutils.alloca_once_value(builder, vlyk__xpnvk)
            jkzvk__rht = cgutils.alloca_once_value(builder, context.
                get_constant_null(fxv__xso))
            ooms__rgo = builder.not_(is_ll_eq(builder, rrsc__wvn, jkzvk__rht))
            vew__dols = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, ooms__rgo))
            with builder.if_then(vew__dols):
                duyun__shu = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, fxv__xso, vlyk__xpnvk)
                arr_obj = pyapi.from_native_value(fxv__xso, vlyk__xpnvk, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, duyun__shu, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(duyun__shu)
    df_obj = builder.load(res)
    ybex__hyhq = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', ybex__hyhq)
    pyapi.decref(ybex__hyhq)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    relgm__oshrp = pyapi.borrow_none()
    oecu__rdri = pyapi.unserialize(pyapi.serialize_object(slice))
    qyv__yihjy = pyapi.call_function_objargs(oecu__rdri, [relgm__oshrp])
    xirq__rha = pyapi.long_from_longlong(col_ind)
    jnrga__xhho = pyapi.tuple_pack([qyv__yihjy, xirq__rha])
    pbo__rymbg = pyapi.object_getattr_string(df_obj, 'iloc')
    gahpz__xbsyd = pyapi.object_getitem(pbo__rymbg, jnrga__xhho)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        zlxb__xabo = pyapi.object_getattr_string(gahpz__xbsyd, 'array')
    else:
        zlxb__xabo = pyapi.object_getattr_string(gahpz__xbsyd, 'values')
    if isinstance(data_typ, types.Array):
        eft__esb = context.insert_const_string(builder.module, 'numpy')
        whax__ifi = pyapi.import_module_noblock(eft__esb)
        arr_obj = pyapi.call_method(whax__ifi, 'ascontiguousarray', (
            zlxb__xabo,))
        pyapi.decref(zlxb__xabo)
        pyapi.decref(whax__ifi)
    else:
        arr_obj = zlxb__xabo
    pyapi.decref(oecu__rdri)
    pyapi.decref(qyv__yihjy)
    pyapi.decref(xirq__rha)
    pyapi.decref(jnrga__xhho)
    pyapi.decref(pbo__rymbg)
    pyapi.decref(gahpz__xbsyd)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        ovfd__gmzds = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            ovfd__gmzds.parent, args[1], data_typ)
        sls__uup = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            fvok__bbajo = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            ufga__zji = df_typ.table_type.type_to_blk[data_typ]
            aurdi__ziaw = getattr(fvok__bbajo, f'block_{ufga__zji}')
            vcr__olcz = ListInstance(c.context, c.builder, types.List(
                data_typ), aurdi__ziaw)
            fnirr__cefj = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            vcr__olcz.inititem(fnirr__cefj, sls__uup.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, sls__uup.value, col_ind)
        pxrdu__hdjii = DataFramePayloadType(df_typ)
        cuyu__htkhv = context.nrt.meminfo_data(builder, ovfd__gmzds.meminfo)
        kvcp__rlg = context.get_value_type(pxrdu__hdjii).as_pointer()
        cuyu__htkhv = builder.bitcast(cuyu__htkhv, kvcp__rlg)
        builder.store(dataframe_payload._getvalue(), cuyu__htkhv)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        zlxb__xabo = c.pyapi.object_getattr_string(val, 'array')
    else:
        zlxb__xabo = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        eft__esb = c.context.insert_const_string(c.builder.module, 'numpy')
        whax__ifi = c.pyapi.import_module_noblock(eft__esb)
        arr_obj = c.pyapi.call_method(whax__ifi, 'ascontiguousarray', (
            zlxb__xabo,))
        c.pyapi.decref(zlxb__xabo)
        c.pyapi.decref(whax__ifi)
    else:
        arr_obj = zlxb__xabo
    fsdyj__nykm = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    wux__wwq = c.pyapi.object_getattr_string(val, 'index')
    qqbgm__dsm = c.pyapi.to_native_value(typ.index, wux__wwq).value
    ujydh__rab = c.pyapi.object_getattr_string(val, 'name')
    ytz__tzlhu = c.pyapi.to_native_value(typ.name_typ, ujydh__rab).value
    qoyx__obf = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, fsdyj__nykm, qqbgm__dsm, ytz__tzlhu)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(wux__wwq)
    c.pyapi.decref(ujydh__rab)
    return NativeValue(qoyx__obf)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        xjnln__ouf = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(xjnln__ouf._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    hfkz__yes = c.context.insert_const_string(c.builder.module, 'pandas')
    ezwz__xfur = c.pyapi.import_module_noblock(hfkz__yes)
    fcre__yzx = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c
        .builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, fcre__yzx.data)
    c.context.nrt.incref(c.builder, typ.index, fcre__yzx.index)
    c.context.nrt.incref(c.builder, typ.name_typ, fcre__yzx.name)
    arr_obj = c.pyapi.from_native_value(typ.data, fcre__yzx.data, c.env_manager
        )
    wux__wwq = c.pyapi.from_native_value(typ.index, fcre__yzx.index, c.
        env_manager)
    ujydh__rab = c.pyapi.from_native_value(typ.name_typ, fcre__yzx.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(ezwz__xfur, 'Series', (arr_obj, wux__wwq,
        dtype, ujydh__rab))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(wux__wwq)
    c.pyapi.decref(ujydh__rab)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(ezwz__xfur)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    fcc__dvt = []
    for mxq__sdfj in typ_list:
        if isinstance(mxq__sdfj, int) and not isinstance(mxq__sdfj, bool):
            vsxu__hpmn = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), mxq__sdfj))
        else:
            hclb__wzzix = numba.typeof(mxq__sdfj)
            glf__othja = context.get_constant_generic(builder, hclb__wzzix,
                mxq__sdfj)
            vsxu__hpmn = pyapi.from_native_value(hclb__wzzix, glf__othja,
                env_manager)
        fcc__dvt.append(vsxu__hpmn)
    golq__blutd = pyapi.list_pack(fcc__dvt)
    for val in fcc__dvt:
        pyapi.decref(val)
    return golq__blutd


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    jvpzt__tylkj = not typ.has_runtime_cols
    gvt__kyv = 2 if jvpzt__tylkj else 1
    dup__wxa = pyapi.dict_new(gvt__kyv)
    krio__zsrp = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(dup__wxa, 'dist', krio__zsrp)
    pyapi.decref(krio__zsrp)
    if jvpzt__tylkj:
        keca__wsh = _dtype_to_type_enum_list(typ.index)
        if keca__wsh != None:
            tfnhh__sci = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, keca__wsh)
        else:
            tfnhh__sci = pyapi.make_none()
        if typ.is_table_format:
            rbz__zivyg = typ.table_type
            vuo__mdc = pyapi.list_new(lir.Constant(lir.IntType(64), len(typ
                .data)))
            for ufga__zji, dtype in rbz__zivyg.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                lpcdv__mfd = c.context.get_constant(types.int64, len(
                    rbz__zivyg.block_to_arr_ind[ufga__zji]))
                erxn__hvbj = c.context.make_constant_array(c.builder, types
                    .Array(types.int64, 1, 'C'), np.array(rbz__zivyg.
                    block_to_arr_ind[ufga__zji], dtype=np.int64))
                ear__zboc = c.context.make_array(types.Array(types.int64, 1,
                    'C'))(c.context, c.builder, erxn__hvbj)
                with cgutils.for_range(c.builder, lpcdv__mfd) as bvxs__xdbak:
                    i = bvxs__xdbak.index
                    kiu__mxll = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), ear__zboc, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(vuo__mdc, kiu__mxll, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            bvrfg__tmjk = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    golq__blutd = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    golq__blutd = pyapi.make_none()
                bvrfg__tmjk.append(golq__blutd)
            vuo__mdc = pyapi.list_pack(bvrfg__tmjk)
            for val in bvrfg__tmjk:
                pyapi.decref(val)
        cfa__grtkt = pyapi.list_pack([tfnhh__sci, vuo__mdc])
        pyapi.dict_setitem_string(dup__wxa, 'type_metadata', cfa__grtkt)
    pyapi.object_setattr_string(obj, '_bodo_meta', dup__wxa)
    pyapi.decref(dup__wxa)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    dup__wxa = pyapi.dict_new(2)
    krio__zsrp = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    keca__wsh = _dtype_to_type_enum_list(typ.index)
    if keca__wsh != None:
        tfnhh__sci = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, keca__wsh)
    else:
        tfnhh__sci = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            unqw__lpapy = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            unqw__lpapy = pyapi.make_none()
    else:
        unqw__lpapy = pyapi.make_none()
    qii__iwuml = pyapi.list_pack([tfnhh__sci, unqw__lpapy])
    pyapi.dict_setitem_string(dup__wxa, 'type_metadata', qii__iwuml)
    pyapi.decref(qii__iwuml)
    pyapi.dict_setitem_string(dup__wxa, 'dist', krio__zsrp)
    pyapi.object_setattr_string(obj, '_bodo_meta', dup__wxa)
    pyapi.decref(dup__wxa)
    pyapi.decref(krio__zsrp)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as syob__yigzz:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    unwf__goo = numba.np.numpy_support.map_layout(val)
    yhe__hotww = not val.flags.writeable
    return types.Array(dtype, val.ndim, unwf__goo, readonly=yhe__hotww)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    hra__lgwqq = val[i]
    if isinstance(hra__lgwqq, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(hra__lgwqq, bytes):
        return binary_array_type
    elif isinstance(hra__lgwqq, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(hra__lgwqq, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(hra__lgwqq))
    elif isinstance(hra__lgwqq, (dict, Dict)) and all(isinstance(
        bqfx__omrvb, str) for bqfx__omrvb in hra__lgwqq.keys()):
        vxwsc__yris = tuple(hra__lgwqq.keys())
        ljb__kphfs = tuple(_get_struct_value_arr_type(v) for v in
            hra__lgwqq.values())
        return StructArrayType(ljb__kphfs, vxwsc__yris)
    elif isinstance(hra__lgwqq, (dict, Dict)):
        jnfdf__oiozz = numba.typeof(_value_to_array(list(hra__lgwqq.keys())))
        pgchh__fpe = numba.typeof(_value_to_array(list(hra__lgwqq.values())))
        jnfdf__oiozz = to_str_arr_if_dict_array(jnfdf__oiozz)
        pgchh__fpe = to_str_arr_if_dict_array(pgchh__fpe)
        return MapArrayType(jnfdf__oiozz, pgchh__fpe)
    elif isinstance(hra__lgwqq, tuple):
        ljb__kphfs = tuple(_get_struct_value_arr_type(v) for v in hra__lgwqq)
        return TupleArrayType(ljb__kphfs)
    if isinstance(hra__lgwqq, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(hra__lgwqq, list):
            hra__lgwqq = _value_to_array(hra__lgwqq)
        euh__qyw = numba.typeof(hra__lgwqq)
        euh__qyw = to_str_arr_if_dict_array(euh__qyw)
        return ArrayItemArrayType(euh__qyw)
    if isinstance(hra__lgwqq, datetime.date):
        return datetime_date_array_type
    if isinstance(hra__lgwqq, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(hra__lgwqq, bodo.Time):
        return TimeArrayType(hra__lgwqq.precision)
    if isinstance(hra__lgwqq, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(hra__lgwqq, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {hra__lgwqq}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    krg__lqf = val.copy()
    krg__lqf.append(None)
    vlyk__xpnvk = np.array(krg__lqf, np.object_)
    if len(val) and isinstance(val[0], float):
        vlyk__xpnvk = np.array(val, np.float64)
    return vlyk__xpnvk


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    fxv__xso = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        fxv__xso = to_nullable_type(fxv__xso)
    return fxv__xso
