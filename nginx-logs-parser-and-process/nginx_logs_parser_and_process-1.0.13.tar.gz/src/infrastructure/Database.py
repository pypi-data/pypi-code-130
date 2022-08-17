from abc import ABC


class Database(ABC):
    def __init__(self):
        pass

    def connect(self):
        raise NotImplementedError

    def get_table_name(self) -> str:
        raise NotImplementedError

    def truncate_table(self):
        raise NotImplementedError

    def pass_temporal_to_final_logs_table(self):
        raise NotImplementedError
