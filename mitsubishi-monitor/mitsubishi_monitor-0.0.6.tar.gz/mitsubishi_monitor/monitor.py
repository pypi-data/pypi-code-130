"""
The monitor is used for direct connection with equipment such as a robotic arm and PLC with
the aim of obtaining statistical data on energy consumption, movement of monitors, axis load, etc.

This monitor was taken from Mitsubishi's RT Toolbox3 monitoring software and specifically the oscilloscope function.

Each constant in const.py was obtained by intercepting the
communication between the connected computer and the device itself.
"""
import socket
import logging
from .util import Error, WrongIpAddress


class Monitor:
    def __init__(self, ip_addr, port, datatype):
        """
        Initialization of monitor.
        :param ip_addr: IP address of device
        :param port: port of device
        :param datatype: const.MonitorType - type of collected data
        """
        print('------------------------------ TEST printU-------------------------------------')
        self._ip_addr = ip_addr
        self._port = port
        self._datatype = datatype
        self._socket = None
        self.logger = logging.getLogger(__name__)
        try:
            socket.inet_aton(self._ip_addr)  # Check whether IP address is valid
        except socket.error:
            self.logger.warning("IP_ADDR: {} PORT: {},  IP_ADDR is not valid".format(self._ip_addr, self._port))
            raise Error(WrongIpAddress)

    def end_communication(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = bytearray(b'\xff\x00\x00\x00\x00\x00')
        msg += bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self._socket.sendto(msg, (self._ip_addr, self._port))

    def create_message(self):
        """
        Creates message for device.
        :return: msg
        """
        msg = bytearray(b'\x01\x00\x00\x00') + self._datatype
        msg += bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        return msg

    def start_monitor(self):
        """
        Send LLC (IEEE 802.2 - logical link  control) message
        which tells your device to send data at a certain frequency.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.sendto(self.create_message(), (self._ip_addr, self._port))

    def receive_data(self):
        """
        Receive UDP (in real-time) / TCP (otherwise) response from your device.
        This response needs to be parsed and this library provides parsing methods in util.py.
        """
        response = self._socket.recv(512)
        #TODO
        print(response)
        return response
