from typing import Any, List
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import TradingHubPositionInfo


class TradingHub(BaseContract):
    """
    A class to Interface with the TradingHub contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.ITradingHub)

    def buy_cover(
        self,
        pool_id: int,
        amount: int,
        amount_in_max: int,
        swap_router: str,
        path: str,
        gas_params: GasParams,
    ) -> Any:
        """
        Send a signed transaction to the TradingHub contract to call the buyCover function
        Args:
            pool_id: The pool id
            amount: The amount to buy
            amount_in_max: The maximum amount to buy
            swap_router: The swap router address
            path: The path to use
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "buyCover",
            pool_id,
            amount,
            amount_in_max,
            swap_router,
            path,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def get_position_info(self, position: str) -> TradingHubPositionInfo:
        """
        Get the position info for a position
        Args:
            position: The position to get the info for
        Returns:
            The position info
        """
        return TradingHubPositionInfo(*self.call("getPositionInfo", position))

    def get_positions(self, account: str) -> List[str]:
        """
        Get the positions for an account
        Args:
            account: The account to get the positions for
        Returns:
            The positions for the account
        """
        return self.call("getPositions", account)

    def get_positions_by_pool_id(self, pool_id: int, position_state: int) -> List[str]:
        """
        Get all positions for a pool id
        Args:
            pool_id: The pool id to get the positions for
            position_state: The position state to get the positions for
        Returns:
            The positions for the pool id
        """
        return self.call("getPositionsByPoolId", pool_id, position_state)

    def get_positions_by_state(self, position_state: int) -> List[str]:
        """
        Get all positions by their state
        Args:
            position_state: The state to get the positions for
        Returns:
            The positions for the state
        """
        return self.call("getPositionsByState", position_state)

    def is_pool_withdrawable(self, pool_id: int) -> bool:
        """
        Check if a pool is withdrawable
        Args:
            pool_id: The pool id to check
        Returns:
            True if the pool is withdrawable, False otherwise
        """
        return self.call("isPoolWithdrawable", pool_id)

    def sell_short(
        self,
        pool_id: int,
        amount: int,
        amount_out_min: int,
        swap_router: str,
        path: str,
        gas_params: GasParams,
    ) -> Any:
        """
        Send a signed transaction to the TradingHub contract to call the sellShort function
        Args:
            pool_id: The pool id
            amount: The amount to sell
            amount_out_min: The minimum amount to sell
            swap_router: The swap router address
            path: The path to use
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "sellShort",
            pool_id,
            amount,
            amount_out_min,
            swap_router,
            path,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
