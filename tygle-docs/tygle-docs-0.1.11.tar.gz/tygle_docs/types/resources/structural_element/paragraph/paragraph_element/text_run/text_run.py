from typing import List

from pydantic import BaseModel, Field


class TextRun(BaseModel):
    content: str
    suggested_insertion_ids: List[str] = Field(
        default_factory=list, alias="suggestedInsertionIds"
    )
    suggested_deletion_ids: List[str] = Field(
        default_factory=list, alias="suggestedDeletionIds"
    )
