import psycopg2
from .settings import DB_CONNECTION
from AGCoder import Coder
from .query_postgres import AGQueryPostgres


#
# Variable with all security settings for a PostgreSQL user
# Should be kept as session variable just like the conn object
# Check if standard user have rights to these information by default
# If not create tmp_permission_user and grant the right for the information
#
class AGSecurityListPostgres:
    usename: str = None

    def __init__(self, usename):
        self.conn_string = DB_CONNECTION
        self.conn = psycopg2.connect(self.conn_string)

        self.usename = usename

    #
    # If a user is member of one or more groups, and just one of the groups have a permission,
    # the user will have this permission i.e. false + false + true = true, false + false = false
    # all these calls should be packed into stored procedures or views
    #
    def get_user_groups(self):
        #
        # Database
        #
        db_grant = AGQueryPostgres("pg_catalog", "pg_roles")
        db_grant.select = [
            "rolname", "rolsuper", "rolinherit", "rolcreaterole", "rolcreatedb", "rolcanlogin",
            "rolconnlimit", "rolvaliduntil", "rolreplication", "rolbypassrls"
        ]
        db_grant.where = [
            {
                "rolname": self.usename
            }
        ]
        db_grant.order_by = ["rolname"]
        db_grant_rows = db_grant.execute()

        return db_grant_rows[0]

    def get_database_rights(self):
        # Return JSON with database
        pass

    # If you do not pass schema name, list them all, table name=list everything in the schema
    def get_table_rights(self, schema_name=None, table_name=None):
        # Return JSON with user groups
        pass

    # If you do not pass schema name, list them all, view name=list everything in the schema
    def get_view_rights(self, schema_name=None, view_name=None):
        # Return JSON with user groups
        pass

    def get_stored_procedure_rights(self, schema_name=None, stored_procedure_name=None):
        # Return JSON with user groups
        pass


#
# Shared library to call stored procedures with changes in security settings
#
class AGSecurityUpdatePostgres:
    usename: str = None
    command: list = []

    # Variables
    conn = None
    conn_string: str = None

    def __init__(self, usename):
        self.conn_string = DB_CONNECTION_SECURITY_OFFICER
        self.conn = psycopg2.connect(self.conn_string)

        self.usename = usename
        self._define_sql()
        self._define_list_sql(usename)

    #
    # SQL Library
    #
    def _define_sql(self):
        c = Coder("sql")

        # Create role
        self.command.append(
            {"create_role": "CREATE ROLE %1"}
        )

    def _define_list_sql(self, usename):
        #
        # Database
        #
        db_grant = AGQueryPostgres("pg_catalog", "pg_roles", conn=self.conn)
        db_grant.select = [
            "rolname", "rolsuper", "rolinherit", "rolcreaterole", "rolcreatedb", "rolcanlogin",
            "rolconnlimit", "rolvaliduntil", "rolreplication", "rolbypassrls"
        ]
        db_grant.where = [
            {
                "rolname": usename
            }
        ]
        db_grant.order_by = ["rolname"]
        db_grant_rows = db_grant.execute()

        #
        # Group
        #
        db_role = AGQueryPostgres("pg_catalog", "pg_auth_members", conn=self.conn)
        db_role.select = ["role.rolname"]
        db_role.id_name = "roleid"
        db_role.inner_join = [
            {
                "schema_name": "pg_catalog",
                "table_name": "pg_roles",
                "alias": "role",
                "relation": "oid",
            }
        ]
        db_role.where = [
            {
                "role.rolname": usename
            }
        ]
        db_role_rows = db_grant.execute()

        print(db_grant_rows)


s = AGSecurityListPostgres("test")
s.get_user_groups()
