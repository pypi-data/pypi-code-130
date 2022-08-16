from typing import ClassVar

from pydantic import BaseModel, Field
from tygle_docs.types.responses import ReplaceAllTextResponse

from .update_request import UpdateRequestBody


class SubstringMatchCriteria(BaseModel):
    text: str = Field()
    match_case: bool = Field(alias="matchCase")


class ReplaceAllText(UpdateRequestBody):
    response_type: ClassVar = ReplaceAllTextResponse
    key: ClassVar = "replaceAllText"

    replace_text: str = Field(alias="replaceText")
    contains_text: SubstringMatchCriteria = Field(alias="containsText")
