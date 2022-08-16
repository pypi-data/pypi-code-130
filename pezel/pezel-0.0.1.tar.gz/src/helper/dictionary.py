import functools
import operator


def _build_missing_getitem(obj, k):
    if k not in obj:
        obj[k] = {}

    return operator.getitem(obj, k)


def flatten_dict(unflatten_dict):
    flat_dict = []
    stack = [([k], v) for k, v in unflatten_dict.items()]
    while stack:
        current_keys, current_val = stack.pop()
        if isinstance(current_val, dict):
            stack.extend([(current_keys + [k], v) for k, v in current_val.items()])
        elif isinstance(current_val, list):
            stack.extend([(current_keys + [i], v) for i, v in enumerate(current_val)])
        else:
            flat_dict.append((current_keys, current_val))

    return flat_dict


def set_nested_dict(nested_dict, key_list, value, build_missing=False):
    if build_missing:
        getitem_fn = _build_missing_getitem
    else:
        getitem_fn = operator.getitem

    functools.reduce(getitem_fn, key_list[:-1], nested_dict)[key_list[-1]] = value
