import asyncio
import motor.motor_asyncio
from datadbs.general import GeneralData
from networktools.time import timestamp, now

mongourl = "mongodb://localhost:27017/"

class AsyncMongoDB(GeneralData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station = kwargs.get('dbname')
        self.dbname = kwargs.get('dbname')
        self.default_db = kwargs.get('dbname')
        self.set_defaultdb(self.dbname)
        self.client_host = None
        self.client_port = 0
        self.session = None

    def __repr__(self):
        return f"AsyncMongo({self.default_db}, {self.address})"

    def __str__(self):
        return f"AsyncMongo({self.default_db}, {self.address})"

    @property
    def client_address(self):
        return (self.client_host, self.client_port)

    @property
    def active(self):
        return self.client_host and self.client_port > 0

    @property
    def url(self):
        return f"mongodb://{self.host}:{self.port}"

    # database manage
    def set_defaultdb(self, dbname: str, first_time=False):
        if dbname:
            self.default_db = dbname
            print("Station %s, db %s" % (self.station, self.default_db))
            if first_time:
                self.logger.info("Database set on %s by default" % dbname)


    async def async_connect(self, loop=None, *args, **kwargs):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            self.host, self.port)
        self.session = await self.client.start_session()

    async def connect(self, loop=None, *args, **kwargs):
        await self.async_connect(loop, *args, **kwargs)

    def database(self, dbname):
        return self.client.get_database(dbname)
    
    async def create_db(self, dbname:str=None):
        db = dbname or self.default_db
        return self.database(db)

    async def delete_db(self, dbname:str):
        await self.client.drop_database(dbname)

    async def list_dbs(self):
        self.dbs= await self.client.list_database_names()
        return self.dbs

    async def close(self):
        await self.session.end_session()
        self.client.close 

    async def server_info(self):
        return await self.client.server_info()

    async def save_data(self, table_name:str, data, options=None, dbname:str=None):
        collection = self.get_table(table_name, dbname)
        async with self.session.start_transaction():
            await collection.insert_one(data, session=self.session)
            #todo: implement bulk write

    def start_transaction(self):
        return self.session.start_transaction()

    async def list_tables(self, dbname: str = None):
        db = dbname or self.default_db
        self.tables = await self.client[db].list_collection_names()
        return self.tables

    async def create_table(self, table_name: str, dbname: str = None):
        db = dbname or self.default_db
        return self.client[db].create_collection(table_name)
 

    async def delete_table(self, table_name: str, dbname: str = None):
        db = dbname or self.default_db
        return self.client[db].drop_collection(table_name)
 
    def get_table(self, table_name:str, dbname:str=None):
        db = dbname or self.default_db
        return self.client[db].get_collection(table_name)

    async def create_index(self,
                           table_name: str,
                           index: str = None,
                           dbname: str = None):
        collection = self.get_table(table_name, dbname)
        collection.create_index(index)
