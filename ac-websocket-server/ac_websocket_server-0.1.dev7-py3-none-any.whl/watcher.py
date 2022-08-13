'''Assetto Corsa Log Watcher'''

from aiowatcher import AIOWatcher
import asyncio
import os
import re
import sys

from .observer import Notifier


class Watcher(Notifier):
    '''Represents a watcher for AC logfiles.   
    Parses log files and sends messages to send_queue.'''

    def __init__(self, filename: str) -> None:
        '''Create Watcher instance for filename.'''

        self.__stop = asyncio.Event()

        self.directory = os.path.dirname(filename)
        self.filename = os.path.basename(filename)

        self.__session_name: str = None
        self.__session_laps: int = None
        self.__session_time: int = None

        self.__driver_host: str = None
        self.__driver_port: int = None
        self.__driver_name: str = None
        self.__driver_guid: str = None
        self.__driver_car: str = None

        super().__init__()

    async def parse_lines(self, file, lines):

        for line in lines:

            '''
            DynamicTrack: first session, resetting grip
            Weather update. Ambient: 17.255133 Road: 23.6746 Graphics: 3_clear
            Wind update. Speed: 0 Direction: 0
            SENDING session name : Practice
            SENDING session index : 0
            SENDING session type : 1
            SENDING session time : 10
            SENDING session laps : 0
            SENDING http://93.57.10.21/lobby.ashx/ping?session=1&timeleft=600&port=9600&clients=0&track=magione&pickup=1
            OK
            '''
            m = re.compile(
                r'^SENDING session name : (.*)').match(line)
            if m:
                self.__session_name = m.group(1)

            m = re.compile(
                r'^SENDING session time : (.*)').match(line)
            if m:
                self.__session_time = int(m.group(1))

            m = re.compile(
                r'^SENDING session laps : (.*)').match(line)
            if m:
                self.__session_laps = int(m.group(1))
                await self.put(f'Starting {self.__session_name} session ' +
                               f'with {str(self.__session_laps)} laps and {str(self.__session_time)} minutes')

            '''
            NEW PICKUP CONNECTION from  192.168.1.1:50834
            VERSION 202
            Mark Hannon
            REQUESTED CAR: bmw_m3_e30*
            ENTRY LIST OPEN MODE 1
            Looking for available slot by name for GUID 76561198005431407 bmw_m3_e30
            Looking for available slot
            Slot found at index 0
            ResetCarResults, index: 0
            DRIVER ACCEPTED FOR CAR 0
            DRIVER ACCEPTED FOR CAR Mark Hannon
            Tyre blankets: false
            Sending SESSION ID : 0
            Sending type 1
            Sending type 2
            Sending type 3
            Sending ID : 0
            Sending type 1
            FIND AND SEND PLAYER'S POSITION
            ELAPSED=70807
            Sending 3 checksum requests
            SERVER TIME: 73273
            DRIVER: Mark Hannon []
            OK
            '''

            m = re.compile(
                r'^NEW PICKUP CONNECTION from  (.*):(\d*)').match(line)
            if m:
                self.__driver_host = m.group(1)
                self.__driver_port = int(m.group(2))

            m = re.compile(
                r'^Looking for available slot by name for GUID (\d*) (.*)').match(line)
            if m:
                self.__driver_guid = m.group(1)
                self.__driver_car = m.group(2)

            m = re.compile(
                r'^DRIVER: (.*) \[.*$').match(line)
            if m:
                self.__driver_name = m.group(1)
                await self.put(f'{self.__driver_name} [{self.__driver_guid}] is joining in a ' +
                               f'{self.__driver_car} from {self.__driver_host}:{self.__driver_port}')

            '''
            Clean exit, driver disconnected:  Mark Hannon []
            '''

            m = re.compile(
                r'^Clean exit, driver disconnected:  (.*) \[.*$').match(line)
            if m:
                await self.put(f'{m.group(1)} left')

            '''
            ERROR,SERVER NOT REGISTERED WITH LOBBY - PLEASE RESTART
            ERROR - RESTART YOUR SERVER TO REGISTER WITH THE LOBBY
            '''

            m = re.compile(
                r'^ERROR.*$').match(line)
            if m:
                await self.put(f'{line}')

    async def start(self):
        '''Start monitoring logfile'''

        self.__stop.clear()

        while not self.__stop.is_set():
            aiow = AIOWatcher(self.directory,
                              self.parse_lines,
                              filename=self.filename)
            await aiow.init()
            await aiow.loop()

    async def stop(self):
        '''Stop monitoring logfile'''

        self.__stop.set()


async def callback(filename, lines):
    for line in lines:
        print(line[:-1])


async def main():
    lw = AIOWatcher('var', callback, extensions=['txt'])
    await lw.tail(3)
