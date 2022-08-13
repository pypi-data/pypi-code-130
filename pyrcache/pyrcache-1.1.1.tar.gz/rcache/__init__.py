#!/usr/bin/env python3

from __future__ import annotations
import requests

# GET one object
def rget(key: str, host: str = "localhost", port: int = 8080, db: int = 0) -> any:
    try:
        result = rsend("get", key, "", host=host, port=port, db=db)
    except JSONDecodeError as err:
        raise JSONDecodeError(f"rget() -> {err}")
    else:
        return result

# POST one object
def rset(key: str, value: str, host: str = "localhost", port: int = 8080, db: int = 0):
    rsend("set", key, value, host=host, port=port, db=db)

# GET all keys
def rkeys(host: str = "localhost", port: int = 8080, db: int = 0) -> list[str]:
    try:
        result = rsend("get", "", "", host=host, port=port, db=db)
    except JSONDecodeError as err:
        raise JSONDecodeError(f"rkeys() -> {err}")
    else:
        return result

# Send a request
def rsend(method: str, key: str, value: str, host: str = "localhost", port: int = 8080, db: int = 0) -> any:
    params = {}
    if key != "":
        params.update({"key": key})
    if value != "":
        params.update({"value": value})
    resp = requests.get(f"http://{host}:{port}/{db}/{method}", params=params)
    try:
        result = resp.json()
    except requests.JSONDecodeError as err:
        raise JSONDecodeError(f"send() - invalid result: {err}")
    else:
        return result

class JSONDecodeError(Exception):
    def __init__(self, message):
        self.message = message