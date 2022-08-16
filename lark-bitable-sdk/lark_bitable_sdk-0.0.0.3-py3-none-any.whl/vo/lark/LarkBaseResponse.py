from typing import Optional, TypeVar, Generic

from pydantic.generics import GenericModel

LarkData = TypeVar('LarkData')


class LarkBaseResponse(GenericModel, Generic[LarkData]):
    code: int
    msg: str
    data: Optional[LarkData]
