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
    ahzlf__eys = urlparse(con_str)
    db_type = ahzlf__eys.scheme
    edyb__vwnr = ahzlf__eys.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', edyb__vwnr
    if db_type == 'mysql+pymysql':
        return 'mysql', edyb__vwnr
    if con_str == 'iceberg+glue' or ahzlf__eys.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', edyb__vwnr
    return db_type, edyb__vwnr


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
    csijr__mvrc = sql_node.out_vars[0].name
    ekucl__bwmki = sql_node.out_vars[1].name
    if csijr__mvrc not in lives and ekucl__bwmki not in lives:
        return None
    elif csijr__mvrc not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif ekucl__bwmki not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx, meta_head_only_info=None):
    if bodo.user_logging.get_verbose_level() >= 1:
        zgqji__nqqvq = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        vggh__fkesy = []
        sbqx__bff = []
        for quy__qiaew in sql_node.out_used_cols:
            gxlf__mdht = sql_node.df_colnames[quy__qiaew]
            vggh__fkesy.append(gxlf__mdht)
            if isinstance(sql_node.out_types[quy__qiaew], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                sbqx__bff.append(gxlf__mdht)
        if sql_node.index_column_name:
            vggh__fkesy.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                sbqx__bff.append(sql_node.index_column_name)
        cbp__ipk = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', zgqji__nqqvq,
            cbp__ipk, vggh__fkesy)
        if sbqx__bff:
            iqx__ajg = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', iqx__ajg,
                cbp__ipk, sbqx__bff)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        mnsci__lpxwa = set(sql_node.unsupported_columns)
        ahk__ezdyi = set(sql_node.out_used_cols)
        bvz__vnrt = ahk__ezdyi & mnsci__lpxwa
        if bvz__vnrt:
            wlq__xzarf = sorted(bvz__vnrt)
            nari__jvaav = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            uep__nxb = 0
            for avtu__gbdme in wlq__xzarf:
                while sql_node.unsupported_columns[uep__nxb] != avtu__gbdme:
                    uep__nxb += 1
                nari__jvaav.append(
                    f"Column '{sql_node.original_df_colnames[avtu__gbdme]}' with unsupported arrow type {sql_node.unsupported_arrow_types[uep__nxb]}"
                    )
                uep__nxb += 1
            owh__zmrq = '\n'.join(nari__jvaav)
            raise BodoError(owh__zmrq, loc=sql_node.loc)
    vch__fmbv, jkz__tjd = bodo.ir.connector.generate_filter_map(sql_node.
        filters)
    pwj__bylpt = ', '.join(vch__fmbv.values())
    kvn__dpy = (
        f'def sql_impl(sql_request, conn, database_schema, {pwj__bylpt}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        liw__kqlb = []
        for tbsq__hcg in sql_node.filters:
            pvf__uxj = []
            for aadmx__rvrhj in tbsq__hcg:
                dorcx__jjjx = '{' + vch__fmbv[aadmx__rvrhj[2].name
                    ] + '}' if isinstance(aadmx__rvrhj[2], ir.Var
                    ) else aadmx__rvrhj[2]
                if aadmx__rvrhj[1] in ('startswith', 'endswith'):
                    bhuu__zkrwk = ['(', aadmx__rvrhj[1], '(', aadmx__rvrhj[
                        0], ',', dorcx__jjjx, ')', ')']
                else:
                    bhuu__zkrwk = ['(', aadmx__rvrhj[0], aadmx__rvrhj[1],
                        dorcx__jjjx, ')']
                pvf__uxj.append(' '.join(bhuu__zkrwk))
            liw__kqlb.append(' ( ' + ' AND '.join(pvf__uxj) + ' ) ')
        uzw__ecxe = ' WHERE ' + ' OR '.join(liw__kqlb)
        for quy__qiaew, ccnnq__xvs in enumerate(vch__fmbv.values()):
            kvn__dpy += f'    {ccnnq__xvs} = get_sql_literal({ccnnq__xvs})\n'
        kvn__dpy += f'    sql_request = f"{{sql_request}} {uzw__ecxe}"\n'
    azl__cze = ''
    if sql_node.db_type == 'iceberg':
        azl__cze = pwj__bylpt
    kvn__dpy += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {azl__cze})
