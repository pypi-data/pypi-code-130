"""Helper functions for converting operations into Java code."""
from typing import Callable, Mapping, Optional

from atoti_core import DataType, is_numeric_array_type, is_numeric_type

from ...column import Column
from ...type import BOOLEAN, DOUBLE, FLOAT, INT, LONG

_BUFFER_WRITE_TEMPLATE = "{buffer_code}.{writer_code}(0, {value_code});"


_READERS: Mapping[DataType, Callable[[int], str]] = {
    BOOLEAN: lambda index: f"fact.readBoolean({index})",
    INT: lambda index: f"fact.readInt({index})",
    LONG: lambda index: f"fact.readLong({index})",
    FLOAT: lambda index: f"fact.readFloat({index})",
    DOUBLE: lambda index: f"fact.readDouble({index})",
}


def get_column_reader_code(column: Column, index: int) -> str:
    def _default(i: int) -> str:
        if is_numeric_array_type(column.data_type):
            return f"(fact.isNull({i}) ? null : fact.readVector({i}).cloneOnHeap())"
        raise TypeError("Unsupported column type: " + column.data_type)

    return _READERS.get(column.data_type, _default)(index)


def _ensure_java_numeric_scalar_output_type(output_type: DataType) -> None:
    if not is_numeric_type(output_type):
        raise TypeError("Unsupported output type: " + output_type)


def get_buffer_read_code(*, buffer_code: str, output_type: DataType) -> str:
    _ensure_java_numeric_scalar_output_type(output_type)

    method_name = f"read{output_type.capitalize()}"
    return f"{buffer_code}.{method_name}(0)"


def get_buffer_add_code(
    *, buffer_code: str, value_code: str, output_type: DataType
) -> str:
    _ensure_java_numeric_scalar_output_type(output_type)
    writer_code = f"add{output_type.capitalize()}"
    return _BUFFER_WRITE_TEMPLATE.format(
        buffer_code=buffer_code, writer_code=writer_code, value_code=value_code
    )


def get_buffer_write_code(
    *, buffer_code: str, value_code: str, output_type: Optional[DataType]
) -> str:
    if output_type is None:
        return _BUFFER_WRITE_TEMPLATE.format(
            buffer_code=buffer_code, writer_code="write", value_code=value_code
        )

    _ensure_java_numeric_scalar_output_type(output_type)

    writer_code = f"write{output_type.capitalize()}"
    return _BUFFER_WRITE_TEMPLATE.format(
        buffer_code=buffer_code, writer_code=writer_code, value_code=value_code
    )


_TERMINATE_CODE: Mapping[DataType, Callable[[str], str]] = {
    DOUBLE: lambda value_code: f"Double.valueOf({value_code})",
    FLOAT: lambda value_code: f"Float.valueOf({value_code})",
    LONG: lambda value_code: f"Long.valueOf({value_code})",
    INT: lambda value_code: f"Integer.valueOf({value_code})",
}


def get_terminate_code(output_type: DataType, value_code: str) -> str:
    def _raise(_: str) -> str:
        raise TypeError("Unsupported output type: " + output_type)

    return _TERMINATE_CODE.get(output_type, _raise)(value_code)
