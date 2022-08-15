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
    loltk__fzken = urlparse(conn_str)
    drara__uifqj = {}
    if loltk__fzken.username:
        drara__uifqj['user'] = loltk__fzken.username
    if loltk__fzken.password:
        drara__uifqj['password'] = loltk__fzken.password
    if loltk__fzken.hostname:
        drara__uifqj['account'] = loltk__fzken.hostname
    if loltk__fzken.port:
        drara__uifqj['port'] = loltk__fzken.port
    if loltk__fzken.path:
        hyj__hfx = loltk__fzken.path
        if hyj__hfx.startswith('/'):
            hyj__hfx = hyj__hfx[1:]
        btl__maqxw = hyj__hfx.split('/')
        if len(btl__maqxw) == 2:
            tuknc__uhu, schema = btl__maqxw
        elif len(btl__maqxw) == 1:
            tuknc__uhu = btl__maqxw[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        drara__uifqj['database'] = tuknc__uhu
        if schema:
            drara__uifqj['schema'] = schema
    if loltk__fzken.query:
        for yhh__yhy, xkxem__bkpaf in parse_qsl(loltk__fzken.query):
            drara__uifqj[yhh__yhy] = xkxem__bkpaf
            if yhh__yhy == 'session_parameters':
                drara__uifqj[yhh__yhy] = json.loads(xkxem__bkpaf)
    drara__uifqj['application'] = 'bodo'
    return drara__uifqj


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for zhi__ptp in batches:
            zhi__ptp._bodo_num_rows = zhi__ptp.rowcount
            self._bodo_total_rows += zhi__ptp._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    wwb__ibgzx = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    bsur__yqwx = MPI.COMM_WORLD
    hmbjn__cakn = tracing.Event('snowflake_connect', is_parallel=False)
    binhf__nzmy = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**binhf__nzmy)
    hmbjn__cakn.finalize()
    if bodo.get_rank() == 0:
        udvy__xgs = conn.cursor()
        cfctb__ake = tracing.Event('get_schema', is_parallel=False)
        zuq__kmlct = f'select * from ({query}) x LIMIT {100}'
        xct__lnj = udvy__xgs.execute(zuq__kmlct).fetch_arrow_all()
        if xct__lnj is None:
            dwz__dazps = udvy__xgs.describe(query)
            bjya__rslvv = [pa.field(tbew__mkmzh.name, FIELD_TYPE_TO_PA_TYPE
                [tbew__mkmzh.type_code]) for tbew__mkmzh in dwz__dazps]
            schema = pa.schema(bjya__rslvv)
        else:
            schema = xct__lnj.schema
        cfctb__ake.finalize()
        txyna__dxhy = tracing.Event('execute_query', is_parallel=False)
        udvy__xgs.execute(query)
        txyna__dxhy.finalize()
        batches = udvy__xgs.get_result_batches()
        bsur__yqwx.bcast((batches, schema))
    else:
        batches, schema = bsur__yqwx.bcast(None)
    hjv__rxx = SnowflakeDataset(batches, schema, conn)
    wwb__ibgzx.finalize()
    return hjv__rxx
