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
class AztQuoteSpi:
    api = None  # AztQuoteApi实例引用

    # 订阅行情回报，msg为QuoteRegisterRsp实例
    def onSubscribe(self, msg):
        pass

    # 取消订阅行情回报，msg为QuoteRegisterRsp实例
    def onUnSubscribe(self, msg):
        pass

    # 深度行情回报，msg为StockQuoteData实例
    def onDepthMarketData(self, msg):
        pass

    # 连接中断回报，err为可rasie的Exception错误
    def quoteConnectionBroken(self, err):
        """用户可以在连接中断后再次调用start函数重新尝试连接行情服务"""
