# -*- coding: utf-8 -*- 
# Time: 2022-03-01 11:00
# Copyright (c) 2022
# author: Euraxluo


import random
import asyncio
import aiohttp
import warnings
from concurrent import futures
from amap_distance_matrix.helper import *
from amap_distance_matrix.services.register import register

"""
高德地图webapi接口服务包装
"""


###############geo################

async def async_request_geo(url: str) -> list:
    """
    通过url进行司机的寻址
    :param url: amap geo url
    :return:
    """
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            result = await resp.json()
            if result['status'] == '1' and len(result['geocodes']) > 0:
                if len(result['geocodes'][0]['location']) > 0:
                    return format_loc(result['geocodes'][0]['location'])
        return []


def request_geo(url: str) -> list:
    """
    通过url进行司机的寻址
    :param url: amap geo url
    :return:
    """
    result = register.session().get(url).json()
    if result['status'] == '1' and len(result['geocodes']) > 0:
        if len(result['geocodes'][0]['location']) > 0:
            return format_loc(result['geocodes'][0]['location'])
    return []


def geo_url(addr: str, city: str, keys: Union[List[str], str] = None):
    """
    地址寻址服务 url包装
    :param addr: 地址字符串
    :param city: 城市字符串/城市编码(geocode)
    :param keys: 高德地图webApiKeys
    :return:
    """
    if isinstance(keys, list):
        choice_key = random.choice(keys)
    elif isinstance(keys, str):
        choice_key = keys
    elif keys is None and register.keys:
        choice_key = register.keys_balance.next
    else:
        raise KeyError(f"addressing Exception: keys must Union[List[str], str],now is {keys}")
    return "https://restapi.amap.com/v3/geocode/geo?address=%s&city=%s&output=json&key=%s" % (addr, city, choice_key)


async def async_geo(address_city_list: List[Tuple[str, str]]) -> list:
    """
    异步 寻址
    :param address_city_list:
    :return:
    """
    location_list = []
    for idx, (addr, city) in enumerate(address_city_list):
        location = await async_request_geo(geo_url(addr, city))
        location_list.append(location)
    return location_list


def futures_geo(address_city_list: List[Tuple[str, str]]) -> list:
    """
    异步 寻址
    :param address_city_list:
    :return:
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        try:
            event_loop = asyncio.get_event_loop()
        except Exception as _:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            event_loop = asyncio.get_event_loop()

    location_list = []

    tasks: List[futures] = []
    tasks_address = []

    for idx, (addr, city) in enumerate(address_city_list):
        url = geo_url(addr, city)
        task = event_loop.run_in_executor(register.pool, request_geo, url)
        tasks.append(task)
        tasks_address.append((addr, city))

    event_loop.run_until_complete(asyncio.wait(tasks))
    for idx, task in enumerate(tasks):
        location = task.result()
        location_list.append(location)
    return location_list


def geo_addr_city(address_city_list: List[Tuple[str, str]]):
    """
    通过 地址和城市寻址
    :param address_city_list: 地址城市tuple列表  List[Tuple[str, str]]
    :return: 有可能返回空数组
    """
    return futures_geo(address_city_list)


async def async_geo_addr_city(address_city_list: List[Tuple[str, str]]):
    """
    通过 地址和城市寻址
    :param address_city_list: 地址城市tuple列表  List[Tuple[str, str]]
    :return:
    """
    if len(address_city_list) < 10:
        return await async_geo(address_city_list)
    else:
        return futures_geo(address_city_list)
