"""
File that contains the main functionality for the Iceberg
integration within the Bodo repo. This does not contain the
main IR transformation.
"""
import os
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse
from uuid import uuid4
import numba
import numpy as np
import pyarrow as pa
from mpi4py import MPI
from numba.core import types
from numba.extending import intrinsic
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.io.fs_io import get_s3_bucket_region_njit
from bodo.io.helpers import is_nullable
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.typing import BodoError, raise_bodo_error


def format_iceberg_conn(conn_str: str) ->str:
    fkvk__vuj = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and fkvk__vuj.scheme not in (
        'iceberg', 'iceberg+file', 'iceberg+s3', 'iceberg+thrift',
        'iceberg+http', 'iceberg+https'):
        raise BodoError(
            "'con' must start with one of the following: 'iceberg://', 'iceberg+file://', 'iceberg+s3://', 'iceberg+thrift://', 'iceberg+http://', 'iceberg+https://', 'iceberg+glue'"
            )
    if sys.version_info.minor < 9:
        if conn_str.startswith('iceberg+'):
            conn_str = conn_str[len('iceberg+'):]
        if conn_str.startswith('iceberg://'):
            conn_str = conn_str[len('iceberg://'):]
    else:
        conn_str = conn_str.removeprefix('iceberg+').removeprefix('iceberg://')
    return conn_str


@numba.njit
def format_iceberg_conn_njit(conn_str):
    with numba.objmode(conn_str='unicode_type'):
        conn_str = format_iceberg_conn(conn_str)
    return conn_str


