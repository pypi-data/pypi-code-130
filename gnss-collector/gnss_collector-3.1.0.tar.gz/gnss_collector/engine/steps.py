from enum import IntEnum 

class CollectSteps(IntEnum):
    CREATE = 0 
    CONNECT = 1 
    COLLECT = 3


class DBSteps(IntEnum):
    CREATE = 0 
    CONNECT = 1 
    RECONNECT = 2
    SAVE = 3

class Logger(IntEnum):
    NOTSET = 0
    DEBUG = 10 
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    EXCEPTION = 60


class ORMSteps(IntEnum):
    CONNECT = 1
    DISTRIBUTE = 2
    EXECUTE = 3



class ControlActions(IntEnum):
    ACTIVATE = 0
    MONITOR = 1
