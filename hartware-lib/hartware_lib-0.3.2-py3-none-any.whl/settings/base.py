from pydantic import BaseSettings, Field

from hartware_lib.pydantic.field_types import BooleanFromString


class AppBaseSettings(BaseSettings):
    testing: BooleanFromString = Field(default=False, env="TEST")
    debug: BooleanFromString = Field(default=False, env="DEBUG")
