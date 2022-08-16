import asyncio
from functools import wraps
import sys

args = sys.argv
func_name = args[1]
args = args[2:]


def _get_key(arg: str):
    if arg.startswith('--'):
        key = arg[2:]
    elif arg.startswith('-'):
        key = arg[1:]
    return key


def _set_alias(alias: dict, obj: dict) -> dict:
    if isinstance(alias, dict):
        for old, new in alias.items():
            obj[new] = obj[old]
            del obj[old]
        return obj


def _parse_args(args) -> dict:
    obj = {}
    for i, arg in enumerate(args):
        if i % 2 == 0:
            key = _get_key(arg)
            obj[key] = None
        else:
            key = _get_key(args[i - 1])
            obj[key] = arg
    return obj


def dong(alias: dict = None, help: str = '', sync: bool = False):
    """
    example:
    @vs()
    async def hello(name, age):
        print(name, age)

    """
    def arun(func):
        @wraps(func)
        def wrapper():

            if func_name == func.__name__:
                obj = _parse_args(args)
                if alias:
                    obj = _set_alias(alias, obj)
                if sync:
                    return func(**obj)
                asyncio.run(func(**obj))
        return wrapper()
    return arun
