from arklibrary import Stream, Header, Ini
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


class GameBotClient:
    """
    The API will be connecting as a client to bots listening.
    """

    PATH = Path.cwd() / Path('config.ini')
    __ID = 0

    def __init__(self, type: str = None, timeout=5):
        self.type = type
        self.__ID = GameBotClient.__ID
        GameBotClient.__ID += 1
        message = f'Socket {self.__ID} Connection Started'.center(100)
        print(f'\r\033[7;35m{message}\033[0m')
        user_config = Path().cwd() / Path('config.ini')
        default_config = Path(__file__).parent / Path('config.ini')
        config = Ini(user_config) if user_config.exists() else Ini(default_config)
        self.server_host = config['NETWORK']['host']
        self.server_port = int(config['NETWORK']['port'])
        self.client_host = config['SERVER']['host']
        self.client_port = config['SERVER']['port']
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.connected = False
        self.timeout = None
        self.header = None

    def connect(self, host=None, port=None):
        connecting(f"Connecting to {self.server_host}:{self.server_port}")
        try:
            self.socket.connect((host or self.server_host, port or self.server_port))
            self.connected = True
            connect(f'{self.server_host}:{self.server_port}')
            if self.type == "bot":
                self.register_bot()
        except ConnectionRefusedError:
            connect(f"Unable to connect with {self.server_host}:{self.server_port}", failed=True)
            self.connected = False

    def register_bot(self):
        data = {
            'server_id': '0',
            'server_name': 'My Server',
            'map': 'Ragnarok',
            'to_address': '127.0.0.1:65432',
            'encoding': 'Stream',
            'registering': True,
            'type': 'bot'
        }
        self.send("register", **data)

    def bot_header(self):
        return {
            'server_id': '0',
            'server_name': 'My Server',
            'map': 'Ragnarok',
            'to_address': '127.0.0.1:65432',
            'encoding': 'Stream',
            'pinging': True,
            'type': 'bot'
        }

    def api_header(self):
        return {
            'server_id': '0',
            'server_name': 'My Server',
            'map': 'Ragnarok',
            'to_address': '127.0.0.1:65432',
            'encoding': 'Stream',
            'type': 'api'
        }

    def disconnect(self):
        if not self.connected:
            return
        disconnecting(f"{self.server_host}:{self.server_port}")
        self.socket.close()
        self.socket = None
        self.connected = False
        disconnect(f"{self.server_host}:{self.server_port}")

    def read_header(self):
        if not self.connected:
            return
        dimension_stream: bytes = self.socket.recv(Header.DIMENSION)
        header_length: int = Header.dimension(dimension_stream)
        header_stream = self.socket.recv(header_length)
        header = Header.decode(header_stream)
        header_length = Header.dimension(dimension)
        return Header.header_stream(self.socket.recv(header_length))

    def readall(self):
        if not self.connected:
            return
        header = self.read_header()
        fragments = bytearray()
        chunk_size = 40  # number of bytes to read at a time
        while len(fragments) < message_length:
            chunk = bytearray(self.socket.recv(chunk_size))  # Should be ready to read
            fragments += chunk
        recv_data = bytes(fragments)
        return recv_data

    def read(self, num_bytes: int = None) -> bytes:
        if num_bytes:
            recv_data = self.socket.recv(num_bytes)
        else:
            recv_data = self.readall()
        stream = Stream(stream=recv_data)
        response(stream.decode())
        return recv_data

    def send(self, data, **kwargs):
        if not self.connected:
            return
        sent(f'{data}')
        if not kwargs:
            if self.type == "bot":
                kwargs.update(self.bot_header())
            elif self.type == "api":
                kwargs.update(self.api_header())
        stream = Stream.new(data, **kwargs)
        self.socket.sendall(stream.encode())
        return Stream(stream=self.read(4096))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __repr__(self):
        attr = {
            'connected': self.connected,
            'host': self.server_host,
            'port': self.server_port
        }
        items = []
        for k, v in attr.items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mGameBotClient\033[0m({args})>\033[0m'

    def __del__(self):
        message = f'Socket {self.__ID} Connection Ended'.center(100)
        print(f'\r\033[7;35m{message}\033[0m')


if __name__ == "__main__":
    class A:
        def __init__(self):
            self.a = 1

        def __getitem_(self, item):
            return self.__dict__[item]

        def keys(self):
            return self.__dict__.keys()

        def __str__(self):
            return f"<A(a={repr(self.a)})>"

        def __repr__(self):
            return f"<A(a={repr(self.a)})>"

if __name__ == "__main__":
    with GameBotClient() as bot:
        response = bot.send(A())

    """
from server.game_bot_client import GameBotClient
with GameBotClient() as bot:
    response = bot.send("Hello world!")
    """

    """
cd ~/Ark-API && python3 -c "from server import GameBotClient; bot = GameBotClient(host='68.126.220.147'); bot.connect(); bot.disconnect()"; cd
cd ~/Ark-API && python3 -c "from server import GameBotClient; bot = GameBotClient(host='172.20.176.1'); bot.connect(); bot.disconnect()"; cd
cd ~/Ark-API && python3 -c "from server import GameBotClient; bot = GameBotClient(host='192.168.56.1'); bot.connect(); bot.disconnect()"; cd
cd ~/Ark-API && python3 -c "from server import GameBotClient; bot = GameBotClient(host='192.168.1.135'); bot.connect(); bot.disconnect()"; cd
cd ~/Ark-API && python3 -c "from server import GameBotClient; bot = GameBotClient(host='192.168.1.254'); bot.connect(); bot.disconnect()"; cd
    """
