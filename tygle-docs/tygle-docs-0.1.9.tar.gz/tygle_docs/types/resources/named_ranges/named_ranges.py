from typing import List

from pydantic import BaseModel, Field

from .named_range import NamedRange


class NamedRanges(BaseModel):
    name: str = Field()
    named_ranges: List[NamedRange] = Field()
