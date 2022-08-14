from .bases import Namespaced
from .exceptions import SchemaRequired
from .enums import ExternalStorage, ExternalPathConfig, Credentials, Encryption
from typing import Optional

class ExternalStage(Namespaced):
    def __init__(self, stage_name: str, schema: Optional[str] = None, database: Optional[str] = None) -> None:
        if database and not schema:
            raise SchemaRequired('Database name provided but schema missing')

        self.stage_name = stage_name
        self.schema = schema
        self.database = database

    @property
    def fullname(self) -> str:
        '''
        So long as this class raises on init that a schema is required if a database is provided
        then this is safe to do
        '''
        name = self.stage_name

        if self.schema:
            name = f'{self.schema}.{name}'

        if self.database:
            name = f'{self.database}.{name}'

        return name

'''
Below this is initially out of scope
'''

class InternalStage(Namespaced):
    def __init__(self, stage_name: str, schema: Optional[str] = None, database: Optional[str] = None) -> None:
        '''
        There's a personal internal stage available in Snowflake by using a ~
        If that's what you want, just use stage_name='~' on init, let's not make
        it more complicated than that
        '''
        
        if database and not schema:
            raise SchemaRequired('Database name provided but schema missing')

        self.stage_name = stage_name
        self.schema = schema
        self.database = database

    @property
    def fullname(self) -> str:
        pass

class ExternalLocation(Namespaced):
    def __init__(self, location_type: ExternalStorage, path_config: ExternalPathConfig, credentials: Optional[Credentials], encryption: Optional[Encryption]) -> None:
        '''
        There's a personal internal stage available in Snowflake by using a ~
        If that's what you want, just use stage_name='~' on init, let's not make
        it more complicated than that
        '''

        self.location_type = location_type
        self.path_config = path_config
        self.credentials = credentials
        self.encryption = encryption
        
    @property
    def fullname(self) -> str:
        pass
