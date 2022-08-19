#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : service
# @Time         : 2022/8/19 下午5:14
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


import grpc
from appzoo.grpc_app.base_pb2 import Request, Response
from appzoo.grpc_app.base_pb2_grpc import GrpcServiceServicer, GrpcServiceStub, add_GrpcServiceServicer_to_server

from meutils.pipe import *


class Service(GrpcServiceServicer):

    def __init__(self, debug=False):
        self.debug = debug

    def main(self, *args, **kwargs):
        raise NotImplementedError

    @logger.catch()
    def _request(self, request, context):
        if self.debug:
            logger.debug(request.data)
        return Response(data=self.main(request.data))

    def run(self, port=8000, max_workers=3):

        server = grpc.server(ThreadPoolExecutor(max_workers))  # compression = None
        add_GrpcServiceServicer_to_server(self, server)

        server.add_insecure_port(f'[::]:{port}')
        server.start()
        logger.info("GrpcService Running ...")
        try:
            while 1:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    class MyService(Service):

        def main(self, data: list) -> list:
            return data


    MyService(debug=True).run()
