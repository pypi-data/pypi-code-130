from typing import Any

from pyclickup.utils.validators.base import ValidationError
from .string import StringValidator
from ..types import RawCustomField


class PhoneValidator(StringValidator):
    """Validates that value is `str` of digets. `+` can also be used."""

    @classmethod
    def validate(cls, value: Any, raw_field: RawCustomField) -> None:
        super().validate(value, raw_field)
        
        if not all([value.startswith('+'), value[1:].isnumeric()]):
            raise ValidationError(
                "Must be string with numbers [0-9] starting with `+`"
            )
