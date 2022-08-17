import logging
from typing import NamedTuple, Type, TypeVar, get_type_hints

from ._logging import log
from ._typing import Operations, Operator, Payload, Schema
from .exceptions import SchemaValidationError

T = TypeVar("T")


class _Print(NamedTuple):
    text: str


async def _print(payload: _Print):
    print(payload.text)


BASE_OPERATIONS: Operations = {"print": _print}


def verify_schema(schema: Schema, data: Payload) -> None:
    """Verify that a payload matches the schema."""
    for key, typ in schema.items():
        value = data.get(key)
        vtype = type(value) if value is not None else None

        if isinstance(typ, tuple):
            if vtype not in typ:
                log(
                    "schema validation",
                    f"expected {', '.join([i.__name__ if i else 'None' for i in typ])}, got {vtype}",  # noqa
                    level=logging.DEBUG,
                )
                raise SchemaValidationError(current=vtype, needed=typ)
            continue

        if vtype is not typ:
            log(
                "schema validation",
                f"expected {typ.__name__}, got {vtype}",
                level=logging.DEBUG,
            )
            raise SchemaValidationError(current=vtype, needed=typ)


async def call_operation(op: Operator[T], payload: Payload) -> None:
    """Call an operation."""
    hints = get_type_hints(op)
    cl: Type[T] = hints[tuple(hints.keys())[0]]

    verify_schema(get_type_hints(cl), payload)
    await op(cl(**payload))


def invalid_payload(exc: SchemaValidationError) -> Payload:
    """Raise an invalid payload error."""
    needed = exc.needed

    return {
        "current": exc.current,
        "needed": exc.needed.__name__  # type: ignore
        if not isinstance(needed, tuple)
        else [i.__name__ if i else str(i) for i in needed],
    }
