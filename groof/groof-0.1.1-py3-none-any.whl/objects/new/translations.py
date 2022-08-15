from ...base import NewObject
from dataclasses import dataclass, astuple


@dataclass
class Translations(NewObject):
    """ Translations """

    def __hash__(self):
        return hash(astuple(self))

    def get(self, lang: str = None) -> str | None:
        from ...context import ctx

        return getattr(self, lang or ctx.lang, None)

    def format(self, *args, **kwargs):
        # noinspection PyArgumentList
        return self.__class__(*[i.format(*args, **kwargs) for i in astuple(self)])

    def __contains__(self, item):
        return item in astuple(self)
