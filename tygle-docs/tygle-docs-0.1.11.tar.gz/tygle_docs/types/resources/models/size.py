from pydantic import BaseModel, Field

from .dimension import Dimension


class Size(BaseModel):
    height: Dimension = Field()
    width: Dimension = Field()
