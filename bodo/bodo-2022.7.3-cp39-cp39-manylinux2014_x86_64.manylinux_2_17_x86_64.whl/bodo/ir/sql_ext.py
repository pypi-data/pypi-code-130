"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
from typing import List, Optional
from urllib.parse import urlparse
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.table import Table, TableType
from bodo.io.helpers import PyArrowTableSchemaType, is_nullable
from bodo.io.parquet_pio import ParquetPredicateType
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc,
        unsupported_columns, unsupported_arrow_types, is_select_query,
        index_column_name, index_column_type, database_schema,
        pyarrow_table_schema=None):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None
        self.unsupported_columns = unsupported_columns
        self.unsupported_arrow_types = unsupported_arrow_types
        self.is_select_query = is_select_query
        self.index_column_name = index_column_name
        self.index_column_type = index_column_type
        self.out_used_cols = list(range(len(df_colnames)))
        self.database_schema = database_schema
        self.pyarrow_table_schema = pyarrow_table_schema

    def __repr__(self):
        return (
            f'{self.df_out} = ReadSql(sql_request={self.sql_request}, connection={self.connection}, col_names={self.df_colnames}, types={self.out_types}, vars={self.out_vars}, limit={self.limit}, unsupported_columns={self.unsupported_columns}, unsupported_arrow_types={self.unsupported_arrow_types}, is_select_query={self.is_select_query}, index_column_name={self.index_column_name}, index_column_type={self.index_column_type}, out_used_cols={self.out_used_cols}, database_schema={self.database_schema}, pyarrow_table_schema={self.pyarrow_table_schema})'
            )


def parse_dbtype(con_str):
    qos__iqarm = urlparse(con_str)
    db_type = qos__iqarm.scheme
    kmsig__tub = qos__iqarm.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', kmsig__tub
    if db_type == 'mysql+pymysql':
        return 'mysql', kmsig__tub
    if con_str == 'iceberg+glue' or qos__iqarm.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', kmsig__tub
    return db_type, kmsig__tub


def remove_iceberg_prefix(con):
    import sys
    if sys.version_info.minor < 9:
        if con.startswith('iceberg+'):
            con = con[len('iceberg+'):]
        if con.startswith('iceberg://'):
            con = con[len('iceberg://'):]
    else:
        con = con.removeprefix('iceberg+').removeprefix('iceberg://')
    return con


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    snm__pvhsv = sql_node.out_vars[0].name
    ngj__apl = sql_node.out_vars[1].name
    if snm__pvhsv not in lives and ngj__apl not in lives:
        return None
    elif snm__pvhsv not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif ngj__apl not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx, meta_head_only_info=None):
    if bodo.user_logging.get_verbose_level() >= 1:
        oer__ylmfd = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        gswsq__rlu = []
        mmn__azy = []
        for bxyrx__jzmdx in sql_node.out_used_cols:
            uek__rqr = sql_node.df_colnames[bxyrx__jzmdx]
            gswsq__rlu.append(uek__rqr)
            if isinstance(sql_node.out_types[bxyrx__jzmdx], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                mmn__azy.append(uek__rqr)
        if sql_node.index_column_name:
            gswsq__rlu.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                mmn__azy.append(sql_node.index_column_name)
        qzedd__writf = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', oer__ylmfd,
            qzedd__writf, gswsq__rlu)
        if mmn__azy:
            dybkh__awmu = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                dybkh__awmu, qzedd__writf, mmn__azy)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        vnqf__nby = set(sql_node.unsupported_columns)
        ojkz__mail = set(sql_node.out_used_cols)
        npxd__qrjhj = ojkz__mail & vnqf__nby
        if npxd__qrjhj:
            edl__izme = sorted(npxd__qrjhj)
            iofa__tpnow = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            ononz__fnsk = 0
            for vpeya__zuho in edl__izme:
                while sql_node.unsupported_columns[ononz__fnsk] != vpeya__zuho:
                    ononz__fnsk += 1
                iofa__tpnow.append(
                    f"Column '{sql_node.original_df_colnames[vpeya__zuho]}' with unsupported arrow type {sql_node.unsupported_arrow_types[ononz__fnsk]}"
                    )
                ononz__fnsk += 1
            fib__cuia = '\n'.join(iofa__tpnow)
            raise BodoError(fib__cuia, loc=sql_node.loc)
    wcmr__gfiay, laa__eft = bodo.ir.connector.generate_filter_map(sql_node.
        filters)
    eyxw__hylnp = ', '.join(wcmr__gfiay.values())
    ptae__aydf = (
        f'def sql_impl(sql_request, conn, database_schema, {eyxw__hylnp}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        mwbfv__pnpd = []
        for porz__hqbls in sql_node.filters:
            tbi__qhnfz = []
            for fmswp__hbcjm in porz__hqbls:
                ibyyb__toyqr = '{' + wcmr__gfiay[fmswp__hbcjm[2].name
                    ] + '}' if isinstance(fmswp__hbcjm[2], ir.Var
                    ) else fmswp__hbcjm[2]
                if fmswp__hbcjm[1] in ('startswith', 'endswith'):
                    ykgza__dncvp = ['(', fmswp__hbcjm[1], '(', fmswp__hbcjm
                        [0], ',', ibyyb__toyqr, ')', ')']
                else:
                    ykgza__dncvp = ['(', fmswp__hbcjm[0], fmswp__hbcjm[1],
                        ibyyb__toyqr, ')']
                tbi__qhnfz.append(' '.join(ykgza__dncvp))
            mwbfv__pnpd.append(' ( ' + ' AND '.join(tbi__qhnfz) + ' ) ')
        kybm__yvwhb = ' WHERE ' + ' OR '.join(mwbfv__pnpd)
        for bxyrx__jzmdx, msprb__rujh in enumerate(wcmr__gfiay.values()):
            ptae__aydf += (
                f'    {msprb__rujh} = get_sql_literal({msprb__rujh})\n')
        ptae__aydf += f'    sql_request = f"{{sql_request}} {kybm__yvwhb}"\n'
    cag__dwho = ''
    if sql_node.db_type == 'iceberg':
        cag__dwho = eyxw__hylnp
    ptae__aydf += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {cag__dwho})
