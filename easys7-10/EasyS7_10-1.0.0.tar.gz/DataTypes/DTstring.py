import struct
import snap7

class DTstring:
    def __init__(self):
        pass


    def set_string(self,_bytearray, byte_index, value, max_size):
        """
        Set string value
        :params value: string data
        :params max_size: max possible string size
        """
        assert isinstance(value, str)

        size = len(value)
        # FAIL HARD WHEN trying to write too much data into PLC
        if size > max_size:
            raise ValueError(f'size {size} > max_size {max_size} {value}')
        # set len count on first position
        _bytearray[byte_index + 1] = len(value)
        
        i = 0
        # fill array which chr integers
        for i, c in enumerate(value):
            _bytearray[byte_index + 2 + i] = ord(c)

        # fill the rest with empty space
        
        for r in range(len(value), _bytearray[byte_index]-2):
            
            _bytearray[byte_index + 2 + r] = ord(' ')
        return _bytearray