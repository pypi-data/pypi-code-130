
def select_prefix_closure( prefix ):
    buf = bytearray()
    for i in range( len(prefix)-1, -1, -1 ):
        if prefix[i] == 255:
            buf.append(0)
            continue
        X = bytearray()
        X.append( prefix[i] + 1 )
        return prefix[0:i] + bytes(X) + bytes(buf)
    return None


class ldb_range_iter():
    def __init__( self, db_ref, start, stop, include_start, include_stop, include_key, include_value, reverse ):
        self.db_it = db_ref.RangeIter(
                    key_from = start,
                    key_to = stop,
                    include_value = include_value,
                    reverse = reverse
                )
        self.start = start
        self.stop = stop
        self.include_start = include_start
        self.include_stop = include_stop
        self.include_key = include_key
        self.include_value = include_value
        self.reverse = reverse
        self.cur_kv = []
        self.val_set = False
        self.iter_finish = False
    def has_next(self):
        if self.iter_finish:
            return False
        if self.val_set:
            return True
        if not self.include_value:
            while True:
                X = next(self.db_it, None)
                if X == None:
                    self.iter_finish = True
                    return False
                key_bytes = bytes(X[0])
                if key_bytes == self.start and not self.include_start:
                    continue
                if key_bytes == self.stop and not self.include_stop:
                    continue
                if not self.include_key:
                    self.cur_kv = []
                    self.val_set = True
                    return True
                self.cur_kv = [ key_bytes ]
                self.val_set = True
                return True
            return False
        while True:
            X = next(self.db_it, None)
            if X == None:
                self.iter_finish = True
                return False
            key_bytes = bytes(X[0])
            value_bytes = bytes(X[1])
            if key_bytes == self.start and not self.include_start:
                continue
            if key_bytes == self.stop and not self.include_stop:
                continue
            if not self.include_key:
                self.cur_kv = [ value_bytes ]
                self.val_set = True
                return True
            self.cur_kv = [ key_bytes, value_bytes ]
            self.val_set = True
            return True
        return False
    def get_next(self):
        if not self.has_next():
            return None
        self.val_set = False
        return self.cur_kv


class ldb_prefix_iterator():
    def __init__( self, db_ref,  prefix, include_key, include_value, reverse  ):
        prefix_closure = select_prefix_closure( prefix )
        self.db_it = db_ref.RangeIter(
                    key_from = prefix,
                    key_to = prefix_closure,
                    include_value = include_value,
                    reverse = reverse
                )
        self.start = prefix
        self.stop = prefix_closure
        self.include_key = include_key
        self.include_value = include_value
        self.reverse = reverse
        self.cur_kv = []
        self.val_set = False
        self.iter_finish = False
    def has_next(self):
        if self.iter_finish:
            return False
        if self.val_set:
            return True
        if not self.include_value:
            while True:
                X = next(self.db_it, None)
                if X == None:
                    self.iter_finish = True
                    return False
                key_bytes = bytes(X[0])
                if self.prefix != key_bytes[0:len(self.prefix)]:
                    continue
                if not self.include_key:
                    self.cur_kv = []
                    self.val_set = True
                    return True
                self.cur_kv = [ key_bytes ]
                self.val_set = True
                return True
            return False
        while True:
            X = next(self.db_it, None)
            if X == None:
                self.iter_finish = True
                return False
            key_bytes = bytes(X[0])
            value_bytes = bytes(X[1])
            if self.prefix != key_bytes[0:len(self.prefix)]:
                continue
            if not self.include_key:
                self.cur_kv = [ value_bytes ]
                self.val_set = True
                return True
            self.cur_kv = [ key_bytes, value_bytes ]
            self.val_set = True
            return True
        return False
    def get_next(self):
        if not self.has_next():
            return None
        self.val_set = False
        return self.cur_kv


class ldb_iterator():
    def __init__(
            self,
            db_ref,
            start=None,
            stop=None,
            prefix=None,
            include_start=True,
            include_stop=False,
            include_key=True,
            include_value=True,
            reverse=False
        ):
        if prefix != None:
            self.base_it = ldb_prefix_iterator( db_ref, prefix, include_key, include_value, reverse )
            return
        self.base_it = ldb_range_iter( db_ref, start, stop, include_start, include_stop, include_key, include_value, reverse )
    def has_next(self):
        return self.base_it.has_next()
    def get_next(self):
        return self.base_it.get_next()
