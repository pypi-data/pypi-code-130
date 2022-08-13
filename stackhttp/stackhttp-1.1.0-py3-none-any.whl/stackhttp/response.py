from dataclasses import dataclass, field
from io import TextIOWrapper
from json import dumps
import mimetypes
import os
import re
from types import GeneratorType
from typing import Union

CODES = {
    201: ("No Content"),
    200: ("OK"),
    400: ("Bad Request"),
    401: ("Unauthorized"),
    403: ("Forbidden"),
    404: ("Not Found"),
    500: ("Internal Server Error"),
    501: ("Not Implemented")
}

def set_shortcut_content(self, code, page=None, json=None):
    CODES[code] = (*CODES[code][0:2], page, json)

def add_shortcut_code(self, code, status, page=None, json=None):
    CODES[code] = (code, status, page, json)


@dataclass
class Response(object):
    headers: dict = field(default_factory=lambda: {"Server": "stack"})
    code: int = 200
    status: str = 'OK'
    file_chunksize: int = 512
    data: Union[GeneratorType, bytes, str] = b''
    # Transform {key: value} into {sanitized_value: (key, value)}
    shortcut_methods: dict = field(repr=False, default_factory=lambda: {re.sub("[^a-zA-Z ]*", "", value[0]).lower().replace(" ", "_"): (key, *value) for key, value in CODES.items()})
    
    def http(self):
        yield f"HTTP/1.1 {self.code} {self.status}".encode('utf-8')
        for k, v in self.headers.items():
            yield f"\r\n{k}: {v}".encode('utf-8')
        yield b"\r\n\r\n"

        for i in self.data:
            if not isinstance(i, bytes):
                i = i.encode("utf-8")
            yield i
        return
    


    @staticmethod
    def file_generator(path, chunksize):
        file = open(path, 'rb')
        while data := file.read(chunksize):
            yield data
        file.close()

    def define_content(self, content_type, content_length, content, encoding='utf-8'):
        self.headers['Content-Type'] = content_type
        if encoding:
            self.headers['Content-Type'] += f"; charset={encoding}"
        self.headers['Content-Length'] = content_length
        self.data = content
        return self


    def define_code(self, code, status, page=None, json=None):
        self.code = code
        self.status = status
        if page:
            self.send_file(page)
        elif json:
            self.send_json(json) 
    
    @staticmethod
    def shortcut_wrapper(code, status, _page=None, _json=None, callback=None):
        def wrapper(page=None, json=None):
            page = page or _page
            json = json or _json
            return callback(code=code, status=status, page=page, json=json)
        return wrapper


    def __getattribute__(self, name):
        # Implement dynamic code setting.
        _shortcut_methods = object.__getattribute__(self, "shortcut_methods")
        if name in _shortcut_methods:
            return self.shortcut_wrapper(*_shortcut_methods[name], callback=self.define_code)
        else:
            return object.__getattribute__(self, name)


    def __dir__(self):
        return [*super().__dir__(), *self.shortcut_methods.keys()]

    def send_file(self, path, encoding=None):
        mime_type = mimetypes.guess_type(path)

        return self.define_content(
            mime_type[0],
            os.stat(path).st_size,
            self.file_generator(path, self.file_chunksize)
        )

    def send_json(self, data):
        data = dumps(data)

        return self.define_content(
            'application/json',
            len(data),
            data
        )
