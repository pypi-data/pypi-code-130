from .base_model import BaseModel
from .tg_object import TgObject


class TgMethod(BaseModel):
    """ Base class for all telegram methods """

    __response_type__: type[TgObject] = None
