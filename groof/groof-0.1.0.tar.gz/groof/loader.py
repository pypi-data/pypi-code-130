import logging

import mongoengine
import requests
from envparse import env

from .handlers.base import Handler

BOT_TOKEN = env('BOT_TOKEN')
MONGO_DB = env('MONGO_DB')
MONGO_HOST = env('MONGO_HOST', 'localhost')

logger = logging.getLogger('bot')
mongoengine.connect(MONGO_DB, host=MONGO_HOST)
session = requests.Session()


HANDLERS: list[Handler] = []
