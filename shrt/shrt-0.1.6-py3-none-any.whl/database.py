import databases
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, Index, create_engine

from .settings import get_global_settings

metadata = MetaData()
settings = get_global_settings()
database = databases.Database(settings.database_url)
global_engine = None

redirects = Table(
    'redirect',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('path', String, unique=True),
    Column('target', String),
    Column('is_custom', Boolean, default=False),
)

Index('custom_targets', redirects.c.target, redirects.c.is_custom)


def get_engine():
    global global_engine
    if not global_engine:
        global_engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})
        metadata.create_all(global_engine)
    return global_engine
