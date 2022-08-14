__title__ = 'sidserver'
__author__ = '.....'
__license__ = '......'
__copyright__ = '......'
__version__ = '2.2'

from .client import Client
from .lib.util import helpers,headers,device

from requests import get
from json import loads

__newest__ = loads(get("https://pypi.org/pypi/sidserver/json").text)["info"]["version"]

if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
