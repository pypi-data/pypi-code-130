from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, RedirectResponse

from shrt.database import redirects, database
from shrt.schemas import Redirect

router = APIRouter()


@router.get('/{path}', response_class=RedirectResponse, status_code=302, responses={
    404: {'content': {'text/plain': {'default': 'Page not found'}}}
})
async def redirect(path: str):
    query = redirects.select().where(redirects.c.path == path)
    result = await database.fetch_one(query)
    if not result:
        return PlainTextResponse('Page not found', status_code=404)
    else:
        redirect_obj = Redirect.from_orm(result)
        return redirect_obj.target
