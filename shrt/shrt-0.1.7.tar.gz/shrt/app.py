from fastapi import FastAPI

from .settings import get_global_settings


settings = get_global_settings()
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)
