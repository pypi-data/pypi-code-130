from struct import Struct

"""
   NosoFileStream

   Wrapping binary reads and struct in a simpler package
"""

class NosoFileStream:

    """
      TODO:
        - Implement the write methods
        - Implement seek, maybe?
    """
    
    def __init__(self, filename):
        self.f = open(filename, 'rb')

    def read_int(self):
        s = Struct('i')
        data = self.f.read(s.size)
        result, = s.unpack(data)
        return result

    def read_int64(self):
        s = Struct('q')
        data = self.f.read(s.size)
        result, = s.unpack(data)
        return result

    def read_pas_str(self, size):
        s = Struct('B'+str(size)+'s')
        data = self.f.read(s.size)
        str_size, str_container = s.unpack(data)
        string = str_container[:str_size].decode('utf-8')

        # Pascal Strings may contain garbage after length, so we need to
        # store both the full length and the string
        # Need to do some magic here to conceal this :(
        return data, string

    def close(self):
        self.f.close()

class NosoMemStream:
    
    """
      TODO:
        - Implement the read methods
        - Implement seek, maybe?
    """
    
    def __init__(self):
        self._data = bytearray()

    def write_int(self, data):
        s = Struct('i')
        self._data += s.pack(data)

    def write_int64(self, data):
        s = Struct('q')
        self._data += s.pack(data)

    def write_pas_str(self, data):
        self._data += data

    @property
    def asByteArray(self):
        return self._data
