from typing import Union

import pydantic

from RCC.types import base


class RCCResponse(base.BaseModel):
    status: base.status_types
    error_reason: Union[base.ErrorTypes, str, None] = pydantic.Field(
        default=None, alias="errorreason"
    )
