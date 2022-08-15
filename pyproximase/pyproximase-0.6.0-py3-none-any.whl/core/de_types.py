import struct
from enum import Enum
from enum import IntEnum
import base64

import time
from ..proto import common_pb2
from ..proto import proxima_se_pb2
from ..proto import proxima_se_pb2_grpc  # NOQA
from ..proto import admin_pb2
from ..proto import frontend_pb2

from .types import ProximaSeStatus
from .types import _Printable 

from ..version import __version__



class NodeStatus(_Printable):
    """
    NodeStatus

    Attributes:
        host (str): host of node
        last_heartbeat_ts (long): last_heartbeat_ts of node 
        status  (str): status of node 
    """

    def __init__(self, host, last_heartbeat_ts, status):
        """
        Constructor

        Args:
            host (str): Host name.
            last_heartbeat_ts(long): Last_heartbeat_ts  of node.
            status(str): Status of node.
        """

        self.host = host 
        self.last_heartbeat_ts  = last_heartbeat_ts 
        self.status = status 

    def to_pb(self):
        """Return corresponding protobuf message."""
        node_status = admin_pb2.NodeStatus()
        node_status.host = self.host
        node_status.last_heartbeat_ts = self.last_heartbeat_ts
        node_status.status = self.status
        return node_status 

    @staticmethod
    def from_pb(pb_node_status):
        """Parse from corresponding protobuf type."""
        return  NodeStatus(pb_node_status.host, pb_node_status.last_heartbeat_ts,
                                pb_node_status.status)



class ResourceGroupConfig(_Printable):
    """
    NodeStatus

    Attributes:
        name(str): name of resource group 
        sharding_count(int32): sharding_count of resource group 
        replica_count(int32): replica count of resource group
        cpu_request(float): cpu_request of resource group
        memory_request(float): memory_request of resource group (in MB) 
        disk_request(float): disk_request of resource group (in GB) 
    """

    def __init__(self, name, sharding_count, replica_count, cpu_request, memory_request, disk_request):
        """
        Constructor

        Args:
            name(str): name of resource group 
            sharding_count(int32): sharding_count of resource group 
            replica_count(int32): replica count of resource group
            cpu_request(float): cpu_request of resource group
            memory_request(float): memory_request of resource group (in MB) 
            disk_request(float): disk_request of resource group (in GB) 
        """
        self.name = name 
        self.sharding_count = sharding_count
        self.replica_count = replica_count
        self.cpu_request = cpu_request 
        self.memory_request = memory_request 
        self.disk_request = disk_request 

    def to_pb(self):
        """Return corresponding protobuf message."""
        resource_group_config = admin_pb2.ResourceGroupConfig()
        resource_group_config.name = self.name
        resource_group_config.sharding_count = self.sharding_count
        resource_group_config.replica_count = self.replica_count
        resource_group_config.cpu_request  = self.cpu_request
        resource_group_config.memory_request = self.memory_request
        resource_group_config.disk_request = self.disk_request
        return resource_group_config 

    @staticmethod
    def from_pb(pb_resource_group_config):
        """Parse from corresponding protobuf type."""
        return  ResourceGroupConfig(pb_resource_group_config.name, pb_resource_group_config.sharding_count,
                                    pb_resource_group_config.replica_count,
                                    pb_resource_group_config.cpu_request, pb_resource_group_config.memory_request,
                                    pb_resource_group_config.disk_request)

class Placement(_Printable):
    """
    Placement 

    Attributes:
        se_shardings (List[Sharding]): se_shardings info array list 
        repository_endpoint(str): endpoiont of repository 
    """
    class Replica(_Printable):
        """
        Replica.

        Attributes:
            endpoint (str): replica endpoint 
        """

        def __init__(self, endpoiont):
            """
            Constructor.

            Args:
                endpoint (str): replica endpoint 
            """
            self.endpoiont = endpoiont 

    class Sharding(_Printable):
        """
        Sharding.

        Attributes:
            sharding_id(int32): sharding_id 
            replicas(List[Replica]): replica info array list 
        """

        def __init__(self, sharding_id, replicas):
            """
            Constructor.

            Args:
                sharding_id(int32): sharding_id 
                replicas(List[Replica]): replica info array list 
            """
            self.sharding_id = sharding_id 
            self.replicas = replicas 

    def __init__(self, se_shardings, repository_endpoint):
        """
        Constructor

        Args:
            se_shardings (List[Sharding]): se_shardings info array list 
            repository_endpoint(str): endpoiont of repository 
        """
        self.se_shardings = se_shardings 
        self.repository_endpoint = repository_endpoint 

