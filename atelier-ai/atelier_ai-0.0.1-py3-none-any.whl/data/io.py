#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Atelier - Workspace for Sculpting and Curating Data Science                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.4                                                                              #
# Filename   : /io.py                                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/atelier                                            #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 15th 2022 06:03:55 pm                                                 #
# Modified   : Monday August 15th 2022 07:13:31 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : BSD 3-clause "New" or "Revised" License                                             #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
import os
import pickle
import logging
import pandas as pd
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
        encoding_errors = kwargs.get("encoding_errors", "strict")
        header = kwargs.get("header", "infer")
        usecols = kwargs.get("usecols", None)
        nrows = kwargs.get("nrows", None)
        thousands = kwargs.get("thousands", ",")

        return pd.read_csv(
            filepath,
            encoding_errors=encoding_errors,
            sep=sep,
            header=header,
            usecols=usecols,
            nrows=nrows,
            thousands=thousands,
        )

    def write(self, data: Union[pd.DataFrame, dict], filepath: str, **kwargs) -> None:

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        sep = kwargs.get("sep", ",")
        header = kwargs.get("header", True)
        columns = kwargs.get("columns", None)
        index = kwargs.get("index", False)
        errors = kwargs.get("errors", "strict")
        encoding = kwargs.get("encoding", "utf-8")

        data.to_csv(
            filepath,
            sep=sep,
            header=header,
            columns=columns,
            index=index,
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


class IOFactory:
    """IO Factory"""

    __io = {
        "csv": CsvIO(),
        "yml": YamlIO(),
        "yaml": YamlIO(),
        "pickle": PickleIO(),
        "pkl": PickleIO(),
    }

    @staticmethod
    def io(fileformat: str) -> IO:
        try:
            return IOFactory.__io[fileformat]
        except KeyError as e:
            logging.error("Format {} is not supported".format(fileformat))
            raise e
