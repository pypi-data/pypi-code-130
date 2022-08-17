# echo-multi-server.py
import sys
import socket
import selectors
import types
from time import sleep
from itertools import cycle

host = "127.0.0.1"  # Standard loopback interface address (localhost)
port = 65432  # Port to listen on (non-privileged ports are > 1023)

selector = None
lsock = None


def set_variables():
    global selector
    global lsock
    global host
    global port
    selector = selectors.DefaultSelector()

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Listening on {host}:{port} (press CTRL-C to close server)")
    lsock.setblocking(False)
    selector.register(lsock, selectors.EVENT_READ, data=None)


def accept_wrapper(sock):
    global selector
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data=data)


def service_connection(key, mask):
    global selector
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            selector.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            client_message = data.outb
            print(f'\033[93mSending to client {data.addr}: {client_message}\033[0m')
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


# Run this on a separate terminal
def multi_server():
    global selector
    try:
        set_variables()
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, exiting\n")
    finally:
        selector.close()


if __name__ == "__main__":
    multi_server()
