import json

# contract source at .contract_sources/OffchainLookup.sol
OFFCHAIN_LOOKUP_BYTECODE = "608060405260405180604001604052806040518060600160405280602c815260200162000ec9602c9139815260200160405180606001604052806025815260200162000ef56025913981525060009060026200005d92919062000072565b503480156200006b57600080fd5b506200025b565b828054828255906000526020600020908101928215620000c6579160200282015b82811115620000c5578251829080519060200190620000b4929190620000d9565b509160200191906001019062000093565b5b509050620000d591906200016a565b5090565b828054620000e79062000226565b90600052602060002090601f0160209004810192826200010b576000855562000157565b82601f106200012657805160ff191683800117855562000157565b8280016001018555821562000157579182015b828111156200015657825182559160200191906001019062000139565b5b50905062000166919062000192565b5090565b5b808211156200018e5760008181620001849190620001b1565b506001016200016b565b5090565b5b80821115620001ad57600081600090555060010162000193565b5090565b508054620001bf9062000226565b6000825580601f10620001d35750620001f4565b601f016020900490600052602060002090810190620001f3919062000192565b5b50565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b600060028204905060018216806200023f57607f821691505b602082108103620002555762000254620001f7565b5b50919050565b610c5e806200026b6000396000f3fe608060405234801561001057600080fd5b50600436106100415760003560e01c806309a3c01b146100465780636337ed5814610064578063da96d05a14610094575b600080fd5b61004e6100c4565b60405161005b9190610424565b60405180910390f35b61007e600480360381019061007991906104bf565b610114565b60405161008b9190610424565b60405180910390f35b6100ae60048036038101906100a9919061050c565b610202565b6040516100bb9190610424565b60405180910390f35b606080306000826309a3c01b60e01b846040517f556f183000000000000000000000000000000000000000000000000000000000815260040161010b9594939291906107d5565b60405180910390fd5b606060008383810190610127919061096d565b90507fd9bdd1345ca2a00d0c1413137c1b2b1d0a35e5b0e11508f3b3eff856286af0758160405160200161015b91906109fd565b60405160208183030381529060405280519060200120146101b1576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016101a890610a71565b60405180910390fd5b306000858563da96d05a60e01b88886040517f556f18300000000000000000000000000000000000000000000000000000000081526004016101f99796959493929190610abe565b60405180910390fd5b606060008585810190610215919061096d565b90507faed76f463930323372899e36460e078e5292aac45f645bbe567be6fca83ede108160405160200161024991906109fd565b604051602081830303815290604052805190602001201461029f576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161029690610b9c565b60405180910390fd5b600084848101906102b0919061096d565b90507fd9bdd1345ca2a00d0c1413137c1b2b1d0a35e5b0e11508f3b3eff856286af075816040516020016102e491906109fd565b604051602081830303815290604052805190602001201461033a576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161033190610c08565b60405180910390fd5b86868080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505092505050949350505050565b600081519050919050565b600082825260208201905092915050565b60005b838110156103c55780820151818401526020810190506103aa565b838111156103d4576000848401525b50505050565b6000601f19601f8301169050919050565b60006103f68261038b565b6104008185610396565b93506104108185602086016103a7565b610419816103da565b840191505092915050565b6000602082019050818103600083015261043e81846103eb565b905092915050565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b600080fd5b60008083601f84011261047f5761047e61045a565b5b8235905067ffffffffffffffff81111561049c5761049b61045f565b5b6020830191508360018202830111156104b8576104b7610464565b5b9250929050565b600080602083850312156104d6576104d5610450565b5b600083013567ffffffffffffffff8111156104f4576104f3610455565b5b61050085828601610469565b92509250509250929050565b6000806000806040858703121561052657610525610450565b5b600085013567ffffffffffffffff81111561054457610543610455565b5b61055087828801610469565b9450945050602085013567ffffffffffffffff81111561057357610572610455565b5b61057f87828801610469565b925092505092959194509250565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006105b88261058d565b9050919050565b6105c8816105ad565b82525050565b600081549050919050565b600082825260208201905092915050565b60008190508160005260206000209050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061064657607f821691505b602082108103610659576106586105ff565b5b50919050565b600082825260208201905092915050565b60008190508160005260206000209050919050565b600081546106928161062e565b61069c818661065f565b945060018216600081146106b757600181146106c9576106fc565b60ff19831686526020860193506106fc565b6106d285610670565b60005b838110156106f4578154818901526001820191506020810190506106d5565b808801955050505b50505092915050565b60006107118383610685565b905092915050565b6000600182019050919050565b6000610731826105ce565b61073b81856105d9565b93508360208202850161074d856105ea565b8060005b85811015610788578484038952816107698582610705565b945061077483610719565b925060208a01995050600181019050610751565b50829750879550505050505092915050565b60007fffffffff0000000000000000000000000000000000000000000000000000000082169050919050565b6107cf8161079a565b82525050565b600060a0820190506107ea60008301886105bf565b81810360208301526107fc8187610726565b9050818103604083015261081081866103eb565b905061081f60608301856107c6565b818103608083015261083181846103eb565b90509695505050505050565b600080fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b61087a826103da565b810181811067ffffffffffffffff8211171561089957610898610842565b5b80604052505050565b60006108ac610446565b90506108b88282610871565b919050565b600067ffffffffffffffff8211156108d8576108d7610842565b5b6108e1826103da565b9050602081019050919050565b82818337600083830152505050565b600061091061090b846108bd565b6108a2565b90508281526020810184848401111561092c5761092b61083d565b5b6109378482856108ee565b509392505050565b600082601f8301126109545761095361045a565b5b81356109648482602086016108fd565b91505092915050565b60006020828403121561098357610982610450565b5b600082013567ffffffffffffffff8111156109a1576109a0610455565b5b6109ad8482850161093f565b91505092915050565b600081519050919050565b600081905092915050565b60006109d7826109b6565b6109e181856109c1565b93506109f18185602086016103a7565b80840191505092915050565b6000610a0982846109cc565b915081905092915050565b600082825260208201905092915050565b7f7465737420646174612076616c69646174696f6e206661696c65642e00000000600082015250565b6000610a5b601c83610a14565b9150610a6682610a25565b602082019050919050565b60006020820190508181036000830152610a8a81610a4e565b9050919050565b6000610a9d8385610396565b9350610aaa8385846108ee565b610ab3836103da565b840190509392505050565b600060a082019050610ad3600083018a6105bf565b8181036020830152610ae58189610726565b90508181036040830152610afa818789610a91565b9050610b0960608301866107c6565b8181036080830152610b1c818486610a91565b905098975050505050505050565b7f68747470207265717565737420726573756c742076616c69646174696f6e206660008201527f61696c65642e0000000000000000000000000000000000000000000000000000602082015250565b6000610b86602683610a14565b9150610b9182610b2a565b604082019050919050565b60006020820190508181036000830152610bb581610b79565b9050919050565b7f6578747261446174612076616c69646174696f6e206661696c65642e00000000600082015250565b6000610bf2601c83610a14565b9150610bfd82610bbc565b602082019050919050565b60006020820190508181036000830152610c2181610be5565b905091905056fea2646970667358221220528c32029f8724a4e2b6a2a469880824c952eae5971f18628559629192c102b164736f6c634300080d003368747470733a2f2f776562332e70792f676174657761792f7b73656e6465727d2f7b646174617d2e6a736f6e68747470733a2f2f776562332e70792f676174657761792f7b73656e6465727d2e6a736f6e"  # noqa: E501
OFFCHAIN_LOOKUP_BYTECODE_RUNTIME = "608060405234801561001057600080fd5b50600436106100415760003560e01c806309a3c01b146100465780636337ed5814610064578063da96d05a14610094575b600080fd5b61004e6100c4565b60405161005b9190610424565b60405180910390f35b61007e600480360381019061007991906104bf565b610114565b60405161008b9190610424565b60405180910390f35b6100ae60048036038101906100a9919061050c565b610202565b6040516100bb9190610424565b60405180910390f35b606080306000826309a3c01b60e01b846040517f556f183000000000000000000000000000000000000000000000000000000000815260040161010b9594939291906107d5565b60405180910390fd5b606060008383810190610127919061096d565b90507fd9bdd1345ca2a00d0c1413137c1b2b1d0a35e5b0e11508f3b3eff856286af0758160405160200161015b91906109fd565b60405160208183030381529060405280519060200120146101b1576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016101a890610a71565b60405180910390fd5b306000858563da96d05a60e01b88886040517f556f18300000000000000000000000000000000000000000000000000000000081526004016101f99796959493929190610abe565b60405180910390fd5b606060008585810190610215919061096d565b90507faed76f463930323372899e36460e078e5292aac45f645bbe567be6fca83ede108160405160200161024991906109fd565b604051602081830303815290604052805190602001201461029f576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161029690610b9c565b60405180910390fd5b600084848101906102b0919061096d565b90507fd9bdd1345ca2a00d0c1413137c1b2b1d0a35e5b0e11508f3b3eff856286af075816040516020016102e491906109fd565b604051602081830303815290604052805190602001201461033a576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161033190610c08565b60405180910390fd5b86868080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505092505050949350505050565b600081519050919050565b600082825260208201905092915050565b60005b838110156103c55780820151818401526020810190506103aa565b838111156103d4576000848401525b50505050565b6000601f19601f8301169050919050565b60006103f68261038b565b6104008185610396565b93506104108185602086016103a7565b610419816103da565b840191505092915050565b6000602082019050818103600083015261043e81846103eb565b905092915050565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b600080fd5b60008083601f84011261047f5761047e61045a565b5b8235905067ffffffffffffffff81111561049c5761049b61045f565b5b6020830191508360018202830111156104b8576104b7610464565b5b9250929050565b600080602083850312156104d6576104d5610450565b5b600083013567ffffffffffffffff8111156104f4576104f3610455565b5b61050085828601610469565b92509250509250929050565b6000806000806040858703121561052657610525610450565b5b600085013567ffffffffffffffff81111561054457610543610455565b5b61055087828801610469565b9450945050602085013567ffffffffffffffff81111561057357610572610455565b5b61057f87828801610469565b925092505092959194509250565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006105b88261058d565b9050919050565b6105c8816105ad565b82525050565b600081549050919050565b600082825260208201905092915050565b60008190508160005260206000209050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061064657607f821691505b602082108103610659576106586105ff565b5b50919050565b600082825260208201905092915050565b60008190508160005260206000209050919050565b600081546106928161062e565b61069c818661065f565b945060018216600081146106b757600181146106c9576106fc565b60ff19831686526020860193506106fc565b6106d285610670565b60005b838110156106f4578154818901526001820191506020810190506106d5565b808801955050505b50505092915050565b60006107118383610685565b905092915050565b6000600182019050919050565b6000610731826105ce565b61073b81856105d9565b93508360208202850161074d856105ea565b8060005b85811015610788578484038952816107698582610705565b945061077483610719565b925060208a01995050600181019050610751565b50829750879550505050505092915050565b60007fffffffff0000000000000000000000000000000000000000000000000000000082169050919050565b6107cf8161079a565b82525050565b600060a0820190506107ea60008301886105bf565b81810360208301526107fc8187610726565b9050818103604083015261081081866103eb565b905061081f60608301856107c6565b818103608083015261083181846103eb565b90509695505050505050565b600080fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b61087a826103da565b810181811067ffffffffffffffff8211171561089957610898610842565b5b80604052505050565b60006108ac610446565b90506108b88282610871565b919050565b600067ffffffffffffffff8211156108d8576108d7610842565b5b6108e1826103da565b9050602081019050919050565b82818337600083830152505050565b600061091061090b846108bd565b6108a2565b90508281526020810184848401111561092c5761092b61083d565b5b6109378482856108ee565b509392505050565b600082601f8301126109545761095361045a565b5b81356109648482602086016108fd565b91505092915050565b60006020828403121561098357610982610450565b5b600082013567ffffffffffffffff8111156109a1576109a0610455565b5b6109ad8482850161093f565b91505092915050565b600081519050919050565b600081905092915050565b60006109d7826109b6565b6109e181856109c1565b93506109f18185602086016103a7565b80840191505092915050565b6000610a0982846109cc565b915081905092915050565b600082825260208201905092915050565b7f7465737420646174612076616c69646174696f6e206661696c65642e00000000600082015250565b6000610a5b601c83610a14565b9150610a6682610a25565b602082019050919050565b60006020820190508181036000830152610a8a81610a4e565b9050919050565b6000610a9d8385610396565b9350610aaa8385846108ee565b610ab3836103da565b840190509392505050565b600060a082019050610ad3600083018a6105bf565b8181036020830152610ae58189610726565b90508181036040830152610afa818789610a91565b9050610b0960608301866107c6565b8181036080830152610b1c818486610a91565b905098975050505050505050565b7f68747470207265717565737420726573756c742076616c69646174696f6e206660008201527f61696c65642e0000000000000000000000000000000000000000000000000000602082015250565b6000610b86602683610a14565b9150610b9182610b2a565b604082019050919050565b60006020820190508181036000830152610bb581610b79565b9050919050565b7f6578747261446174612076616c69646174696f6e206661696c65642e00000000600082015250565b6000610bf2601c83610a14565b9150610bfd82610bbc565b602082019050919050565b60006020820190508181036000830152610c2181610be5565b905091905056fea2646970667358221220528c32029f8724a4e2b6a2a469880824c952eae5971f18628559629192c102b164736f6c634300080d0033"  # noqa: E501
OFFCHAIN_LOOKUP_ABI = json.loads(
    """[
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender", "type": "address"
            },
            {
                "internalType": "string[]",
                "name": "urls",
                "type": "string[]"
            },
            {
                "internalType": "bytes",
                "name": "callData",
                "type": "bytes"},
            {
                "internalType": "bytes4",
                "name": "callbackFunction",
                "type":"bytes4"
            },
            {
                "internalType": "bytes",
                "name": "extraData",
                "type": "bytes"
            }
        ],
        "name": "OffchainLookup",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "continuousOffchainLookup",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type":"bytes"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "testOffchainLookupData",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "", "type": "bytes"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes",
                "name": "specifiedDataFromTest",
                "type": "bytes"
            }
        ],
        "name": "testOffchainLookup",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes",
                "name": "result",
                "type": "bytes"
            },
            {
                "internalType": "bytes",
                "name": "extraData",
                "type": "bytes"
            }
        ],
        "name": "testOffchainLookupWithProof",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]"""
)
