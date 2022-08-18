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

import queue
import threading
import time

from AztVe.protos import MsgType_pb2 as MsgTypeProto, Trade_Message_pb2 as MsgProto, EnumType_pb2 as Enum
from AztVe.protos import UnitedMessage_pb2 as UnitMsgProto
from AztVe.structs import trade_spi_struct
from AztVe import common
from .trade_spi import AztTradeSpi

logger = common.logger


class VeApiBase(common.AztApiObject):
    def __init__(self):
        # 服务器地址
        self._server_addr = None
        # 设置默认的spi
        self.spi = AztTradeSpi()
        # 设置zmq
        self.__socket = common.ZmqSocketCls()
        # 设置信号
        self._logined = False
        # 同步管道
        self.__req_queue_manage = dict()
        # 设置账户标识
        self._sender_user = None
        # 心跳
        self._heart_beat_times = 3  # 心跳次数
        self._heart_beat_count = self._heart_beat_times  # 心跳倒数
        self._heart_beat_interval = 5  # 心跳间隔时间，5秒
        self._heart_beat_req = self.__init_heart_beat_req()  # 心跳请求
        # zmq.poller检查超时时间
        self.__recv_timeout = None

    # wrapper api ------------------------------------------------------------------------------------------------------
    def _start(self, server_addr, spi=None, hb_times = None, hb_interval = None,
               recv_timeout = None):
        # 设置服务器地址
        if not server_addr.startswith("tcp"):
            server_addr = f"tcp://{server_addr}"
        self._server_addr = server_addr
        # 设置spi
        if spi:
            self.spi = common.DefaultSpi(spi)

        if hb_times is not None:
            self._heart_beat_times = hb_times
            self._heart_beat_count = hb_times
        if hb_interval is not None and hb_interval >= 3:
            self._heart_beat_interval = hb_interval
        if recv_timeout is not None:
            self.__recv_timeout = recv_timeout * 1000  # 单位：毫秒

        # 连接服务器
        logger.log(f"开始连接服务器 - {self._server_addr}")
        self.__socket.connect(self._server_addr, self.__recv_timeout)

        # 设置接收线程
        self.__socket.set_closed(False)
        self.__thread_report_recv = threading.Thread(target=self.__report_recv)
        self.__thread_report_recv.setDaemon(True)
        self.__thread_report_recv.start()

        if not hasattr(self, "is_closed"):
            setattr(self, "is_closed", self._is_closed)

        # 发送心跳请求，确认服务器已连接
        ret_heart_beat = self._get_result(Enum.KVexchangeMsgID_HeartBeatAck, self._heart_beat_interval, True,
                                          self.__send_heart_beat)
        if ret_heart_beat is None:
            self._stop()
            return common.ConnectedFailed(f"服务器 - {self._server_addr} - 连接失败！")

        self.__socket.set_connected(True)
        # self._connected = True

        if not hasattr(self, "is_connected"):
            setattr(self, "is_connected", self._is_connected)

        # logger.log(f"已成功连接服务器 - {self._server_addr}!")
        # 开启心跳线程
        self.__thread_heart_beat = threading.Thread(target=self.__heart_beat)
        self.__thread_heart_beat.setDaemon(True)
        self.__thread_heart_beat.start()

    def _join(self, timeout= None):
        if hasattr(self, "__thread_report_recv"):
            self.__thread_report_recv.join(timeout=timeout)

    def _stop(self):
        err = self.__socket.close()
        if err:
            return err
        self.__req_queue_manage.clear()
        self._logined = False

    def _is_closed(self):
        return self.__socket.is_closed()

    def _is_connected(self):
        return self.__socket.is_connected()

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
    @staticmethod
    def __init_heart_beat_req():
        unit_msg = UnitMsgProto.UnitedMessage()
        unit_msg.msg_type = MsgTypeProto.KMsgType_Exchange_Req
        unit_msg.msg_id = Enum.KVexchangeMsgID_HeartBeatReq
        unit_msg.msg_body.Pack(MsgProto.HeartBeatReq())
        return unit_msg

    def __send_heart_beat(self):
        self.__socket.send(self._heart_beat_req.SerializeToString())

    def __heart_beat(self):
        logger.log("心跳线程启动成功！")
        time.sleep(self._heart_beat_interval)

        while self._heart_beat_count > 0 and not self.__socket.is_closed():
            self._heart_beat_count -= 1
            self.__send_heart_beat()
            time.sleep(self._heart_beat_interval)
        if not self.__socket.is_closed():
            logger.error("与服务器连接已中断！")
            self._stop()
            self.spi.tradeConnectionBroken(common.ConnectedBroken("服务连接中断"))

    # zmq --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __gen_unit_msg(msg, msg_id, msg_type=MsgTypeProto.KMsgType_Exchange_Req):
        # logger.debug(f"发送请求：{msg_type} - {msg_id}")
        # logger.debug(f"发送内容：\n{msg}")
        unit_msg = UnitMsgProto.UnitedMessage(msg_type=msg_type, msg_id=msg_id)
        unit_msg.msg_body.Pack(msg)
        return unit_msg.SerializeToString()

    def _send_unitmsg(self, msg, msg_id):
        self.__socket.send(self.__gen_unit_msg(msg, msg_id))

    # report handle ----------------------------------------------------------------------------------------------------

    def __report_recv(self):
        while True:
            recv_msg = self.__socket.recv()
            if recv_msg is None:
                break
            unit_msg = UnitMsgProto.UnitedMessage()
            unit_msg.ParseFromString(recv_msg)
            self.__report_handel(unit_msg)

    def __report_handel(self, unit_msg):
        # logger.debug(f"收到消息：{unit_msg.msg_type} - {unit_msg.msg_id}\n{unit_msg}")

        if unit_msg.msg_type != MsgTypeProto.KMsgType_Exchange_Rsp:
            return

        if unit_msg.msg_id == Enum.KVexchangeMsgID_RegisterAck:
            msg = MsgProto.RegisterAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = trade_spi_struct.RegisterAck.__proto2py__(msg)
            self.__queue_put(Enum.KVexchangeMsgID_RegisterAck, cbmsg)

        elif unit_msg.msg_id == Enum.KVexchangeMsgID_LoginAck:
            self._logined = True
            if not hasattr(self, "is_logined"):
                setattr(self, "is_logined", self._is_logined)

            msg = MsgProto.LoginAck()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.LoginAck.__proto2py__(msg)
            self.spi.onLogin(cbmsg)
            self.__queue_put(Enum.KVexchangeMsgID_LoginAck, cbmsg)

        elif unit_msg.msg_id == Enum.KVexchangeMsgID_UserInfoQryAck:
            msg = MsgProto.UserRegisterInfo()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.UserRegisterInfo.__proto2py__(msg)
            self.spi.onQueryAccountInfo(cbmsg)
            self.__queue_put(Enum.KVexchangeMsgID_UserInfoQryAck, cbmsg)

        elif unit_msg.msg_id == Enum.KTradeReqType_AccDepositAck:
            msg = MsgProto.AccDepositAck()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.AccDepositAck.__proto2py__(msg)
            self.spi.onDepositAsset(cbmsg)
            self.__queue_put(Enum.KTradeReqType_AccDepositAck, cbmsg)

        elif unit_msg.msg_id == Enum.KTradeReqType_TradingAccQryAck:
            msg = MsgProto.AccMargin()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.AccMargin.__proto2py__(msg)
            self.spi.onQueryAsset(cbmsg)
            self.__queue_put(Enum.KTradeReqType_TradingAccQryAck, cbmsg)

        elif unit_msg.msg_id == Enum.KQueryOrdersAck:
            msg = MsgProto.QueryOrdersAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = trade_spi_struct.QueryOrdersAck.__proto2py__(msg)
            self.spi.onQueryOrders(cbmsg)
            self.__queue_put(Enum.KQueryOrdersAck, cbmsg)

        elif unit_msg.msg_id == Enum.KQueryTradesAck:
            msg = MsgProto.QueryTradesAck()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.QueryTradesAck.__proto2py__(msg)
            self.spi.onQueryTrades(cbmsg)
            self.__queue_put(Enum.KQueryTradesAck, cbmsg)

        elif unit_msg.msg_id == Enum.KQueryPositionsAck:
            msg = MsgProto.QueryPositionsAck()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            cbmsg = trade_spi_struct.QueryPositionsAck.__proto2py__(msg)
            self.spi.onQueryPositions(cbmsg)
            self.__queue_put(Enum.KQueryPositionsAck, cbmsg)

        elif unit_msg.msg_id == Enum.KQueryHistoryOrdersAck:
            msg = MsgProto.QueryOrdersAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = trade_spi_struct.QueryOrdersAck.__proto2py__(msg)
            self.spi.onQueryHistoryOrders(cbmsg)
            self.__queue_put(Enum.KQueryHistoryOrdersAck, cbmsg)

        elif unit_msg.msg_id == Enum.KQueryHistoryTradesAck:
            msg = MsgProto.QueryTradesAck()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(unit_msg, msg)
            cbmsg = trade_spi_struct.QueryTradesAck.__proto2py__(msg)
            self.spi.onQueryHistoryTrades(cbmsg)
            self.__queue_put(Enum.KQueryHistoryTradesAck, cbmsg)

        elif unit_msg.msg_id == Enum.KTradeReqType_QryHisAccAck:
            msg = MsgProto.QryHisAccAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = trade_spi_struct.QryHisAccAck.__proto2py__(msg)
            self.spi.onQueryHistoryAsset(cbmsg)
            self.__queue_put(Enum.KTradeReqType_QryHisAccAck, cbmsg)

        elif unit_msg.msg_id == Enum.KTradeReqType_QryHisDepositAck:
            msg = MsgProto.QryHisDepositAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = trade_spi_struct.QryHisDepositAck.__proto2py__(msg)
            self.spi.onQueryHistoryDeposit(cbmsg)
            self.__queue_put(Enum.KTradeReqType_QryHisDepositAck, cbmsg)

        # ----------------------------------------------------------
        elif unit_msg.msg_id == Enum.KTradeRspType_OrdStatusReport:
            msg = MsgProto.OrdReport()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            self.spi.onOrderReport(trade_spi_struct.OrdReport.__proto2py__(msg))

        elif unit_msg.msg_id == Enum.KTradeReqType_ExecReport:
            msg = MsgProto.TradeReport()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            self.spi.onTradeReport(trade_spi_struct.TradeReport.__proto2py__(msg))

        elif unit_msg.msg_id == Enum.KTradeReqType_RejectCancelReport:
            msg = MsgProto.CancelOrderReject()
            unit_msg.msg_body.Unpack(msg)
            # logger.debug(msg)
            self.spi.onCancelOrderReject(trade_spi_struct.CancelOrderReject.__proto2py__(msg))

        elif unit_msg.msg_id == Enum.KVexchangeMsgID_HeartBeatAck:
            self._heart_beat_count = self._heart_beat_times
            self.__queue_put(Enum.KVexchangeMsgID_HeartBeatAck, True)
        else:
            logger.warning("Unkown recv msg msg_id!")
