from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .paragraph import Paragraph
from .table import Table


class StructuralElement(BaseModel):
    start_index: Optional[int] = Field(None, alias="startIndex")
    end_index: int = Field(alias="endIndex")
    paragraph: Optional[Paragraph] = Field(None)
    section_break: Optional[Dict[str, Dict]] = Field(
        None, alias="sectionBreak"
    )  # TODO: Type
    table: Optional[Table] = Field(None)
    table_of_contents: Optional[Dict[str, Dict]] = Field(
        None, alias="tableOfContents"
    )  # TODO: Type


class StructuralElementList(BaseModel):
    __root__: List[StructuralElement]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __len__(self):
        return len(self.__root__)
