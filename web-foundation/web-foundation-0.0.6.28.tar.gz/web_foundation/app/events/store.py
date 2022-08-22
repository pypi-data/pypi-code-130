from typing import Any

from web_foundation.kernel import IMessage


class StoreUpdateEvent(IMessage):
    message_type = "store_update"

    def __init__(self, key: str, value: Any):
        super().__init__()
        self.key = key
        self.value = value


    def __str__(self):
        return f"StoreUpdateEvent({self.key})"