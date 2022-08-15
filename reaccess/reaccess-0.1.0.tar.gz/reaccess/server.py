import socket
import subprocess


class Server(object):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None
    ) -> None:
        if not host:
            host = 'localhost'
        
        if not port:
            port = 2808

        self._password = password

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        address = (host, port)

        self._socket.bind(address)
        self._socket.listen(1)

    def _wait_data(self, client: socket.socket) -> str:
        data = client.recv(1024)
        return data.decode()

    def run(self) -> None:
        while True:
            client, addr = self._socket.accept()

            try:
                if self._password:
                    client.send(b'required_password')
                    
                    while True:
                        password = self._wait_data(client)

                        if self._password == password:
                            client.send(b'logged')
                            break
                        else:
                            client.send(b'incorrect')
                else:
                    client.send(b'logged')

                while True:
                    command = self._wait_data(client)
                
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        universal_newlines=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    while process.poll() is None:
                        output = process.stdout.readline()
                        client.send(output.encode())
                    else:
                        client.send(b'finish')
            except (BrokenPipeError, OSError):
                continue
            except KeyboardInterrupt:
                self._socket.close()
                client.close()