"""
    ohqx__hps = {}
    exec(ptae__aydf, {}, ohqx__hps)
    uxd__xav = ohqx__hps['sql_impl']
    if sql_node.limit is not None:
        limit = sql_node.limit
    elif meta_head_only_info and meta_head_only_info[0] is not None:
        limit = meta_head_only_info[0]
    else:
        limit = None
    gmqu__djoz = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    fzz__cnhz = types.none if sql_node.database_schema is None else string_type
    tftiq__smf = compile_to_numba_ir(uxd__xav, {'_sql_reader_py':
        gmqu__djoz, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, fzz__cnhz) +
        tuple(typemap[loarn__kmfk.name] for loarn__kmfk in laa__eft),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        agmv__lmpd = [sql_node.df_colnames[bxyrx__jzmdx] for bxyrx__jzmdx in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            agmv__lmpd.append(sql_node.index_column_name)
        rcrr__vxa = escape_column_names(agmv__lmpd, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            bwcn__nbfpl = ('SELECT ' + rcrr__vxa + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            bwcn__nbfpl = ('SELECT ' + rcrr__vxa + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        bwcn__nbfpl = sql_node.sql_request
    replace_arg_nodes(tftiq__smf, [ir.Const(bwcn__nbfpl, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + laa__eft)
    rotk__fqb = tftiq__smf.body[:-3]
    rotk__fqb[-2].target = sql_node.out_vars[0]
    rotk__fqb[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        rotk__fqb.pop(-1)
    elif not sql_node.out_used_cols:
        rotk__fqb.pop(-2)
    return rotk__fqb


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        agmv__lmpd = [(hgxt__rxyyl.upper() if hgxt__rxyyl in
            converted_colnames else hgxt__rxyyl) for hgxt__rxyyl in col_names]
        rcrr__vxa = ', '.join([f'"{hgxt__rxyyl}"' for hgxt__rxyyl in
            agmv__lmpd])
    elif db_type == 'mysql':
        rcrr__vxa = ', '.join([f'`{hgxt__rxyyl}`' for hgxt__rxyyl in col_names]
            )
    else:
        rcrr__vxa = ', '.join([f'"{hgxt__rxyyl}"' for hgxt__rxyyl in col_names]
            )
    return rcrr__vxa


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    bab__djz = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(bab__djz,
        'Filter pushdown')
    if bab__djz == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(bab__djz, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif bab__djz == bodo.pd_timestamp_type:

        def impl(filter_value):
            qyxfp__txml = filter_value.nanosecond
            xeuqw__mxsu = ''
            if qyxfp__txml < 10:
                xeuqw__mxsu = '00'
            elif qyxfp__txml < 100:
                xeuqw__mxsu = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{xeuqw__mxsu}{qyxfp__txml}'"
                )
        return impl
    elif bab__djz == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {bab__djz} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    nqk__uetec = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    bab__djz = types.unliteral(filter_value)
    if isinstance(bab__djz, types.List) and (isinstance(bab__djz.dtype,
        scalar_isinstance) or bab__djz.dtype in nqk__uetec):

        def impl(filter_value):
            carg__clx = ', '.join([_get_snowflake_sql_literal_scalar(
                hgxt__rxyyl) for hgxt__rxyyl in filter_value])
            return f'({carg__clx})'
        return impl
    elif isinstance(bab__djz, scalar_isinstance) or bab__djz in nqk__uetec:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {bab__djz} used in filter pushdown.'
            )


def sql_remove_dead_column(sql_node, column_live_map, equiv_vars, typemap):
    return bodo.ir.connector.base_connector_remove_dead_columns(sql_node,
        column_live_map, equiv_vars, typemap, 'SQLReader', sql_node.df_colnames
        )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
remove_dead_column_extensions[SqlReader] = sql_remove_dead_column
ir_extension_table_column_use[SqlReader
    ] = bodo.ir.connector.connector_table_column_use
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as kuxyn__ovpjt:
        tmnof__lmfan = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(tmnof__lmfan)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as kuxyn__ovpjt:
        tmnof__lmfan = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(tmnof__lmfan)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as kuxyn__ovpjt:
        tmnof__lmfan = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(tmnof__lmfan)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as kuxyn__ovpjt:
        tmnof__lmfan = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(tmnof__lmfan)


def req_limit(sql_request):
    import re
    ppj__xyym = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    slie__hci = ppj__xyym.search(sql_request)
    if slie__hci:
        return int(slie__hci.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type: str, limit: Optional[int], parallel, typemap, filters,
    pyarrow_table_schema: 'Optional[pyarrow.Schema]'):
    ina__bhkpo = next_label()
    agmv__lmpd = [col_names[bxyrx__jzmdx] for bxyrx__jzmdx in out_used_cols]
    tpex__bzolf = [col_typs[bxyrx__jzmdx] for bxyrx__jzmdx in out_used_cols]
    if index_column_name:
        agmv__lmpd.append(index_column_name)
        tpex__bzolf.append(index_column_type)
    njcl__csio = None
    itz__kvrqf = None
    iwnkz__zokl = TableType(tuple(col_typs)) if out_used_cols else types.none
    cag__dwho = ''
    wcmr__gfiay = {}
    laa__eft = []
    if filters and db_type == 'iceberg':
        wcmr__gfiay, laa__eft = bodo.ir.connector.generate_filter_map(filters)
        cag__dwho = ', '.join(wcmr__gfiay.values())
    ptae__aydf = (
        f'def sql_reader_py(sql_request, conn, database_schema, {cag__dwho}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        aiod__team, diz__umw = bodo.ir.connector.generate_arrow_filters(filters
            , wcmr__gfiay, laa__eft, col_names, col_names, col_typs,
            typemap, 'iceberg')
        adnt__fvwa: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[bxyrx__jzmdx]) for bxyrx__jzmdx in out_used_cols]
        sxb__tazdm = {joduu__hdtb: bxyrx__jzmdx for bxyrx__jzmdx,
            joduu__hdtb in enumerate(adnt__fvwa)}
        cpfxd__snjf = [int(is_nullable(col_typs[bxyrx__jzmdx])) for
            bxyrx__jzmdx in adnt__fvwa]
        uwfbb__adu = ',' if cag__dwho else ''
        ptae__aydf += f"""  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})
  dnf_filters, expr_filters = get_filters_pyobject("{aiod__team}", "{diz__umw}", ({cag__dwho}{uwfbb__adu}))
  out_table = iceberg_read(
    unicode_to_utf8(conn),
    unicode_to_utf8(database_schema),
    unicode_to_utf8(sql_request),
    {parallel},
    {-1 if limit is None else limit},
    dnf_filters,
    expr_filters,
    selected_cols_arr_{ina__bhkpo}.ctypes,
    {len(adnt__fvwa)},
    nullable_cols_arr_{ina__bhkpo}.ctypes,
    pyarrow_table_schema_{ina__bhkpo},
  )
  check_and_propagate_cpp_exception()