"""
    ekdb__erlu = {}
    exec(kvn__dpy, {}, ekdb__erlu)
    xob__tch = ekdb__erlu['sql_impl']
    if sql_node.limit is not None:
        limit = sql_node.limit
    elif meta_head_only_info and meta_head_only_info[0] is not None:
        limit = meta_head_only_info[0]
    else:
        limit = None
    hnlcy__sil = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    stdzr__tfgrf = (types.none if sql_node.database_schema is None else
        string_type)
    gbmg__rjwf = compile_to_numba_ir(xob__tch, {'_sql_reader_py':
        hnlcy__sil, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type,
        stdzr__tfgrf) + tuple(typemap[zmgq__vmm.name] for zmgq__vmm in
        jkz__tjd), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        jjwg__ojjnk = [sql_node.df_colnames[quy__qiaew] for quy__qiaew in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            jjwg__ojjnk.append(sql_node.index_column_name)
        fccif__nis = escape_column_names(jjwg__ojjnk, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            kvqkj__zqmxm = ('SELECT ' + fccif__nis + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            kvqkj__zqmxm = ('SELECT ' + fccif__nis + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        kvqkj__zqmxm = sql_node.sql_request
    replace_arg_nodes(gbmg__rjwf, [ir.Const(kvqkj__zqmxm, sql_node.loc), ir
        .Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + jkz__tjd)
    zliv__rrg = gbmg__rjwf.body[:-3]
    zliv__rrg[-2].target = sql_node.out_vars[0]
    zliv__rrg[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        zliv__rrg.pop(-1)
    elif not sql_node.out_used_cols:
        zliv__rrg.pop(-2)
    return zliv__rrg


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        jjwg__ojjnk = [(cdao__uzulv.upper() if cdao__uzulv in
            converted_colnames else cdao__uzulv) for cdao__uzulv in col_names]
        fccif__nis = ', '.join([f'"{cdao__uzulv}"' for cdao__uzulv in
            jjwg__ojjnk])
    elif db_type == 'mysql':
        fccif__nis = ', '.join([f'`{cdao__uzulv}`' for cdao__uzulv in
            col_names])
    else:
        fccif__nis = ', '.join([f'"{cdao__uzulv}"' for cdao__uzulv in
            col_names])
    return fccif__nis


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    ykfp__mqth = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ykfp__mqth,
        'Filter pushdown')
    if ykfp__mqth == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(ykfp__mqth, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif ykfp__mqth == bodo.pd_timestamp_type:

        def impl(filter_value):
            tvxvm__xes = filter_value.nanosecond
            sjgx__ldg = ''
            if tvxvm__xes < 10:
                sjgx__ldg = '00'
            elif tvxvm__xes < 100:
                sjgx__ldg = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{sjgx__ldg}{tvxvm__xes}'"
                )
        return impl
    elif ykfp__mqth == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {ykfp__mqth} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    aiuec__etz = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    ykfp__mqth = types.unliteral(filter_value)
    if isinstance(ykfp__mqth, types.List) and (isinstance(ykfp__mqth.dtype,
        scalar_isinstance) or ykfp__mqth.dtype in aiuec__etz):

        def impl(filter_value):
            brlw__ibag = ', '.join([_get_snowflake_sql_literal_scalar(
                cdao__uzulv) for cdao__uzulv in filter_value])
            return f'({brlw__ibag})'
        return impl
    elif isinstance(ykfp__mqth, scalar_isinstance) or ykfp__mqth in aiuec__etz:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {ykfp__mqth} used in filter pushdown.'
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
    except ImportError as oavbe__oopzb:
        rotrw__gkxd = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(rotrw__gkxd)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as oavbe__oopzb:
        rotrw__gkxd = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(rotrw__gkxd)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as oavbe__oopzb:
        rotrw__gkxd = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(rotrw__gkxd)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as oavbe__oopzb:
        rotrw__gkxd = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(rotrw__gkxd)


def req_limit(sql_request):
    import re
    wxij__suo = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    qif__bkm = wxij__suo.search(sql_request)
    if qif__bkm:
        return int(qif__bkm.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type: str, limit: Optional[int], parallel, typemap, filters,
    pyarrow_table_schema: 'Optional[pyarrow.Schema]'):
    zcuvr__nwiun = next_label()
    jjwg__ojjnk = [col_names[quy__qiaew] for quy__qiaew in out_used_cols]
    hieq__ynu = [col_typs[quy__qiaew] for quy__qiaew in out_used_cols]
    if index_column_name:
        jjwg__ojjnk.append(index_column_name)
        hieq__ynu.append(index_column_type)
    nzyl__rbkv = None
    nrs__pbna = None
    yxq__tsxh = TableType(tuple(col_typs)) if out_used_cols else types.none
    azl__cze = ''
    vch__fmbv = {}
    jkz__tjd = []
    if filters and db_type == 'iceberg':
        vch__fmbv, jkz__tjd = bodo.ir.connector.generate_filter_map(filters)
        azl__cze = ', '.join(vch__fmbv.values())
    kvn__dpy = (
        f'def sql_reader_py(sql_request, conn, database_schema, {azl__cze}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        jrdnh__xrvw, tbx__spfil = bodo.ir.connector.generate_arrow_filters(
            filters, vch__fmbv, jkz__tjd, col_names, col_names, col_typs,
            typemap, 'iceberg')
        mytr__kgcwm: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[quy__qiaew]) for quy__qiaew in out_used_cols]
        pddo__idsql = {ouq__cel: quy__qiaew for quy__qiaew, ouq__cel in
            enumerate(mytr__kgcwm)}
        uliy__zmhi = [int(is_nullable(col_typs[quy__qiaew])) for quy__qiaew in
            mytr__kgcwm]
        ixst__nftpe = ',' if azl__cze else ''
        kvn__dpy += f"""  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})
  dnf_filters, expr_filters = get_filters_pyobject("{jrdnh__xrvw}", "{tbx__spfil}", ({azl__cze}{ixst__nftpe}))
  out_table = iceberg_read(
    unicode_to_utf8(conn),
    unicode_to_utf8(database_schema),
    unicode_to_utf8(sql_request),
    {parallel},
    {-1 if limit is None else limit},
    dnf_filters,
    expr_filters,
    selected_cols_arr_{zcuvr__nwiun}.ctypes,
    {len(mytr__kgcwm)},
    nullable_cols_arr_{zcuvr__nwiun}.ctypes,
    pyarrow_table_schema_{zcuvr__nwiun},
  )
  check_and_propagate_cpp_exception()
