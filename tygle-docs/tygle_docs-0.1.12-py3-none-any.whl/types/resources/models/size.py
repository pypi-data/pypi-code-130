from typing import Optional

from pydantic import BaseModel, Field

from .dimension import Dimension


class Size(BaseModel):
    height: Optional[Dimension] = Field(None)
    width: Optional[Dimension] = Field(None)
