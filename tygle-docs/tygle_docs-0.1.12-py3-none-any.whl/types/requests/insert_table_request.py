from typing import ClassVar, Optional

from pydantic import Field

from .models import EndOfSegmentLocation, Location
from .update_request import UpdateRequestBody


class InsertTable(UpdateRequestBody):
    key: ClassVar = "insertTable"

    rows: int = Field()
    columns: int = Field()
    location: Optional[Location] = Field(None)
    end_of_segment_location: Optional[EndOfSegmentLocation] = Field(
        None, alias="endOfSegmentLocation"
    )
