from dataclasses import dataclass

from .DataClass import DataClass


# noinspection SpellCheckingInspection
@dataclass
class TipResponse(DataClass):
    Use: str = None
    IsRadio: int = None
    HintInfo: str = None
    MatchCount: int = None
    IsKlist: int = None
    Hot: int = None
