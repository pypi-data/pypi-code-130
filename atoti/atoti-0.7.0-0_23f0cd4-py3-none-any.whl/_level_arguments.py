from typing import Tuple

from ._table_utils import ColumnCoordinates
from .order._order import Order
from .type import DataType

LevelArguments = Tuple[str, ColumnCoordinates, DataType, Order]
