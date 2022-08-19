#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : client
# @Time         : 2022/8/19 下午5:15
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


import grpc
from appzoo.grpc_app.base_pb2 import Request, Response
from appzoo.grpc_app.base_pb2_grpc import GrpcServiceServicer, GrpcServiceStub, add_GrpcServiceServicer_to_server


class Client:

    def __init__(self, ip='0.0.0.0', port=8000):
        self.conn = grpc.insecure_channel(f"{ip}:{port}")
        self._client = GrpcServiceStub(channel=self.conn)

    def request(self, data):
        request = Request(data=data)
        response = self._client._request(request)
        return response.data


if __name__ == '__main__':
    client = Client()
    print(client.request(['1, 2, 3, 4', 'as']))
