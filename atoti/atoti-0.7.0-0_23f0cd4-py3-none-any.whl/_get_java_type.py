from typing import Any, Mapping, Type

from atoti_core import DataType, is_numeric_type, to_array_type

from .type import DOUBLE, LONG, STRING

# Currently, supported types for Python constants.
_PYTHON_TYPE_TO_JAVA_TYPE: Mapping[Type[Any], DataType] = {
    str: STRING,
    # Use the widest type to avoid compilation problems
    int: LONG,
    float: DOUBLE,
}


def get_data_type(value: Any, /) -> DataType:
    python_type = type(value)

    if python_type == list:
        first_element_type = get_data_type(value[0])
        if not is_numeric_type(first_element_type):
            raise TypeError("Only lists of numeric values are supported.")
        return to_array_type(first_element_type)

    try:
        return _PYTHON_TYPE_TO_JAVA_TYPE[python_type]
    except KeyError as error:
        raise TypeError(
            f"Python type: {python_type} has no corresponding data type."
        ) from error
