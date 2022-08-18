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

from .quote_spi import AztQuoteSpi
from AztVe.common import logger, QujamSocket, HeaderSendPolicy, HeaderRecvPolicy
from AztVe import common
from AztVe.protos import Quote_Message_pb2 as MsgProto, UnitedMessage_pb2 as UnitMsgProto
from AztVe.structs import quote_spi_struct


class QuoteApiBase(common.AztApiObject):

    def __init__(self):
        self.__socket = None

        self.spi = AztQuoteSpi()
        self.__req_queue_manage = dict()

        # self._heart_beat_times = 3  # 心跳次数
        # self._heart_beat_count = self._heart_beat_times  # 心跳倒数
        # self._heart_beat_interval = 5  # 心跳间隔时间，5秒
        # self._heart_beat_req = self.__init_heart_beat_req()  # 心跳请求

    # queue manage -----------------------------------------------------------------------------------------------------
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

    # def __heart_beat(self):
    #     while self._heart_beat_count > 0 and not self.__tcp_socket.is_closed():
    #         self._heart_beat_count -= 1
    #         self.__send_heart_beat()
    #         time.sleep(self._heart_beat_interval)
    #     if not self.__tcp_socket.is_closed():
    #         logger.error("与服务器连接已中断！")
    #         err = self._stop()
    #         if err:
    #             raise err
    #         self.spi.quoteConnectionBroken()
    #
    # @staticmethod
    # def __init_heart_beat_req():
    #     unitedmsg = UnitMsgProto.UnitedMessage(msg_type=MsgProto.KQuoteMsgType_HeartBeat)
    #     return unitedmsg.SerializeToString()
    #
    # def __send_heart_beat(self):
    #     self.__tcp_socket.send(self._heart_beat_req)

    @staticmethod
    def __gen_unit_msg(msg, msg_id, msg_type=MsgProto.KQuoteMsgType_Unknown):
        unit_msg = UnitMsgProto.UnitedMessage(msg_type=msg_type, msg_id=msg_id)
        unit_msg.msg_body.Pack(msg)
        return unit_msg.SerializeToString()

    def __tcp_recv_handle(self, msg):
        logger.debug("收到tcp消息,长度:", len(msg))
        # 解析msg
        unitedmsg = UnitMsgProto.UnitedMessage()
        try:
            unitedmsg.ParseFromString(msg)
        except MsgProto._message.DecodeError:
            logger.debug("反序列化失败,发生数据丢包")
            return

        msg_type = unitedmsg.msg_type
        if msg_type == MsgProto.KQuoteMsgType_HeartBeat:
            self._heart_beat_count = self._heart_beat_times
            self.__queue_put(MsgProto.KQuoteMsgType_HeartBeat, True)
        elif msg_type == MsgProto.KQuoteMsgType_TcpConnConfirm:
            tcp_cc = MsgProto.TcpConnectionConfirm()
            unitedmsg.msg_body.Unpack(tcp_cc)
            self.__queue_put(MsgProto.KQuoteMsgType_TcpConnConfirm, tcp_cc)
        elif msg_type == MsgProto.KQuoteMsgType_RealTime:
            msg_id = unitedmsg.msg_id
            if msg_id == MsgProto.KQuoteMsgID_QuoteRegister:  # 订阅回复
                register_rsp = MsgProto.QuoteRegisterRsp()
                unitedmsg.msg_body.Unpack(register_rsp)
                ret = quote_spi_struct.QuoteRegisterRsp.__proto2py__(register_rsp)
                self.spi.onSubscribe(ret)
            elif msg_id == MsgProto.KQuoteMsgID_UnRegister:  # 取消订阅
                unregister = MsgProto.QuoteRegisterRsp()
                unitedmsg.msg_body.Unpack(unregister)
                ret = quote_spi_struct.QuoteRegisterRsp.__proto2py__(unregister)
                self.spi.onUnSubscribe(ret)
            elif msg_id == MsgProto.KQuoteMsgID_QuoteSnapshot:
                data = MsgProto.QuoteData()
                unitedmsg.msg_body.Unpack(data)
                if data.data_type == MsgProto.KMarketDataType_V2_Actual:  # 股票数据
                    ret = quote_spi_struct.StockQuoteData.__proto2py__(data, 2)
                    self.spi.onDepthMarketData(ret)

    def __udp_recv_handle(self, msg):
        logger.debug("收到udp消息长度:", len(msg))
        unitedmsg = UnitMsgProto.UnitedMessage()
        try:
            unitedmsg.ParseFromString(msg)
        except:
            logger.debug("反序列化失败,发生数据丢包")
            return
        if unitedmsg.msg_type != MsgProto.KQuoteMsgType_RealTime or \
                unitedmsg.msg_id != MsgProto.KQuoteMsgID_QuoteSnapshot:
            return
        data = MsgProto.QuoteData()
        unitedmsg.msg_body.Unpack(data)
        if data.data_type == MsgProto.KMarketDataType_V2_Actual:  # 股票数据
            ret = quote_spi_struct.StockQuoteData.__proto2py__(data, 2)
            self.spi.onDepthMarketData(ret)

    def __socket_err_handle(self, err):
        # 与服务端连接发生错误
        self.spi.quoteConnectionBroken(err)
        pass

    def _start(self, ip, port, spi=None, timeout=None, set_heart_beat=False):
        # self.__tcp_socket = TcpSocketCls()
        self.__socket = QujamSocket()

        # 设置接收回调
        self.__socket.set_tcp_recv_cb(self.__tcp_recv_handle)
        # 设置接收错误回调
        self.__socket.set_tcp_recv_err(self.__socket_err_handle)
        # 设置数据处理策略
        self.__socket.set_tcp_recv_policy(HeaderRecvPolicy)
        self.__socket.set_tcp_send_policy(HeaderSendPolicy)

        error = self.__socket.connect_tcp(ip, port, timeout)

        if not error:
            setattr(self, "is_closed", self._is_closed)
            if spi:
                self.spi = common.DefaultSpi(spi)
            # 发送tcp连接确认请求
            tcp_cc = UnitMsgProto.UnitedMessage(msg_type=MsgProto.KQuoteMsgType_TcpConnConfirm)
            tcp_cc_rep = self._get_result(MsgProto.KQuoteMsgType_TcpConnConfirm, 3, True,
                                          self.__socket.send_tcp, tcp_cc.SerializeToString())
            if tcp_cc_rep is None:
                self._stop()
                return common.ConnectedFailed(f"服务器 - {ip}:{port} - 连接失败！")

            if tcp_cc_rep.use_udp:
                self.__socket.set_udp_recv_cb(self.__udp_recv_handle)
                self.__socket.set_udp_recv_err(self.__socket_err_handle)

                self.__socket.connect_udp(ip, tcp_cc_rep.udp_port)

                united_msg = UnitMsgProto.UnitedMessage(msg_type=MsgProto.KQuoteMsgType_UdpConnConfirm)
                udp_cc = MsgProto.UdpConnectionConfirm(tcp_owner=tcp_cc_rep.tcp_owner)
                united_msg.msg_body.Pack(udp_cc)
                self.__socket.send_udp(united_msg.SerializeToString())

                self.__socket.make_loop_thread(self.__socket.send_udp, fargs=(b"1",), btime=10)

            logger.debug(f"已连接行情服务 - {ip}:{port}")

            # if set_heart_beat:
            #     self.__thread_heart_beat = threading.Thread(target=self.__heart_beat)
            #     self.__thread_heart_beat.setDaemon(True)
            #     self.__thread_heart_beat.start()

        return error

    def _is_closed(self):
        return self.__socket.is_closed()

    def _stop(self):
        return self.__socket.close()

    def _join(self, timeout=None):
        self.__socket.join(timeout)

    def _subscribe(self, codes):
        if self.__socket.is_closed():
            raise common.UnconnectedError("尚未连接行情服务器！")

        if isinstance(codes, list):
            codes = ",".join(codes)
        req = MsgProto.QuoteRegisterMsg(exchange_securitys=codes)
        unitedmsg = self.__gen_unit_msg(req, MsgProto.KQuoteMsgID_QuoteRegister, MsgProto.KQuoteMsgType_RealTime)
        return self.__socket.send_tcp(unitedmsg)

    def _unsubscribe(self, codes):
        if self.__socket.is_closed():
            raise common.UnconnectedError("尚未连接行情服务器！")
        if isinstance(codes, list):
            codes = ",".join(codes)
        req = MsgProto.QuoteRegisterMsg(exchange_securitys=codes)
        unitedmsg = self.__gen_unit_msg(req, MsgProto.KQuoteMsgID_UnRegister, MsgProto.KQuoteMsgType_RealTime)
        return self.__socket.send_tcp(unitedmsg)

    # def __sync_mode_wrapper(self, req, sync=False, timeout=None, rid=None, once=False):
    #     if sync:
    #         return self._get_result(rid, timeout, once, self.__socket.send_tcp, req)
    #     self.__socket.send_tcp(req)
