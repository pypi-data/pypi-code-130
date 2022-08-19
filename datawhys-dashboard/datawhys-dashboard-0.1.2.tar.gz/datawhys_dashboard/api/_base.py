import json
import platform

import requests

import datawhys_dashboard as dwdash


def request(
    method: str,
    url: str,
    key: str = None,
    api_base: str = None,
    headers: dict = None,
    data: dict = None,
    **kwargs
):
    """
    Send an API request.
    """
    api_base = api_base or dwdash.api_base
    api_key = key or dwdash.api_key
    rheaders = _request_headers(api_v02_key=api_key)

    # merge headers into request headers
    if headers is not None:
        for key, value in headers.items():
            rheaders[key] = value

    # remove any None values
    rheaders = {k: v for k, v in rheaders.items() if v is not None}
    data = (
        {k: v for k, v in data.items() if v is not None} if data is not None else None
    )

    res = requests.request(
        method, api_base + url, headers=rheaders, data=data, **kwargs
    )
    return res.json()


def request_v01(
    method: str,
    url: str,
    key: str = None,
    api_base: str = None,
    headers: dict = None,
    data: dict = None,
    **kwargs
):
    """
    Send an API request.
    """
    api_base = api_base or dwdash.api_v01_base
    api_key = key or dwdash.api_v01_key
    rheaders = _request_headers(api_v01_key=api_key)

    # merge headers into request headers
    if headers is not None:
        for key, value in headers.items():
            rheaders[key] = value

    # remove any None values
    rheaders = {k: v for k, v in rheaders.items() if v is not None}
    data = (
        {k: v for k, v in data.items() if v is not None} if data is not None else None
    )

    res = requests.request(
        method, api_base + url, headers=rheaders, data=data, **kwargs
    )
    return res.json()


def _request_headers(api_v01_key: str = None, api_v02_key: str = None):
    """
    Get the base headers for an API request.
    """
    user_agent = "DataWhys/v1 DashboardSDK/%s" % (dwdash.__version__,)

    ua = {
        "bindings_version": dwdash.__version__,
        "lang": "python",
        "publisher": "datawhys",
        "httplib": "requests",
        "lang_version": platform.python_version(),
        "platform": platform.platform(),
        "uname": " ".join(platform.uname()),
    }

    headers = {
        "X-DataWhys-Client-User-Agent": json.dumps(ua),
        "User-Agent": user_agent,
        "Content-Type": "application/json",
    }

    if api_v01_key:
        headers["Authorization"] = "Token " + api_v01_key

    if api_v02_key:
        headers["X-API-Token"] = api_v02_key

    return headers
