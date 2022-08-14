# [Standard Library]
from abc import ABC
from typing import Callable
from typing import Dict
from typing import Union

from .event import Event


class Subscriber(ABC):
    handlers: Union[Dict[type, Callable], None] = None

    def __init__(self):
        if not hasattr(self, "handlers"):
            raise AttributeError("Subscriber class must have handlers property")

    def _on_update(self, event: Event) -> None:
        # check if property "handlers" exist in class
        if not hasattr(self, "handlers") or not self.handlers:
            raise AttributeError("Subscriber class must have handlers property")
        # check if event type is in handlers
        handler = self.handlers.get(type(event))
        if handler:
            # call handler function
            handler(event)
