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
import zmq
from zmq.utils.monitor import recv_monitor_message
import threading
from .azt_errors import *
from .qujam_heart_beat import QujamHeartBeat


class QujamSocketZmq:
    def __init__(self):
        self.m_ctx = None
        self.m_dealer_socket = None
        self.m_socket_poll = None
        self.m_socket_moniter = None
        self.m_zmq_addr = None
        self.m_closed = True

        self.m_event_connect = None

        self.m_zmq_recv_cb = self.default_recv_func
        self.m_zmq_recv_err = self.default_recv_func

        self.m_thread_pool = []
        self.m_thread_signals = []
        self.m_main_thread = None

        self.m_heart_beat = None

    def default_recv_func(self, *args, **kwargs):
        pass

    def connect_router(self, ip: str, port: int, timeout: int = None, mt=False):
        self.m_zmq_addr = (ip, port)
        self.m_ctx = zmq.Context()
        self.m_dealer_socket = self.m_ctx.socket(zmq.DEALER)
        self.m_socket_moniter = self.m_dealer_socket.get_monitor_socket(
            zmq.Event.HANDSHAKE_SUCCEEDED | zmq.Event.DISCONNECTED | zmq.Event.MONITOR_STOPPED
        )
        # self.m_socket_moniter = self.m_dealer_socket.get_monitor_socket()
        self.m_socket_poll = zmq.Poller()
        self.m_socket_poll.register(self.m_dealer_socket, zmq.POLLIN)
        self.m_event_connect = threading.Event()
        if self.m_closed:
            self.m_closed = False

        self.make_loop_thread(
            fn=self._socket_moniter,
            err_cb=self.zmq_recv_err,
            finish_exc=CloseSocketZmq,
        )
        self.m_dealer_socket.connect(f"tcp://{ip}:{port}")
        if not self.m_event_connect.wait(timeout):
            self.m_closed = True
            return ConnectedFailed("连接失败")

        t = self.make_loop_thread(
            fn=self._socket_recv,
            ret_cb=self.zmq_recv,
            err_cb=self.zmq_recv_err,
            finish_exc=CloseSocketZmq,
        )
        if mt or not self.m_main_thread:
            self.m_main_thread = t

    def _socket_moniter(self):
        if self.m_socket_moniter.poll():
            event = recv_monitor_message(self.m_socket_moniter)['event']
            if event == zmq.Event.HANDSHAKE_SUCCEEDED:
                self.m_event_connect.set()
            elif event == zmq.Event.DISCONNECTED:
                self.close()
                raise ConnectedBroken("与服务端连接中断")
            elif event == zmq.Event.MONITOR_STOPPED:
                self.close()
                raise CloseSocketZmq()

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
            # nt = threading.currentThread()
            # print(f"线程{nt.getName()}启动,执行:", fn)
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
            # print(f"线程{nt.getName()}结束")

        _t = threading.Thread(target=thread_func)
        _t.setDaemon(True)
        _t.start()
        self.m_thread_pool.append(_t)
        if not btime or not ptime:
            self.m_thread_signals.append(thread_signal)
        return _t

    def close(self):
        if not self.m_closed:
            self.m_closed = True
            for ev in self.m_thread_signals:
                if not ev.is_set():
                    ev.set()
            if self.m_dealer_socket:
                self.m_socket_poll.unregister(self.m_dealer_socket)
                self.m_dealer_socket.disconnect(f"tcp://{self.m_zmq_addr[0]}:{self.m_zmq_addr[1]}")
                self.m_dealer_socket.disable_monitor()
                self.m_dealer_socket.close()
                self.m_socket_moniter.close()
                self.m_socket_moniter = None
                self.m_dealer_socket = None
                self.m_socket_poll = None
            if self.m_ctx:
                self.m_ctx.term()
                self.m_ctx = None

    def send(self, data: bytes):
        if not self.m_closed:
            self.m_dealer_socket.send(data)

    def _socket_recv(self):
        try:
            if self.m_socket_poll.poll():
                return self.m_dealer_socket.recv(flags=zmq.NOBLOCK)
        except zmq.error.ZMQError:
            if self.m_closed:
                raise CloseSocketZmq()
            raise ConnectedBroken("连接中断")
        except Exception as e:
            raise e

    def zmq_recv(self, msg: bytes):
        self.m_zmq_recv_cb(msg)

    def zmq_recv_err(self, err):
        self.m_zmq_recv_err(err)

    def set_recv_cb(self, fn):
        self.m_zmq_recv_cb = fn

    def set_recv_err(self, fn):
        self.m_zmq_recv_err = fn

    def set_heart_beat(self, hb_data: bytes = None, hb_t: int = 3, hb_tv: int = 5):
        self.m_heart_beat = QujamHeartBeat(hb_data, hb_t)
        self.make_loop_thread(
            fn=self._heart_beat,
            err_cb=self.zmq_recv_err,
            btime=hb_tv,
            finish_exc=CloseSocketZmq,
        )

    def keep_heart_beat(self):
        self.m_heart_beat.keep()

    def _heart_beat(self):
        if self.m_closed:
            raise CloseSocketZmq()
        if self.m_heart_beat.alive():
            data = self.m_heart_beat.data()
            if data:
                self.send(data)
            self.m_heart_beat.cost()
            return
        raise ConnectedBroken("与服务端连接中断")

    def join(self, timeout=None):
        if timeout is not None and self.m_main_thread:
            self.m_main_thread.join(timeout)
            return
        for t in self.m_thread_pool:
            t.join()

    def is_closed(self):
        return self.m_closed
