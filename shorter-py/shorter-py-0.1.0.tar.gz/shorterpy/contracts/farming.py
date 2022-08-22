from typing import Any, List
from shorterpy.contracts.base import BaseContract, Contracts
from shorterpy.api.apiProvider import ApiProvider
from shorterpy.common.types import GasParams
from shorterpy.contracts.types import PendingRewards


class Farming(BaseContract):
    """
    Class to Interface with Farming contract
    """

    def __init__(self, api: ApiProvider):
        super().__init__(api, Contracts.IFarming)

    def all_pending_rewards(self, user: str) -> PendingRewards:
        """
        Call the allPendingRewards function to get all pending rewards for a user
        Args:
            user: The user to get the pending rewards for
        Returns:
            A PendingRewards object containing all pending rewards for the user
        """
        return PendingRewards(*self.call("allPendingRewards", user))

    def get_user_staked_amount(self, user: str) -> int:
        """
        Call the getUserStakedAmount function to get the staked amount for a user
        Args:
            user: The user to get the staked amount for
        Returns:
            The staked amount for the user
        """
        return self.call("getUserStakedAmount", user)

    def harvest_all(
        self,
        gov_rewards: int,
        farming_rewards: int,
        vote_against_rewards: int,
        trading_reward_pools: List[int],
        staked_reward_pools: List[int],
        create_reward_pools: List[int],
        vote_reward_pools: List[int],
        gas_params: GasParams,
    ) -> Any:
        """
        Send a signed transaction to the Farming contract to call the harvestAll function
        Args:
            gov_rewards: The amount of gov rewards to harvest
            farming_rewards: The amount of farming rewards to harvest
            vote_against_rewards: The amount of vote against rewards to harvest
            trading_reward_pools: The list of trading reward pools to harvest
            staked_reward_pools: The list of staked reward pools to harvest
            create_reward_pools: The list of create reward pools to harvest
            vote_reward_pools: The list of vote reward pools to harvest
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "harvestAll",
            gov_rewards,
            farming_rewards,
            vote_against_rewards,
            trading_reward_pools,
            staked_reward_pools,
            create_reward_pools,
            vote_reward_pools,
            private_key=self._api.account.key,
            tx_params=tx_params,
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def lp_token(self) -> str:
        """
        Call the lpToken function to get the address of the LP token
        Returns:
            The address of the LP token
        """
        return self.call("lpToken")

    def stake(self, amount: int, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the Farming contract to call the stake function
        Args:
            amount: The amount to stake
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "stake", amount, private_key=self._api.account.key, tx_params=tx_params
        )
        return self._api.send_tx_and_get_receipt(signed_tx)

    def un_stake(self, amount: int, gas_params: GasParams) -> Any:
        """
        Send a signed transaction to the Farming contract to call the unStake function
        Args:
            amount: The amount to un-stake
            gas_params: Gas parameters to use for the transaction
        Returns:
            The receipt of the transaction
        """
        nonce = self._api.api.eth.getTransactionCount(self._api.account.address)
        tx_params = {"nonce": nonce, **(gas_params.to_dict())}
        signed_tx = self.build_and_sign_tx(
            "unStake", amount, private_key=self._api.account.key, tx_params=tx_params
        )
        return self._api.send_tx_and_get_receipt(signed_tx)
