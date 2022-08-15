from .. import api
from ..api import request
from ..context import ctx
from ..objects import File
from ..objects.tg_methods import GetFile


def get_file(
        file_id: str = None,
) -> File:
    return request(
        GetFile,
        locals(),
        file_id=ctx.file_id,
    )


def get_file_url(
        file_id: str = None,
) -> str:
    file = get_file(file_id)
    return api.get_file_url(file.file_path)
