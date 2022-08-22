import argparse
import json
import signal
import traceback
import uuid
from typing import Callable

import grpc
import structlog
from google.protobuf.struct_pb2 import Struct
from structlog.types import FilteringBoundLogger

from . import kubefox_pb2 as kf
from . import kubefox_pb2_grpc as kf_rpc

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(key="ts"),
        structlog.processors.EventRenamer(to="msg"),
        structlog.processors.JSONRenderer(),
    ]
)


class KubeFox:

    entrypoint: Callable = None
    broker: kf_rpc.ComponentServiceStub = None
    sub_id: str = None
    log: FilteringBoundLogger = structlog.get_logger()

    def entrypoint(self, func: Callable):
        self.entrypoint = func
        return func

    def start(self) -> None:
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

        parser = argparse.ArgumentParser()

        # Adding optional argument
        parser.add_argument(
            "-b",
            "--broker-grpc-addr",
            default="localhost:7070",
            help="address and port of the broker's gRPC server, default localhost:7070",
        )

        args = parser.parse_args()

        service_config_json = json.dumps(
            {
                "methodConfig": [
                    {
                        "name": [{}],
                        "retryPolicy": {
                            "maxAttempts": 5,
                            "initialBackoff": "0.25s",
                            "maxBackoff": "2s",
                            "backoffMultiplier": 2,
                            "retryableStatusCodes": ["UNAVAILABLE"],
                        },
                    }
                ]
            }
        )
        options = []
        options.append(("grpc.enable_retries", 1))
        options.append(("grpc.service_config", service_config_json))

        with grpc.insecure_channel(args.broker_grpc_addr, options=options) as channel:
            self.broker = kf_rpc.ComponentServiceStub(channel)
            try:
                conf = self.broker.GetConfig(kf.ConfigRequest())
                self.log = self.log.bind(
                    componentId=conf.component.id,
                    componentHash=conf.component.hash,
                    componentName=conf.component.name,
                )

                self.sub_id = str(uuid.uuid4())
                self.log.info(f"subscribing to broker at {args.broker_grpc_addr}, subscription={self.sub_id}")

                self._run(self.broker, self.sub_id)
            except BaseException as e:
                self._stop()
                raise e

    def _run(self, broker: kf_rpc.ComponentServiceStub, sub_id: str) -> None:
        for request in broker.Subscribe(kf.SubscribeRequest(id=sub_id)):
            try:
                kit = Kit(request, broker, self.log)
                self.entrypoint(kit)
                broker.SendResponse(kf.Response(parent_id=request.metadata.id, data=kit.response))
            except Exception as e:
                print(e)
                traceback.print_exc()

    def _stop(self, sig=None, frame=None):
        if self.broker != None:
            self.log.info(f"unsubscribing from broker, subscription={self.sub_id}")
            self.broker.Unsubscribe(kf.SubscribeRequest(id=self.sub_id))
        exit()


class Kit:

    request: kf.Data = None
    response: kf.Data = kf.Data()
    broker: kf_rpc.ComponentServiceStub = None
    log: FilteringBoundLogger = None

    def __init__(self, request: kf.Data, broker: kf_rpc.ComponentServiceStub, log: FilteringBoundLogger) -> None:
        self.request = request
        self.broker = broker
        self.log = log.bind(traceId=request.metadata.span.trace_id)

    def value(self, key: str) -> str:
        return self.request.values.fields[key].string_value

    def component(self, name: str):
        return Component(name, self)


class Component:

    _name: str = None
    _kit: Kit = None

    def __init__(self, name: str, kit: Kit) -> None:
        self._name = name
        self._kit = kit

    def invoke(self, args: dict = None, content_type: str = None, content: bytes = None) -> kf.Data:
        argsStruct = Struct()
        argsStruct.update(args)

        data = kf.Data(
            args=argsStruct,
            content_type=content_type,
            content=content,
        )

        return self._kit.broker.InvokeRemoteComponent(
            kf.Request(
                target=self._name,
                parent_id=self._kit.request.metadata.id,
                system_tag=self._kit.request.metadata.system_tag,
                environment=self._kit.request.metadata.environment,
                span=self._kit.request.metadata.span,
                data=data,
            )
        )
