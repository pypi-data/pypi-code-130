"""ApiProvider class"""

from web3 import Web3
from eth_account import Account
from enum import Enum


class Network(Enum):
    """
    Enum for network
    """

    MAINNET = 1
    RINKEBY = 2


class ApiProvider:

    abi_dir: str

    def __init__(self, endpoint: str, network: Network, account: Account):
        """
        Initialize ApiProvider object.
        Args:
            endpoint: Endpoint URL
            network: Network type
            account: Account object
        """
        self._api = self._wrap_api(endpoint)
        self._account = account
        self.network = network

    def _wrap_api(self, endpoint):
        """
        Generate Web3 object from the endpoint.
        Args:
            endpoint: Endpoint URL
        Returns:
            Web3 object
        """
        protocol = endpoint.split(":")[0]
        if protocol == "https" or protocol == "http":
            provider = Web3.HTTPProvider(endpoint)
        elif protocol == "ws" or protocol == "wss":
            provider = Web3.WebsocketProvider(endpoint)
        else:
            raise ValueError(f'Unknown protocol in the given endpoint: "{endpoint}"')
        return Web3(provider)

    @property
    def api(self):
        """
        Get the Web3 object.
        Returns:
            Web3 object
        """
        return self._api

    @property
    def account(self):
        """
        Get the account object.
        Returns:
            Account object
        """
        return self._account

    def send_tx_and_get_receipt(self, tx):
        """
        Send a signed transaction and get the receipt.
        Args:
            tx: Signed transaction
        Returns:
            The receipt of the transaction
        """
        tx_hash = self._api.eth.send_raw_transaction(tx.rawTransaction)
        receipt = self._api.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
