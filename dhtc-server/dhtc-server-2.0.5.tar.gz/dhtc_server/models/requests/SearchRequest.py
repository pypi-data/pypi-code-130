from pydantic import Field, BaseModel

from dhtc_server.enums.SearchType import SearchType
from dhtc_server.enums.SearchMode import SearchMode


class SearchRequest(BaseModel):
    type: SearchType = Field()
    mode: SearchMode = Field()
    text: str = Field()
