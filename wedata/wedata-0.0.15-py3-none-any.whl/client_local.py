import os
import glob
import logging

import pandas as pd
from pyarrow import fs
import pyarrow.parquet as pq

from .client import BaseClient
from .utils import get_env


def search_table(table: str, storage_dir: str):
    if storage_dir is None:
        raise Exception("set storage directory before query")
    # check the storage dir
    if not os.path.isdir(storage_dir):
        raise Exception("storage directory path not exist")
    file_list = glob.glob(os.path.join(storage_dir, f'*{table}*.parquet'))
    if len(file_list) == 0:
        raise Exception("table data file not exist")
    return file_list


class LocalClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.storage_dir = None

    def set_storage_dir(self, storage_dir: str):
        if os.path.isdir(storage_dir):
            self.storage_dir = storage_dir
        else:
            raise Exception("storage directory path not exist")

    def query_feature_expose(self, param: dict) -> pd.DataFrame:
        table_name = param['class']
        # todo table name check
        if table_name not in ["aindexeodprices"]:
            raise Exception("invalid table name")
        files = search_table(table_name, self.storage_dir)
        print("\ntable files:")
        for file in files:
            print(file)

        dataset = pq.ParquetDataset(files, use_legacy_dataset=True)
        df = dataset.read().to_pandas()
        return df

    def extract_feature_expose(self, param):
        pass

    def query(self, param):
        pass

    def extract(self, param):
        pass
