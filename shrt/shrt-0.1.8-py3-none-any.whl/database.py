import databases
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, Index, create_engine
from sqlalchemy.engine import Engine

from .settings import get_global_settings

metadata = MetaData()
settings = get_global_settings()
database: databases.Database = databases.Database(settings.database_url)
engine: Engine = None

redirects = Table(
    'redirect',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('path', String, unique=True),
    Column('target', String),
    Column('is_custom', Boolean, default=False),
)

Index('custom_targets', redirects.c.target, redirects.c.is_custom)


def init_engine(apply_schema: bool = False):
    global engine
    if not engine:
        engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})
        if apply_schema:
            metadata.create_all(engine)
