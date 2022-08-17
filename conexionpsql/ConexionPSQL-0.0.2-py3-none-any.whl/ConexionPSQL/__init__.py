
# import the connect library for psycopg2
from psycopg2 import connect

# import the error handling libraries for psycopg2
from psycopg2 import OperationalError, errorcodes, errors

class Conectar():
    def __init__(self, host, port, name, user, password):
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.password = password
        # super(Conectar, self).__init__(host, port, name, user, password)
        
    def Psql(self):
        try:
            connPsql = connect(
                database=self.name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            connPsql.set_client_encoding('LATIN10')
            print("Conexion exitosa")
        except OperationalError as err:
            print("Ha ocurrido un error: ",err)
            connPsql = None
            
        return connPsql