import functools

from dbcontroller import SQL as SQLBase
from fastberry import Fastberry, Model
from sqlalchemy.orm import declarative_base

SETTINGS = Fastberry()

try:
    DATABASE_URL = SETTINGS.env.auth_database
except AttributeError as e:
    DATABASE_URL = None
    raise Exception("Environmental Variables <AUTH_DATABASE> is missing!")


# Base
BASE = declarative_base()

# Model
model = Model(sql=BASE)

# Manager
SQL = functools.partial(SQLBase, DATABASE_URL)
