import os
from sqlalchemy.sql import text as sa_text
from sqlalchemy import create_engine
from src.infrastructure.Database import Database


class CanadaThreeDatabase(Database):
    def __init__(self):
        self.engine = None
        super().__init__()

    def connect(self):
        if not self.engine:
            print("Connecting")
            self.engine = create_engine(os.environ.get("DESTINATION_DATABASE_URI"))
        return self.engine

    def get_table_name(self) -> str:
        return "temporal_logs"

    def get_destination_table_name(self) -> str:
        return "logs"

    def truncate_table(self):
        if self.engine:
            print("Truncating table")
            self.engine.execute(sa_text(f"""TRUNCATE TABLE {self.get_table_name()}""").execution_options(autocommit=True))

    def pass_temporal_to_final_logs_table(self):
        if self.engine:
            print("Passing from temporal to logs table")
            self.engine.execute(
                sa_text(
                    f"""
                DELETE FROM {self.get_table_name()} WHERE uniqueid in (SELECT uniqueid from {self.get_destination_table_name()});
                
                INSERT INTO {self.get_destination_table_name()} (ip, str_datetime, request, status, "size", referer, 
                    user_agent, log_datetime, log_date, log_time, logged, data_from_server, uniqueid)
                SELECT ip, str_datetime, request, status, "size", referer, 
                    user_agent, log_datetime, log_date, log_time, logged, data_from_server, uniqueid
                FROM {self.get_table_name()};
                """
                ).execution_options(autocommit=True)
            )
            self.update_logs2_with_request_without_password()

    def update_logs2_with_request_without_password(self):
        query = """
            INSERT INTO public.logs2
            ("index", ip, str_datetime, request, status, "size", referer, user_agent, log_datetime, log_date, log_time
            , logged, data_from_server, uniqueid)
            SELECT 
            l."index", l.ip, l.str_datetime, REGEXP_REPLACE(l.request, '(password=.*&)(username=.*)', '\2') as request
            , l.status, l."size", l.referer, l.user_agent, l.log_datetime, l.log_date, l.log_time, l.logged
            , l.data_from_server, l.uniqueid
            from public.logs l
            left join logs2 l2 on l2.uniqueid = l.uniqueid 
            where l2.uniqueid is null;
        """
        self.engine.execute(sa_text(query).execution_options(autocommit=True))
