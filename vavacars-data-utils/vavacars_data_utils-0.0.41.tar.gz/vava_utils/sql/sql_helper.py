from sqlalchemy import create_engine, event, text
from sqlalchemy.engine.url import URL
from msal import ConfidentialClientApplication
import urllib
import struct
import subprocess
import pandas as pd
import logging
import random

from typing import List

LOGGER = logging.getLogger(__name__)


def get_mysql_helper(host, user, port, database, password=None, **kwargs):
    engine_url = URL.create(
        drivername="mysql+pymysql", host=host, username=user, database=database, password=password, port=port
    )
    engine = create_engine(engine_url, connect_args={"ssl": {"ssl_check_hostname": False}}, pool_pre_ping=True, **kwargs)
    if not password:

        @event.listens_for(engine, "do_connect")  # https://docs.sqlalchemy.org/en/14/core/engines.html
        def provide_token(dialect, conn_rec, cargs, cparams):
            cmd = "az account get-access-token --resource-type oss-rdbms --output tsv --query accessToken"
            token = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
            cparams["password"] = token

    return SQL_Helper(engine, engine_type="mysql")


def get_sqlserver_helper(
    host,
    database,
    service_principal_id,
    service_principal_secret,
    tenant_id,
    port=1433,
    db_driver="ODBC Driver 17 for SQL Server",
    fast_execute_many=False,
    **kwargs,
):

    creds = ConfidentialClientApplication(
        client_id=service_principal_id,
        client_credential=service_principal_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )

    conn_str = urllib.parse.quote_plus(f"DRIVER={{{db_driver}}};SERVER={host},{port};DATABASE={database}")

    connect_args = {"ansi": False, "TrustServerCertificate": "yes"}
    engine = create_engine(
        url=URL.create("mssql+pyodbc", query={"odbc_connect": conn_str}),
        connect_args=connect_args,
        fast_executemany=fast_execute_many,
        pool_pre_ping=True,
        **kwargs
    )

    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        token = creds.acquire_token_for_client(scopes="https://database.windows.net//.default")
        token_bytes = token["access_token"].encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
        cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    return SQL_Helper(engine, engine_type="sql_server")


class SQL_Helper:
    def __init__(self, engine, engine_type):
        """
        SQL helper constructor.

        Parameters:
            engine: sqlalchemy.engine.base.Engine instance
        """
        self._engine = engine
        self.engine_type = engine_type

    def from_table(self, table, **kwargs):
        """
        Given a table name, returns a Pandas DataFrame.

        Parameters:
            table (string): table name
            **kwargs: additional keyword parameters passed to pd.read_sql_table

        Returns:
            result (pd.DataFrame): SQL table in pandas dataframe format
        """
        return pd.read_sql_table(table, self._engine, **kwargs)

    def from_file(self, filename, query_args={}, limit=None, **kwargs):
        """
        Read SQL query from .sql file into a Pandas DataFrame.

        Parameters:
            filename (string): path to file containing the SQL query
            query_args (dict): query string is formatted with those params: string.format(**query_args)
                               example: {'max_date': '2020-01-01'}
            limit (int): maximum number of results
            **kwargs: additional keyword parameters passed to pd.read_sql_query

        Returns:
            result (pd.DataFrame): query results in  Pandas DataFrame format
        """
        if (limit is not None) and (not isinstance(limit, int)):
            raise ValueError("Limit must be of type int")

        with open(filename, "r") as f:
            query_unformated = f.read().rstrip()
        query = query_unformated.format(**query_args)
        query = query if not limit else query.replace(";", f" LIMIT {limit};")
        return self.from_query(query, **kwargs)

    def from_query(self, query, **kwargs):
        """
        Read SQL query into a Pandas DataFrame.

        Parameters:
            query (string): query string
            **kwargs: additional keyword parameters passed to pd.read_sql_query

        Returns:
            result (pd.DataFrame): query results in  Pandas DataFrame format
        """
        return pd.read_sql_query(query, self._engine, **kwargs)

    def write_df(self, df, table_name, chunksize=1000, **kwargs):
        """
        Store Pandas Dataframe into SQL table

        Args:
            df (pd.DataFrame): data to write
            table_name (str): output database table name 
            **kwargs: additional keyword parameters passed to df.to_sql
        """
        with self._engine.connect() as conn:
            trans = conn.begin()
            try:
                df.to_sql(table_name, conn, chunksize=chunksize, **kwargs)
                trans.commit()
            except Exception as ex:
                LOGGER.warning(str(ex))
                trans.rollback()
                raise ex

    def upsert_df(self, df: pd.DataFrame, table_name: str, upsert_cols: List[str], chunksize: int = 1000):
        """
        Store Pandas Dataframe into SQL table with upsert method. NOTE: Only implemented for SQL Server engines.

        Args:
            df (pd.DataFrame): data to write
            table_name (str): output database table name
            upsert_cols (List[str]): list columns to use as keys for upserting
            chunksize (int): number of rows in each batch to be written at a time
        """
        if self.engine_type != 'sql_server':
            raise NotImplementedError(f'Method not implemented for {self.engine_type} engine')
        try:
            # this is transactional
            with self._engine.connect() as conn:
                trans = conn.begin()
                try:
                    tmp_table_name = f"##{table_name}_tmp_{random.randrange(0, 100)}"  # This has to be a global table
                    # Create tmp table as a copy
                    create_tmp_table_sq = f"SELECT TOP 0 * INTO dbo.{tmp_table_name} FROM dbo.{table_name}"
                    conn.execute(text(create_tmp_table_sq))
                    # First insert in tmp table.
                    df.to_sql(tmp_table_name, conn, if_exists="append", index=False, chunksize=chunksize)
                    col_names = list(df.columns)
                    set_part = []
                    for col in col_names:
                        set_part.append(f"{col} = tmp.{col}")
                    set_part = ", ".join(set_part)
                    upsert_part_cols = []
                    for col in upsert_cols:
                        upsert_part_cols.append(f"t.{col} = tmp.{col}")
                    upsert_part_cols = " AND ".join(upsert_part_cols)
                    update_sql = f"""
                        UPDATE {table_name} SET {set_part}
                        FROM dbo.{table_name} AS t
                        INNER JOIN {tmp_table_name} AS tmp
                        ON {upsert_part_cols};
                    """
                    conn.execute(text(update_sql))
                    not_exists_part_cols = []
                    for col in upsert_cols:
                        not_exists_part_cols.append(f"{col} = tmp.{col}")
                    not_exists_part_cols = " AND ".join(not_exists_part_cols)
                    comma_col_names = f'{", ".join(col_names)}'
                    insert_sql = f"""
                    INSERT INTO dbo.{table_name}({comma_col_names})
                    SELECT {comma_col_names}
                    FROM {tmp_table_name} AS tmp
                    WHERE NOT EXISTS
                    (
                        SELECT 1 FROM {table_name} 
                        WHERE {not_exists_part_cols}
                    );
                    """
                    conn.execute(text(insert_sql))
                    trans.commit()
                except Exception as ex:
                    LOGGER.warning(str(ex))
                    trans.rollback()
                    raise ex
        except Exception as ex:
            LOGGER.error(str(ex), exc_info=ex)
            raise ex
