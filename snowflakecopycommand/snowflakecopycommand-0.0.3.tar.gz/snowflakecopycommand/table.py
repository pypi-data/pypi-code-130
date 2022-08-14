from .bases import Namespaced
from .exceptions import SchemaRequired
from typing import Optional

class Table(Namespaced):
    def __init__(self, table_name: str, schema: Optional[str] = None, database: Optional[str] = None) -> None:
        if database and not schema:
            raise SchemaRequired('Database name provided but schema missing')

        self.table_name = table_name
        self.schema = schema
        self.database = database

    @property
    def fullname(self) -> str:
        '''
        So long as this class raises on init that a schema is required if a database is provided
        then this is safe to do
        '''
        name = self.table_name

        if self.schema:
            name = f'{self.schema}.{name}'

        if self.database:
            name = f'{self.database}.{name}'

        return name