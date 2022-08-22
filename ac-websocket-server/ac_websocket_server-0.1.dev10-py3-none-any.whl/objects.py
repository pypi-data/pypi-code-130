'''Assetto Corsa Driver Class'''

from dataclasses import dataclass


@dataclass(init=False)
class DriverInfo:
    '''Represents a driver.'''
    name: str
    host: str
    port: int
    car: str
    guid: str
    ballast: int
    msg: str


@dataclass
class ServerInfo:
    '''Represents version information for a server.'''

    version: str = ''
    timestamp: str = ''
    track: str = ''
    cars: str = ''
    msg: str = ''


@dataclass
class SessionInfo:
    '''Represents an individual session in the AC game server'''

    type: str = ''
    laps: int = 0
    time: int = 0
    msg: str = ''
