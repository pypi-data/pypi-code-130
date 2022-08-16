from __future__ import annotations

from typing import Union

from atoti_core import coordinates_to_java_description, doc

from .._measures.generic_measure import GenericMeasure
from ..level import Level
from ..measure_description import MeasureConvertible, MeasureDescription
from ._utils import EXTREMUM_MEMBER_DOC


@doc(
    EXTREMUM_MEMBER_DOC,
    op="max",
    example="""
        >>> m["City with maximum price"] = tt.agg.max_member(m["Price"], l["City"])

        At the given level, the measure is equal to the current member of the City level:

        >>> cube.query(m["City with maximum price"], levels=[l["City"]])
                               City with maximum price
        Continent     City
        Europe        Berlin                    Berlin
                      London                    London
                      Paris                      Paris
        North America New York                New York

        At a level above it, the measure is equal to the city of each continent with the maximum price:

        >>> cube.query(m["City with maximum price"], levels=[l["Continent"]])
                      City with maximum price
        Continent
        Europe                         London
        North America                New York

        At the top level, the measure is equal to the city with the maximum price across all continents:

        >>> cube.query(m["City with maximum price"])
          City with maximum price
        0                New York""".replace(
        "\n", "", 1
    ),
)
def max_member(
    measure: Union[MeasureConvertible, MeasureDescription], /, level: Level
) -> MeasureDescription:
    if isinstance(measure, MeasureConvertible):
        measure = measure._measure_description

    return GenericMeasure(
        "COMPARABLE_MAX",
        measure,
        coordinates_to_java_description(level._coordinates),
        True,
        "MEMBER",
    )
