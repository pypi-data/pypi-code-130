import multiprocessing
import json
import os

class EnvData:
    def __init__(self,*args,**kwargs):
        schema = "COLLECTOR"
        self.CLLGROUP = os.getenv("CLL_GROUP")
        try:
            self.CLL_GROUP = json.loads(self.CLLGROUP)
        except Exception as ex:
            raise ex
        self.NPROC = multiprocessing.cpu_count()
        self.EST_BY_PROC = int(os.getenv("COLLECTOR_EST_X_PROC"))
        self.COLLECTOR_TSLEPP = int(os.getenv("COLLECTOR_TSLEEP"))
        self.COLLECTOR_WORKERS = int(os.getenv("COLLECTOR_WORKERS"))
        self.GSOF_TIMEOUT = int(os.getenv("GSOF_TIMEOUT"))

        if self.COLLECTOR_WORKERS > self.NPROC:
            self.COLLECTOR_WORKERS = self.NPROC

            # RETHINK SETTINGS:
        self.RDB_HOST = os.getenv("RDB_HOST")
        self.RDB_PORT = os.getenv("RDB_PORT")
        self.ORM_SERVICE_HOST = os.getenv("ORM_SERVICE_HOST")


        self.CLL_STATUS = os.getenv("CLL_STATUS")

        self.COLLECTOR_SOCKET_IP = os.getenv("COLLECTOR_SOCKET_IP")
        self.COLLECTOR_SOCKET_PORT = os.getenv("COLLECTOR_SOCKET_PORT")
        self.LOG_PATH = os.getenv("LOG_PATH")


        self.DBDATA =  dict(
            dbuser=os.getenv('%s_DBUSER' %schema),
            dbpass=os.getenv('%s_DBPASS' %schema),
            dbname=os.getenv('%s_DBNAME' %schema),
            dbhost=os.getenv('%s_DBHOST' %schema),
            dbport=os.getenv('%s_DBPORT' %schema))

        self.SERVER_NAME=os.getenv('SERVER_NAME')
    
    def show(self):
        [print("export %s=%s"%(k,v if not isinstance(v, tuple) else v[0])) for k,v in vars(self).items()]

    @property
    def json(self):
        return {k:v if not isinstance(v, tuple) else v[0] for k,v in vars(self).items()}

