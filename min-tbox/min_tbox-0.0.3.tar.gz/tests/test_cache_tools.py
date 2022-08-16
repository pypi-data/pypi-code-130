#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
  @Author: zhangzongliang
  @Date: 2022-08-09 15:33:43
  @Description:
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-16 17:43:49
"""
import time
from datetime import datetime
from turtle import pd
import redis
import pytest
from min_tbox import ex_cache

@pytest.fixture(scope="session")
def rds_client():
    rds_params = {
        "host": '127.0.0.1',
        "port": 6379,
        "db": 0,
        "password": None,
    }
    rds = redis.StrictRedis(
        **rds_params,
        socket_timeout=5,
        socket_connect_timeout=5,
        decode_responses=True,
    )
    return rds

def test_cache(rds_client):
    
    class csr:

        num = 0

        @classmethod
        @ex_cache(rds_client, delay=5)
        def add_sum(self, a, b, c=1):
            self.num += 1
            print("calculate time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return a + b + c

    for _ in range(30):
        time.sleep(1)
        print(csr.add_sum(1, 2))
    assert csr.num <= 6 and  csr.num > 0
