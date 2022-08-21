# coding:utf-8

import HuaServer.module.api
import json
import sys
import time
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    def __do(self, uri):
        body = self.request.body
        body = json.loads(body) if body else None
        res = HuaServer.module.api.Api.do(uri, body)
        return res

    def post(self):
        uri = self.request.uri
        if HuaServer.module.api.Api.is_exist(uri):
            code = 200
            message = "[HuaServer] 请求成功"
            data = self.__do(uri)
        else:
            code = 404
            message = "[HuaServer] api不存在"
            data = None
        res = dict(code=code, message=message, data=data)
        self.set_status(code, message)
        self.finish(res)


class Server(object):
    __app = tornado.web.Application([(r"/.*", MainHandler)])

    @classmethod
    def __listen(cls, port):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cls.__app.listen(port)
            print(f"[{now}] [Hua Server] 服务启动成功，端口号：{port}")
        except OSError:
            print(f"[{now}] [Hua Server] 服务启动失败，端口号{port}被占用")
            sys.exit(0)

    @classmethod
    def run(cls, port=6316):
        cls.__listen(port)
        tornado.ioloop.IOLoop.current().start()
