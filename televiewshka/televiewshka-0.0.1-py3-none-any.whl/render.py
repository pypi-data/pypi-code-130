import typing as t
from .type_aliases import ViewHint


class RenderOptions:
    def __init__(self, 
                 view: ViewHint, 
                 inplace: bool, 
                 params: t.Optional[dict] = None):
        self.view = view
        self.inplace = inplace
        self.params = params


def render(view_hint: ViewHint, inplace = False, **kwargs):
    return RenderOptions(view_hint, inplace, kwargs)
