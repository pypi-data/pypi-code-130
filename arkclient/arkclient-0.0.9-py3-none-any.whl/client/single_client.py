# echo-client.py
import sys
import socket
import selectors
import types
from time import sleep
from itertools import cycle

HOST = '127.0.0.1'
PORT = 65432


# Run this in python console
def single_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("Requesting to connect")
        s.connect((HOST, PORT))
        while True:
            message = input("Send To Server: ")
            s.sendall(message.encode())
            data = s.recv(1024)
            if "exit" in message:
                print('\033[31mExit client.\033[0m')
                break
            print(f'\033[93m{data.decode()}\033[0m')


if __name__ == "__main__":
    single_client()
