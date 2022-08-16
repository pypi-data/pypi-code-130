from typing import List

from pydantic import BaseModel, Field

from .range import Range


class NamedRange(BaseModel):
    named_range_id: str = Field(alias="namedRangeId")
    name: str = Field()
    ranges: List[Range] = Field()
