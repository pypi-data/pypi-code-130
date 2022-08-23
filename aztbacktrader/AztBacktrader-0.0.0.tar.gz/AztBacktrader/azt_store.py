import collections
import copy
import queue
import threading
import time

from .azt_ve_wrapper import AztVe
from backtrader import MetaParams, with_metaclass, Position


class MetaSingleton(MetaParams):
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(MetaSingleton, cls).__call__(*args, **kwargs)

        return cls._singleton


class AztStore(with_metaclass(MetaSingleton, object), AztVe.AztTradeSpi, AztVe.AztQuoteSpi):
    BrokerCls = None  # broker class will autoregister
    DataCls = None  # data class will auto register

    params = dict(
        trade_ip=None,  # 柜台地址
        trade_port=None,  # 柜台端口

        quote_ip=None,  # 行情地址
        quote_port=None,  # 行情端口

        trade_account=None,  # 柜台账户
        trade_passwd=None,  # 柜台账户密码
        # 优先使用账户和密码进行登录，如果用户没有提供，则使用策略编号和校验码进行登录
        trade_stgy_id=None,  # 策略编号
        trade_stgy_check_code=None,  # 策略校验码

        timeout=3,  # 连接超时

        reconnect=0,  # 重连次数 0表示不重试 ≥1表示重试次数 -1表示无限重试直至连接成功
        reconnect_tv=3,  # 重试间隔时间（单位：秒，当reconnect=0时可忽略）
    )

    def __init__(self, **kwargs):

        if not self.p.trade_ip or not self.p.trade_port:
            raise Exception("必须填写柜台服务地址！")

        super(AztStore, self).__init__()

        self._lock_pos = threading.Lock()  # 持仓字典锁

        self._env = None  # 所属cerebro对象
        self.broker = None  # broker instance
        self.datas = list()  # datas that have registered over start
        self.notifs = queue.Queue()

        self.datas_queue_manage = dict()  # 行情数据传输队列管理

        self.acc_value = 0.0  # 账户资金
        self.acc_cash = 0.0  # 账户可用资金

        self.positions = collections.defaultdict(Position)  # 持仓明细

        self._disable_reconnect = False  # 不再重连

        self.trade_api = AztVe.AztTradeApi()  # 柜台服务Api
        self.quote_api = AztVe.AztQuoteApi()  # 行情服务Api

        self.cancel_reqs = dict()  # 撤单请求管理

        self._positions_inited = False
        self._asset_inited = False

    # 为行情对象生成单独的传输队列
    def register_data(self, data):
        q = self.datas_queue_manage.get(data.code, None)
        if not q:
            q = queue.Queue()
            self.datas_queue_manage[data.code] = q
        data.qlive = q

    # 关闭行情对象的传输队列
    def unregister_data(self, data):
        self.datas_queue_manage.pop(data.code, None)

    def data_registed(self, data):
        if data.code in self.datas_queue_manage:
            return True
        return False

    # 将行情数据传输到指定队列中
    def deliver_data(self, code, msg):
        if code in self.datas_queue_manage:
            self.datas_queue_manage[code].put(msg)

    # 生成行情对象
    def getdata(self, *args, **kwargs):
        data = self.DataCls(*args, **kwargs)
        data._store = self
        return data

    # 生成代理对象
    @classmethod
    def getbroker(cls, *args, **kwargs):
        # Returns broker with *args, **kwargs from registered ``BrokerCls``
        broker = cls.BrokerCls(*args, **kwargs)
        broker._store = cls
        return broker

    # 启动store，由行情对象或代理对象调用
    def start(self, data=None, broker=None):
        succeed = self.reconnect(fromstart=True)
        if not succeed:
            raise Exception("柜台服务连接失败！")

        if data is not None:
            self._env = data._env  # 设置cerebro
            self.register_data(data)
            self.datas.append(data)
            return

        elif broker:
            self.broker = broker
            return

        self.init_positions()
        self.init_asset()

    # 判断柜台服务是否已连接
    def trade_connected(self):
        succeed = getattr(self.trade_api, "is_logined", None)
        return False if not succeed else succeed()

    # 判断行情服务是否已连接
    def quote_connected(self):
        closed = getattr(self.quote_api, "is_closed", None)
        return False if not closed else (not closed())

    # 重新连接
    def reconnect(self, fromstart=False, resub=False):
        firstconnect = False
        is_logined = getattr(self.trade_api, "is_logined", None)
        if is_logined:
            if is_logined():
                if resub:
                    self.startdatas()
                return True
        else:
            firstconnect = True

        if self._disable_reconnect:
            return False

        retries = self.p.reconnect
        if retries >= 0:
            retries += firstconnect

        while retries < 0 or retries:
            if not firstconnect:
                time.sleep(self.p.reconnect_tv)

            firstconnect = False

            trade_succeed = self.connect_trade_server()
            if trade_succeed:
                if self.p.quote_ip and self.p.quote_port:
                    if self.connect_quote_server():
                        if not fromstart or resub:
                            self.startdatas()
                        return True

            if retries > 0:
                retries -= 1

        self._disable_reconnect = True
        return False

    def startdatas(self):
        codes = []
        for data in self.datas:
            self.register_data(data)
            codes.append(data.code)
        if codes:
            self.quote_api.Subscribe(codes)

    def stopdatas(self):
        codes = []
        for data in self.datas:
            self.unregister_data(data)
            codes.append(data.code)
        if codes:
            self.quote_api.Unsubscribe(codes)

    def connect_quote_server(self):
        if self.quote_connected():
            return True
        error = self.quote_api.Start(self.p.quote_ip, self.p.quote_port, self)
        if not error:
            return True
        return False

    def connect_trade_server(self):
        if self.trade_connected():
            return True
        error = self.trade_api.Start(self.p.trade_ip, self.p.trade_port, self, self.p.timeout)
        if not error:
            account = self.p.trade_account
            passwd = self.p.trade_passwd
            if not account or not passwd:
                stgy_id = self.p.trade_stgy_id
                stgy_check_code = self.p.trade_stgy_check_code
                if not stgy_id or not stgy_check_code:
                    return False
                ret_query_account_info = self.trade_api.QueryAccountInfo(stgy_id, stgy_check_code, sync=True,
                                                                         timeout=self.p.timeout)
                if not ret_query_account_info:
                    return False
                account = ret_query_account_info.account
                passwd = ret_query_account_info.passwd
            ret_login = self.trade_api.Login(account, passwd, True, self.p.timeout)
            if ret_login and ret_login.ret_code == AztVe.KLoginReCode_LoginSucc:
                return True
        return False

    def stop(self):
        is_logined = getattr(self.trade_api, "is_logined", None)

        if is_logined and is_logined():
            self.trade_api.Logout()
        else:
            self.trade_api.Stop()
        self.quote_api.Stop()

    level_log, level_warning, level_error = range(3)
    type_exchange, type_quote, type_cancelfailed = range(3)

    def put_notification(self, msg, *args, **kwargs):
        self.notifs.put((msg, args, kwargs))

    def get_notifications(self):
        self.notifs.put(None)
        return [x for x in iter(self.notifs.get, None)]

    def subscribe_data(self, data):
        # if self.data_registed(data):
        #     return
        self.register_data(data)
        self.quote_api.Subscribe(data.code)
        # if ret_subscribe and not ret_subscribe.error:
        #     if data.code in ret_subscribe.exchange_securitys:
        #         return True
        # return False

    def unsubscribe_data(self, data):
        if not self.data_registed(data):
            return
        self.unregister_data(data)
        self.quote_api.Unsubscribe(data.code)
        # ret_unsubscribe = self.quote_api.Subscribe(data.code)
        # if ret_unsubscribe and not ret_unsubscribe.error:
        #     if data.code in ret_unsubscribe.exchange_securitys:
        #         self.unregister_data(data)
        #         return True
        # return False

    def onSubscribe(self, msg):
        if msg.succeed:
            pass

    def onUnSubscribe(self, msg):
        pass

    def onDepthMarketData(self, data):
        code = f"{data.base_data.market}.{data.base_data.code}"
        self.deliver_data(code, data)

    def init_positions(self):
        if self._positions_inited:
            return
        if self.trade_connected():
            ret_positions = self.trade_api.QueryPositions(sync=True, timeout=self.p.timeout)
            if not ret_positions:
                if self.reconnect(fromstart=True):
                    self.init_positions()
                raise Exception("无法连接柜台服务！")

            for posit in ret_positions.positions:
                self.positions[f"{posit.market}.{posit.code}"].update(posit.total_qty, posit.open_avg_price)
            self._positions_inited = True

    # 更新持仓信息请求
    def update_positions(self, code: str = None):
        if self.trade_connected():
            market_, code_ = code.split(".") if code else (None, None)
            self.trade_api.QueryPositions(market_, code_)

    def onQueryPositions(self, msg):
        with self._lock_pos:
            for posit in msg.positions:
                code = f"{posit.market}.{posit.code}"
                self.positions[code].update(posit.total_qty, posit.open_avg_price)

    def getposition(self, code, clone=False):
        with self._lock_pos:
            if clone:
                return copy.copy(self.positions[code])
            return self.positions[code]

    def init_asset(self):
        if self._asset_inited:
            return
        if self.trade_connected():
            ret_asset = self.trade_api.QueryAsset(sync=True, timeout=self.p.timeout)
            if not ret_asset:
                if self.reconnect(fromstart=True):
                    self.init_asset()
                raise Exception("无法连接柜台服务！")
            self.acc_value = ret_asset.total_amount
            self.acc_cash = ret_asset.available_amount
            self._asset_inited = True

    def update_asset(self):
        if self.trade_connected():
            self.trade_api.QueryAsset()

    def onQueryAsset(self, msg):
        self.acc_cash = msg.available_amount
        if msg.total_amount > self.acc_value:
            self.acc_value = msg.total_amount

    def get_acc_value(self):
        return self.acc_value

    def get_acc_cash(self):
        return self.acc_cash

    def buy(self, order):
        market_, code_ = order.data.code.split(".")
        azt_order = self.trade_api.Buy(market_, code_, order.size, order_type=order.azt_order_type,
                                       order_price=order.price)
        order.azt_client_ref = azt_order.client_ref
        order.azt_order = azt_order
        return order

    def sell(self, order):
        market_, code_ = order.data.code.split(".")
        azt_order = self.trade_api.Sell(market_, code_, order.size, order_type=order.azt_order_type,
                                        order_price=order.price)
        order.azt_client_ref = azt_order.client_ref
        order.azt_order = azt_order
        return order

    # 如果委托尚未被柜台接收（至少要已报），则无法取消
    def cancel(self, order):
        req = self.trade_api.Cancel(order.azt_order_id)
        self.cancel_reqs[req.client_ref] = (order, req)
        return req

    def tradeConnectionBroken(self, err):
        pass

    def quoteConnectionBroken(self, err):
        pass

    def connectionBroken(self, *args):
        if len(args) == 0:
            if self.p.reconnect != 0 and not self.trade_connected():
                self.put_notification(self.level_warning, self.type_exchange,
                                      f"柜台服务 - {self.p.exchange_addr} - 连接中断！正在尝试重连...")
                succeed = self.reconnect()
                if succeed:
                    self.put_notification(self.level_log, self.type_exchange, f"柜台服务 - {self.p.exchange_addr} - 已重新连接！")
                    return
                self.put_notification(self.level_error, self.type_exchange, f"柜台服务 - {self.p.exchange_addr} - 连接失败！")
                return
            self.put_notification(self.level_error, self.type_exchange, f"柜台服务 - {self.p.exchange_addr} - 连接中断！")
        else:
            msg = args[0]
            self.put_notification(self.level_error, self.type_quote, msg)

    # 3 委托成交回报接口
    def onOrderReport(self, msg):
        self.broker.update_order_report(msg)

    def onTradeReport(self, msg):
        self.broker.update_trade_report(msg)
        self.update_asset()
        # self.update_position()

    def onCancelOrderReject(self, msg):
        client_id = msg.client_ref
        tuple_cancel_req = self.cancel_reqs.get(client_id, None)
        if not tuple_cancel_req:
            return

        order, cancel_req = tuple_cancel_req
        order.owner.notify_store(self.level_warning, self.type_cancelfailed,
                                 self._cancel_fail_reason[msg.reject_reason],
                                 cancel_req)

    _cancel_fail_reason = {
        AztVe.KCxRejReasonType_TooLateCancel: "委托订单已无法撤销",
        AztVe.KCxRejReasonType_UnknowOrder: "找不到委托订单",
        AztVe.KCxRejReasonType_Broker: "撤销失败",
        AztVe.KCxRejReasonType_PendingCancel: "委托正在撤销中，请勿重复撤销",
        AztVe.KCxRejReasonType_Duplicate: "撤销操作重复",
        AztVe.KCxRejReasonType_Other: "撤销失败，原因未知"
    }
