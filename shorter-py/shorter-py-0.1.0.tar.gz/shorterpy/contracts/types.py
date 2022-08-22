from dataclasses import dataclass
from typing import List


@dataclass
class PoolInfo:
    """
    A class to hold the info for a pool in StrPool contract
    """

    creator: str
    stakedToken: str
    stableToken: str
    wrappedToken: str
    leverage: int
    durationDays: int
    startBlock: int
    endBlock: int
    id: int
    stakedTokenDecimals: int
    stableTokenDecimals: int
    stateFlag: int


@dataclass
class PositionInfo:
    """
    A class to hold the info for a position in StrPool contract
    """

    trader: str
    closedFlag: bool
    latestFeeBlock: int
    totalSize: int
    unsettledCash: int
    remnantAsset: int
    totalFee: int


@dataclass
class TradingHubPositionInfo:
    """
    A class to hold the info for a position in the trading hub
    """

    poolId: int
    strToken: str
    closingBlock: int
    positionState: int


@dataclass
class LegacyInfos:
    """
    A class to hold legacy info for a position
    """

    bidSize: int
    usedCash: int


@dataclass
class PoolGuardianPoolInfo:
    """
    A class to hold the info for a pool in the pool guardian
    """

    stakedToken: str
    strToken: str
    stateFlag: int


@dataclass
class PendingRewards:
    """
    A class to hold the info for pending rewards of a user
    """

    gov_rewards: int
    farming_rewards: int
    vote_against_rewards: int
    trading_rewards: int
    staked_rewards: int
    creator_rewards: int
    vote_rewards: int
    trading_reward_pools: List[int]
    staked_reward_pools: List[int]
    create_reward_pools: List[int]
    vote_reward_pools: List[int]


@dataclass
class UserShares:
    """
    A class to hold the info for shares of a user
    """

    total_share: int
    locked_share: int


@dataclass
class ProposalInfo:
    """
    A class to hold the info for a proposal
    """

    id: int
    proposer: str
    catagory: str
    startBlock: int
    endBlock: int
    forShares: int
    againstShares: int
    status: int
    displayable: bool


@dataclass
class Phase1Info:
    """
    A class to hold the phase 1 infos
    """

    bid_size: int
    liquidation_price: int
    is_sorted: bool
    flag: bool


@dataclass
class Phase2Info:
    """
    A class to hold the phase 2 infos
    """

    flag: bool
    is_withdrawan: bool
    ruler_addr: str
    debt_size: int
    used_cash: int
    dex_cover_reward: int


@dataclass
class QueryResidueResult:
    """
    A class to hold the result of query residue
    """

    stable_token_size: int
    debt_token_size: int
    priority_fee: int
