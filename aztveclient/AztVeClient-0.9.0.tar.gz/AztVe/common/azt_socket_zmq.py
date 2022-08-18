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
# from zmq.utils.monitor import recv_monitor_message


class Socket:
    def __init__(self):
        self.__context = None
        self.__socket = None
        self.__poller = None
        self.__addr = None
        self.__connected = False
        self.__closed = True
        self.__recv_timeout = None
        self.__moniter = None
        self.__moniter_thread = None

    def connect(self, addr, recv_timeout=None):
        self.__addr = addr
        self.__recv_timeout = recv_timeout
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.DEALER)
        # self.__moniter = self.__socket.get_monitor_socket(
        #     zmq.Event.HANDSHAKE_SUCCEEDED | zmq.Event.DISCONNECTED | zmq.Event.MONITOR_STOPPED)
        # self.__moniter_thread = threading.Thread(target=self.start_moniter)
        # self.__moniter_thread.setDaemon(True)
        # self.__moniter_thread.start()
        self.__poller = zmq.Poller()
        self.__poller.register(self.__socket, zmq.POLLIN)
        self.__socket.connect(addr)

    # def start_moniter(self):
    #     while self.__moniter.poll():
    #         mon_evt = recv_monitor_message(self.__moniter)
    #         event = mon_evt['event']
    #         if event == zmq.Event.HANDSHAKE_SUCCEEDED:
    #             print("已成功连接服务器！")
    #         if event == zmq.Event.MONITOR_STOPPED or event == zmq.Event.DISCONNECTED:
    #             break
    #     self.__moniter.close()

    def set_connected(self, flag=True):
        self.__connected = flag

    def is_connected(self):
        return self.__connected

    def set_closed(self, flag=True):
        self.__closed = flag

    def is_closed(self):
        return self.__closed

    def close(self):
        if not self.__closed:
            self.__closed = True
            # self.__moniter.close()
            try:
                if self.__socket:
                    self.__socket.disconnect(self.__addr)
                    self.__socket.close()
                    if self.__poller:
                        self.__poller.unregister(self.__socket)
                if self.__connected:
                    if self.__context:
                        self.__context.destroy()
                del self.__context
            except Exception as e:
                return e
            finally:
                self.__connected = False

    def send(self, msg):
        if not self.__closed:
            self.__socket.send(msg)

    def recv(self):
        while not self.__closed:
            try:
                events = self.__poller.poll(timeout=self.__recv_timeout)
            except zmq.error.ZMQError as zmqerror:
                if self.__closed:
                    break
                raise zmqerror
            except Exception as e:
                raise e
            if self.__socket in dict(events):
                return self.__socket.recv(flags=zmq.NOBLOCK)
