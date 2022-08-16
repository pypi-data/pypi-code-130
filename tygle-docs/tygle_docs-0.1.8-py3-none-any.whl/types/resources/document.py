from typing import TYPE_CHECKING, ClassVar, Dict

from pydantic import Field, PrivateAttr
from tygle.base import Resource, RESTs

from .body import Body
from .named_ranges import NamedRanges

if TYPE_CHECKING:
    from tygle_docs.rest import Documents


class DocumentRESTs(RESTs):
    def __init__(self, Docs: "Documents") -> None:
        self.Docs = Docs


class Document(Resource):
    __rests__: ClassVar[DocumentRESTs] = PrivateAttr()

    document_id: str = Field(alias="documentId")
    title: str = Field()
    body: Body = Field()
    named_ranges: Dict[str, NamedRanges] = Field()
