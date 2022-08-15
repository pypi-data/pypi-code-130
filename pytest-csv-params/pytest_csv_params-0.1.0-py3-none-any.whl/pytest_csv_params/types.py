"""
Types to ease the usage of the API
"""
import csv
from typing import Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")

DataCast = Callable[[str], T]
DataCastDict = Dict[str, DataCast]

BaseDir = Optional[str]
IdColName = Optional[str]

DataFile = str

CsvDialect = Type[csv.Dialect]
