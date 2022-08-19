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
    rolh__yuh = urlparse(con_str)
    db_type = rolh__yuh.scheme
    wkcw__meqy = rolh__yuh.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', wkcw__meqy
    if db_type == 'mysql+pymysql':
        return 'mysql', wkcw__meqy
    if con_str == 'iceberg+glue' or rolh__yuh.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', wkcw__meqy
    return db_type, wkcw__meqy


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
    zcujc__kmf = sql_node.out_vars[0].name
    zeekx__ezmfd = sql_node.out_vars[1].name
    if zcujc__kmf not in lives and zeekx__ezmfd not in lives:
        return None
    elif zcujc__kmf not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif zeekx__ezmfd not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx, meta_head_only_info=None):
    if bodo.user_logging.get_verbose_level() >= 1:
        xbani__hvan = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        mppu__cduu = []
        umnwt__rnp = []
        for hcl__fbbh in sql_node.out_used_cols:
            yczl__tdpmz = sql_node.df_colnames[hcl__fbbh]
            mppu__cduu.append(yczl__tdpmz)
            if isinstance(sql_node.out_types[hcl__fbbh], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                umnwt__rnp.append(yczl__tdpmz)
        if sql_node.index_column_name:
            mppu__cduu.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                umnwt__rnp.append(sql_node.index_column_name)
        grq__kfuk = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', xbani__hvan,
            grq__kfuk, mppu__cduu)
        if umnwt__rnp:
            fyxj__cru = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', fyxj__cru,
                grq__kfuk, umnwt__rnp)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        ooc__wwvma = set(sql_node.unsupported_columns)
        zwkne__pxs = set(sql_node.out_used_cols)
        ifbp__hsc = zwkne__pxs & ooc__wwvma
        if ifbp__hsc:
            bqtn__uev = sorted(ifbp__hsc)
            sgs__iwi = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            wwc__bfgpr = 0
            for oqs__wzje in bqtn__uev:
                while sql_node.unsupported_columns[wwc__bfgpr] != oqs__wzje:
                    wwc__bfgpr += 1
                sgs__iwi.append(
                    f"Column '{sql_node.original_df_colnames[oqs__wzje]}' with unsupported arrow type {sql_node.unsupported_arrow_types[wwc__bfgpr]}"
                    )
                wwc__bfgpr += 1
            pbpwh__yztm = '\n'.join(sgs__iwi)
            raise BodoError(pbpwh__yztm, loc=sql_node.loc)
    eeb__dsqc, fib__sjzn = bodo.ir.connector.generate_filter_map(sql_node.
        filters)
    hzb__rii = ', '.join(eeb__dsqc.values())
    oppnj__rgpyi = (
        f'def sql_impl(sql_request, conn, database_schema, {hzb__rii}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        cdjt__rjygi = []
        for uxcom__kanti in sql_node.filters:
            qxh__rau = []
            for epdhn__vmena in uxcom__kanti:
                eplh__inum = '{' + eeb__dsqc[epdhn__vmena[2].name
                    ] + '}' if isinstance(epdhn__vmena[2], ir.Var
                    ) else epdhn__vmena[2]
                if epdhn__vmena[1] in ('startswith', 'endswith'):
                    psmgh__qiff = ['(', epdhn__vmena[1], '(', epdhn__vmena[
                        0], ',', eplh__inum, ')', ')']
                else:
                    psmgh__qiff = ['(', epdhn__vmena[0], epdhn__vmena[1],
                        eplh__inum, ')']
                qxh__rau.append(' '.join(psmgh__qiff))
            cdjt__rjygi.append(' ( ' + ' AND '.join(qxh__rau) + ' ) ')
        sdq__iazh = ' WHERE ' + ' OR '.join(cdjt__rjygi)
        for hcl__fbbh, mpq__ofjf in enumerate(eeb__dsqc.values()):
            oppnj__rgpyi += f'    {mpq__ofjf} = get_sql_literal({mpq__ofjf})\n'
        oppnj__rgpyi += f'    sql_request = f"{{sql_request}} {sdq__iazh}"\n'
    bwwoh__uaf = ''
    if sql_node.db_type == 'iceberg':
        bwwoh__uaf = hzb__rii
    oppnj__rgpyi += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {bwwoh__uaf})
