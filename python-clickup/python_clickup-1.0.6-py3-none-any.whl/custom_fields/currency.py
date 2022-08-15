from .number import NumberValidator
from ..utils.validators import PositiveNumberValidator


class CurrencyField(NumberValidator):
    TYPE = "currency"
    VALIDATOR = PositiveNumberValidator