"""
        gvo__upfb = not out_used_cols
        yxq__tsxh = TableType(tuple(col_typs))
        if gvo__upfb:
            yxq__tsxh = types.none
        ekucl__bwmki = 'None'
        if index_column_name is not None:
            cqrge__rwhy = len(out_used_cols) + 1 if not gvo__upfb else 0
            ekucl__bwmki = (
                f'info_to_array(info_from_table(out_table, {cqrge__rwhy}), index_col_typ)'
                )
        kvn__dpy += f'  index_var = {ekucl__bwmki}\n'
        nzyl__rbkv = None
        if not gvo__upfb:
            nzyl__rbkv = []
            goam__xvv = 0
            for quy__qiaew in range(len(col_names)):
                if goam__xvv < len(out_used_cols
                    ) and quy__qiaew == out_used_cols[goam__xvv]:
                    nzyl__rbkv.append(pddo__idsql[quy__qiaew])
                    goam__xvv += 1
                else:
                    nzyl__rbkv.append(-1)
            nzyl__rbkv = np.array(nzyl__rbkv, dtype=np.int64)
        if gvo__upfb:
            kvn__dpy += '  table_var = None\n'
        else:
            kvn__dpy += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{zcuvr__nwiun}, py_table_type_{zcuvr__nwiun})
"""
        kvn__dpy += f'  delete_table(out_table)\n'
        kvn__dpy += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        kvn__dpy += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        uliy__zmhi = [int(is_nullable(col_typs[quy__qiaew])) for quy__qiaew in
            out_used_cols]
        if index_column_name:
            uliy__zmhi.append(int(is_nullable(index_column_type)))
        kvn__dpy += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(uliy__zmhi)}, np.array({uliy__zmhi}, dtype=np.int32).ctypes)
