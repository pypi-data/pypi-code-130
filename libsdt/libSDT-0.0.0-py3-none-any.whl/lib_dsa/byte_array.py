import os
import lib_compute.typon_math as typon_math
import threading

def make_vba(base_path):
    index_fspath = f'{base_path}.index'
    data_fspath = f'{base_path}.data'
    clear_fspath = False
    return variable_bytes_array(index_fspath, data_fspath, clear_fspath)


class variable_bytes_array():
    def __init__(self, index_fspath: str, data_fspath: str, clear_fspath: bool):
        self.index_fspath = index_fspath
        self.data_fspath = data_fspath
        self.item_count = 0
        self.total_bytes = 0
        self.size_fxn = os.path.getsize
        self.mutex = threading.Lock()
        if clear_fspath:
            fptr = open(self.index_fspath, 'wb')
            fptr.close()
            fptr = open(self.data_fspath, 'wb')
            fptr.close()
            return
        if not os.path.exists(self.index_fspath):
            open(self.index_fspath, 'wb').close()
        if not os.path.exists(self.data_fspath):
            open(self.data_fspath, 'wb').close()
        self.item_count = self.size_fxn(self.index_fspath) // 16
        self.total_bytes = self.size_fxn(self.data_fspath)
    def index_size(self) -> int:
        with self.mutex:
            return self.size_fxn(self.index_fspath)
    def data_size(self) -> int:
        with self.mutex:
            return self.size_fxn(self.data_fspath)
    def insert_bytes(self, target_bytes) -> int:
        with self.mutex:
            size_repr = typon_math.serialize_int( len(target_bytes) )
            offset_repr = typon_math.serialize_int( self.total_bytes )
            index_bytes = offset_repr + size_repr
            fptr = open(self.index_fspath, 'ab')
            fptr.write(index_bytes)
            fptr.close()
            fptr1 = open(self.data_fspath, 'ab')
            fptr1.write(target_bytes)
            fptr1.close()
            self.total_bytes += len(target_bytes)
            self.item_count += 1
            return self.item_count - 1
    def batch_insert_bytes(self, target_bytes_L1) -> int:
        with self.mutex:
            current_offset = 0
            fptr = open(self.index_fspath, 'ab')
            fptr1 = open(self.data_fspath, 'ab')
            for i in range(0, len(target_bytes_L1)):
                size_repr = typon_math.serialize_int( len(target_bytes_L1[i]) )
                offset_repr = typon_math.serialize_int(self.total_bytes + current_offset)
                fptr.write(offset_repr)
                fptr.write(size_repr)
                fptr1.write( target_bytes_L1[i] )
                current_offset += len(target_bytes_L1[i])
            fptr.close()
            fptr1.close()
            self.total_bytes += current_offset
            self.item_count += len(target_bytes_L1)
            return self.item_count - 1
    def read_index_bytes(self, offset: int, limit: int) -> str:
        with self.mutex:
            fptr = open(self.index_fspath, 'rb')
            fptr.seek(offset, 0)
            result = fptr.read(limit)
            fptr.close()
            return result
    def read_data_bytes(self, offset: int, limit: int) -> str:
        with self.mutex:
            fptr = open(self.data_fspath, 'rb')
            fptr.seek(offset, 0)
            result = fptr.read(limit)
            fptr.close()
            return result
    def select_id(self, item_id: int) -> str:
        with self.mutex:
            if item_id < 0 or item_id >= self.item_count:
                return ''
            fptr = open(self.index_fspath, 'rb')
            fptr.seek(16 * item_id, 0)
            index_repr = fptr.read(16)
            fptr.close()
            item_offset = typon_math.deserialize_int(index_repr[ 0 : 8 ])
            item_size = typon_math.deserialize_int(index_repr[ 8 : 16 ])
            fptr = open(self.data_fspath, 'rb')
            fptr.seek(item_offset, 0)
            result = fptr.read(item_size)
            fptr.close()
            return result
    def select_id_range(self, id_lower_bound: int, id_upper_bound: int):
        with self.mutex:
            if id_lower_bound < 0 or id_upper_bound > self.item_count or id_lower_bound >= id_upper_bound:
                return []
            fptr = open(self.index_fspath, 'rb')
            fptr.seek(16 * id_lower_bound, 0)
            index_repr = fptr.read(16 * (id_upper_bound - id_lower_bound))
            fptr.close()
            fptr = open(self.data_fspath, 'rb')
            result: vec[str] = []
            for i in range(id_lower_bound, id_upper_bound):
                index_offset = 16 * (i - id_lower_bound)
                item_offset = typon_math.deserialize_int(index_repr[ index_offset + 0 : index_offset + 8 ])
                item_size = typon_math.deserialize_int(index_repr[ index_offset + 8 : index_offset + 16 ])
                fptr.seek(item_offset, 0)
                item_repr = fptr.read(item_size)
                result.append(item_repr)
            fptr.close()
            return result
    def remove_last_k(self, k: int) -> int:
        with self.mutex:
            if k <= 0 or k > self.item_count:
                return 0
            item_id = self.item_count - k
            fptr = open(self.index_fspath, 'rb+')
            fptr.seek(16 * item_id, 0)
            index_repr = fptr.read(16)
            item_offset = typon_math.deserialize_int(index_repr[ 0 : 8 ])
            fptr.truncate(16 * item_id)
            fptr.close()
            fptr1 = open(self.data_fspath, 'rb+')
            fptr1.truncate(item_offset)
            fptr1.close()
            self.item_count -= k
            return item_id
