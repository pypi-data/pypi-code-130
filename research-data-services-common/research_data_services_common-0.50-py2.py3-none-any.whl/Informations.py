from enum import Enum

class LoginMode(Enum):
    credentials = 0
    oauth = 1
    none = 2

class FileTransferMode(Enum):
    active = 0
    passive = 1
    passiveWithLink = 2

class FileTransferArchive(Enum):
    none = 0
    zip = 1