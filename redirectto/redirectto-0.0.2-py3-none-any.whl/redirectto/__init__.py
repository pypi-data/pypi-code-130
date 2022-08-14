"""
Basic HTTP server for redirecting all trafic to specific URL.
Pure python no dependencies.
"""

__title__ = 'Redirect TO'
__version__ = '0.0.2'
__author__ = 'Petr Dovnar'
__license__ = 'BSD 3-Clause'

import argparse
import logging
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
     level=logging.INFO,
     format='[%(asctime)s] %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )
log = logging.getLogger(__name__)


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def serve():
    parser = argparse.ArgumentParser(description='Redirects requests to URL')
    parser.add_argument('url', type=str, help='Targer URL for redirects')
    args = parser.parse_args()

    if not args.url:
        log.error('URL is missing')
        exit(1)

    url = args.url

    log.info('Redirect URL: %s', url)

    class RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()

    ip_address = extract_ip()
    port = 3005

    log.info('Listening on http://%s:%d ...', ip_address, port)

    try:
        log.info('Press Ctrl+C to stop server')
        server = HTTPServer((ip_address, port), RedirectHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('Server stopped by user')

    log.info('Done')


if __name__ == '__main__':
    serve()
