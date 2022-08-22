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
import queue
from typing import Optional

from AztVe.protos import MsgType_pb2 as MsgTypeProto, Trade_Message_pb2 as MsgProto, EnumType_pb2 as Enum
from AztVe.protos import UnitedMessage_pb2 as UnitMsgProto
from AztVe.structs import trade_spi_struct, trade_api_struct
from AztVe import common
from .trade_spi import AztTradeSpi

logger = common.logger
_func_switch = common.QujamFuncSwitch.set_func_switch
_AllowOrderTimeSHSE_SZSE = (
    datetime.time(9, 30, 0), datetime.time(11, 30, 0),
    datetime.time(13, 0), datetime.time(20, 0),
)


class VeApiBase(common.AztApiObject):
    def __init__(self):
        # 设置默认的spi
        self.spi: Optional[AztTradeSpi, None] = None
        # 设置zmq
        self.__socket: Optional[common.QujamSocketZmq, None] = None
        # 设置信号
        self._logined = False
        # 同步管道
        self.__req_queue_manage = dict()
        # 设置账户标识
        self._sender_user = None
        # 设置switch
        self._switch = common.QujamFuncSwitch("vespi")
        self._switch.set_cls(self)

    # wrapper api ------------------------------------------------------------------------------------------------------
    def _start(self, ip, port, spi=None, timeout=None):
        # 设置spi
        self.spi = common.DefaultSpi(spi) if spi else AztTradeSpi()
        # 设置zmq套接字
        self.__socket = common.QujamSocketZmq()
        self.__socket.set_recv_cb(self.__recv_handle)
        self.__socket.set_recv_err(self.__err_handle)
        logger.log(f"准备连接模拟柜台......")
        err = self.__socket.connect_router(ip, port, timeout)
        if err:
            return err
        setattr(self, "is_closed", self._is_closed)
        logger.log(f"已成功连接模拟柜台 - {ip}:{port}")

    def _join(self, timeout=None):
        if self.__socket:
            self.__socket.join(timeout)

    def _stop(self):
        if self.__socket:
            self.__socket.close()
        self.__req_queue_manage.clear()
        self._logined = False

    def _is_closed(self):
        if self.__socket:
            return self.__socket.is_closed()
        return True

    def _is_logined(self):
        return self._logined

    def _verify_logined(self):
        if not self._logined:
            self._stop()
            raise common.NotLoginedError("尚未登录！")

    # queue_manage -----------------------------------------------------------------------------------------------------
    def __queue_subscribe(self, msg_id):
        if msg_id not in self.__req_queue_manage:
            self.__req_queue_manage[msg_id] = queue.Queue()
        return self.__req_queue_manage[msg_id]

    def __queue_unsubscribe(self, msg_id):
        self.__req_queue_manage.pop(msg_id, None)

    def __queue_put(self, msg_id, msg):
        if msg_id in self.__req_queue_manage:
            self.__req_queue_manage[msg_id].put(msg, block=False)

    def _get_result(self, msg_id, timeout=None, once=False, exec_func=None, *args, **kwargs):
        q_ = self.__queue_subscribe(msg_id)
        if exec_func is not None:
            exec_func(*args, **kwargs)
        try:
            return q_.get(timeout=timeout)
        except queue.Empty:
            pass
        finally:
            if once:
                self.__queue_unsubscribe(msg_id)
        return None

    # heart_beat -------------------------------------------------------------------------------------------------------
    def _set_heart_beat(self, hb_times: int = 3, hb_tv: int = 5):
        unit_msg = UnitMsgProto.UnitedMessage(msg_type=MsgTypeProto.KMsgType_Exchange_Req,
                                              msg_id=Enum.KVexchangeMsgID_HeartBeatReq)
        unit_msg.msg_body.Pack(MsgProto.HeartBeatReq())
        self.__socket.set_heart_beat(unit_msg.SerializeToString(), hb_times, hb_tv)

    def _send_unitmsg(self, msg, msg_id, msg_type=MsgTypeProto.KMsgType_Exchange_Req):
        # logger.debug(f"发送消息：{msg_type} - {msg_id}\n{msg}")
        unit_msg = UnitMsgProto.UnitedMessage(msg_type=msg_type, msg_id=msg_id)
        unit_msg.msg_body.Pack(msg)
        self.__socket.send(unit_msg.SerializeToString())

    # recv handle ----------------------------------------------------------------------------------------------------
    def __recv_handle(self, msg: bytes):
        # logger.debug(f"收到消息大小:{len(msg)}")
        unit_msg = UnitMsgProto.UnitedMessage()
        unit_msg.ParseFromString(msg)
        try:
            unit_msg.ParseFromString(msg)
        except MsgProto._message.DecodeError:
            logger.debug("反序列化失败,发生数据丢包")
            return
        # logger.debug(f"收到消息：{unit_msg.msg_type} - {unit_msg.msg_id}")
        if unit_msg.msg_type != MsgTypeProto.KMsgType_Exchange_Rsp:
            return

        try:
            self._switch[unit_msg.msg_id](unit_msg)
        except KeyError:
            logger.warning("Unkown recv msg msg_id!")

    def __err_handle(self, err: Exception):
        self.spi.tradeConnectionBroken(err)

    # recv case --------------------------------------------------------------------------------------------------------
    @_func_switch("vespi", Enum.KVexchangeMsgID_RegisterAck)
    def _case_register(self, unit_msg):
        msg = MsgProto.RegisterAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.RegisterAck.__proto2py__(msg)
        self.__queue_put(Enum.KVexchangeMsgID_RegisterAck, cbmsg)

    @_func_switch("vespi", Enum.KVexchangeMsgID_LoginAck)
    def _case_login(self, unit_msg):
        self._logined = True
        if not hasattr(self, "is_logined"):
            setattr(self, "is_logined", self._is_logined)

        msg = MsgProto.LoginAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.LoginAck.__proto2py__(msg)
        self.spi.onLogin(cbmsg)
        self.__queue_put(Enum.KVexchangeMsgID_LoginAck, cbmsg)

    @_func_switch("vespi", Enum.KVexchangeMsgID_UserInfoQryAck)
    def _case_user_info(self, unit_msg):
        msg = MsgProto.UserRegisterInfo()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.UserRegisterInfo.__proto2py__(msg)
        self.spi.onQueryAccountInfo(cbmsg)
        self.__queue_put(Enum.KVexchangeMsgID_UserInfoQryAck, cbmsg)

    @_func_switch("vespi", Enum.KTradeReqType_AccDepositAck)
    def _case_acc_deposit(self, unit_msg):
        msg = MsgProto.AccDepositAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.AccDepositAck.__proto2py__(msg)
        self.spi.onDepositAsset(cbmsg)
        self.__queue_put(Enum.KTradeReqType_AccDepositAck, cbmsg)

    @_func_switch("vespi", Enum.KTradeReqType_TradingAccQryAck)
    def _case_qurey_asset(self, unit_msg):
        msg = MsgProto.AccMargin()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.AccMargin.__proto2py__(msg)
        self.spi.onQueryAsset(cbmsg)
        self.__queue_put(Enum.KTradeReqType_TradingAccQryAck, cbmsg)

    @_func_switch("vespi", Enum.KQueryOrdersAck)
    def _case_query_orders(self, unit_msg):
        msg = MsgProto.QueryOrdersAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QueryOrdersAck.__proto2py__(msg)
        self.spi.onQueryOrders(cbmsg)
        self.__queue_put(Enum.KQueryOrdersAck, cbmsg)

    @_func_switch("vespi", Enum.KQueryTradesAck)
    def _case_query_trades(self, unit_msg):
        msg = MsgProto.QueryTradesAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QueryTradesAck.__proto2py__(msg)
        self.spi.onQueryTrades(cbmsg)
        self.__queue_put(Enum.KQueryTradesAck, cbmsg)

    @_func_switch("vespi", Enum.KQueryPositionsAck)
    def _case_query_position(self, unit_msg):
        msg = MsgProto.QueryPositionsAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QueryPositionsAck.__proto2py__(msg)
        self.spi.onQueryPositions(cbmsg)
        self.__queue_put(Enum.KQueryPositionsAck, cbmsg)

    @_func_switch("vespi", Enum.KQueryHistoryOrdersAck)
    def _case_query_history_orders(self, unit_msg):
        msg = MsgProto.QueryOrdersAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QueryOrdersAck.__proto2py__(msg)
        self.spi.onQueryHistoryOrders(cbmsg)
        self.__queue_put(Enum.KQueryHistoryOrdersAck, cbmsg)

    @_func_switch("vespi", Enum.KQueryHistoryTradesAck)
    def _case_query_history_trades(self, unit_msg):
        msg = MsgProto.QueryTradesAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QueryTradesAck.__proto2py__(msg)
        self.spi.onQueryHistoryTrades(cbmsg)
        self.__queue_put(Enum.KQueryHistoryTradesAck, cbmsg)

    @_func_switch("vespi", Enum.KTradeReqType_QryHisAccAck)
    def _case_query_history_asset(self, unit_msg):
        msg = MsgProto.QryHisAccAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QryHisAccAck.__proto2py__(msg)
        self.spi.onQueryHistoryAsset(cbmsg)
        self.__queue_put(Enum.KTradeReqType_QryHisAccAck, cbmsg)

    @_func_switch("vespi", Enum.KTradeReqType_QryHisDepositAck)
    def _case_query_history_deposit(self, unit_msg):
        msg = MsgProto.QryHisDepositAck()
        unit_msg.msg_body.Unpack(msg)
        cbmsg = trade_spi_struct.QryHisDepositAck.__proto2py__(msg)
        self.spi.onQueryHistoryDeposit(cbmsg)
        self.__queue_put(Enum.KTradeReqType_QryHisDepositAck, cbmsg)

    @_func_switch("vespi", Enum.KTradeRspType_OrdStatusReport)
    def _case_order_report(self, unit_msg):
        msg = MsgProto.OrdReport()
        unit_msg.msg_body.Unpack(msg)
        self.spi.onOrderReport(trade_spi_struct.OrdReport.__proto2py__(msg))

    @_func_switch("vespi", Enum.KTradeReqType_ExecReport)
    def _case_trade_report(self, unit_msg):
        msg = MsgProto.TradeReport()
        unit_msg.msg_body.Unpack(msg)
        self.spi.onTradeReport(trade_spi_struct.TradeReport.__proto2py__(msg))

    @_func_switch("vespi", Enum.KTradeReqType_RejectCancelReport)
    def _case_cancel_order_reject(self, unit_msg):
        msg = MsgProto.CancelOrderReject()
        unit_msg.msg_body.Unpack(msg)
        self.spi.onCancelOrderReject(trade_spi_struct.CancelOrderReject.__proto2py__(msg))

    @_func_switch("vespi", Enum.KVexchangeMsgID_HeartBeatAck)
    def _case_heart_beat(self, unit_msg):
        self.__socket.keep_heart_beat()

    def _sync_return(self, req, sync=False, timeout=None, sid=None, rid=None, once=False):
        if sync:
            return self._get_result(rid, timeout, once, self._send_unitmsg, req, sid)
        self._send_unitmsg(req, sid)

    def _registerReq(self, req: trade_api_struct.RegisterReq, timeout=None):
        return self._sync_return(req.__py2proto__(), True, timeout,
                                 Enum.KVexchangeMsgID_RegisterReq, Enum.KVexchangeMsgID_RegisterAck)

    # ERegisterRet - 注册完成情况返回码
    # KRegisterRet_Unknown         = 0  # 未知错误
    # KRegisterRet_Success         = 1  # 注册成功
    # KRegisterRet_ReRegister      = 2  # 重复注册
    # KRegisterRet_InvalidStrategy = 3  # 无效或非法 strategy_id

    # ### 2.2.8 RegisterAck - 注册响应
    # | 属性 | 类型 | 说明 |
    # | --- | --- | --- |
    # | registe_info | UserRegisterInfo | 账户注册回复信息 |
    # | regist_code | int | 注册完成情况返回码，具体含义与取值参见枚举常量`ERegisterRet` |

    # ------ LoginReq ------
    def _userLoginReq(self, req: trade_api_struct.LoginReq, sync=False, timeout=None):
        return self._sync_return(req.__py2proto__(), sync, timeout,
                                 Enum.KVexchangeMsgID_LoginReq, Enum.KVexchangeMsgID_LoginAck)

    # ------ LogoutReq ------
    def _userLogoutReq(self, req: trade_api_struct.LogoutReq):
        # self._verify_logined()
        if self._logined:
            self._send_unitmsg(req.__py2proto__(), Enum.KVexchangeMsgID_LogoutReq)
        return self._stop()

    # ------ UserInfoQryReq ------
    def _userInfoQryReq(self, req: trade_api_struct.UserInfoQryReq, sync=False, timeout=None):
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KVexchangeMsgID_UserInfoQryReq,
                                 Enum.KVexchangeMsgID_UserInfoQryAck)

    # ------ AccDepositReq ------
    def _accDepositReq(self, req: trade_api_struct.AccDepositReq, sync=False, timeout=None):
        req.client_ref = common.make_new_str_id()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_AccDepositReq,
                                 Enum.KTradeReqType_AccDepositAck)

    # ------ TradingAccQryReq ------
    def _tradingAccQryReq(self, req: trade_api_struct.TradingAccQryReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_TradingAccQryReq,
                                 Enum.KTradeReqType_TradingAccQryAck)

    # ------ QueryOrdersReq ------
    def _queryOrdersReq(self, req: trade_api_struct.QueryOrdersReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KQueryOrdersReq, Enum.KQueryOrdersAck)

    # ------ QueryTradesReq ------
    def _queryTradesReq(self, req: trade_api_struct.QueryTradesReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KQueryTradesReq, Enum.KQueryTradesAck)

    # ------ QueryPositionsReq ------
    def _queryPositionsReq(self, req: trade_api_struct.QueryPositionsReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KQueryPositionsReq,
                                 Enum.KQueryPositionsAck)

    # ------ QueryHistoryOrdersReq ------
    def _queryHistoryOrdersReq(self, req: trade_api_struct.QueryHistoryOrdersReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KQueryHistoryOrdersReq,
                                 Enum.KQueryHistoryOrdersAck)

    # ------ QueryHistoryTradesReq ------
    def _queryHistoryTradesReq(self, req: trade_api_struct.QueryHistoryTradesReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KQueryHistoryTradesReq,
                                 Enum.KQueryHistoryTradesAck)

    def _queryHistoryAccReq(self, req: trade_api_struct.QryHisAccReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_QryHisAccReq,
                                 Enum.KTradeReqType_QryHisAccAck)

    def _queryHistoryDepositReq(self, req: trade_api_struct.QryHisDepositReq, sync=False, timeout=None):
        self._verify_logined()
        return self._sync_return(req.__py2proto__(), sync, timeout, Enum.KTradeReqType_QryHisDepositReq,
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
