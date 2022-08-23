from copy import deepcopy
from typing import Dict

from boltons.iterutils import remap


def _deepmerge(dest: Dict, src: Dict, path: str = None) -> Dict:
    """
    Take every key, value from src and merge it recursivly into dest.

    Adapted from https://stackoverflow.com/questions/7204805

    Parameters
    ----------
    dest: dict
        destination dictionary

    src: dict
        source dictionary

    Returns
    -------
    dict:
        merged dictionary
    """
    if path is None:
        path = []

    for key in src:
        if key not in dest:
            dest[key] = src[key]
        elif isinstance(dest[key], dict) and isinstance(src[key], dict):
            _deepmerge(dest[key], src[key], path + [str(key)])
        elif dest[key] == src[key]:
            pass  # same leaf value
        else:
            dest[key] = src[key]
    return dest


def deepmerge(dest, src):
    """
    Take every key, value from src and merge it recursivly into dest.
    None values are stripped from src before merging.

    Adapted from https://stackoverflow.com/questions/7204805

    Parameters
    ----------
    dest: dict
        destination dictionary

    src: dict
        source dictionary

    Returns
    -------
    dict:
        merged dictionary
    """
    # pylint: disable=unnecessary-lambda-assignment
    is_not_none = lambda path, key, value: key is not None and value is not None
    src = remap(src, visit=is_not_none)

    return _deepmerge(deepcopy(dest), src)
