from typing import Optional, Mapping

import aiohttp

# from loguru import logger

from RCC.http_client import AiohttpClient
from RCC.methods import APIMethods


class API(APIMethods):
    """Апи для взаимодействия с рцц

    Все методы находятся в модуле methods.py
    """

    API_URL = "https://rustcheatcheck.ru/panel/api"

    def __init__(self, token: str, *, session: Optional[aiohttp.ClientSession] = None):
        self.token = token
        self.http_client = AiohttpClient(session or aiohttp.ClientSession())

    async def request(self, method: str, data: Mapping) -> dict:
        params = {"action": method, "key": self.token}
        params = params | data

        response = await self.http_client.request_json(
            self.API_URL,
            method="GET",
            params=params,
        )
        # logger.debug("Request: {} with {} params returned {}", method, params, response)
        return response
