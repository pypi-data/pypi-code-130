import socket


class Client(object):
    def __init__(self, host: str = None, port: int = None) -> None:
        if not host:
            host = 'localhost'
        
        if not port:
            port = 2808

        address = (host, port)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(address)

    def required_password(self) -> bool:
        connect_info = self._socket.recv(1024)
        return connect_info.decode() == 'required_password'

    def check_password(self, password: str) -> bool:
        self._socket.send(password.encode())
        result = self._socket.recv(1024)
        return result.decode() == 'logged'

    def send_command(self, command: str) -> None:
        self._socket.send(command.encode())
        result = self._socket.recv(1024).decode()

        while result != 'finish':
            print(result)
            result = self._socket.recv(1024).decode()
