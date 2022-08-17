from os.path import join, dirname

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=join(dirname(__package__), "templates"))


def make_response(req: Request, ctx: dict, tpl: str):
    ctx["request"] = req
    return templates.TemplateResponse(tpl, ctx)
