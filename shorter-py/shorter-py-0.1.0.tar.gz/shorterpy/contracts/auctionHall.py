"""AuctionHall Class"""

from typing import Any
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import Phase1Info, Phase2Info, QueryResidueResult


class AuctionHall(BaseContract):
    """
    Class to Interface with AuctionHall contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.IAuctionHall)

    def bid_katana(self, position: str, path: str, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the AuctionHall contract to bid Katana
        Args:
            position: The position to bid on
            path: The path variable
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "bidKatana",
            position,
            path,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def bid_tanto(
        self, position: str, bid_size: int, priority_fee: int, gas_params: GasParams
    ) -> Any:
        """
        Send a signed transaction to the AuctionHall contract to bid Tanto
        Args:
            position: The position to bid on
            bid_size: The bid size
            priority_fee: The priority fee
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "bidTanto",
            position,
            bid_size,
            priority_fee,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def phase1_infos(self, position: str) -> Phase1Info:
        """
        Call the phase1Infos function on the AuctionHall contract
        Args:
            position: The position to query
        Returns:
            The phase1Info for the position
        """
        return Phase1Info(*self.call("phase1Infos", position))

    def phase2_infos(self, position: str) -> Phase2Info:
        """
        Call the phase2Infos function on the AuctionHall contract
        Args:
            position: The position to query
        Returns:
            The phase2Info for the position
        """
        return Phase2Info(*self.call("phase2Infos", position))
        return Phase2Info(*self.call("phase2Infos", position))

    def query_residues(self, position: str, ruler: str) -> QueryResidueResult:
        """
        Call the queryResidues function on the AuctionHall contract
        Args:
            position: The position to query
            ruler: The ruler to query
        Returns:
            The queryResidues result for the position and ruler
        """
        return QueryResidueResult(*self.call("queryResidues", position, ruler))

    def retrieve(self, position: str, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the AuctionHall contract to call the retrieve function
        Args:
            position: The position to retrieve
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "retrieve", position, private_key=self._api.account.key, tx_params=tx_params
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
