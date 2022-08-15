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
    imkmm__jgfeg = tuple(val.columns.to_list())
    gbnv__jyzf = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        jlmzw__mmu = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        jlmzw__mmu = numba.typeof(val.index)
    uhxj__fubmc = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    gtn__jlcpt = len(gbnv__jyzf) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(gbnv__jyzf, jlmzw__mmu, imkmm__jgfeg, uhxj__fubmc,
        is_table_format=gtn__jlcpt)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    uhxj__fubmc = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        rbkun__nmrb = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        rbkun__nmrb = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    exjzv__swe = dtype_to_array_type(dtype)
    if _use_dict_str_type and exjzv__swe == string_array_type:
        exjzv__swe = bodo.dict_str_arr_type
    return SeriesType(dtype, data=exjzv__swe, index=rbkun__nmrb, name_typ=
        numba.typeof(val.name), dist=uhxj__fubmc)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    tfxu__zcmim = c.pyapi.object_getattr_string(val, 'index')
    ksavw__ftskj = c.pyapi.to_native_value(typ.index, tfxu__zcmim).value
    c.pyapi.decref(tfxu__zcmim)
    if typ.is_table_format:
        knss__inpgr = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        knss__inpgr.parent = val
        for nttdj__lma, tetk__ekct in typ.table_type.type_to_blk.items():
            vwcds__mrc = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[tetk__ekct]))
            mmp__toc, whbep__hwaof = ListInstance.allocate_ex(c.context, c.
                builder, types.List(nttdj__lma), vwcds__mrc)
            whbep__hwaof.size = vwcds__mrc
            setattr(knss__inpgr, f'block_{tetk__ekct}', whbep__hwaof.value)
        mkf__sbw = c.pyapi.call_method(val, '__len__', ())
        osggo__gth = c.pyapi.long_as_longlong(mkf__sbw)
        c.pyapi.decref(mkf__sbw)
        knss__inpgr.len = osggo__gth
        mzhf__jll = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [knss__inpgr._getvalue()])
    else:
        czara__ygm = [c.context.get_constant_null(nttdj__lma) for
            nttdj__lma in typ.data]
        mzhf__jll = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            czara__ygm)
    jraq__avbw = construct_dataframe(c.context, c.builder, typ, mzhf__jll,
        ksavw__ftskj, val, None)
    return NativeValue(jraq__avbw)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        otx__dta = df._bodo_meta['type_metadata'][1]
    else:
        otx__dta = [None] * len(df.columns)
    gst__remxq = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=otx__dta[i])) for i in range(len(df.columns))]
    gst__remxq = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        nttdj__lma == string_array_type else nttdj__lma) for nttdj__lma in
        gst__remxq]
    return tuple(gst__remxq)


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
    gok__nyo, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(gok__nyo) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {gok__nyo}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        xzstu__qywxz, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return xzstu__qywxz, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        xzstu__qywxz, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return xzstu__qywxz, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        tou__fsw = typ_enum_list[1]
        qucqa__xpj = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(tou__fsw, qucqa__xpj)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        wczyw__rgtkv = typ_enum_list[1]
        gvt__cmuk = tuple(typ_enum_list[2:2 + wczyw__rgtkv])
        umchd__asb = typ_enum_list[2 + wczyw__rgtkv:]
        nam__pxgj = []
        for i in range(wczyw__rgtkv):
            umchd__asb, rsvj__vxjyc = _dtype_from_type_enum_list_recursor(
                umchd__asb)
            nam__pxgj.append(rsvj__vxjyc)
        return umchd__asb, StructType(tuple(nam__pxgj), gvt__cmuk)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        gzprz__bjjq = typ_enum_list[1]
        umchd__asb = typ_enum_list[2:]
        return umchd__asb, gzprz__bjjq
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        gzprz__bjjq = typ_enum_list[1]
        umchd__asb = typ_enum_list[2:]
        return umchd__asb, numba.types.literal(gzprz__bjjq)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        umchd__asb, wahni__uqt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        umchd__asb, mdwil__vrs = _dtype_from_type_enum_list_recursor(umchd__asb
            )
        umchd__asb, rvm__bsvs = _dtype_from_type_enum_list_recursor(umchd__asb)
        umchd__asb, gfqt__kev = _dtype_from_type_enum_list_recursor(umchd__asb)
        umchd__asb, ojsn__bevbx = _dtype_from_type_enum_list_recursor(
            umchd__asb)
        return umchd__asb, PDCategoricalDtype(wahni__uqt, mdwil__vrs,
            rvm__bsvs, gfqt__kev, ojsn__bevbx)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return umchd__asb, DatetimeIndexType(cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        umchd__asb, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(umchd__asb)
        umchd__asb, gfqt__kev = _dtype_from_type_enum_list_recursor(umchd__asb)
        return umchd__asb, NumericIndexType(dtype, cbq__yfy, gfqt__kev)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        umchd__asb, zbfi__pqbl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(umchd__asb)
        return umchd__asb, PeriodIndexType(zbfi__pqbl, cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        umchd__asb, gfqt__kev = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(umchd__asb)
        return umchd__asb, CategoricalIndexType(gfqt__kev, cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return umchd__asb, RangeIndexType(cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return umchd__asb, StringIndexType(cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return umchd__asb, BinaryIndexType(cbq__yfy)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        umchd__asb, cbq__yfy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return umchd__asb, TimedeltaIndexType(cbq__yfy)
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
        icllt__lfzqu = get_overload_const_int(typ)
        if numba.types.maybe_literal(icllt__lfzqu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, icllt__lfzqu]
    elif is_overload_constant_str(typ):
        icllt__lfzqu = get_overload_const_str(typ)
        if numba.types.maybe_literal(icllt__lfzqu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, icllt__lfzqu]
    elif is_overload_constant_bool(typ):
        icllt__lfzqu = get_overload_const_bool(typ)
        if numba.types.maybe_literal(icllt__lfzqu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, icllt__lfzqu]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        qpel__titmi = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for mrqg__wbos in typ.names:
            qpel__titmi.append(mrqg__wbos)
        for egcb__wui in typ.data:
            qpel__titmi += _dtype_to_type_enum_list_recursor(egcb__wui)
        return qpel__titmi
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        dommy__owqgl = _dtype_to_type_enum_list_recursor(typ.categories)
        hehga__uxhxg = _dtype_to_type_enum_list_recursor(typ.elem_type)
        qoje__dusx = _dtype_to_type_enum_list_recursor(typ.ordered)
        sugas__iqkg = _dtype_to_type_enum_list_recursor(typ.data)
        pox__cfop = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + dommy__owqgl + hehga__uxhxg + qoje__dusx + sugas__iqkg + pox__cfop
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                vnh__jxdt = types.float64
                pxhv__zgzcy = types.Array(vnh__jxdt, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                vnh__jxdt = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    pxhv__zgzcy = IntegerArrayType(vnh__jxdt)
                else:
                    pxhv__zgzcy = types.Array(vnh__jxdt, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                vnh__jxdt = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    pxhv__zgzcy = IntegerArrayType(vnh__jxdt)
                else:
                    pxhv__zgzcy = types.Array(vnh__jxdt, 1, 'C')
            elif typ.dtype == types.bool_:
                vnh__jxdt = typ.dtype
                pxhv__zgzcy = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(vnh__jxdt
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(pxhv__zgzcy)
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
                ebk__hmi = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(ebk__hmi)
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
        xlu__ygh = S.dtype.unit
        if xlu__ygh != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        aftm__akys = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(aftm__akys)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    lbct__wxmvv = cgutils.is_not_null(builder, parent_obj)
    gnlsh__afxtr = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(lbct__wxmvv):
        gvgk__tnn = pyapi.object_getattr_string(parent_obj, 'columns')
        mkf__sbw = pyapi.call_method(gvgk__tnn, '__len__', ())
        builder.store(pyapi.long_as_longlong(mkf__sbw), gnlsh__afxtr)
        pyapi.decref(mkf__sbw)
        pyapi.decref(gvgk__tnn)
    use_parent_obj = builder.and_(lbct__wxmvv, builder.icmp_unsigned('==',
        builder.load(gnlsh__afxtr), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        roo__mleif = df_typ.runtime_colname_typ
        context.nrt.incref(builder, roo__mleif, dataframe_payload.columns)
        return pyapi.from_native_value(roo__mleif, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        wdjb__aeq = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        wdjb__aeq = np.array(df_typ.columns, 'int64')
    else:
        wdjb__aeq = df_typ.columns
    gepgm__msan = numba.typeof(wdjb__aeq)
    xzei__szzqu = context.get_constant_generic(builder, gepgm__msan, wdjb__aeq)
    ajm__vwr = pyapi.from_native_value(gepgm__msan, xzei__szzqu, c.env_manager)
    return ajm__vwr


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (kxh__ueg, ywvxg__xoz):
        with kxh__ueg:
            pyapi.incref(obj)
            uzmn__oglyy = context.insert_const_string(c.builder.module, 'numpy'
                )
            fumen__ffy = pyapi.import_module_noblock(uzmn__oglyy)
            if df_typ.has_runtime_cols:
                kzt__smqf = 0
            else:
                kzt__smqf = len(df_typ.columns)
            uemaj__tfspn = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), kzt__smqf))
            bxk__hpqw = pyapi.call_method(fumen__ffy, 'arange', (uemaj__tfspn,)
                )
            pyapi.object_setattr_string(obj, 'columns', bxk__hpqw)
            pyapi.decref(fumen__ffy)
            pyapi.decref(bxk__hpqw)
            pyapi.decref(uemaj__tfspn)
        with ywvxg__xoz:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            pyjdq__lydl = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            uzmn__oglyy = context.insert_const_string(c.builder.module,
                'pandas')
            fumen__ffy = pyapi.import_module_noblock(uzmn__oglyy)
            df_obj = pyapi.call_method(fumen__ffy, 'DataFrame', (pyapi.
                borrow_none(), pyjdq__lydl))
            pyapi.decref(fumen__ffy)
            pyapi.decref(pyjdq__lydl)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    jkfl__wiqch = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = jkfl__wiqch.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        vvln__dccbm = typ.table_type
        knss__inpgr = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, vvln__dccbm, knss__inpgr)
        avqk__uybk = box_table(vvln__dccbm, knss__inpgr, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (wsde__yeaay, heycw__sog):
            with wsde__yeaay:
                wndqg__mju = pyapi.object_getattr_string(avqk__uybk, 'arrays')
                jkz__bida = c.pyapi.make_none()
                if n_cols is None:
                    mkf__sbw = pyapi.call_method(wndqg__mju, '__len__', ())
                    vwcds__mrc = pyapi.long_as_longlong(mkf__sbw)
                    pyapi.decref(mkf__sbw)
                else:
                    vwcds__mrc = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, vwcds__mrc) as sgiq__xpcyo:
                    i = sgiq__xpcyo.index
                    ubgrm__huiw = pyapi.list_getitem(wndqg__mju, i)
                    kfe__vpg = c.builder.icmp_unsigned('!=', ubgrm__huiw,
                        jkz__bida)
                    with builder.if_then(kfe__vpg):
                        iex__mbta = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, iex__mbta, ubgrm__huiw)
                        pyapi.decref(iex__mbta)
                pyapi.decref(wndqg__mju)
                pyapi.decref(jkz__bida)
            with heycw__sog:
                df_obj = builder.load(res)
                pyjdq__lydl = pyapi.object_getattr_string(df_obj, 'index')
                jhy__yjegg = c.pyapi.call_method(avqk__uybk, 'to_pandas', (
                    pyjdq__lydl,))
                builder.store(jhy__yjegg, res)
                pyapi.decref(df_obj)
                pyapi.decref(pyjdq__lydl)
        pyapi.decref(avqk__uybk)
    else:
        hwh__osrtp = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        xqckf__lnhzp = typ.data
        for i, uvdm__cdfet, exjzv__swe in zip(range(n_cols), hwh__osrtp,
            xqckf__lnhzp):
            pvkp__dtyx = cgutils.alloca_once_value(builder, uvdm__cdfet)
            usyjz__duzg = cgutils.alloca_once_value(builder, context.
                get_constant_null(exjzv__swe))
            kfe__vpg = builder.not_(is_ll_eq(builder, pvkp__dtyx, usyjz__duzg))
            yfv__ppl = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, kfe__vpg))
            with builder.if_then(yfv__ppl):
                iex__mbta = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, exjzv__swe, uvdm__cdfet)
                arr_obj = pyapi.from_native_value(exjzv__swe, uvdm__cdfet,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, iex__mbta, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(iex__mbta)
    df_obj = builder.load(res)
    ajm__vwr = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', ajm__vwr)
    pyapi.decref(ajm__vwr)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    jkz__bida = pyapi.borrow_none()
    jdhox__piq = pyapi.unserialize(pyapi.serialize_object(slice))
    qnr__tand = pyapi.call_function_objargs(jdhox__piq, [jkz__bida])
    mxhu__tmb = pyapi.long_from_longlong(col_ind)
    cynl__ihf = pyapi.tuple_pack([qnr__tand, mxhu__tmb])
    fdee__nedje = pyapi.object_getattr_string(df_obj, 'iloc')
    clzr__ayy = pyapi.object_getitem(fdee__nedje, cynl__ihf)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        tvesm__izgyi = pyapi.object_getattr_string(clzr__ayy, 'array')
    else:
        tvesm__izgyi = pyapi.object_getattr_string(clzr__ayy, 'values')
    if isinstance(data_typ, types.Array):
        fayad__ajtcq = context.insert_const_string(builder.module, 'numpy')
        wtk__tymmb = pyapi.import_module_noblock(fayad__ajtcq)
        arr_obj = pyapi.call_method(wtk__tymmb, 'ascontiguousarray', (
            tvesm__izgyi,))
        pyapi.decref(tvesm__izgyi)
        pyapi.decref(wtk__tymmb)
    else:
        arr_obj = tvesm__izgyi
    pyapi.decref(jdhox__piq)
    pyapi.decref(qnr__tand)
    pyapi.decref(mxhu__tmb)
    pyapi.decref(cynl__ihf)
    pyapi.decref(fdee__nedje)
    pyapi.decref(clzr__ayy)
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
        jkfl__wiqch = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            jkfl__wiqch.parent, args[1], data_typ)
        exw__gtki = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            knss__inpgr = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            tetk__ekct = df_typ.table_type.type_to_blk[data_typ]
            lki__ktkm = getattr(knss__inpgr, f'block_{tetk__ekct}')
            mgjc__zhq = ListInstance(c.context, c.builder, types.List(
                data_typ), lki__ktkm)
            aeq__lqt = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[col_ind])
            mgjc__zhq.inititem(aeq__lqt, exw__gtki.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, exw__gtki.value, col_ind)
        fvl__shilr = DataFramePayloadType(df_typ)
        rqd__rwrl = context.nrt.meminfo_data(builder, jkfl__wiqch.meminfo)
        ihhj__rbmsp = context.get_value_type(fvl__shilr).as_pointer()
        rqd__rwrl = builder.bitcast(rqd__rwrl, ihhj__rbmsp)
        builder.store(dataframe_payload._getvalue(), rqd__rwrl)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        tvesm__izgyi = c.pyapi.object_getattr_string(val, 'array')
    else:
        tvesm__izgyi = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        fayad__ajtcq = c.context.insert_const_string(c.builder.module, 'numpy')
        wtk__tymmb = c.pyapi.import_module_noblock(fayad__ajtcq)
        arr_obj = c.pyapi.call_method(wtk__tymmb, 'ascontiguousarray', (
            tvesm__izgyi,))
        c.pyapi.decref(tvesm__izgyi)
        c.pyapi.decref(wtk__tymmb)
    else:
        arr_obj = tvesm__izgyi
    owoyy__evqy = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    pyjdq__lydl = c.pyapi.object_getattr_string(val, 'index')
    ksavw__ftskj = c.pyapi.to_native_value(typ.index, pyjdq__lydl).value
    iqdz__soq = c.pyapi.object_getattr_string(val, 'name')
    idr__yns = c.pyapi.to_native_value(typ.name_typ, iqdz__soq).value
    xwt__soq = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, owoyy__evqy, ksavw__ftskj, idr__yns)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(pyjdq__lydl)
    c.pyapi.decref(iqdz__soq)
    return NativeValue(xwt__soq)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        wol__ezn = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(wol__ezn._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    uzmn__oglyy = c.context.insert_const_string(c.builder.module, 'pandas')
    hhcl__xgxo = c.pyapi.import_module_noblock(uzmn__oglyy)
    coqbn__fez = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, coqbn__fez.data)
    c.context.nrt.incref(c.builder, typ.index, coqbn__fez.index)
    c.context.nrt.incref(c.builder, typ.name_typ, coqbn__fez.name)
    arr_obj = c.pyapi.from_native_value(typ.data, coqbn__fez.data, c.
        env_manager)
    pyjdq__lydl = c.pyapi.from_native_value(typ.index, coqbn__fez.index, c.
        env_manager)
    iqdz__soq = c.pyapi.from_native_value(typ.name_typ, coqbn__fez.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(hhcl__xgxo, 'Series', (arr_obj, pyjdq__lydl,
        dtype, iqdz__soq))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(pyjdq__lydl)
    c.pyapi.decref(iqdz__soq)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(hhcl__xgxo)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    xkf__csa = []
    for gtlr__dxvh in typ_list:
        if isinstance(gtlr__dxvh, int) and not isinstance(gtlr__dxvh, bool):
            panxe__jmfc = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), gtlr__dxvh))
        else:
            orrg__qqh = numba.typeof(gtlr__dxvh)
            mwav__lcn = context.get_constant_generic(builder, orrg__qqh,
                gtlr__dxvh)
            panxe__jmfc = pyapi.from_native_value(orrg__qqh, mwav__lcn,
                env_manager)
        xkf__csa.append(panxe__jmfc)
    xumg__uldix = pyapi.list_pack(xkf__csa)
    for val in xkf__csa:
        pyapi.decref(val)
    return xumg__uldix


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    sww__nyge = not typ.has_runtime_cols
    crcch__ngo = 2 if sww__nyge else 1
    xcbzk__xtaoa = pyapi.dict_new(crcch__ngo)
    cojv__fyrn = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(xcbzk__xtaoa, 'dist', cojv__fyrn)
    pyapi.decref(cojv__fyrn)
    if sww__nyge:
        ifo__cpvz = _dtype_to_type_enum_list(typ.index)
        if ifo__cpvz != None:
            fbsu__rru = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, ifo__cpvz)
        else:
            fbsu__rru = pyapi.make_none()
        if typ.is_table_format:
            nttdj__lma = typ.table_type
            wqz__vsa = pyapi.list_new(lir.Constant(lir.IntType(64), len(typ
                .data)))
            for tetk__ekct, dtype in nttdj__lma.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                vwcds__mrc = c.context.get_constant(types.int64, len(
                    nttdj__lma.block_to_arr_ind[tetk__ekct]))
                iga__grwk = c.context.make_constant_array(c.builder, types.
                    Array(types.int64, 1, 'C'), np.array(nttdj__lma.
                    block_to_arr_ind[tetk__ekct], dtype=np.int64))
                rvv__xrft = c.context.make_array(types.Array(types.int64, 1,
                    'C'))(c.context, c.builder, iga__grwk)
                with cgutils.for_range(c.builder, vwcds__mrc) as sgiq__xpcyo:
                    i = sgiq__xpcyo.index
                    bcwk__wad = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), rvv__xrft, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(wqz__vsa, bcwk__wad, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            zrelx__ootzx = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    xumg__uldix = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    xumg__uldix = pyapi.make_none()
                zrelx__ootzx.append(xumg__uldix)
            wqz__vsa = pyapi.list_pack(zrelx__ootzx)
            for val in zrelx__ootzx:
                pyapi.decref(val)
        zyag__fqia = pyapi.list_pack([fbsu__rru, wqz__vsa])
        pyapi.dict_setitem_string(xcbzk__xtaoa, 'type_metadata', zyag__fqia)
    pyapi.object_setattr_string(obj, '_bodo_meta', xcbzk__xtaoa)
    pyapi.decref(xcbzk__xtaoa)


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
    xcbzk__xtaoa = pyapi.dict_new(2)
    cojv__fyrn = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    ifo__cpvz = _dtype_to_type_enum_list(typ.index)
    if ifo__cpvz != None:
        fbsu__rru = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, ifo__cpvz)
    else:
        fbsu__rru = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            cwe__fksy = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            cwe__fksy = pyapi.make_none()
    else:
        cwe__fksy = pyapi.make_none()
    hgli__ifstd = pyapi.list_pack([fbsu__rru, cwe__fksy])
    pyapi.dict_setitem_string(xcbzk__xtaoa, 'type_metadata', hgli__ifstd)
    pyapi.decref(hgli__ifstd)
    pyapi.dict_setitem_string(xcbzk__xtaoa, 'dist', cojv__fyrn)
    pyapi.object_setattr_string(obj, '_bodo_meta', xcbzk__xtaoa)
    pyapi.decref(xcbzk__xtaoa)
    pyapi.decref(cojv__fyrn)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as hklz__srux:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    fwbkz__szngv = numba.np.numpy_support.map_layout(val)
    pilw__jpf = not val.flags.writeable
    return types.Array(dtype, val.ndim, fwbkz__szngv, readonly=pilw__jpf)


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
    tyv__hzots = val[i]
    if isinstance(tyv__hzots, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(tyv__hzots, bytes):
        return binary_array_type
    elif isinstance(tyv__hzots, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(tyv__hzots, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(tyv__hzots))
    elif isinstance(tyv__hzots, (dict, Dict)) and all(isinstance(
        wmutv__zoqz, str) for wmutv__zoqz in tyv__hzots.keys()):
        gvt__cmuk = tuple(tyv__hzots.keys())
        mzz__siii = tuple(_get_struct_value_arr_type(v) for v in tyv__hzots
            .values())
        return StructArrayType(mzz__siii, gvt__cmuk)
    elif isinstance(tyv__hzots, (dict, Dict)):
        gmx__kpx = numba.typeof(_value_to_array(list(tyv__hzots.keys())))
        pzxg__vxh = numba.typeof(_value_to_array(list(tyv__hzots.values())))
        gmx__kpx = to_str_arr_if_dict_array(gmx__kpx)
        pzxg__vxh = to_str_arr_if_dict_array(pzxg__vxh)
        return MapArrayType(gmx__kpx, pzxg__vxh)
    elif isinstance(tyv__hzots, tuple):
        mzz__siii = tuple(_get_struct_value_arr_type(v) for v in tyv__hzots)
        return TupleArrayType(mzz__siii)
    if isinstance(tyv__hzots, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(tyv__hzots, list):
            tyv__hzots = _value_to_array(tyv__hzots)
        bbrdz__zxhix = numba.typeof(tyv__hzots)
        bbrdz__zxhix = to_str_arr_if_dict_array(bbrdz__zxhix)
        return ArrayItemArrayType(bbrdz__zxhix)
    if isinstance(tyv__hzots, datetime.date):
        return datetime_date_array_type
    if isinstance(tyv__hzots, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(tyv__hzots, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(tyv__hzots, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {tyv__hzots}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    wwf__wyp = val.copy()
    wwf__wyp.append(None)
    uvdm__cdfet = np.array(wwf__wyp, np.object_)
    if len(val) and isinstance(val[0], float):
        uvdm__cdfet = np.array(val, np.float64)
    return uvdm__cdfet


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
    exjzv__swe = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        exjzv__swe = to_nullable_type(exjzv__swe)
    return exjzv__swe
