# -*- coding: utf-8 -*-
# @Author: Noaghzil
# @Date:   2022-08-15 10:38:25
# @Last Modified by:   Noaghzil
# @Description: 封装http请求
# @Last Modified time: 2022-08-15 15:30:21
from email import header
import json
import logging
import time

import aiohttp
from aiohttp import ClientResponse

logger = logging.getLogger(__name__)


def _try_to_json(data) -> str:
    try:
        return json.dumps(data)[:2000]
    except:
        return str(data)[:2000]


class Http:

    def __init__(self, timeout=10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def request(self, url, method, headers=None, data=None, content_type='json'):
        """
            网络请求
            :param url: 地址
            :param method: http方法
            :param data: 参数
            :param content_type: 返回类型
            :return: 结果
        """
        data = data or {}
        headers = headers or {"Content-Type": "application/json"}
        result = {}
        start = time.time()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info("Http.%s time: [%s], request to [%s] with data [%s]" % (method, url, _try_to_json(data), now_time))
        headers = {"Content-Type": "application/json"}
        pms = {"method": method, "url": url, "headers": headers}
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            if headers.get('Content-Type') == 'application/json':
                pms["json"] = data
            else:
                pms["params"] = data
            async with session.request(**pms) as response:
                result = await self.get_result(response, content_type)
                spend = time.time() - start
                if spend > 3:
                    logger.warning("Http.%s time: [%s], response is success but slow, spend: [%s]" %
                                   (method, now_time, spend))
                else:
                    logger.info("Http.%s time: [%s]" % (method, spend))
        return result

    async def get(self, url, data=None, headers=None, content_type='json') -> dict:
        """
            Http get方法
            :param url: 地址
            :param data: 参数
            :param content_type: 返回类型
            :return: 结果
        """
        result = await self.request(url, 'GET', headers, data, content_type)
        return result

    async def post(self, url, data=None, headers=None, content_type='json') -> dict:
        """
            Http post方法
            :param url: 地址
            :param data: 参数
            :param content_type: 返回类型
            :return: 结果
        """
        result = await self.request(url, 'POST', headers, data, content_type)
        return result

    async def get_result(self, response: ClientResponse, content_type='json'):
        """
            获取返回结果
            :param response: 响应
            :param content_type: 返回类型
            :return: 结果
        """
        result = {}
        try:
            if content_type == 'json':
                result = await response.json(content_type=None)
            else:
                result = await response.read()
            logger.info("Http.get_result is [%s]", _try_to_json(result))
        except json.decoder.JSONDecodeError as e:
            r = await response.read()
            logger.exception("Error while Http.get_result is [%s], return [%s]", e, _try_to_json(r))
            raise ValueError("Error while Http.get_result is [%s], return [%s]", e, _try_to_json(r))
        return result
