import logging

from attr import attrs, attrib
from typing import Dict


@attrs(kw_only=True)
class LoggerMixin:
    @property
    def logger(self):
        """returns parent logger"""
        return logging.getLogger("stderr")


@attrs(kw_only=True)
class AppMixin(LoggerMixin):
    _app = attrib()

    @property
    def app(self: object) -> object:
        return self._app

    @property
    def config(self: object) -> Dict:
        return self.app.config


## TODO
