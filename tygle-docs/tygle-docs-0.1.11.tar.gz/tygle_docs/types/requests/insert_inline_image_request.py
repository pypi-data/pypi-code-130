from typing import ClassVar, Optional

from pydantic import Field
from tygle_docs.types.resources.models import Size

from .models import EndOfSegmentLocation, Location
from .update_request import UpdateRequestBody


class InsertInlineImage(UpdateRequestBody):
    key: ClassVar = "insertInlineImage"

    uri: str = Field()
    object_size: Size = Field(alias="objectSize")
    location: Optional[Location] = Field(None)
    end_of_segment_location: Optional[EndOfSegmentLocation] = Field(
        None, alias="endOfSegmentLocation"
    )
