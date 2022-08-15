from typing import Callable, Type
from fastapi.openapi.utils import OpenAPI, get_openapi
from fastapi import FastAPI as Api
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
from fastapi.routing import APIRouter as Router
from pydantic import BaseSettings as UserSettings
from fastapi import (
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

from spec import Spec
from spec.types import Lang


class ServiceMixin:
    """Service mixin."""

    spec: Spec
    i18n: Callable
    settings: Type[UserSettings] = None


class App(Api, ServiceMixin):
    """App."""

    pass


__all__ = (
    'Spec',
    'Api',
    'App',
    'Router',
    'Request',
    'Response',
    'Header',
    'Path',
    'Body',
    'Cookie',
    'Query',
    'Depends',
    'Form',
    'File',
    'Lang',
    'UserSettings',
    'JSONResponse',
    'UJSONResponse',
    'ORJSONResponse',
    'RedirectResponse',
    'HTMLResponse',
    'StreamingResponse',
    'PlainTextResponse',
    'FileResponse',
    'OpenAPI',
    'get_openapi',
)
