import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    mftn__zcvll = {}
    stfcb__qqxd, nblnu__lfsw = self._current_database_schema(connection, **kw)
    fdiwr__wys = self._denormalize_quote_join(stfcb__qqxd, schema)
    try:
        hmika__gsgr = self._get_schema_primary_keys(connection, fdiwr__wys,
            **kw)
        njan__dij = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as xbh__fylis:
        if xbh__fylis.orig.errno == 90030:
            return None
        raise
    for table_name, ulwz__awq, vujrt__fgwep, hmd__ineaq, pqm__zkfed, nocrp__qmof, wjtf__mpfjm, bpz__metf, uub__sfda, ykdhf__dwalr in njan__dij:
        table_name = self.normalize_name(table_name)
        ulwz__awq = self.normalize_name(ulwz__awq)
        if table_name not in mftn__zcvll:
            mftn__zcvll[table_name] = list()
        if ulwz__awq.startswith('sys_clustering_column'):
            continue
        krjiv__kcon = self.ischema_names.get(vujrt__fgwep, None)
        iqny__xwd = {}
        if krjiv__kcon is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(vujrt__fgwep, ulwz__awq))
            krjiv__kcon = sqltypes.NULLTYPE
        elif issubclass(krjiv__kcon, sqltypes.FLOAT):
            iqny__xwd['precision'] = pqm__zkfed
            iqny__xwd['decimal_return_scale'] = nocrp__qmof
        elif issubclass(krjiv__kcon, sqltypes.Numeric):
            iqny__xwd['precision'] = pqm__zkfed
            iqny__xwd['scale'] = nocrp__qmof
        elif issubclass(krjiv__kcon, (sqltypes.String, sqltypes.BINARY)):
            iqny__xwd['length'] = hmd__ineaq
        befh__dzht = krjiv__kcon if isinstance(krjiv__kcon, sqltypes.NullType
            ) else krjiv__kcon(**iqny__xwd)
        vzgof__kwh = hmika__gsgr.get(table_name)
        mftn__zcvll[table_name].append({'name': ulwz__awq, 'type':
            befh__dzht, 'nullable': wjtf__mpfjm == 'YES', 'default':
            bpz__metf, 'autoincrement': uub__sfda == 'YES', 'comment':
            ykdhf__dwalr, 'primary_key': ulwz__awq in hmika__gsgr[
            table_name]['constrained_columns'] if vzgof__kwh else False})
    return mftn__zcvll


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    mftn__zcvll = []
    stfcb__qqxd, nblnu__lfsw = self._current_database_schema(connection, **kw)
    fdiwr__wys = self._denormalize_quote_join(stfcb__qqxd, schema)
    hmika__gsgr = self._get_schema_primary_keys(connection, fdiwr__wys, **kw)
    njan__dij = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, ulwz__awq, vujrt__fgwep, hmd__ineaq, pqm__zkfed, nocrp__qmof, wjtf__mpfjm, bpz__metf, uub__sfda, ykdhf__dwalr in njan__dij:
        table_name = self.normalize_name(table_name)
        ulwz__awq = self.normalize_name(ulwz__awq)
        if ulwz__awq.startswith('sys_clustering_column'):
            continue
        krjiv__kcon = self.ischema_names.get(vujrt__fgwep, None)
        iqny__xwd = {}
        if krjiv__kcon is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(vujrt__fgwep, ulwz__awq))
            krjiv__kcon = sqltypes.NULLTYPE
        elif issubclass(krjiv__kcon, sqltypes.FLOAT):
            iqny__xwd['precision'] = pqm__zkfed
            iqny__xwd['decimal_return_scale'] = nocrp__qmof
        elif issubclass(krjiv__kcon, sqltypes.Numeric):
            iqny__xwd['precision'] = pqm__zkfed
            iqny__xwd['scale'] = nocrp__qmof
        elif issubclass(krjiv__kcon, (sqltypes.String, sqltypes.BINARY)):
            iqny__xwd['length'] = hmd__ineaq
        befh__dzht = krjiv__kcon if isinstance(krjiv__kcon, sqltypes.NullType
            ) else krjiv__kcon(**iqny__xwd)
        vzgof__kwh = hmika__gsgr.get(table_name)
        mftn__zcvll.append({'name': ulwz__awq, 'type': befh__dzht,
            'nullable': wjtf__mpfjm == 'YES', 'default': bpz__metf,
            'autoincrement': uub__sfda == 'YES', 'comment': ykdhf__dwalr if
            ykdhf__dwalr != '' else None, 'primary_key': ulwz__awq in
            hmika__gsgr[table_name]['constrained_columns'] if vzgof__kwh else
            False})
    return mftn__zcvll


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
