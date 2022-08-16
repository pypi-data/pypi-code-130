from functools import wraps
import inspect
import copy

def ignore(item):
    return ("WvK43p#AK6n3&8nIh#mLI9rhb$I5nmir3$lp0Kzq*UGvta9#RE_Slava_Ukraini",item)

def reinit_default_args(func):
    """
    decorator that creates new default arguments on each function call.
    Usage:

    to make new default arg on each call simply use:

    @reinit_default_args
    def func(a=[]):
        ...

    to ignore some default values use:
    @reinit_default_args
    def func(a=ignore([])):
        ...
        
    """

    @wraps(func)
    def wrapper_func(*args, **kwargs):
        args_func = inspect.getfullargspec(func)
        print(args_func)
        if args_func.defaults is not None:
            for i in range(len(args_func.defaults)):
                i=-1-i
                if args_func.args[i] not in kwargs:
                    if isinstance(args_func.defaults[i], tuple):
                        if len(args_func.defaults[i])==2:
                            if args_func.defaults[i][0]=="WvK43p#AK6n3&8nIh#mLI9rhb$I5nmir3$lp0Kzq*UGvta9#RE_Slava_Ukraini":
                                kwargs[args_func.args[i]] = args_func.defaults[i][1]
                                continue
                    kwargs[args_func.args[i]] = copy.copy(args_func.defaults[i])
        if args_func.kwonlyargs is not None:
            for i in range(len(args_func.kwonlyargs)):
                if args_func.kwonlyargs[i] not in kwargs:
                    if isinstance(args_func.kwonlydefaults[args_func.kwonlyargs[i]], tuple):
                        if len(args_func.kwonlydefaults[args_func.kwonlyargs[i]])==2:
                            if args_func.kwonlydefaults[args_func.kwonlyargs[i]][0]=="WvK43p#AK6n3&8nIh#mLI9rhb$I5nmir3$lp0Kzq*UGvta9#RE_Slava_Ukraini":
                                kwargs[args_func.kwonlyargs[i]] = args_func.kwonlydefaults[args_func.kwonlyargs[i]][1]
                                continue
                    kwargs[args_func.kwonlyargs[i]] = copy.copy(args_func.kwonlydefaults[args_func.kwonlyargs[i]])
        func(*args, **kwargs)
    return wrapper_func