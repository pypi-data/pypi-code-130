from typing import Dict, Any

import requests

from utils.ErrorUtils import print_error


def do_post(url: str, body: Dict[str, Any] = None, header: Dict[str, Any] = None) -> Dict[str, Any]:
    response = requests.post(url, json=body, headers=header)
    if response.status_code != 200:
        print_error("do_post failed!", url=url, status_code=response.status_code, result=response.json())
    return response.json()


def do_get(url: str, params: Dict[str, Any] = None, header: Dict[str, Any] = None) -> Dict[str, Any]:
    response = requests.get(url, params=params, headers=header)
    if response.status_code != 200:
        print_error("do_get failed!", url=url, status_code=response.status_code, result=response.json())
    return response.json()


def do_put(url: str, body: Dict[str, Any] = None, header: Dict[str, Any] = None) -> Dict[str, Any]:
    response = requests.put(url, json=body, headers=header)
    if response.status_code != 200:
        print_error("do_put failed!", url=url, status_code=response.status_code, result=response.json())
    return response.json()


def do_delete(url: str, header: Dict[str, Any] = None) -> Dict[str, Any]:
    response = requests.delete(url, headers=header)
    if response.status_code != 200:
        print_error("do_delete failed!", url=url, status_code=response.status_code, result=response.json())
    return response.json()
