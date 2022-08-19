from typing import Literal
import enum

import pydantic

from RCC.exceptions import PlayerInfoNotFound, RCCStatusError


status_types = Literal["success", "error"]


class ErrorTypes(enum.Enum):
    player_not_found = "Игрок не вызывался на проверку и баны отсутствуют"


class BaseModel(pydantic.BaseModel):
    pass


__all__ = ("Base", "BaseModel")
