from functools import cache
from genericpath import isfile
from http import client
import io
import ssl
from typing import Dict, Literal, List, Optional, Union, Iterator
import logging
from xml.dom import ValidationErr
from buffy.buffyserver.api.v1.models import (
    Request as ApiRequest,
    Request_in as ApiRequest_in,
    Response as ApiResponse,
    ResponseDownloadStats,
)
from buffy.buffyserver.api.v1.models_recaching_strategies import ReCachingStrategy
from buffy.buffyserver.api.v1.models import RequestCacheConfiguration

from pathlib import Path, PurePath
from buffy.tools.stuborn_downloader import StubornDownloader
import requests
from io import FileIO
import tempfile
import tqdm
import threading
import time
from pydantic import parse_obj_as, parse_raw_as
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

log = logging.getLogger(__name__)


class BuffyServerError(Exception):
    pass


class BuffyCacheEmptyError(Exception):
    pass


class BuffyPyClient:
    buffy_server_timeout_sec = 3

    class Request:
        def __init__(self, request: ApiRequest_in, client: "BuffyPyClient"):
            self._client = client
            self._api_request_in: ApiRequest_in = request
            self._api_request: ApiRequest = None
            self._api_response: ApiResponse = None
            self._use_local_download: bool = False
            self._local_downloader: StubornDownloader = None
            self._local_temp_file: FileIO = None
            self.force_version: str = None
            self.prefere_version: str = None
            self.prefere_tag: str = None
            self.prefere_pinned: bool = False
            self.prefere_cached_instead_of_waiting: bool = False
            self.fallback_to_older_version = True
            self.buffy_server_http_headers: Dict = {}
            self.buffy_server_http_auth: HTTPBasicAuth = None

        @property
        def cache_configuration(self) -> RequestCacheConfiguration:
            if not self._api_request:
                return self._api_request_in.cache_configuration
            else:
                return self._api_request.cache_configuration

        @cache_configuration.setter
        def cache_configuration(self, cache_configuration: RequestCacheConfiguration):
            if not self._api_request:
                self._api_request_in.cache_configuration = cache_configuration
            else:
                self._api_request.cache_configuration = cache_configuration
                try:
                    res = requests.put(
                        f"{self._client.api_url}/request/{self._api_request.id}/cache-config",
                        data=cache_configuration.json()
                        if cache_configuration
                        else None,
                        timeout=self._client.buffy_server_timeout_sec,
                        headers=self.buffy_server_http_headers,
                        auth=self.buffy_server_http_auth,
                    )
                    res.raise_for_status()
                except requests.exceptions.ConnectionError as e:
                    log.warning(
                        f"Can not reach BuffyServer @ '{self._client.api_url}'. Cache configuration is not updated on server side."
                    )

        def order(self):
            try:
                res: requests.Response = requests.put(
                    f"{self._client.api_url}/request/",
                    data=self._api_request_in.json(),
                    timeout=self._client.buffy_server_timeout_sec,
                    verify=False,
                    headers=self._client.http_headers,
                    auth=self._client.http_auth,
                )
                res.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                if self._client.local_download_fallback:
                    log.warning(
                        f"Can not reach BuffyServer @ '{self._client.api_url}'. Fallback to local uncached download."
                    )
                    self._use_local_download = True
                    self.download_thread = threading.Thread(target=self._local_download)
                    self.download_thread.start()
                    return
                else:
                    log.error(f"Can not reach BuffyServer @ '{self._client.api_url}'.")
                    raise e

            self._api_request: ApiRequest = ApiRequest.parse_raw(res.content)
            if (
                self._api_request_in.cache_configuration
                and self._api_request_in.cache_configuration
                != self._api_request.cache_configuration
            ):
                # the caller updated the cache config. lets update on server side
                self.cache_configuration = self._api_request_in.cache_configuration
            self._wait_for_request_processed()

        def _wait_for_request_processed(self):
            """Wait until the request is processed by the backend and a possible response had arrived in the database"""
            if self._api_request is None:
                raise ValidationErr(
                    f"Request for '{self._api_request_in.url}' must be started with method 'BuffyPyClient.Request.order() first'"
                )
            while not self._api_request.latest_request_is_processed:
                res: requests.Response = requests.get(
                    f"{self._client.api_url}/request/{self._api_request.id}",
                    headers=self.buffy_server_http_headers,
                    auth=self.buffy_server_http_auth,
                )
                res.raise_for_status()
                updated_api_request: ApiRequest = ApiRequest.parse_raw(res.content)
                if (
                    self._api_request.latest_request_datetime_utc
                    != updated_api_request.latest_request_datetime_utc
                ):
                    # another client requested the same resource. we now assume our request is processed. This is a dirty workaround for now...
                    # a better solution would be to have identifiert for every single request made and a api endpoint to query if this certain request is processed.
                    self._api_request = updated_api_request
                    self._api_request.latest_request_is_processed = True
                else:
                    self._api_request = updated_api_request
                time.sleep(0.1)

        def _wait_for_response_completion(
            self, render_progressbar: bool = False, timeout_sec: int = None
        ):
            if timeout_sec or render_progressbar:
                raise NotImplementedError()
            is_complete: bool = False
            while not is_complete:
                stats: ResponseDownloadStats = self._get_download_stats()
                if stats.state == "finished":
                    return
                if stats.state == "failed":
                    raise BuffyServerError(stats.error)
                time.sleep(0.3)

        def _wait_for_response_content_attributes(self, timeout_sec: int = None):
            if timeout_sec:
                raise NotImplementedError()
            if self._use_local_download:
                self._local_downloader.get_response_content_attrs()
            else:
                is_complete: bool = False
                while not is_complete:
                    resp = self._find_response()

                    if resp.content_attributes.filename is not None:
                        return
                    time.sleep(0.3)

        def _find_response(self, override_prefere_version: str = None) -> ApiResponse:
            # Check if we already called _find_response() and found a response
            if self._api_response:
                # update state of reponse
                self._get_download_stats(response=self._api_response)
                if self._api_response.status != "failed":
                    # if the state of the reponse is healthy we can serve it.
                    # otherwise we continue the function and need to find another one
                    return self._api_response
            prefer_version = (
                override_prefere_version
                if override_prefere_version
                else self.prefere_version
            )
            if self._use_local_download:
                return None

            elif (
                not (
                    prefer_version
                    or self.prefere_tag
                    or self.prefere_pinned
                    or self.prefere_cached_instead_of_waiting
                )
                and self._api_request is None
            ):
                raise ValidationErr(
                    f"Request for '{self._api_request_in.url}' must be started with method 'BuffyPyClient.Request.order() first'"
                )

            response: ApiResponse = None
            if prefer_version:
                # The client pefers a certain version.

                response_url: str = f"{self._client.api_url}/request/{self._api_request.id}/v/{prefer_version}"
                response_raw = requests.get(
                    response_url,
                    headers=self.buffy_server_http_headers,
                    auth=self.buffy_server_http_auth,
                ).content
                if not response_raw and self.force_version:
                    raise ValueError(
                        f"Can not get BuffyResponse at '{response_url}'. Probably version '{prefer_version}' set in BuffyClient.Request.prefere_version is not existent"
                    )
                response = ApiResponse.parse_raw(response_raw)
                if (
                    not self.prefere_cached_instead_of_waiting
                    and response.status != "failed"
                    or self.force_version
                ):
                    # no matter if this response is still downloading, the client wants this version
                    return response
            if not prefer_version or not response:
                all_responses_raw = requests.Response = requests.get(
                    f"{self._client.api_url}/request/{self._api_request.id}/response",
                    headers=self.buffy_server_http_headers,
                    auth=self.buffy_server_http_auth,
                ).content
                buffy_responses: List[ApiResponse] = parse_raw_as(
                    List[ApiResponse], all_responses_raw
                )
                for resp in buffy_responses:
                    if resp.tags and self.prefere_tag in resp.tags:
                        response = resp
                    if self.prefere_pinned and resp.pinned:
                        response = resp
                if not response and buffy_responses:
                    # we just take the latest response
                    response = buffy_responses[-1]
            if (
                self.prefere_cached_instead_of_waiting
                and response.status in ["wait", "in_progress"]
                and response.previous_version
            ) or response.status == "failed":
                if response.previous_version:
                    response = self._find_response(
                        override_prefere_version=response.previous_version
                    )
                elif response.status == "failed":
                    raise BuffyCacheEmptyError(
                        f"Current response for request '{self._api_request.url}' failed to download and no previous version is cached. sorry!"
                    )
            self._api_response = response
            return response

        def download_response_content(self, chunk_size: int = 65536) -> Iterator:
            self._wait_for_response_completion()
            if not self._use_local_download:
                response = self._find_response()
                download_url = (
                    f"{self._client.api_url}/{response.content_download_path}"
                )
                with requests.get(
                    download_url,
                    headers=self.buffy_server_http_headers,
                    auth=self.buffy_server_http_auth,
                    stream=True,
                ) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        yield chunk
            else:
                self._local_temp_file.seek(0)
                while True:
                    chunk = self._local_temp_file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        def get_filename(self, fallback_filename="download") -> Union[str, None]:
            self._wait_for_response_content_attributes()

            if self._use_local_download:
                filename = self._local_downloader.get_response_content_attrs(
                    cached_only=True
                ).filename
            else:
                filename = self._find_response().content_attributes.filename
            return filename if filename else fallback_filename

        def download_response_content_to(
            self, target: Union[str, Path, FileIO] = None, dir: Union[str, Path] = None
        ) -> Path:
            file = target
            if dir and target:
                raise ValueError("Use target or dir as filesink not both")
            if dir:
                target = Path(PurePath(dir, self.get_filename()))
            if isinstance(target, str):
                target = Path(target)
            if isinstance(target, Path):
                file = open(target, "wb")
            for chunk in self.download_response_content():
                file.write(chunk)
            if isinstance(target, (str, Path)):
                # We only close the file object if we created ourselves
                file.close()
            return target

        def _local_download(self):
            # in extra thread option?
            self._local_downloader = StubornDownloader(self._api_request_in)
            self._local_downloader.CLOSE_FILE_OBJ = False
            self._local_temp_file = tempfile.TemporaryFile()
            self._local_downloader.download(file_obj=self._local_temp_file)

        def _wait_for_local_download(self):
            raise NotImplementedError()

        def _get_download_stats(
            self, response: ApiResponse = None
        ) -> ResponseDownloadStats:
            if self._use_local_download:
                return self._local_downloader.status
            else:
                # update response status
                response_url: str = f"{self._client.api_url}/request/{self._api_request.id}/response/v/{response.version if response else self._find_response().version}"
                response_raw = requests.get(
                    response_url,
                    headers=self.buffy_server_http_headers,
                    auth=self.buffy_server_http_auth,
                ).content
                self._api_response = ApiResponse.parse_raw(response_raw)
                return self._api_response.download_stats

        def __del__(self):
            if self._local_temp_file and not self._local_temp_file.closed:
                self._local_temp_file.close()

    def __init__(
        self,
        url: str = None,
        host: str = None,
        port: int = 8008,
        base_path: str = None,
        group_name: str = None,
        api_version: Literal["v1"] = "v1",
        ssl: bool = True,
        http_auth: HTTPBasicAuth = None,
        http_headers: Dict = {},
        local_download_fallback: bool = True,
    ):
        self.http_auth = None
        if not host and not url:
            host = "localhost"
        if host:
            self.ssl = ssl
            self.host = host
            self.port = port
            self.base_path = base_path
        elif url:
            parsed_url = urlparse(url)
            self.ssl = True if parsed_url.scheme in ["https", None] else False
            self.host = parsed_url.hostname
            if not parsed_url.port and not self.ssl:
                self.port = 80
            elif not parsed_url.port and self.ssl:
                self.port = 443
            elif parsed_url.port:
                self.port = parsed_url.port

            self.base_path = parsed_url.path
            if parsed_url.username:
                self.http_auth = HTTPBasicAuth(
                    username=parsed_url.username, password=parsed_url.password
                )

        if http_auth:
            self.http_auth = http_auth
        self.http_headers = http_headers
        self.group_name = group_name
        self.api_version = api_version
        self.local_download_fallback = local_download_fallback

    @property
    def api_url(self):
        api_url = f"http{'s' if self.ssl else ''}://{self.host}:{self.port}/{self.base_path + '/' if self.base_path else ''}{self.api_version}"
        log.debug(f"api_url: {api_url}")
        return api_url

    def create_request(
        self,
        url: str,
        http_method: Literal["get", "post", "put"] = "get",
        http_params: Dict = {},
        http_request_body: Optional[Dict] = {},
        http_header_fields: Dict = {},
        info_description: str = None,
        info_link: str = None,
        hold_download_start: bool = False,
        cache_configuration: RequestCacheConfiguration = None,
    ) -> "BuffyPyClient.Request":
        api_req = ApiRequest_in(url=url)
        api_req.http_method = http_method
        api_req.http_params = http_params
        api_req.http_request_body = http_request_body
        api_req.http_header_fields = http_header_fields
        api_req.description = info_description
        api_req.documentation_link = info_link
        api_req.cache_configuration = cache_configuration

        req = BuffyPyClient.Request(api_req, self)
        if hold_download_start:
            return req
        req.order()
        return req
