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

class AztTradeSpi:
    api = None  # AztTradeApi实例引用

    # 连接中断回报，一旦被调用，则说明客户端与服务端的连接中断了
    def tradeConnectionBroken(self, err):
        pass

    # 登录回报，msg为LoginAck实例
    def onLogin(self, msg):
        pass

    # 账户入金回报，msg为AccDepositAck实例
    def onDepositAsset(self, msg):
        pass

    # 查询账户信息回报，msg为UserRegisterInfo实例
    def onQueryAccountInfo(self, msg):
        pass

    # 查询账户资产信息回报，msg为AccMargin实例
    def onQueryAsset(self, msg):
        pass

    # 查询委托订单信息回报，msg为QueryOrdersAck实例
    def onQueryOrders(self, msg):
        pass

    # 查询成交信息回报，msg为QueryTradesAck实例
    def onQueryTrades(self, msg):
        pass

    # 查询持仓信息回报，msg为QueryPositionsAck实例
    def onQueryPositions(self, msg):
        pass

    # 查询历史委托信息回报，msg为QueryOrdersAck实例
    def onQueryHistoryOrders(self, msg):
        pass

    # 查询历史成交信息回报，msg为QueryTradesAck实例
    def onQueryHistoryTrades(self, msg):
        pass

    # 委托执行回报，msg为OrdReport实例
    def onOrderReport(self, msg):
        pass

    # 委托成交回报，msg为TradeReport实例
    def onTradeReport(self, msg):
        pass

    # 撤单失败回报，msg为CancelOrderReject实例
    def onCancelOrderReject(self, msg):
        pass

    # 查询账户历史资产信息回报，msg为QryHisAccAck实例
    def onQueryHistoryAsset(self, msg):
        pass

    # 查询历史入金信息回报，msg为QryHisDepositAck实例
    def onQueryHistoryDeposit(self, msg):
        pass
