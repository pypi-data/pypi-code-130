from .__data_structure__.ring_twoway_link import LinkedLooplist
from .__data_structure__.synchronize_many import Resource
from .__data_structure__.synchronize_iterate import Synchro
from .__data_structure__.dynamic_cache import Cache
from .__data_structure__.link import LinkedList
from .__data_structure__.goods import ResourcePool
import traceback


# 捕获装饰器方法
def tryFunc_args(iftz=True, except_return_value=None):
    def temp(func):
        def temp_ch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if iftz:
                    traceback.print_exc()
                return except_return_value

        return temp_ch

    return temp
