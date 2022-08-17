from sqlitedict import SqliteDict
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from pathlib import Path
from os import makedirs
import logging

LOGGER = logging.getLogger(__name__)


class SqliteGtfo:
    def __init__(self, table_name, table_path=None, auto_init=True):
        self.db = None
        self.table_name = table_name
        if not table_path:
            table_path = env_vars()['NU_TABLE_PATH']
        makedirs(table_path, exist_ok=True)
        self.full_db_path = Path(f"{table_path}/{table_name}.sqlite").absolute()

        if auto_init:
            self._init_db()

    def _init_db(self):
        self.db = SqliteDict(self.full_db_path.as_posix(), tablename='gtfo', autocommit=False)

    def write(self, key, value):
        self.db[key] = value
        self.db.commit()

    def write_batch(self, write_dict):
        for key, value in write_dict.items():
            self.db[key] = value
        self.db.commit()

    def read(self, key):
        try:
            return self.db[key]
        except KeyError:
            return ''

    def delete(self, key):
        del self.db[key]
        self.db.commit()

    def close(self):
        self.db.close()
