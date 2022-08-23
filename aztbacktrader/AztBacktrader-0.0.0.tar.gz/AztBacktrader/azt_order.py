from backtrader import OrderBase
from .azt_ve_wrapper import AztVe


class AztOrder(OrderBase):
    _AztOrderTypes = {
        OrderBase.Market: AztVe.KOrderType_Market,
        OrderBase.Limit: AztVe.KOrderType_Limit,
        OrderBase.Stop: AztVe.KOrderType_Stop,
    }
    _AztOrderTypes_reverse = dict(zip(_AztOrderTypes.values(), _AztOrderTypes.keys()))
    _AztOrderSide = {
        OrderBase.Buy: AztVe.KOrderDirection_Buy,
        OrderBase.Sell: AztVe.KOrderDirection_Sell,
    }
    _AztOrderSide_reverse = dict(zip(_AztOrderSide.values(), _AztOrderSide.keys()))
    azt_order = None

    def __init__(self, buysell=None, **kwargs):
        self.ordtype = buysell
        super(AztOrder, self).__init__()

        self.azt_client_ref = kwargs.get("client_ref", None)  # 客户端生成订单编号
        self.azt_market, self.azt_code = self.data.code.split(".") if self.data else (
            kwargs.get("market", None), kwargs.get("code", None))
        self.azt_order_type = kwargs.get("order_type", None) or self._AztOrderTypes[self.exectype]
        self.azt_order_id = kwargs.get("order_id", None)  # 服务端生成订单编号
        self.azt_order = kwargs.get("azt_order", None)

    @classmethod
    def _from_placeorder(cls, porder):
        buysell = cls._AztOrderSide_reverse[porder.order_side]
        price = porder.order_price
        size = porder.order_qty
        if size > 0 and buysell == OrderBase.Sell:
            size = -size

        return cls(buysell=buysell,
                   client_ref=porder.client_ref,
                   market=porder.market,
                   code=porder.code,
                   order_type=porder.order_type,
                   price=price,
                   size=size,
                   order_id=porder.order_id,
                   azt_order=porder
                   )
