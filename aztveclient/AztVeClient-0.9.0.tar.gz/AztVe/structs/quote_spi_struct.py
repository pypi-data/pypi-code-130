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

import datetime

from ..common.azt_dataclass import aztdataclass
from ..protos import Quote_Message_pb2 as MsgProto


# @aztdataclass(MsgProto.QuoteStockExtra, price_dec="price_decimal_place", amount_dec="amount_decimal_place",
#               adj_price=["ma_bid_price", "ma_ask_price", "ma_bond_bid_price", "ma_bond_ask_price", "iopv",
#                          "warrant_lower_price", "warrant_upper_price"],
#               adj_amount=["yield_to_maturity", "etf_buy_money", "etf_sell_money", "cancel_buy_money",
#                           "cancel_sell_money"],
#               )
# class QuoteStockExtra:
#     total_bid_qty: int = None  # 委托买入总量(SH, SZ) - 使用QuoteBaseMsg中数量小数位
#     total_ask_qty: int = None  # 委托卖出总量(SH, SZ)
#     ma_bid_price: float = None  # 加权平均委买价格(SH, SZ) - 使用QuoteBaseMsg中价格小数位
#     ma_ask_price: float = None  # 加权平均委卖价格(SH, SZ) - 使用QuoteBaseMsg中价格小数位
#     ma_bond_bid_price: float = None  # 债券加权平均委买价格(SH) - 使用QuoteBaseMsg中价格小数位
#     ma_bond_ask_price: float = None  # 债券加权平均委卖价格(SH) - 使用QuoteBaseMsg中价格小数位
#     yield_to_maturity: float = None  # 债券到期收益率(SH)
#     iopv: float = None  # 基金实时参考净值(SH, SZ)
#     etf_buy_count: int = None  # ETF申购笔数(SH)
#     etf_sell_count: int = None  # ETF赎回笔数(SH)
#     etf_buy_qty: int = None  # ETF申购数量(SH)
#     etf_buy_money: float = None  # ETF申购金额(SH)
#     etf_sell_qty: int = None  # ETF赎回数量(SH)
#     etf_sell_money: float = None  # ETF赎回金额(SH)
#     total_warrant_exec_qty: int = None  # 权证执行的总数量(SH)
#     warrant_lower_price: float = None  # 权证跌停价格（元）(SH)
#     warrant_upper_price: float = None  # 权证涨停价格（元）(SH)
#     cancel_buy_count: int = None  # 买入撤单笔数(SH)
#     cancel_sell_count: int = None  # 卖出撤单笔数(SH)
#     cancel_buy_qty: int = None  # 买入撤单数量(SH) - 使用QuoteBaseMsg中数量小数位
#     cancel_sell_qty: int = None  # 卖出撤单数量(SH) - 使用QuoteBaseMsg中数量小数位
#     cancel_buy_money: float = None  # 买入撤单金额(SH)
#     cancel_sell_money: float = None  # 卖出撤单金额(SH)
#     total_buy_count: int = None  # 买入总笔数(SH)
#     total_sell_count: int = None  # 卖出总笔数(SH)
#     duration_after_buy: int = None  # 买入委托成交最大等待时间(SH)
#     duration_after_sell: int = None  # 卖出委托成交最大等待时间(SH)
#     num_bid_orders: int = None  # 买方委托价位数(SH)
#     num_ask_orders: int = None  # 卖方委托价位数(SH)
#     pre_iopv: float = None  # 基金T - 1
#
#
# @aztdataclass(MsgProto.QuoteBaseMsg, price_dec="price_decimal_place", amount_dec="amount_decimal_place",
#               adj_price=["open", "high", "low", "last", "pre_close", "close", "upper_limit", "lower_limit",
#                          "avg_price"],
#               adj_amount=["total_amount"],
#               adj_map_price=["bid_price", "ask_price"],
#               adj_map=["bid_volume", "ask_volume"],
#               adj_time=dict(data_time="%Y%m%d-%H:%M:%S.%f")
#               )
# class QuoteBaseMsg:
#     market: str = None  # 市场
#     code: str = None  # 合约代码
#     security_type: int = None  # 合约类型
#
#     open: float = None  # 开盘价
#     high: float = None  # 最高价
#     low: float = None  # 最低价
#     last: float = None  # 最新价
#     pre_close: float = None  # 昨收盘
#     close: float = None  # 今收盘
#
#     upper_limit: float = None  # 涨停价
#     lower_limit: float = None  # 跌停价
#
#     total_amount: float = None  # 总成交金额（单位元，与交易所一致）
#     last_volume: float = None  # 总成交量  （单位股，与交易所一致）
#     avg_price: float = None  # 当日均价
#     bid_price: {int: float} = None  # 买价 - XTP(十档) - CTP(五档)
#     ask_price: {int: float} = None  # 卖价 - XTP(十档)
#     bid_volume: {int: int} = None  # 买量 - XTP(十档)
#     ask_volume: {int: int} = None  # 卖量 - XTP(十档)
#
#     data_time: datetime.datetime = None  # 时间: YYYYMMDD - HH:MM: SS.sss
#
#
# @aztdataclass(MsgProto.QuoteMsg,
#               adj_any=dict(stock_extra_data=QuoteStockExtra),
#               adj_name=dict(quote_base_msg="qoute_base_msg", stock_extra_data="extra_data"),
#               )
# class QuoteStockMsg:
#     quote_base_msg: QuoteBaseMsg = None
#     stock_extra_data: QuoteStockExtra = None
#
#
# @aztdataclass(MsgProto.QuoteRegisterMsgs,adj_repeat=["exchange_securitys"])
# class QuoteRegisterMsgs:
#     exchange_securitys: [str] = None
#     error = None

