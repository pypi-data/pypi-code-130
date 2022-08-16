# -*- coding: utf-8 -*-
# @Author: Noaghzil
# @Date:   2022-08-15 11:12:05
# @Last Modified by:   Noaghzil
# @Last Modified time: 2022-08-16 17:43:57
import pytest
from min_tbox.api import Http


@pytest.fixture(scope="session")
def client():
    return Http()


@pytest.mark.asyncio
async def test_http_get(client: Http):
    """
     Http get方法,  测试用例
    """
    url_path = "https://xxx.com/soi/polling?chat_id=17654642284957696&uid=200&user_type=1&action=get_msgs"
    result = await client.get(url_path)
    assert result['code'] == "200"
    assert result['status'] == 0
    assert len(result['update_details']) == 1
    assert 1 == 1


@pytest.mark.asyncio
async def test_http_post(client: Http):
    """
     Http post方法, 测试用例
    """
    url_path = "https://xxx.com/chat_api/member/chat_label"
    params = {
        "chat_id": 96,
        "app_id": "5fa769c142e6df8c6a36b3d3",
        "uid": "123",
        "user_type": 1,
        "chat_label": "docker交流群"
    }
    result = await client.post(url_path, data=params)
    assert result['status'] == 0