"""
        kvn__dpy += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            kvn__dpy += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            kvn__dpy += '  index_var = None\n'
        if out_used_cols:
            uep__nxb = []
            goam__xvv = 0
            for quy__qiaew in range(len(col_names)):
                if goam__xvv < len(out_used_cols
                    ) and quy__qiaew == out_used_cols[goam__xvv]:
                    uep__nxb.append(goam__xvv)
                    goam__xvv += 1
                else:
                    uep__nxb.append(-1)
            nzyl__rbkv = np.array(uep__nxb, dtype=np.int64)
            kvn__dpy += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{zcuvr__nwiun}, py_table_type_{zcuvr__nwiun})
"""
        else:
            kvn__dpy += '  table_var = None\n'
        kvn__dpy += '  delete_table(out_table)\n'
        kvn__dpy += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            kvn__dpy += f"""  type_usecols_offsets_arr_{zcuvr__nwiun}_2 = type_usecols_offsets_arr_{zcuvr__nwiun}
"""
            nrs__pbna = np.array(out_used_cols, dtype=np.int64)
        kvn__dpy += '  df_typeref_2 = df_typeref\n'
        kvn__dpy += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            kvn__dpy += '  pymysql_check()\n'
        elif db_type == 'oracle':
            kvn__dpy += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            kvn__dpy += '  psycopg2_check()\n'
        if parallel:
            kvn__dpy += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                kvn__dpy += f'  nb_row = {limit}\n'
            else:
                kvn__dpy += '  with objmode(nb_row="int64"):\n'
                kvn__dpy += f'     if rank == {MPI_ROOT}:\n'
                kvn__dpy += (
                    "         sql_cons = 'select count(*) from (' + sql_request + ') x'\n"
                    )
                kvn__dpy += '         frame = pd.read_sql(sql_cons, conn)\n'
                kvn__dpy += '         nb_row = frame.iat[0,0]\n'
                kvn__dpy += '     else:\n'
                kvn__dpy += '         nb_row = 0\n'
                kvn__dpy += '  nb_row = bcast_scalar(nb_row)\n'
            kvn__dpy += f"""  with objmode(table_var=py_table_type_{zcuvr__nwiun}, index_var=index_col_typ):
"""
            kvn__dpy += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                kvn__dpy += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                kvn__dpy += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            kvn__dpy += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            kvn__dpy += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            kvn__dpy += f"""  with objmode(table_var=py_table_type_{zcuvr__nwiun}, index_var=index_col_typ):
"""
            kvn__dpy += '    df_ret = pd.read_sql(sql_request, conn)\n'
            kvn__dpy += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            kvn__dpy += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            kvn__dpy += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            kvn__dpy += '    index_var = None\n'
        if out_used_cols:
            kvn__dpy += f'    arrs = []\n'
            kvn__dpy += f'    for i in range(df_ret.shape[1]):\n'
            kvn__dpy += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            kvn__dpy += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{zcuvr__nwiun}_2, {len(col_names)})
"""
        else:
            kvn__dpy += '    table_var = None\n'
    kvn__dpy += '  return (table_var, index_var)\n'
    gnk__uokij = globals()
    gnk__uokij.update({'bodo': bodo, f'py_table_type_{zcuvr__nwiun}':
        yxq__tsxh, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        gnk__uokij.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{zcuvr__nwiun}': nzyl__rbkv})
    if db_type == 'iceberg':
        gnk__uokij.update({f'selected_cols_arr_{zcuvr__nwiun}': np.array(
            mytr__kgcwm, np.int32), f'nullable_cols_arr_{zcuvr__nwiun}': np
            .array(uliy__zmhi, np.int32), f'py_table_type_{zcuvr__nwiun}':
            yxq__tsxh, f'pyarrow_table_schema_{zcuvr__nwiun}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        gnk__uokij.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        gnk__uokij.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(hieq__ynu), bodo.RangeIndexType(None),
            tuple(jjwg__ojjnk)), 'Table': Table,
            f'type_usecols_offsets_arr_{zcuvr__nwiun}': nrs__pbna})
    ekdb__erlu = {}
    exec(kvn__dpy, gnk__uokij, ekdb__erlu)
    hnlcy__sil = ekdb__erlu['sql_reader_py']
    dcg__fdcw = numba.njit(hnlcy__sil)
    compiled_funcs.append(dcg__fdcw)
    return dcg__fdcw


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
