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

#  =============================================================================
#  GNU Lesser General Public License (LGPL)
#
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
from AztVe.structs import trade_api_struct
from ._trade_api_base import *

_AllowOrderTimeSHSE_SZSE = (
    datetime.time(9, 30, 0), datetime.time(11, 30, 0),
    datetime.time(13, 0), datetime.time(20, 0),
)


class VeApiWrapper(VeApiBase):
    def __sync_mode_wrapper(self, req, sync=False, timeout=None, sid=None, rid=None, once=False):
        if sync:
            return self._get_result(rid, timeout, once, self._send_unitmsg,req, sid)
        self._send_unitmsg(req, sid)

    def _registerReq(self, req: trade_api_struct.RegisterReq, timeout=None):
        return self.__sync_mode_wrapper(req.__py2proto__(), True, timeout,
                                        Enum.KVexchangeMsgID_RegisterReq, Enum.KVexchangeMsgID_RegisterAck)

    # ------ LoginReq ------
    def _userLoginReq(self, req: trade_api_struct.LoginReq, sync=False, timeout=None):
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout,
                                        Enum.KVexchangeMsgID_LoginReq, Enum.KVexchangeMsgID_LoginAck)

    # ------ LogoutReq ------
    def _userLogoutReq(self, req: trade_api_struct.LogoutReq):
        # self._verify_logined()
        if self._logined:
            self._send_unitmsg(req.__py2proto__(), Enum.KVexchangeMsgID_LogoutReq)
        return self._stop()

    # ------ UserInfoQryReq ------
    def _userInfoQryReq(self, req: trade_api_struct.UserInfoQryReq, sync=False, timeout=None):
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KVexchangeMsgID_UserInfoQryReq,
                                        Enum.KVexchangeMsgID_UserInfoQryAck)

    # ------ AccDepositReq ------
    def _accDepositReq(self, req: trade_api_struct.AccDepositReq, sync=False, timeout=None):
        req.client_ref = common.make_new_str_id()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_AccDepositReq,
                                        Enum.KTradeReqType_AccDepositAck)

    # ------ TradingAccQryReq ------
    def _tradingAccQryReq(self, req: trade_api_struct.TradingAccQryReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_TradingAccQryReq,
                                        Enum.KTradeReqType_TradingAccQryAck)

    # ------ QueryOrdersReq ------
    def _queryOrdersReq(self, req: trade_api_struct.QueryOrdersReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KQueryOrdersReq, Enum.KQueryOrdersAck)

    # ------ QueryTradesReq ------
    def _queryTradesReq(self, req: trade_api_struct.QueryTradesReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KQueryTradesReq, Enum.KQueryTradesAck)

    # ------ QueryPositionsReq ------
    def _queryPositionsReq(self, req: trade_api_struct.QueryPositionsReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KQueryPositionsReq,
                                        Enum.KQueryPositionsAck)

    # ------ QueryHistoryOrdersReq ------
    def _queryHistoryOrdersReq(self, req: trade_api_struct.QueryHistoryOrdersReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KQueryHistoryOrdersReq,
                                        Enum.KQueryHistoryOrdersAck)

    # ------ QueryHistoryTradesReq ------
    def _queryHistoryTradesReq(self, req: trade_api_struct.QueryHistoryTradesReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KQueryHistoryTradesReq,
                                        Enum.KQueryHistoryTradesAck)

    def _queryHistoryAccReq(self, req: trade_api_struct.QryHisAccReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_QryHisAccReq,
                                        Enum.KTradeReqType_QryHisAccAck)

    def _queryHistoryDepositReq(self, req: trade_api_struct.QryHisDepositReq, sync=False, timeout=None):
        self._verify_logined()
        return self.__sync_mode_wrapper(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_QryHisDepositReq,
                                        Enum.KTradeReqType_QryHisDepositAck)

    # ------ PlaceOrder ------
    def _placeOrder(self, req: trade_api_struct.PlaceOrder):
        self._verify_logined()
        now = datetime.datetime.now()
        now_time = now.time()
        if _AllowOrderTimeSHSE_SZSE[0] <= now_time <= _AllowOrderTimeSHSE_SZSE[1] or \
                _AllowOrderTimeSHSE_SZSE[2] <= now_time <= _AllowOrderTimeSHSE_SZSE[3]:
            req.client_ref = common.make_new_str_id()
            req.sender_user = self._sender_user
            req.send_time = now
            self._send_unitmsg(req.__py2proto__(), Enum.KTradeReqType_PlaceOrder)
            return req
        else:
            raise common.NonTradingTimeError

    # ------ CancelOrder ------
    def _cancelOrder(self, req: trade_api_struct.CancelOrder):
        self._verify_logined()
        req.client_ref = common.make_new_str_id()
        req.sender_user = self._sender_user
        req.send_time = datetime.datetime.now()
        self._send_unitmsg(req.__py2proto__(), Enum.KTradeReqType_CancelOrder)
        return req
