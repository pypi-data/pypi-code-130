from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, RedirectResponse

from shrt.app import settings
from shrt.database import redirects, database
from shrt.schemas import Redirect
from shrt.utils import get_cache, set_cache

router = APIRouter()


@router.get('/{path}', response_class=RedirectResponse, status_code=302, responses={
    404: {'content': {'text/plain': {'default': 'Page not found'}}}
})
async def redirect(path: str):
    if settings.use_cache:
        cached_result = await get_cache(f'shrt:url:{path}')
        if cached_result:
            return cached_result
    query = redirects.select().where(redirects.c.path == path)
    result = await database.fetch_one(query)
    if not result:
        return PlainTextResponse('Page not found', status_code=404)
    else:
        redirect_obj = Redirect.from_orm(result)
        if settings.use_cache:
            await set_cache(f'shrt:url:{path}', redirect_obj.target, ex=86400*365)
        return redirect_obj.target
