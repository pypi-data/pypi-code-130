from pydantic import BaseModel, Field


class Location(BaseModel):
    segment_id: str = Field(alias="segmentId")
    index: int = Field()