"""
        xroc__cby = not out_used_cols
        iwnkz__zokl = TableType(tuple(col_typs))
        if xroc__cby:
            iwnkz__zokl = types.none
        ngj__apl = 'None'
        if index_column_name is not None:
            bozwf__lpiem = len(out_used_cols) + 1 if not xroc__cby else 0
            ngj__apl = (
                f'info_to_array(info_from_table(out_table, {bozwf__lpiem}), index_col_typ)'
                )
        ptae__aydf += f'  index_var = {ngj__apl}\n'
        njcl__csio = None
        if not xroc__cby:
            njcl__csio = []
            cjo__qgab = 0
            for bxyrx__jzmdx in range(len(col_names)):
                if cjo__qgab < len(out_used_cols
                    ) and bxyrx__jzmdx == out_used_cols[cjo__qgab]:
                    njcl__csio.append(sxb__tazdm[bxyrx__jzmdx])
                    cjo__qgab += 1
                else:
                    njcl__csio.append(-1)
            njcl__csio = np.array(njcl__csio, dtype=np.int64)
        if xroc__cby:
            ptae__aydf += '  table_var = None\n'
        else:
            ptae__aydf += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ina__bhkpo}, py_table_type_{ina__bhkpo})
"""
        ptae__aydf += f'  delete_table(out_table)\n'
        ptae__aydf += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        ptae__aydf += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        cpfxd__snjf = [int(is_nullable(col_typs[bxyrx__jzmdx])) for
            bxyrx__jzmdx in out_used_cols]
        if index_column_name:
            cpfxd__snjf.append(int(is_nullable(index_column_type)))
        ptae__aydf += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(cpfxd__snjf)}, np.array({cpfxd__snjf}, dtype=np.int32).ctypes)
