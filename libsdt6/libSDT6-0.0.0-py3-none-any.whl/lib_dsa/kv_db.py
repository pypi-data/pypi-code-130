import os
import leveldb
import lib_compute.typon_math as typon_math
import lib_dsa.byte_array as byte_array
import lib_dsa.kv_iter as kv_iter

class kv_iterator_vba():
    def __init__(self, lvl_db_iter, kvs_ref, include_key, include_value):
        self.lvl_db_iter = lvl_db_iter
        self.include_key = include_key
        self.include_value = include_value
    def has_next(self):
        return self.lvl_db_iter.has_next()
    def get_next(self):
        if not self.has_next():
            return None
        key, index_repr = self.lvl_db_iter.get_next()
        result = []
        if self.include_key:
            result.append(key)
        if self.include_value:
            item_index = typon_math.deserialize_int( index_repr )
            result.append( self.kvs_ref.vba.select_id( item_index ) )
        return result


class kv_iterator_no_vba():
    def __init__(self, lvl_db_iter, kvs_ref):
        self.lvl_db_iter = lvl_db_iter
    def has_next(self):
        return self.lvl_db_iter.has_next()
    def get_next(self):
        return self.lvl_db_iter.get_next()


class kv_store():
    def __init__(self, db_path, vba_engine=False):
        self.db_path = db_path
        self.db = leveldb.LevelDB( db_path, create_if_missing=True )
        self.vba_engine = vba_engine
        if vba_engine:
            self.vba = byte_array.make_vba( db_path )
    def engine_get(self, key):
        V1 = None
        try:
            V1 = self.db.Get(key)
            V1 = bytes(V1)
        except:
            V1 = None
        if not self.vba_engine:
            return V1
        item_index = typon_math.deserialize_int(V1)
        return self.vba.select_id(item_index)
    def engine_set(self, key, value):
        if not self.vba_engine:
            return self.db.Put(key, value)
        index_repr = typon_math.serialize_int( self.vba.item_count )
        kvs_op = self.db.Put(key, index_repr)
        le_op = self.vba.insert_bytes( value )
        return [ kvs_op, le_op ]
    def engine_remove(self, key):
        return self.db.Delete(key)
    def get(self, key, key_encoding='latin-1'):
        if isinstance(key, str):
            key_bytes = key.encode(key_encoding)
            return self.engine_get(key_bytes)
        return self.engine_get(key)
    def set(self, key, value, key_encoding='latin-1', value_encoding='latin-1'):
        if isinstance(key, str):
            key_bytes = key.encode(key_encoding)
            if isinstance(value, str):
                value_bytes = value.encode(value_encoding)
                return self.engine_set(key_bytes, value_bytes)
            return self.engine_set(key_bytes, value)
        if isinstance(value, str):
            value_bytes = value.encode(value_encoding)
            return self.engine_set(key, value_bytes)
        return self.engine_set(key, value)
    def remove(self, key, key_encoding='latin-1'):
        if isinstance(key, str):
            key_bytes = key.encode(key_encoding)
            return self.engine_remove(key_bytes)
        return self.engine_remove(key)
    def batch_write(self, op_args_L1, transaction=False):
        if self.vba_engine:
            wb = self.db.WriteBatch()
            value_insert_L1 = []
            insert_count = 0
            for op_args in op_args_L1:
                if op_args[0] == 'set':
                    index_repr = typon_math.serialize_int( self.vba.item_count + insert_count )
                    insert_count += 1
                    value_insert_L1.append( op_args[2] )
                    wb.Put( op_args[1], index_repr )
                    continue
                if op_args[0] == 'remove':
                    wb.Delete( op_args[1] )
            vba_op = self.vba.batch_insert_bytes(value_insert_L1)
            kvs_op = self.db.Write(wb, sync=transaction)
            return [ kvs_op, vba_op ]
        wb = self.db.WriteBatch()
        for op_args in op_args_L1:
            if op_args[0] == 'set':
                wb.Put( op_args[1], op_args[2] )
                continue
            if op_args[0] == 'remove':
                wb.Delete( op_args[1] )
        kvs_op = self.db.Write(wb, sync=transaction)
        return kvs_op
    def iterator(
            self,
            start=None,
            stop=None,
            prefix=None,
            include_start=True,
            include_stop=False,
            include_key=True,
            include_value=True,
            reverse=False
        ):
        if not self.vba_engine:
            lvl_db_iter = kv_iter.ldb_iterator(
                            self.db,
                            start=start,
                            stop=stop,
                            prefix=prefix,
                            include_start=include_start,
                            include_stop=include_stop,
                            include_key=include_key,
                            include_value=include_value,
                            reverse=reverse
                        )
            return kv_iterator_no_vba(lvl_db_iter, self)
        lvl_db_iter = kv_iter.ldb_iterator(
                    self.db,
                    start=start,
                    stop=stop,
                    prefix=prefix,
                    include_start=include_start,
                    include_stop=include_stop,
                    include_key=True,
                    include_value=True,
                    reverse=reverse
                )
        return kv_iterator_vba(lvl_db_iter, self, include_key, include_value)
