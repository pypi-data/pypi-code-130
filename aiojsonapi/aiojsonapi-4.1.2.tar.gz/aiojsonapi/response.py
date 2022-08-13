"""Module with API response wrappers."""

import json

import aiohttp.web

from aiojsonapi.config import config


class GoodResponse(aiohttp.web.Response):
    """Wrapper for good response result data."""

    def __init__(self, result, *args, status_code=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = json.dumps({"result": result, "error": False}, cls=config.json_encoder)
        self._status = status_code
        self.content_type = "application/json"


class BadResponse(aiohttp.web.Response):
    """Wrapper for bad response result data."""

    def __init__(self, result, *args, status_code=400, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = json.dumps({"error": True, "reason": result}, cls=config.json_encoder)
        self._status = status_code
        self.content_type = "application/json"
