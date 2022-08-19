import os
import sys
from fastapi import FastAPI
from typing import Dict, Tuple
from multiprocessing import Process
import logging
from getversion import get_module_version
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler((sys.stdout))],
)


log = logging.getLogger(__name__)
if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "../..")
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))

from Configs import getConfig
from buffy.buffyserver.config import DEFAULT

from buffy.buffyserver.api.v1.api import (
    get_v1_router,
    tags_metadata,
)
from buffy.buffyserver.backend.storage.interface import StorageInterface
from buffy.buffyserver.backend.storage.redis_storage import RedisStorage
from buffy.buffyserver.backend.request_download_service.service import (
    RequestDownloaderService,
)
from pathlib import Path, PurePath

config_file_path = PurePath(Path(__file__).parent.resolve(), "config.py")


# atm we only have one storage module (redis)
storage_module_mapping: Dict[str, StorageInterface] = {"redis": RedisStorage}


def _start_api_service():
    import uvicorn

    config: DEFAULT = getConfig(config_classes_pathes=[config_file_path])
    # config: DEFAULT = getConfig()

    app = FastAPI(openapi_tags=tags_metadata)
    storage = storage_module_mapping[config.STORAGE_BACKEND_MODULE](
        **config.STORAGE_BACKEND_CONFIG
    )
    app.include_router(get_v1_router(storage), prefix="/v1")

    uvicorn.run(app, **config.UVICORN_PARAMS)


def _start_backend_service():
    # config: DEFAULT = getConfig()
    config: DEFAULT = getConfig(config_classes_pathes=[config_file_path])
    storage = storage_module_mapping[config.STORAGE_BACKEND_MODULE](
        **config.STORAGE_BACKEND_CONFIG
    )
    service = RequestDownloaderService(
        storage=storage,
        max_simultaneous_downloads=config.DOWNLOAD_SERVICE_MAX_DOWNLOADS,
        max_simultaneous_downloads_per_domain=config.DOWNLOAD_SERVICE_MAX_DOWNLOADS_PER_DOMAIN,
    )
    service.validate_storage_every_n_sec = config.STORAGE_VALIDATE_EVERY_N_SEC
    service.clean_storage_every_n_sec = config.STORAGE_CLEAN_EVERY_N_SEC
    service.validate_storage_at_boot = config.STORAGE_VALIDATE_ON_BOOT
    service.run()


def start_buffy_server(
    env_vars: Dict = None, watchdog: bool = True
) -> Tuple[Process, Process]:
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = v

    import buffy
    import pydantic
    import uvicorn

    config: DEFAULT = getConfig(config_classes_pathes=[config_file_path])
    log.info(f"BuffyServer version: '{get_module_version(buffy)[0]}'")
    log.info(f"Pydantic version: '{get_module_version(pydantic)[0]}'")
    log.info(f"Uvicorn version: '{get_module_version(uvicorn)[0]}'")
    log.info(
        f"Storage config ('STORAGE_BACKEND_CONFIG'): '{config.STORAGE_BACKEND_CONFIG}'"
    )
    log.info(f"Uvicorn config ('UVICORN_PARAMS'): '{config.UVICORN_PARAMS}'")
    # toDo: make a more stuborn watchdog process starter.
    backend = Process(target=_start_backend_service, name="Buffy_backend")
    api = Process(target=_start_api_service, name="Buffy_api_service")
    backend.start()
    api.start()
    if watchdog:
        # todo try n-time to rescue/restart a service
        healthy: bool = True
        while healthy:
            if not backend.is_alive():
                backend.join()
                api.terminate()
                api.join()
                raise ValueError(f"Backend exited with code {backend.exitcode}")
            if not api.is_alive():
                api.join()
                backend.terminate()
                backend.join()
                raise ValueError(f"API Service exited with code {api.exitcode}")
            time.sleep(1)
    return backend, api


if __name__ == "__main__":

    start_buffy_server()
