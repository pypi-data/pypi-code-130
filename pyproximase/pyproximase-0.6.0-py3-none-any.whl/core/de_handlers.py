import requests
import grpc
import orjson as json

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.message import Message

from .types import ProximaSeException
from .types import ProximaSeStatus
from .types import CollectionInfo
from .types import CollectionStats
from .types import QueryResponse
from .types import Document
from .types import _TimerStage
from .types import _Timer
from .types import _build_collection_name
from .de_types import NodeStatus
from .de_types import ResourceGroupConfig 
from .de_types import Placement 
from .de_types import ResourceGroupPlacement 
from .de_types import ResourceGroupStatus
from .de_types import ResourceGroupStatus
from .de_types import ResourceGroupInfo
from .de_types import ClusterStatusResponse 
from .de_types import DescribeResourceGroupResponse
from .de_types import DropResourceGroupRequest 

import proto.common_pb2 as common_pb2
import proto.proxima_se_pb2 as proxima_se_pb2
import proto.proxima_se_pb2_grpc as proxima_se_pb2_grpc
import proto.admin_pb2 as admin_pb2
import proto.admin_pb2_grpc as admin_pb2_grpc
import proto.frontend_pb2 as frontend_pb2
import proto.frontend_pb2_grpc as frontend_pb2_grpc

from .handlers import HttpHandler
from .handlers import GrpcHandler
from .handlers import AsyncGrpcHandler

def parse_resource_group_lists(status, list_response):
    if not status.ok():
        return status, [], []
    return status, [
        ResourceGroupInfo.from_pb(c) for c in list_response.resource_group_info
    ], [
        NodeStatus.from_pb(c) for c in list_response.fe_node_status
    ]

class DeHttpHandler(HttpHandler):
    _MANAGE_RESOURCE_GROUP_URL = "/v1/resource_group/"
    _STATS_CLUSTER_URL = "/v1/cluster_status"

    def __init__(self, host, port, timeout):
        super().__init__(host, port, timeout)

    def create_resource_group(self, resource_group_config):
        rsp = self._send_request(self._MANAGE_RESOURCE_GROUP_URL +
                                 resource_group_config.name,
                                 resource_group_config)
        return self._parse_status(rsp)

    def drop_resource_group(self, drop_resource_group_request):
        rsp = self._send_request(self._MANAGE_RESOURCE_GROUP_URL +
                                 drop_resource_group_request.resource_group_name,
                                 body=drop_resource_group_request,
                                 method='DELETE')
        return self._parse_status(rsp)

    def describe_resource_group(self, resource_group_name):
        rsp = self._send_request(self._MANAGE_RESOURCE_GROUP_URL +
                                 resource_group_name,
                                 method='GET')
        return self._parse_response(
            rsp, ResourceGroupInfo, 'resource_group',
            admin_pb2.DescribeResourceGroupResponse())

    def update_resource_group(self, ru_request):
        rsp = self._send_request(self._MANAGE_RESOURCE_GROUP_URL +
                                 ru_request.resource_group_name,
                                 body=ru_request,
                                 method='PUT')
        return self._parse_status(rsp)


    def cluster_status(self, cluster_status_request):
        url = self._STATS_CLUSTER_URL
        if cluster_status_request.token != "":
            url = url + "?token=" + cluster_status_request.token 
        rsp = self._send_request(url,
                                 body=cluster_status_request,
                                 method='GET')
        pb_rsp = self._parse_response(rsp,message=admin_pb2.ClusterStatusResponse())
        return parse_resource_group_lists(*pb_rsp)
         

class DeGrpcHandler(GrpcHandler):
    def __init__(self, host, port, timeout):
        super().__init__(host, port, timeout)
        self._frontend_stub = frontend_pb2_grpc.FrontendServiceStub(self._channel)

    def create_resource_group(self, resource_group_config):
        rsp = self._frontend_stub.create_resource_group(resource_group_config, timeout=self._timeout)
        return self._parse_status(rsp)

    def update_resource_group(self, update_resource_group_request):
        rsp = self._frontend_stub.create_resource_group(update_resource_group_request, timeout=self._timeout)
        return self._parse_status(rsp)

    def drop_resource_group(self, drop_resource_group_request):
        rsp = self._frontend_stub.drop_resource_group(drop_resource_group_request, timeout=self._timeout)
        return self._parse_status(rsp)

    def describe_resource_group(self, resource_group_name):
        rsp = self._frontend_stub.describe_resource_group(
            _build_collection_name(resource_group_name), timeout=self._timeout)
        return self._parse_response(rsp, ResourceGroupInfo, 'resource_group')

    def cluster_status(self, cluster_status_request):
        rsp = self._frontend_stub.cluster_status(cluster_status_request, timeout=self._timeout)
        status, rsp = self._parse_response(rsp)
        return parse_resource_group_lists(status, rsp)


class DeAsyncGrpcHandler(AsyncGrpcHandler):
    def __init__(self, host, port, timeout):
        super().__init__(host, port, timeout)
        self._frontend_stub = frontend_pb2_grpc.FrontendServiceStub(self._channel)

    async def create_resource_group(self, resource_group_config):
        rsp = await self._frontend_stub.create_resource_group(resource_group_config, timeout=self._timeout)
        return self._parse_status(rsp)

    async def update_resource_group(self, update_resource_group_request):
        rsp = self._frontend_stub.create_resource_group(update_resource_group_request, timeout=self._timeout)
        return self._parse_status(rsp)

    async def drop_resource_group(self, drop_resource_group_request):
        rsp = await self._frontend_stub.drop_resource_group(drop_resource_group_request, timeout=self._timeout)
        return self._parse_status(rsp)

    async def describe_resource_group(self, resource_group_name):
        rsp = await self._frontend_stub.describe_resource_group(
            _build_collection_name(resource_group_name), timeout=self._timeout)
        return self._parse_response(rsp, ResourceGroupInfo, 'resource_group')

    async def cluster_status(self, cluster_status_request):
        rsp = await self._frontend_stub.cluster_status(cluster_status_request, timeout=self._timeout)
        status, rsp = self._parse_response(rsp)
        return parse_resource_group_lists(status, rsp)


