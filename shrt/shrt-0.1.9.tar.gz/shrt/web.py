from .app import app, settings
from .database import database, init_engine
from .utils import redis_init
from .views import status, redirect

app.include_router(status.router, prefix='/status', include_in_schema=False)
app.include_router(redirect.router, prefix='', tags=['redirect'], include_in_schema=True)


@app.on_event("startup")
async def startup():
    init_engine()
    await database.connect()
    if settings.use_cache:
        redis_init(url=settings.redis_url)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
