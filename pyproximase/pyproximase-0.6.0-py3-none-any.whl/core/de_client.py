import abc

from .types import ProximaSeException
from .types import _build_get_document_request
from .types import _build_list_condition
from .types import WriteRequest
from .types import _check_version
from .types import _Timer
from .types import _TimerStage

from .handlers import HttpHandler
from .handlers import GrpcHandler
from .handlers import AsyncGrpcHandler
from .de_handlers import DeHttpHandler 
from .de_handlers import DeGrpcHandler 
from .de_handlers import DeAsyncGrpcHandler 
from .client import BaseClient


class DeBaseClient(BaseClient):
    """
    BaseClient.
    """

    @abc.abstractmethod
    def __init__(self, handler, de_handler):
        super().__init__(handler)
        self._de_handler = de_handler 

    def create_resource_group(self, resource_group_config):
        """
        Create resource group.

        Args:
            resource_group_config(ResourceGroupConfig): resource group config.

        Returns:
            ProximaSeStatus: status
        """
        return self._de_handler.create_resource_group(resource_group_config.to_pb())

    def describe_resource_group(self, resource_group_name):
        """
        Describe resource group.

        Args:
            resource_group_name(str):  resource group name

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * :class:`ResourceGroupInfo`: resource group information
        """
        return self._de_handler.describe_resource_group(resource_group_name)

    def update_resource_group(self, update_resource_group_request):
        """
        Describe resource group.

        Args:
            update_resource_group_request(UpdateResourceGroupRequest):  
                update resource group request 

        Returns:
            ProximaSeStatus: status
        """
        return self._de_handler.update_resource_group(update_resource_group_request.to_pb())


    def drop_resource_group(self, drop_resource_group_request):
        """
        Drop resource group.

        Args:
            drop_resource_group_request(DropResourceGroupRequest): 
                drop resource_group request 

        Returns:
            ProximaSeStatus: status
        """
        return self._de_handler.drop_resource_group(drop_resource_group_request.to_pb())

    def cluster_status(self, cluster_status_request):
        """
        Stats collection.

        Args:
            cluster_status_request(ClusterStatusRequest): request cluster status 

        Returns:
            tuple: 3-element tuple containing
              * :class:`ProximaSeStatus`: status
              * List[:class:`ResourceGroupInfo`]: resource group info list
              * List[:class:`NodeStatus`]: frontend node status list
        """
        return self._de_handler.cluster_status(cluster_status_request.to_pb())


class DeClient(DeBaseClient):
    def __init__(self, host, port=16000, handler='grpc', timeout=10):
        """
        Constructor.

        Args:
            host (str): hostname
            port (int): port
            handler (str): use grpc or http, defaults to grpc.
            de_handler (str): use grpc or http, defaults to grpc.
            timeout (Optional[float]): timeout in seconds, default to 10. Passing None means no timeout.
        """
        if handler.lower() == 'http':
            handler = HttpHandler(host, port, timeout)
            de_handler = DeHttpHandler(host, port, timeout)
        elif handler.lower() == 'grpc':
            handler = GrpcHandler(host, port, timeout)
            de_handler = DeGrpcHandler(host, port, timeout)
        else:
            raise ProximaSeException(f"Invalid handler type[{handler}]")
        super().__init__(handler, de_handler)


class DeAsyncClient(DeBaseClient):
    def __init__(self, host, port=16000, handler='grpc', timeout=10):
        """
        Constructor.

        Args:
            host (str): hostname
            port (int): port
            handler (str): only grpc is supported for now.
            timeout (Optional[float]): timeout in seconds, default to 10. Passing None means no timeout.
        """
        if handler.lower() != 'grpc':
            raise ProximaSeException("AsyncClient only support grpc")
        super().__init__(AsyncGrpcHandler(host, port, timeout), DeAsyncGrpcHandler(host, port, timeout))
