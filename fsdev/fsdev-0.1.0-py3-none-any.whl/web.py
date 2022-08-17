from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes

from . import errors
from . import fs

TEMPLATE_MIMETYPES = ("text/html",)


class Server(ThreadingHTTPServer):
    """A simple extension of the built-in `ThreadingHTTPServer` to always use the same
    handler."""

    def __init__(self, host: str, port: int, root: str) -> None:
        super().__init__((host, port), Handler)

        self.root = root


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle indexes
        self.path += "index.html" if self.path[-1] == "/" else ""

        # If partial
        if is_partial(self.path):
            status = 403
            mimetype = "text/html"
            contents = errors.E403

        else:
            status = 200
            mimetype, _ = mimetypes.guess_type(self.path)
            contents = fs.read(self.server.root, self.path)

        # Serve contents
        self.send_response(status)
        self.send_header("Content-type", mimetype)
        self.end_headers()
        self.wfile.write(contents.encode())


def is_partial(path):
    return path[1] == "_"


def is_template(mimetype):
    return mimetype in TEMPLATE_MIMETYPES
    