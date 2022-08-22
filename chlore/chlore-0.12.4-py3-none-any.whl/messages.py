import typing
from fastapi import Request
from enum import IntEnum


class FlashType(IntEnum):
    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4


def add_message(request: Request, category: FlashType, message: str) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []


class FlashMessages:
    def __init__(self, request: Request):
        self.request = request

    def add(self, category: FlashType, message: str):
        return add_message(self.request, category, message)

    def pop_all(self):
        return get_messages(self.request)

    def debug(self, message: str):
        self.add(FlashType.DEBUG, message)

    def info(self, message: str):
        self.add(FlashType.INFO, message)

    def success(self, message: str):
        self.add(FlashType.SUCCESS, message)

    def warning(self, message: str):
        self.add(FlashType.WARNING, message)

    def error(self, message: str):
        self.add(FlashType.ERROR, message)

    @classmethod
    def __call__(cls, request: Request):
        "Small hack: make this Class a fastapi dependable."
        return FlashMessages(request)
