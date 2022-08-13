from argparse import ArgumentParser
from htsct.db.main import App


class CLICommand:
    """gui
    """

    @staticmethod
    def add_argments(parser: ArgumentParser):
        add = parser.add_argument
        add("--port", default=8000, dest="port")
        add("--host", default="0.0.0.0", dest="host")

    @staticmethod
    def run(args, parser):
        host = args.host
        port = args.port
        App(host, port).run()
