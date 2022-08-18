#  =============================================================================
#  GNU Lesser General Public License (LGPL)
#
#  Copyright (c) 2022 Qujamlee from www.aztquant.com
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  =============================================================================

from ._trade_api_wrapper import *


class AztTradeApi(VeApiWrapper):
    __account = None

    # 初始化
    def Start(self, server_addr: str, spi=None, hb_times: int = 3, hb_interval: int = 5, recv_timeout: int = None):
        if spi:
            if isinstance(spi, type):
                spi = spi()
            if getattr(self.spi, "api", None) is None:
                setattr(self.spi, "api", self)
        return self._start(server_addr, spi, hb_times, hb_interval, recv_timeout)

    # 登录
    def Login(self, account: str, passwd: str, sync: bool = False, timeout: int = None):
        self.__account = account
        login_req = trade_api_struct.LoginReq(account=account, passwd=passwd)
        return self._userLoginReq(login_req, sync, timeout)

    # 登出
    def Logout(self):
        logout_req = trade_api_struct.LogoutReq(account=self.__account)
        return self._userLogoutReq(logout_req)

    def Stop(self):
        return self._stop()

    # 查询账户信息
    def QueryAccountInfo(self, strategy_id: str = None, strategy_check_code: str = None, account: str = None,
                         passwd: str = None, sync: bool = False, timeout: int = None):
        if not strategy_id and not strategy_check_code:
            if not account and not passwd:
                raise common.ArgsError("参数必须填写strategy_id和strategy_check_code（查询账户所有信息）或者account和passwd（查询账户状态）！")
            account_info_req = trade_api_struct.UserInfoQryReq(account=account, passwd=passwd)
        else:
            account_info_req = trade_api_struct.UserInfoQryReq(
                strategy_id=strategy_id,
                strategy_check_code=strategy_check_code
            )
        return self._userInfoQryReq(account_info_req, sync, timeout)

    # 账户入金
    def DepositAsset(self, amount: float, sync: bool = False, timeout: int = None):
        accdeposit_req = trade_api_struct.AccDepositReq(account=self.__account, amount=amount)
        return self._accDepositReq(accdeposit_req, sync, timeout)

    # 查询账户资产信息
    def QueryAsset(self, sync: bool = False, timeout: int = None):
        trade_req = trade_api_struct.TradingAccQryReq(account=self.__account)
        return self._tradingAccQryReq(trade_req, sync, timeout)

    def QueryHistoryAsset(self, date: datetime.datetime = None, sync: bool = False, timeout: int = None):
        historyasset_req = trade_api_struct.QryHisAccReq(account=self.__account, settlement_date=date)
        return self._queryHistoryAccReq(historyasset_req, sync, timeout)

    def QueryHistoryDeposit(self, date: datetime.datetime = None, sync: bool = False, timeout: int = None):
        historydeposit_req = trade_api_struct.QryHisDepositReq(account=self.__account, settlement_date=date)
        return self._queryHistoryDepositReq(historydeposit_req, sync, timeout)

    # 查询订单信息
    def QueryOrders(self, market: str = None, code: str = None, client_ref: str = None, order_id: str = None,
                    unfinished: bool = False, sync: bool = False, timeout: int = None):
        order_req = trade_api_struct.QueryOrdersReq(account=self.__account, market=market, code=code, order_id=order_id,
                                                    unfinished=unfinished, client_ref=client_ref)
        return self._queryOrdersReq(order_req, sync, timeout)

    # 查询交易信息
    def QueryTrades(self, market: str = None, code: str = None, order_id: str = None, trade_id: str = None,
                    sync: bool = False, timeout: int = None):
        trade_req = trade_api_struct.QueryTradesReq(account=self.__account, market=market, code=code, order_id=order_id,
                                                    trade_id=trade_id)
        return self._queryTradesReq(trade_req, sync, timeout)

    # 查询持仓信息
    def QueryPositions(self, market: str = None, code: str = None, sync: bool = False, timeout: int = None):
        position_req = trade_api_struct.QueryPositionsReq(account=self.__account, market=market, code=code)
        return self._queryPositionsReq(position_req, sync, timeout)

    # 查询历史委托信息
    def QueryHistoryOrders(self, market: str = None, code: str = None, start_time: datetime.datetime = None,
                           end_time: datetime.datetime = None, sync: bool = False, timeout: int = None):
        historyorders_req = trade_api_struct.QueryHistoryOrdersReq(account=self.__account, market=market, code=code,
                                                                   start_time=start_time, end_time=end_time)
        return self._queryHistoryOrdersReq(historyorders_req, sync, timeout)

    # 查询历史交易信息
    def QueryHistoryTrades(self, market: str = None, code: str = None, start_time: datetime.datetime = None,
                           end_time: datetime.datetime = None, sync: bool = False, timeout: int = None):
        historytrades_req = trade_api_struct.QueryHistoryTradesReq(account=self.__account, market=market, code=code,
                                                                   start_time=start_time, end_time=end_time)
        return self._queryHistoryTradesReq(historytrades_req, sync, timeout)

    def _insert_order(self, market: str, code: str, order_type: int, order_side: int, effect: int,
                      order_price: float, order_qty: int, discretion_price: float):
        order_req = trade_api_struct.PlaceOrder(
            account=self.__account,
            market=market,
            code=code,
            order_type=order_type,
            business_type=Enum.KBusinessType_NORMAL,
            order_side=order_side,
            effect=effect,
            order_price=order_price,
            order_qty=order_qty,
            discretion_price=discretion_price
        )
        return self._placeOrder(order_req)

    # 买入委托
    def Buy(self, market: str, code: str,
            order_qty: int = 100,  # 默认买入1手(100股)
            order_type: int = Enum.KOrderType_Market,  # 默认市价委托
            effect: int = Enum.KPositionEffect_Open,  # 默认多仓委托,股票委托不用关注
            order_price: float = None,  # 委托限价,适用于限价单,保留两位小数
            discretion_price: float = None  # 市价转限价后委托限价,适用于市价转限价委托,保留两位小数
            ):
        return self._insert_order(market, code, order_type, Enum.KOrderDirection_Buy, effect, order_price,
                                  order_qty, discretion_price)

    # 卖出委托
    def Sell(self, market: str, code: str,
             order_qty: int = 100,  # 默认卖出1手(100股)
             order_type: int = Enum.KOrderType_Market,  # 默认市价委托
             effect: int = Enum.KPositionEffect_Close,  # 默认空仓委托,股票委托不用关注
             order_price: float = None,  # 委托限价,适用于限价单,保留两位小数
             discretion_price: float = None  # 市价转限价后委托限价,适用于市价转限价委托,保留两位小数
             ):
        return self._insert_order(market, code, order_type, Enum.KOrderDirection_Sell, effect, order_price,
                                  order_qty, discretion_price)

    # 撤单委托
    def Cancel(self, order_id: str):
        order_req = trade_api_struct.CancelOrder(account=self.__account, org_order_id=order_id)
        return self._cancelOrder(order_req)

    def Join(self, timeout: int = None):
        self._join(timeout=timeout)
