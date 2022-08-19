import psycopg2
from .query_json_to_sql import AGJsonToSQL


class AGQueryPostgres:
    # Variables
    conn = None
    conn_string: str = None
    json_obj: AGJsonToSQL = None
    SQL: str = None
    inner_sql: str = None
    query: dict = None
    rows: list = []

    def __init__(self):
        self.SQL = ""
        self.inner_sql = ""
        self.query = {}
        self.rows = []
        self.json_obj = AGJsonToSQL()

    def build_sql(self, query: dict = None):
        if query is not None:
            sql = self.json_obj.execute(query)
        else:
            sql = self.json_obj.execute()

        return sql

    def execute(self, query: dict = None) -> dict:
        sql = self.build_sql(query)

        self.rows = self._get_rows(sql)
        self.SQL = sql
        self.inner_sql = self.json_obj.inner_sql

        if query is not None:
            # Save query in standards - last_query
            self.query = query

        if self.json_obj.limit == 0:
            page = 1
        else:
            page = int(self.json_obj.offset / self.json_obj.limit) + 1

        result_execute = {
            "count": len(self.rows),
            "offset": self.json_obj.offset,
            "limit": self.json_obj.limit,
            "page": page,
            "results": self.rows
        }
        return result_execute

    def explain(self, query: dict = None) -> dict:
        sql = self.build_sql(query)

        self.SQL = sql
        self.inner_sql = self.json_obj.inner_sql

        explanation = self.execute_direct("EXPLAIN " + sql)
        for s in explanation:
            print(s)

        return explanation

    #
    # Get rows
    #
    def _get_rows(self, sql: str) -> list:

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            # Clean rows for tuples
            for x, r in enumerate(rows):
                rows[x] = r[0]
        except Exception as e:
            print(e)
            cursor.close()
            rows = []

        return rows

    def print_rows(self):
        for r in self.rows:
            print(r)

    #
    # Execute RAW SQL
    #
    def execute_direct(self, sql: str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result_direct = cursor.fetchall()
            self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            self.conn.rollback()
            print(error)
            result_direct = error

        return result_direct


class AGQueryPostgresQueryLibrary:
    usename = None
    conn = None

    def __init__(self, usename: str, conn):
        self.usename = usename
        self.conn = conn

    def save_query(self, name: str, query: dict):
        # Save query to standards query_library and last_query
        pass

    def load_query(self, name: str):
        # Load query from standards query_library and last_query
        # and return Query JSON
        pass

    def delete_query(self, name: str):
        # Delete query from standards query_library
        pass

    def load_manifest(self, name: str):
        # Load query manifest and return Query JSON
        pass



