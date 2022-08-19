"""Spec types."""

from __future__ import annotations

import asyncio

from enum import Enum
from pathlib import Path as PPath
from pydantic import BaseSettings as UserSettings
from dataclasses import dataclass
from logging import getLogger

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

from poetry.core.pyproject import PyProjectTOML as PyProject
from fastapi.middleware import Middleware

from spec import fn, exception as exc_type  # noqa
from spec.loader import load_spec, load_i18n

log = getLogger(__name__)

AsyncIOErrors = (
    asyncio.CancelledError,
    asyncio.IncompleteReadError,
    asyncio.InvalidStateError,
    asyncio.TimeoutError,
)


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
    """Service environment.

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

    def dont_care_secrets(self) -> bool:
        """If is unimportant by secrets or others."""
        return self in (
            Environment.stage,
            Environment.pre_stage,
            Environment.develop,
            Environment.testing,
            Environment.unknown,
        )


@dataclass(frozen=True)
class URI:
    """Service uri."""

    host: str
    port: int
    scheme: str


@dataclass(frozen=True)
class Status:
    """Service status."""

    debug: bool
    testing: bool
    on_k8s: bool


@dataclass(frozen=True)
class Path:
    """Service paths."""

    app: PPath
    temp: PPath

    assets: PPath
    static: PPath
    media: PPath
    i18n: PPath

    pyproject: PPath
    log_config_name: Optional[str]
    log_config_path: Optional[PPath]


@dataclass(frozen=True)
class Service:
    """Service  params."""

    uri: URI
    entrypoint: str

    # from env  (TODO: or from tech_name)
    name: str

    # from poetry config
    tech_name: str
    tech_description: str
    tech_version: str


@dataclass(frozen=True)
class Policies:
    """Service policies."""

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
    """Service i18n localizations."""

    lang: str

    support_codes: Sequence[str]
    all_codes: Sequence[str]

    locales: Sequence[str]


@dataclass(frozen=True)
class ApiDoc:
    """Service api doc options."""

    prefix: str
    enabled: bool
    blm: bool


def literal_languages() -> Tuple:
    """Literal languages."""
    params = load_i18n()
    return tuple(params.all_codes)


Lang = Literal[literal_languages()]  # noqa


@dataclass(frozen=True)
class Profile:
    """Service profiling options."""

    log_level: str
    sentry_dsn: Optional[str] = None


@dataclass(frozen=True)
class Spec:
    """Service spec."""

    service: Service
    environment: Environment
    status: Status

    path: Path
    pyproject: PyProject

    policies: Policies
    i18n: I18N
    api_doc: ApiDoc

    profile: Profile

    def as_dict(self) -> Dict[str, Any]:
        """Spec as dict."""
        return {
            'pyproject': self.pyproject,
            'environment': self.environment,
            'service': self.service,
            'status': self.status,
            'path': self.path,
            'policies': self.policies,
            'api_doc': self.api_doc,
            'i18n': self.i18n,
            'profile': self.profile,
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

    active: bool = True

    module_settings: ModuleSettings
    middleware_settings: ModuleSettings

    prepare: CallbackPrepare
    release: CallbackRelease

    def __init__(
        self,
        alias: str = None,
        app: App = None,
        middleware_settings: Dict = None,
        **module_settings,
    ):
        """Init module."""
        self.alias = Module.alias_lookup(alias, self)
        self.module_settings = module_settings
        self.middleware_settings = middleware_settings
        print('----------------')
        if app:
            self.app = app
            self.inject(app, **module_settings)

    @staticmethod
    def alias_lookup(alias, module) -> str:
        """Alias lookup."""
        fallback_alias = str(module.__class__.__name__).lower()
        return str(alias).lower() if alias else fallback_alias

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
        log_extra = {'alias': self.alias}

        if app.spec.environment.dont_care_secrets():
            log_extra.update({
                'module_settings': self.module_settings,
                'middleware_settings': self.middleware_settings,
            })

        try:
            _runtime = self(
                alias=self.alias,
                app=app,
                middleware_settings=self.middleware_settings,
                **module_kwargs,
            )
        except Exception as _module_exc:
            log.error(f'Inject module: {_module_exc}', extra=log_extra)
            raise exc_type.ModuleException(_module_exc)

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
            log.error(
                f'Asgi module error: {exc}',
                extra={
                    'alias': self.alias,
                    'exc': exc,
                    'scope': scope,
                    'receive': receive,
                    'send': send,
                },
                exc_info=True,
            )
            return self.exception(exc, scope, receive, send, app)

    def lifespan(self, scope, receive, send, app: App):
        """Lifespan process."""

        async def _hook():
            """Hook by app life span type message."""

            message = await receive()

            log_extra = {'alias': self.alias, 'receive': message}
            if self.app.spec.environment.dont_care_secrets():
                log_extra.update({
                    'module_settings': self.module_settings,
                    'middleware_settings': self.middleware_settings,
                })

            if message['type'] == 'lifespan.startup':
                try:
                    await self.prepare(scope)
                except Exception as _prepare_exc:
                    self.active = False
                    log.error(
                        f'Prepare module error: {_prepare_exc}',
                        extra=log_extra,
                    )

            elif message['type'] == 'lifespan.shutdown':
                await self.release(scope)
            elif message['type'] == 'lifespan.startup.failed':
                self.active = False
            return message

        return app(scope, _hook, send)

    # Export

    async def middleware(self, scope, receive, send, app: App):  # noqa
        """Expose default middleware."""
        await app(scope, receive, send)

    async def prepare(self, scope):
        """Expose default prepare."""
        pass

    async def release(self, scope):
        """Expose release."""
        pass

    def exception(self, exc, scope, receive, send, app: App):
        """Expose exception."""
        raise exc_type.ModuleException(exc_type)


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
    'Policies',
    'I18N',
    'Path',
    'URI',
    'Service',
    'ApiDoc',
    'App',
    'Spec',
    'Environment',
    'Status',
    'exc_type',
    'load_spec',
    'PyProject',
)
