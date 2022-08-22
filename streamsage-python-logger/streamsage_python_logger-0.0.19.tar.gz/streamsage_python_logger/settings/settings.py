from pydantic import BaseModel, BaseSettings, Field


class LoggerSettings(BaseSettings):
    APP_CONTEXT: str = Field("NoneContextApp", env='LOG_SDK_CONTEXT')
    LOG_SDK_TRANSPORTS: str = Field("default", env="LOG_SDK_TRANSPORTS")
    LOG_SDK_TRANSPORT_FLUENT_URL: str = Field('fluent:24224', env='LOG_SDK_TRANSPORT_FLUENT_URL')
    LOG_SDK_TRANSPORT_FLUENT_LEVEL: str = Field("TRACE", env="LOG_SDK_TRANSPORT_FLUENT_LEVEL")
    LOG_SDK_TRANSPORT_FLUENT_TIMEOUT: float = Field(3.0, env="LOG_SDK_TRANSPORT_FLUENT_TIMEOUT")
    LOG_SDK_TRANSPORT_CONSOLE_LEVEL: str = Field("TRACE", env="LOG_SDK_TRANSPORT_CONSOLE_LEVEL")
