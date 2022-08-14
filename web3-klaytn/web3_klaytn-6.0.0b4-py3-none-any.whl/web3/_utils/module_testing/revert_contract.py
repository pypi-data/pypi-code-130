import json

REVERT_CONTRACT_SOURCE = """
pragma solidity ^0.6.1;

contract RevertContract {
  function normalFunction() public pure returns (bool) {
      return true;
  }

  function revertWithMessage() public pure {
      revert('Function has been reverted.');
  }

  function revertWithoutMessage() public pure {
      revert();
  }
}
"""


REVERT_CONTRACT_BYTECODE = "608060405234801561001057600080fd5b50610123806100206000396000f3fe6080604052348015600f57600080fd5b5060043610603c5760003560e01c8063185c38a4146041578063c06a97cb146049578063d67e4b84146051575b600080fd5b60476071565b005b604f60df565b005b605760e4565b604051808215151515815260200191505060405180910390f35b6040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601b8152602001807f46756e6374696f6e20686173206265656e2072657665727465642e000000000081525060200191505060405180910390fd5b600080fd5b6000600190509056fea264697066735822122062c811906544562ea796d11199e2d956938f2a76c2aa3053dc7ab2470d854c0a64736f6c63430006060033"  # noqa: E501


REVERT_CONTRACT_RUNTIME_CODE = "6080604052348015600f57600080fd5b5060043610603c5760003560e01c8063185c38a4146041578063c06a97cb146049578063d67e4b84146051575b600080fd5b60476071565b005b604f60df565b005b605760e4565b604051808215151515815260200191505060405180910390f35b6040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601b8152602001807f46756e6374696f6e20686173206265656e2072657665727465642e000000000081525060200191505060405180910390fd5b600080fd5b6000600190509056fea264697066735822122062c811906544562ea796d11199e2d956938f2a76c2aa3053dc7ab2470d854c0a64736f6c63430006060033"  # noqa: E501


_REVERT_CONTRACT_ABI = json.loads(
    """[
    {
        "inputs": [],
        "name": "normalFunction",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "revertWithMessage",
        "outputs": [],
        "payable": false,
        "stateMutability": "pure",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "revertWithoutMessage",
        "outputs": [],
        "payable": false,
        "stateMutability": "pure",
        "type": "function"
    }
]"""
)
