import hashlib
from .streams import NosoFileStream
from .streams import NosoMemStream

"""
  NosoBlock

  The block class that contains a Noso Block
"""

class NosoBlock:

    def __init__(self, *args):
        if args:
            self.number =         long(args[0])
            self.time_start =     long(args[1])
            self.time_end =       long(args[2])
            self.time_total =      int(args[3])
            self.time_last_20 =    int(args[4])
            self.transfer_count =  int(args[5])
            self.difficulty =      int(args[6])
            self.target_hash =         args[7]
            self._target_hash = None
            self.solution =            args[8]
            self._solution = None
            self.last_block_hash =     args[9]
            self._last_block_hash = None
            self.next_block_diff = int(args[10])
            self.miner =               args[11]
            self._miner = None
            self.fee =            long(args[12])
            self.reward =         long(args[13])
            self.orders = list()
            self.pos_reward =     long(args[14])
            self.pos_list = list()
            self.mns_reward =     long(args[15])
            self.mns_list = list()
        else:
            self.number = -1
            self.time_start = -1
            self.time_end = -1
            self.time_total = -1
            self.time_last_20 = -1
            self.transfer_count = 0
            self.difficulty = -1
            self.target_hash = 'UNKNOWN'
            self._target_hash = None
            self.solution = 'UNKNOWN'
            self._solution = None
            self.last_block_hash = 'UNKNOWN'
            self._last_block_hash = None
            self.next_block_diff = -1
            self.miner = 'UNKNOWN'
            self._miner = None
            self.fee = -1
            self.reward = -1
            self.orders = list()
            self.pos_reward = -1
            self.pos_list = list()
            self.mns_reward = -1
            self.mns_list = list()

    @property
    def hash(self):
        ms = NosoMemStream()
        ms.write_int64(self.number)
        ms.write_int64(self.time_start)
        ms.write_int64(self.time_end)
        ms.write_int(self.time_total)
        ms.write_int(self.time_last_20)
        ms.write_int(self.transfer_count)
        ms.write_int(self.difficulty)
        ms.write_pas_str(self._target_hash);
        ms.write_pas_str(self._solution);
        ms.write_pas_str(self._last_block_hash);
        ms.write_int(self.next_block_diff)
        ms.write_pas_str(self._miner);
        ms.write_int64(self.fee)
        ms.write_int64(self.reward)

        if len(self.orders) > 0:
            for order in self.orders:
                ms.write_int(order.block)
                ms.write_pas_str(order._order_id)
                ms.write_int(order.transfer_count)
                ms.write_pas_str(order._order_type)
                ms.write_int64(order.timestamp)
                ms.write_pas_str(order._reference)
                ms.write_int(order.transfer_pos)
                ms.write_pas_str(order._sender)
                ms.write_pas_str(order._address)
                ms.write_pas_str(order._receiver)
                ms.write_int64(order.fee)
                ms.write_int64(order.amount)
                ms.write_pas_str(order._signature)
                ms.write_pas_str(order._transfer_id)

        if len(self.pos_list) > 0:
            ms.write_int64(self.pos_reward)
            ms.write_int(len(self.pos_list))
            for address in self.pos_list:
                ms.write_pas_str(address[0])

        if len(self.mns_list) > 0:
            ms.write_int64(self.mns_reward)
            ms.write_int(len(self.mns_list))
            for address in self.mns_list:
                ms.write_pas_str(address[0])

        h = hashlib.md5()
        h.update(ms.asByteArray)
        result = h.hexdigest()

        return result.upper()

    def load_from_file(self, filename):
        nfs = NosoFileStream(filename)
        self.load_from_stream(nfs)
        nfs.close()

    def load_from_stream(self, nsf):
        self.number = nsf.read_int64()
        self.time_start = nsf.read_int64()
        self.time_end = nsf.read_int64()
        self.time_total = nsf.read_int()
        self.time_last_20 = nsf.read_int()
        self.transfer_count = nsf.read_int()
        self.difficulty = nsf.read_int()
        self._target_hash, self.target_hash = nsf.read_pas_str(32)
        self._solution,self.solution = nsf.read_pas_str(200)
        self._last_block_hash,self.last_block_hash = nsf.read_pas_str(32)
        self.next_block_diff = nsf.read_int()
        self._miner,self.miner = nsf.read_pas_str(40)
        self.fee = nsf.read_int64()
        self.reward = nsf.read_int64()

        # Orders/Transfers
        if self.transfer_count > 0:
            for x in range(0, self.transfer_count):
                order = NosoOrder()
                order.load_from_stream(nsf)
                self.orders.append(order)

        # PoS
        if self.number >= 8425:
            self.pos_reward = nsf.read_int64()
            pos_count = nsf.read_int()
            for x in range(0, pos_count):
                self.pos_list.append(nsf.read_pas_str(32))
        
        # MNs
        if self.number >= 48010:
            self.mns_reward = nsf.read_int64()
            mns_count = nsf.read_int()
            for x in range(0, mns_count):
                self.mns_list.append(nsf.read_pas_str(32))
        

"""
  NosoOrder

  The Order class that contains the order/stransfer pair
"""
class NosoOrder:

    def __init__(self, *args):
        if args:
            self.block =          int(args[0])
            self.order_id =           args[1]
            self._order_id = None
            self.transfer_count = int(args[2])
            self.order_type =         args[3]
            self._order_type = None
            self.timestamp =     long(args[4])
            self.reference =          args[5]
            self._reference = None
            self.trasnfer_pos =   int(args[6])
            self.sender =             args[7]
            self._sender = None
            self.address =            args[8]
            self._address = None
            self.receiver =           args[9]
            self._receiver = None
            self.fee =          long(args[10])
            self.amount =       long(args[11])
            self.signature =         args[12]
            self._signature = None
            self.transfer_id =       args[13]
            self._transfer_id = None
        else:
            self.block = -1
            self.order_id = 'UNKNONW'
            self._order_id = None
            self.trasnfer_count = 0
            self.order_type = 'UNKNOWN'
            self._order_type = None
            self.timestamp = -1
            self.reference = ''
            self.transfer_pos = -1
            self.sender = 'UNKNOWN'
            self._sender = None
            self.address = 'UNKNOWN'
            self._address = None
            self.receiver = 'UNKNOWN'
            self._receiver = None
            self.fee = -1
            self.amount = -1
            self.signature = 'UNKNOWN'
            self._signature = None
            self.trasnfer_id = 'UNKNOWN'
            self._trasnfer_id = None

    def load_from_stream(self, nsf):
        self.block = nsf.read_int()
        self._order_id,self.order_id = nsf.read_pas_str(64)
        self.transfer_count = nsf.read_int()
        self._order_type,self.order_type = nsf.read_pas_str(6)
        self.timestamp = nsf.read_int64()
        self._reference,self.reference = nsf.read_pas_str(64)
        self.transfer_pos = nsf.read_int()
        self._sender,self.sender = nsf.read_pas_str(120)
        self._address,self.address = nsf.read_pas_str(40)
        self._receiver,self.receiver = nsf.read_pas_str(40)
        self.fee = nsf.read_int64()
        self.amount = nsf.read_int64()
        self._signature,self.signature = nsf.read_pas_str(120)
        self._transfer_id,self.transfer_id = nsf.read_pas_str(64)