class ResourceGroupPlacement(_Printable):
    """
    ResourceGroupPlacement 

    Attributes:
        resource_group_name(str): name of resourece group 
        placement(Placement]): Placement Info of resource group 
        collection_names(List[str]): collection names  array list of resource group 
    """
    def __init__(self, resourece_group_name, placement, collection_names):

        self.resource_group_name = se_shardings 
        self.placement = placement 
        self.collection_names = collection_names 

class ResourceGroupStatus(_Printable):
    """
    ResourceGroupStatus

    Attributes:
        resource_group_placement(ResourceGroupPlacement): ResourceGroupPlacement of resource group 
        se_available_count(int32) : se_available_count of resource group
        repo_available_count(int32) : repository available count of resourece group
        se_available_hosts(List[str]): se available hosts
        se_failed_hosts(List[str]): se failed hosts
        update_ts(long) : update time stamp of resource group
    """
    def __init__(self, resource_group_placement, se_available_count, repo_available_count,
                 se_available_hosts, se_failed_hosts, update_ts):

        self.resource_group_placement = resource_group_placement 
        self.se_available_count = se_available_count 
        self.repo_available_count = repo_available_count
        self.se_available_hosts = se_available_hosts
        self.se_failed_hosts = se_failed_hosts
        self.update_ts = update_ts 

class ResourceGroupInfo(_Printable):
    """
    ResourceGroupInfo

    Attributes:
        config(ResourceGroupConfig): config  of resource group 
        status(ResourceGroupStatus): status of resource group 
    """
    def __init__(self, config, status):

        self.config = config 
        self.status = status 

    def to_pb(self):
        """Return corresponding protobuf message."""
        resource_group_info = admin_pb2.ResourceGroupInfo()
        resource_group_info.config = self.config
        resource_group_info.status = self.status
        return resource_group_info

    @staticmethod
    def from_pb(pb_resource_group_info):
        """Parse from corresponding protobuf type."""
        return  ResourceGroupInfo(pb_resource_group_info.config, pb_resource_group_info.status)


class ClusterStatusRequest(_Printable):
    """
    ClusterStatusRequest

    Attributes:
        token(str): token of cluster 
    """
    def __init__(self, token):
        self.token = token 

    def to_pb(self):
        """Return corresponding protobuf message."""
        cluster_status_request = admin_pb2.ClusterStatusRequest()
        cluster_status_request.token = self.token
        return cluster_status_request

    @staticmethod
    def from_pb(pb_cluster_status_request):
        """Parse from corresponding protobuf type."""
        return  ClusterStatusRequest(pb_cluster_status_request.token)

class UpdateResourceGroupRequest(_Printable):
    """
    UpdateResourceGroupRequest 

    Attributes:
        resource_group_name(str): name of resource group 
        sharding_count(int): sharding count of resource group 
    """
    def __init__(self, resource_group_name, sharding_count):
        self.resource_group_name = resource_group_name 
        self.sharding_count = sharding_count 

    def to_pb(self):
        """Return corresponding protobuf message."""
        ru_request = admin_pb2.UpdateResourceGroupRequest()
        ru_request.resource_group_name = self.resource_group_name
        ru_request.sharding_count = self.sharding_count
        return ru_request 

    @staticmethod
    def from_pb(ru_request):
        """Parse from corresponding protobuf type."""
        return  UpdateResourceGroupRequest(ru_request.resource_group_name,
                ru_request.sharding_count)


class ClusterStatusResponse(_Printable):
    """
    ClusterStatusResponse 

    Attributes:
        status(ProximaSeStatus): proximaSE status
        resource_group_info(ResourceGroupInfo): resource group info  
        fe_node_status(NodeStatus) : node status of frontend
    """
    def __init__(self, status, resource_group_info, fe_node_status):

        self.status = status 
        self.resource_group_info = resource_group_info 
        self.fe_node_status = fe_node_status 

class DescribeResourceGroupResponse(_Printable):
    """
    DescribeResourceGroupResponse 

    Attributes:
        status(ProximaSeStatus): proximaSE status
        resource_group(ResourceGroupInfo): resource group info  
    """
    def __init__(self, status, resource_group):

        self.status = status 
        self.resource_group = resource_group

class DropResourceGroupRequest(_Printable):
    """
    DropResourceGroupRequest 

    Attributes:
        resource_group_name(str): name of resource group 
        force_delete(bool): force_delete resource group or not 
    """
    def __init__(self, resource_group_name, force_delete):

        self.resource_group_name = resource_group_name
        self.force_delete = force_delete 

    def to_pb(self):
        """Return corresponding protobuf message."""
        drop_resource_group_request = admin_pb2.DropResourceGroupRequest()
        drop_resource_group_request.resource_group_name = self.resource_group_name
        drop_resource_group_request.force_delete = self.force_delete
        return drop_resource_group_request 