"""
    hjjn__jtw = {}
    exec(oppnj__rgpyi, {}, hjjn__jtw)
    wkr__cgcyi = hjjn__jtw['sql_impl']
    if sql_node.limit is not None:
        limit = sql_node.limit
    elif meta_head_only_info and meta_head_only_info[0] is not None:
        limit = meta_head_only_info[0]
    else:
        limit = None
    lqrao__jmkt = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    nry__ygwtv = (types.none if sql_node.database_schema is None else
        string_type)
    mbud__fvuwj = compile_to_numba_ir(wkr__cgcyi, {'_sql_reader_py':
        lqrao__jmkt, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, nry__ygwtv
        ) + tuple(typemap[hawx__cfmon.name] for hawx__cfmon in fib__sjzn),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        gtmkh__yhasl = [sql_node.df_colnames[hcl__fbbh] for hcl__fbbh in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            gtmkh__yhasl.append(sql_node.index_column_name)
        ela__gdper = escape_column_names(gtmkh__yhasl, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            ajoqx__ajeav = ('SELECT ' + ela__gdper + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            ajoqx__ajeav = ('SELECT ' + ela__gdper + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        ajoqx__ajeav = sql_node.sql_request
    replace_arg_nodes(mbud__fvuwj, [ir.Const(ajoqx__ajeav, sql_node.loc),
        ir.Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + fib__sjzn)
    ahs__epuut = mbud__fvuwj.body[:-3]
    ahs__epuut[-2].target = sql_node.out_vars[0]
    ahs__epuut[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        ahs__epuut.pop(-1)
    elif not sql_node.out_used_cols:
        ahs__epuut.pop(-2)
    return ahs__epuut


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        gtmkh__yhasl = [(igz__zhk.upper() if igz__zhk in converted_colnames
             else igz__zhk) for igz__zhk in col_names]
        ela__gdper = ', '.join([f'"{igz__zhk}"' for igz__zhk in gtmkh__yhasl])
    elif db_type == 'mysql':
        ela__gdper = ', '.join([f'`{igz__zhk}`' for igz__zhk in col_names])
    else:
        ela__gdper = ', '.join([f'"{igz__zhk}"' for igz__zhk in col_names])
    return ela__gdper


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    auppe__qodi = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(auppe__qodi,
        'Filter pushdown')
    if auppe__qodi == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(auppe__qodi, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif auppe__qodi == bodo.pd_timestamp_type:

        def impl(filter_value):
            xni__udkrx = filter_value.nanosecond
            gbgx__lnadu = ''
            if xni__udkrx < 10:
                gbgx__lnadu = '00'
            elif xni__udkrx < 100:
                gbgx__lnadu = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{gbgx__lnadu}{xni__udkrx}'"
                )
        return impl
    elif auppe__qodi == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {auppe__qodi} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    iwnwy__dfx = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    auppe__qodi = types.unliteral(filter_value)
    if isinstance(auppe__qodi, types.List) and (isinstance(auppe__qodi.
        dtype, scalar_isinstance) or auppe__qodi.dtype in iwnwy__dfx):

        def impl(filter_value):
            qhmfr__kwd = ', '.join([_get_snowflake_sql_literal_scalar(
                igz__zhk) for igz__zhk in filter_value])
            return f'({qhmfr__kwd})'
        return impl
    elif isinstance(auppe__qodi, scalar_isinstance
        ) or auppe__qodi in iwnwy__dfx:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {auppe__qodi} used in filter pushdown.'
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
    except ImportError as gii__buvf:
        zgre__gba = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(zgre__gba)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as gii__buvf:
        zgre__gba = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(zgre__gba)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as gii__buvf:
        zgre__gba = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(zgre__gba)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as gii__buvf:
        zgre__gba = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(zgre__gba)


def req_limit(sql_request):
    import re
    vvg__wzi = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    cvlv__avx = vvg__wzi.search(sql_request)
    if cvlv__avx:
        return int(cvlv__avx.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type: str, limit: Optional[int], parallel, typemap, filters,
    pyarrow_table_schema: 'Optional[pyarrow.Schema]'):
    eafvw__kwrt = next_label()
    gtmkh__yhasl = [col_names[hcl__fbbh] for hcl__fbbh in out_used_cols]
    jwbvw__atx = [col_typs[hcl__fbbh] for hcl__fbbh in out_used_cols]
    if index_column_name:
        gtmkh__yhasl.append(index_column_name)
        jwbvw__atx.append(index_column_type)
    djhf__uzdy = None
    kllp__oekh = None
    qwxyb__lwko = TableType(tuple(col_typs)) if out_used_cols else types.none
    bwwoh__uaf = ''
    eeb__dsqc = {}
    fib__sjzn = []
    if filters and db_type == 'iceberg':
        eeb__dsqc, fib__sjzn = bodo.ir.connector.generate_filter_map(filters)
        bwwoh__uaf = ', '.join(eeb__dsqc.values())
    oppnj__rgpyi = (
        f'def sql_reader_py(sql_request, conn, database_schema, {bwwoh__uaf}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        bmr__dagvb, akt__cyk = bodo.ir.connector.generate_arrow_filters(filters
            , eeb__dsqc, fib__sjzn, col_names, col_names, col_typs, typemap,
            'iceberg')
        kvwn__ahyi: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[hcl__fbbh]) for hcl__fbbh in out_used_cols]
        faj__yphmd = {kjol__jzoty: hcl__fbbh for hcl__fbbh, kjol__jzoty in
            enumerate(kvwn__ahyi)}
        gmfud__ncd = [int(is_nullable(col_typs[hcl__fbbh])) for hcl__fbbh in
            kvwn__ahyi]
        vsqg__rbbe = ',' if bwwoh__uaf else ''
        oppnj__rgpyi += f"""  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})
  dnf_filters, expr_filters = get_filters_pyobject("{bmr__dagvb}", "{akt__cyk}", ({bwwoh__uaf}{vsqg__rbbe}))
  out_table = iceberg_read(
    unicode_to_utf8(conn),
    unicode_to_utf8(database_schema),
    unicode_to_utf8(sql_request),
    {parallel},
    {-1 if limit is None else limit},
    dnf_filters,
    expr_filters,
    selected_cols_arr_{eafvw__kwrt}.ctypes,
    {len(kvwn__ahyi)},
    nullable_cols_arr_{eafvw__kwrt}.ctypes,
    pyarrow_table_schema_{eafvw__kwrt},
  )
  check_and_propagate_cpp_exception()
