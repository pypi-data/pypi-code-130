import struct

"""
   NosoFileStream

   Wrapping binary reads and struct in a simpler package
"""

class NosoFileStream:
    
    def __init__(self, filename):
        self.f = open(filename, 'rb')

    def read_int(self):
        s = struct.Struct('i')
        data = self.f.read(s.size)
        result, = s.unpack(data)
        return result

    def read_int64(self):
        s = struct.Struct('q')
        data = self.f.read(s.size)
        result, = s.unpack(data)
        return result

    def read_pas_str(self, size):
        s = struct.Struct('B '+str(size)+'s')
        data = self.f.read(s.size)
        str_size, str_container = s.unpack(data)
        result = str_container[:str_size].decode('utf-8')
        #result = str_container[:str_size].decode('ascii')
        #result = str_container[:str_size].decode()
        #result = str_container[:str_size]
        return result

    def close(self):
        self.f.close()
