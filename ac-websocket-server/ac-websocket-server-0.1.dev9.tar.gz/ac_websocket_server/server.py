'''Assetto Corsa Websocket Server Class'''

import asyncio
import configparser
import hashlib
import logging
import os
import sys
import websockets

from ac_websocket_server.debug import monitor_tasks
from ac_websocket_server.constants import HOST, PORT
from ac_websocket_server.error import AssettoCorsaWebsocketsServerError
from ac_websocket_server.game import Server
from ac_websocket_server.handlers import handler

EXTRA_DEBUG = False


class AssettoCorsaWebsocketsServer:
    '''Represents an Assetto Corsa WebSocket Server.

    Allows control of an Assetto Corsa server with a websockets interface.'''

    def __init__(self,
                 server_directory: str = None,
                 host: str = HOST,
                 port: int = PORT
                 ) -> None:

        self.__logger = logging.getLogger('ac-ws.ws-server')

        if EXTRA_DEBUG:
            asyncio.get_event_loop().create_task(monitor_tasks())

        self.connected = set()

        self.host = host
        self.port = port

        if not server_directory:
            self.server_directory = os.getcwd()
        else:
            self.server_directory = server_directory

        self.game: Server = None

        self.send_queue = asyncio.Queue()

        self.stop_server: asyncio.Future = None

    async def consumer(self, message):
        self.__logger.debug(f'Received message: {message}')
        if 'start_server' in str(message):
            self.__logger.info('Received request to start game server')
            if not self.game:
                try:
                    self.game = Server(server_directory=self.server_directory)
                    self.game.subscribe(self)
                    await self.game.start()
                    self.__logger.info('Game server started')
                except AssettoCorsaWebsocketsServerError as e:
                    await self.send_queue.put(str(e))
            return
        if 'stop_server' in str(message):
            self.__logger.info('Received request to stop game server')
            if self.game:
                try:
                    await self.game.stop()
                    self.game.unsubscribe(self)
                    self.__logger.info('Game server stopped')
                except AssettoCorsaWebsocketsServerError as e:
                    await self.send_queue.put(str(e))
            return

        response_message = f'Received unrecognised message: {message}'
        await self.send_queue.put(response_message)

    async def handler(self, websocket):

        self.connected.add(websocket)

        await websocket.send(
            f'Welcome to the Assetto Corsa WebSocker server running at {self.host}:{self.port}')

        await handler(websocket, self.consumer, self.producer)

    async def notify(self, notifier):
        '''Receive a notification of a new message from notifier.
        Pull the data off the notifier queue and process.'''

        message = await notifier.get()
        await self.send_queue.put(message)

    async def producer(self):
        data = await self.send_queue.get()
        self.__logger.debug(f'Sending message: {data}')
        return data

    async def start(self):
        '''Start the websocket server'''

        try:

            self.__logger.info(f'Starting websocket server')

            self.stop_server = asyncio.Future()

            async with websockets.serve(self.handler, self.host, self.port):
                await self.stop_server

            self.__logger.info(f'Stopping websocket server')

        except KeyboardInterrupt:
            self.__logger.info(f'Interupting the server')

    async def stop(self):
        '''Stop the websocket server'''

        self.stop_server.set_result()
