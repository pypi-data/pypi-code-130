import importlib
from abc import ABC
from typing import Generic, TypeVar

from requests import Response, Session

from pytestapilib.http.builder import RequestBuilder
from pytestapilib.http.log import ResponseLogger


class BaseResponse(ABC):

    def __init__(self, response: Response):
        self.response = response

    def get_original(self) -> Response:
        return self.response

    def get_body(self):
        return self.get_original().json()


TObj = TypeVar("TObj", bound=BaseResponse)


class BaseRequest(ABC, Generic[TObj]):

    def __init__(self):
        self.request = None

    def send(self, session: Session) -> TObj:
        prep_request = RequestBuilder(session, self.request).intercept()
        response = session.send(prep_request)
        ResponseLogger(response).log()
        generic_response = self.__get_generic_response(response)
        return generic_response

    def __get_generic_response(self, response: Response):
        full_class_name = str(self.__class__.__orig_bases__[0]).split("[")[1].split("]")[0]
        class_name = full_class_name.split(".")[-1]
        full_module_name = full_class_name.removesuffix("." + class_name)
        module = importlib.import_module(full_module_name)
        clazz = getattr(module, class_name)
        clazz_instance = clazz(response)
        return clazz_instance
