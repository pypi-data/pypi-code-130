from .exceptions import ValueNotOfSupportedType


class RedisValidations:
    # Setting up the key validation method
    def key_validation(key):
        if isinstance(key, (bytes, str, float, int)):
            return True
        raise ValueNotOfSupportedType(
            "Key should be of datatype bytes, str, float or int")

    # Setting up the value validation method
    def value_validation(value):
        if isinstance(value, (bytes, str, float, int)):
            return True
        raise ValueNotOfSupportedType(
            "Value should be of datatype bytes, str, float or int")

    # Check if the value is int
    def isint(value):
        try:
            int(value)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    # Check if the value is float
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        except TypeError:
            return False
