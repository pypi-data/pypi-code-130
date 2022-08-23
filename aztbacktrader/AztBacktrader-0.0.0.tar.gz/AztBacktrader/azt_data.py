import queue

from backtrader.feed import DataBase
from backtrader import date2num, with_metaclass, num2date
from .azt_store import AztStore


class MetaAztData(DataBase.__class__):
    def __init__(cls, name, bases, dct):
        super(MetaAztData, cls).__init__(name, bases, dct)
        AztStore.DataCls = cls


# class AztData(DataBase):
class AztData(with_metaclass(MetaAztData, DataBase)):
    lines = ("pre_close", "today_amount", "today_volume", "bid_price", "ask_price", "bid_volume", "ask_volume")
    params = dict(
        qcheck=3.0,
    )

    def __str__(self):
        return "\n".join(
            [
                f"datetime:{num2date(self.l.datetime[0])}",
                f"open:{self.l.open[0]}",
                f"high:{self.l.high[0]}",
                f"low:{self.l.low[0]}",
                f"close:{self.l.close[0]}",
                f"volume:{self.l.volume[0]}",
                f"pre_close:{self.l.pre_close[0]}",
                f"today_amount:{self.l.today_amount[0]}",
                f"today_volume:{self.l.today_volume[0]}",
                f"bid_price:{self.l.bid_price[0]}",
                f"ask_price:{self.l.ask_price[0]}",
                f"bid_volume:{self.l.bid_volume[0]}",
                f"ask_volume:{self.l.ask_volume[0]}",
            ]
        )

    def __init__(self, **kwargs):
        self.aztstore = AztStore(**kwargs)
        self.code = self.p.dataname
        self.qlive = None

    def islive(self):
        return True

    def setenvironment(self, env):
        super(AztData, self).setenvironment(env)
        env.addstore(self.aztstore)

    def start(self):
        super().start()
        self.aztstore.start(data=self)
        # if not self.aztstore.trade_connected():
        #     return
        self.req_data()

    def stop(self):
        super(AztData, self).stop()
        self.cancel_data()
        self.aztstore.stop()

    def haslivedata(self):
        return bool(self.qlive)

    def req_data(self):
        if self.aztstore.quote_connected():
            self.aztstore.subscribe_data(self)
            return True
        return False

    def cancel_data(self):
        if self.aztstore.quote_connected():
            self.aztstore.unsubscribe_data(self)
            return True
        return False

    def _load(self):
        try:
            msg = self.qlive.get(timeout=self._qcheck)
        except queue.Empty:
            return None
        if not msg:
            # print(msg)
            self.put_notification(self.CONNBROKEN)
            return False
        # if self._last
        self.put_notification(self.LIVE, msg)
        return self._load_tick_data(msg.base_data)

    def _load_tick_data(self, tick_data):
        dt = date2num(tick_data.data_time)
        self.l.datetime[0] = dt

        self.l.open[0] = tick_data.open
        self.l.high[0] = tick_data.high
        self.l.low[0] = tick_data.low
        self.l.close[0] = tick_data.last

        self.l.pre_close[0] = tick_data.pre_close
        self.l.today_amount[0] = tick_data.today_amount
        self.l.today_volume[0] = tick_data.today_volume

        self.l.bid_price[0] = tick_data.bid_price[0]  # 买1价
        self.l.ask_price[0] = tick_data.ask_price[0]  # 卖1价
        self.l.bid_volume[0] = tick_data.bid_volume[0]  # 买1量
        self.l.ask_volume[0] = tick_data.ask_volume[0]  # 卖1量

        try:
            last_today_vol = self.l.today_volume[-1]
        except IndexError:
            last_today_vol = 0
        self.l.volume[0] = self.l.today_volume[0] - last_today_vol

        self.l.openinterest[0] = 0

        return True
