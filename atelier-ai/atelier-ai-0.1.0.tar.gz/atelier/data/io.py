#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Atelier AI: Studio for AI Designers                                                 #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.4                                                                              #
# Filename   : \io.py                                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/atelier-ai                                         #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 15th 2022 06:03:55 pm                                                 #
# Modified   : Tuesday August 16th 2022 08:45:20 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : BSD 3-clause "New" or "Revised" License                                             #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pickle
import logging

import yaml
from yaml.loader import SafeLoader
from typing import Union

# ------------------------------------------------------------------------------------------------ #
logging.getLogger(__name__).addHandler(logging.NullHandler())
# ------------------------------------------------------------------------------------------------ #


class IO(ABC):
    @abstractmethod
    def read(self, filepath: str, **kwargs) -> Union[pd.DataFrame, dict]:
        """Data read. Removed pass to suppress pytest coverage message"""

    @abstractmethod
    def write(self, data: Union[pd.DataFrame, dict], filepath: str, **kwargs) -> None:
        """Data write Removed pass to suppress pytest coverage message"""


# ------------------------------------------------------------------------------------------------ #


class CsvIO(IO):
    def read(self, filepath: str, **kwargs) -> Union[pd.DataFrame, dict]:

        sep = kwargs.get("sep", ",")
        header = kwargs.get("header", "infer")
        index_col = kwargs.get("index_col", False)
        usecols = kwargs.get("usecols", None)
        nrows = kwargs.get("nrows", None)
        encoding = kwargs.get("encoding", "utf-8")
        encoding_errors = kwargs.get("encoding_errors", "strict")
        low_memory = kwargs.get("low_memory", False)
        thousands = kwargs.get("thousands", ",")

        return pd.read_csv(
            filepath,
            sep=sep,
            header=header,
            index_col=index_col,
            usecols=usecols,
            nrows=nrows,
            encoding=encoding,
            encoding_errors=encoding_errors,
            low_memory=low_memory,
            thousands=thousands,
        )

    def write(self, data: Union[pd.DataFrame, dict], filepath: str, **kwargs) -> None:

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        sep = kwargs.get("sep", ",")
        columns = kwargs.get("columns", None)
        header = kwargs.get("header", True)
        index = kwargs.get("index", False)
        index_label = kwargs.get("index_label", False)
        errors = kwargs.get("errors", "strict")
        encoding = kwargs.get("encoding", "utf-8")

        data.to_csv(
            filepath,
            sep=sep,
            columns=columns,
            header=header,
            index=index,
            index_label=index_label,
            errors=errors,
            encoding=encoding,
        )


# ------------------------------------------------------------------------------------------------ #


class YamlIO(IO):
    def read(self, filepath: str, **kwargs) -> Union[pd.DataFrame, dict]:
        with open(filepath, "r") as file:
            return yaml.load(file, Loader=SafeLoader)

    def write(self, data: Union[pd.DataFrame, dict], filepath: str, **kwargs) -> None:

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as file:
            yaml.dump(data, file)


# ------------------------------------------------------------------------------------------------ #


class PickleIO(IO):
    def read(self, filepath: str, **kwargs) -> Union[pd.DataFrame, dict]:

        with open(filepath, "rb") as file:
            return pickle.load(file)

    def write(self, data: Union[pd.DataFrame, dict], filepath: str, **kwargs) -> None:

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as file:
            pickle.dump(data, file)


# ------------------------------------------------------------------------------------------------ #


class ParquetIO(IO):
    """Reads, and writes Spark DataFrames to / from Parquet storage format.."""

    def read(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Reads a Spark DataFrame from Parquet file resource
        Args:
            filepath (str): The path to the parquet file resource
            kwargs:
                column (list): columns to read from the file
        Returns:
            pd.DataFrame
        """
        columns = kwargs.get("columns", None)

        try:
            table = pq.read_table(source=filepath, columns=columns)
            return table.to_pandas()

        except FileNotFoundError as e:
            logging.error("File {} was not found.".format(filepath))
            raise e

    def write(self, data: pd.DataFrame, filepath: str, **kwargs) -> None:
        """Writes Spark DataFrame to Parquet file resource
        Args:
            data (pyspark.sql.DataFrame): Spark DataFrame to write
            filepath (str): The path to the parquet file to be written

        """

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        table = pa.Table.from_pandas(data)
        pq.write_table(table, filepath)


# ------------------------------------------------------------------------------------------------ #


class IOFactory:
    """IO Factory"""

    __io = {
        "csv": CsvIO(),
        "yml": YamlIO(),
        "yaml": YamlIO(),
        "pickle": PickleIO(),
        "pkl": PickleIO(),
        "parquet": ParquetIO(),
    }

    @staticmethod
    def io(fileformat: str) -> IO:
        try:
            return IOFactory.__io[fileformat]
        except KeyError as e:
            logging.error("Format {} is not supported".format(fileformat))
            raise e
