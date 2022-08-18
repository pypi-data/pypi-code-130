from multicall import Call, Multicall
from enum import IntEnum
from web3 import Web3
def from_baseUnit(decimal):
    '''
    :param value:
    :param decimal: 1e8,1e18,....
    :return:
    '''
    def from_wei(value):
        return value / decimal
    return from_wei
def to_baseUnit(value):
    '''
    :param value:
    :param decimal: 1e8,1e18,....
    :return:
    '''
    return int(value)
class NetworkEx(IntEnum):
    EthMainnet = 1
    Rinkeby = 4
    WanMainnet = 888
    WanTestnet = 999
    BscMainnet = 56
    BscTestnet = 97
    MoonbaseAlpha = 1287
    Moonriver = 1285
    Moonbeam = 1284
    AvalancheFuji = 43113
    AvalancheMainnet = 43114
    MaticTestnet = 80001
    Matic = 137
    ArbitrumTestnetRinkeby = 421611
    ArbitrumOne = 42161
    FTM = 250
    FTMtest = 4002
    # OETH = 10
    OETHtest = 69
    XDC = 50
    XDCtest = 51
    GLMR = 1284
    OKC = 66
    OKCtest = 65
    CLV = 1024
    CLVtest = 1024


MULTICALL_ADDRESSES = {
    NetworkEx.EthMainnet: '0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441',
    NetworkEx.Rinkeby: '0x42Ad527de7d4e9d9d011aC45B31D8551f8Fe9821',
    NetworkEx.WanMainnet:'0xBa5934Ab3056fcA1Fa458D30FBB3810c3eb5145f',
    NetworkEx.WanTestnet:'0x14095a721Dddb892D6350a777c75396D634A7d97',
    NetworkEx.BscMainnet: '0x023a33445F11C978f8a99E232E1c526ae3C0Ad70',
    NetworkEx.BscTestnet:'0x54b738619DE4770A17fF3D6bA4c2b591a886A062',
    NetworkEx.MoonbaseAlpha:'0x136333217C18Cd6E018B85Aaf8Bd563EB72E97Fd',
    NetworkEx.Moonriver:'0x1Fe0C23940FcE7f440248e00Ce2a175977EE4B16',
    NetworkEx.AvalancheFuji:'0x0EA414bAAf9643be59667E92E26a87c4Bae3F33a',
    NetworkEx.AvalancheMainnet:'0xA4726706935901fe7dd0F23Cf5D4fb19867dfc88',
    NetworkEx.MaticTestnet:'0x905B3237B2367B2DdEBdF54D4F5320429710850a',
    NetworkEx.ArbitrumTestnetRinkeby:'0x06c6b65A8d5F52FA1E6d90bDB3Bdd4CB85F4587f',
    NetworkEx.ArbitrumOne:'0xb66f96e30d6a0ae64d24e392bb2dbd25155cb3a6',
    NetworkEx.Matic: '0x1bbc16260d5d052f1493b8f2aeee7888fed1e9ab',
    NetworkEx.FTM:'0x5f4870D51d2629D7493970B9d4526377Da98e95e',
    NetworkEx.FTMtest:'0x5379271958a603ba1cd782588643d9566799670c',
    NetworkEx.OETHtest:'0xcB5E16FC59108511B86342D654c89E5e0c460c85',
    NetworkEx.XDC:'0x711bC8Dc6BF017958470c6A25f77D05Db2DCe65B',
    NetworkEx.XDCtest:'0x4a9F99ceb037E8C4FBEC272D17D40282aA67d9c6',
    NetworkEx.GLMR:'0xBAcAaa4509EE9c9b2cF7133B970BC6db47713477',
    NetworkEx.OKC: '0xbd4191828aeff23fb9e0249a5ae583a4b9425e49',
    NetworkEx.OKCtest:'0x3ecc2399611A26E70dbac73714395b13Bc3B69fA',
    NetworkEx.CLV:'0x9b281146a04a67948f4601abda704016296017c5',
    NetworkEx.CLVtest:'0x9b281146a04a67948f4601abda704016296017c5'
}

class EMultilCall(Multicall):
    def __call__(self):
        aggregate = Call(
            MULTICALL_ADDRESSES[self.w3.eth.chainId],
            'aggregate((address,bytes)[])(uint256,bytes[])',
            returns=None,
            _w3=self.w3,
            block_id=self.block_id
        )
        args = [[[call.target, call.data] for call in self.calls]]
        block, outputs = aggregate(args)
        result = {}
        for call, output in zip(self.calls, outputs):
            result.update(call.decode_output(output))
        return result

if __name__ == '__main__':
    calls = [Call('0x07FDb4e8f8E420d021B9abEB2B1f6DcE150Ef77c','totalSupply()(uint256)',[['ToTallSupply', to_baseUnit]]),Call('0xc8F5b26589392fDE84eE0482e2b5a77DFbE943Fc','totalSupply()(uint256)',[['ToTall2Supply', to_baseUnit]])]
    multi = EMultilCall(calls,_w3=Web3(Web3.HTTPProvider('https://gwan-ssl.wandevs.org:46891')))
    print(multi())