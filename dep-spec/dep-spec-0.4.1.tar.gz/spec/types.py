"""Spec types."""

from __future__ import annotations

import pathlib

from enum import Enum
from pydantic import BaseSettings as UserSettings
from dataclasses import dataclass

from typing import (
    Any,
    Callable,
    Awaitable,
    Dict,
    Literal,
    Type,
    Tuple,
    Optional,
    Sequence,
    Union,
)
from threading import Lock
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


async def callback_prepare_type(
    app: App,  # noqa
    spec: Spec,  # noqa
    extra: Dict = None,  # noqa
) -> None:
    """Callback prepare annotation."""
    pass


async def callback_release_type(
    app: App,  # noqa
    spec: Spec,  # noqa
    extra: Dict = None,  # noqa
) -> None:
    """Callback release annotation."""
    pass


callback_prepare: Callable[
    [App, Spec, Optional[Dict]],
    Awaitable[None],
] = callback_prepare_type


callback_release: Callable[
    [App, Spec, Optional[Dict]],
    Awaitable[None],
] = callback_release_type


ModuleSettings = Union[Dict, None]

CallbackPrepare = Union[callback_prepare, None]
CallbackRelease = Union[callback_release, None]


_keep_thread = Lock()

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

    modules: Dict[str, Module] = None


class App(Api, ServiceMixin):
    """App."""

    pass


class _ModuleMeta(type):
    """Module meta class."""

    def __new__(mcs, name, bases, params):
        """New."""
        cls = super().__new__(mcs, name, bases, params)

        if bases and not cls.alias: # noqa
            assert f'Module `{cls}` has no alias'

        return cls


class ModuleMiddleware:
    """Module middleware."""

    __slots__ = 'app',

    module: Module = None

    def __init__(self, app):
        """Init middleware."""
        self.app = app

    def __call__(self, scope, receive, send) -> None:
        """Call module asgi hook."""
        return self.module.process(scope, receive, send, app=self.app)


class Module(metaclass=_ModuleMeta):
    """Module."""

    alias: str = None

    module_settings: ModuleSettings
    middleware_settings: ModuleSettings

    prepare: CallbackPrepare
    release: CallbackRelease

    def __init__(
        self,
        alias: str,
        app: App = None,
        middleware_settings: Dict = None,
        **module_settings,
    ):
        """Init module."""
        self.alias = str(alias).lower()
        self.module_settings = module_settings
        self.middleware_settings = middleware_settings

        if app:
            self.app = app
            self.inject(app, **module_settings)

    def __call__(
        self,
        app: App,
        middleware_settings: Dict = None,
        **module_settings,
    ):
        self.app = app

        with _keep_thread:
            if not app.modules:
                self.app.modules = dict()
            self.app.modules[self.alias] = self

        if middleware_settings:
            self.middleware_settings.update(middleware_settings)
        if module_settings:
            self.module_settings.update(module_settings)

        return type(
            f'{self.alias}Middleware',
            (ModuleMiddleware,),
            {'module': self},
        )

    def inject(self, app: App, **module_kwargs) -> None:
        """Inject. Calling when app already exists."""

        _runtime = self(
            alias=self.alias,
            app=app,
            middleware_settings=self.middleware_settings,
            **module_kwargs,
        )

        self.app.add_middleware(_runtime)

    # ASGI Interface processing

    def process(self, scope, receive, send, app: App = None):
        """Process ASGI call."""

        app = app or self.app  # noqa

        try:
            if scope['type'] == 'lifespan':
                return self.lifespan(scope, receive, send, app)
            return self.middleware(scope, receive, send, app)
        except Exception as exc:
            return self.exception(exc, scope, receive, send, app)

    def lifespan(self, scope, receive, send, app: App):
        """Lifespan process."""

        async def _hook():
            """Hook by app life span type message."""
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await self.prepare(scope)
            elif message['type'] == 'lifespan.shutdown':
                await self.release(scope)
            return message

        return app(scope, _hook, send)

    # Export

    async def middleware(self, scope, receive, send, app: App):  # noqa
        """Default middleware."""
        return await app(scope, send, receive)

    async def prepare(self, scope):
        """Default prepare method."""
        pass

    async def release(self, scope):
        """Default release method."""
        pass

    def exception(self, exc, scope, receive, send, app: App):
        """Default exception."""
        raise exc


__all__ = (
    'Router',
    'Route',
    'OpenAPI',
    'get_openapi',
    'Headers',
    'Api',
    'datastructures',
    'Request',
    'Header',
    'Path',
    'Body',
    'Cookie',
    'Query',
    'Depends',
    'Form',
    'File',
    'JSONResponse',
    'UJSONResponse',
    'ORJSONResponse',
    'RedirectResponse',
    'HTMLResponse',
    'StreamingResponse',
    'PlainTextResponse',
    'FileResponse',
    'Response',
    'Middleware',
    'CallbackRelease',
    'CallbackPrepare',
    'ModuleSettings',
    'UserSettings',
    'Module',
    'ModuleMiddleware',
    'Lang',
    'Policy',
    'I18N',
    'Paths',
    'Socket',
    'Info',
    'Doc',
    'App',
    'Spec',
    'Environment',
    'Runtime',
    'Socket',
)
