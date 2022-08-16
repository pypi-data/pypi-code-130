from pydantic import BaseModel, Field


class EndOfSegmentLocation(BaseModel):
    segment_id: str = Field(alias="segmentId")
