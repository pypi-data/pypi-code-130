from typing import Optional

from pydantic import BaseModel, Field


class TagsModel(BaseModel):
    created_on: Optional[str] = Field(alias="created_on")
    modified_on: Optional[str] = Field(alias="modified_on")
    tags_id: int = Field(alias="tags_id")
    tags_name: str = Field(alias="tags_name")
    tags_description: str = Field(alias="tags_description")
