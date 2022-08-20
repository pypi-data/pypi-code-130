from dataclasses import dataclass
from typing import Literal, Type, TypeVar

from pydantic import BaseSettings


class AuthConfig(BaseSettings):
    url: str
    cookie_domain: str
    pubkey_path: str


class DatabaseConfig(BaseSettings):
    url: str


class LoggingConfig(BaseSettings):
    format: Literal["console", "json"] = "console"


AnyConfig = TypeVar("AnyConfig", bound=BaseSettings)
ChloreConfig = TypeVar("ChloreConfig", AuthConfig, LoggingConfig, DatabaseConfig)


@dataclass
class _InternalConfig:
    auth: AuthConfig = None
    logging: LoggingConfig = None
    database: DatabaseConfig = None

    def wants(self, type: Type[AnyConfig]) -> bool:
        return type in ChloreConfig.__constraints__

    def register(self, type: Type[ChloreConfig], value: ChloreConfig):
        table = {
            AuthConfig: "auth",
            LoggingConfig: "logging",
            DatabaseConfig: "database",
        }
        setattr(self, table[type], value)


CONFIG = _InternalConfig()


def from_env(t: Type[AnyConfig], with_prefix: str = "") -> AnyConfig:
    class WithPrefix(t):
        class Config:
            env_prefix = with_prefix

    result = WithPrefix()
    if CONFIG.wants(t):
        CONFIG.register(t, result)
    return result
