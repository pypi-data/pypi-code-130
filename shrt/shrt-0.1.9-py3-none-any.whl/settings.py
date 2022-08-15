from pathlib import Path

from pydantic import BaseSettings, Field, AnyUrl, RedisDsn

from .utils.cache import redis_installed

APP_PATH = Path(__file__).parent.absolute()


class DbDsn(AnyUrl):
    host_required = False


class Settings(BaseSettings):
    app_name: str = 'URL Shortener'
    admin_email: str = 'url@examlpe.com'
    debug: bool = Field(False)
    environment: str = Field('development')

    base_path: Path = APP_PATH.parent.absolute()
    app_path: Path = APP_PATH

    database_url: DbDsn = Field('sqlite:///./redirect.db')

    redis_url: RedisDsn = Field('redis://localhost/0')
    use_cache: bool = Field(redis_installed)

    default_random_length: int = Field(6)


global_settings = None


def get_global_settings():
    global global_settings
    if not global_settings:
        global_settings = Settings()
    return global_settings
