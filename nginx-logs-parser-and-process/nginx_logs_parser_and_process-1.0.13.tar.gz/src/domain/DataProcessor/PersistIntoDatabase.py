from pandas import DataFrame

from src.infrastructure.Database import Database


class PersistIntoDatabase:
    def __init__(self, database: Database):
        self.database = database
        self.table_name = self.database.get_table_name()
        self.database_conn = self.database.connect()

    def process(self, dataframe: DataFrame):
        if self.database_conn:
            dataframe.to_sql(self.table_name, self.database_conn, if_exists="append")
            self.database.pass_temporal_to_final_logs_table()
