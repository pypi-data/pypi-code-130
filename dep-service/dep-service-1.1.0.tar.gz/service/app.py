"""App."""

from functools import partial
from typing import Dict, List, Type
from service.types import UserSettings
from spec import Spec, load_spec
from logging import getLogger

from .types import App, Router, JSONResponse


log = getLogger(__name__)

# Use for service maintenance
service_router = Router(prefix='/service', tags=['service'])


@service_router.get('/health')
async def health() -> JSONResponse:
    """Default health."""
    return JSONResponse({'status': 'ok'})


async def prepare(
    app: App,
    spec: Spec,
    kw: Dict = None,
    settings: Dict = None,
):
    """On app startup."""
    log.warning(
        'Prepare running service',
        extra={'spec': spec.as_dict(), 'kw': kw, 'settings': settings},
    )


async def release(app: App, spec: Spec, kw: Dict = None):
    """On app shutdown."""
    log.warning(
        'Release service resources',
        extra={'app': app, 'spec': spec.as_dict(), 'kw': kw},
    )


def create(
    routers: List[Router] = None,
    settings: Type[UserSettings] = None,
    kw: Dict = None,
    disable_service_routes: bool = False,
) -> App:
    """Create service app."""

    spec = load_spec()
    user_settings = settings() if settings else None
    app = App(**kw) if kw else App()

    app.add_event_handler(
        'startup',
        partial(prepare, app=app, spec=spec, kw=kw, settings=user_settings),
    )

    app.add_event_handler(
        'shutdown',
        partial(release, app=app, spec=spec, kw=kw),
    )

    if not disable_service_routes:
        app.router.include_router(service_router)

    if routers:
        for router in routers:
            app.router.include_router(router)

    app.spec = spec
    app.settings = settings() if settings else None

    app.i18n = print

    return app
