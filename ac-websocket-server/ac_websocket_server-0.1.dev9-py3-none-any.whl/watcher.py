'''
Assetto Corsa Log Watcher.

Ideas and code from: https://github.com/kuralabs/logserver/blob/master/server/server.py
'''

import asyncio
import logging
import re

import aiofiles


from .observer import Notifier

TAIL_DELAY = 1


class Watcher(Notifier):
    '''Represents a watcher for AC logfiles.
    Parses log files and sends messages to send_queue.'''

    def __init__(self, filename: str) -> None:
        '''Create Watcher instance for filename.'''

        self.__logger = logging.getLogger('ac-ws.watcher')

        self.__filename = filename

        self.__server_version: str
        self.__server_timestamp: str

        self.__session_track: str
        self.__session_cars: str

        self.__session_name: str
        self.__session_laps: int
        self.__session_time: int

        self.__driver_host: str
        self.__driver_port: int
        self.__driver_name: str
        self.__driver_guid: str
        self.__driver_car: str

        self.__readlines_task: asyncio.Task

        super().__init__()

    async def parse_lines(self, _file, lines):
        '''Parse lines of logfile and send messages to observer.'''
        # pylint: disable=invalid-name, pointless-string-statement

        for line in lines:

            '''
            Server CFG Path :  cfg/server_cfg.ini
            Entry List Path :  cfg/entry_list.ini
            Assetto Corsa Dedicated Server v1.15
            Protocol version: 202
            2022-07-22 10:42:32.8776464 +1000 AEST m=+0.007426800
            Num CPU: 1
            LOCAL IP 0: 172.30.0.235
            LOCAL IP 1: fe80::3d63:1f6:80c3:7b07%Ethernet 2
            Using cfg path:  cfg/server_cfg.ini
            Car list:
            _ks_mazda_mx5_cup_
            Client interval HZ: 18
            WARNING: pitstop window needs a valid range
            WARNING: MAX_CONTACTS_PER_KM was 0 or not found, setting to default: 5
            AUTH_PLUGIN_ADDRESS
            Initialising UDP Plugin with target: 127.0.0.1:12001 on the local port 11001
            TRACK=rt_autodrom_most
            CARS=["ks_mazda_mx5_cup"]
            Loading PRACTICE session
            SESSION: Practice
            TYPE=PRACTICE
            TIME=120
            LAPS=0
            OPEN=1
            WAIT TIME=0
            '''

            m = re.compile(
                r'^Assetto Corsa Dedicated Server (.*)').match(line)
            if m:
                self.__server_version = m.group(1)

            m = re.compile(
                r'^(\d{4}-\d{2}-\d{2} .*)$').match(line)
            if m:
                self.__server_timestamp = m.group(1)

            m = re.compile(
                r'^TRACK=(.*)').match(line)
            if m:
                self.__session_track = m.group(1)

            m = re.compile(
                r'^CARS=(.*)').match(line)
            if m:
                self.__session_cars = m.group(1)
                await self.put(f'Connected to Asessto Corsa Dedicated server {self.__server_version} ' +
                               f'at {self.__session_track} running {self.__session_cars} cars')
                await self.put(f'Server up since {self.__server_timestamp}')

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

    async def readlines(self):
        '''Co-routine to be run as a task to read lines from logfile.'''
        #pylint: disable=invalid-name

        self.__logger.debug(f'Started watching {self.__filename}: ')

        async with aiofiles.open(self.__filename, mode='r') as f:

            while True:
                line = await f.readline()
                if line:
                    await self.parse_lines(self.__filename, [line])
                else:
                    await asyncio.sleep(TAIL_DELAY)

        self.__logger.debug(f'Stopped watching {self.__filename}: ')

    async def start(self):
        '''Start monitoring logfile'''

        self.__readlines_task = asyncio.create_task(self.readlines())

    async def stop(self):
        '''Stop monitoring logfile'''

        self.__readlines_task.cancel()
