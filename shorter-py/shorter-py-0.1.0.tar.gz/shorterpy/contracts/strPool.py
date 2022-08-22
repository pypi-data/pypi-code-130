from typing import Any
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import PoolInfo, PositionInfo


class StrPool(BaseContract):
    """
    A class to Interface with any StrPool contracts
    """

    def __init__(self, api: ApiProvider, addr: str):
        """
        Initialize the class with the api provider and the address of the contract
        """
        super().__init__(api, Contracts.IStrPool)
        self.connect(addr, self.abi)

    def deposit(self, amount: str, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the StrPool contract to deposit an amount
        Args:
            amount: The amount to deposit
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "deposit", amount, private_key=self._api.account.key, tx_params=tx_params
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def get_info(self) -> PoolInfo:
        """
        Get the info of the pool
        Returns:
            The info of the pool
        """
        return PoolInfo(*self.call("getInfo"))

    def is_delivery(self) -> bool:
        """
        Check if the pool is in delivery mode
        Returns:
            True if the pool is in delivery mode, False otherwise
        """
        return self.call("isDelivery")

    def postition_info_map(self, address: str) -> PositionInfo:
        """
        Get the info of a position
        Args:
            address: The address of the position
        Returns:
            The info of the position
        """
        return PositionInfo(*self.call("positionInfoMap", address))

    def withdraw(self, percent: int, amount: str, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the StrPool contract to withdraw an amount
        Args:
            percent: The percent of the pool to withdraw
            amount: The amount to withdraw
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "withdraw",
            percent,
            amount,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def withdraw_remnant_asset(self, position: str, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the StrPool contract to withdraw the remnant asset
        Args:
            position: The address of the position
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "withdrawRemnantAsset",
            position,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
