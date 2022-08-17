import hashlib
import typing
import inspect
from typing import Dict, Optional, Literal, Union, Type, List
from pydantic import BaseModel, Field
import datetime
import enum
from buffy.buffyserver.api.v1.models_recaching_strategies import ReCachingStrategy
import json

SUPPORTED_HASH_TYPES = typing.Literal[tuple(hashlib.algorithms_guaranteed)]
AVAILABLE_RECHACHING_STRATEGIES = typing.Union[tuple(ReCachingStrategy.list())]
# print("AVAILABLE_RECHACHING_STRATEGIES", AVAILABLE_RECHACHING_STRATEGIES)
# RECACHING_STRATEGIES = typing.Literal[tuple(ReCachingStrategy.str_list())]


class RequestCacheConfiguration(BaseModel):
    request_id: Optional[str]
    # recaching_strategy: Union[ReCachingStrategy.never, ReCachingStrategy.age] = Field(
    #    discriminator="strategy_name"
    # )
    # d = {"propertyName": "strategy_name"}
    recaching_strategy: AVAILABLE_RECHACHING_STRATEGIES = Field(
        default=ReCachingStrategy.never(),
        discriminator="strategy_name",
    )
    max_cached_versions: int = 2

    # To be implemented later # unpack_response: bool = False


class Request_in(BaseModel):
    url: str
    http_method: Literal["get", "post", "put"] = "get"
    http_header_fields: Optional[Dict] = {}

    # https://docs.python-requests.org/en/latest/user/quickstart/#passing-parameters-in-urls
    http_params: Optional[Dict] = {}
    http_request_body: Optional[Dict] = {}
    group_name: Optional[str] = "DEFAULT_GROUP"
    description: Optional[str] = None
    documentation_link: Optional[str] = None
    validation_hash_type: Optional[SUPPORTED_HASH_TYPES] = "md5"
    cache_configuration: Optional[RequestCacheConfiguration] = None

    @property
    def signature(self) -> int:
        return hash(
            (
                self.url,
                self.http_method,
                json.dumps(self.http_header_fields),
                json.dumps(self.http_params),
                json.dumps(self.http_request_body),
                self.group_name,
            )
        )


class Request(Request_in):
    id: Optional[str]
    inital_request_datetime_utc: datetime.datetime = None
    latest_request_datetime_utc: Optional[datetime.datetime] = None
    latest_request_is_processed: bool = None
    cache_configuration: RequestCacheConfiguration

    @classmethod
    def from_request_in(cls, request_in: Request_in) -> "Request":
        if request_in.cache_configuration is None:
            request_in.cache_configuration = RequestCacheConfiguration()
        return cls(**request_in.dict())


class ResponseContentAttributes(BaseModel):
    media_type: Optional[str] = None
    etag: Optional[str] = None
    content_size_bytes: Optional[int] = None
    last_modified_datetime_utc: Optional[datetime.datetime] = None
    filename: Optional[str] = None
    content_disposition: Optional[str] = None

    def is_empty(self):
        return not all(dict(self).values())


class ResponseDownloadStats(BaseModel):
    downloaded_bytes: int = 0
    avg_bytes_per_sec: int = None
    download_running_duration_sec: float = None
    download_start_time_unix_ts: float = None
    total_bytes_to_download: int = None
    state: Literal["init", "downloading", "failed", "finished"]
    error: str = None


class Response(BaseModel):
    id: str = None
    request_id: str
    version: str
    previous_version: Optional[str] = None
    next_version: Optional[str] = None
    status: Literal["wait", "in_progress", "ready", "failed"]
    content_download_path: Optional[str] = None
    cached_datetime_utc: Optional[datetime.datetime] = None
    request_datetime_utc: Optional[datetime.datetime] = None
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
    pinned: Optional[bool] = False
    tags: Optional[List[str]] = None
    valid: Optional[bool] = None
    download_stats: ResponseDownloadStats = None
    content_attributes: ResponseContentAttributes = None
    content_hash_hex: str = None
