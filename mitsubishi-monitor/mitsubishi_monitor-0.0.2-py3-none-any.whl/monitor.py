"""
The monitor is used for direct connection with equipment such as a robotic arm and PLC with
the aim of obtaining statistical data on energy consumption, movement of monitors, axis load, etc.

This monitor was taken from Mitsubishi's RT Toolbox3 monitoring software and specifically the oscilloscope function.

Each constant in const.py was obtained by intercepting the
communication between the connected computer and the device itself.

TODO For correct function the following steps must be completed:
 1. RT ToolBox3 - set device to online mode
 2. RT ToolBox3 - open oscillograph
 3. RT ToolBox3 - start any monitoring (start button - top left button)
 4. Start your python script -> it  reroutes sending of data to yours computer
"""
import socket
import logging
from .util import Error, WrongIpAddress


class Monitor:
    def __init__(self, ip_addr, port, mfreq, mtype):
        """
        Initialization of monitor.
        :param ip_addr: IP address of device
        :param port: port of device
        :param mfreq: const.MonitorFreq - frequency of data collecting
        :param mtype: const.MonitorType - type of collected data
        """
        self._ip_addr = ip_addr
        self._port = port
        self._mtime = mfreq
        self._mtype = mtype
        self._socket = None
        self.logger = logging.getLogger(__name__)
        try:
            socket.inet_aton(self._ip_addr)     # Check whether IP address is valid
        except socket.error:
            self.logger.warning("IP_ADDR: {} PORT: {},  IP_ADDR is not valid".format(self._ip_addr, self._port))
            raise Error(WrongIpAddress)

    def start_monitor(self):
        """
        Send LLC (IEEE 802.2 - logical link  control) message
        which tells your device to send data at a certain frequency.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.sendto(self._mtype, (self._ip_addr, self._port))

    def receive_data(self):
        """
        Receive UDP (in real-time) / TCP (otherwise) response from your device.
        This response needs to be parsed and this library provides parsing methods in util.py.
        """
        response = self._socket.recv(512)
        print(response)

    def close_socket(self):
        """
        End communication.
        """
        self._socket.close()
