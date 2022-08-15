"""
Mitsubishi-monitor is used to monitor orthogonal and joint position
data of the current position of the robot controller.
"""
import socket
import logging
from .util import Error, WrongIpAddress


class Monitor:
    def __init__(self, ip_addr, port, mtime, mtype):
        self._ip_addr = ip_addr
        self._port = port
        self._mtime = mtime
        self._mtype = mtype
        self._socket = None
        self.logger = logging.getLogger(__name__)
        try:
            socket.inet_aton(self._ip_addr)     # Check whether IP address is valid
        except socket.error:
            self.logger.warning("IP_ADDR: {} PORT: {},  IP_ADDR is not valid".format(self._ip_addr, self._port))
            raise Error(WrongIpAddress)

    def start_monitor(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.sendto(self._mtype, (self._ip_addr, self._port))

    def receive_data(self):
        response = self._socket.recv(512)
        print(response)

    def close_socket(self):
        self._socket.close()
