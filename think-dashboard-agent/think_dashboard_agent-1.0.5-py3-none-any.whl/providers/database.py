import psycopg2

from think_dashboard_agent.types import DatabaseInstance, InstanceCheckResult
from .base import BaseProvider


class DatabaseProvider(BaseProvider):
    def __init__(self, instance: DatabaseInstance):
        self.instance = instance
        self.__connection = None

    @classmethod
    def init(cls, instance: DatabaseInstance) -> "DatabaseProvider":
        return cls(instance)

    # Create a connection to the database
    def connect(self):
        if self.__connection is None or self.__connection.closed > 0:
            self.__connection = psycopg2.connect(
                host=self.instance.host,
                port=self.instance.port,
                user=self.instance.username,
                password=self.instance.password,
                database=self.instance.database
            )
        return self.__connection

    # Close the connection to the database
    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    def exc(self, connection):
        cur = connection.cursor()
        cur.execute("""
                    SELECT count(table_name) 
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                    """)
        return cur.fetchone()[0]

    def check(self, auto_close: bool = True) -> InstanceCheckResult:
        try:
            connection = self.connect()
            result = self.exc(connection)
            return InstanceCheckResult(data=result)
        except psycopg2.OperationalError:
            return InstanceCheckResult(status=500, error='Unable to connect to the database')
        except psycopg2.Error as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            if auto_close:
                self.close()
