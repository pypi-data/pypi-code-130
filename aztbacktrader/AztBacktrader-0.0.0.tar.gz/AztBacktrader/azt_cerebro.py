from backtrader import Cerebro
from .azt_data import AztData
from .azt_broker import AztBroker
from .azt_sizer import AztSizer


class AztCerebro(Cerebro):
    params = dict(
        quicknotify=True
    )

    def __init__(self,
                 exchange_addr=None,  # 柜台服务地址
                 quote_addr=None,  # 行情服务地址
                 account=None,  # 柜台服务账户
                 passwd=None,  # 柜台服务密码
                 strategy_id=None,
                 strategy_check_code=None,
                 timeout=3,  # 连接超时时间（单位：秒）
                 reconnect=0,  # 重连次数 0表示不重试 ≥1表示重试次数 -1表示无限重试直至连接成功
                 reconnect_interval=3,  # 重试间隔时间（单位：秒，当reconnect=0时可忽略）
                 datanames=None,  # 行情订阅列表
                 **kwargs
                 ):
        super(AztCerebro, self).__init__()

        self._broker = AztBroker(
            exchange_addr=exchange_addr,
            quote_addr=quote_addr,
            account=account,
            passwd=passwd,
            strategy_id=strategy_id,
            strategy_check_code=strategy_check_code,
            timeout=timeout,
            reconnect=reconnect,
            reconnect_interval=reconnect_interval,
            **kwargs
        )
        self._broker.cerebro = self

        if datanames:
            for dataname in datanames:
                data = AztData(dataname=dataname)
                self.adddata(data, name=dataname)
        self.sizers[None] = (AztSizer, (), {})
