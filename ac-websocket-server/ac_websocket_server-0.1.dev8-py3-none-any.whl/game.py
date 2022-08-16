'''Assetto Corsa Game Server Class'''

import asyncio
from asyncore import read
import configparser
from dataclasses import dataclass, field
from datetime import datetime
from distutils.log import error
from genericpath import isdir
import hashlib
import logging
from mimetypes import init
import os
from posixpath import dirname
import sys
from typing import List
import websockets

from ac_websocket_server.error import AssettoCorsaWebsocketsServerError
from .watcher import Watcher


@dataclass
class Ports:
    '''Represents ports used by AC game server.'''
    http: int
    tcp: int
    udp: int


@dataclass
class Session:
    '''Represents an individual session in the AC game server'''

    type: str
    laps: int
    time: int


@dataclass
class Server:
    '''Represents an Assetto Corsa Server.'''

    server_directory: str

    name: str = field(init=False)
    ports: Ports = field(init=False)
    sessions: List[Session] = field(init=False)

    def __post_init__(self):

        self.__logger = logging.getLogger('ac-ws.game')

        self.__cfg: configparser = None

        self.__queue: asyncio.Queue = asyncio.Queue()

        if os.path.exists(f'{self.server_directory}/acServer.py'):
            self.__cwd = None
            self.__exe = f'{self.server_directory}/acServer.py'
            self.__hash = None
        else:
            self.__cwd = self.server_directory
            if sys.platform == 'linux':
                self.__exe = f'{self.server_directory}/acServer'
                self.__hash = 'f781ddfe02e68adfa170b28d0eccbbdc'
            else:
                self.__exe = f'{self.server_directory}/acServer.exe'
                self.__hash = '357e1f1fd8451eac2d567e154f5ee537'

        if os.path.exists(f'{self.server_directory}/cfg/server_cfg.ini'):

            self.__cfg = configparser.ConfigParser()
            self.__cfg.read(f'{self.server_directory}/cfg/server_cfg.ini')

            self.name = self.__cfg['SERVER']['NAME']

            self.ports = Ports(http=self.__cfg['SERVER']['HTTP_PORT'],
                               tcp=self.__cfg['SERVER']['TCP_PORT'],
                               udp=self.__cfg['SERVER']['UDP_PORT'])

            self.sessions = []

        else:
            self.__logger.error(
                f'Missing server_cfg.ini file in {self.server_directory}')

        if not os.path.exists(f'{self.server_directory}/cfg/entry_list.ini'):
            self.__logger.error(
                f'Missing entry_list.ini file in {self.server_directory}')

        self.__logfile_stdout: str
        self.__logfile_stderr: str

        self.__observers = []

        self.__process: asyncio.subprocess.Process

    async def get(self):
        '''Fetch an item from the queue.  Returns None if the queue is empty.'''

        try:
            response = self.__queue.get_nowait()
        except asyncio.QueueEmpty:
            response = None

        return response

    async def notify(self, notifier):
        '''Receive a notification of a new message from log watcher.'''

        message = await notifier.get()
        await self.put(message)

    async def put(self, item):
        '''Put an item on the queu and notify all observers.'''

        await self.__queue.put(item)
        for obs in self.__observers:
            await obs.notify(self)

    async def start(self):
        '''Start the game server.'''

        if self.__hash:
            try:
                with open(self.__exe, 'rb') as file_to_check:
                    data = file_to_check.read()
                    if self.__hash != hashlib.md5(data).hexdigest():
                        raise AssettoCorsaWebsocketsServerError(
                            f'{self.__exe} checksum mismatch')
            except FileNotFoundError:
                raise AssettoCorsaWebsocketsServerError(
                    f'{self.__exe} missing')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.__logger.info(f'Starting game server')

        os.makedirs(f'{self.server_directory}/logs/session', exist_ok=True)
        os.makedirs(f'{self.server_directory}/logs/error', exist_ok=True)

        self.__logfile_stdout = f'{self.server_directory}/logs/session/output{timestamp}.log'
        self.__logfile_stderr = f'{self.server_directory}/logs/error/error{timestamp}.log'

        session_file = open(self.__logfile_stdout, 'w')
        error_file = open(self.__logfile_stderr, 'w')

        try:
            self.__process = await asyncio.create_subprocess_exec(
                self.__exe, cwd=self.__cwd, stdout=session_file, stderr=error_file)

            self.__logger.info(f'Process pid is: {self.__process.pid}')
            await self.put(f'Assetto Corsa server started')
            await self.put(str(self))
            self.__watcher_stdout = Watcher(self.__logfile_stdout)
            self.__watcher_stdout.subscribe(self)
            await self.__watcher_stdout.start()
        except PermissionError as e:
            self.__logger.error(f'Process did not start: {e}')
            await self.put(f'Assetto Corsa server did not start')
            raise AssettoCorsaWebsocketsServerError(e)

    async def stop(self):
        '''Stop the game server'''

        self.__logger.info(f'Stopping game server')
        await self.put(f'Assetto Corsa server is stopping')

        self.__process.terminate()

        status_code = await asyncio.wait_for(self.__process.wait(), None)
        self.__logger.info(f'Game server exited with {status_code}')

        await self.__watcher_stdout.stop()
        self.__watcher_stdout.unsubscribe(self)

    def subscribe(self, observer):
        '''Subscribe an observer object for state changes.
        Observer object must include an async notify(self, observable, *args, **kwargs) method.'''
        self.__observers.append(observer)

    def unsubscribe(self, observer):
        '''Unsubscribe an observer object.'''
        try:
            self.__observers.remove(observer)
        except ValueError as error:
            self.logger.debug(
                "Unsubscribe failed with value error: %s for %s", error, observer)
