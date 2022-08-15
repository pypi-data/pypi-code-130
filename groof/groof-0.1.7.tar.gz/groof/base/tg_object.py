from .base_model import BaseModel


class TgObject(BaseModel):
    """ Base class for all telegram objects """

    __aliases__ = {'from_user': 'from'}
