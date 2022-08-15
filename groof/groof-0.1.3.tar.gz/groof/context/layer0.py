from contextvars import ContextVar
from dataclasses import dataclass

from ..objects import Update

UPDATE = ContextVar('UPDATE')


@dataclass
class ContextLayer0:
    token: str = None
    parse_mode: str = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    protect_content: bool = None

    @property
    def update(self) -> Update | None:
        """ Update """
        return UPDATE.get(None)

    @update.setter
    def update(self, value: Update):
        UPDATE.set(value)
