
from .publish import Puber
from .subscribe import Subscriber
from .log_publish import LogPuber
from .log_subscribe import LogSubscriber

__pubers__ = {}

def register_puber(name, *args, **kwargs):
    global __pubers__
    if name not in __pubers__:
        __pubers__[name] = Puber(*args, **kwargs)
        print("存在相同名称的puber:%s" % name)
    return True

def get_puber(name):
    if name not in __pubers__:
        raise Exception("不存在的Puber")
    return __pubers__[name]


__version__ = "0.1.3"
