from __future__ import annotations

from functools import reduce
from typing import Dict, List, Mapping, Optional, Tuple, Union

from .._condition import Condition
from .._data_type_error import DataTypeError
from .._measures.boolean_measure import BooleanMeasure
from .._measures.filtered_measure import SwitchMeasure
from .._multi_condition import MultiCondition
from .._single_condition import SingleCondition
from ..measure import Measure
from ..measure_description import (
    LiteralMeasureValue,
    MeasureConvertible,
    MeasureDescription,
    MeasureLike,
    _convert_to_measure_description,
)
from ..type import BOOLEAN


def switch(
    subject: Union[MeasureDescription, MeasureConvertible],
    cases: Mapping[
        Optional[Union[LiteralMeasureValue, Tuple[Optional[LiteralMeasureValue], ...]]],
        MeasureLike,
    ],
    /,
    *,
    default: Optional[MeasureLike] = None,
) -> MeasureDescription:
    """Return a measure equal to the value of the first case for which *subject* is equal to the case's key.

    *cases*'s values and *default* must either be all numerical, all boolean or all objects.

    Args:
        subject: The measure or level to compare to *cases*' keys.
        cases: A mapping from keys to compare with *subject* to the values to return if the comparison is ``True``.
        default: The measure to use when none of the *cases* matched.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Id", "City", "Value"],
        ...     data=[
        ...         (0, "Paris", 1.0),
        ...         (1, "Paris", 2.0),
        ...         (2, "London", 3.0),
        ...         (3, "London", 4.0),
        ...         (4, "Paris", 5.0),
        ...         (5, "Singapore", 7.0),
        ...         (6, "NYC", 2.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["Id"], table_name="Switch example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Continent"] = tt.switch(
        ...     l["City"],
        ...     {
        ...         ("Paris", "London"): "Europe",
        ...         "Singapore": "Asia",
        ...         "NYC": "North America",
        ...     },
        ... )
        >>> cube.query(m["Continent"], levels=[l["City"]])
                       Continent
        City
        London            Europe
        NYC        North America
        Paris             Europe
        Singapore           Asia
        >>> m["Europe & Asia value"] = tt.agg.sum(
        ...     tt.switch(
        ...         m["Continent"], {("Europe", "Asia"): m["Value.SUM"]}, default=0.0
        ...     ),
        ...     scope=tt.OriginScope(l["Id"], l["City"]),
        ... )
        >>> cube.query(m["Europe & Asia value"], levels=[l["City"]])
                  Europe & Asia value
        City
        London                   7.00
        NYC                       .00
        Paris                    8.00
        Singapore                7.00
        >>> cube.query(m["Europe & Asia value"])
          Europe & Asia value
        0               22.00

    See also:
        :func:`atoti.where`.
    """
    condition_to_measure = {}
    for conditions, measure in cases.items():
        if not isinstance(conditions, tuple) or conditions is None:
            condition_to_measure[subject == conditions] = measure
        else:
            condition_to_measure[
                reduce(
                    lambda a, b: a | b,
                    [subject == condition for condition in conditions],
                )
            ] = measure
    return _switch(condition_to_measure, default=default)


def _switch(
    condition_to_measure: Mapping[
        Union[
            BooleanMeasure,
            Condition,
            Measure,
        ],
        MeasureLike,
    ],
    /,
    *,
    default: Optional[MeasureLike] = None,
) -> MeasureDescription:
    measure_to_conditions: Dict[MeasureDescription, Tuple[MeasureDescription, ...]] = {}

    for condition, true_value in condition_to_measure.items():
        conditions: List[MeasureDescription] = []

        if isinstance(condition, BooleanMeasure):
            conditions.append(condition)

        elif isinstance(condition, SingleCondition):
            conditions.append(condition._measure_description)

        elif isinstance(condition, Measure):
            if condition.data_type != BOOLEAN:
                message = (
                    "Incorrect measure type."
                    f" Expected measure {condition.name} to be of type boolean but got {condition.data_type}."
                )
                raise DataTypeError(message)

            conditions.append(condition)

        elif isinstance(condition, MultiCondition):
            for _condition in condition.conditions:
                if isinstance(_condition, SingleCondition):
                    conditions.append(_condition._measure_description)
                if isinstance(_condition, BooleanMeasure):
                    conditions.append(_condition)
        measure_to_conditions[_convert_to_measure_description(true_value)] = (
            *conditions,
        )

    return SwitchMeasure(
        _measure_to_conditions=measure_to_conditions,
        _default_measure=_convert_to_measure_description(default)
        if default is not None
        else None,
    )
