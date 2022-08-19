from dataclasses import dataclass

from .DataClass import DataClass


@dataclass
class Image(DataClass):
    small: str = None
    big: str = None
    hd: str = None
    id: str = None
    name: str = None
    head: str = None
