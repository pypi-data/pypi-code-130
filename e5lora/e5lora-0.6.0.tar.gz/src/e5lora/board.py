'''Holds the Board class for commmunicating with an SEEED Studio E5 board.
'''

import threading
import logging
import queue

from serial import Serial


class Board:
    """Class that writes and reads from the E5 board.
    """

    def __init__(
        self,
        port = '/dev/ttyUSB0',   # Serial port connected to the E5 board
        downlink_callback = None,    # function this class will call if a Downlink is received
        ):

        # open up the port to communicate to the E5 board
        self.port = Serial(port, 9600, timeout=0.5)

        # remember the callback function
        self.downlink_callback = downlink_callback

        # set up a Queue to accept commands to send to E5 module
        self.cmd_q = queue.SimpleQueue()

        # start the thread that communicates with the board through the serial port.
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):

        while True:

            # process any commands in the Queue
            try:
                cmd = self.cmd_q.get_nowait()
                # add an "AT+" in front and send as bytes to the board
                cmd_bytes = bytes(f'AT+{cmd.upper()}\n', 'utf-8')
                self.port.write(cmd_bytes)
            except queue.Empty:
                pass
            except Exception as err:
                logging.exception('Error accessing command queue.')

            # if there is no data, this blocks for the port timeout duration set in the
            # __init__ routine.  This delay is needed to keep the loop frequency reasonable.
            recv_line = self.port.readline().decode('utf-8').strip()
            if len(recv_line):
                logging.debug(recv_line)
                if 'PORT: 1; RX: "' in recv_line:
                    # this is a downlink message
                    data = recv_line.split('"')[-2]
                    logging.debug(f'Downlink message: {data}')
                    # convert data to a bytes object and call the downlink callback
                    if self.downlink_callback:
                        data_bytes = bytes.fromhex(data)
                        self.downlink_callback(data_bytes)


    def send_uplink(self, data_list):
        """Creates and sends an uplink message through the E5. 'data_list' is used to create the
        message.  'data_list' is an iterable of two-tuples; the first item of the tuple is 
        a non-negative integer data value and the second item is the number of bytes to use to encode the
        integer data value.  For example: (110, 2) will send the value 110 as a 2 byte integer.
        All of the encoded integers in 'data_list' will be concatenated together to make
        the message.
        """
        msg = ''
        for val, encode_len in data_list:
            msg += f'%0{encode_len * 2}X' % val

        self.add_command(f'MSGHEX="{msg}"')

    def add_command(self, cmd):
        """Adds a command to the queue to be sent to the E5 board.  'cmd' is a string;
        an 'AT+' is prepended to the string before being sent to the E5.
        """
        self.cmd_q.put(cmd)

    def set_data_rate(self, dr: int):
        """Changes the Data Rate of the E5 board
        """
        self.cmd_q.put(f'DR={dr}')

def to_int(bytes_obj: bytes):
    """Converts a bytes object 'bytes_obj' to an integer assuming MSB is stored
    at the beginning of the bytes object.
    """
    return int.from_bytes(bytes_obj, 'big')
