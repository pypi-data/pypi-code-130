from typing import Any, List, Mapping, Optional, Tuple

from atoti_core import coordinates_to_java_description

from .._measures.generic_measure import GenericMeasure
from ..level import Level
from ..measure_description import MeasureDescription


def _unwrap_conditions(
    conditions: Mapping[Level, Any]
) -> Tuple[List[Level], List[Any], List[Optional[Level]]]:
    """Unwrap a map of conditions.

    Transform a map of conditions into its corresponding list of levels, values, and target levels.
    """
    levels: List[Level] = []
    values: List[Any] = []
    target_levels: List[Optional[Level]] = []
    for level, value in conditions.items():
        levels.append(level)
        if isinstance(value, Level):
            target_levels.append(value)
            values.append(None)
        else:
            target_levels.append(None)
            values.append(value)
    return levels, values, target_levels


def at(
    measure: MeasureDescription, coordinates: Mapping[Level, Any], /
) -> MeasureDescription:
    """Return a measure equal to the passed measure at some other coordinates of the cube.

    Args:
        measure: The measure to take at other coordinates.
        coordinates: A ``{level_to_shift_on: value_to_shift_to}`` mapping.

                .. doctest::

                    >>> df = pd.DataFrame(
                    ...     columns=[
                    ...         "Country",
                    ...         "City",
                    ...         "Target Country",
                    ...         "Target City",
                    ...         "Quantity",
                    ...     ],
                    ...     data=[
                    ...         ("Germany", "Berlin", "UK", "London", 15),
                    ...         ("UK", "London", "Germany", "Berlin", 24),
                    ...         ("USA", "New York", "UK", "London", 10),
                    ...         ("USA", "New York", "France", "Paris", 3),
                    ...         ("USA", "Seattle", "Germany", "Berlin", 3),
                    ...     ],
                    ... )
                    >>> table = session.read_pandas(df, table_name="At")
                    >>> cube = session.create_cube(table, mode="manual")
                    >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
                    >>> h["Geography"] = [table["Country"], table["City"]]
                    >>> h["Target Geography"] = [
                    ...     table["Target Country"],
                    ...     table["Target City"],
                    ... ]
                    >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
                    >>> # Using a constant matching an existing member of the key level
                    >>> m["USA quantity"] = tt.at(
                    ...     m["Quantity.SUM"], {l["Country"]: "USA"}
                    ... )
                    >>> cube.query(
                    ...     m["Quantity.SUM"],
                    ...     m["USA quantity"],
                    ...     levels=[l["Country"]],
                    ... )
                            Quantity.SUM USA quantity
                    Country
                    Germany           15           16
                    UK                24           16
                    USA               16           16
                    >>> # Using another level whose current member the key level will be shifted to
                    >>> m["Target quantity"] = tt.at(
                    ...     m["Quantity.SUM"],
                    ...     {
                    ...         l["Country"]: l["Target Country"],
                    ...         l["City"]: l["Target City"],
                    ...     },
                    ... )
                    >>> cube.query(
                    ...     m["Quantity.SUM"],
                    ...     m["Target quantity"],
                    ...     levels=[l["City"], l["Target City"]],
                    ... )
                                                                Quantity.SUM Target quantity
                    Country City     Target Country Target City
                    Germany Berlin   UK             London                15              24
                    UK      London   Germany        Berlin                24              15
                    USA     New York France         Paris                  3
                                     UK             London                10              24
                            Seattle  Germany        Berlin                 3              15

              If this other level is not expressed, the shifting will not be done.

    """
    levels, values, target_levels = _unwrap_conditions(coordinates)
    return GenericMeasure(
        "LEVEL_AT",
        measure,
        [coordinates_to_java_description(level._coordinates) for level in levels],
        values,
        [
            coordinates_to_java_description(level._coordinates)
            for level in target_levels
            if level is not None
        ],
    )
