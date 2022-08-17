"""App."""

from typing import Dict, List, Type
from service.types import UserSettings
from spec import Spec, load_spec
from logging import getLogger

from spec.types import Module, App, Router, JSONResponse, get_openapi, exc_type

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


def create(
    routers: List[Router] = None,
    modules: List[Module] = None,
    settings: Type[UserSettings] = None,
    kw: Dict = None,
    service_routes: bool = True,
) -> App:
    """Create service app."""

    spec = load_spec()
    user_settings = settings() if settings else None

    app = App(**kw) if kw else App()
    app.settings = user_settings
    app.spec = spec

    prepare_routers(app, routers=routers, service_routes=service_routes)
    prepare_openapi(app=app, spec=spec)

    if modules:
        for module in modules:
            try:
                module.inject(app)
            except Exception as _inject_ext:
                log_extra = {'alias': module.alias}
                if app.spec.runtime.environment.dont_care_secrets():
                    log_extra.update({
                        'spec': spec,
                        'settings': settings,
                        'kw': kw,
                    })
                log.error(
                    f'Inject module {module.alias} error: {_inject_ext}',
                    extra=log_extra,
                )
                raise exc_type.ModuleException(_inject_ext)

    return app
