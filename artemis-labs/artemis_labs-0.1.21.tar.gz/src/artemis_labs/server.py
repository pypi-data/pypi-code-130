import http.server
import socketserver
from threading import Thread
import os 

# Port
PORT = 8081

# Create server to host files
def host_server():

    # Create server
    try:
        Handler = http.server.SimpleHTTPRequestHandler
        Handler.extensions_map.update({
            ".js": "application/javascript",
        })
        httpd = socketserver.TCPServer(("", PORT), Handler)
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.socket.close()
        exit()

# Main
if __name__ == "__main__":
    server_thread = Thread(target=host_server)
    server_thread.start()