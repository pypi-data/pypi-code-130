from urllib.parse import parse_qsl, urlparse
import pyarrow as pa
import snowflake.connector
import bodo
from bodo.utils import tracing
from bodo.utils.typing import BodoError
FIELD_TYPE_TO_PA_TYPE = [pa.int64(), pa.float64(), pa.string(), pa.date32(),
    pa.timestamp('ns'), pa.string(), pa.timestamp('ns'), pa.timestamp('ns'),
    pa.timestamp('ns'), pa.string(), pa.string(), pa.binary(), pa.time64(
    'ns'), pa.bool_()]


def get_connection_params(conn_str):
    import json
    eqjd__badtt = urlparse(conn_str)
    yixw__pnko = {}
    if eqjd__badtt.username:
        yixw__pnko['user'] = eqjd__badtt.username
    if eqjd__badtt.password:
        yixw__pnko['password'] = eqjd__badtt.password
    if eqjd__badtt.hostname:
        yixw__pnko['account'] = eqjd__badtt.hostname
    if eqjd__badtt.port:
        yixw__pnko['port'] = eqjd__badtt.port
    if eqjd__badtt.path:
        rydv__huj = eqjd__badtt.path
        if rydv__huj.startswith('/'):
            rydv__huj = rydv__huj[1:]
        eno__jimqq = rydv__huj.split('/')
        if len(eno__jimqq) == 2:
            wbtl__trslz, schema = eno__jimqq
        elif len(eno__jimqq) == 1:
            wbtl__trslz = eno__jimqq[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        yixw__pnko['database'] = wbtl__trslz
        if schema:
            yixw__pnko['schema'] = schema
    if eqjd__badtt.query:
        for xdeq__bev, lzje__xywyz in parse_qsl(eqjd__badtt.query):
            yixw__pnko[xdeq__bev] = lzje__xywyz
            if xdeq__bev == 'session_parameters':
                yixw__pnko[xdeq__bev] = json.loads(lzje__xywyz)
    yixw__pnko['application'] = 'bodo'
    return yixw__pnko


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for hsq__wtun in batches:
            hsq__wtun._bodo_num_rows = hsq__wtun.rowcount
            self._bodo_total_rows += hsq__wtun._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    usvf__yojwz = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    fxf__qwpyh = MPI.COMM_WORLD
    czjx__djd = tracing.Event('snowflake_connect', is_parallel=False)
    pmu__ivuj = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**pmu__ivuj)
    czjx__djd.finalize()
    if bodo.get_rank() == 0:
        kizaf__hro = conn.cursor()
        hwduq__yqw = tracing.Event('get_schema', is_parallel=False)
        ano__drunp = f'select * from ({query}) x LIMIT {100}'
        umk__dot = kizaf__hro.execute(ano__drunp).fetch_arrow_all()
        if umk__dot is None:
            cciyx__ffces = kizaf__hro.describe(query)
            ezrz__aszv = [pa.field(anhs__beetp.name, FIELD_TYPE_TO_PA_TYPE[
                anhs__beetp.type_code]) for anhs__beetp in cciyx__ffces]
            schema = pa.schema(ezrz__aszv)
        else:
            schema = umk__dot.schema
        hwduq__yqw.finalize()
        rmdn__yrtgd = tracing.Event('execute_query', is_parallel=False)
        kizaf__hro.execute(query)
        rmdn__yrtgd.finalize()
        batches = kizaf__hro.get_result_batches()
        fxf__qwpyh.bcast((batches, schema))
    else:
        batches, schema = fxf__qwpyh.bcast(None)
    aqzyk__xjpy = SnowflakeDataset(batches, schema, conn)
    usvf__yojwz.finalize()
    return aqzyk__xjpy
