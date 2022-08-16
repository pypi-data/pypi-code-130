from pydantic import BaseModel, Field


class Range(BaseModel):
    segment_id: str = Field(alias="segmentId")
    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
