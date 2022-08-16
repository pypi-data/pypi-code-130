from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Mapping

from aiohttp import ClientResponse
from aiohttp.typedefs import StrOrURL

__all__ = [
    'ClientResponseContextManager',
    'HttpClientExcData',
]


class ClientResponseContextManager(AbstractContextManager):
    """``aiohttp.ClientResponse`` context manager."""
    def __init__(self, resp: ClientResponse) -> None:
        self._resp = resp

    def __enter__(self) -> ClientResponse:
        return self._resp

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._resp.release()


@dataclass(frozen=True)
class HttpClientExcData:
    """Exception data."""
    url: StrOrURL
    method: str
    params: Mapping[str, Any]
