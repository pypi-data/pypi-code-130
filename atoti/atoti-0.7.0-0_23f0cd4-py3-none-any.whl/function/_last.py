from .._measures.first_last import FirstLast
from ..level import Level
from ..measure_description import MeasureDescription


def last(
    measure: MeasureDescription,
    on: Level,
    /,
) -> MeasureDescription:
    """Return a measure equal to the last value of the passed measure on the level.

    Example:
        Measure definition::

            m["Turnover last day"] = atoti.last(m["Turnover"], l["Date"])

        Considering a single-level hierarchy ``Date``:

        +------------+----------+-------------------+
        |    Date    | Turnover | Turnover last day |
        +============+==========+===================+
        | 2020-01-01 |      100 |               300 |
        +------------+----------+-------------------+
        | 2020-01-02 |      500 |               300 |
        +------------+----------+-------------------+
        | 2020-01-03 |      200 |               300 |
        +------------+----------+-------------------+
        | 2020-01-04 |      400 |               300 |
        +------------+----------+-------------------+
        | 2020-01-05 |      300 |               300 |
        +------------+----------+-------------------+
        | TOTAL      |     1500 |               300 |
        +------------+----------+-------------------+

    Args:
        measure: The measure to shift.
        on: The level to shift on.

    """
    return FirstLast(
        _underlying_measure=measure, _level_coordinates=on._coordinates, _mode="LAST"
    )