"""
        ptae__aydf += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            ptae__aydf += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            ptae__aydf += '  index_var = None\n'
        if out_used_cols:
            ononz__fnsk = []
            cjo__qgab = 0
            for bxyrx__jzmdx in range(len(col_names)):
                if cjo__qgab < len(out_used_cols
                    ) and bxyrx__jzmdx == out_used_cols[cjo__qgab]:
                    ononz__fnsk.append(cjo__qgab)
                    cjo__qgab += 1
                else:
                    ononz__fnsk.append(-1)
            njcl__csio = np.array(ononz__fnsk, dtype=np.int64)
            ptae__aydf += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ina__bhkpo}, py_table_type_{ina__bhkpo})
"""
        else:
            ptae__aydf += '  table_var = None\n'
        ptae__aydf += '  delete_table(out_table)\n'
        ptae__aydf += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            ptae__aydf += f"""  type_usecols_offsets_arr_{ina__bhkpo}_2 = type_usecols_offsets_arr_{ina__bhkpo}
"""
            itz__kvrqf = np.array(out_used_cols, dtype=np.int64)
        ptae__aydf += '  df_typeref_2 = df_typeref\n'
        ptae__aydf += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            ptae__aydf += '  pymysql_check()\n'
        elif db_type == 'oracle':
            ptae__aydf += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            ptae__aydf += '  psycopg2_check()\n'
        if parallel:
            ptae__aydf += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                ptae__aydf += f'  nb_row = {limit}\n'
            else:
                ptae__aydf += '  with objmode(nb_row="int64"):\n'
                ptae__aydf += f'     if rank == {MPI_ROOT}:\n'
                ptae__aydf += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                ptae__aydf += '         frame = pd.read_sql(sql_cons, conn)\n'
                ptae__aydf += '         nb_row = frame.iat[0,0]\n'
                ptae__aydf += '     else:\n'
                ptae__aydf += '         nb_row = 0\n'
                ptae__aydf += '  nb_row = bcast_scalar(nb_row)\n'
            ptae__aydf += f"""  with objmode(table_var=py_table_type_{ina__bhkpo}, index_var=index_col_typ):
"""
            ptae__aydf += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                ptae__aydf += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                ptae__aydf += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            ptae__aydf += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            ptae__aydf += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            ptae__aydf += f"""  with objmode(table_var=py_table_type_{ina__bhkpo}, index_var=index_col_typ):
"""
            ptae__aydf += '    df_ret = pd.read_sql(sql_request, conn)\n'
            ptae__aydf += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            ptae__aydf += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            ptae__aydf += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            ptae__aydf += '    index_var = None\n'
        if out_used_cols:
            ptae__aydf += f'    arrs = []\n'
            ptae__aydf += f'    for i in range(df_ret.shape[1]):\n'
            ptae__aydf += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            ptae__aydf += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{ina__bhkpo}_2, {len(col_names)})
"""
        else:
            ptae__aydf += '    table_var = None\n'
    ptae__aydf += '  return (table_var, index_var)\n'
    ouv__wyqem = globals()
    ouv__wyqem.update({'bodo': bodo, f'py_table_type_{ina__bhkpo}':
        iwnkz__zokl, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        ouv__wyqem.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{ina__bhkpo}': njcl__csio})
    if db_type == 'iceberg':
        ouv__wyqem.update({f'selected_cols_arr_{ina__bhkpo}': np.array(
            adnt__fvwa, np.int32), f'nullable_cols_arr_{ina__bhkpo}': np.
            array(cpfxd__snjf, np.int32), f'py_table_type_{ina__bhkpo}':
            iwnkz__zokl, f'pyarrow_table_schema_{ina__bhkpo}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        ouv__wyqem.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        ouv__wyqem.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(tpex__bzolf), bodo.RangeIndexType(None
            ), tuple(agmv__lmpd)), 'Table': Table,
            f'type_usecols_offsets_arr_{ina__bhkpo}': itz__kvrqf})
    ohqx__hps = {}
    exec(ptae__aydf, ouv__wyqem, ohqx__hps)
    gmqu__djoz = ohqx__hps['sql_reader_py']
    yvq__rsx = numba.njit(gmqu__djoz)
    compiled_funcs.append(yvq__rsx)
    return yvq__rsx


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean, types.int32,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
