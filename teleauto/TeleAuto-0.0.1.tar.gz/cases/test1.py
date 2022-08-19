#!/usr/bin/python
#_*_encoding:utf-8_*_

import requests
import glo

def test_passing():
    res = requests.get(glo.get_value("ep") + "/api/pipeline/list?page_num=1&page_size=10")
    print("\n----------------")
    print(res.json()["msg"])
    assert res.json()["page_info"]["total"] == 7