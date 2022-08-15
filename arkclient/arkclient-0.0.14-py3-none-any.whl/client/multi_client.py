# echo-client.py
import sys
import socket
import selectors
import types
from time import sleep
from itertools import cycle

HOST = '127.0.0.1'
PORT = 65432


sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections():
    server_addr = (HOST, PORT)
    for i in range(0, 2):  # 2 connections for messages with array from above
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)


# Run this in python console
def multi_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Requesting to connect")
        s.connect((HOST, PORT))
        while True:
            message = input("Send To Server: ")
            s.sendall(message.encode())
            data = s.recv(1024)
            if "exit" in message:
                print('\033[31mExited client.\033[0m')
                break
            if "exit" in data.decode().lower():
                print('\033[31mServer has stopped running.\033[0m')
                break
            print(f'\033[93mRecieved from server: {repr(data.decode())}\033[0m')


if __name__ == "__main__":
    multi_client()
