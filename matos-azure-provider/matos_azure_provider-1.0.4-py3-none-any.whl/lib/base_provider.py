# -*- coding: utf-8 -*-
import logging
from typing import Any
from matos_azure_provider.lib.auth import Connection

logger = logging.getLogger(__name__)


class BaseProvider(Connection):
    """Base provider class

    Args:
        Connection (Object): connection class
    """
    def __init__(self, **kwargs) -> None:
        """
        Class contructor method
        """
        try:

            super().__init__(**kwargs)
            self._client_type = kwargs.pop("client_type")
            if self._client_type:
                self._conn = self.client(service_name=self._client_type)
        except Exception as ex:
            logging.warning(ex)

    @property
    def conn(self) -> Any:
        """connection property

        Returns:
            Any: connection object
        """
        if not self._conn:
            return None
        return self._conn

    @property
    def client_type(self) -> str:
        """client type property

        Returns:
            str: client type
        """
        return self._client_type

    def get_inventory(self) -> Any:
        """get inventory base method

        Raises:
            NotImplementedError: Not implement exception

        Returns:
            Any: result object
        """
        raise NotImplementedError

    def get_resources(self) -> Any:
        """Get resource base method

        Raises:
            NotImplementedError: Not implement exception

        Returns:
            Any: result object
        """
        raise NotImplementedError
