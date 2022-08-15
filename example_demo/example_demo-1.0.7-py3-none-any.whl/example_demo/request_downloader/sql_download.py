from example_demo.exceptions import OnedatautilConfigException
from sqlalchemy import create_engine
import pandas as pd
from example_demo.request_downloader.mysql_downloader import MYSQLDownloader


class SqlalchemyCon():
    def __init__(self, connect_url):
        self.connect_url = connect_url

    def creat_engine(self):
        return create_engine(self.connect_url)

    def get_data_sql(self, sql):
        engine = create_engine()
        return pd.read_sql(sql, con=engine)

    def df_to_sql(self,dataframe,table,**kwargs):
        engine = create_engine()
        dataframe.to_sql(table, engine,**kwargs)


class SQLDownloader():
    def __init__(self, sour, *args, **kwargs):

        self.db_info = sour.get("request_info")

    def download(self):
        connect_url = self.db_info.get("connect_url")
        get_sql = self.db_info.get("get_sql")
        if not get_sql:
            raise OnedatautilConfigException("no get sql!!")
        if connect_url:
            return SqlalchemyCon(connect_url).get_data_sql(get_sql)
        db_type = self.db_info.get("db_type")
        if db_type == 'mysql':
            request_info = dict(
                host=self.db_info.get("host"),
                port=self.db_info.get("port"),
                user=self.db_info.get("user"),
                passwd=self.db_info.get("password"),
                schema=self.db_info.get("table"),
            )
            return MYSQLDownloader({"request_info": request_info, "mysql_sql_get": get_sql}).download()
