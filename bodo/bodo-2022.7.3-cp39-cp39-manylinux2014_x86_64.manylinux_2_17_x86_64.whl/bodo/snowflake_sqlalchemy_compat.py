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
    tizao__quq = {}
    jak__tsu, akkp__zjkv = self._current_database_schema(connection, **kw)
    wuxph__hjvvz = self._denormalize_quote_join(jak__tsu, schema)
    try:
        jahu__ccerh = self._get_schema_primary_keys(connection,
            wuxph__hjvvz, **kw)
        szpi__wctb = connection.execute(text(
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
    except sa_exc.ProgrammingError as iaaoy__wcshn:
        if iaaoy__wcshn.orig.errno == 90030:
            return None
        raise
    for table_name, qxltc__fyir, gmn__yrn, vjb__tylno, bskmx__xda, fhcjs__hqot, kwc__pmgp, butzr__nxgzg, bay__tmap, cugws__xdxw in szpi__wctb:
        table_name = self.normalize_name(table_name)
        qxltc__fyir = self.normalize_name(qxltc__fyir)
        if table_name not in tizao__quq:
            tizao__quq[table_name] = list()
        if qxltc__fyir.startswith('sys_clustering_column'):
            continue
        kiucr__ddlg = self.ischema_names.get(gmn__yrn, None)
        elymj__juh = {}
        if kiucr__ddlg is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(gmn__yrn, qxltc__fyir))
            kiucr__ddlg = sqltypes.NULLTYPE
        elif issubclass(kiucr__ddlg, sqltypes.FLOAT):
            elymj__juh['precision'] = bskmx__xda
            elymj__juh['decimal_return_scale'] = fhcjs__hqot
        elif issubclass(kiucr__ddlg, sqltypes.Numeric):
            elymj__juh['precision'] = bskmx__xda
            elymj__juh['scale'] = fhcjs__hqot
        elif issubclass(kiucr__ddlg, (sqltypes.String, sqltypes.BINARY)):
            elymj__juh['length'] = vjb__tylno
        ycgi__gtf = kiucr__ddlg if isinstance(kiucr__ddlg, sqltypes.NullType
            ) else kiucr__ddlg(**elymj__juh)
        aunsb__ukp = jahu__ccerh.get(table_name)
        tizao__quq[table_name].append({'name': qxltc__fyir, 'type':
            ycgi__gtf, 'nullable': kwc__pmgp == 'YES', 'default':
            butzr__nxgzg, 'autoincrement': bay__tmap == 'YES', 'comment':
            cugws__xdxw, 'primary_key': qxltc__fyir in jahu__ccerh[
            table_name]['constrained_columns'] if aunsb__ukp else False})
    return tizao__quq


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
    tizao__quq = []
    jak__tsu, akkp__zjkv = self._current_database_schema(connection, **kw)
    wuxph__hjvvz = self._denormalize_quote_join(jak__tsu, schema)
    jahu__ccerh = self._get_schema_primary_keys(connection, wuxph__hjvvz, **kw)
    szpi__wctb = connection.execute(text(
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
    for table_name, qxltc__fyir, gmn__yrn, vjb__tylno, bskmx__xda, fhcjs__hqot, kwc__pmgp, butzr__nxgzg, bay__tmap, cugws__xdxw in szpi__wctb:
        table_name = self.normalize_name(table_name)
        qxltc__fyir = self.normalize_name(qxltc__fyir)
        if qxltc__fyir.startswith('sys_clustering_column'):
            continue
        kiucr__ddlg = self.ischema_names.get(gmn__yrn, None)
        elymj__juh = {}
        if kiucr__ddlg is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(gmn__yrn, qxltc__fyir))
            kiucr__ddlg = sqltypes.NULLTYPE
        elif issubclass(kiucr__ddlg, sqltypes.FLOAT):
            elymj__juh['precision'] = bskmx__xda
            elymj__juh['decimal_return_scale'] = fhcjs__hqot
        elif issubclass(kiucr__ddlg, sqltypes.Numeric):
            elymj__juh['precision'] = bskmx__xda
            elymj__juh['scale'] = fhcjs__hqot
        elif issubclass(kiucr__ddlg, (sqltypes.String, sqltypes.BINARY)):
            elymj__juh['length'] = vjb__tylno
        ycgi__gtf = kiucr__ddlg if isinstance(kiucr__ddlg, sqltypes.NullType
            ) else kiucr__ddlg(**elymj__juh)
        aunsb__ukp = jahu__ccerh.get(table_name)
        tizao__quq.append({'name': qxltc__fyir, 'type': ycgi__gtf,
            'nullable': kwc__pmgp == 'YES', 'default': butzr__nxgzg,
            'autoincrement': bay__tmap == 'YES', 'comment': cugws__xdxw if 
            cugws__xdxw != '' else None, 'primary_key': qxltc__fyir in
            jahu__ccerh[table_name]['constrained_columns'] if aunsb__ukp else
            False})
    return tizao__quq


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