"""
        ukqwm__rifjb = not out_used_cols
        qwxyb__lwko = TableType(tuple(col_typs))
        if ukqwm__rifjb:
            qwxyb__lwko = types.none
        zeekx__ezmfd = 'None'
        if index_column_name is not None:
            phcj__oogv = len(out_used_cols) + 1 if not ukqwm__rifjb else 0
            zeekx__ezmfd = (
                f'info_to_array(info_from_table(out_table, {phcj__oogv}), index_col_typ)'
                )
        oppnj__rgpyi += f'  index_var = {zeekx__ezmfd}\n'
        djhf__uzdy = None
        if not ukqwm__rifjb:
            djhf__uzdy = []
            etl__touz = 0
            for hcl__fbbh in range(len(col_names)):
                if etl__touz < len(out_used_cols
                    ) and hcl__fbbh == out_used_cols[etl__touz]:
                    djhf__uzdy.append(faj__yphmd[hcl__fbbh])
                    etl__touz += 1
                else:
                    djhf__uzdy.append(-1)
            djhf__uzdy = np.array(djhf__uzdy, dtype=np.int64)
        if ukqwm__rifjb:
            oppnj__rgpyi += '  table_var = None\n'
        else:
            oppnj__rgpyi += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{eafvw__kwrt}, py_table_type_{eafvw__kwrt})
"""
        oppnj__rgpyi += f'  delete_table(out_table)\n'
        oppnj__rgpyi += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        oppnj__rgpyi += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        gmfud__ncd = [int(is_nullable(col_typs[hcl__fbbh])) for hcl__fbbh in
            out_used_cols]
        if index_column_name:
            gmfud__ncd.append(int(is_nullable(index_column_type)))
        oppnj__rgpyi += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(gmfud__ncd)}, np.array({gmfud__ncd}, dtype=np.int32).ctypes)
