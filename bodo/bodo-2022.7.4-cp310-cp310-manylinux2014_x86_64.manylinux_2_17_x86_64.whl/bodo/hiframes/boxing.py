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
    vasn__czu = tuple(val.columns.to_list())
    yxuus__sapi = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        kbv__wrgvv = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        kbv__wrgvv = numba.typeof(val.index)
    fbvdn__ekp = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    tkny__ehp = len(yxuus__sapi) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(yxuus__sapi, kbv__wrgvv, vasn__czu, fbvdn__ekp,
        is_table_format=tkny__ehp)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    fbvdn__ekp = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        aoaj__vgrfd = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        aoaj__vgrfd = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    plo__car = dtype_to_array_type(dtype)
    if _use_dict_str_type and plo__car == string_array_type:
        plo__car = bodo.dict_str_arr_type
    return SeriesType(dtype, data=plo__car, index=aoaj__vgrfd, name_typ=
        numba.typeof(val.name), dist=fbvdn__ekp)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    zziws__hwqex = c.pyapi.object_getattr_string(val, 'index')
    fqmcl__culqv = c.pyapi.to_native_value(typ.index, zziws__hwqex).value
    c.pyapi.decref(zziws__hwqex)
    if typ.is_table_format:
        nlvn__ieaf = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        nlvn__ieaf.parent = val
        for kee__hxl, balm__nsee in typ.table_type.type_to_blk.items():
            jzfs__krfog = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[balm__nsee]))
            pkx__tjhy, zsaq__zzc = ListInstance.allocate_ex(c.context, c.
                builder, types.List(kee__hxl), jzfs__krfog)
            zsaq__zzc.size = jzfs__krfog
            setattr(nlvn__ieaf, f'block_{balm__nsee}', zsaq__zzc.value)
        tbz__blm = c.pyapi.call_method(val, '__len__', ())
        rrq__llcz = c.pyapi.long_as_longlong(tbz__blm)
        c.pyapi.decref(tbz__blm)
        nlvn__ieaf.len = rrq__llcz
        xqr__sqbg = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [nlvn__ieaf._getvalue()])
    else:
        wiwwy__wap = [c.context.get_constant_null(kee__hxl) for kee__hxl in
            typ.data]
        xqr__sqbg = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            wiwwy__wap)
    twrv__vvgpz = construct_dataframe(c.context, c.builder, typ, xqr__sqbg,
        fqmcl__culqv, val, None)
    return NativeValue(twrv__vvgpz)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        omob__ckko = df._bodo_meta['type_metadata'][1]
    else:
        omob__ckko = [None] * len(df.columns)
    pxus__arw = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=omob__ckko[i])) for i in range(len(df.columns))]
    pxus__arw = [(bodo.dict_str_arr_type if _use_dict_str_type and kee__hxl ==
        string_array_type else kee__hxl) for kee__hxl in pxus__arw]
    return tuple(pxus__arw)


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
    cmlct__izk, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(cmlct__izk) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {cmlct__izk}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        bqyf__vmlq, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return bqyf__vmlq, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        bqyf__vmlq, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return bqyf__vmlq, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        kzmni__qyrfh = typ_enum_list[1]
        atl__esgs = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(kzmni__qyrfh, atl__esgs)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        wkq__yrbu = typ_enum_list[1]
        tpv__yhmts = tuple(typ_enum_list[2:2 + wkq__yrbu])
        aln__zhjtz = typ_enum_list[2 + wkq__yrbu:]
        gghk__izi = []
        for i in range(wkq__yrbu):
            aln__zhjtz, ehsdx__okog = _dtype_from_type_enum_list_recursor(
                aln__zhjtz)
            gghk__izi.append(ehsdx__okog)
        return aln__zhjtz, StructType(tuple(gghk__izi), tpv__yhmts)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        jnrtu__xgl = typ_enum_list[1]
        aln__zhjtz = typ_enum_list[2:]
        return aln__zhjtz, jnrtu__xgl
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        jnrtu__xgl = typ_enum_list[1]
        aln__zhjtz = typ_enum_list[2:]
        return aln__zhjtz, numba.types.literal(jnrtu__xgl)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        aln__zhjtz, pui__mgy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        aln__zhjtz, kra__dfoq = _dtype_from_type_enum_list_recursor(aln__zhjtz)
        aln__zhjtz, jtck__juuwl = _dtype_from_type_enum_list_recursor(
            aln__zhjtz)
        aln__zhjtz, yyhr__uqnj = _dtype_from_type_enum_list_recursor(aln__zhjtz
            )
        aln__zhjtz, zexjz__owiy = _dtype_from_type_enum_list_recursor(
            aln__zhjtz)
        return aln__zhjtz, PDCategoricalDtype(pui__mgy, kra__dfoq,
            jtck__juuwl, yyhr__uqnj, zexjz__owiy)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return aln__zhjtz, DatetimeIndexType(lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        aln__zhjtz, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(aln__zhjtz
            )
        aln__zhjtz, yyhr__uqnj = _dtype_from_type_enum_list_recursor(aln__zhjtz
            )
        return aln__zhjtz, NumericIndexType(dtype, lvk__vnwni, yyhr__uqnj)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        aln__zhjtz, aqa__oxumn = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(aln__zhjtz
            )
        return aln__zhjtz, PeriodIndexType(aqa__oxumn, lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        aln__zhjtz, yyhr__uqnj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(aln__zhjtz
            )
        return aln__zhjtz, CategoricalIndexType(yyhr__uqnj, lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return aln__zhjtz, RangeIndexType(lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return aln__zhjtz, StringIndexType(lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return aln__zhjtz, BinaryIndexType(lvk__vnwni)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        aln__zhjtz, lvk__vnwni = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return aln__zhjtz, TimedeltaIndexType(lvk__vnwni)
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
        thbsd__bchd = get_overload_const_int(typ)
        if numba.types.maybe_literal(thbsd__bchd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, thbsd__bchd]
    elif is_overload_constant_str(typ):
        thbsd__bchd = get_overload_const_str(typ)
        if numba.types.maybe_literal(thbsd__bchd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, thbsd__bchd]
    elif is_overload_constant_bool(typ):
        thbsd__bchd = get_overload_const_bool(typ)
        if numba.types.maybe_literal(thbsd__bchd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, thbsd__bchd]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        kiw__zszm = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for kfom__enl in typ.names:
            kiw__zszm.append(kfom__enl)
        for bhicr__jkq in typ.data:
            kiw__zszm += _dtype_to_type_enum_list_recursor(bhicr__jkq)
        return kiw__zszm
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        pncuu__offjr = _dtype_to_type_enum_list_recursor(typ.categories)
        oacfs__fhey = _dtype_to_type_enum_list_recursor(typ.elem_type)
        ccx__amol = _dtype_to_type_enum_list_recursor(typ.ordered)
        vqqm__kmiw = _dtype_to_type_enum_list_recursor(typ.data)
        gwj__brb = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + pncuu__offjr + oacfs__fhey + ccx__amol + vqqm__kmiw + gwj__brb
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                jvxj__vqxx = types.float64
                kjt__cumxj = types.Array(jvxj__vqxx, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                jvxj__vqxx = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    kjt__cumxj = IntegerArrayType(jvxj__vqxx)
                else:
                    kjt__cumxj = types.Array(jvxj__vqxx, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                jvxj__vqxx = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    kjt__cumxj = IntegerArrayType(jvxj__vqxx)
                else:
                    kjt__cumxj = types.Array(jvxj__vqxx, 1, 'C')
            elif typ.dtype == types.bool_:
                jvxj__vqxx = typ.dtype
                kjt__cumxj = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(jvxj__vqxx
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(kjt__cumxj)
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
                szn__ngwzr = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(szn__ngwzr)
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
        kvj__aoaj = S.dtype.unit
        if kvj__aoaj != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        rmr__ehria = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(rmr__ehria)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    tpn__vff = cgutils.is_not_null(builder, parent_obj)
    offc__reuf = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(tpn__vff):
        mom__vttd = pyapi.object_getattr_string(parent_obj, 'columns')
        tbz__blm = pyapi.call_method(mom__vttd, '__len__', ())
        builder.store(pyapi.long_as_longlong(tbz__blm), offc__reuf)
        pyapi.decref(tbz__blm)
        pyapi.decref(mom__vttd)
    use_parent_obj = builder.and_(tpn__vff, builder.icmp_unsigned('==',
        builder.load(offc__reuf), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        wzjwx__fuot = df_typ.runtime_colname_typ
        context.nrt.incref(builder, wzjwx__fuot, dataframe_payload.columns)
        return pyapi.from_native_value(wzjwx__fuot, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        suaw__ljqkg = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        suaw__ljqkg = np.array(df_typ.columns, 'int64')
    else:
        suaw__ljqkg = df_typ.columns
    fvor__augb = numba.typeof(suaw__ljqkg)
    dauv__jpsg = context.get_constant_generic(builder, fvor__augb, suaw__ljqkg)
    qcv__ylvg = pyapi.from_native_value(fvor__augb, dauv__jpsg, c.env_manager)
    return qcv__ylvg


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (seebz__bvt, qpmw__kkt):
        with seebz__bvt:
            pyapi.incref(obj)
            fpzhe__udk = context.insert_const_string(c.builder.module, 'numpy')
            njvb__dwgh = pyapi.import_module_noblock(fpzhe__udk)
            if df_typ.has_runtime_cols:
                xpqt__tor = 0
            else:
                xpqt__tor = len(df_typ.columns)
            vjnv__mwybv = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), xpqt__tor))
            gxvok__cvjd = pyapi.call_method(njvb__dwgh, 'arange', (
                vjnv__mwybv,))
            pyapi.object_setattr_string(obj, 'columns', gxvok__cvjd)
            pyapi.decref(njvb__dwgh)
            pyapi.decref(gxvok__cvjd)
            pyapi.decref(vjnv__mwybv)
        with qpmw__kkt:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            cghw__vpxux = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            fpzhe__udk = context.insert_const_string(c.builder.module, 'pandas'
                )
            njvb__dwgh = pyapi.import_module_noblock(fpzhe__udk)
            df_obj = pyapi.call_method(njvb__dwgh, 'DataFrame', (pyapi.
                borrow_none(), cghw__vpxux))
            pyapi.decref(njvb__dwgh)
            pyapi.decref(cghw__vpxux)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    zmc__lxtp = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = zmc__lxtp.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        qyov__jkfm = typ.table_type
        nlvn__ieaf = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, qyov__jkfm, nlvn__ieaf)
        uez__otf = box_table(qyov__jkfm, nlvn__ieaf, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (hvys__pczv, zuda__gqwam):
            with hvys__pczv:
                ylkdz__lfri = pyapi.object_getattr_string(uez__otf, 'arrays')
                fgv__wbpw = c.pyapi.make_none()
                if n_cols is None:
                    tbz__blm = pyapi.call_method(ylkdz__lfri, '__len__', ())
                    jzfs__krfog = pyapi.long_as_longlong(tbz__blm)
                    pyapi.decref(tbz__blm)
                else:
                    jzfs__krfog = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, jzfs__krfog) as xawzy__ogq:
                    i = xawzy__ogq.index
                    gisuo__mis = pyapi.list_getitem(ylkdz__lfri, i)
                    qjnio__bof = c.builder.icmp_unsigned('!=', gisuo__mis,
                        fgv__wbpw)
                    with builder.if_then(qjnio__bof):
                        fhwfj__txrr = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, fhwfj__txrr, gisuo__mis)
                        pyapi.decref(fhwfj__txrr)
                pyapi.decref(ylkdz__lfri)
                pyapi.decref(fgv__wbpw)
            with zuda__gqwam:
                df_obj = builder.load(res)
                cghw__vpxux = pyapi.object_getattr_string(df_obj, 'index')
                hhzgn__gpk = c.pyapi.call_method(uez__otf, 'to_pandas', (
                    cghw__vpxux,))
                builder.store(hhzgn__gpk, res)
                pyapi.decref(df_obj)
                pyapi.decref(cghw__vpxux)
        pyapi.decref(uez__otf)
    else:
        kxo__piuv = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        upyy__fqgsl = typ.data
        for i, kmm__djmgb, plo__car in zip(range(n_cols), kxo__piuv,
            upyy__fqgsl):
            zogu__ffnx = cgutils.alloca_once_value(builder, kmm__djmgb)
            poj__dik = cgutils.alloca_once_value(builder, context.
                get_constant_null(plo__car))
            qjnio__bof = builder.not_(is_ll_eq(builder, zogu__ffnx, poj__dik))
            pkr__nqq = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, qjnio__bof))
            with builder.if_then(pkr__nqq):
                fhwfj__txrr = pyapi.long_from_longlong(context.get_constant
                    (types.int64, i))
                context.nrt.incref(builder, plo__car, kmm__djmgb)
                arr_obj = pyapi.from_native_value(plo__car, kmm__djmgb, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, fhwfj__txrr, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(fhwfj__txrr)
    df_obj = builder.load(res)
    qcv__ylvg = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', qcv__ylvg)
    pyapi.decref(qcv__ylvg)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    fgv__wbpw = pyapi.borrow_none()
    dnf__ipow = pyapi.unserialize(pyapi.serialize_object(slice))
    nohs__dfcsv = pyapi.call_function_objargs(dnf__ipow, [fgv__wbpw])
    fjrs__xxmak = pyapi.long_from_longlong(col_ind)
    jzu__sbj = pyapi.tuple_pack([nohs__dfcsv, fjrs__xxmak])
    ots__wbka = pyapi.object_getattr_string(df_obj, 'iloc')
    hse__ndpa = pyapi.object_getitem(ots__wbka, jzu__sbj)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        qxk__maxix = pyapi.object_getattr_string(hse__ndpa, 'array')
    else:
        qxk__maxix = pyapi.object_getattr_string(hse__ndpa, 'values')
    if isinstance(data_typ, types.Array):
        ammz__gbsro = context.insert_const_string(builder.module, 'numpy')
        kbg__tvo = pyapi.import_module_noblock(ammz__gbsro)
        arr_obj = pyapi.call_method(kbg__tvo, 'ascontiguousarray', (
            qxk__maxix,))
        pyapi.decref(qxk__maxix)
        pyapi.decref(kbg__tvo)
    else:
        arr_obj = qxk__maxix
    pyapi.decref(dnf__ipow)
    pyapi.decref(nohs__dfcsv)
    pyapi.decref(fjrs__xxmak)
    pyapi.decref(jzu__sbj)
    pyapi.decref(ots__wbka)
    pyapi.decref(hse__ndpa)
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
        zmc__lxtp = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            zmc__lxtp.parent, args[1], data_typ)
        gafuh__cie = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            nlvn__ieaf = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            balm__nsee = df_typ.table_type.type_to_blk[data_typ]
            snzhe__sbx = getattr(nlvn__ieaf, f'block_{balm__nsee}')
            rorbe__qbni = ListInstance(c.context, c.builder, types.List(
                data_typ), snzhe__sbx)
            xqp__hfob = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[col_ind])
            rorbe__qbni.inititem(xqp__hfob, gafuh__cie.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, gafuh__cie.value, col_ind)
        tjm__jupqd = DataFramePayloadType(df_typ)
        svmm__rwc = context.nrt.meminfo_data(builder, zmc__lxtp.meminfo)
        rwwuy__xtpzm = context.get_value_type(tjm__jupqd).as_pointer()
        svmm__rwc = builder.bitcast(svmm__rwc, rwwuy__xtpzm)
        builder.store(dataframe_payload._getvalue(), svmm__rwc)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        qxk__maxix = c.pyapi.object_getattr_string(val, 'array')
    else:
        qxk__maxix = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        ammz__gbsro = c.context.insert_const_string(c.builder.module, 'numpy')
        kbg__tvo = c.pyapi.import_module_noblock(ammz__gbsro)
        arr_obj = c.pyapi.call_method(kbg__tvo, 'ascontiguousarray', (
            qxk__maxix,))
        c.pyapi.decref(qxk__maxix)
        c.pyapi.decref(kbg__tvo)
    else:
        arr_obj = qxk__maxix
    nwc__pnao = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    cghw__vpxux = c.pyapi.object_getattr_string(val, 'index')
    fqmcl__culqv = c.pyapi.to_native_value(typ.index, cghw__vpxux).value
    cseoj__ihk = c.pyapi.object_getattr_string(val, 'name')
    brpl__jwuw = c.pyapi.to_native_value(typ.name_typ, cseoj__ihk).value
    kbpdv__ioh = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, nwc__pnao, fqmcl__culqv, brpl__jwuw)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(cghw__vpxux)
    c.pyapi.decref(cseoj__ihk)
    return NativeValue(kbpdv__ioh)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        bhce__pcqz = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(bhce__pcqz._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    fpzhe__udk = c.context.insert_const_string(c.builder.module, 'pandas')
    vyz__ffhh = c.pyapi.import_module_noblock(fpzhe__udk)
    ksq__lzct = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c
        .builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, ksq__lzct.data)
    c.context.nrt.incref(c.builder, typ.index, ksq__lzct.index)
    c.context.nrt.incref(c.builder, typ.name_typ, ksq__lzct.name)
    arr_obj = c.pyapi.from_native_value(typ.data, ksq__lzct.data, c.env_manager
        )
    cghw__vpxux = c.pyapi.from_native_value(typ.index, ksq__lzct.index, c.
        env_manager)
    cseoj__ihk = c.pyapi.from_native_value(typ.name_typ, ksq__lzct.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(vyz__ffhh, 'Series', (arr_obj, cghw__vpxux,
        dtype, cseoj__ihk))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(cghw__vpxux)
    c.pyapi.decref(cseoj__ihk)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(vyz__ffhh)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    iwmy__zws = []
    for txnbs__ncaou in typ_list:
        if isinstance(txnbs__ncaou, int) and not isinstance(txnbs__ncaou, bool
            ):
            yjc__loan = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), txnbs__ncaou))
        else:
            ckw__mxk = numba.typeof(txnbs__ncaou)
            elo__ftfw = context.get_constant_generic(builder, ckw__mxk,
                txnbs__ncaou)
            yjc__loan = pyapi.from_native_value(ckw__mxk, elo__ftfw,
                env_manager)
        iwmy__zws.append(yjc__loan)
    fnzja__epzn = pyapi.list_pack(iwmy__zws)
    for val in iwmy__zws:
        pyapi.decref(val)
    return fnzja__epzn


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    ypfeg__fwmme = not typ.has_runtime_cols
    lws__jlu = 2 if ypfeg__fwmme else 1
    qex__dbap = pyapi.dict_new(lws__jlu)
    jolfm__coxo = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(qex__dbap, 'dist', jolfm__coxo)
    pyapi.decref(jolfm__coxo)
    if ypfeg__fwmme:
        xsx__jnx = _dtype_to_type_enum_list(typ.index)
        if xsx__jnx != None:
            oyhgm__rhspi = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, xsx__jnx)
        else:
            oyhgm__rhspi = pyapi.make_none()
        if typ.is_table_format:
            kee__hxl = typ.table_type
            sikna__ltlhw = pyapi.list_new(lir.Constant(lir.IntType(64), len
                (typ.data)))
            for balm__nsee, dtype in kee__hxl.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                jzfs__krfog = c.context.get_constant(types.int64, len(
                    kee__hxl.block_to_arr_ind[balm__nsee]))
                vldh__ntev = c.context.make_constant_array(c.builder, types
                    .Array(types.int64, 1, 'C'), np.array(kee__hxl.
                    block_to_arr_ind[balm__nsee], dtype=np.int64))
                nndu__zxyvg = c.context.make_array(types.Array(types.int64,
                    1, 'C'))(c.context, c.builder, vldh__ntev)
                with cgutils.for_range(c.builder, jzfs__krfog) as xawzy__ogq:
                    i = xawzy__ogq.index
                    gkzq__ehmg = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), nndu__zxyvg, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(sikna__ltlhw, gkzq__ehmg, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            olb__jxf = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    fnzja__epzn = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    fnzja__epzn = pyapi.make_none()
                olb__jxf.append(fnzja__epzn)
            sikna__ltlhw = pyapi.list_pack(olb__jxf)
            for val in olb__jxf:
                pyapi.decref(val)
        ixjc__xdhce = pyapi.list_pack([oyhgm__rhspi, sikna__ltlhw])
        pyapi.dict_setitem_string(qex__dbap, 'type_metadata', ixjc__xdhce)
    pyapi.object_setattr_string(obj, '_bodo_meta', qex__dbap)
    pyapi.decref(qex__dbap)


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
    qex__dbap = pyapi.dict_new(2)
    jolfm__coxo = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    xsx__jnx = _dtype_to_type_enum_list(typ.index)
    if xsx__jnx != None:
        oyhgm__rhspi = type_enum_list_to_py_list_obj(pyapi, context,
            builder, c.env_manager, xsx__jnx)
    else:
        oyhgm__rhspi = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            juyd__odor = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            juyd__odor = pyapi.make_none()
    else:
        juyd__odor = pyapi.make_none()
    sjpf__lcu = pyapi.list_pack([oyhgm__rhspi, juyd__odor])
    pyapi.dict_setitem_string(qex__dbap, 'type_metadata', sjpf__lcu)
    pyapi.decref(sjpf__lcu)
    pyapi.dict_setitem_string(qex__dbap, 'dist', jolfm__coxo)
    pyapi.object_setattr_string(obj, '_bodo_meta', qex__dbap)
    pyapi.decref(qex__dbap)
    pyapi.decref(jolfm__coxo)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as knxd__tyff:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    nics__aggs = numba.np.numpy_support.map_layout(val)
    tdycy__iptn = not val.flags.writeable
    return types.Array(dtype, val.ndim, nics__aggs, readonly=tdycy__iptn)


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
    pnm__ybfhr = val[i]
    if isinstance(pnm__ybfhr, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(pnm__ybfhr, bytes):
        return binary_array_type
    elif isinstance(pnm__ybfhr, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(pnm__ybfhr, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(pnm__ybfhr))
    elif isinstance(pnm__ybfhr, (dict, Dict)) and all(isinstance(lon__kbbne,
        str) for lon__kbbne in pnm__ybfhr.keys()):
        tpv__yhmts = tuple(pnm__ybfhr.keys())
        zdj__iciwx = tuple(_get_struct_value_arr_type(v) for v in
            pnm__ybfhr.values())
        return StructArrayType(zdj__iciwx, tpv__yhmts)
    elif isinstance(pnm__ybfhr, (dict, Dict)):
        jccc__cuzz = numba.typeof(_value_to_array(list(pnm__ybfhr.keys())))
        mhk__nmn = numba.typeof(_value_to_array(list(pnm__ybfhr.values())))
        jccc__cuzz = to_str_arr_if_dict_array(jccc__cuzz)
        mhk__nmn = to_str_arr_if_dict_array(mhk__nmn)
        return MapArrayType(jccc__cuzz, mhk__nmn)
    elif isinstance(pnm__ybfhr, tuple):
        zdj__iciwx = tuple(_get_struct_value_arr_type(v) for v in pnm__ybfhr)
        return TupleArrayType(zdj__iciwx)
    if isinstance(pnm__ybfhr, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(pnm__ybfhr, list):
            pnm__ybfhr = _value_to_array(pnm__ybfhr)
        jypk__owec = numba.typeof(pnm__ybfhr)
        jypk__owec = to_str_arr_if_dict_array(jypk__owec)
        return ArrayItemArrayType(jypk__owec)
    if isinstance(pnm__ybfhr, datetime.date):
        return datetime_date_array_type
    if isinstance(pnm__ybfhr, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(pnm__ybfhr, bodo.Time):
        return TimeArrayType(pnm__ybfhr.precision)
    if isinstance(pnm__ybfhr, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(pnm__ybfhr, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {pnm__ybfhr}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    zitq__nkxgk = val.copy()
    zitq__nkxgk.append(None)
    kmm__djmgb = np.array(zitq__nkxgk, np.object_)
    if len(val) and isinstance(val[0], float):
        kmm__djmgb = np.array(val, np.float64)
    return kmm__djmgb


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
    plo__car = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        plo__car = to_nullable_type(plo__car)
    return plo__car
