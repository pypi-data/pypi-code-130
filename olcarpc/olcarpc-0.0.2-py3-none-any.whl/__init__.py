import google.protobuf.json_format as jf

from .generated import *

__pdoc__ = {
    'olca_pb2': False,
    'services_pb2': False,
    'services_pb2_grpc': False,
}


def to_json(entity, indent: int = 2) -> str:
    return jf.MessageToJson(entity, indent=indent)


class Client:

    def __init__(self, port=8080):
        self.__port = port
        self.__channel = grpc.insecure_channel(
            'localhost:%i' % port, options=[
                ('grpc.max_send_message_length', 1024 * 1024 * 1024),
                ('grpc.max_receive_message_length', 1024 * 1024 * 1024),
            ])
        self.fetch = DataFetchServiceStub(self.__channel)
        self.update = DataUpdateServiceStub(self.__channel)
        self.flow_maps = FlowMapServiceStub(self.__channel)
        self.results = ResultServiceStub(self.__channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.__channel is not None:
            self.__channel.close()
            self.__channel = None
