from typing import Any
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import LegacyInfos


class VaultButler(BaseContract):
    """
    A class to Interface with VaultButler contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.IVaultButler)

    def execute_naginata(
        self, position: str, bid_size: str, gas_params: GasParams
    ) -> Any:
        """
        Send a signed transaction to the VaultButler contract to execute Naginata
        Args:
            position: The position to execute on
            bid_size: The bid size
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "executeNaginata",
            position,
            bid_size,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def legacy_infos(self, position: str) -> LegacyInfos:
        """
        Get the legacy infos for a position
        Args:
            position: The position to get the info for
        Returns:
            The legacy infos
        """
        return LegacyInfos(*self.call("legacyInfos", position))

    def price_of_legacy(self, position: str) -> int:
        """
        Get the price of legacy for a position
        Args:
            position: The position to get the price for
        Returns:
            The price of legacy
        """
        return self.call("priceOfLegacy", position)
