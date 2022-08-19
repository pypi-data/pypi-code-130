from __future__ import annotations

import abc
from typing import Mapping

import aiohttp


class ABCAPI(abc.ABC):

    token: str
    http_client: aiohttp.ClientSession

    @abc.abstractmethod
    async def request(self, method: str, data: Mapping) -> dict:
        pass

    @property
    def api_instance(self) -> ABCAPI:
        return self
