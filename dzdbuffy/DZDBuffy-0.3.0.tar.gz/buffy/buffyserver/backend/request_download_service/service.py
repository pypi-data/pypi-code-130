from __future__ import annotations
from pathlib import PurePath
from typing import List, Dict, TYPE_CHECKING


import time
import datetime
import logging
import traceback
from buffy.buffyserver.backend.storage.interface import StorageInterface
from buffy.buffyserver.api.v1.models import (
    Request,
    Response,
    ResponseDownloadStats,
)
from buffy.buffyserver.api.v1.models_recaching_strategies import (
    ReCachingStrategy,
    BaseReCachingStrategy,
)
from buffy.buffyserver.backend.request_download_service.queue import (
    RequestDownloadQueue,
    Download,
)

from buffy.buffyserver.backend.storage_janitor import StorageJanitor


log = logging.getLogger(__name__)


class RequestDownloaderService:
    server_tick_min_duration_sec: float = 0.3
    clean_storage_every_n_sec: int = 60
    validate_storage_at_boot: bool = True
    validate_storage_every_n_sec: int = 43200
    # 43200s = 12h
    def __init__(
        self,
        storage: StorageInterface,
        max_simultaneous_downloads: int = 4,
        max_simultaneous_downloads_per_domain: int = 1,
    ):
        self.storage: StorageInterface = storage
        self.downloads: RequestDownloadQueue = RequestDownloadQueue()
        self.max_simultaneous_downloads: int = max_simultaneous_downloads
        self.max_simultaneous_downloads_per_domain: int = (
            max_simultaneous_downloads_per_domain
        )
        self._strategies_states: Dict[str, Dict] = {}
        self.running: bool = False

        self._init_strategy_states()
        if not self.storage.test_connection():
            raise SystemError("Storage backend connection not successful")

        self._janitor = StorageJanitor(storage=self.storage)
        self._last_storage_clean: float = 0.0
        self._last_storage_validation: float = None

    def run(self):
        self._last_storage_validation: float = (
            0.0 if self.validate_storage_at_boot else time.time()
        )
        self.running = True
        while self.running:
            self._clean_and_validate_storage()
            for request in reversed(self.storage.list_requests()):
                if self._local_response_cache_needs_recaching(request):
                    self._create_new_response(request)
                if request.latest_requests:
                    # we reset the list request timings. client can check now if their request was allready processed by the backend. They just need to check if their timestamp is still `latest_requests` aka the wait line
                    request.latest_requests = []
                    request = self.storage.update_request(request)
            self._start_next_response_download()
            self._update_running_response_download_statuses()
            self._dispose_finished_response_downloads()

            time.sleep(self.server_tick_min_duration_sec)

    def _clean_and_validate_storage(self):
        current_time = time.time()
        if current_time - self._last_storage_clean > self.clean_storage_every_n_sec:
            log.debug("Clean storage...")
            self._janitor.cleanup_storage()
            log.debug("...cleaning storage done.")
            self._last_storage_clean = time.time()
        if (
            current_time - self._last_storage_validation
            > self.validate_storage_every_n_sec
        ):
            log.info("Validate storage...")
            self._janitor.verifiy_storage()
            log.info("...validating storage done.")
            self._last_storage_validation = time.time()

    def _init_strategy_states(self):
        for strategy in ReCachingStrategy.list():
            self._strategies_states[strategy.__name__] = {}

    def _local_response_cache_needs_recaching(self, request: Request) -> bool:
        """Depeding on the configured 'ReCachingStrategy' for a request, we determine if the request needs an updated response (aka "does the remote file needs to be downloaded (again)?")

        Args:
            request (Request): _description_

        Returns:
            bool: _description_
        """

        latest_response: Response = self.storage.get_response(
            request_id=request.id, version="latest"
        )

        if not latest_response:
            return True
        if TYPE_CHECKING:
            request.cache_configuration.recaching_strategy: BaseReCachingStrategy = (
                request.cache_configuration.recaching_strategy
            )
        strategy_name = request.cache_configuration.recaching_strategy.strategy_name
        return request.cache_configuration.recaching_strategy.request_needs_recache(
            request=request,
            latest_response=latest_response,
            strategy_state=self._strategies_states[strategy_name],
            storage=self.storage,
        )

    def _create_new_response(self, request: Request):
        version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        previous_respond: Response = None

        # Register next version in version chain
        previous_respond = self.storage.get_response(
            request_id=request.id, version="latest"
        )
        if previous_respond:
            previous_respond.next_version = version
            self.storage.update_response(response=previous_respond)

        response = self.storage.create_response(
            response=Response(
                request_id=request.id,
                status="wait",
                version=version,
                previous_version=previous_respond.version if previous_respond else None,
                status_bytes_downloaded=0,
                request_datetime_utc=request.latest_request_datetime_utc,
                # content_attributes=downloader.get_response_content_attrs(),
            )
        )

        self.downloads.add_download(
            request=request,
            response=response,
            file_target=self.storage.write_response_content(response=response),
        )

    def _start_next_response_download(self):
        for domain in self.downloads.domains:
            if (
                len(self.downloads.get_downloads(by_status="run"))
                >= self.max_simultaneous_downloads
            ):
                return
            elif (
                len(self.downloads.get_downloads(by_domain=domain, by_status="run"))
                >= self.max_simultaneous_downloads_per_domain
            ):
                continue
            elif (
                len(self.downloads.get_downloads(by_domain=domain, by_status="wait"))
                == 0
            ):
                continue
            else:
                waiting_downloads: List[Download] = self.downloads.get_downloads(
                    by_domain=domain, by_status="wait"
                )
                waiting_downloads[0].thread.start()
                log.debug(f"STARTED DOWNLOAD {waiting_downloads[0].request}")

    def _update_running_response_download_statuses(self):
        running_downloads: List[Download] = self.downloads.get_downloads(
            by_status="run"
        )
        for download in running_downloads:
            download.response.download_stats = download.downloader.status
            download.response.status = "in_progress"
            if (
                download.response.content_attributes is None
                or download.response.content_attributes.is_empty()
            ):
                download.response.content_attributes = (
                    download.downloader.get_response_content_attrs(cached_only=True)
                )
            self.storage.update_response(download.response)

    def _dispose_finished_response_downloads(self):
        finished_downloads: List[Download] = self.downloads.get_downloads(
            by_status="finished"
        )
        download_to_clean: List[Download] = []
        for download in finished_downloads:
            tb = None
            try:
                download.thread.join(timeout=0.6)
            except Exception as e:
                tb = traceback.format_exc()
                log.error(tb)
                download.thread.failed = True
            if download.thread.failed:
                download.response.status = "failed"
                if not download.response.download_stats:
                    download.response.download_stats = ResponseDownloadStats()
                download.response.download_stats.error = (
                    tb if tb else download.thread.error_stack_trace
                )
            else:
                download.response.status = "ready"
                download.response.cached_datetime_utc = datetime.datetime.utcnow()
                download.response.download_stats = download.downloader.status
                download.response.content_hash_hex = download.downloader.hash
                download.response.content_download_path = str(
                    PurePath(
                        "request",
                        download.request.id,
                        "response",
                        "v",
                        download.response.version,
                        "content",
                    )
                )
                download.response.content_attributes = (
                    download.downloader.get_response_content_attrs(cached_only=True)
                )

            self.storage.update_response(download.response)
            download_to_clean.append(download)
        for download in download_to_clean:
            self.downloads.remove_download(download=download)
