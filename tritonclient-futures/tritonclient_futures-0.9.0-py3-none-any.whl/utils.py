#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   utils.py
@Time    :   2022/08/12 23:30:02
@Author  :   nicholas wu 
@Version :   v1.0
@Contact :   nicholas_wu@aliyun.com
'''
from functools import wraps
import rapidjson as json
from requests import Session, adapters, RequestException
from tritonclient.utils import InferenceServerException, raise_error, deserialize_bytes_tensor, triton_to_np_dtype
from tritonclient.http import _get_query_string, _get_inference_request


class Response:
    def __init__(self, content, headers, status_code):
        self._content = content
        self._headers = headers
        self._status_code = status_code
        self._offset = 0

    def get(self, name):
        return self._headers.get(name)

    @property
    def status_code(self):
        return self._status_code

    @property
    def content(self):
        header_length = self.get("Inference-Header-Content-Length")
        return self._content[header_length: ]

    def read(self, length=-1):
        if length == -1:
            return self._content[self._offset:]
        else:
            prev_offset = self._offset
            self._offset += length
            return self._content[prev_offset:self._offset]

def _get_error(response: Response):
    """
    Returns the InferenceServerException object if response
    indicates the error. If no error then return None
    """
    if response.status_code != 200:
        error_response = json.loads(response._content)
        return InferenceServerException(msg=error_response["error"])
    else:
        return None


def _raise_if_error(response):
    """
    Raise InferenceServerException if received non-Success
    response from the server
    """
    error = _get_error(response)
    if error is not None:
        raise error


def catch_requests_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
            headers = resp.headers
            content = resp.content
            status_code = resp.status_code
        except RequestException as e:
            headers = {}
            content = json.dumps({"error": repr(e)})
            status_code = 201
        resp = Response(content, headers, status_code)
        return resp
    return wrapper


    