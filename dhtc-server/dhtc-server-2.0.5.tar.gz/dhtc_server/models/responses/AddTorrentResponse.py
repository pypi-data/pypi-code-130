from pydantic import BaseModel


class AddTorrentResponse(BaseModel):
    InfoHash: str
    SeenCount: int
