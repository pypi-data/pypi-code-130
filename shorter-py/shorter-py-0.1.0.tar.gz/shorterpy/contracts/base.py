from enum import Enum
from shorterpy.api import ApiProvider
import pkgutil
import json
from shorterpy.contracts.constants import ADDRESSES


class Contracts(Enum):
    """
    Enum for contract
    """

    IAuctionHall = 1
    IPoolGuardian = 2
    IVaultButler = 3
    IFarming = 4
    ICommittee = 5
    IStrPool = 6
    ITradingHub = 7
    IERC20 = 8


class BaseContract:
    """
    Base class for all contracts
    """

    def __init__(self, api: ApiProvider, name: Contracts):
        self._api = api
        data = pkgutil.get_data(__name__, f"./abi/{name.name}.json")
        if data is not None:
            self.abi = json.loads(data.decode("utf-8"))["abi"]
        else:
            raise Exception(f"{name.name} not found")
        self.addr = ADDRESSES[self._api.network.name][name.name]
        self.connect(self.addr, self.abi)

    def connect(self, addr: str, abi: str):
        """
        Connect to the contract
        Args:
            addr: The address of the contract
            abi: The abi of the contract
        """
        self.contract = self._api.api.eth.contract(address=addr, abi=abi)

    def call(self, func: str, *args):
        """
        Call a function on the contract
        Args:
            func: The function to call
            args: The arguments to pass to the function
        Returns:
            The return value of the function
        """
        return self.contract.functions[func](*args).call()

    def build_and_sign_tx(self, func: str, *args, private_key: str, tx_params: dict):
        """
        Build and sign a transaction
        Args:
            func: The function to call
            args: The arguments to pass to the function
            private_key: The private key to sign the transaction with
            tx_params: The transaction parameters
        Returns:
            The signed transaction
        """
        tx = self.contract.functions[func](*args).buildTransaction(tx_params)
        signed_tx = self._api.api.eth.account.sign_transaction(tx, private_key)
        return signed_tx
