from typing import Dict, Literal, Union
from Configs import ConfigBase


class DEFAULT(ConfigBase):
    LOG_LEVEL: str = "INFO"

    #####################
    ### SERVER PARAMS ##
    ###################

    # UVICORN_PARAMS - json/dict - Configuration of the uvicorn webserver
    # You put any `uvicorn.run` parameter in this dict.
    # See https://www.uvicorn.org/settings/ for all parameters
    UVICORN_PARAMS: Dict = {"port": 8008, "host": "0.0.0.0"}

    STORAGE_MODULE: Literal["redis"] = "redis"

    # STORAGE_CONFIG - json/dict - Configuration for the storage module used.
    # atm only the `redis`-storage-module is supported.
    # The value for key `redis_connection_params` can contain any parameter for the redis python client https://redis.readthedocs.io/en/latest/connections.html#generic-client
    # example:
    # STORAGE_CONFIG = {"file_storage_base_path":"./","redis_connection_params":{"host":"145.23.45.23","port":6379,"password":"s3cret"}}
    STORAGE_CONFIG: Dict = {
        "file_storage_base_path": "./buffy-server-cache",
        "redis_connection_params": {},
    }

    # DOWNLOAD_SERVICE_MAX_DOWNLOADS - int - How many downloads simultaniously should be started in the background?
    DOWNLOAD_SERVICE_MAX_DOWNLOADS: int = 4
    # DOWNLOAD_SERVICE_MAX_DOWNLOADS_PER_DOMAIN - int - How many downloads simultaniously should be started in the background per domain?
    DOWNLOAD_SERVICE_MAX_DOWNLOADS_PER_DOMAIN: int = 1
