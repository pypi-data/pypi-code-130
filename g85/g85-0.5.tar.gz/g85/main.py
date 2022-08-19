from typing import Dict, List, Tuple, Union, Optional
import datetime
from collections import Counter
from dataclasses import dataclass, field
from itertools import chain


@dataclass
class Device:
    BinType: str
    NullBin: Union[str, int]
    ProductId: Optional[str] = None
    LotId: Optional[str] = None
    WaferSize: Optional[float] = None
    CreateDate: Optional[datetime.datetime] = None
    DeviceSizeX: Optional[float] = None
    DeviceSizeY: Optional[float] = None
    SupplierName: Optional[str] = None
    OriginLocation: Optional[int] = None
    MapType: str = 'Array'
    Orientation: float = 0
    reference_xy: Optional[Tuple[int, int]] = None

    bin_pass: Dict[Union[int, str], bool] = field(default_factory=dict)  # Is this bin passing?
    map: Union[List[List[int]], List[List[str]]] = field(default_factory=list)   # The actual map
    # Map attribs: MapName, MapVersion
    # SupplierData attribs: ProductCode, RecipeName

    misc: Dict[str, str] = field(default_factory=dict)  # Any unexpected fields go here

    @property
    def Rows(self) -> int:
        return len(self.map)

    @property
    def Columns(self) -> int:
        if self.Rows == 0:
            return 0
        return len(self.map[0])

    def bin_counts(self) -> Counter:
        return Counter(chain(*self.map))


@dataclass
class Map:
    xmlns: str = 'http://www.semi.org'
    FormatRevision: str = "SEMI G85 0703"
    SubstrateType: Optional[str] = None
    SubstrateId: Optional[str] = None

    devices: List[Device] = field(default_factory=list)
    misc: Dict[str, str] = field(default_factory=dict)  # Any unexpected fields go here

