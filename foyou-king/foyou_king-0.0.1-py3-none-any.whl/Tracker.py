from dataclasses import dataclass

from .DataClass import DataClass


@dataclass
class Tracker(DataClass):
    filename: str = None
    tracker_url: str = None
    url: str = None
    hash: str = None
    backup_url: str = None
    url_valid_duration: int = None
