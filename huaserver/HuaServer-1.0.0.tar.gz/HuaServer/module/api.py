# coding:utf-8


class Api(object):
    __HANDLERS = dict()

    @classmethod
    def bind(cls, api_name, api_func):
        cls.__HANDLERS[api_name] = api_func

    @classmethod
    def do(cls, uri, body):
        func = cls.__HANDLERS.get(uri)
        return func(body)

    @classmethod
    def is_exist(cls, uri):
        return uri in cls.__HANDLERS
