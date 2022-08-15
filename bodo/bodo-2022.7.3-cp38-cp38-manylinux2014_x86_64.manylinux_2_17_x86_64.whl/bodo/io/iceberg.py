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
    sqzxs__leaj = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and sqzxs__leaj.scheme not in (
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
    pzckw__rktp = schema
    for nqy__dmln in range(len(schema)):
        pweum__reve = schema.field(nqy__dmln)
        if pa.types.is_floating(pweum__reve.type):
            pzckw__rktp = pzckw__rktp.set(nqy__dmln, pweum__reve.
                with_nullable(False))
        elif pa.types.is_list(pweum__reve.type):
            pzckw__rktp = pzckw__rktp.set(nqy__dmln, pweum__reve.with_type(
                pa.list_(pa.field('element', pweum__reve.type.value_type))))
    return pzckw__rktp


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    mwup__nztg = _clean_schema(schema)
    xdlc__xsrd = _clean_schema(other)
    return mwup__nztg.equals(xdlc__xsrd)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    thtcx__mho = None
    ygqb__rfeav = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            thtcx__mho, ygqb__rfeav, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as mfpyd__lbxvw:
            if isinstance(mfpyd__lbxvw, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                thtcx__mho = BodoError(
                    f'{mfpyd__lbxvw.message}: {mfpyd__lbxvw.java_error}')
            else:
                thtcx__mho = BodoError(mfpyd__lbxvw.message)
    lxmra__ltxxd = MPI.COMM_WORLD
    thtcx__mho = lxmra__ltxxd.bcast(thtcx__mho)
    if isinstance(thtcx__mho, Exception):
        raise thtcx__mho
    col_names = thtcx__mho
    ygqb__rfeav = lxmra__ltxxd.bcast(ygqb__rfeav)
    pyarrow_schema = lxmra__ltxxd.bcast(pyarrow_schema)
    keyk__unnx = [_get_numba_typ_from_pa_typ(mxbz__hvhkz, False, True, None
        )[0] for mxbz__hvhkz in ygqb__rfeav]
    return col_names, keyk__unnx, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        qgg__juewv = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as mfpyd__lbxvw:
        if isinstance(mfpyd__lbxvw, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(
                f'{mfpyd__lbxvw.message}:\n{mfpyd__lbxvw.java_error}')
        else:
            raise BodoError(mfpyd__lbxvw.message)
    return qgg__juewv


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
    qusm__vqh = tracing.Event('get_iceberg_pq_dataset')
    lxmra__ltxxd = MPI.COMM_WORLD
    iend__vdhxs = None
    if bodo.get_rank() == 0:
        pjkq__xtrib = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            iend__vdhxs = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                kyyao__mexxu = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                pjkq__xtrib.add_attribute('num_files', len(iend__vdhxs))
                pjkq__xtrib.add_attribute(f'first_{kyyao__mexxu}_files',
                    ', '.join(iend__vdhxs[:kyyao__mexxu]))
        except Exception as mfpyd__lbxvw:
            iend__vdhxs = mfpyd__lbxvw
        pjkq__xtrib.finalize()
    iend__vdhxs = lxmra__ltxxd.bcast(iend__vdhxs)
    if isinstance(iend__vdhxs, Exception):
        ust__npcjx = iend__vdhxs
        raise BodoError(
            f"""Error reading Iceberg Table: {type(ust__npcjx).__name__}: {str(ust__npcjx)}
"""
            )
    pqu__jrd: List[str] = iend__vdhxs
    if len(pqu__jrd) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(pqu__jrd,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as mfpyd__lbxvw:
            if re.search('Schema .* was different', str(mfpyd__lbxvw), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{mfpyd__lbxvw}"""
                    )
            else:
                raise
    fyk__xxyve = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    qusm__vqh.finalize()
    return fyk__xxyve


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        ypm__tgoo = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        shky__fzix = []
        for rsn__jij, big__fij in zip(numba_type.names, numba_type.data):
            iuem__oniek, egg__rwe = _numba_to_pyarrow_type(big__fij)
            shky__fzix.append(pa.field(rsn__jij, iuem__oniek, True))
        ypm__tgoo = pa.struct(shky__fzix)
    elif isinstance(numba_type, DecimalArrayType):
        ypm__tgoo = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        nbzdi__aqi: PDCategoricalDtype = numba_type.dtype
        ypm__tgoo = pa.dictionary(_numba_to_pyarrow_type(nbzdi__aqi.
            int_type)[0], _numba_to_pyarrow_type(nbzdi__aqi.elem_type)[0],
            ordered=False if nbzdi__aqi.ordered is None else nbzdi__aqi.ordered
            )
    elif numba_type == boolean_array:
        ypm__tgoo = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        ypm__tgoo = pa.string()
    elif numba_type == binary_array_type:
        ypm__tgoo = pa.binary()
    elif numba_type == datetime_date_array_type:
        ypm__tgoo = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        ypm__tgoo = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        ypm__tgoo = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return ypm__tgoo, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    shky__fzix = []
    for rsn__jij, jcb__sblaf in zip(df.columns, df.data):
        try:
            pcfxt__siak, wml__gad = _numba_to_pyarrow_type(jcb__sblaf)
        except BodoError as mfpyd__lbxvw:
            raise_bodo_error(mfpyd__lbxvw.msg, mfpyd__lbxvw.loc)
        shky__fzix.append(pa.field(rsn__jij, pcfxt__siak, wml__gad))
    return pa.schema(shky__fzix)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        lxmra__ltxxd = MPI.COMM_WORLD
        uubne__tadv = lxmra__ltxxd.Get_rank()
        file_name = f'{uubne__tadv:05}-{uubne__tadv}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    lxmra__ltxxd = MPI.COMM_WORLD
    pmwo__dbh = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if lxmra__ltxxd.Get_rank() == 0:
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
        except connector.IcebergError as mfpyd__lbxvw:
            if isinstance(mfpyd__lbxvw, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                pmwo__dbh = BodoError(
                    f'{mfpyd__lbxvw.message}: {mfpyd__lbxvw.java_error}')
            else:
                pmwo__dbh = BodoError(mfpyd__lbxvw.message)
        except Exception as mfpyd__lbxvw:
            pmwo__dbh = mfpyd__lbxvw
    pmwo__dbh = lxmra__ltxxd.bcast(pmwo__dbh)
    if isinstance(pmwo__dbh, Exception):
        raise pmwo__dbh
    table_loc = lxmra__ltxxd.bcast(table_loc)
    iceberg_schema_id = lxmra__ltxxd.bcast(iceberg_schema_id)
    partition_spec = lxmra__ltxxd.bcast(partition_spec)
    sort_order = lxmra__ltxxd.bcast(sort_order)
    iceberg_schema_str = lxmra__ltxxd.bcast(iceberg_schema_str)
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
    lxmra__ltxxd = MPI.COMM_WORLD
    success = False
    if lxmra__ltxxd.Get_rank() == 0:
        dltdm__kkzn = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, dltdm__kkzn,
            pa_schema, partition_spec, sort_order, mode)
    success = lxmra__ltxxd.bcast(success)
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
    ifzj__nlor = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    agon__fixo = 'snappy'
    iwbew__gcss = -1
    orsr__wlo = np.zeros(1, dtype=np.int64)
    zempu__nge = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(ifzj__nlor),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(agon__fixo), is_parallel, unicode_to_utf8(
            bucket_region), iwbew__gcss, unicode_to_utf8(iceberg_schema_str
            ), orsr__wlo.ctypes, zempu__nge.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        lxmra__ltxxd = MPI.COMM_WORLD
        fnames = lxmra__ltxxd.gather(ifzj__nlor)
        if lxmra__ltxxd.Get_rank() != 0:
            fnames = ['a', 'b']
    mwlcp__mct = bodo.gatherv(orsr__wlo)
    bes__dumh = bodo.gatherv(zempu__nge)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': bes__dumh.tolist(), 'record_count':
            mwlcp__mct.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        hvd__lxr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        sjx__zfoap = cgutils.get_or_insert_function(builder.module,
            hvd__lxr, name='iceberg_pq_write')
        builder.call(sjx__zfoap, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
