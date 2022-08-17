from pydantic import BaseModel
from typing import List

from dhtc_server.models.Torrent import TorrentFile


class AddTorrentRequest(BaseModel):
    InfoHash: str
    Name: str
    TotalSize: int
    DiscoveredOn: int
    Files: List[TorrentFile]
