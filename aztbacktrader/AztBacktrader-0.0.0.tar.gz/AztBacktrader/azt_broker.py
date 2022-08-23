import queue

from .azt_ve_wrapper import AztVe

from backtrader import date2num
from backtrader.broker import MetaBroker, BrokerBase
from .azt_store import AztStore
from .azt_order import AztOrder


class MetaAztBroker(MetaBroker):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        AztStore.BrokerCls = cls


# [2022-07-04 18:13:56] todo 记得恢复元类
# class AztBroker(with_metaclass(MetaAztBroker, BrokerBase)):
class AztBroker(BrokerBase):
    params = dict()

    # 1 生命周期管理 -----------------------------------------------------------------------------------------------------
    # 1.1 初始化
    def __init__(self, **kwargs):
        super().__init__()

        self.aztstore = AztStore(**kwargs)  # 实例化Store

        self.startingcash = self.cash = 0.0
        self.startingvalue = self.value = 0.0

        # self._lock_orders = threading.Lock()  # control access
        self.orders_record = dict()  # orders by client id
        self.orders_record_by_status = dict()

        self._tmp_order_status = dict()  # 委托状态

        # self.executions = dict()  # notified executions
        self.notifs = queue.Queue()  # holds orders which are notified
        # self.tonotify = collections.deque()  # hold oids to be notified

    # 1.2 启动
    def start(self):
        super().start()
        self.aztstore.start(broker=self)  # 调用store的start

        if self.aztstore.trade_connected():
            self.startingcash = self.cash = self.aztstore.get_acc_cash()
            self.startingvalue = self.value = self.aztstore.get_acc_value()
        else:
            self.startingcash = self.cash = 0.0
            self.startingvalue = self.value = 0.0

    # 1.3 迭代
    def next(self):
        self.notifs.put(None)  # mark notificatino boundary

    # 1.4 停止
    def stop(self):
        super(AztBroker, self).stop()
        self.aztstore.stop()

    # 2 提交委托 --------------------------------------------------------------------------------------------------------
    # 2.1 提交
    def submit(self, order):
        order.submit(self)
        self._record_order_by_id(order)
        self._record_order_by_status(order)

    # 2.2 买入
    def buy(self, owner, data,
            size, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0,
            **kwargs):
        order = AztOrder(AztOrder.Buy, owner=owner, data=data,
                         size=size, price=price, pricelimit=plimit,
                         exectype=exectype, valid=valid,
                         tradeid=tradeid, **kwargs)
        order = self.aztstore.buy(order)
        order.addcomminfo(self.getcommissioninfo(data))
        self.submit(order)
        return order

    # 2.3 卖出
    def sell(self, owner, data,
             size, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0,
             **kwargs):
        order = AztOrder(AztOrder.Sell, owner=owner, data=data,
                         size=size, price=price, pricelimit=plimit,
                         exectype=exectype, valid=valid,
                         tradeid=tradeid, **kwargs)
        order.addcomminfo(self.getcommissioninfo(data))
        order = self.aztstore.sell(order)
        self.submit(order)
        return order

    # 2.4 取消委托
    def cancel(self, order):
        o_ = self._get_order_by_id(order.azt_client_ref)
        if not o_ or o_.status in self._couldnot_cancel:
            return

        return self.aztstore.cancel(order)

    # 3 查询方法 --------------------------------------------------------------------------------------------------------
    # 3.1 查询可用资金
    def getcash(self):
        self.cash = self.aztstore.get_acc_cash()
        return self.cash

    # 3.2 查询账户资金
    def getvalue(self, datas=None):
        self.value = self.aztstore.get_acc_value()
        return self.value

    # 3.3 查询指定持仓
    def getposition(self, data, clone=True):
        return self.aztstore.getposition(data.code, clone)

    # 3.4 查询所有持仓
    def getpositions(self):
        return self.aztstore.positions

    positions = property(getpositions)

    # 3.5 查询委托状态
    def orderstatus(self, order):
        ordr = self._get_order_by_id(order.azt_client_ref)
        return ordr.status if ordr else order.status

    # 3.6 查询指定状态委托
    def statusorder(self, status):
        if status in self.orders_record_by_status:
            ids = self.orders_record_by_status[status]
            return [self.orders_record[idx] for idx in ids if idx in self.orders_record]
        return []

    # def getcommissioninfo(self, data):
    #     pass  # [2022-07-06 11:02:57] todo 待后期完善
    #     return AztCommInfo()

    # 4 通知管理 --------------------------------------------------------------------------------------------------------
    # 4.1 添加订单通知
    def notify(self, order):
        self.notifs.put(order.clone())

    # 4.2 取出通知内容
    def get_notification(self):
        try:
            return self.notifs.get(False)
        except queue.Empty:
            pass
        return None

    # 5 store回调处理 ---------------------------------------------------------------------------------------------------
    # 5.1 委托订单处理回报
    def update_order_report(self, msg):
        AztVe.debug(f"收到委托回报：\n", msg)
        place_order = msg.place_order
        order = self._get_order_by_id(place_order.client_ref)
        if not order:
            order = AztOrder._from_placeorder(place_order)

        status_msg = msg.status_msg
        order_status = status_msg.order_status

        order.azt_order = place_order

        # 1 订单有成交
        if order_status in [AztVe.KOrderStatus_PartiallyFilled, AztVe.KOrderStatus_Filled,
                            AztVe.KOrderStatus_DoneForDay]:
            self._tmp_order_status[place_order.client_ref] = order_status
            return  # 直接返回，在update_exec_report中处理
        # 2 委托已报
        elif order_status == AztVe.KOrderStatus_New:  # 1 已报
            if order.status == order.Accepted:
                return  # 过滤重复信息
            self._change_order_status(order, order.accept, self)
        # 3 委托已撤销
        elif order_status in [AztVe.KOrderStatus_Canceled, AztVe.KOrderStatus_Stopped]:  # 已撤
            if order.status == order.Canceled:
                return
            self._change_order_status(order, order.cancel)
        # 4 委托被拒绝
        elif order_status == AztVe.KOrderStatus_Rejected:
            if order.status == order.Rejected:
                return
            self._change_order_status(order, order.reject, self)
        # 5 委托已到期
        elif order_status == AztVe.KOrderStatus_Expired:
            if order.status == order.Expired:
                return
            self._change_order_status(order, order.expire)

        # 通知订单变化
        self.notify(order)

    # 5.2 委托订单成交回报
    def update_trade_report(self, msg):
        if msg.exec_type not in [AztVe.KExecType_DoneForDay, AztVe.KExecType_Trade]:
            # 只处理成交的信息
            return
        c_orderid = msg.client_ref
        order = self._get_order_by_id(c_orderid)
        order_status = self._tmp_order_status.get(c_orderid, None)
        if not order or not order_status:
            return

        position = self.getposition(order.data, clone=False)
        pprice_orig = position.price

        size = msg.traded_qty if order.azt_order.order_side == AztVe.KOrderDirection_Buy else -msg.traded_qty
        price = msg.traded_price
        psize, pprice, opened, closed = position.update(size, price)

        comm = msg.fee
        closedcomm = comm * closed / size
        openedcomm = comm - closedcomm

        closedvalue = abs(closed) * pprice_orig
        openedvalue = abs(opened) * price

        pnl = closed * (pprice_orig - price)
        dt = date2num(msg.transact_time)
        margin = None
        order.execute(dt, size, price, closed, closedvalue, closedcomm, opened, openedvalue, openedcomm, margin, pnl,
                      psize, pprice)
        if order_status in [AztVe.KOrderStatus_Filled, AztVe.KOrderStatus_DoneForDay]:
            self._change_order_status(order, order.completed)
            self._tmp_order_status.pop(c_orderid)
        else:
            self._change_order_status(order, order.partial)

        self.notify(order)

    # # 6 数据启停管理 -----------------------------------------------------------------------------------------------------
    # def startdatas(self):
    #     self.aztstore.startdatas()
    #
    # def stopdatas(self):
    #     self.aztstore.stopdatas()

    # 方法实现过程 -------------------------------------------------------------------------------------------------------
    # 根据状态记录订单
    def _record_order_by_status(self, order):
        _status = order.status
        if _status not in self.orders_record_by_status:
            self.orders_record_by_status[_status] = set()
        _client_id = order.azt_client_ref
        self.orders_record_by_status[_status].add(_client_id)

    # 根据状态剔除订单记录
    def _remove_order_by_status(self, order):
        _status = order.status
        if _status not in self.orders_record_by_status:
            return
        _client_id = order.azt_client_ref
        self.orders_record_by_status[_status].discard(_client_id)

    def _change_order_status(self, order, orderfunc, *args, **kwargs):
        self._remove_order_by_status(order)
        orderfunc(*args, **kwargs)
        self._record_order_by_status(order)

    # 根据客户端委托编号记录委托
    def _record_order_by_id(self, order):
        self.orders_record[order.azt_client_ref] = order

    # 根据客户端委托编号获取指令
    def _get_order_by_id(self, client_id):
        return self.orders_record.get(client_id, None)

    _couldnot_cancel = [AztOrder.Created, AztOrder.Canceled, AztOrder.Completed, AztOrder.Expired, AztOrder.Rejected,
                        AztOrder.Margin]

    def add_order_history(self, orders, notify=False):
        pass

    def set_fund_history(self, fund):
        pass
