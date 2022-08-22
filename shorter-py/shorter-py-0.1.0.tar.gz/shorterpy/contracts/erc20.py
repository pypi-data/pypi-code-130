from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api import ApiProvider
from shorterpy.common.types import GasParams
from typing import Any


class ERC20(BaseContract):
    """
    Class to Interface with any ERC20 contract
    """

    def __init__(self, api: ApiProvider, addr: str):
        super().__init__(api, Contracts.IERC20)
        self.connect(addr, self.abi)

    def approve(self, spender: str, amount: int, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the ERC20 contract to approve an amount to a spender
        Args:
            spender: The address of the spender
            amount: The amount to approve
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "approve",
            spender,
            amount,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
