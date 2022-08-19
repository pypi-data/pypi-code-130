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
    cbv__fsyxf = urlparse(conn_str)
    punin__xxq = {}
    if cbv__fsyxf.username:
        punin__xxq['user'] = cbv__fsyxf.username
    if cbv__fsyxf.password:
        punin__xxq['password'] = cbv__fsyxf.password
    if cbv__fsyxf.hostname:
        punin__xxq['account'] = cbv__fsyxf.hostname
    if cbv__fsyxf.port:
        punin__xxq['port'] = cbv__fsyxf.port
    if cbv__fsyxf.path:
        dtdfc__ppw = cbv__fsyxf.path
        if dtdfc__ppw.startswith('/'):
            dtdfc__ppw = dtdfc__ppw[1:]
        cqce__qoy = dtdfc__ppw.split('/')
        if len(cqce__qoy) == 2:
            pxyy__ugzax, schema = cqce__qoy
        elif len(cqce__qoy) == 1:
            pxyy__ugzax = cqce__qoy[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        punin__xxq['database'] = pxyy__ugzax
        if schema:
            punin__xxq['schema'] = schema
    if cbv__fsyxf.query:
        for ogxt__alt, wvs__rwok in parse_qsl(cbv__fsyxf.query):
            punin__xxq[ogxt__alt] = wvs__rwok
            if ogxt__alt == 'session_parameters':
                punin__xxq[ogxt__alt] = json.loads(wvs__rwok)
    punin__xxq['application'] = 'bodo'
    return punin__xxq


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for lcav__fnbs in batches:
            lcav__fnbs._bodo_num_rows = lcav__fnbs.rowcount
            self._bodo_total_rows += lcav__fnbs._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    opjvo__mzw = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    orxli__qkpl = MPI.COMM_WORLD
    qla__ize = tracing.Event('snowflake_connect', is_parallel=False)
    tszrf__ypyn = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**tszrf__ypyn)
    qla__ize.finalize()
    if bodo.get_rank() == 0:
        wfan__guef = conn.cursor()
        tfs__gegj = tracing.Event('get_schema', is_parallel=False)
        gwzcw__qhl = f'select * from ({query}) x LIMIT {100}'
        ywi__gvrx = wfan__guef.execute(gwzcw__qhl).fetch_arrow_all()
        if ywi__gvrx is None:
            vlfzc__whbtf = wfan__guef.describe(query)
            nbamy__hjgst = [pa.field(ksz__fxxef.name, FIELD_TYPE_TO_PA_TYPE
                [ksz__fxxef.type_code]) for ksz__fxxef in vlfzc__whbtf]
            schema = pa.schema(nbamy__hjgst)
        else:
            schema = ywi__gvrx.schema
        tfs__gegj.finalize()
        ynpn__vqxp = tracing.Event('execute_query', is_parallel=False)
        wfan__guef.execute(query)
        ynpn__vqxp.finalize()
        batches = wfan__guef.get_result_batches()
        orxli__qkpl.bcast((batches, schema))
    else:
        batches, schema = orxli__qkpl.bcast(None)
    gbebd__ziycs = SnowflakeDataset(batches, schema, conn)
    opjvo__mzw.finalize()
    return gbebd__ziycs
