# echo-multi-server.py
import sys
import socket
import selectors
import types
from time import sleep
from itertools import cycle

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


# Run this on a separate terminal
def single_server():
    print("Entering socket")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Binding")
        s.bind((HOST, PORT))
        print("Listening")
        s.listen()
        print("Accepting...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if "exit" in data.decode().lower():
                    print('\033[31mExit server.\033[0m')
                    break
                message = f"\nServer Received:\n\t\"{data.decode()}\"\n".encode()
                print(message.decode())
                conn.sendall(message)


if __name__ == "__main__":
    single_server()
