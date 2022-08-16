from dataclasses import dataclass, field

@dataclass
class Price:
    price_aware: bool = False
    allow_top_up: bool = False
    min_price: float = 0.0
    top_price: float = 0.0
    cautionhour_type: float = 0.0

@dataclass
class HubOptions:
    price: Price
    peaqev_lite: bool = False
    powersensor_includes_car: bool = False
    locale: str = ""
    chargertype: str = ""
    chargerid: str = ""
    startpeaks: dict = field(default_factory=dict)
    behavior_on_default: bool = False
    cautionhours: list = field(default_factory=[])
    nonhours: list = field(default_factory=[])