@aztdataclass(MsgProto.QuoteBaseData, adj_map=["bid_price", "ask_price", "bid_volume", "ask_volume"],
              adj_time=dict(data_time="%Y-%m-%d %H:%M:%S.%f"))
class QuoteBaseData:
    market: str = None  # 市场
    code: str = None  # 合约代码

    open: float = None  # 开盘价
    high: float = None  # 最高价
    low: float = None  # 最低价
    last: float = None  # 最新价
    pre_close: float = None  # 昨收盘
    close: float = None  # 今收盘

    upper_limit: float = None  # 涨停价
    lower_limit: float = None  # 跌停价

    today_amount: float = None  # 总成交金额（单位元，与交易所一致）
    today_volume: float = None  # 总成交量  （单位股，与交易所一致）
    avg_price: float = None  # 当日均价

    bid_price: {int: float} = None  # 买价 - XTP(十档) - CTP(五档)
    ask_price: {int: float} = None  # 卖价 - XTP(十档)
    bid_volume: {int: int} = None  # 买量 - XTP(十档)
    ask_volume: {int: int} = None  # 卖量 - XTP(十档)

    data_time: datetime.datetime = None  # 时间: YYYY-MM-DD HH:MM:SS.sss


@aztdataclass(MsgProto.QuoteStockExData)
class QuoteStockExData:
    total_bid_qty: int = None  # 委托买入总量(SH, SZ) - 使用QuoteBaseMsg中数量小数位
    total_ask_qty: int = None  # 委托卖出总量(SH, SZ)
    ma_bid_price: float = None  # 加权平均委买价格(SH, SZ) - 使用QuoteBaseMsg中价格小数位
    ma_ask_price: float = None  # 加权平均委卖价格(SH, SZ) - 使用QuoteBaseMsg中价格小数位
    ma_bond_bid_price: float = None  # 债券加权平均委买价格(SH) - 使用QuoteBaseMsg中价格小数位
    ma_bond_ask_price: float = None  # 债券加权平均委卖价格(SH) - 使用QuoteBaseMsg中价格小数位

    yield_to_maturity: float = None  # 债券到期收益率(SH)
    iopv: float = None  # 基金实时参考净值(SH, SZ)

    etf_buy_count: int = None  # ETF申购笔数(SH)
    etf_sell_count: int = None  # ETF赎回笔数(SH)
    etf_buy_qty: int = None  # ETF申购数量(SH)
    etf_buy_money: float = None  # ETF申购金额(SH)
    etf_sell_qty: float = None  # ETF赎回数量(SH)
    etf_sell_money: float = None  # ETF赎回金额(SH)

    total_warrant_exec_qty: float = None  # 权证执行的总数量(SH)
    warrant_lower_price: float = None  # 权证跌停价格（元）(SH)
    warrant_upper_price: float = None  # 权证涨停价格（元）(SH)

    cancel_buy_count: int = None  # 买入撤单笔数(SH)
    cancel_sell_count: int = None  # 卖出撤单笔数(SH)
    cancel_buy_qty: float = None  # 买入撤单数量(SH) - 使用QuoteBaseMsg中数量小数位
    cancel_sell_qty: float = None  # 卖出撤单数量(SH) - 使用QuoteBaseMsg中数量小数位
    cancel_buy_money: float = None  # 买入撤单金额(SH)
    cancel_sell_money: float = None  # 卖出撤单金额(SH)
    total_buy_count: int = None  # 买入总笔数(SH)
    total_sell_count: int = None  # 卖出总笔数(SH)
    duration_after_buy: int = None  # 买入委托成交最大等待时间(SH)
    duration_after_sell: int = None  # 卖出委托成交最大等待时间(SH)
    num_bid_orders: int = None  # 买方委托价位数(SH)
    num_ask_orders: int = None  # 卖方委托价位数(SH)

    pre_iopv: float = None  # 基金T - 1


@aztdataclass(MsgProto.QuoteData, adj_any=dict(extra_data=QuoteStockExData))
class StockQuoteData:
    base_data: QuoteBaseData = None
    extra_data: QuoteStockExData = None


@aztdataclass(MsgProto.QuoteRegisterRsp)
class QuoteRegisterRsp:
    exchange_securitys: str = None
    succeed: bool = None


# @aztdataclass(MsgProto.QuoteRegisterMsg)
# class QuoteRegisterMsg:
#     exchange_securitys: str = None  # 代码行情订阅 exp: SHSE.600259,SZSE.000001(订阅多标的) or SHSE.600259(订阅一个标的)
