from abc import abstractmethod, ABC

from algora.common.model import DataRequest
from algora.common.type import DataResponse


class Source(ABC):
    """
    Data source class, containing name and get_data methods.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Data source name.

        Returns:
            str: Data source name
        """
        pass

    @abstractmethod
    def get_data(self, request: DataRequest) -> DataResponse:
        """
        Get data and return result.

        Args:
            request (DataRequest): Data request class

        Returns:
            DataResponse: Data response
        """
        pass


class AsyncSource(ABC):
    """
    Asynchronous data source class, containing name and asynchronous get_data methods.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Data source name.

        Returns:
            str: Data source name
        """
        pass

    @abstractmethod
    async def get_data(self, request: DataRequest) -> DataResponse:
        """
        Asynchronously get data and return result.

        Args:
            request (DataRequest): Data request class

        Returns:
            DataResponse: Data response
        """
        pass
