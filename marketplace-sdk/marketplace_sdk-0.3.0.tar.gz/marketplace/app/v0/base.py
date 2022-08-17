import json
from typing import List

from fastapi.responses import HTMLResponse
from marketplace_standard_app_api.models.system import GlobalSearchResponse

from marketplace.client import MarketPlaceClient

from ..utils import check_capability_availability


class _MarketPlaceAppBase:
    def __init__(self, client: MarketPlaceClient, capabilities: List):
        self._client: MarketPlaceClient = client
        self.capabilities = capabilities  # FOR DEBUGGING

    @check_capability_availability
    def frontend(self) -> HTMLResponse:
        return self._client.get(path="frontend")

    @check_capability_availability
    def heartbeat(self) -> HTMLResponse:
        return self._client.get(path="heartbeat")

    @check_capability_availability
    def global_search(
        self, q: str, limit: int = 100, offset: int = 0
    ) -> GlobalSearchResponse:
        return GlobalSearchResponse.parse_obj(
            json.loads(
                self._client.get(
                    "globalSearch", params={"q": q, "limit": limit, "offset": offset}
                )
            )
        )
