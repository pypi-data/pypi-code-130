from dataclasses import dataclass
from enum import Enum

class PriceType(Enum):
    Static = 0
    Tiered = 1


@dataclass
class LocalePrice:
    currency:str

    


#if tiered, do a list of the tiers
    