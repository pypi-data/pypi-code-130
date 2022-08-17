from pydantic import BaseModel


class SearchTorrentRequest(BaseModel):
    Text: str
