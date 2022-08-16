"""
Types to ease the usage of the API
"""
import csv
from typing import Any, Callable, Dict, Optional, Type

DataCast = Callable[[str], Any]
DataCastDict = Dict[str, DataCast]
DataCasts = Optional[DataCastDict]

BaseDir = Optional[str]
IdColName = Optional[str]

DataFile = str

CsvDialect = Type[csv.Dialect]