def _clean_schema(schema: pa.Schema) ->pa.Schema:
    kwlzq__eclr = schema
    for rauz__earbt in range(len(schema)):
        jvvq__iphpp = schema.field(rauz__earbt)
        if pa.types.is_floating(jvvq__iphpp.type):
            kwlzq__eclr = kwlzq__eclr.set(rauz__earbt, jvvq__iphpp.
                with_nullable(False))
        elif pa.types.is_list(jvvq__iphpp.type):
            kwlzq__eclr = kwlzq__eclr.set(rauz__earbt, jvvq__iphpp.
                with_type(pa.list_(pa.field('element', jvvq__iphpp.type.
                value_type))))
    return kwlzq__eclr


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    evup__lwca = _clean_schema(schema)
    xnqy__rskf = _clean_schema(other)
    return evup__lwca.equals(xnqy__rskf)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    fff__ajahp = None
    xou__afuh = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            fff__ajahp, xou__afuh, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as exv__udq:
            if isinstance(exv__udq, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                fff__ajahp = BodoError(
                    f'{exv__udq.message}: {exv__udq.java_error}')
            else:
                fff__ajahp = BodoError(exv__udq.message)
    umec__fxafg = MPI.COMM_WORLD
    fff__ajahp = umec__fxafg.bcast(fff__ajahp)
    if isinstance(fff__ajahp, Exception):
        raise fff__ajahp
    col_names = fff__ajahp
    xou__afuh = umec__fxafg.bcast(xou__afuh)
    pyarrow_schema = umec__fxafg.bcast(pyarrow_schema)
    dxsn__oldh = [_get_numba_typ_from_pa_typ(mky__cqxm, False, True, None)[
        0] for mky__cqxm in xou__afuh]
    return col_names, dxsn__oldh, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        kbsa__ijtf = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as exv__udq:
        if isinstance(exv__udq, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{exv__udq.message}:\n{exv__udq.java_error}')
        else:
            raise BodoError(exv__udq.message)
    return kbsa__ijtf


class IcebergParquetDataset(object):

    def __init__(self, conn, database_schema, table_name, pa_table_schema,
        pq_dataset=None):
        self.pq_dataset = pq_dataset
        self.conn = conn
        self.database_schema = database_schema
        self.table_name = table_name
        self.schema = pa_table_schema
        self.pieces = []
        self._bodo_total_rows = 0
        self._prefix = ''
        self.filesystem = None
        if pq_dataset is not None:
            self.pieces = pq_dataset.pieces
            self._bodo_total_rows = pq_dataset._bodo_total_rows
            self._prefix = pq_dataset._prefix
            self.filesystem = pq_dataset.filesystem


def get_iceberg_pq_dataset(conn, database_schema, table_name,
    typing_pa_table_schema, dnf_filters=None, expr_filters=None,
    is_parallel=False):
    vmp__sqn = tracing.Event('get_iceberg_pq_dataset')
    umec__fxafg = MPI.COMM_WORLD
    bwk__msg = None
    if bodo.get_rank() == 0:
        ajae__xunqb = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            bwk__msg = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                rmwk__tjjz = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                ajae__xunqb.add_attribute('num_files', len(bwk__msg))
                ajae__xunqb.add_attribute(f'first_{rmwk__tjjz}_files', ', '
                    .join(bwk__msg[:rmwk__tjjz]))
        except Exception as exv__udq:
            bwk__msg = exv__udq
        ajae__xunqb.finalize()
    bwk__msg = umec__fxafg.bcast(bwk__msg)
    if isinstance(bwk__msg, Exception):
        ybl__qmo = bwk__msg
        raise BodoError(
            f'Error reading Iceberg Table: {type(ybl__qmo).__name__}: {str(ybl__qmo)}\n'
            )
    hmc__tlb: List[str] = bwk__msg
    if len(hmc__tlb) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(hmc__tlb,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as exv__udq:
            if re.search('Schema .* was different', str(exv__udq), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{exv__udq}"""
                    )
            else:
                raise
    tzqxb__rzo = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    vmp__sqn.finalize()
    return tzqxb__rzo


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        tci__nnlxy = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        eblo__gwrmp = []
        for nfznx__kgbw, bsxs__rnf in zip(numba_type.names, numba_type.data):
            fxj__mfux, cgiin__tmxa = _numba_to_pyarrow_type(bsxs__rnf)
            eblo__gwrmp.append(pa.field(nfznx__kgbw, fxj__mfux, True))
        tci__nnlxy = pa.struct(eblo__gwrmp)
    elif isinstance(numba_type, DecimalArrayType):
        tci__nnlxy = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        agkfe__exbun: PDCategoricalDtype = numba_type.dtype
        tci__nnlxy = pa.dictionary(_numba_to_pyarrow_type(agkfe__exbun.
            int_type)[0], _numba_to_pyarrow_type(agkfe__exbun.elem_type)[0],
            ordered=False if agkfe__exbun.ordered is None else agkfe__exbun
            .ordered)
    elif numba_type == boolean_array:
        tci__nnlxy = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        tci__nnlxy = pa.string()
    elif numba_type == binary_array_type:
        tci__nnlxy = pa.binary()
    elif numba_type == datetime_date_array_type:
        tci__nnlxy = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        tci__nnlxy = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        tci__nnlxy = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return tci__nnlxy, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    eblo__gwrmp = []
    for nfznx__kgbw, tlgw__drfz in zip(df.columns, df.data):
        try:
            xxd__jezy, gihi__xza = _numba_to_pyarrow_type(tlgw__drfz)
        except BodoError as exv__udq:
            raise_bodo_error(exv__udq.msg, exv__udq.loc)
        eblo__gwrmp.append(pa.field(nfznx__kgbw, xxd__jezy, gihi__xza))
    return pa.schema(eblo__gwrmp)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        umec__fxafg = MPI.COMM_WORLD
        wyxa__pzkw = umec__fxafg.Get_rank()
        file_name = f'{wyxa__pzkw:05}-{wyxa__pzkw}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    umec__fxafg = MPI.COMM_WORLD
    hwu__fkvcj = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if umec__fxafg.Get_rank() == 0:
        try:
            (table_loc, iceberg_schema_id, pa_schema, iceberg_schema_str,
                partition_spec, sort_order) = (connector.get_typing_info(
                conn, database_schema, table_name))
            if (if_exists == 'append' and pa_schema is not None and not
                _schemas_equal(pa_schema, df_pyarrow_schema)):
                if numba.core.config.DEVELOPER_MODE:
                    raise BodoError(
                        f"""Iceberg Table and DataFrame Schemas Need to be Equal for Append

Iceberg:
{pa_schema}

DataFrame:
{df_pyarrow_schema}
"""
                        )
                else:
                    raise BodoError(
                        'Iceberg Table and DataFrame Schemas Need to be Equal for Append'
                        )
            if iceberg_schema_id is None:
                iceberg_schema_str = connector.pyarrow_to_iceberg_schema_str(
                    df_pyarrow_schema)
        except connector.IcebergError as exv__udq:
            if isinstance(exv__udq, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                hwu__fkvcj = BodoError(
                    f'{exv__udq.message}: {exv__udq.java_error}')
            else:
                hwu__fkvcj = BodoError(exv__udq.message)
        except Exception as exv__udq:
            hwu__fkvcj = exv__udq
    hwu__fkvcj = umec__fxafg.bcast(hwu__fkvcj)
    if isinstance(hwu__fkvcj, Exception):
        raise hwu__fkvcj
    table_loc = umec__fxafg.bcast(table_loc)
    iceberg_schema_id = umec__fxafg.bcast(iceberg_schema_id)
    partition_spec = umec__fxafg.bcast(partition_spec)
    sort_order = umec__fxafg.bcast(sort_order)
    iceberg_schema_str = umec__fxafg.bcast(iceberg_schema_str)
    if iceberg_schema_id is None:
        already_exists = False
        iceberg_schema_id = -1
    else:
        already_exists = True
    return (already_exists, table_loc, iceberg_schema_id, partition_spec,
        sort_order, iceberg_schema_str)


def register_table_write(conn_str: str, db_name: str, table_name: str,
    table_loc: str, fnames: List[str], all_metrics: Dict[str, List[Any]],
    iceberg_schema_id: int, pa_schema, partition_spec, sort_order, mode: str):
    import bodo_iceberg_connector
    umec__fxafg = MPI.COMM_WORLD
    success = False
    if umec__fxafg.Get_rank() == 0:
        juw__qhpkb = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, juw__qhpkb,
            pa_schema, partition_spec, sort_order, mode)
    success = umec__fxafg.bcast(success)
    return success


@numba.njit()
def iceberg_write(table_name, conn, database_schema, bodo_table, col_names,
    if_exists, is_parallel, df_pyarrow_schema):
    assert is_parallel, 'Iceberg Write only supported for distributed dataframes'
    with numba.objmode(already_exists='bool_', table_loc='unicode_type',
        iceberg_schema_id='i8', partition_spec='unicode_type', sort_order=
        'unicode_type', iceberg_schema_str='unicode_type'):
        (already_exists, table_loc, iceberg_schema_id, partition_spec,
            sort_order, iceberg_schema_str) = (get_table_details_before_write
            (table_name, conn, database_schema, df_pyarrow_schema, if_exists))
    if already_exists and if_exists == 'fail':
        raise ValueError(f'Table already exists.')
    if already_exists:
        mode = if_exists
    else:
        mode = 'create'
    ekgja__rqme = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    wlk__osxk = 'snappy'
    pmhq__yluc = -1
    nko__nbd = np.zeros(1, dtype=np.int64)
    gsik__kob = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(ekgja__rqme),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(wlk__osxk), is_parallel, unicode_to_utf8(
            bucket_region), pmhq__yluc, unicode_to_utf8(iceberg_schema_str),
            nko__nbd.ctypes, gsik__kob.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        umec__fxafg = MPI.COMM_WORLD
        fnames = umec__fxafg.gather(ekgja__rqme)
        if umec__fxafg.Get_rank() != 0:
            fnames = ['a', 'b']
    fqhq__yuc = bodo.gatherv(nko__nbd)
    mfhe__jxocc = bodo.gatherv(gsik__kob)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': mfhe__jxocc.tolist(),
            'record_count': fqhq__yuc.tolist()}, iceberg_schema_id,
            df_pyarrow_schema, partition_spec, sort_order, mode)
    if not success:
        raise BodoError('Iceberg write failed.')


import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('iceberg_pq_write', arrow_cpp.iceberg_pq_write)


@intrinsic
def iceberg_pq_write_table_cpp(typingctx, fname_t, path_name_t, table_t,
    col_names_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, iceberg_metadata_t, record_count_t, file_size_in_bytes_t):

    def codegen(context, builder, sig, args):
        zyqlp__vkbq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jle__omnad = cgutils.get_or_insert_function(builder.module,
            zyqlp__vkbq, name='iceberg_pq_write')
        builder.call(jle__omnad, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
