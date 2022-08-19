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
    ywnd__zoog = context.get_python_api(builder)
    return ywnd__zoog.unserialize(ywnd__zoog.serialize_object(pyval))


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
    hps__edpi = 'ns', 'us', 'ms', 's'
    if pa_ts_typ.unit not in hps__edpi:
        return types.Array(bodo.datetime64ns, 1, 'C'), False
    elif pa_ts_typ.tz is not None:
        awgu__dwbg = pa_ts_typ.to_pandas_dtype().tz
        ljosb__ojmow = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(
            awgu__dwbg)
        return bodo.DatetimeArrayType(ljosb__ojmow), True
    else:
        return types.Array(bodo.datetime64ns, 1, 'C'), True


def _get_numba_typ_from_pa_typ(pa_typ: pa.Field, is_index,
    nullable_from_metadata, category_info, str_as_dict=False):
    if isinstance(pa_typ.type, pa.ListType):
        jpwrw__lrig, jyn__jgd = _get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info)
        return ArrayItemArrayType(jpwrw__lrig), jyn__jgd
    if isinstance(pa_typ.type, pa.StructType):
        dil__rxh = []
        qvf__yhd = []
        jyn__jgd = True
        for cnfbh__mcw in pa_typ.flatten():
            qvf__yhd.append(cnfbh__mcw.name.split('.')[-1])
            szndu__kqjkv, dgos__yri = _get_numba_typ_from_pa_typ(cnfbh__mcw,
                is_index, nullable_from_metadata, category_info)
            dil__rxh.append(szndu__kqjkv)
            jyn__jgd = jyn__jgd and dgos__yri
        return StructArrayType(tuple(dil__rxh), tuple(qvf__yhd)), jyn__jgd
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
        ggch__hqn = _pyarrow_numba_type_map[pa_typ.type.index_type]
        xpfgi__rsm = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=ggch__hqn)
        return CategoricalArrayType(xpfgi__rsm), True
    if isinstance(pa_typ.type, pa.lib.TimestampType):
        return get_arrow_timestamp_type(pa_typ.type)
    elif pa_typ.type in _pyarrow_numba_type_map:
        yqex__bhsro = _pyarrow_numba_type_map[pa_typ.type]
        jyn__jgd = True
    else:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    if yqex__bhsro == datetime_date_type:
        return datetime_date_array_type, jyn__jgd
    if isinstance(yqex__bhsro, TimeType):
        return TimeArrayType(yqex__bhsro.precision), jyn__jgd
    if yqex__bhsro == bytes_type:
        return binary_array_type, jyn__jgd
    jpwrw__lrig = (string_array_type if yqex__bhsro == string_type else
        types.Array(yqex__bhsro, 1, 'C'))
    if yqex__bhsro == types.bool_:
        jpwrw__lrig = boolean_array
    moxlu__oqhqy = (use_nullable_int_arr if nullable_from_metadata is None else
        nullable_from_metadata)
    if moxlu__oqhqy and not is_index and isinstance(yqex__bhsro, types.Integer
        ) and pa_typ.nullable:
        jpwrw__lrig = IntegerArrayType(yqex__bhsro)
    return jpwrw__lrig, jyn__jgd
