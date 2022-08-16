from .._measures.first_last import FirstLast
from ..level import Level
from ..measure_description import MeasureDescription


def first(
    measure: MeasureDescription,
    on: Level,
    /,
) -> MeasureDescription:
    """Return a measure equal to the first value of the passed measure on the level.

    Example:
        MeasureDescription definition::

            m["Turnover first day"] = atoti.first(m["Turnover"], l["Date"])

        Considering a single-level hierarchy ``Date``:

        +------------+----------+--------------------+
        |    Date    | Turnover | Turnover first day |
        +============+==========+====================+
        | 2020-01-01 |      100 |                100 |
        +------------+----------+--------------------+
        | 2020-01-02 |      500 |                100 |
        +------------+----------+--------------------+
        | 2020-01-03 |      200 |                100 |
        +------------+----------+--------------------+
        | 2020-01-04 |      400 |                100 |
        +------------+----------+--------------------+
        | 2020-01-05 |      300 |                100 |
        +------------+----------+--------------------+
        | TOTAL      |     1500 |                100 |
        +------------+----------+--------------------+

    Args:
        measure: The measure to shift.
        on: The level to shift on.

    """
    return FirstLast(
        _underlying_measure=measure, _level_coordinates=on._coordinates, _mode="FIRST"
    )
