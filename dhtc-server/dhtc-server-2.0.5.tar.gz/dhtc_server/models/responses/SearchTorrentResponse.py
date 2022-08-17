from pydantic import BaseModel
from typing import List

from dhtc_server.models.Torrent import Torrent


class SearchTorrentResponse(BaseModel):
    Torrents: List[Torrent]
