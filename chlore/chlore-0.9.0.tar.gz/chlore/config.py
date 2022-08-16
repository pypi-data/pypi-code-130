from dataclasses import dataclass
from typing import Literal, Type, TypeVar

from pydantic import BaseSettings


class LoggingConfig(BaseSettings):
    format: Literal["console", "json"] = "console"


class DatabaseConfig(BaseSettings):
    url: str


AnyConfig = TypeVar("AnyConfig", bound=BaseSettings)
ChloreConfig = TypeVar("ChloreConfig", LoggingConfig, DatabaseConfig)


@dataclass
class _InternalConfig:
    logging: LoggingConfig = None
    database: DatabaseConfig = None

    def wants(self, type: Type[AnyConfig]) -> bool:
        return type in ChloreConfig.__constraints__

    def register(self, type: Type[ChloreConfig], value: ChloreConfig):
        table = {
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
