from arklibrary import Stream, Ini
import socket
from pathlib import Path


__LABEL_WIDTH = 15
__HEADER_WIDTH = 98
__TEMP_MESSAGE = '{tabs}\033[7;{label_color}m{label}\033[0;{text_color}m\t\t{message}\033[0m'
__MESSAGE = '\r{tabs}\033[7;{label_color}m{label}\033[0;{text_color}m\t\t{message}\033[0m'
__TEMP_HEADER = '{tabs}\033[7;{label_color}m{label}: {message}\033[0m'
__HEADER = '\r{tabs}\033[7;{label_color}m{label}: {message}\033[0m'


def connecting(message: str):
    label_color = 93
    text_color = 33
    tabs = "\t" * 0
    label_text = "CONNECTING".center(__HEADER_WIDTH // 2)
    message_text = f"{message}".center(__HEADER_WIDTH // 2)
    print(__TEMP_HEADER.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message_text, label=label_text), end='')


def connect(message: str, failed=False):
    label_color = 91 if failed else 92
    text_color = 32
    tabs = "\t" * 0
    label_text = ("FAILED" if failed else "CONNECTED").center(__HEADER_WIDTH // 2)
    message_text = f"{message}".center(__HEADER_WIDTH // 2)
    print(__HEADER.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message_text, label=label_text))


def disconnecting(message: str):
    label_color = 93
    text_color = 33
    tabs = "\t" * 0
    label_text = "DISCONNECTING".center(__HEADER_WIDTH // 2)
    message_text = f"{message}".center(__HEADER_WIDTH // 2)
    print(__TEMP_HEADER.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message_text, label=label_text), end='')


def disconnect(message: str):
    label_color = 92
    text_color = 32
    tabs = "\t" * 0
    label_text = "DISCONNECTED".center(__HEADER_WIDTH // 2)
    message_text = f"{message}".center(__HEADER_WIDTH // 2)
    print(__HEADER.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message_text,
                          label=label_text))


def sent(message: str):
    label_color = 96
    text_color = 36
    tabs = "\t" * 0
    label = "SENT".center(__LABEL_WIDTH)
    print(__MESSAGE.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message, label=label))


def response(message: str):
    label_color = 97
    text_color = 0
    tabs = "\t" * 0
    label = "RESPONSE".center(__LABEL_WIDTH)
    print(__MESSAGE.format(tabs=tabs, label_color=label_color, text_color=text_color, message=message, label=label))


class APIClient:
    """
    The API will be connecting as a client to bots listening.
    """

    PATH = Path.cwd() / Path('config.ini')

    def __init__(self, host=None, port=None, timeout=5):
        user_config = Path().cwd() / Path('config.ini')
        default_config = Path(__file__).parent / Path('config.ini')
        config = Ini(user_config) if user_config.exists() else Ini(default_config)
        self.host = host or config['ARK-SERVER']['host'] or '127.0.0.1'
        self.port = int(port) or int(config['ARK-SERVER']['port']) or 65432
        self.server_address = f"{self.host}:{self.port}"
        self.client_address = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.connected = False
        self.timeout = None
        self.header = None

    def connect(self):
        connecting(f"Connecting to {self.server_address}")
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            connect(f'{self.server_address}')
            out_stream = Stream(type='client', function='connect', from_address=self.client_address, to_address=self.server_address)
            self.socket.sendall(out_stream.encode())
            in_stream = self.read()
            self.client_address = f"{in_stream.to_address}"

        except ConnectionRefusedError:
            connect(f"Unable to connect with {self.server_address}", failed=True)
            self.connected = False

    def disconnect(self):
        if not self.connected:
            return
        disconnecting(f"{self.server_address}")
        self.socket.close()
        self.socket = None
        self.connected = False
        disconnect(f"{self.server_address}")

    def readall(self):
        if not self.connected:
            return
        fragments = bytearray()
        chunk_size = 40  # number of bytes to read at a time
        size = self.socket.recv(Stream.SIZE)
        if not size:
            return
        message_length = int(size.decode())  # TODO: disconnect if not possible because its someone trying to hack
        while len(fragments) < message_length:
            chunk = bytearray(self.socket.recv(chunk_size))  # Should be ready to read
            fragments += chunk
        recv_data = bytes(fragments)
        return recv_data

    def read(self, num_bytes: int = None) -> Stream:
        if num_bytes:
            recv_data = self.socket.recv(num_bytes)
        else:
            recv_data = self.readall()
        stream = Stream.new(recv_data)
        response(stream.body)
        return stream

    def send(self, data):
        if not self.connected:
            return
        sent(f'{data}')
        from_addr = f"{self.client_address}"
        to_addr = f"{self.server_address}"
        stream = Stream(from_address=from_addr, to_address=to_addr, body=data)
        self.socket.sendall(stream.encode())
        return Stream.new(self.read())

    def commands(self, data: dict):
        if not self.connected:
            return
        from_addr = f"{self.client_address}"
        to_addr = f"{self.server_address}"
        stream = Stream(from_address=from_addr, to_address=to_addr, type='api', function='commands', body=data)
        self.socket.sendall(stream.encode())
        return self.read()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __repr__(self):
        attr = {
            'connected': self.connected,
            'server_address': self.server_address,
            'client_address': self.client_address
        }
        items = []
        for k, v in attr.items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mGameBotClient\033[0m({args})>\033[0m'

