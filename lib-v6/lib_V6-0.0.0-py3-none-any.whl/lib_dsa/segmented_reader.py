import lib_compute.typon_math as typon_math

def read_bytes( fp, num_bytes, buffer_size ):
    if num_bytes >= buffer_size:
        return fp.read(num_bytes)
    return fp.read(buffer_size)


class forward_reader():
    def __init__( self, file_name, buffer_size ):
        self.file_name = file_name
        self.buffer_size = buffer_size
        self.buffer_index = 0
        self.entry_size = -1
        self.fp = open(file_name, 'rb')
        self.buffer = self.fp.read(buffer_size)
        self.iter_complete = False
    def has_next(self):
        if self.iter_complete:
            return False
        if self.entry_size > -1:
            return True
        if len( self.buffer ) < self.buffer_index + 8:
            bytes_to_read = self.buffer_index + 8 - len(self.buffer)
            buf_seg = read_bytes( self.fp, bytes_to_read, self.buffer_size )
            if len(buf_seg) < bytes_to_read:
                self.iter_complete = True
                return False
            if self.buffer_index > 0:
                self.buffer = self.buffer[ self.buffer_index : len(self.buffer) ]
                self.buffer_index = 0
            self.buffer += buf_seg
        size_repr = self.buffer[ self.buffer_index : self.buffer_index + 8 ]
        entry_size = typon_math.deserialize_int(size_repr)
        self.buffer_index += 8
        if len( self.buffer ) < self.buffer_index + entry_size:
            bytes_to_read = self.buffer_index + entry_size - len(self.buffer)
            buf_seg = read_bytes( self.fp, bytes_to_read, self.buffer_size )
            if len(buf_seg) < bytes_to_read:
                self.iter_complete = True
                return False
            if self.buffer_index > 0:
                self.buffer = self.buffer[ self.buffer_index : len(self.buffer) ]
                self.buffer_index = 0
            self.buffer += buf_seg
        entry_data = self.buffer[ self.buffer_index : self.buffer_index + entry_size ]
        self.entry_size = entry_size
        return True
    def get_next(self):
        if not self.has_next():
            return [ -1, -1 ]
        result = [ self.buffer_index, self.entry_size ]
        self.buffer_index += self.entry_size
        self.entry_size = -1
        return result
    def get_next_str(self):
        initial_index, entry_size = self.get_next()
        return self.buffer[ initial_index : initial_index + entry_size ]
