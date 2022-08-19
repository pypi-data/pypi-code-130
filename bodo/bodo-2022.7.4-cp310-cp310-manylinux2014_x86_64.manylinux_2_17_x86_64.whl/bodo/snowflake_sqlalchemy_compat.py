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
    pufyv__vwndn = {}
    ebrm__ala, pcl__rwavr = self._current_database_schema(connection, **kw)
    joaa__yoy = self._denormalize_quote_join(ebrm__ala, schema)
    try:
        lrxix__fwsay = self._get_schema_primary_keys(connection, joaa__yoy,
            **kw)
        xxe__quf = connection.execute(text(
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
    except sa_exc.ProgrammingError as ocjry__iqqn:
        if ocjry__iqqn.orig.errno == 90030:
            return None
        raise
    for table_name, fbz__aapxe, csyw__wwslm, izm__ngnsy, ompz__unqdi, dbms__ymks, gkpiw__upfkq, eqy__sdlbq, imxll__rdlz, gpg__yodp in xxe__quf:
        table_name = self.normalize_name(table_name)
        fbz__aapxe = self.normalize_name(fbz__aapxe)
        if table_name not in pufyv__vwndn:
            pufyv__vwndn[table_name] = list()
        if fbz__aapxe.startswith('sys_clustering_column'):
            continue
        nhy__haqmy = self.ischema_names.get(csyw__wwslm, None)
        otonj__lqdz = {}
        if nhy__haqmy is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(csyw__wwslm, fbz__aapxe))
            nhy__haqmy = sqltypes.NULLTYPE
        elif issubclass(nhy__haqmy, sqltypes.FLOAT):
            otonj__lqdz['precision'] = ompz__unqdi
            otonj__lqdz['decimal_return_scale'] = dbms__ymks
        elif issubclass(nhy__haqmy, sqltypes.Numeric):
            otonj__lqdz['precision'] = ompz__unqdi
            otonj__lqdz['scale'] = dbms__ymks
        elif issubclass(nhy__haqmy, (sqltypes.String, sqltypes.BINARY)):
            otonj__lqdz['length'] = izm__ngnsy
        efks__dfms = nhy__haqmy if isinstance(nhy__haqmy, sqltypes.NullType
            ) else nhy__haqmy(**otonj__lqdz)
        xdln__sso = lrxix__fwsay.get(table_name)
        pufyv__vwndn[table_name].append({'name': fbz__aapxe, 'type':
            efks__dfms, 'nullable': gkpiw__upfkq == 'YES', 'default':
            eqy__sdlbq, 'autoincrement': imxll__rdlz == 'YES', 'comment':
            gpg__yodp, 'primary_key': fbz__aapxe in lrxix__fwsay[table_name
            ]['constrained_columns'] if xdln__sso else False})
    return pufyv__vwndn


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
    pufyv__vwndn = []
    ebrm__ala, pcl__rwavr = self._current_database_schema(connection, **kw)
    joaa__yoy = self._denormalize_quote_join(ebrm__ala, schema)
    lrxix__fwsay = self._get_schema_primary_keys(connection, joaa__yoy, **kw)
    xxe__quf = connection.execute(text(
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
    for table_name, fbz__aapxe, csyw__wwslm, izm__ngnsy, ompz__unqdi, dbms__ymks, gkpiw__upfkq, eqy__sdlbq, imxll__rdlz, gpg__yodp in xxe__quf:
        table_name = self.normalize_name(table_name)
        fbz__aapxe = self.normalize_name(fbz__aapxe)
        if fbz__aapxe.startswith('sys_clustering_column'):
            continue
        nhy__haqmy = self.ischema_names.get(csyw__wwslm, None)
        otonj__lqdz = {}
        if nhy__haqmy is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(csyw__wwslm, fbz__aapxe))
            nhy__haqmy = sqltypes.NULLTYPE
        elif issubclass(nhy__haqmy, sqltypes.FLOAT):
            otonj__lqdz['precision'] = ompz__unqdi
            otonj__lqdz['decimal_return_scale'] = dbms__ymks
        elif issubclass(nhy__haqmy, sqltypes.Numeric):
            otonj__lqdz['precision'] = ompz__unqdi
            otonj__lqdz['scale'] = dbms__ymks
        elif issubclass(nhy__haqmy, (sqltypes.String, sqltypes.BINARY)):
            otonj__lqdz['length'] = izm__ngnsy
        efks__dfms = nhy__haqmy if isinstance(nhy__haqmy, sqltypes.NullType
            ) else nhy__haqmy(**otonj__lqdz)
        xdln__sso = lrxix__fwsay.get(table_name)
        pufyv__vwndn.append({'name': fbz__aapxe, 'type': efks__dfms,
            'nullable': gkpiw__upfkq == 'YES', 'default': eqy__sdlbq,
            'autoincrement': imxll__rdlz == 'YES', 'comment': gpg__yodp if 
            gpg__yodp != '' else None, 'primary_key': fbz__aapxe in
            lrxix__fwsay[table_name]['constrained_columns'] if xdln__sso else
            False})
    return pufyv__vwndn


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
