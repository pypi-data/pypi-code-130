from typing import ClassVar

from pydantic import Field
from tygle_docs.types.resources.named_ranges.named_range.range import Range

from .update_request import UpdateRequestBody


class DeleteContentRange(UpdateRequestBody):
    key: ClassVar = "deleteContentRange"

    range: Range = Field()
