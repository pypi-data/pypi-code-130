"""
File that contains some IO related helpers.
"""
import pyarrow as pa
from mpi4py import MPI
from numba.core import types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, models, register_model, typeof_impl, unbox
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type
from bodo.hiframes.time_ext import TimeType, TimeArrayType
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.typing import BodoError


class PyArrowTableSchemaType(types.Opaque):

    def __init__(self):
        super(PyArrowTableSchemaType, self).__init__(name=
            'PyArrowTableSchemaType')


pyarrow_table_schema_type = PyArrowTableSchemaType()
types.pyarrow_table_schema_type = pyarrow_table_schema_type
register_model(PyArrowTableSchemaType)(models.OpaqueModel)


@unbox(PyArrowTableSchemaType)
def unbox_pyarrow_table_schema_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(PyArrowTableSchemaType)
def box_pyarrow_table_schema_type(typ, val, c):
    c.pyapi.incref(val)
    return val


@typeof_impl.register(pa.lib.Schema)
def typeof_pyarrow_table_schema(val, c):
    return pyarrow_table_schema_type


@lower_constant(PyArrowTableSchemaType)
def lower_pyarrow_table_schema(context, builder, ty, pyval):
    mqc__kwuuz = context.get_python_api(builder)
    return mqc__kwuuz.unserialize(mqc__kwuuz.serialize_object(pyval))


def is_nullable(typ):
    return bodo.utils.utils.is_array_typ(typ, False) and (not isinstance(
        typ, types.Array) and not isinstance(typ, bodo.DatetimeArrayType))


def pa_schema_unify_reduction(schema_a, schema_b, unused):
    return pa.unify_schemas([schema_a, schema_b])


pa_schema_unify_mpi_op = MPI.Op.Create(pa_schema_unify_reduction, commute=True)
use_nullable_int_arr = True
_pyarrow_numba_type_map = {pa.bool_(): types.bool_, pa.int8(): types.int8,
    pa.int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.
    int64, pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32():
    types.uint32, pa.uint64(): types.uint64, pa.float32(): types.float32,
    pa.float64(): types.float64, pa.string(): string_type, pa.large_string(
    ): string_type, pa.binary(): bytes_type, pa.date32():
    datetime_date_type, pa.date64(): types.NPDatetime('ns'), pa.time32('s'):
    TimeType(0), pa.time32('ms'): TimeType(3), pa.time64('us'): TimeType(6),
    pa.time64('ns'): TimeType(9), pa.null(): string_type}


def get_arrow_timestamp_type(pa_ts_typ):
    lvyhv__hur = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in lvyhv__hur:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        wmoho__xrx = pa_ts_typ.to_pandas_dtype().tz
        xeh__kpp = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(wmoho__xrx)
        return bodo.DatetimeArrayType(xeh__kpp), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ: pa.Field, is_index,
    nullable_from_metadata, category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        pcda__pve, vnwng__eco = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(pcda__pve), vnwng__eco
    if isinstance(pa_typ.type, pa.StructType):
        jur__qgiy = []
        ytzg__qwxh = []
        vnwng__eco = True
        for fuzuq__hcrwf in pa_typ.flatten():
            ytzg__qwxh.append(fuzuq__hcrwf.name.split('.')[-1])
            zpdkx__rolne, aejjr__obf = _get_numba_typ_from_pa_typ(fuzuq__hcrwf,
                is_index, nullable_from_metadata, category_info)
            jur__qgiy.append(zpdkx__rolne)
            vnwng__eco = vnwng__eco and aejjr__obf
        return StructArrayType(tuple(jur__qgiy), tuple(ytzg__qwxh)), vnwng__eco
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale), True
    if str_as_dict:
        if pa_typ.type != pa.string():
            raise BodoError(
                f'Read as dictionary used for non-string column {pa_typ}')
        return dict_str_arr_type, True
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        rnun__mdt = _pyarrow_numba_type_map[pa_typ.type.index_type]
        lfkiz__pkly = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=rnun__mdt)
        return CategoricalArrayType(lfkiz__pkly), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pyarrow_numba_type_map:
        dfxom__azso = _pyarrow_numba_type_map[pa_typ.type]
        vnwng__eco = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if dfxom__azso == datetime_date_type:
        return datetime_date_array_type, vnwng__eco
    if isinstance(dfxom__azso, TimeType):
        return TimeArrayType(dfxom__azso.precision), vnwng__eco
    if dfxom__azso == bytes_type:
        return binary_array_type, vnwng__eco
    pcda__pve = (string_array_type if dfxom__azso == string_type else types
        .Array(dfxom__azso, 1, 'C'))
    if dfxom__azso == types.bool_:
        pcda__pve = boolean_array
    umi__sii = (use_nullable_int_arr if nullable_from_metadata is None else
        nullable_from_metadata)
    if umi__sii and not is_index and isinstance(dfxom__azso, types.Integer
        ) and pa_typ.nullable:
        pcda__pve = IntegerArrayType(dfxom__azso)
    return pcda__pve, vnwng__eco
