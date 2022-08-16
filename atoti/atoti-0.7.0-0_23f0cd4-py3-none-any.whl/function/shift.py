from typing import Union

from atoti_core import coordinates_to_java_description, deprecated

from atoti.hierarchy import Hierarchy
from atoti.level import Level

from .._measures.generic_measure import GenericMeasure
from ..hierarchy import Hierarchy
from ..measure_description import MeasureDescription


def shift(
    measure: MeasureDescription,
    on: Union[Hierarchy, Level],
    /,
    *,
    offset: int = 1,
) -> MeasureDescription:
    """Return a measure equal to the passed measure shifted to another member of the hierarchy.

    Args:
        measure: The measure to shift.
        on: The hierarchy to shift on.
        offset: The amount of members to shift by.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Country", "City", "Price"],
        ...     data=[
        ...         ("France", "Bordeaux", 1),
        ...         ("France", "Lyon", 2),
        ...         ("France", "Paris", 3),
        ...         ("Germany", "Berlin", 4),
        ...         ("Germany", "Frankfurt", 5),
        ...         ("Germany", "Munich", 6),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     table_name="Shift example",
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> m["Shifted Price.SUM"] = tt.shift(m["Price.SUM"], h["City"], offset=2)
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Shifted Price.SUM"],
        ...     levels=[l["City"]],
        ...     include_totals=True,
        ... )
                  Price.SUM Shifted Price.SUM
        City
        Total            21
        Berlin            4                 5
        Bordeaux          1                 2
        Frankfurt         5                 6
        Lyon              2                 3
        Munich            6
        Paris             3

        >>> h["Location"] = [l["Country"], l["City"]]
        >>> m["Shifted Price.SUM"] = tt.shift(m["Price.SUM"], h["Location"], offset=1)
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Shifted Price.SUM"],
        ...     levels=[
        ...         l["Shift example", "Location", "Country"],
        ...         l["Shift example", "Location", "City"],
        ...     ],
        ...     include_totals=True,
        ... )
                          Price.SUM Shifted Price.SUM
        Country City
        Total                    21
        France                    6                15
                Bordeaux          1                 2
                Lyon              2                 3
                Paris             3                 4
        Germany                  15
                Berlin            4                 5
                Frankfurt         5                 6
                Munich            6
    """
    if isinstance(on, Level):
        deprecated(
            "Passing a `Level` to the *on* parameter is deprecated, use a `Hierarchy` instead."
        )

    return GenericMeasure(
        "LEAD_LAG",
        measure,
        coordinates_to_java_description(
            on._coordinates if isinstance(on, Hierarchy) else on._hierarchy_coordinates
        ),
        offset,
    )