"""
        oppnj__rgpyi += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            oppnj__rgpyi += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            oppnj__rgpyi += '  index_var = None\n'
        if out_used_cols:
            wwc__bfgpr = []
            etl__touz = 0
            for hcl__fbbh in range(len(col_names)):
                if etl__touz < len(out_used_cols
                    ) and hcl__fbbh == out_used_cols[etl__touz]:
                    wwc__bfgpr.append(etl__touz)
                    etl__touz += 1
                else:
                    wwc__bfgpr.append(-1)
            djhf__uzdy = np.array(wwc__bfgpr, dtype=np.int64)
            oppnj__rgpyi += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{eafvw__kwrt}, py_table_type_{eafvw__kwrt})
"""
        else:
            oppnj__rgpyi += '  table_var = None\n'
        oppnj__rgpyi += '  delete_table(out_table)\n'
        oppnj__rgpyi += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            oppnj__rgpyi += f"""  type_usecols_offsets_arr_{eafvw__kwrt}_2 = type_usecols_offsets_arr_{eafvw__kwrt}
"""
            kllp__oekh = np.array(out_used_cols, dtype=np.int64)
        oppnj__rgpyi += '  df_typeref_2 = df_typeref\n'
        oppnj__rgpyi += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            oppnj__rgpyi += '  pymysql_check()\n'
        elif db_type == 'oracle':
            oppnj__rgpyi += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            oppnj__rgpyi += '  psycopg2_check()\n'
        if parallel:
            oppnj__rgpyi += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                oppnj__rgpyi += f'  nb_row = {limit}\n'
            else:
                oppnj__rgpyi += '  with objmode(nb_row="int64"):\n'
                oppnj__rgpyi += f'     if rank == {MPI_ROOT}:\n'
                oppnj__rgpyi += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                oppnj__rgpyi += (
                    '         frame = pd.read_sql(sql_cons, conn)\n')
                oppnj__rgpyi += '         nb_row = frame.iat[0,0]\n'
                oppnj__rgpyi += '     else:\n'
                oppnj__rgpyi += '         nb_row = 0\n'
                oppnj__rgpyi += '  nb_row = bcast_scalar(nb_row)\n'
            oppnj__rgpyi += f"""  with objmode(table_var=py_table_type_{eafvw__kwrt}, index_var=index_col_typ):
"""
            oppnj__rgpyi += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                oppnj__rgpyi += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                oppnj__rgpyi += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            oppnj__rgpyi += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            oppnj__rgpyi += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            oppnj__rgpyi += f"""  with objmode(table_var=py_table_type_{eafvw__kwrt}, index_var=index_col_typ):
"""
            oppnj__rgpyi += '    df_ret = pd.read_sql(sql_request, conn)\n'
            oppnj__rgpyi += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            oppnj__rgpyi += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            oppnj__rgpyi += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            oppnj__rgpyi += '    index_var = None\n'
        if out_used_cols:
            oppnj__rgpyi += f'    arrs = []\n'
            oppnj__rgpyi += f'    for i in range(df_ret.shape[1]):\n'
            oppnj__rgpyi += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            oppnj__rgpyi += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{eafvw__kwrt}_2, {len(col_names)})
"""
        else:
            oppnj__rgpyi += '    table_var = None\n'
    oppnj__rgpyi += '  return (table_var, index_var)\n'
    hdvo__hho = globals()
    hdvo__hho.update({'bodo': bodo, f'py_table_type_{eafvw__kwrt}':
        qwxyb__lwko, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        hdvo__hho.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{eafvw__kwrt}': djhf__uzdy})
    if db_type == 'iceberg':
        hdvo__hho.update({f'selected_cols_arr_{eafvw__kwrt}': np.array(
            kvwn__ahyi, np.int32), f'nullable_cols_arr_{eafvw__kwrt}': np.
            array(gmfud__ncd, np.int32), f'py_table_type_{eafvw__kwrt}':
            qwxyb__lwko, f'pyarrow_table_schema_{eafvw__kwrt}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        hdvo__hho.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        hdvo__hho.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(jwbvw__atx), bodo.RangeIndexType(None),
            tuple(gtmkh__yhasl)), 'Table': Table,
            f'type_usecols_offsets_arr_{eafvw__kwrt}': kllp__oekh})
    hjjn__jtw = {}
    exec(oppnj__rgpyi, hdvo__hho, hjjn__jtw)
    lqrao__jmkt = hjjn__jtw['sql_reader_py']
    mvut__wft = numba.njit(lqrao__jmkt)
    compiled_funcs.append(mvut__wft)
    return mvut__wft


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
