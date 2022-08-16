import copy
import datetime


def convert_timestamp_to_date_utc(timestamp):
    try:
        if timestamp is not None:
            return datetime.datetime.utcfromtimestamp(timestamp).replace(
                tzinfo=datetime.timezone.utc
            )
        else:
            return None
    except Exception as e:
        return None


def get_value_from_field(data, from_field, default_value=None):
    data_copy = copy.deepcopy(data)
    field_road = from_field.split('.')
    value = default_value
    for field in field_road:
        value = data_copy.get(field, {})
        if value is None:
            return value
        data_copy = value
    if value == {}:
        value = default_value
    return value


def remove_none_field(data):
    data_copy = copy.deepcopy(data)

    def recurse_dict(data_in, data_copy_in):
        for key, value in data_in.items():
            if not isinstance(value, dict) and value is None:
                del data_copy_in[key]
            elif isinstance(value, dict):
                recurse_dict(value, data_copy_in[key])

    recurse_dict(data, data_copy)
    return data_copy
