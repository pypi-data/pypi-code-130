"""fsdev CLI"""

from argparse import ArgumentParser
from os import environ
from pathlib import Path

from . import fs
from .web import Server

HOST = "localhost"
PORT = 8000
PARSER = ArgumentParser(description="A simple filesystem-based dev server.")
PARSER.add_argument("command", choices=("serve", "build"),
                    help=("build outputs a static site to a build directory,"
                          "and serve starts a dev server for the site."))


def run():
    """CLI entrypoint
    
    Parses args and calls commands.
    """

    # Get environment
    root = Path(environ.get("SITE_ROOT", "."))

    # Get CLI args
    args = PARSER.parse_args()

    # Route commands
    if args.command == "serve":
        serve(root)
    
    elif args.command == "build":
        build(root)


def serve(root):
    """Serve command
    
    Creates a server on `HOST`:`PORT` serving files from `root` and
    start it"""

    print(f"Server started at http://{HOST}:{PORT}\n\n"
            "  Ctrl+C to exit\n")

    server = Server(HOST, PORT, root)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped.")


def build(root):
    """Build command"""

    fs.build(root)
