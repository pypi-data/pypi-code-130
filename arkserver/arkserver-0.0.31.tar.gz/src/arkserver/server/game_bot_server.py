from arklibrary import Stream, Ini
import socket
import selectors
import types
from pathlib import Path


# TODO: When a client connects, respond with their ip address

class GameBotServer:
    """
    Every Admin bot will be running this service
    """
    PATH = Path.cwd() / Path('config.ini')

    def __init__(self, host: str = None, port: str = None, public_host=None, timeout=5, config=None):
        ini = Ini(Path(config)) if config else Ini(self.PATH)
        self.host = '0.0.0.0'
        self.port = port and int(port) or ini['ARK-SERVER'] and int(ini['ARK-SERVER']['port']) or 65432
        address = public_host or ini['ARK-SERVER'] and ini['ARK-SERVER']['host'] or '0.0.0.0'
        self.public_address = f"{address}:{self.port}"
        self.selector = selectors.DefaultSelector()
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.settimeout(timeout)
        self.connected = False
        self.client_sockets = {}
        self.client_keys = {}
        self.servers = {}
        self.data = {}

    def connect(self):
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen()
        print(f"Listening on {self.host}:{self.port} (press CTRL-C to close server)")
        self.lsock.setblocking(False)
        self.selector.register(self.lsock, selectors.EVENT_READ, data=None)
        self.connected = True

    def disconnect(self):
        self.shutdown()
        self.selector.close()
        self.connected = False

    def read(self, addr: str):
        sock = self.client_sockets[addr]
        fragments = bytearray()
        try:
            while True:
                chunk = bytearray(sock.recv(4096))  # Should be ready to read
                if not chunk:
                    break
                fragments += chunk
        except BlockingIOError:
            recv_data = bytes(fragments)
            stream = Stream(stream=recv_data)
            print(f'\033[93mReceived from client ({addr}): {stream.body}\033[0m')
            return recv_data
        except ConnectionResetError:
            """ When the client forces the connection to close: ctrl-c """
            return None

    def write(self, stream: Stream):
        print(f'\033[93mSending to client ({stream.to_address}): {stream.body}\033[0m')
        sock = self.client_sockets[stream.to_address]
        key = self.client_keys[stream.to_address]
        encoded = stream.encode()
        size = f"{len(encoded)}".rjust(Stream.SIZE, '0').encode()
        sent = sock.send(size + encoded)
        key.data.outb = key.data.outb[sent:]

    def disconnect_client(self, addr):
        print(f"Closing connection to {addr}")
        sock = self.client_sockets[addr]
        self.selector.unregister(sock)
        sock.close()
        del self.client_keys[addr]
        del self.client_sockets[addr]

    def shutdown(self):
        addresses = list(self.client_keys.keys())
        for addr in addresses:
            self.send_disconnect(addr)
            self.disconnect_client(addr)

    def send_disconnect(self, addr):
        sock = self.client_sockets[addr]
        data = self.client_keys[addr].data
        sent = sock.send("exit".encode())  # Should be ready to write
        data.outb = data.outb[sent:]

    def accept_wrapper(self, key):
        sock = key.fileobj
        conn, (host, port) = sock.accept()  # Shoulbd be ready to read
        client_address = f"{host}:{port}"
        print(f"Accepted connection from {client_address}")

        self.client_sockets[client_address] = sock
        self.client_keys[client_address] = key

        conn.setblocking(False)
        data = types.SimpleNamespace(addr=client_address, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)
        return client_address

    def service_connection(self, key, mask):
        data = key.data
        addr = data.addr
        self.client_sockets[addr] = key.fileobj
        self.client_keys[addr] = key
        stream = None

        if mask & selectors.EVENT_READ:
            read = self.read(addr)
            if read:
                stream = Stream.new(read)
                stream.from_address = addr
                data.outb += read
            else:
                self.disconnect_client(addr)
        if mask & selectors.EVENT_WRITE:
            if stream:
                if stream.type == 'api':
                    self.api_functions(stream)
                elif stream.type == "client":
                    self.client_functions(stream)

    def client_functions(self, in_stream: Stream):
        client_address = in_stream.from_address
        server_address = self.public_address
        out_stream = Stream(from_address=server_address, to_address=client_address)
        if in_stream.function == 'ping':
            server_id = in_stream.body
            if server_id in self.data:
                out_stream.body = self.data[server_id]
                del self.data[server_id]
        elif in_stream.function == 'write':
            pass
        elif in_stream.function == 'connect':
            out_stream.function = 'connect'
            out_stream.body = "Connected"
        self.write(out_stream)

    def api_functions(self, in_stream: Stream):
        client_address = in_stream.from_address
        server_address = self.public_address
        out_stream = Stream(from_address=server_address, to_address=client_address)
        if in_stream.function == 'commands':
            commands = in_stream.body['commands']
            server_id = in_stream.body['server_id']
            if server_id in self.data:
                self.data[server_id] += commands
            else:
                self.data[server_id] = commands
            out_stream.body = {'success': commands}
        self.write(out_stream)

    def run(self):
        self.connect()
        try:
            while True:
                events = self.selector.select(timeout=None)
                for selector_key, mask in events:
                    if selector_key.data is None:
                        self.accept_wrapper(selector_key)
                    else:
                        self.service_connection(selector_key, mask)
        except KeyboardInterrupt:
            print("\nCaught keyboard interrupt, exiting:")
        finally:
            self.disconnect()
            print("All connections closed.")

    def __repr__(self):
        attr = {
            'connected': self.connected,
            'host': self.host,
            'port': self.port
        }
        items = []
        for k, v in attr.items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mGameBotServer\033[0m({args})>\033[0m'
