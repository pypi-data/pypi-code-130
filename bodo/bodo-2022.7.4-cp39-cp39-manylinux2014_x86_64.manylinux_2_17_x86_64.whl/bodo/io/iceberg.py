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
    hptcc__tcyxb = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and hptcc__tcyxb.scheme not in (
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
    egu__zul = schema
    for llnj__qit in range(len(schema)):
        pxho__ceu = schema.field(llnj__qit)
        if pa.types.is_floating(pxho__ceu.type):
            egu__zul = egu__zul.set(llnj__qit, pxho__ceu.with_nullable(False))
        elif pa.types.is_list(pxho__ceu.type):
            egu__zul = egu__zul.set(llnj__qit, pxho__ceu.with_type(pa.list_
                (pa.field('element', pxho__ceu.type.value_type))))
    return egu__zul


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    vysx__yqhbc = _clean_schema(schema)
    uwj__fxmm = _clean_schema(other)
    return vysx__yqhbc.equals(uwj__fxmm)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    mrtmc__wong = None
    eafvt__cro = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            mrtmc__wong, eafvt__cro, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as svc__yolt:
            if isinstance(svc__yolt, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                mrtmc__wong = BodoError(
                    f'{svc__yolt.message}: {svc__yolt.java_error}')
            else:
                mrtmc__wong = BodoError(svc__yolt.message)
    ecgr__wyxis = MPI.COMM_WORLD
    mrtmc__wong = ecgr__wyxis.bcast(mrtmc__wong)
    if isinstance(mrtmc__wong, Exception):
        raise mrtmc__wong
    col_names = mrtmc__wong
    eafvt__cro = ecgr__wyxis.bcast(eafvt__cro)
    pyarrow_schema = ecgr__wyxis.bcast(pyarrow_schema)
    gtcu__gxf = [_get_numba_typ_from_pa_typ(tub__xinb, False, True, None)[0
        ] for tub__xinb in eafvt__cro]
    return col_names, gtcu__gxf, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        ofnn__hope = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as svc__yolt:
        if isinstance(svc__yolt, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{svc__yolt.message}:\n{svc__yolt.java_error}')
        else:
            raise BodoError(svc__yolt.message)
    return ofnn__hope


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
    pbuaa__woxup = tracing.Event('get_iceberg_pq_dataset')
    ecgr__wyxis = MPI.COMM_WORLD
    lhr__mom = None
    if bodo.get_rank() == 0:
        dfycb__mwdz = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            lhr__mom = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                lrcc__gqed = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                dfycb__mwdz.add_attribute('num_files', len(lhr__mom))
                dfycb__mwdz.add_attribute(f'first_{lrcc__gqed}_files', ', '
                    .join(lhr__mom[:lrcc__gqed]))
        except Exception as svc__yolt:
            lhr__mom = svc__yolt
        dfycb__mwdz.finalize()
    lhr__mom = ecgr__wyxis.bcast(lhr__mom)
    if isinstance(lhr__mom, Exception):
        tmg__kqmk = lhr__mom
        raise BodoError(
            f"""Error reading Iceberg Table: {type(tmg__kqmk).__name__}: {str(tmg__kqmk)}
"""
            )
    gmd__fmt: List[str] = lhr__mom
    if len(gmd__fmt) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(gmd__fmt,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as svc__yolt:
            if re.search('Schema .* was different', str(svc__yolt), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{svc__yolt}"""
                    )
            else:
                raise
    yqly__vmznj = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    pbuaa__woxup.finalize()
    return yqly__vmznj


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        otn__pfb = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        tgvgy__vmgt = []
        for ebxz__aaqft, gmie__wggq in zip(numba_type.names, numba_type.data):
            ggo__sfsio, vqt__eoqft = _numba_to_pyarrow_type(gmie__wggq)
            tgvgy__vmgt.append(pa.field(ebxz__aaqft, ggo__sfsio, True))
        otn__pfb = pa.struct(tgvgy__vmgt)
    elif isinstance(numba_type, DecimalArrayType):
        otn__pfb = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        heqhx__lgf: PDCategoricalDtype = numba_type.dtype
        otn__pfb = pa.dictionary(_numba_to_pyarrow_type(heqhx__lgf.int_type
            )[0], _numba_to_pyarrow_type(heqhx__lgf.elem_type)[0], ordered=
            False if heqhx__lgf.ordered is None else heqhx__lgf.ordered)
    elif numba_type == boolean_array:
        otn__pfb = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        otn__pfb = pa.string()
    elif numba_type == binary_array_type:
        otn__pfb = pa.binary()
    elif numba_type == datetime_date_array_type:
        otn__pfb = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        otn__pfb = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        otn__pfb = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return otn__pfb, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    tgvgy__vmgt = []
    for ebxz__aaqft, ytndr__xydw in zip(df.columns, df.data):
        try:
            pha__paaa, xyi__adzqo = _numba_to_pyarrow_type(ytndr__xydw)
        except BodoError as svc__yolt:
            raise_bodo_error(svc__yolt.msg, svc__yolt.loc)
        tgvgy__vmgt.append(pa.field(ebxz__aaqft, pha__paaa, xyi__adzqo))
    return pa.schema(tgvgy__vmgt)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        ecgr__wyxis = MPI.COMM_WORLD
        sdpcv__ovtah = ecgr__wyxis.Get_rank()
        file_name = f'{sdpcv__ovtah:05}-{sdpcv__ovtah}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    ecgr__wyxis = MPI.COMM_WORLD
    ykee__xpwdb = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if ecgr__wyxis.Get_rank() == 0:
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
        except connector.IcebergError as svc__yolt:
            if isinstance(svc__yolt, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                ykee__xpwdb = BodoError(
                    f'{svc__yolt.message}: {svc__yolt.java_error}')
            else:
                ykee__xpwdb = BodoError(svc__yolt.message)
        except Exception as svc__yolt:
            ykee__xpwdb = svc__yolt
    ykee__xpwdb = ecgr__wyxis.bcast(ykee__xpwdb)
    if isinstance(ykee__xpwdb, Exception):
        raise ykee__xpwdb
    table_loc = ecgr__wyxis.bcast(table_loc)
    iceberg_schema_id = ecgr__wyxis.bcast(iceberg_schema_id)
    partition_spec = ecgr__wyxis.bcast(partition_spec)
    sort_order = ecgr__wyxis.bcast(sort_order)
    iceberg_schema_str = ecgr__wyxis.bcast(iceberg_schema_str)
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
    ecgr__wyxis = MPI.COMM_WORLD
    success = False
    if ecgr__wyxis.Get_rank() == 0:
        lwyym__xxwqo = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, lwyym__xxwqo,
            pa_schema, partition_spec, sort_order, mode)
    success = ecgr__wyxis.bcast(success)
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
    aeb__hta = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    xby__xefq = 'snappy'
    ehid__huck = -1
    bdzja__trvwf = np.zeros(1, dtype=np.int64)
    nbqc__ygtqy = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(aeb__hta),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(xby__xefq), is_parallel, unicode_to_utf8(
            bucket_region), ehid__huck, unicode_to_utf8(iceberg_schema_str),
            bdzja__trvwf.ctypes, nbqc__ygtqy.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        ecgr__wyxis = MPI.COMM_WORLD
        fnames = ecgr__wyxis.gather(aeb__hta)
        if ecgr__wyxis.Get_rank() != 0:
            fnames = ['a', 'b']
    lqv__uxv = bodo.gatherv(bdzja__trvwf)
    qpy__byhfp = bodo.gatherv(nbqc__ygtqy)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': qpy__byhfp.tolist(), 'record_count':
            lqv__uxv.tolist()}, iceberg_schema_id, df_pyarrow_schema,
            partition_spec, sort_order, mode)
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
        fvat__ziau = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        cfyx__ety = cgutils.get_or_insert_function(builder.module,
            fvat__ziau, name='iceberg_pq_write')
        builder.call(cfyx__ety, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
