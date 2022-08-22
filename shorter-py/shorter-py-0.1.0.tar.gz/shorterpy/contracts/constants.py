from shorterpy.api import Network

ADDRESSES: dict[str, dict[str, str]] = {
    Network.RINKEBY.name: {
        "IPoolGuardian": "0xC7d06fD23c91A82746Faf3036fb108F9BaE1e54B",
        "ITradingHub": "0xDeA57Fb4d730F7c299cdb6A07ad7516A0419C3d4",
        "AuctionHall": "0xaB9017f5F60A39c153FbDbEdbA48f4D1e593C3A8",
        "ICommittee": "0x7734A0C45454b407e8aABB21367B3cCeFf537888",
        "IFarming": "0x3C0DcCc861FA43CaA95e98c353Ef84b6a9Bcb4E9",
        "IVaultButler": "0x6069B184bD998B10dc019A587441C58d8D0EA18d",
        "IStrPool": "0x0000000000000000000000000000000000000000",
        "IERC20": "0x0000000000000000000000000000000000000000",
    },
    Network.MAINNET.name: {
        # coming soon
    },
}
