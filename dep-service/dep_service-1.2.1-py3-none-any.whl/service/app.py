"""App."""

from functools import partial
from typing import Dict, List, Type
from service.types import UserSettings
from spec import Spec, load_spec
from logging import getLogger

from spec.types import Plugin, App, Router, JSONResponse, get_openapi

log = getLogger(__name__)

# Use for service maintenance
service_router = Router(prefix='/service', tags=['service'])


@service_router.get('/health')
async def health() -> JSONResponse:
    """Default health."""
    return JSONResponse({'status': 'ok'})


def prepare_routers(
    app: App,
    routers: List[Router] = None,
    service_routes: bool = True,
):
    """Prepare routers."""

    if service_routes:
        app.router.include_router(service_router)

    if routers:
        for router in routers:
            app.router.include_router(router)


def prepare_instance(
    app: App,
    spec: Spec,
    kw: Dict = None,
    plugins: List[Plugin] = None,
    user_settings: Dict = None,
) -> None:
    """Prepare app instance."""
    app.spec = spec
    app.settings = user_settings or None
    app.i18n = print or None  # TODO: (!)

    app.add_event_handler(
        'startup',
        partial(
            prepare_in_async_context,
            app=app,
            spec=spec,
            kw=kw,
            settings=user_settings,
            plugins=plugins,
        ),
    )

    app.add_event_handler(
        'shutdown',
        partial(
            release_in_async_context,
            app=app,
            spec=spec,
            kw=kw,
            plugins=plugins,
        ),
    )


def prepare_openapi(app: App, spec: Spec):
    """Prepare openapi."""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=spec.info.verbose_name or spec.info.tech_name,
        version=spec.info.version,
        description=spec.info.description,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema

    return app.openapi_schema


async def prepare_in_async_context(
    app: App,  # noqa
    spec: Spec,
    kw: Dict = None,
    settings: Dict = None,
    plugins: List[Plugin] = None,
):
    """On app startup."""

    log.warning(
        'Prepare running service',
        extra={'spec': spec.as_dict(), 'kw': kw, 'settings': settings},
    )
    if plugins:
        for plugin in plugins:
            await plugin.prepare(app=app, spec=spec)


async def release_in_async_context(
    app: App,
    spec: Spec,
    kw: Dict = None,
    plugins: List[Plugin] = None,
):
    """On app shutdown."""
    log.warning(
        'Release service resources',
        extra={'app': app, 'spec': spec.as_dict(), 'kw': kw},
    )
    if plugins:
        for plugin in plugins:
            await plugin.release(app=app, spec=spec)


def create(
    routers: List[Router] = None,
    plugins: List[Plugin] = None,
    settings: Type[UserSettings] = None,
    kw: Dict = None,
    service_routes: bool = True,
) -> App:
    """Create service app."""

    spec = load_spec()
    user_settings = settings() if settings else None
    app = App(**kw) if kw else App()

    if plugins:
        for plugin in plugins:
            plugin.inject(app=app, spec=spec)

    prepare_routers(app, routers=routers, service_routes=service_routes)
    prepare_openapi(app=app, spec=spec)
    prepare_instance(
        app=app,
        spec=spec,
        user_settings=user_settings,
        plugins=plugins,
        kw=kw,
    )

    return app
