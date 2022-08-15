from dataclasses import dataclass

from .base import Filter
from ..context import ctx
from ..utils import listify


@dataclass
class Message(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.message)
        except AttributeError:
            return False


@dataclass
class Text(Filter):
    value: str | list[str] = None

    def __call__(self):
        try:
            if not (text := ctx.update.message.text):
                return False
        except AttributeError:
            return False

        if self.value is None:
            return bool(text)
        return text in listify(self.value)


@dataclass
class Command(Filter):
    value: str | list[str] = None

    def __call__(self):
        try:
            if not (text := ctx.update.message.text):
                return False
        except AttributeError:
            return False

        if self.value is None:
            return text.startswith('/')

        return text.lstrip('/') in listify(self.value)


@dataclass
class Contact(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.message.contact)
        except AttributeError:
            return False


@dataclass
class Document(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.message.document)
        except AttributeError:
            return False


@dataclass
class Photo(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.message.photo)
        except AttributeError:
            return False


@dataclass
class Animation(Filter):
    def __call__(self):
        try:
            return bool(ctx.update.message.animation)
        except AttributeError:
            return False
