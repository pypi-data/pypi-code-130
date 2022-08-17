from pydantic import BaseModel


class TorrentCountResponse(BaseModel):
    Count: int
