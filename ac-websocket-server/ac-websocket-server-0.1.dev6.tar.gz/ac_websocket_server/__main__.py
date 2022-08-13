#!/usr/bin/env python

'''Assetto Corsa Websockets Server.'''

import argparse
import asyncio
import logging
import sys

from ac_websocket_server.constants import HOST, PORT, PROG
from ac_websocket_server.error import AssettoCorsaWebsocketsServerError
from ac_websocket_server.server import AssettoCorsaWebsocketsServer


def get_options(args):
    '''Parse arguments for options.'''

    parser = argparse.ArgumentParser(prog=PROG,
                                     description='''
                                     A web-sockets server to control a local Assetto Corsa Server.''')

    parser.add_argument("--game", type=str,
                        help="acserver root directory")

    parser.add_argument("--host", type=str, default=HOST,
                        help="host to connect/listen")

    parser.add_argument("--port", type=int, default=PORT,
                        help="port to connect/listen")

    parser.add_argument("--verbose", action="store_true",
                        help="show verbose output")

    return parser.parse_args(args)


async def main(args):

    options = get_options(args)

    logger = logging.getLogger('ac-ws')

    if options.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        server = AssettoCorsaWebsocketsServer(host=options.host,
                                              port=options.port,
                                              server_directory=options.game)

        await server.start()

    except AssettoCorsaWebsocketsServerError as e:
        print(f'ERROR: {str(e)}')


if __name__ == '__main__':

    asyncio.run(main(sys.argv[1:]))
