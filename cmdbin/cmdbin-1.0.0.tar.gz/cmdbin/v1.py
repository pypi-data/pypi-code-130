import requests
from requests import Response

from cmdbin import __clean_endpoint


def new(data: str, raw: bool = False, endpoint: str = "https://cmdbin.cc/") -> (int, str):
    response: Response = requests.post(__clean_endpoint(endpoint) + "v1/new",
                                       headers={"Content-Type": "text/plain"},
                                       data=data)
    return response.status_code, response.text


def new_slugonly(data: str, raw: bool = False, endpoint: str = "https://cmdbin.cc/v1/new-slugonly") -> (int, str):
    response: Response = requests.post(__clean_endpoint(endpoint) + "v1/new-slugonly",
                                       headers={"Content-Type": "text/plain"},
                                       data=data)
    return response.status_code, response.text
