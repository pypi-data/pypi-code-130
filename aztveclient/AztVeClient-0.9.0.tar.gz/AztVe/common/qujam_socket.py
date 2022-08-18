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

import socket
import threading

from .azt_errors import *
from .azt_buffer import *


class QujamSocket:
    def __init__(self, **kwargs):
        self.p_tcp_recv_buflen = kwargs.get("tcp_recv_buflen", 65536)
        self.p_udp_recv_buflen = kwargs.get("udp_recv_buflen", 2048)

        self.m_tcp_socket = None
        self.m_udp_socket = None

        self.m_tcp_addr = None
        self.m_udp_addr = None
        self.m_closed = True

        self.m_tcp_recv_buffer = BufferQueue()
        self.m_tcp_recv_policy = DefalutRecvPolicy()
        self.m_tcp_send_policy = DefaultSendPolicy()

        self.m_tcp_recv_cb = self.default_recv_func
        self.m_udp_recv_cb = self.default_recv_func

        self.m_tcp_recv_err = self.default_recv_func
        self.m_udp_recv_err = self.default_recv_func

        self.m_thread_pool = []
        self.m_thread_signals = []
        self.m_main_thread = None

    def default_recv_func(self, *args, **kwargs):
        pass

    def connect_tcp(self, ip: str, port: int, timeout=None):
        self.m_tcp_addr = (ip, port)
        self.m_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.m_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if timeout is not None:
            self.m_tcp_socket.settimeout(timeout)
        try:
            self.m_tcp_socket.connect(self.m_tcp_addr)
        except TimeoutError:
            return ConnectedFailed("服务连接超时")
        except ConnectionRefusedError:
            return ConnectedFailed("服务连接被拒")

        if self.m_closed:
            self.m_closed = False

        t = self.make_loop_thread(
            fn=self.m_tcp_socket.recv,
            fargs=(self.p_tcp_recv_buflen,),
            ret_cb=self.tcp_recv,
            err_cb=self.tcp_recv_err,
            finish_exc=OSError,
        )
        if not self.m_main_thread:
            self.m_main_thread = t

    def connect_udp(self, ip: str, port: int):
        self.m_udp_addr = (ip, port)
        self.m_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.m_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.m_udp_socket.connect(self.m_udp_addr)
        if self.m_closed:
            self.m_closed = False

        t = self.make_loop_thread(
            fn=self.m_udp_socket.recvfrom,
            fargs=(self.p_udp_recv_buflen,),
            ret_cb=self.udp_recv,
            err_cb=self.udp_recv_err,
            finish_exc=OSError,
        )
        if not self.m_main_thread:
            self.m_main_thread = t

    # 发送函数 =============================================================================
    def send_tcp(self, data: bytes):
        if not self.m_closed:
            data = self.m_tcp_send_policy(data)
            self.m_tcp_socket.send(data)

    def send_udp(self, data: bytes):
        if not self.m_closed:
            self.m_udp_socket.sendto(data, self.m_udp_addr)

    # socket是否关闭 =======================================================================
    def is_closed(self):
        return self.m_closed

    def close(self):
        if not self.m_closed:
            self.m_closed = True
        for ev in self.m_thread_signals:
            if not ev.is_set():
                ev.set()
        if self.m_tcp_socket:
            self.m_tcp_socket.shutdown(socket.SHUT_RDWR)
            self.m_tcp_socket.close()
            self.m_tcp_socket = None
        if self.m_udp_socket:
            self.m_udp_socket.shutdown(socket.SHUT_RDWR)
            self.m_udp_socket.close()
            self.m_udp_socket = None

    # 设置函数
    def set_tcp_recv_cb(self, fn):
        self.m_tcp_recv_cb = fn

    def set_udp_recv_cb(self, fn):
        self.m_udp_recv_cb = fn

    def set_tcp_recv_err(self, fn):
        self.m_tcp_recv_err = fn

    def set_udp_recv_err(self, fn):
        self.m_udp_recv_err = fn

    def set_tcp_recv_policy(self, policycls, *args, **kwargs):
        self.m_tcp_recv_policy = policycls(*args, **kwargs)

    def set_tcp_send_policy(self, policycls, *args, **kwargs):
        self.m_tcp_send_policy = policycls(*args, **kwargs)

    # 生成循环线程
    def make_loop_thread(self, fn, fargs=(), fkwargs=None, ret_cb=None, err_cb=None, btime=None, ptime=None,
                         finish_exc=None):
        if not finish_exc:
            finish_exc = []
        elif finish_exc.__class__ is not list:
            finish_exc = [finish_exc]
        if fkwargs is None:
            fkwargs = {}
        if ret_cb is None:
            def defalut_ret_cb(*args):
                pass

            ret_cb = defalut_ret_cb

        if err_cb is None:
            def defalut_err_cb(err):
                raise err

            err_cb = defalut_err_cb
        thread_signal = threading.Event()

        def _sleep_time(st):
            if st is None:
                def _stime():
                    pass
            else:
                def _stime():
                    thread_signal.wait(st)
            return _stime

        fn_btime = _sleep_time(btime)
        fn_ptime = _sleep_time(ptime)

        def thread_func():
            while not self.m_closed:
                fn_btime()
                if self.m_closed:
                    break
                try:
                    ret = fn(*fargs, **fkwargs)
                    if self.m_closed:
                        break
                    ret_cb(ret)
                except Exception as err:
                    if err.__class__ in finish_exc:
                        break
                    err_cb(err)
                    break
                fn_ptime()

        _t = threading.Thread(target=thread_func)
        _t.setDaemon(True)
        _t.start()
        self.m_thread_pool.append(_t)
        if not btime or not ptime:
            self.m_thread_signals.append(thread_signal)
        return _t

    # tcp消息接收
    def tcp_recv(self, data: bytes):
        if not len(data):
            self.close()
            raise ConnectedBroken("服务器已停止运行")
        self.m_tcp_recv_buffer.enqueue(data)
        data_msgs = self.m_tcp_recv_policy(self.m_tcp_recv_buffer)
        if data_msgs is None:
            return
        for msg in data_msgs:
            self.m_tcp_recv_cb(msg)

    # tcp消息接收错误回调
    def tcp_recv_err(self, err: Exception):
        self.m_tcp_recv_err(err)

    # udp消息接收
    def udp_recv(self, data):
        self.m_udp_recv_cb(data[0])

    # udp消息接收错误回调
    def udp_recv_err(self, err: Exception):
        self.m_udp_recv_err(err)

    def join(self, timeout=None):
        if timeout is not None:
            self.m_main_thread.join(timeout)
            for t in self.m_thread_pool[1:]:
                t.join(0)
            return
        for t in self.m_thread_pool:
            t.join()
