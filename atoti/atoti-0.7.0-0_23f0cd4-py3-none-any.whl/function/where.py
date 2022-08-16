from __future__ import annotations

from typing import Optional, Union, overload

from .._condition import Condition
from .._measures.boolean_measure import BooleanMeasure
from .._operation import ConditionOperation, Operation, TernaryOperation, _to_operation
from ..column import Column
from ..measure import Measure
from ..measure_description import LiteralMeasureValue, MeasureDescription, MeasureLike
from .switch import _switch

_OperationLike = Union[LiteralMeasureValue, Column, Operation]


@overload
def where(  # pylint: disable=too-many-positional-parameters
    condition: ConditionOperation,
    true_value: _OperationLike,
    false_value: Optional[_OperationLike] = None,
    /,
) -> TernaryOperation:
    ...


@overload
def where(  # pylint: disable=too-many-positional-parameters
    condition: Union[
        BooleanMeasure,
        Condition,
        Measure,
    ],
    true_value: MeasureLike,
    false_value: Optional[MeasureLike] = None,
    /,
) -> MeasureDescription:
    ...


def where(  # pylint: disable=too-many-positional-parameters
    condition: Union[
        BooleanMeasure,
        ConditionOperation,
        Condition,
        Measure,
    ],
    true_value: Union[MeasureLike, _OperationLike],
    # Not keyword-only to be symmetrical with true_value and because
    # there probably will not be more optional parameters.
    false_value: Optional[Union[MeasureLike, _OperationLike]] = None,
    /,
) -> Union[MeasureDescription, TernaryOperation]:
    """Return a conditional measure.

    This function is like an *if-then-else* statement:

    * Where the condition is ``True``, the new measure will be equal to *true_value*.
    * Where the condition is ``False``, the new measure will be equal to *false_value*.

    If *false_value* is not ``None``, *true_value* and *false_value* must either be both numerical, both boolean or both objects.

    If one of the values compared in the condition is ``None``, the condition will be considered ``False``.

    Different types of conditions are supported:

    * Measures compared to anything measure-like::

        m["Test"] == 20

    * Levels compared to levels, (if the level is not expressed, it is considered ``None``)::

        l["source"] == l["destination"]

    * Levels compared to literals of the same type::

        l["city"] == "Paris"
        l["date"] > datetime.date(2020,1,1)
        l["age"] <= 18

    * A conjunction or disjunction of conditions using the ``&`` operator or ``|`` operator::

        (m["Test"] == 20) & (l["city"] == "Paris")
        (l["Country"] == "USA") | (l["Currency"] == "USD")

    Args:
        condition: The condition to evaluate.
        true_value: The measure to propagate where the condition is ``True``.
        false_value: The measure to propagate where the condition is ``False``.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Id", "City", "Value"],
        ...     data=[
        ...         (0, "Paris", 1.0),
        ...         (1, "Paris", 2.0),
        ...         (2, "London", 3.0),
        ...         (3, "London", 4.0),
        ...         (4, "Paris", 5.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["Id"], table_name="filter example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Paris value"] = tt.where(l["City"] == "Paris", m["Value.SUM"], 0)
        >>> cube.query(m["Paris value"], levels=[l["City"]])
               Paris value
        City
        London         .00
        Paris         8.00

    See also:
        :func:`atoti.switch`.
    """
    if isinstance(condition, ConditionOperation):
        true_operation = _to_operation(true_value)
        false_operation = _to_operation(false_value)
        return TernaryOperation(
            condition=condition,
            true_operation=true_operation,
            false_operation=false_operation,
        )
    if isinstance(true_value, (Column, Operation)) or isinstance(
        false_value, (Column, Operation)
    ):
        raise ValueError(
            "Cannot use tt.where on operations if the condition is not also an operation. Please convert the true (and false) value(s) to a measure(s)."
        )
    return _switch({condition: true_value}, default=false_value)
