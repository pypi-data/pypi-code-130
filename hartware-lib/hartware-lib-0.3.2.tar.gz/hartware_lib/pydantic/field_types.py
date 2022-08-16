class CustomFieldType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate


class BooleanFromString(CustomFieldType):
    @classmethod
    def validate(cls, v):
        if isinstance(v, bool):  # Let pass boolean default values
            return v

        if v.lower() in ("yes", "true", "1"):
            return True
        elif v.lower() in ("no", "false", "0"):
            return False
        else:
            raise ValueError(
                "Invalid string representation of a boolean, should be either 1|0|true|false|yes|no"
            )
