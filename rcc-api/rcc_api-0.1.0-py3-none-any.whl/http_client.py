from __future__ import annotations

from typing import Optional

import aiohttp


class AiohttpClient:
    def __init__(
        self, session: Optional[aiohttp.ClientSession] = None, **session_params
    ):
        self.session = session

        self._session_params = session_params

        user_agent = "RustCheatCheckAPI (https://github.com/MaHryCT3/RCC_api)"
        self.headers: dict[str, str] = {
            "User-Agent": user_agent,
        }

    async def request_raw(
        self,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        if not self.session:
            self.session = aiohttp.ClientSession(**self._session_params)
        self.session.headers.update(self.headers)
        async with self.session.request(
            url=url, method=method, params=params, **kwargs
        ) as response:
            await response.read()
            return response

    async def request_json(
        self,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        response = await self.request_raw(url, method, params, **kwargs)
        return await response.json(encoding="utf-8", content_type=None)

    async def request_text(
        self,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        **kwargs,
    ) -> str:
        response = await self.request_raw(url, method, params, **kwargs)
        return await response.text(encoding="utf-8")

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self) -> AiohttpClient:
        return self

    async def __aexit__(self) -> None:
        await self.close()

    def __del__(self):
        if self.session and not self.session.closed:
            if self.session._connector is not None and self.session._connector_owner:
                self.session._connector.close()
            self.session._connector = None
