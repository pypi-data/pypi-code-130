def clean_dict(value: dict) -> dict:
    from .cast import BaseModel, cast

    """ Recursively clean dict from `None` values """

    def clean_obj(obj):
        if isinstance(obj, BaseModel):
            return cast(obj, dict)
        if isinstance(obj, list):
            return [clean_obj(i) for i in obj]
        if isinstance(obj, dict):
            return {k: clean_obj(v) for k, v in obj.items() if v is not None}
        return obj

    return clean_obj(value)
