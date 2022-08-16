"""
The file util.py provides the general majority of exceptions and allows
you to use various methods of parsing the data obtained from the device.

TODO
 create parsing methods (BADC - float-mid-big endian)
"""


class Error(Exception):
    """Base Error class"""
    pass


class WrongIpAddress(Error):
    """Wrong format of target IP address"""
    pass


class ResponseParser:
    pass
