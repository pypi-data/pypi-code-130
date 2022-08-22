from typing import List
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.contracts.types import PoolGuardianPoolInfo


class PoolGuardian(BaseContract):
    """
    A class to Interface with the PoolGuardian contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.IPoolGuardian)

    def get_created_pool_ids(self, creator: str) -> List[int]:
        """
        Get the list of pool ids created by a creator
        Args:
            creator: The address of the creator
        Returns:
            The list of pool ids created by the creator
        """
        return self.call("getCreatedPoolIds", creator)

    def get_pool_info(self, pool_id: int) -> PoolGuardianPoolInfo:
        """
        Call the getPoolInfo function of the PoolGuardian contract
        Args:
            pool_id: The id of the pool to get info for
        Returns:
            A PoolGuardianPoolInfo object containing the info for the pool
        """
        return PoolGuardianPoolInfo(*self.call("getPoolInfo", pool_id))

    def query_pools(self, staked_token: str, status: int) -> List[int]:
        """
        Call the queryPools function of the PoolGuardian contract
        Args:
            staked_token: The staked token to query for
            status: The status of the pool to query for
        Returns:
            The list of pool ids that match the query
        """
        return self.call("queryPools", staked_token, status)
