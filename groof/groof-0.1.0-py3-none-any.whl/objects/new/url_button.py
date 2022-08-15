from __future__ import annotations

from dataclasses import dataclass

from ...base import NewObject


@dataclass
class UrlButton(NewObject):
    """ UrlButton """
    text: str
    url: str = None

    def __call__(self, **_vars) -> UrlButton:
        """ Return button copy [text=text.format(**_vars), url=url.format(**_vars)] """
        return UrlButton(self.text.format(**_vars), self.url.format(**_vars))
