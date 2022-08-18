import os
import lib_dsa.kv_db as kv_db
import lib_compute.typon_math as typon_math

class graph_edge_iterator():
    def __init__(self, gs_ref, src_node_bytes):
        self.gs_ref = gs_ref
        self.src_node_bytes = src_node_bytes
        self.edge_it = gs_ref.iterator(
                    prefix=src_node_bytes,
                    include_key=True,
                    include_value=True,
                    reverse=False
                )
        self.tgt_node_bytes = b''
        self.val_set = False
    def has_next(self):
        if self.val_set:
            return True
        if not self.edge_it.has_next():
            return False
        while self.edge_it.has_next():
            potential_edge, evalue = self.edge_it.get_next()
            src_len = typon_math.deserialize_int32( potential_edge[ len(potential_edge)-4 : ] )
            pt_src = potential_edge[ 0 : src_len ]
            if pt_src == self.src_node_bytes:
                self.tgt_node_bytes = potential_edge[ src_len : len(potential_edge)-4 ]
                self.val_set = True
                return True
        return False
    def get_next(self):
        if not self.has_next():
            return b''
        self.val_set = False
        return self.tgt_node_bytes


class graph_store():
    def __init__(self, db_base, vba_engine=False):
        if not os.path.isdir(db_base):
            os.mkdir(db_base)
        node_table = f'{db_base}/n'
        edge_table = f'{db_base}/e'
        self.node_store = kv_db.kv_store( node_table, vba_engine=vba_engine )
        self.edge_store = kv_db.kv_store( edge_table, vba_engine=False )
    def node_batch_write(self, op_args_L1, transaction=False):
        return self.node_store.batch_write(op_args_L1, transaction=transaction)
    def set_node(self, node_key, node_value, key_encoding='latin-1', value_encoding='latin-1'):
        return self.node_store.set(node_key, node_value, key_encoding=key_encoding, value_encoding=value_encoding)
    def get_node(self, node_key, key_encoding='latin-1'):
        return self.node_store.get(node_key, key_encoding=key_encoding)
    def remove_node(self, node_key, key_encoding='latin-1'):
        return self.node_store.remove(node_key, key_encoding=key_encoding)
    def set_edge(self, src_node, tgt_node, src_encoding='latin-1', tgt_encoding='latin-1'):
        src_enc = src_node
        if isinstance(src_enc, str):
            src_enc = src_node.encode(src_encoding)
        tgt_enc = tgt_node
        if isinstance(tgt_enc, str):
            tgt_enc = tgt_node.encode(tgt_encoding)
        edge_repr = b'\x01'
        src_len_enc = typon_math.serialize_int32( len(src_node) )
        edge_key = src_enc + tgt_enc + src_len_enc
        return self.node_store.set(edge_key, edge_repr)
    def remove_edge(self, src_node, tgt_node, src_encoding='latin-1', tgt_encoding='latin-1'):
        src_enc = src_node
        if isinstance(src_enc, str):
            src_enc = src_node.encode(src_encoding)
        tgt_enc = tgt_node
        if isinstance(tgt_enc, str):
            tgt_enc = tgt_node.encode(tgt_encoding)
        src_len_enc = typon_math.serialize_int32( len(src_node) )
        edge_key = src_enc + tgt_enc + src_len_enc
        return self.node_store.remove(edge_key)
    def edge_iterator(self, src_node, src_encoding='latin-1'):
        src_node_bytes = src_node
        if isinstance(src_node, str):
            src_node_bytes = src_node.encode(src_encoding)
        return graph_edge_iterator( self, src_node_bytes )
    def iterate_edges(self, src_node, src_encoding='latin-1'):
        src_node_bytes = src_node
        if isinstance(src_node, str):
            src_node_bytes = src_node.encode(src_encoding)
        result = []
        edge_it = graph_edge_iterator( self, src_node_bytes )
        while edge_it.has_next():
            result.append( edge_it.get_next() )
        return result
