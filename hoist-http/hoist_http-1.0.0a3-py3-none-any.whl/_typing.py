from typing import (
    TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type,
    TypeVar, Union
)

from typing_extensions import Protocol

if TYPE_CHECKING:
    from versions import Version
    from yarl import URL

    from ._messages import BaseMessagable, ListenerData
    from .message import Message
    from .server import Server


_T = TypeVar("_T")


class DataclassLike(Protocol):
    """Protocol representing a dataclass-like object."""

    __annotations__: Dict[str, Any]

    def __init__(self, *args, **kwargs) -> None:
        ...


_A = TypeVar("_A", bound=Type[DataclassLike])

Payload = Dict[str, Any]
Operator = Callable[[_T], Awaitable[Any]]
SchemaNeededType = Union[Type[Any], Tuple[Optional[Type[Any]], ...]]
Schema = Dict[str, SchemaNeededType]
Operations = Dict[str, Operator]
UrlLike = Union[str, "URL"]
LoginFunc = Callable[["Server", str], Awaitable[bool]]
ResponseErrors = Dict[int, Tuple[str, str]]
Listener = Union[
    Callable[["Message", _T], Awaitable[None]],
    Callable[["Message"], Awaitable[None]],
    Callable[[], Awaitable[None]],
]
MessageListeners = Dict[
    Optional[Union[Tuple[str, ...], str]],
    List["ListenerData"],
]
VersionLike = Union[str, "Version"]


TransportMessageListener = Callable[
    ["BaseMessagable", str, Payload, Optional[dict], int],
    Awaitable[None],
]
