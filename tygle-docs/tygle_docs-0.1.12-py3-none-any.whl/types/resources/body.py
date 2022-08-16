from typing import List

from pydantic import BaseModel, Field

from .structural_element import StructuralElementList


class Body(BaseModel):
    content: StructuralElementList = Field()
