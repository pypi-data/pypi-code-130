#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sessions.py
@Time    :   2022/08/16 17:10:08
@Author  :   nicholas wu 
@Version :   v1.0
@Contact :   nicholas_wu@aliyun.com
'''
from requests import Session, adapters

class TritonClientStub(Session):
    def __init__(self, pool_connections, pool_maxsize, max_retries=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adapter = adapters.HTTPAdapter(
            pool_connections = pool_connections,
            pool_maxsize = pool_maxsize,
            max_retries = max_retries
        )
        self.mount("http://", adapter=adapter)
        self.mount("https://", adapter=adapter)
