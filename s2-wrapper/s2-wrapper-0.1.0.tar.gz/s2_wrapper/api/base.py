import json
from dataclasses import dataclass, asdict
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from httpx import Client


class BaseEndpoints:
    _client: "Client"

    API_PATH: str

    def __init__(self, client: "Client") -> None:
        self._client = client
