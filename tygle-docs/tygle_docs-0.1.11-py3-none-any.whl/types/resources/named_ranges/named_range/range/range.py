from typing import Optional

from pydantic import BaseModel, Field


class Range(BaseModel):
    segment_id: Optional[str] = Field(None, alias="segmentId")
    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
