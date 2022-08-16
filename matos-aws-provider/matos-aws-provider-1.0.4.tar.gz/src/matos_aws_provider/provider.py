import threading
from typing import List, Any
import logging
from matos_aws_provider.lib.auth import Connection
from matos_aws_provider.plugins import get_package
from matos_aws_provider.lib import factory, loader

logger = logging.getLogger(__name__)


class Provider(Connection):
    """ Aws provider factory class

    Args:
        Connection (Connection): Aws connection class
    """

    def __init__(self, **kwargs) -> None:
        """
        Class constructor method
        """
        super().__init__(**kwargs)
        loader.load_plugins(get_package())
        self.service_factory = factory

    def get_assets(self, **kwargs):
        """
        Discover aws resources
        """
        threads = []
        resources = [{"type": "iam"}]
        lock = threading.Lock()

        def fetch_discovery_details(rsc_type):
            service_discovery = self.service_factory.create({"type": rsc_type})
            result = service_discovery.get_inventory()

            if result is None:
                return

            with lock:
                if isinstance(result, list):
                    resources.extend(service_discovery.get_inventory())
                else:
                    resources.append(service_discovery.get_inventory())

        service_map = self.service_factory.fetch_plugins()
        for rsc_type, _ in service_map.items():
            thread = threading.Thread(target=fetch_discovery_details, args=(rsc_type,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return resources

    def get_resource_inventories(self, resource_list: List[Any]):
        """
        Get resources data
        """
        resource_inventories = {}
        lock = threading.Lock()

        def fetch_resource_details(rsc):
            resource_type = rsc.get('type')
            try:
                detail = self._get_assets_inventory(rsc)
                with lock:
                    resource_inventories[resource_type] = [detail] if resource_type not in resource_inventories \
                        else [*resource_inventories[resource_type], detail]
            except Exception as e:
                logger.error(f"{e}")

        threads = []
        for resource in resource_list:
            thread = threading.Thread(target=fetch_resource_details, args=(resource,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        return resource_inventories

    def _get_assets_inventory(self, resource, **kwargs):
        cloud_resource = self.service_factory.create(resource)
        resource_details = cloud_resource.get_resources()
        if resource_details:
            resource.update(details=resource_details)
        return resource
