from dataclasses import dataclass
from typing import Any, Collection, Literal, Mapping, Optional, Sequence

from atoti_core import EMPTY_MAPPING, LevelCoordinates, keyword_only_dataclass

AggregateProviderKey = Literal["bitmap", "leaf"]


@keyword_only_dataclass
@dataclass(frozen=True)
class AggregateProviderDescription:
    key: AggregateProviderKey
    levels_coordinates: Collection[LevelCoordinates] = ()
    measures_names: Collection[str] = ()
    filters: Mapping[LevelCoordinates, Sequence[Any]] = EMPTY_MAPPING
    partitioning: Optional[str] = None
