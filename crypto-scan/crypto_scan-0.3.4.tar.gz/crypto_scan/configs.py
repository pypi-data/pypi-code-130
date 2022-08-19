ETH_CHAIN = 'ETHERIUM'
POLYGON_CHAIN = 'POLYGON'
BSC_CHAIN = 'BSC'
SOLANA_CHAIN = 'SOLANA'

CHAIN_OPTIONS = [ETH_CHAIN, POLYGON_CHAIN, BSC_CHAIN]  # SOLANA_CHAIN

ETHNET = "https://api.etherscan.io"
POLYGONNET = "https://api.polygonscan.com"
BSCNET = "https://api.bscscan.com/"

ETHERSCAN_URL = "https://etherscan.io"
POLYSCAN_URL = "https://polygonscan.com"
BSCSCAN_URL = "https://bscscan.com"

COIN_GECHO_CHAIN_DATA = {
    ETH_CHAIN: {
        "chain_id": "ethereum",
        "coin_id": "ethereum",
        "symbol": "eth",
    },
    POLYGON_CHAIN: {
        "chain_id": "polygon-pos",
        "coin_id": "matic-network",
        "symbol": "matic",
    },
    SOLANA_CHAIN: {
        "chain_id": "solana",
        "coin_id": "solana",
        "symbol": "sol",
    },
    BSC_CHAIN: {
        "chain_id": "binancecoin",
        "coin_id": "binancecoin",
        "symbol": "bnb",
    },
}
