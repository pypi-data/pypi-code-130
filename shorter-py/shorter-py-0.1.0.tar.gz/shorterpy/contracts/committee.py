from typing import Any
from shorterpy.contracts.base import Contracts, BaseContract
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import ProposalInfo, UserShares


class Committee(BaseContract):
    """
    A class to Interface with Committee contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.ICommittee)

    def create_pool_proposal(
        self,
        staked_token: str,
        leverage: int,
        duration_days: int,
        gas_params: GasParams,
    ) -> Any:
        """
        Send a signed transaction to the Committee contract to create a pool proposal
        Args:
            staked_token: The address of the staked token
            leverage: The leverage
            duration_days: The duration in days
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "createPoolProposal",
            staked_token,
            leverage,
            duration_days,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def deposit(self, amount: int, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the Committee contract to call the deposit function
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

    def get_user_shares(self, account: str) -> UserShares:
        """
        Call the getUserShares function on the Committee contract
        Args:
            account: The address of the user
        Returns:
            The UserShares object
        """
        return UserShares(*self.call("getUserShares", account))

    def is_ruler(self, account: str) -> bool:
        """
        Call the isRuler function on the Committee contract
        Args:
            account: The address of the user
        Returns:
            True if the user is a ruler, False otherwise
        """
        return self.call("isRuler", account)

    def proposal_gallery(self, proposal_id: int) -> ProposalInfo:
        """
        Call the proposalGallery function on the Committee contract
        Args:
            proposal_id: The id of the proposal
        Returns:
            The ProposalInfo object
        """
        return ProposalInfo(*self.call("proposalGallery", proposal_id))

    def vote(
        self, proposal_id: int, direction: bool, vote_share: int, gas_params: GasParams
    ) -> Any:
        """
        Send a signed transaction to the Committee contract to vote on a proposal
        Args:
            proposal_id: The id of the proposal
            direction: The direction of the vote
            vote_share: The share of the vote
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "vote",
            proposal_id,
            direction,
            vote_share,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def withdraw(self, amount: int, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the Committee contract to withdraw funds
        Args:
            amount: The amount to withdraw
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "withdraw", amount, private_key=self._api.account.key, tx_params=tx_params
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
