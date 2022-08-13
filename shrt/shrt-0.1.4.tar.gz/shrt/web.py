from .app import app
from .database import database
from .views import status, redirect

app.include_router(status.router, prefix='/status', include_in_schema=False)
app.include_router(redirect.router, prefix='', tags=['redirect'], include_in_schema=True)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
