from models.model import ClientModel
import pyodbc
class DatabaseClient(ClientModel):
    def __init__(self, server, database, username, password, driverLocation, *args, **kwargs):
        self.server=server
        self.database=database
        self.username=username
        self.password=password
        self.driverLocation=driverLocation
        if self.databaseType().lower() == "mssql":
            self.cnxn = pyodbc.connect(
                "DRIVER="+str(driverLocation)+";"+
                "SERVER="+str(server)+";"+
                "DATABASE="+str(database)+";"+
                "UID="+str(username)+";"+
                "PWD="+str(password)+";"
            , timeout=5)
            self.cursor = self.cnxn.cursor()
        else:
            self.cursor=self.getCursorFromDatabase(
                self.server,
                self.database,
                self.username,
                self.password,
                self.driverLocation
            )
        super().__init__(*args, **kwargs)

    def getCursor(self):
        return self.cursor

    @abstractmethod
    def databaseType(self):
        return "MSSQL"

    def getCursorFromDatabase(self,
        server:str,
        database:str,
        username:str,
        password:str,
        driverLocation:str
    ):
        raise NotImplementedError("getCursorFromDatabase is not implemented")

    def fetchall(self, query:str):
        self.cursor.execute(query)
        rowAll = self.cursor.fetchall()
        return rowAll

    def fetchone(self, query:str):
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row