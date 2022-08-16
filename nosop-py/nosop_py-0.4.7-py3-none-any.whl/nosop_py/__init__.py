import socket

__version__ = '0.4.7'

"""
  NosoSocket

  A class to manage a EOL terminated protocol for NosoCoin, aka NosoP

"""
class NosoSocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
        else:
            self.sock = sock
            self.sock.settimeout(30)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        msg = msg + '\r\n'
        msg = str.encode(msg)
        totalsent = 0
        MSGLEN = len(msg)
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")

            totalsent = totalsent + sent

    def receive(self, EOFChar=b'\n'):
        msg = []
        MSGLEN = 1024 * 1024 * 10 # 10 MB
        while len(msg) < MSGLEN:
            chunk = self.sock.recv(MSGLEN-len(msg))
            if chunk.find(EOFChar) != -1:
                msg.append(chunk)
                #print('Found EOFChar')
                #print('Len msg:',len(msg))
                return b''.join(msg).decode('UTF-8')

            msg.append(chunk)
        #print('Did not found EOFChar')
        #print('Len msg:',len(msg))
        return b''.join(msg).decode('UTF-8')

    def close(self):
        self.sock.close()

"""
    NosoNodeInfo

    A class to contain the data provided by asking the status of a node

"""
class NosoNodeInfo:

    """
    NODESTATUS 1{Peers} 2{LastBlock} 3{Pendings} 4{Delta} 5{headers} 6{version} 7{UTCTime} 8{MNsHash} 9{MNscount}
               10{LasBlockHash} 11{BestHashDiff} 12{LastBlockTimeEnd} 13{LBMiner} 14{ChecksCount} 15{LastBlockPoW}
               16{LastBlockDiff} 17{summary} 18{GVTs} 19{nosoCFG}
    """

    def __init__(self, *args):
        if args:
            self.peers = int(args[1])
            self.block = int(args[2])
            self.pending = int(args[3])
            self.sync_delta = int(args[4])
            self.branch = args[5]
            self.version = args[6]
            self.time = args[7]
            self.mn_hash = args[8]
            self.mn_count = int(args[9])
            self.last_block_hash = args[10]
            self.best_hash_diff = args[11]
            self.last_block_time_end = int(args[12])
            self.last_best_hash_miner = args[13]
            self.checks_count = int(args[14])
            self.last_block_pow = args[15]
            self.last_block_diff = args[16]
            self.summary = args[17]
            self.gvts = args[18]
            self.cfgs = args[19]
        else:
            self.peers = -1
            self.block = -1
            self.pending = -1
            self.sync_delta = -1
            self.branch = 'NONE'
            self.version = 'UNKNOWN'
            self.time = -1
            self.mn_hash = 'UNKNOWN'
            self.mn_count = -1
            self.last_block_hash = 'UNKNOWN'
            self.best_hash_diff = 'UNKNOWN'
            self.last_block_time_end = -1
            self.last_best_hash_miner = 'UNKNOWN'
            self.checks_count = -1
            self.last_block_pow = 'UNKNOWN'
            self.last_block_diff = 'UNKNOWN'
            self.summary = 'UNKNOWN'
            self.gvts = 'UNKNOWN'
            self.cfgs = 'UNKNOWN'

"""
    NosoNode

    A class that will ask for the status of a node

"""
class NosoNode:

    def __init__(self, name, host = 'localhost', port = 8080):
        self.sock = NosoSocket()
        self.name = name
        self.host = host
        self.port = port

    def get_info(self):
        error = False
        try:
            self.sock.connect(self.host, self.port)
            self.sock.send('NODESTATUS')
            response = self.sock.receive()

        finally:
            self.sock.close()

        elements = response.split()

        if elements[0] == 'NODESTATUS':
            return NosoNodeInfo(*elements)
        else:
            print('Wrong response from node')
            return None

"""
    NosoPoolInfo

    A class to contain the data provided by asking the status of a pool

"""
class NosoPoolInfo:

    def __init__(self, name, *args):
        self.name = name
        self.miners = list()
        if args:
            self.miners_count = int(args[0])
            self.last_block_rate = int(args[1])
            self.pool_fee = int(args[2])
            if len(args) > 3:
                self.main_net_hash_rate = int(args[3])
            else:
                self.main_net_hash_rate = -1
        else:
            self.miners_count = -1
            self.last_block_rate = -1
            self.pool_fee = -1
            self.main_net_hash_rate = -1

"""
    NosoPool

    A class that will ask for the status of a pool

"""
class NosoPool:

    def __init__(self, name, host, port):
        self.sock = NosoSocket()
        self.name = name
        self.host = host
        self.port = port

    def get_info(self):
        error = False
        try:
            self.sock.connect(self.host, self.port)
            self.sock.send('POOLINFO')
            response = self.sock.receive()

        finally:
            self.sock.close()

        elements = response.split()
        #print('Before last:',elements[len(elements)-2])
        #print('Last:',elements[len(elements)-1])

        return NosoPoolInfo(self.name, *elements)

