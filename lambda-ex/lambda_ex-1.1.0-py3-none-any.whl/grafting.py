from functools import partial
from typing import Callable

_grafted = set()


class GRAFTEE:
    pass


def grafting(trigger: Callable, *args, one_off=True, **kwargs) -> Callable:
    """
    a handy implementation for "one-off" used decorator.

    classic usage:
        from lambda_ex import grafting
        @grafting(button.clicked.connect)
        def on_clicked():
            print('clicked')
    """
    _is_func_in_params = GRAFTEE in args or GRAFTEE in tuple(kwargs.values())
    
    def decorator(func):
        uid = (id(trigger), id(func))
        if one_off and uid in _grafted:
            return func
        else:
            _grafted.add(uid)
        if _is_func_in_params:
            new_args = (func if x is GRAFTEE else x
                        for x in args)
            new_kwargs = {k: (func if v is GRAFTEE else v)
                          for k, v in kwargs.items()}
            trigger(*new_args, **new_kwargs)
        else:
            trigger(partial(func, *args, **kwargs))
        return func
    
    return decorator
