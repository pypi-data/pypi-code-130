"""Spec types."""

from __future__ import annotations

import pathlib

from enum import Enum
from functools import partial
from pydantic import BaseSettings as UserSettings
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Type,
    Tuple,
    Optional,
    Sequence,
)

from fastapi.routing import APIRouter as Router, APIRoute as Route
from fastapi.openapi.utils import OpenAPI, get_openapi
from fastapi.datastructures import Headers
from fastapi import (
    FastAPI as Api,
    datastructures,
    Request,
    Header,
    Path,
    Body,
    Cookie,
    Query,
    Depends,
    Form,
    File,
)
from fastapi.responses import (
    JSONResponse,
    UJSONResponse,
    ORJSONResponse,
    RedirectResponse,
    HTMLResponse,
    StreamingResponse,
    PlainTextResponse,
    FileResponse,
    Response,
)

from fastapi.middleware import Middleware

from spec import fn, exception as exc_type  # noqa


_PLUGIN_REGISTRY = {}


class Environment(str, Enum):
    """Environment.

    Relevant to the git branch name usually.
    Using for logging conditions, sentry environment, etc.
    """

    unknown = 'unknown'

    testing = 'testing'
    develop = 'develop'

    stage = 'stage'
    pre_stage = 'pre-stage'

    production = 'production'
    pre_production = 'pre-production'


@dataclass(frozen=True)
class Socket:
    """Service socket."""

    host: str
    port: int
    scheme: str


@dataclass(frozen=True)
class Runtime:
    """Runtime."""

    debug: bool
    environment: Environment
    entrypoint: str
    testing: bool
    on_k8s: bool


@dataclass(frozen=True)
class Paths:
    """Paths."""

    app: pathlib.Path
    temp: pathlib.Path

    assets: pathlib.Path
    static: pathlib.Path
    media: pathlib.Path
    i18n: pathlib.Path

    pyproject: pathlib.Path
    log_config_name: Optional[str]
    log_config_path: Optional[pathlib.Path]


@dataclass(frozen=True)
class Info:
    """Info."""

    tech_name: str
    verbose_name: str

    description: str
    version: str


@dataclass(frozen=True)
class Policy:
    """Policy."""

    service_workers: int

    db_pool_size: int
    db_max_connections: int

    request_timeout: int
    request_retry_max: int

    scheduler_enabled: bool
    scheduler_persistent: bool
    scheduler_workers: int
    scheduler_instances: int
    scheduler_coalesce: bool
    scheduler_host: str
    scheduler_port: int
    scheduler_db: int


@dataclass(frozen=True)
class I18N:
    """I18N."""

    lang: str

    support_codes: Sequence[str]
    all_codes: Sequence[str]

    locales: Sequence[str]


@dataclass(frozen=True)
class Doc:
    """ApiDoc."""

    prefix: str
    enabled: bool
    blm: bool


def literal_languages() -> Tuple:
    """Literal languages."""
    from .loader import i18n
    params = i18n()
    return tuple(params.all_codes)


Lang = Literal[literal_languages()]  # noqa


@dataclass(frozen=True)
class Spec:
    """Service spec."""

    socket: Socket
    info: Info
    runtime: Runtime
    paths: Paths
    policy: Policy
    i18n: I18N
    doc: Doc
    log_level: str
    sentry_dsn: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        """Spec as dict."""
        return {
            'socket': self.socket,
            'info': self.info,
            'runtime': self.runtime,
            'paths': self.paths,
            'policy': self.policy,
            'doc': self.doc,
            'i18n': self.i18n,
            'sentry_dsn': self.sentry_dsn,
            'log_level': self.log_level,
        }


class ServiceMixin:
    """Service mixin."""

    spec: Spec
    i18n: Callable
    settings: Type[UserSettings] = None

    @staticmethod
    def plugins(fqdn: str) -> Optional[Plugin]:
        """Plugins"""
        return _PLUGIN_REGISTRY.get(fqdn, None)


class App(Api, ServiceMixin):
    """App."""

    pass


class Plugin:
    """Plugin."""

    alias: str

    type_name: str

    middleware: Type[Middleware] = None
    middleware_kw: Dict = None

    env: Dict

    def __init__(self, alias: str, middleware_kw: Dict = None):
        """Init."""
        self.alias = str(alias).lower()
        self.env = fn.alias_plugin_options(
            alias=self.alias,
            plugin=self.type_name,
        )
        self.middleware_kw = middleware_kw

        if self.fqdn not in _PLUGIN_REGISTRY.keys():
            _PLUGIN_REGISTRY[self.fqdn] = self

    def inject(self, app: App, spec: Spec) -> None:
        """Inject application instance before actual hooks call."""

        app.add_event_handler(
            'startup',
            partial(self.prepare, app=app, spec=spec),
        )

        app.add_event_handler(
            'shutdown',
            partial(self.release, app=app, spec=spec),
        )

        if self.middleware:
            if self.middleware_kw:
                app.add_middleware(
                    self.middleware,
                    **self.middleware_kw,
                )
            else:
                app.add_middleware(self.middleware)

    @property
    def fqdn(self) -> str:
        """fqdn."""
        return f'{self.type_name}.{self.alias}'.lower()

    # Export hooks

    async def prepare(self, app: App, spec: Spec):
        """Plugin prepare."""
        pass

    async def release(self, app: App, spec: Spec):
        """Plugin release."""
        pass
