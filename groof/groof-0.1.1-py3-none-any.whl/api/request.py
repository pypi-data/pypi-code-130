import json
import typing

from requests import Response

from ..base import TgMethod, TgObject, BaseModel
from ..base.exceptions import RequestError
from ..loader import BOT_TOKEN, session
from ..objects import InlineKeyboard, Keyboard, Translations, InputFile
from ..utils import cast, clean_dict

METHOD_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/{{method}}'
FILE_URL = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{{file_path}}'

OK = 'ok'
RESULT = 'result'
ERROR_CODE = 'error_code'
DESCRIPTION = 'description'


def get_method_url(method: str):
    return METHOD_URL.format(method=method)


def get_file_url(file_path: str):
    return FILE_URL.format(file_path=file_path)


def parse_response(method: type[TgMethod], params: dict, files: dict, resp: Response):
    result: dict = resp.json()

    if result[OK]:
        result = result[RESULT]
    else:
        raise RequestError(result[ERROR_CODE], result[DESCRIPTION], params, files)

    return cast(result, method.__response_type__)


def request(method: type[TgMethod], params: dict, **alternatives) -> TgObject | typing.Any:
    endpoint = get_method_url(method.__name__)
    params = params.copy()
    files = {}

    for key in alternatives:
        if params[key] is None:
            params[key] = alternatives[key]

    for key, value in params.items():
        if isinstance(value, Keyboard):
            params[key] = value.to_tg_object()
        elif isinstance(value, InlineKeyboard):
            params[key] = value.to_tg_object()
        elif isinstance(value, Translations):
            params[key] = value.get()
        elif isinstance(value, InputFile):
            params[key] = None
            reader = open(value.path, 'rb')
            files[key] = value.name or reader.name, reader

    for key, value in params.items():
        if isinstance(value, BaseModel):
            params[key] = cast(value, dict)

    if params.get('entities') or params.get('caption_entities'):
        params['parse_mode'] = None

    params = clean_dict(params)

    for key, value in params.items():
        if isinstance(value, (list, dict)):
            params[key] = json.dumps(value)

    files = files or None
    resp = session.post(endpoint, data=params, files=files)
    return parse_response(method, params, files, resp)
